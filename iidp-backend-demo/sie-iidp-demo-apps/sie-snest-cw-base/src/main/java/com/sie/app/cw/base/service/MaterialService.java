package com.sie.app.cw.base.service;

import com.sie.app.cw.base.model.Material;
import com.sie.snest.engine.data.RecordSet;
import com.sie.snest.engine.rule.Filter;
import com.sie.snest.sdk.annotation.meta.MethodService;
import com.sie.snest.sdk.annotation.meta.Service;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * 物料业务服务：编码由编码规则生成，物料编码全库唯一。
 * <p>
 * 平台自带的 create 服务在本机引擎版本下取不到记录列表（BussModelDataAccess.create 抛空指针），
 * 因此新增物料也走自定义服务，与产品保持一致。
 */
@Service(name = "materialService", path = MaterialService.class, targets = {"material"}, description = "物料业务服务")
public class MaterialService {

    private static final Logger log = LoggerFactory.getLogger(MaterialService.class);

    private static final String MATERIAL_RULE = "MT";

    /**
     * 新建物料。
     *
     * @param rs    调用上下文
     * @param name  物料名称
     * @param spec  规格
     * @param unit  计量单位
     * @return 新建的物料
     */
    @MethodService(name = "createWithCode", displayName = "新建物料并生成编码", auth = "create")
    public Material createWithCode(RecordSet rs, String name, String spec, String unit) {
        if (name == null || name.trim().isEmpty()) {
            throw new IllegalArgumentException("物料名称不能为空！");
        }
        Material material = new Material();
        material.setCode(CodeGenFacade.generate(MATERIAL_RULE));
        material.setName(name.trim());
        material.setSpec(spec == null ? "" : spec.trim());
        material.setUnit(unit == null || unit.trim().isEmpty() ? "个" : unit.trim());
        Material created = material.create();
        log.info("新建物料 {} {}", created.getCode(), name);
        return created;
    }

    /**
     * 按编码查物料，供 BOM 维护时校验物料是否存在。
     *
     * @param rs   调用上下文
     * @param code 物料编码
     * @return 物料，不存在返回 null
     */
    @MethodService(name = "findByCode", displayName = "按编码查物料", auth = "read")
    public Material findByCode(RecordSet rs, String code) {
        if (code == null || code.trim().isEmpty()) {
            throw new IllegalArgumentException("物料编码不能为空！");
        }
        Material probe = new Material();
        java.util.List<Material> rows = probe.search(Filter.equal("code", code.trim()),
                java.util.Arrays.asList("code", "name", "spec", "unit", "status"), 1, 1, null);
        return rows == null || rows.isEmpty() ? null : rows.get(0);
    }
}
