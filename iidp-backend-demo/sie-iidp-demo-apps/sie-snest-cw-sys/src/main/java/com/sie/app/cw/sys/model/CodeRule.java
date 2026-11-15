package com.sie.app.cw.sys.model;

import com.sie.app.cw.sys.service.CodeRuleService;
import com.sie.snest.engine.data.RecordSet;
import com.sie.snest.engine.model.Bool;
import com.sie.snest.sdk.BaseModel;
import com.sie.snest.sdk.annotation.meta.MethodService;
import com.sie.snest.sdk.annotation.meta.Model;
import com.sie.snest.sdk.annotation.meta.Property;
import com.sie.snest.sdk.annotation.orm.Option;
import com.sie.snest.sdk.annotation.orm.Selection;
import com.sie.snest.sdk.annotation.validate.Validate;

/**
 * 编码规则：prefix + 日期段 + separator + 定长流水号。
 * 例：prefix=WO，dateFormat=yyyyMMdd，separator=-，seqLength=4 → WO20261115-0001
 */
@Model(name = "code_rule", tableName = "cw_code_rule", description = "编码规则", displayName = "编码规则", isAutoLog = Bool.True)
public class CodeRule extends BaseModel<CodeRule> {

    @Validate.NotBlank(message = "规则编码不能为空！")
    @Property(displayName = "规则编码", columnName = "rule_code", unique = true, displayForModel = true, length = 64)
    private String ruleCode;

    @Property(displayName = "规则名称", columnName = "rule_name", length = 128)
    private String ruleName;

    @Validate.NotBlank(message = "编码前缀不能为空！")
    @Property(displayName = "编码前缀", columnName = "prefix", length = 32)
    private String prefix;

    @Property(displayName = "流水号位数", columnName = "seq_length", defaultValue = "4")
    private Integer seqLength;

    @Property(displayName = "日期格式", columnName = "date_format", defaultValue = "yyyyMMdd", length = 32)
    private String dateFormat;

    @Property(displayName = "分隔符", columnName = "separator", length = 8)
    private String separator;

    @Property(displayName = "是否启用", columnName = "enabled", defaultValue = "1", widget = "select", length = 8)
    @Selection(values = {
            @Option(label = "启用", value = "1"),
            @Option(label = "停用", value = "0")
    })
    private String enabled;

    /**
     * 生成下一个业务编码（占用流水号），供引擎方法元数据注册与视图调用。
     */
    @MethodService(name = "generate", displayName = "生成编码", auth = "create", description = "按编码规则生成下一个业务编码")
    public String generate(RecordSet rs, String ruleCode) {
        return new CodeRuleService().generate(ruleCode);
    }

    /**
     * 预览下一个业务编码（不占用流水号）。
     */
    @MethodService(name = "preview", displayName = "预览编码", auth = "read", description = "预览下一个业务编码")
    public String preview(RecordSet rs, String ruleCode) {
        return new CodeRuleService().preview(ruleCode);
    }

    public CodeRule setRuleCode(String ruleCode) {
        this.set("ruleCode", ruleCode);
        return this;
    }

    public String getRuleCode() {
        return getStr("ruleCode");
    }

    public CodeRule setRuleName(String ruleName) {
        this.set("ruleName", ruleName);
        return this;
    }

    public String getRuleName() {
        return getStr("ruleName");
    }

    public CodeRule setPrefix(String prefix) {
        this.set("prefix", prefix);
        return this;
    }

    public String getPrefix() {
        return getStr("prefix");
    }

    public CodeRule setSeqLength(Integer seqLength) {
        this.set("seqLength", seqLength);
        return this;
    }

    public Integer getSeqLength() {
        return getInt("seqLength");
    }

    public CodeRule setDateFormat(String dateFormat) {
        this.set("dateFormat", dateFormat);
        return this;
    }

    public String getDateFormat() {
        return getStr("dateFormat");
    }

    public CodeRule setSeparator(String separator) {
        this.set("separator", separator);
        return this;
    }

    public String getSeparator() {
        return getStr("separator");
    }

    public CodeRule setEnabled(String enabled) {
        this.set("enabled", enabled);
        return this;
    }

    public String getEnabled() {
        return getStr("enabled");
    }
}
