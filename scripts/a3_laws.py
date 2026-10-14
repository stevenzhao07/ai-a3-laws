#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
a3_laws.py — A³ Laws 运行时约束库
====================================
把「立法者（A³ Laws）」理念工程化为可部署的运行时约束：
  A1 Authority   权限边界：动作须落在 authority_scope 白名单
  A2 Autonomy     自主边界：高风险动作须 human_review=True（人类监督）
  A3 Accountability 追责边界：须含 actor_id + decision_id 且可日志

`A3Guard.check(decision)` 返回违规清单；可嵌入门禁或 Agent 循环。
零依赖（仅 Python 3.8+ 标准库）。（对应『运行时约束』能力缺口。）
"""
from __future__ import annotations
import sys
import argparse
import json

# 高风险动作白名单：除临床直接动作（prescribe/operate/approve/discard/
# override/release）外，模型生命周期动作 train/retrain/update 同样列为
# 高风险——训练、再训练与模型更新会改变系统行为分布，直接影响患者安全，
# 按 A2 自主边界须强制人类监督（human_review=True）。
HIGH_RISK_ACTIONS = {"prescribe", "operate", "approve", "discard", "override", "release",
                     "train", "retrain", "update"}


class Violation:
    def __init__(self, law: str, msg: str):
        self.law = law
        self.msg = msg

    def __repr__(self):
        return f"<{self.law}> {self.msg}"


def law_a1_authority(d: dict) -> Violation | None:
    action = d.get("action")
    scope = d.get("authority_scope") or []
    if action is None:
        return Violation("A1", "缺少 action 字段，无法判定权限边界")
    if isinstance(scope, str):
        scope = [scope]
    if action not in scope:
        return Violation("A1", f"动作 '{action}' 超出授权范围 {scope}")
    return None


def law_a2_autonomy(d: dict) -> Violation | None:
    action = d.get("action")
    if action in HIGH_RISK_ACTIONS and not d.get("human_review"):
        return Violation("A2", f"高风险动作 '{action}' 缺少人类监督(human_review=True)")
    return None


def law_a3_accountability(d: dict) -> Violation | None:
    missing = [k for k in ("actor_id", "decision_id") if not d.get(k)]
    if missing:
        return Violation("A3", f"缺少可追责标识: {missing}")
    return None


LAWS = [
    ("A1", law_a1_authority),
    ("A2", law_a2_autonomy),
    ("A3", law_a3_accountability),
]


class A3Guard:
    @staticmethod
    def check(decision: dict) -> list[Violation]:
        out = []
        for _lid, fn in LAWS:
            v = fn(decision)
            if v:
                out.append(v)
        return out


def _demo() -> int:
    samples = [
        {"action": "read", "authority_scope": ["read", "write"], "actor_id": "agent-1", "decision_id": "d-1"},
        {"action": "prescribe", "authority_scope": ["read"], "actor_id": "agent-1", "decision_id": "d-2", "human_review": True},
        {"action": "operate", "authority_scope": ["operate"], "decision_id": "d-3"},
    ]
    rc = 0
    for s in samples:
        vs = A3Guard.check(s)
        status = "PASS" if not vs else "BLOCK"
        print(f"[{status}] {json.dumps(s, ensure_ascii=False)}")
        for v in vs:
            print(f"    - {v}")
        if vs:
            rc = 1
    # demo 用于展示「通过 / 阻断」两种结果，统一退出 0（展示性质）
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="A³ Laws 运行时约束校验")
    ap.add_argument("--demo", action="store_true", help="跑内置样例")
    ap.add_argument("--selftest", action="store_true", help="跑内置自测（断言 + 负对照 + xfail）")
    ap.add_argument("--json", help="传入决策 JSON 字符串进行校验")
    args = ap.parse_args()
    if getattr(args, "selftest", False):
        return _selftest()
    if args.demo:
        return _demo()
    if args.json:
        try:
            d = json.loads(args.json)
        except ValueError as e:
            print(f"[error] --json 不是合法 JSON: {e}", file=sys.stderr)
            return 2
        if not isinstance(d, dict):
            print("[error] --json 须为 JSON 对象（决策 dict），例如 "
                  '{"action":"prescribe","authority_scope":["prescribe"],'
                  '"actor_id":"agent-1","decision_id":"d-1","human_review":true}',
                  file=sys.stderr)
            return 2
        vs = A3Guard.check(d)
        if vs:
            for v in vs:
                print(v)
            return 1
        # 无违规时给一行确认（2026-10-13：原静默 exit 0，外人视角像"没跑"）。
        print("[PASS] 无违规：决策通过 A1/A2/A3 三定律校验")
        return 0
    ap.print_help()
    return 2


# ==================== 内置自测（--selftest） ====================
# 由 conformance 补丁于 2026-10-14 生成（生成器 v2）。
# 特性：端到端 CLI 调用 + 内容断言 + 负对照 + xfail（已知缺陷显式标注，不掩盖）。
_SELFTEST_CASES = [(['--demo'], 0, [], [], None), (['--json', '{"action":"prescribe","authority_scope":["prescribe"],"actor_id":"a","decision_id":"d","human_review":true}'], 0, ['PASS'], [], None)]


def _selftest() -> int:
    import os as _os
    import subprocess as _sp
    _here = _os.path.dirname(_os.path.abspath(__file__))
    # 仓库根：脚本位于 <repo>/scripts/ 时取上一级；否则取脚本所在目录
    _root = _os.path.dirname(_here) if _os.path.basename(_here) == "scripts" else _here
    _script = _os.path.abspath(__file__)
    _fail, _xfail, _n = [], [], 0
    for _case in _SELFTEST_CASES:
        _args, _rc, _must, _mustnot = _case[0], _case[1], _case[2], _case[3]
        _reason = _case[4] if len(_case) > 4 else None
        _n += 1
        _p = _sp.run([sys.executable, _script] + _args, capture_output=True, cwd=_root)
        _out = _p.stdout.decode("utf-8", "replace")
        _bad = []
        if _p.returncode != _rc:
            _bad.append(f"rc={_p.returncode} 期望 {_rc}")
        for _m in _must:
            if _m not in _out:
                _bad.append(f"输出缺少 {_m!r}")
        for _m in _mustnot:
            if _m in _out:
                _bad.append(f"输出含禁止内容 {_m!r}")
        if _rc == 0 and not _out.strip():
            _bad.append("rc=0 但输出为空（假绿）")
        if _bad:
            if _reason:
                _xfail.append(f"xfail args={_args}：{'；'.join(_bad)} ← 已知缺陷：{_reason}")
            else:
                _fail.append(f"args={_args}：{'；'.join(_bad)}")
    # 通用负对照：未知参数必须非零
    _n += 1
    _p = _sp.run([sys.executable, _script, "--__nonexistent_flag__"], capture_output=True, cwd=_root)
    if _p.returncode == 0:
        _fail.append("负对照失败：未知参数竟返回 0")
    for _x in _xfail:
        print("[selftest][xfail] " + _x)
    if _fail:
        print(f"[selftest] FAILED {len(_fail)}/{_n}")
        for _f in _fail:
            print("  - " + _f)
        return 1
    print(f"[selftest] PASS {_n - len(_xfail)}/{_n}（含负对照；xfail {len(_xfail)} 项为已知缺陷）")
    return 0


if __name__ == "__main__":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    raise SystemExit(main())
