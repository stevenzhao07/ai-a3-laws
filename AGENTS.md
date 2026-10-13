# AGENTS.md · ai-a3-laws

> 机器可发现入口（AI 编码代理 / Codex / Claude / Cursor）。单一事实源：本文件。

## 这是什么
把「立法者（A³ Laws）」理念工程化为可部署的运行时约束库：对每一次自主决策做三定律校验——A1 权限边界（Authority）、A2 自主边界（人类监督）、A3 追责边界（可归因日志）。返回违规清单，可嵌入门禁或 Agent 循环。（对应『运行时约束』能力缺口。）

## 运行
```bash
python scripts/a3_laws.py --demo
python scripts/a3_laws.py --help
```

## 扩展契约（lgd-skeleton/1.0）
- **一切即插件**：仅依赖声明式 `module.json`，零配置。
- **按需装（lazy）**：仅 triggers 命中时加载。
- **可嵌套（nested）**：可被 `medical-ai-toolkit` 总入口路由。
- **扩展点**：`plugins/`(新增定律：在 `LAWS` 注册表加一个 `(law_id, fn)` 即可，主流程自动遍历。)

## 红线
纯技术贡献，不含商业营销；MedXpert 仅作为贡献者署名（@stevenzhao07）。
