# 桌面壳产品标识占位为 com.metacontrol.ai

productIdentifier（及 productName=元控智能、companyName=MetaControl AI）是应用在 Windows 卸载注册表与安装器元数据里的"身份证号"，装机后再更改会导致新旧两版并排安装而非覆盖升级。决策：占位阶段统一用 `com.metacontrol.ai`（2026-10-14 敲定，随演示版开发引入）；公司正式域名确定后、对外大规模分发**之前**替换一次（届时零存量装机，无痛）。规则：一旦有存量装机，identifier 冻结不再改。壳图标资产从 openclaw 项目 LOGO 母版（D:\openclaw\openclaw\img\LOGO.png）加工，正式 VI 出来后只换图重打包。
