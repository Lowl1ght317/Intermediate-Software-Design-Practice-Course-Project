package com.sie.app.cw.prod.model;

import com.sie.snest.engine.model.Bool;
import com.sie.snest.sdk.BaseModel;
import com.sie.snest.sdk.DataType;
import com.sie.snest.engine.data.RecordSet;
import com.sie.snest.sdk.annotation.meta.MethodService;
import com.sie.snest.sdk.annotation.meta.Model;
import com.sie.snest.sdk.annotation.meta.Property;
import com.sie.snest.sdk.annotation.orm.JoinColumn;
import com.sie.snest.sdk.annotation.orm.ManyToOne;
import com.sie.snest.sdk.annotation.orm.Option;
import com.sie.snest.sdk.annotation.orm.Selection;
import com.sie.snest.sdk.annotation.validate.Validate;

import java.util.Date;

/**
 * 生产工单：校园文创产品的设计→打样→批量制作→入库流程单据。
 * <p>
 * 说明：产品模型（product）位于 cw-base 应用，两个 APP 由引擎分别装载，
 * 因此这里不直接引用 cw-base 的 Product 类，而是通过 targetModel 以模型名建立关联，
 * 字段类型使用所有应用共享的 BaseModel。
 */
@Model(name = "work_order", tableName = "cw_work_order", description = "生产工单", displayName = "生产工单", isAutoLog = Bool.True)
public class WorkOrder extends BaseModel<WorkOrder> {

    @Validate.NotBlank(message = "工单编码不能为空！")
    @Property(displayName = "工单编码", columnName = "code", unique = true, displayForModel = true, length = 64)
    private String code;

    @ManyToOne(targetModel = "product", displayName = "文创产品")
    @JoinColumn(name = "product_id")
    private BaseModel product;

    @Property(displayName = "计划数量", columnName = "plan_qty", defaultValue = "0")
    private Integer planQty;

    @Property(displayName = "工单状态", columnName = "status", defaultValue = "1", widget = "select", length = 256)
    @Selection(values = {
            @Option(label = "草稿", value = "1"),
            @Option(label = "已下达", value = "2"),
            @Option(label = "已完工", value = "3")
    })
    private String status;

    @Property(displayName = "计划日期", columnName = "plan_date", dataType = DataType.DATE)
    private Date planDate;

    public WorkOrder setCode(String code) {
        this.set("code", code);
        return this;
    }

    public String getCode() {
        return getStr("code");
    }

    @SuppressWarnings("unchecked")
    public WorkOrder setProduct(BaseModel product) {
        this.set("product", product);
        return this;
    }

    public BaseModel getProduct() {
        return (BaseModel) this.get("product");
    }

    public WorkOrder setPlanQty(Integer planQty) {
        this.set("planQty", planQty);
        return this;
    }

    public Integer getPlanQty() {
        return getInt("planQty");
    }

    public WorkOrder setStatus(String status) {
        this.set("status", status);
        return this;
    }

    public String getStatus() {
        return getStr("status");
    }

    public WorkOrder setPlanDate(Date planDate) {
        this.set("planDate", planDate);
        return this;
    }

    public Date getPlanDate() {
        return getDate("planDate");
    }

    // ---------- 业务服务入口（引擎只把 @Model 类上的 @MethodService 注册为模型服务） ----------

    @MethodService(name = "createWithCode", displayName = "新建工单并生成编码", auth = "create")
    public WorkOrder createWithCode(RecordSet rs, String productId, Integer planQty, String planDate) {
        return new com.sie.app.cw.prod.service.WorkOrderService().createWithCode(rs, productId, planQty, planDate);
    }

    @MethodService(name = "changeStatus", displayName = "工单状态迁移", auth = "update")
    public java.util.Map<String, Object> changeStatus(RecordSet rs, String code, String target) {
        return new com.sie.app.cw.prod.service.WorkOrderService().changeStatus(rs, code, target);
    }
}