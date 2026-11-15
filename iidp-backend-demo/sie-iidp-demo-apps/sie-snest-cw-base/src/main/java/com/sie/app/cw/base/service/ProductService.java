package com.sie.app.cw.base.service;

import com.sie.app.cw.base.model.Material;
import com.sie.app.cw.base.model.Product;
import com.sie.app.cw.base.model.ProductBom;
import com.sie.snest.engine.data.RecordSet;
import com.sie.snest.engine.model.Bool;
import com.sie.snest.engine.data.access.ModelDataAccessFactory;
import com.sie.snest.engine.db.relationdb.RelationDBAccessor;
import com.sie.snest.engine.rule.Filter;
import com.sie.snest.sdk.annotation.meta.MethodService;
import com.sie.snest.sdk.annotation.meta.Service;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * 文创产品业务服务。
 * <p>
 * 这里的服务承担两件模型层做不到的事：
 * 1) 新建产品时调用 cw-sys 的编码服务取号，保证“业务模型编码由编码规则生成”；
 * 2) BOM 明细作为子表随主表一起保存，保存前做“同物料重复”与“用量大于 0”的校验。
 */
@Service(name = "productService", path = ProductService.class, targets = {"product"}, description = "文创产品业务服务")
public class ProductService {

    private static final Logger log = LoggerFactory.getLogger(ProductService.class);

    /** 产品编码使用的规则标识，与 cw_code_rule.rule_code 对应 */
    private static final String PRODUCT_RULE = "CP";

    private static final List<String> PRODUCT_PROPS = Arrays.asList(
            "code", "name", "spec", "status");

    private static final List<String> BOM_PROPS = Arrays.asList(
            "product", "material", "amount");

    /**
     * 新建产品：编码由编码服务生成，名称非空由模型注解校验。
     *
     * @param rs     调用上下文
     * @param name   产品名称
     * @param spec   规格
     * @param status 状态，默认设计中的 1
     * @return 新建的产品（含 code）
     */
    @MethodService(name = "createWithCode", displayName = "新建产品并生成编码", auth = "create")
    public Product createWithCode(RecordSet rs, String name, String spec, String status) {
        String code = CodeGenFacade.generate(PRODUCT_RULE);
        Product product = new Product();
        product.setCode(code);
        product.setName(name);
        product.setSpec(spec);
        product.setStatus(status == null || status.isEmpty() ? "1" : status);
        Product created = product.create();
        log.info("新建产品 {} 编码 {}", name, code);
        return created;
    }

    /**
     * 给产品追加一条 BOM 明细，重复物料与非法用量在此拦截。
     *
     * @param rs          调用上下文
     * @param productCode 产品编码
     * @param materialCode 物料编码
     * @param amount      用量
     * @return 保存后的 BOM 明细
     */
    @MethodService(name = "addBom", displayName = "追加BOM明细", auth = "update")
    public ProductBom addBom(RecordSet rs, String productCode, String materialCode, Integer amount) {
        if (amount == null || amount <= 0) {
            throw new IllegalArgumentException("用量必须大于 0");
        }
        Product product = new Product().select(Filter.equal("code", productCode), "id", "code", "name");
        if (product == null) {
            throw new IllegalArgumentException("产品不存在：" + productCode);
        }
        Material material = new Material().select(Filter.equal("code", materialCode), "id", "code", "name");
        if (material == null) {
            throw new IllegalArgumentException("物料不存在：" + materialCode);
        }
        // 关联字段过滤走原生 SQL：@ManyToOne 属性在 SDK 的 Filter 里匹配不到行（实测返回空），
        // 直接用列名 product / material 判断更可靠。
        if (existsBom(product.getId(), material.getId())) {
            throw new IllegalArgumentException("物料已存在，请修改用量");
        }
        ProductBom bom = new ProductBom();
        // 关联字段写主键字符串：传 BaseModel 实例会让 ORM 在序列化关系对象时抛 NotSerializableException
        bom.set("product", product.getId());
        bom.set("material", material.getId());
        bom.setAmount(amount);
        return bom.create();
    }


    /** 是否已存在同一产品同一物料的 BOM 行（原生 SQL，按列名过滤）。 */
    private boolean existsBom(String productId, String materialId) {
        RelationDBAccessor accessor = ModelDataAccessFactory.getBussDataRelDBAccessor();
        accessor.execute("SELECT id FROM cw_product_bom WHERE product = '" + escape(productId)
                + "' AND material = '" + escape(materialId) + "' LIMIT 1");
        java.util.Map<String, Object> row = accessor.fetchMapOne();
        return row != null && !row.isEmpty();
    }

    /** 统计某产品的 BOM 行数。 */
    private int countBom(String productId) {
        RelationDBAccessor accessor = ModelDataAccessFactory.getBussDataRelDBAccessor();
        accessor.execute("SELECT COUNT(*) AS c FROM cw_product_bom WHERE product = '" + escape(productId) + "'");
        java.util.Map<String, Object> row = accessor.fetchMapOne();
        if (row == null || row.get("c") == null) {
            return 0;
        }
        return ((Number) row.get("c")).intValue();
    }

    private String escape(String value) {
        return value == null ? "" : value.replace("'", "''");
    }

    /**
     * BOM 校验：至少要有一行明细，用量必须大于 0。
     *
     * @param rs          调用上下文
     * @param productCode 产品编码
     * @return 校验结果，ok=true 表示可以提交
     */
    @MethodService(name = "checkBom", displayName = "校验产品BOM", auth = "read")
    public Map<String, Object> checkBom(RecordSet rs, String productCode) {
        Map<String, Object> result = new LinkedHashMap<>();
        Product product = new Product().select(Filter.equal("code", productCode), "id", "code");
        if (product == null) {
            result.put("ok", Bool.False);
            result.put("message", "产品不存在：" + productCode);
            return result;
        }
        int count = countBom(product.getId());
        boolean ok = count > 0;
        result.put("ok", ok ? Bool.True : Bool.False);
        result.put("count", count);
        result.put("message", ok ? "校验通过，共 " + count + " 行 BOM" : "请至少添加一行 BOM 明细");
        return result;
    }
    /** 调试用：返回按编码解析出的产品主键与 BOM 行数，便于定位分页/关联字段问题。 */
    @MethodService(name = "debugBom", displayName = "调试BOM查询", auth = "read")
    public Map<String, Object> debugBom(RecordSet rs, String productCode) {
        Map<String, Object> out = new LinkedHashMap<>();
        Product product = new Product().select(Filter.equal("code", productCode), "id", "code", "name");
        out.put("productFound", product != null);
        out.put("productId", product == null ? null : product.getId());
        if (product == null) {
            return out;
        }
        for (int ps : new int[]{0, 10, 1000}) {
            List<ProductBom> list = new ProductBom().search(
                    Filter.equal("product", product.getId()), BOM_PROPS, 1, ps, null);
            out.put("size_" + ps, list == null ? -1 : list.size());
        }
        List<ProductBom> all = new ProductBom().search(null, BOM_PROPS, 1, 1000, null);
        out.put("all", all == null ? -1 : all.size());
        return out;
    }
}
