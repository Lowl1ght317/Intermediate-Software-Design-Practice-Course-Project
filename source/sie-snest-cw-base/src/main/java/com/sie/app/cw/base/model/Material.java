package com.sie.app.cw.base.model;

import com.sie.snest.engine.model.Bool;
import com.sie.snest.sdk.BaseModel;
import com.sie.snest.sdk.annotation.meta.Model;
import com.sie.snest.sdk.annotation.meta.Property;
import com.sie.snest.sdk.annotation.orm.Option;
import com.sie.snest.sdk.annotation.orm.Selection;
import com.sie.snest.sdk.annotation.validate.Validate;

/**
 * 文创生产物料（徽章底座、帆布、油墨、包装袋等）
 */
@Model(name = "material", tableName = "cw_material", description = "文创生产物料", displayName = "物料", isAutoLog = Bool.True)
public class Material extends BaseModel<Material> {

    @Validate.NotBlank(message = "物料名称不能为空！")
    @Property(displayName = "物料名称", displayForModel = true)
    private String name;

    @Validate.NotBlank(message = "物料编码不能为空！")
    @Property(displayName = "物料编码", unique = true)
    private String code;

    @Property(displayName = "规格")
    private String spec;

    @Property(displayName = "计量单位", defaultValue = "个", widget = "select", length = 64)
    @Selection(values = {
            @Option(label = "个", value = "个"),
            @Option(label = "米", value = "米"),
            @Option(label = "千克", value = "千克"),
            @Option(label = "毫升", value = "毫升"),
            @Option(label = "套", value = "套"),
            @Option(label = "张", value = "张")
    })
    private String unit;

    public Material setName(String name) {
        this.set("name", name);
        return this;
    }

    public String getName() {
        return getStr("name");
    }

    public Material setCode(String code) {
        this.set("code", code);
        return this;
    }

    public String getCode() {
        return getStr("code");
    }

    public Material setSpec(String spec) {
        this.set("spec", spec);
        return this;
    }

    public String getSpec() {
        return getStr("spec");
    }

    public Material setUnit(String unit) {
        this.set("unit", unit);
        return this;
    }

    public String getUnit() {
        return getStr("unit");
    }

    // ---------- 业务服务入口（引擎只把 @Model 类上的 @MethodService 注册为模型服务） ----------

    @com.sie.snest.sdk.annotation.meta.MethodService(name = "createWithCode", displayName = "新建物料并生成编码", auth = "create")
    public Material createWithCode(com.sie.snest.engine.data.RecordSet rs, String name, String spec, String unit) {
        return new com.sie.app.cw.base.service.MaterialService().createWithCode(rs, name, spec, unit);
    }

    @com.sie.snest.sdk.annotation.meta.MethodService(name = "findByCode", displayName = "按编码查物料", auth = "read")
    public Material findByCode(com.sie.snest.engine.data.RecordSet rs, String code) {
        return new com.sie.app.cw.base.service.MaterialService().findByCode(rs, code);
    }
}