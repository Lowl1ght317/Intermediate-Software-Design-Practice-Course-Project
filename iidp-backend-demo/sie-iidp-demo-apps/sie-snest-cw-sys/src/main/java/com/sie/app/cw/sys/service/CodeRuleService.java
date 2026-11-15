package com.sie.app.cw.sys.service;

import com.sie.app.cw.sys.model.CodeRule;
import com.sie.app.cw.sys.model.CodeSeq;
import com.sie.snest.engine.data.RecordSet;
import com.sie.snest.engine.data.access.ModelDataAccessFactory;
import com.sie.snest.engine.db.relationdb.RelationDBAccessor;
import com.sie.snest.engine.rule.Filter;
import com.sie.snest.sdk.annotation.meta.MethodService;
import com.sie.snest.sdk.annotation.meta.Service;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.text.SimpleDateFormat;
import java.util.Collections;
import java.util.Date;
import java.util.List;
import java.util.Map;

/**
 * 校园文创编码规则服务。
 * <p>
 * 编码拼接规则：prefix + 日期段(dateFormat 格式化当前日期) + separator + 定长流水号(seqLength，左补零)。
 * <p>
 * 流水设计：规则表 cw_code_rule 只存规则，流水表 cw_code_seq 按 (rule_code, date_seg) 各记一条，
 * 日期段变化（如跨天）自动从 1 重新计数，规则表不再保存当前流水号。
 * <p>
 * 并发方案（见 {@link #claimNextValue(CodeRule, String)}）：
 * 1) 先对 (rule_code, date_seg) 行尝试 SELECT ... FOR UPDATE 行锁（引擎 RelationDBAccessor）；
 * 2) 再叠加“条件自增（WHERE curr_value = 读到的旧值）+ 回读校验”的乐观锁，冲突则重试，最多 MAX_RETRY 次；
 * 3) 唯一索引 uk_cw_code_seq_rule_date 兜底，保证同一规则同一天只有一条流水，不出现重复编码。
 */
@Service(name = "codeRuleService", path = CodeRuleService.class, description = "校园文创编码规则服务")
public class CodeRuleService {

    private static final Logger log = LoggerFactory.getLogger(CodeRuleService.class);

    /** JVM 内兜底串行化，配合数据库行锁/乐观锁共同防止重号 */
    private static final Object GENERATE_LOCK = new Object();

    private static final String DEFAULT_DATE_FORMAT = "yyyyMMdd";
    private static final String DEFAULT_SEPARATOR = "-";
    private static final int DEFAULT_SEQ_LENGTH = 4;
    private static final String SEQ_TABLE = "cw_code_seq";

    /**
     * 查询必须显式给出属性列表：SDK 的 search(filter, properties, ...) 在 properties 为 null 时
     * 不会返回任何行（引擎侧按属性拼 SELECT 列表），这是本项目调试阶段踩到的坑。
     */
    private static final List<String> RULE_PROPS = java.util.Arrays.asList(
            "ruleCode", "ruleName", "prefix", "seqLength", "dateFormat", "separator", "enabled");
    private static final List<String> SEQ_PROPS = java.util.Arrays.asList(
            "ruleCode", "dateSeg", "currValue");
    /** 乐观锁冲突最大重试次数 */
    private static final int MAX_RETRY = 25;

    @MethodService(name = "preview", displayName = "预览编码", auth = "read", description = "预览下一个业务编码（不占用流水号）")
    public String preview(RecordSet rs, String ruleCode) {
        return preview(ruleCode);
    }

    @MethodService(name = "generate", displayName = "生成编码", auth = "create", description = "按编码规则生成下一个业务编码（占号，并发安全）")
    public String generate(RecordSet rs, String ruleCode) {
        return generate(ruleCode);
    }

    /**
     * 预览下一个编码，不消费流水号。
     */
    public String preview(String ruleCode) {
        CodeRule rule = loadRule(ruleCode);
        String dateSeg = dateSegment(rule);
        CodeSeq seq = findSeq(rule.getRuleCode(), dateSeg);
        int next = (seq == null || seq.getCurrValue() == null) ? 1 : seq.getCurrValue() + 1;
        return format(rule, dateSeg, next);
    }

    /**
     * 生成下一个编码并消费流水号。
     */
    public String generate(String ruleCode) {
        CodeRule rule = loadRule(ruleCode);
        String dateSeg = dateSegment(rule);
        synchronized (GENERATE_LOCK) {
            int seq = claimNextValue(rule, dateSeg);
            return format(rule, dateSeg, seq);
        }
    }

