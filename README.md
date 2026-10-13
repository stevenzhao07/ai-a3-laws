# ai-a3-laws

> **Contributed by [@stevenzhao07](https://github.com/stevenzhao07) · Affiliation: MedXpert (medical-device RA & regulatory consultancy) · Pure technical input, no commercial promotion.**

把「立法者（A³ Laws）」理念工程化为可部署的运行时约束库：对每一次自主决策做三定律校验——A1 权限边界（Authority）、A2 自主边界（人类监督）、A3 追责边界（可归因日志）。返回违规清单，可嵌入门禁或 Agent 循环。（对应『运行时约束』能力缺口。）

这是 MedXpert 把"医疗 AI 信任"方法论工程化落地的可插拔模块之一——把抽象的合规要求变成一条可重复运行的命令或参考实现。方法论四要素（白话版）：**治理守护者 XCGS** ＝ 为 AI 留下可核验的治理证据；**立法者 A³ Laws** ＝ 给自主系统划权限 / 监督 / 追责三条硬边界；**护照官 AI 护照** ＝ 为模型签发可追溯的身份凭证；**人机共存** ＝ 明确人类与 AI 的分工与兜底。

---

## 可插拔模块契约（lgd-skeleton/1.0）

本仓库是一个 **`lgd-skeleton/1.0` 可插拔模块**：

- **一切即插件**：仅依赖声明式 `module.json`，零配置；
- **按需装（lazy）**：仅 triggers 命中时加载；
- **可嵌套（nested）**：可被 `medical-ai-toolkit` 总入口路由发现；
- **扩展点**：`plugins/`(新增定律：在 `LAWS` 注册表加一个 `(law_id, fn)` 即可，主流程自动遍历。)。

机器可发现入口：`AGENTS.md` · `CLAUDE.md` · `llms.txt`。

## 特性

- 三条定律：`A1 Authority`（动作须在 authority_scope 白名单）、`A2 Autonomy`（高风险动作须 human_review=True）、`A3 Accountability`（须含 actor_id + decision_id 且可日志）
- 零依赖：仅 Python 3.8+ 标准库
- 可嵌门禁：`A3Guard.check(decision)` 返回 `list[Violation]`，退出码友好
- CLI：`python scripts/a3_laws.py --demo` 跑内置样例

**上游投稿目标**：OWASP AI Exchange

## 内容说明

A¹/A²/A³ 三定律对应「立法者」方法论：给自主系统划安全边界，而不是事后审计。它不自称标准，定位为可复用的参考实现，欢迎上游（OWASP AI Exchange）采纳。

## 免责声明

本工具仅提供结构化模板与计算能力，**不构成法规建议、合规结论或专业意见**。医疗 AI / 医疗器械相关的落地决策，须由合资格人员依据目标辖区（NMPA / FDA / EU MDR / PMDA）最新法规文本作出；条款与限值以官方发布文本为准。使用本工具产生的一切后果由使用者自行承担。

## 使用

```bash
# 跑内置样例（展示「通过 / 阻断」两种结果）
python scripts/a3_laws.py --demo
```

也可用 `--json` 传入自定义决策做校验（须为 JSON 对象）：

```bash
python scripts/a3_laws.py --json '{"action":"prescribe","authority_scope":["prescribe"],"actor_id":"agent-1","decision_id":"d-1","human_review":true}'
# 退出码：0 = 无违规；1 = 有违规（逐条打印）；2 = 输入非法（非 JSON / 非对象）
```

字段：`action`（动作）、`authority_scope`（A1 授权白名单）、`human_review`（A2，高风险动作须为 true）、`actor_id` / `decision_id`（A3 可追责标识）。

## 快速开始（30 秒）

```bash
git clone https://github.com/stevenzhao07/ai-a3-laws.git && cd ai-a3-laws
python scripts/a3_laws.py --demo
```

> 想参与或遇到问题？[提 Issue](https://github.com/stevenzhao07/ai-a3-laws/issues) · 完整《AI 参与指南》见 [medical-ai-toolkit](https://github.com/stevenzhao07/medical-ai-toolkit)。

## 路由（总入口）

本模块由 **[medical-ai-toolkit](https://github.com/stevenzhao07/medical-ai-toolkit)** 作为 `lgd-skeleton/1.0` 总入口自动路由发现。

## 关联模块

- [delivery-guard](https://github.com/stevenzhao07/delivery-guard)
- [ai-model-passport](https://github.com/stevenzhao07/ai-model-passport)
- [ai-governance-checklist](https://github.com/stevenzhao07/ai-governance-checklist)

## 许可

CC0 — 见 [LICENSE](./LICENSE)。

## 关联（方法论来源）

- 理念溯源：个人专家关于医疗 AI 信任与治理的公开方法论（个人观点，不构成标准）
- 同账号系列：见 `medical-ai-toolkit` 导航
