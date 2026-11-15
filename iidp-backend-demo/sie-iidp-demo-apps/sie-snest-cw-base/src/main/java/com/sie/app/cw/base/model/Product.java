package com.sie.app.cw.base.model;

import com.sie.snest.engine.model.Bool;
import com.sie.snest.sdk.BaseModel;
import com.sie.snest.sdk.annotation.meta.Model;
import com.sie.snest.engine.data.RecordSet;
import com.sie.snest.sdk.annotation.meta.MethodService;
import com.sie.snest.sdk.annotation.meta.Property;
import com.sie.snest.sdk.annotation.orm.OneToMany;
import com.sie.snest.sdk.annotation.orm.Option;
import com.sie.snest.sdk.annotation.orm.Selection;
import com.sie.snest.sdk.annotation.validate.Validate;

import java.util.List;

/**
 * 校园文创产品（校徽徽章、帆布包、明信片、马克杯等）
 */
@Model(name = "product", tableName = "cw_product", description = "校园文创产品", displayName = "文创产品", isAutoLog = Bool.True)
public class Product extends BaseModel<Product> {

    @Validate.NotBlank(message = "产品名称不能为空！")
    @Property(displayName = "产品名称", displayForModel = true)
    private String name;

    @Property(displayName = "产品编码", unique = true, readonly = true, displayForModel = true)
    private String code;

    @Property(displayName = "规格")
    private String spec;

    @Property(displayName = "产品状态", defaultValue = "1", widget = "select", length = 256)
    @Selection(values = {
            @Option(label = "设计中", value = "1"),
            @Option(label = "打样中", value = "2"),
            @Option(label = "批量制作", value = "3"),
            @Option(label = "已入库", value = "4")
    })
    private String status;

    @OneToMany
    private List<ProductBom> productBomList;

    public Product setName(String name) {
        this.set("name", name);
        return this;
    }

    public String getName() {
        return getStr("name");
    }

    public Product setCode(String code) {
        this.set("code", code);
        return this;
    }

    public String getCode() {
        return getStr("code");
    }

    public Product setSpec(String spec) {
        this.set("spec", spec);
        return this;
    }

    public String getSpec() {
        return getStr("spec");
    }

    public Product setStatus(String status) {
        this.set("status", status);
        return this;
    }

    public String getStatus() {
        return getStr("status");
    }

    public Product setProductBomList(List<ProductBom> productBomList) {
        this.set("productBomList", productBomList);
        return this;
    }

    @SuppressWarnings("unchecked")
    public List<ProductBom> getProductBomList() {
        return (List<ProductBom>) this.get("productBomList");
    }

    // ---------- 业务服务入口（引擎只把 @Model 类上的 @MethodService 注册为模型服务） ----------

    @MethodService(name = "createWithCode", displayName = "新建产品并生成编码", auth = "create")
    public Product createWithCode(RecordSet rs, String name, String spec, String status) {
        return new com.sie.app.cw.base.service.ProductService().createWithCode(rs, name, spec, status);
    }

    @MethodService(name = "addBom", displayName = "追加BOM明细", auth = "update")
    public ProductBom addBom(RecordSet rs, String productCode, String materialCode, Integer amount) {
        return new com.sie.app.cw.base.service.ProductService().addBom(rs, productCode, materialCode, amount);
    }

    @MethodService(name = "checkBom", displayName = "校验产品BOM", auth = "read")
    public java.util.Map<String, Object> checkBom(RecordSet rs, String productCode) {
        return new com.sie.app.cw.base.service.ProductService().checkBom(rs, productCode);
    }

    /**
     * 重写平台自带的 create：界面上的「新增」也走编码服务取号。
     * <p>
     * 不重写时，界面新增走的是平台 create，code 由前端传入（通常为空），
     * 结果列表里出现没有编码的产品，与“业务编码由编码规则生成”的要求冲突。
     * 这里先把空编码补齐，再交回给父服务做真正的落库。
     */
    @MethodService(name = "create", displayName = "新增产品", auth = "create")
    public RecordSet create(List<java.util.Map<String, Object>> valuesList) {
        if (valuesList != null) {
            for (java.util.Map<String, Object> values : valuesList) {
                Object code = values.get("code");
                if (code == null || String.valueOf(code).trim().isEmpty()) {
                    values.put("code", com.sie.app.cw.base.service.CodeGenFacade.generate("CP"));
                }
            }
        }
        return (RecordSet) getMeta().get("product").callSuper(Product.class, "create", valuesList);
    }
}