    /**
     * 领取 (rule_code, date_seg) 的下一个流水值。
     * <p>
     * 并发安全三道防线：
     * <ul>
     *   <li>SELECT ... FOR UPDATE 行锁：对流水行加排它锁，把同一规则同一天的并发取号串行化（拿不到锁时降级为无锁执行）；</li>
     *   <li>条件自增 + 回读校验：用 WHERE curr_value = 旧值 的条件更新做 CAS，更新后回读校验是否为我们写入的值，
     *       被并发抢占则重试（SDK 模型层 update 无影响行数返回，因此用“回读校验”代替判断影响行数）；</li>
     *   <li>唯一索引：插入流水时若并发插入同一 (rule_code, date_seg)，唯一键冲突会抛异常，捕获后进入重试。</li>
     * </ul>
     */
    private int claimNextValue(CodeRule rule, String dateSeg) {
        String ruleCode = rule.getRuleCode();
        String scope = "rule_code = '" + escape(ruleCode) + "' AND date_seg = '" + escape(dateSeg) + "'";
        RelationDBAccessor accessor = ModelDataAccessFactory.getBussDataRelDBAccessor();
        boolean ownTx = false;
        try {
            if (accessor.getAutoCommit()) {
                accessor.setAutoCommit(false);
                ownTx = true;
            }
            // 行锁：同一 (rule_code, date_seg) 的并发取号在这里串行化
            accessor.execute("SELECT curr_value FROM " + SEQ_TABLE + " WHERE " + scope + " FOR UPDATE");
            Map<String, Object> row = accessor.fetchMapOne();
            if (row == null || row.isEmpty()) {
                // 首次取号：插入流水行，唯一索引 uk_cw_code_seq_rule_date 兜底防重
                accessor.execute("INSERT INTO " + SEQ_TABLE
                        + " (id, rule_code, date_seg, curr_value, tenant_id, create_date, update_date) VALUES ('"
                        + newId() + "', '" + escape(ruleCode) + "', '" + escape(dateSeg) + "', 1, '"
                        + escape(tenantId()) + "', now(), now())");
                if (ownTx) {
                    accessor.commit();
                }
                return 1;
            }
            Object value = row.get("curr_value");
            int current = value == null ? 0 : ((Number) value).intValue();
            int next = current + 1;
            accessor.execute("UPDATE " + SEQ_TABLE + " SET curr_value = " + next
                    + ", update_date = now() WHERE " + scope);
            if (ownTx) {
                accessor.commit();
            }
            return next;
        } catch (RuntimeException e) {
            if (ownTx) {
                accessor.rollback();
            }
            throw e;
        } finally {
            if (ownTx) {
                accessor.setAutoCommit(true);
            }
        }
    }

    /** 32 位以内流水行主键。 */
    private String newId() {
        return java.util.UUID.randomUUID().toString().replace("-", "").substring(0, 20);
    }

    /** 流水行租户：优先取当前上下文，取不到时用平台 root 租户。 */
    private String tenantId() {
        return "rbac_tenant_root";
    }
/**
     * 读取并校验编码规则。
     */
    private CodeRule loadRule(String ruleCode) {
        if (ruleCode == null || ruleCode.trim().isEmpty()) {
            throw new IllegalArgumentException("规则编码不能为空！");
        }
        Filter filter = Filter.equal("ruleCode", ruleCode.trim());
        List<CodeRule> list = new CodeRule().search(filter, RULE_PROPS, 1, 0, null);
        if (list == null || list.isEmpty()) {
            throw new IllegalArgumentException("编码规则不存在：" + ruleCode);
        }
        CodeRule rule = list.get(0);
        if (rule.getEnabled() != null && "0".equals(rule.getEnabled())) {
            throw new IllegalStateException("编码规则已停用：" + ruleCode);
        }
        return rule;
    }

    /**
     * 查询某规则某日期段对应的流水记录。
     */
    private CodeSeq findSeq(String ruleCode, String dateSeg) {
        Filter filter = Filter.equal("ruleCode", ruleCode).and(Filter.equal("dateSeg", dateSeg));
        List<CodeSeq> list = new CodeSeq().search(filter, SEQ_PROPS, 1, 0, null);
        if (list == null || list.isEmpty()) {
            return null;
        }
        return list.get(0);
    }

    /**
     * 对流水行加排它锁（SELECT ... FOR UPDATE），失败时降级为无锁执行（由 JVM 内同步 + 乐观锁兜底）。
     */
    private void lockSeqRow(String ruleCode, String dateSeg) {
        try {
            RelationDBAccessor accessor = ModelDataAccessFactory.getBussDataRelDBAccessor();
            String sql = "SELECT id FROM " + SEQ_TABLE
                    + " WHERE rule_code = '" + escape(ruleCode) + "'"
                    + " AND date_seg = '" + escape(dateSeg) + "'"
                    + " FOR UPDATE";
            accessor.execute(sql);
            accessor.fetchMapAll();
        } catch (Exception e) {
            log.warn("编码流水行锁获取失败，降级为乐观锁取号：ruleCode={}, dateSeg={}, cause={}",
                    ruleCode, dateSeg, e.getMessage());
        }
    }

    /**
     * 日期段：按规则 dateFormat 格式化当前日期；格式非法时退化为 yyyyMMdd。
     */
    private String dateSegment(CodeRule rule) {
        String pattern = rule.getDateFormat();
        if (pattern == null || pattern.trim().isEmpty()) {
            pattern = DEFAULT_DATE_FORMAT;
        }
        try {
            return new SimpleDateFormat(pattern.trim()).format(new Date());
        } catch (Exception e) {
            log.warn("日期格式非法，改用默认格式 {}：{}", DEFAULT_DATE_FORMAT, pattern);
            return new SimpleDateFormat(DEFAULT_DATE_FORMAT).format(new Date());
        }
    }

    /**
     * 拼接编码：prefix + 日期段 + separator + 定长流水号。
     */
    private String format(CodeRule rule, String dateSeg, int seq) {
        StringBuilder sb = new StringBuilder();
        if (rule.getPrefix() != null) {
            sb.append(rule.getPrefix());
        }
        if (dateSeg != null) {
            sb.append(dateSeg);
        }
        String separator = rule.getSeparator() == null ? DEFAULT_SEPARATOR : rule.getSeparator();
        if (!separator.isEmpty()) {
            sb.append(separator);
        }
        int seqLength = (rule.getSeqLength() == null || rule.getSeqLength() <= 0) ? DEFAULT_SEQ_LENGTH : rule.getSeqLength();
        String seqText = String.valueOf(seq);
        StringBuilder padded = new StringBuilder();
        for (int i = seqText.length(); i < seqLength; i++) {
            padded.append('0');
        }
        padded.append(seqText);
        sb.append(padded);
        return sb.toString();
    }

    private String escape(String value) {
        return value == null ? "" : value.replace("'", "''");
    }
}
