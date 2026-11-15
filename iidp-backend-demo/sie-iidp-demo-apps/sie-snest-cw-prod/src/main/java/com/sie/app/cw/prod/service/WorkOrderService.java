package com.sie.app.cw.prod.service;

import com.sie.app.cw.prod.model.WorkOrder;
import com.sie.snest.engine.data.RecordSet;
import com.sie.snest.engine.rule.Filter;
import com.sie.snest.sdk.BaseModel;
import com.sie.snest.sdk.annotation.meta.MethodService;
import com.sie.snest.sdk.annotation.meta.Service;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Arrays;
import java.util.Date;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * 生产工单业务服务：下达与完工走状态机，编码由编码规则生成。
 * <p>
 * 状态取值与详细设计 5.6 节一致：1 草稿、2 已下达、3 已完工；
 * 只允许 1→2（下达）、2→3（完工）、2→1（撤回），其余迁移一律拒绝并给出中文提示。
 */
@Service(name = "workOrderService", path = WorkOrderService.class, targets = {"work_order"}, description = "生产工单业务服务")
public class WorkOrderService {

    private static final Logger log = LoggerFactory.getLogger(WorkOrderService.class);

    private static final String WORK_ORDER_RULE = "WO";

    private static final List<String> WO_PROPS = Arrays.asList(
            "code", "product", "planQty", "status", "planDate");

    /**
     * 新建工单：编码由编码规则生成，状态固定从草稿开始。
     *
     * @param rs         调用上下文
     * @param productId  产品主键（cw-base 的 product）
     * @param planQty    计划数量
     * @param planDate   计划完工日期，格式 yyyy-MM-dd，可为空
     * @return 新建的工单
     */
    @MethodService(name = "createWithCode", displayName = "新建工单并生成编码", auth = "create")
    public WorkOrder createWithCode(RecordSet rs, String productId, Integer planQty, String planDate) {
        if (planQty == null || planQty <= 0) {
            throw new IllegalArgumentException("计划数量必须大于 0");
        }
        String code = CodeGenFacade.generate(WORK_ORDER_RULE);
        WorkOrder order = new WorkOrder();
        order.setCode(code);
        // 关联字段直接写主键字符串，引擎按 @JoinColumn(product_id) 落库；
        // 若传 BaseModel 实例，ORM 在序列化关系对象时会抛 NotSerializableException。
        order.set("product", productId);
        order.setPlanQty(planQty);
        order.setStatus("1");
        if (planDate != null && !planDate.trim().isEmpty()) {
            order.setPlanDate(parseDate(planDate));
        }
        WorkOrder created = order.create();
        log.info("新建工单 {} 产品 {} 数量 {}", code, productId, planQty);
        return created;
    }

    /**
     * 工单状态迁移。
     *
     * @param rs     调用上下文
     * @param code   工单编码
     * @param target 目标状态：2 下达、3 完工、1 撤回
     * @return 迁移结果，含原状态与新状态
     */
    @MethodService(name = "changeStatus", displayName = "工单状态迁移", auth = "update")
    public Map<String, Object> changeStatus(RecordSet rs, String code, String target) {
        WorkOrder order = new WorkOrder().select(Filter.equal("code", code), "code", "status", "planQty");
        if (order == null) {
            throw new IllegalArgumentException("工单不存在：" + code);
        }
        String from = order.getStatus();
        String to = target == null ? "" : target.trim();
        if (!allowed(from, to)) {
            throw new IllegalStateException("工单当前状态为 " + label(from) + "，不能直接变更为 " + label(to));
        }
        Map<String, Object> change = new LinkedHashMap<>();
        change.put("status", to);
        new WorkOrder().updateByFilter(change, Filter.equal("code", code));
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("code", code);
        result.put("from", from);
        result.put("to", to);
        result.put("message", "已由" + label(from) + "变更为" + label(to));
        log.info("工单 {} 状态 {} -> {}", code, from, to);
        return result;
    }

    /** 允许的状态迁移：草稿→已下达、已下达→已完工、已下达→草稿（撤回）。 */
    private boolean allowed(String from, String to) {
        if (from == null) {
            return false;
        }
        return ("1".equals(from) && "2".equals(to))
                || ("2".equals(from) && "3".equals(to))
                || ("2".equals(from) && "1".equals(to));
    }

    /**
     * 按主键变更状态，供列表行按钮调用：按钮把当前行整条传进来，这里再按 id 找到工单编码。
     */
    public Map<String, Object> changeStatusById(RecordSet rs, String id, String target) {
        if (id == null || id.trim().isEmpty()) {
            throw new IllegalArgumentException("缺少工单 id，按钮未取到当前行");
        }
        WorkOrder order = new WorkOrder().select(Filter.equal("id", id), "id", "code", "status");
        if (order == null) {
            throw new IllegalArgumentException("工单不存在：" + id);
        }
        return changeStatus(rs, order.getCode(), target);
    }

    private String label(String status) {
        if ("1".equals(status)) {
            return "草稿";
        }
        if ("2".equals(status)) {
            return "已下达";
        }
        if ("3".equals(status)) {
            return "已完工";
        }
        return "未知(" + status + ")";
    }

    private Date parseDate(String text) {
        try {
            return new SimpleDateFormat("yyyy-MM-dd").parse(text.trim());
        } catch (ParseException e) {
            throw new IllegalArgumentException("日期格式应为 yyyy-MM-dd：" + text);
        }
    }
}
