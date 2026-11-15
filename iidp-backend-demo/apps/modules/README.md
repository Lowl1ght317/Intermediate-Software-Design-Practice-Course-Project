# apps/modules —— 引擎启动时扫描的 APP 目录

这个目录里的 jar 会被引擎逐个解析并注册成 APP。**jar 不入库**（二进制、体积大、且平台官方包由课程提供），克隆下来后按下面清单放齐即可。

## 需要的 jar

课程环境提供的 11 个官方包（版本以课程发的 `apps/modules` 为准）：

```
sie-iidp-app-store-app-v3.0.1-RELEASE.jar
sie-iidp-cache-v3.0.1-RELEASE.jar
sie-iidp-config-v3.0.1-RELEASE.jar
sie-iidp-dev-center-v3.0.0-RELEASE.jar
sie-iidp-dict-v3.0.0-RELEASE.jar
sie-iidp-file-v3.0.1-RELEASE.jar
sie-iidp-i18n-v3.0.0-RELEASE.jar
sie-iidp-iam-v3.0.1-HOTFIX.001.jar
sie-iidp-log-v3.0.1-RELEASE.jar
sie-iidp-tenant-v3.0.1-RELEASE.jar
sie-iidp-user-prefer-v3.0.0-RELEASE.jar
```

自研的三个包由 `mvn package` 自动复制进来（`sie-snest-maven-plugin` 的 `copyDir`）：

```
sie-snest-cw-base-1.0-SNAPSHOT.jar
sie-snest-cw-prod-1.0-SNAPSHOT.jar
sie-snest-cw-sys-1.0-SNAPSHOT.jar
```

## 一个重要坑

**不要**把同一 APP 的多个版本（例如 `-RELEASE` 与 `-UAT.001` 并存）或示例工程的 `sie-snest-mes-1.0-SNAPSHOT.jar` 一起放进来。

引擎启动时 `SingleAppLoader.listLocalAppsByJson()` 解析出的列表里会出现 `null` 元素，接着在 `AppProcessor.toMap()` 抛 `NullPointerException`，表现为"启动即崩"。清理成"11 个官方 RELEASE + 3 个自研"即可。
