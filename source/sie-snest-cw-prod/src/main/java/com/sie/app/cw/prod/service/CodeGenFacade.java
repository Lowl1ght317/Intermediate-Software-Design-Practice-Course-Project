package com.sie.app.cw.prod.service;

import com.sie.snest.engine.data.access.ModelDataAccessFactory;
import com.sie.snest.engine.db.relationdb.RelationDBAccessor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Map;

/**
 * cw-base 侧的业务编码取号门面。
 * <p>
 * 编码规则与流水的权威实现在 cw-sys 的 {@code codeRuleService}。两个 APP 由不同类加载器装载，
 * 跨 APP 直接 new 对方的模型类会抛 ClassNotFoundException，因此本类以 SQL 方式访问同一对表
 * （cw_code_rule / cw_code_seq），与 cw-sys 共用同一份规则数据和同一个流水序列，
 * 保证“产品、物料、工单”的编号来自同一个计数器，不会出现两套号码。
 * <p>
 * 取号顺序：查规则 → 算日期段 → 对流水行 FOR UPDATE 加锁 → 自增 → 回读 → 拼码。
 */
final class CodeGenFacade {

    private static final Logger log = LoggerFactory.getLogger(CodeGenFacade.class);

    private static final String RULE_TABLE = "cw_code_rule";
    private static final String SEQ_TABLE = "cw_code_seq";

    private CodeGenFacade() {
    }

    /**
     * 按规则标识取下一个业务编码。
     *
     * @param ruleCode 规则标识，对应 cw_code_rule.rule_code
     * @return 形如 CP20261115-0001 的编码
     */
    static String generate(String ruleCode) {
        RelationDBAccessor accessor = ModelDataAccessFactory.getBussDataRelDBAccessor();
        accessor.execute("SELECT prefix, seq_length, date_format, `separator`, enabled FROM " + RULE_TABLE
                + " WHERE rule_code = '" + escape(ruleCode) + "'");
        List<Map<String, Object>> rules = accessor.fetchMapAll();
        if (rules == null || rules.isEmpty()) {
            throw new IllegalArgumentException("编码规则不存在：" + ruleCode);
        }
        Map<String, Object> rule = rules.get(0);
        if ("0".equals(str(rule.get("enabled")))) {
            throw new IllegalStateException("编码规则已停用：" + ruleCode);
        }
        String prefix = str(rule.get("prefix"));
        String separator = rule.get("separator") == null ? "-" : str(rule.get("separator"));
        int seqLength = intOf(rule.get("seq_length"), 4);
        String pattern = rule.get("date_format") == null ? "yyyyMMdd" : str(rule.get("date_format"));
        String dateSeg;
        try {
            dateSeg = new SimpleDateFormat(pattern).format(new Date());
        } catch (Exception e) {
            dateSeg = new SimpleDateFormat("yyyyMMdd").format(new Date());
        }
        int seq = claim(accessor, ruleCode, dateSeg);
        StringBuilder sb = new StringBuilder(prefix).append(dateSeg);
        if (separator != null && !separator.isEmpty()) {
            sb.append(separator);
        }
        String number = String.valueOf(seq);
        while (number.length() < seqLength) {
            number = "0" + number;
        }
        String code = sb.append(number).toString();
        log.info("cw-base 取号：rule={}, dateSeg={}, seq={}, code={}", ruleCode, dateSeg, seq, code);
        return code;
    }

    /**
     * 对 (rule_code, date_seg) 流水行加锁并自增，行不存在则插入。
     */
    private static int claim(RelationDBAccessor accessor, String ruleCode, String dateSeg) {
        String where = " WHERE rule_code = '" + escape(ruleCode) + "' AND date_seg = '" + escape(dateSeg) + "'";
        for (int attempt = 1; attempt <= 5; attempt++) {
            accessor.execute("SELECT id, curr_value FROM " + SEQ_TABLE + where + " FOR UPDATE");
            List<Map<String, Object>> rows = accessor.fetchMapAll();
            if (rows == null || rows.isEmpty()) {
                try {
                    accessor.execute("INSERT INTO " + SEQ_TABLE
                            + " (id, rule_code, date_seg, curr_value) VALUES ('" + escape(ruleCode + dateSeg)
                            + "', '" + escape(ruleCode) + "', '" + escape(dateSeg) + "', 1)");
                    return 1;
                } catch (RuntimeException e) {
                    log.info("流水行插入冲突，第 {} 次重试：{}", attempt, e.getMessage());
                    continue;
                }
            }
            int current = intOf(rows.get(0).get("curr_value"), 0);
            int next = current + 1;
            accessor.execute("UPDATE " + SEQ_TABLE + " SET curr_value = " + next + where
                    + " AND curr_value = " + current);
            accessor.execute("SELECT curr_value FROM " + SEQ_TABLE + where);
            List<Map<String, Object>> check = accessor.fetchMapAll();
            if (check != null && !check.isEmpty() && intOf(check.get(0).get("curr_value"), -1) == next) {
                return next;
            }
            log.info("流水自增冲突，第 {} 次重试：{}", attempt, dateSeg);
        }
        throw new IllegalStateException("编码生成失败：并发冲突重试 5 次仍未成功，ruleCode=" + ruleCode);
    }

    private static String str(Object o) {
        return o == null ? "" : String.valueOf(o);
    }

    private static int intOf(Object o, int def) {
        if (o == null) {
            return def;
        }
        try {
            return Integer.parseInt(String.valueOf(o));
        } catch (NumberFormatException e) {
            return def;
        }
    }

    private static String escape(String s) {
        return s == null ? "" : s.replace("'", "''");
    }
}
