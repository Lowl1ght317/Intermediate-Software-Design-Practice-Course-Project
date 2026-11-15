package com.sie.app.cw.base.model;

import com.sie.snest.engine.model.Bool;
import com.sie.snest.sdk.BaseModel;
import com.sie.snest.sdk.annotation.meta.Model;
import com.sie.snest.sdk.annotation.meta.Property;
import com.sie.snest.sdk.annotation.orm.JoinColumn;
import com.sie.snest.sdk.annotation.orm.ManyToOne;

/**
 * 产品BOM：每件文创产品的物料用量
 */
@Model(name = "product_bom", tableName = "cw_product_bom", description = "产品BOM", displayName = "产品BOM", isAutoLog = Bool.True)
public class ProductBom extends BaseModel<ProductBom> {

    @ManyToOne(displayName = "产品")
    @JoinColumn
    private Product product;

    @ManyToOne(displayName = "物料")
    @JoinColumn
    private Material material;

    @Property(displayName = "用量")
    private Integer amount;

    public ProductBom setProduct(Product product) {
        this.set("product", product);
        return this;
    }

    public Product getProduct() {
        return (Product) this.get("product");
    }

    public ProductBom setMaterial(Material material) {
        this.set("material", material);
        return this;
    }

    public Material getMaterial() {
        return (Material) this.get("material");
    }

    public ProductBom setAmount(Integer amount) {
        this.set("amount", amount);
        return this;
    }

    public Integer getAmount() {
        return getInt("amount");
    }
}
