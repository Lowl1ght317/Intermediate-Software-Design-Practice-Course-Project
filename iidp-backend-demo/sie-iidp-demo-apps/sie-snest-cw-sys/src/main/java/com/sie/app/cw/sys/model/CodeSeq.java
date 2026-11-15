package com.sie.app.cw.sys.model;

import com.sie.snest.engine.model.Bool;
import com.sie.snest.sdk.BaseModel;
import com.sie.snest.sdk.annotation.meta.Model;
import com.sie.snest.sdk.annotation.meta.Property;
import com.sie.snest.sdk.annotation.orm.Index;

/**
 * 编码流水：按 规则编码 + 日期段 各记一条流水，日期段变化（如跨天）自动从 1 重新计数。
 * 唯一索引 uk_cw_code_seq_rule_date 保证同一规则同一天只有一条流水记录，作为并发取号的最后一道防线。
 */
@Model(name = "code_seq", tableName = "cw_code_seq", description = "编码流水", displayName = "编码流水", isAutoLog = Bool.True,
        indexes = {
                @Index(name = "uk_cw_code_seq_rule_date", columnList = {"rule_code", "date_seg"}, unique = true)
        })
public class CodeSeq extends BaseModel<CodeSeq> {

    @Property(displayName = "规则编码", columnName = "rule_code", length = 64)
    private String ruleCode;

    @Property(displayName = "日期段", columnName = "date_seg", length = 32)
    private String dateSeg;

    @Property(displayName = "当前流水值", columnName = "curr_value", defaultValue = "0")
    private Integer currValue;

    public CodeSeq setRuleCode(String ruleCode) {
        this.set("ruleCode", ruleCode);
        return this;
    }

    public String getRuleCode() {
        return getStr("ruleCode");
    }

    public CodeSeq setDateSeg(String dateSeg) {
        this.set("dateSeg", dateSeg);
        return this;
    }

    public String getDateSeg() {
        return getStr("dateSeg");
    }

    public CodeSeq setCurrValue(Integer currValue) {
        this.set("currValue", currValue);
        return this;
    }

    public Integer getCurrValue() {
        return getInt("currValue");
    }
}
