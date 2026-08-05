#!/usr/bin/env python3
"""Render the daily three-trend payload with the MckEngine design skill.

The renderer is intentionally data-first: Goal 9 writes ``daily-trends.json``
and this script turns that same payload into a three-slide PPTX plus 16:9 PNGs.
The generated project folder also preserves the Mck harness artifacts and gate
results, so a visual can be reviewed or regenerated without re-running news
collection.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any, Dict, Iterable, List


def resolve_skill_dir() -> Path:
    candidates = [
        os.environ.get("MCK_PPT_SKILL_PATH", ""),
        os.path.expanduser("~/.workbuddy/skills/mck-ppt-design"),
        os.path.expanduser("~/.codex/skills/mck-ppt-design-skill"),
    ]
    for candidate in candidates:
        if candidate and (Path(candidate) / "mck_ppt").is_dir():
            return Path(candidate).resolve()
    raise RuntimeError(
        "Mck PPT skill not found. Set MCK_PPT_SKILL_PATH or install "
        "likaku/Mck-ppt-design-skill."
    )


SKILL_DIR = resolve_skill_dir()
if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))

from mck_ppt import MckEngine  # noqa: E402
from mck_ppt.constants import (  # noqa: E402
    ACCENT_BLUE,
    ACCENT_GREEN,
    ACCENT_ORANGE,
    ACCENT_RED,
    Inches,
)


SIGNAL_COLORS = {"🔴": ACCENT_RED, "🟡": ACCENT_ORANGE, "⚪": ACCENT_BLUE}


def compact(value: Any, limit: int = 42) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    if len(text) <= limit:
        return text
    return text[: max(1, limit - 1)].rstrip() + "…"


def as_evidence_rows(items: Iterable[Any]) -> List[List[str]]:
    rows: List[List[str]] = []
    for item in list(items)[:4]:
        if isinstance(item, dict):
            title = item.get("title") or item.get("label") or item.get("source") or "未命名佐证"
            signal = item.get("signal") or item.get("signal_level") or "🟡"
            status = "已核验" if item.get("verified") or item.get("cross_validated") else "待复核"
        else:
            title, signal, status = item, "🟡", "已进入判断"
        rows.append([compact(title, 30), signal, status])
    while len(rows) < 3:
        rows.append(["基于多源信号判断", "—", "待补充"])
    return rows


def normalize_payload(raw: Dict[str, Any]) -> Dict[str, Any]:
    trends = raw.get("trends") or []
    if len(trends) != 3:
        raise ValueError(f"Mck daily trend renderer expects exactly 3 trends, got {len(trends)}")

    normalized: List[Dict[str, Any]] = []
    for index, trend in enumerate(trends, 1):
        evidence = trend.get("evidence") or trend.get("sources") or []
        signal = trend.get("signal") or trend.get("signal_level") or "🟡"
        normalized.append(
            {
                "index": index,
                "title": compact(trend.get("action_title") or trend.get("title"), 56),
                "core": compact(trend.get("core") or trend.get("desc") or trend.get("summary"), 260),
                "critical": compact(
                    trend.get("critical")
                    or "真正变化的是底层约束，而不是发布数量；先把证据与采用信号分开。",
                    220,
                ),
                "next_watch": compact(
                    trend.get("next_watch")
                    or "观察产品采用、价格变化、开发者迁移或客户续费等可验证信号。",
                    150,
                ),
                "evidence": evidence,
                "signal": signal,
                "variable": compact(trend.get("variable") or "结构变量", 18),
                "source": trend.get("source") or raw.get("source") or "AI News Digest daily report",
            }
        )
    return {
        "schema_version": raw.get("schema_version", "1.0"),
        "date": raw.get("date") or "unknown-date",
        "title": raw.get("title") or "AI 日报每日关键趋势",
        "source_markdown": raw.get("source_markdown", "daily-report.md"),
        "trends": normalized,
    }


def build_harness_files(payload: Dict[str, Any], project_dir: Path) -> None:
    project_dir.mkdir(parents=True, exist_ok=True)
    date = payload["date"]
    brief = (
        f"# AI 日报每日关键趋势 · {date}\n\n"
        "- audience: AI 行业研究、产品与运营团队\n"
        "- goal: 用同一份趋势判断生成可核验的咨询式视觉资产\n"
        "- key_messages: 3 条趋势，每条包含佐证、结构判断与下周观察\n"
    )
    (project_dir / "brief.md").write_text(brief, encoding="utf-8")

    slides = []
    for trend in payload["trends"]:
        rows = as_evidence_rows(trend["evidence"])
        slides.append(
            {
                "idx": trend["index"],
                "layout": "table_insight",
                "title": trend["title"],
                "headers": ["关键佐证", "信号", "证据状态"],
                "rows": rows,
                "insights": [
                    f"核心判断：{trend['critical']}",
                    f"下周观察：{trend['next_watch']}",
                ],
                "source": trend["source"],
            }
        )

    outline = {
        "brief": {"audience": "AI 行业团队", "goal": "每日趋势判断可视化", "duration_minutes": 3},
        "slides": [
            {"idx": slide["idx"], "layout": slide["layout"], "title": slide["title"], "key_point": slide["title"]}
            for slide in slides
        ],
    }
    content = {"date": date, "slides": slides}
    (project_dir / "outline.json").write_text(json.dumps(outline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (project_dir / "content.json").write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_gate(script: Path, *args: str) -> Dict[str, Any]:
    subprocess.run([sys.executable, str(script), *args], check=True)
    output = Path(args[-1]) / ("gate_s3.json" if script.name.endswith("s3.py") else "gate_result.json")
    result = json.loads(output.read_text(encoding="utf-8"))
    if not result.get("passed"):
        raise RuntimeError(f"Mck gate failed: {output}\n{json.dumps(result, ensure_ascii=False, indent=2)}")
    return result


def render_ppt(payload: Dict[str, Any], project_dir: Path) -> Path:
    deck_path = project_dir / f"ai-daily-{payload['date']}-mck.pptx"
    engine = MckEngine(total_slides=3)
    for trend in payload["trends"]:
        signal = trend["signal"] if trend["signal"] in SIGNAL_COLORS else "🟡"
        source = compact(trend["source"], 110)
        engine.table_insight(
            title=trend["title"],
            headers=["关键佐证", "信号", "证据状态"],
            rows=as_evidence_rows(trend["evidence"]),
            insights=[
                f"核心判断：{trend['critical']}",
                f"下周观察：{trend['next_watch']}",
            ],
            col_widths=[Inches(3.8), Inches(1.1), Inches(2.3)],
            insight_title=f"结构判断 · {trend['variable']}",
            source=source,
            bottom_bar=("信号", f"{signal}  ·  {trend['variable']}  ·  关键判断见右侧"),
        )
    engine.save(str(deck_path))
    patch_cjk_font(deck_path)
    return deck_path


def patch_cjk_font(deck_path: Path) -> None:
    """Map the upstream KaiTi default to a font available to macOS/LibreOffice.

    The PPTX still keeps the upstream skill unchanged; this only makes local
    PNG export deterministic when KaiTi is not installed in the renderer.
    """
    temporary = deck_path.with_suffix(".fontfix.pptx")
    with zipfile.ZipFile(deck_path, "r") as source, zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED) as target:
        for item in source.infolist():
            data = source.read(item.filename)
            if item.filename.endswith(".xml"):
                data = data.replace(b"KaiTi", b"Arial Unicode MS")
            target.writestr(item, data)
    temporary.replace(deck_path)


def export_pngs(deck_path: Path, project_dir: Path) -> List[str]:
    soffice = os.environ.get("SOFFICE_BIN") or shutil.which("soffice")
    pdftoppm = os.environ.get("PDFTOPPM_BIN") or shutil.which("pdftoppm")
    if not soffice or not pdftoppm:
        raise RuntimeError("PPTX generated, but soffice/pdftoppm is required to export PNGs")

    pdf_dir = project_dir / "pdf"
    pdf_dir.mkdir(exist_ok=True)
    render_env = os.environ.copy()
    soffice_path = Path(soffice).resolve()
    fontconfig_candidates = [
        soffice_path.parent.parent / "Resources" / "fontconfig" / "fonts.conf",
        soffice_path.parents[2] / "native/libreoffice-headless/libreoffice/LibreOfficeDev.app/Contents/Resources/fontconfig/fonts.conf",
    ]
    for bundled_fontconfig in fontconfig_candidates:
        if bundled_fontconfig.exists():
            render_env["FONTCONFIG_FILE"] = str(bundled_fontconfig)
            break
    subprocess.run(
        [soffice, "--headless", "--convert-to", "pdf", "--outdir", str(pdf_dir), str(deck_path)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=render_env,
    )
    pdf_path = pdf_dir / f"{deck_path.stem}.pdf"
    if not pdf_path.exists():
        raise RuntimeError(f"LibreOffice did not create {pdf_path}")

    output_paths: List[str] = []
    for index in range(1, 4):
        base = project_dir / f"trend-{index}-mck"
        subprocess.run(
            [pdftoppm, "-png", "-r", "144", "-f", str(index), "-l", str(index), str(pdf_path), str(base)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        candidates = sorted(project_dir.glob(f"trend-{index}-mck-*.png"))
        if not candidates:
            raise RuntimeError(f"No PNG exported for slide {index}")
        exported = candidates[0]
        target = project_dir / f"trend-{index}-mck.png"
        if exported != target:
            exported.replace(target)
        output_paths.append(str(target))
    return output_paths


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trends-json", required=True, help="Goal 9 daily-trends.json")
    parser.add_argument("--out-dir", required=True, help="Directory for PPTX, PNGs and harness artifacts")
    args = parser.parse_args()

    input_path = Path(args.trends_json).resolve()
    project_dir = Path(args.out_dir).resolve()
    payload = normalize_payload(json.loads(input_path.read_text(encoding="utf-8")))
    build_harness_files(payload, project_dir)

    run_gate(SKILL_DIR / "references/scripts/gate_check_s3.py", str(project_dir / "content.json"), str(project_dir))
    deck_path = render_ppt(payload, project_dir)
    run_gate(SKILL_DIR / "references/scripts/gate_check.py", str(deck_path), str(project_dir))
    pngs = export_pngs(deck_path, project_dir)

    manifest = {
        "renderer": "mck-ppt-design",
        "skill_dir": str(SKILL_DIR),
        "input": str(input_path),
        "date": payload["date"],
        "pptx": str(deck_path),
        "pngs": pngs,
        "aspect_ratio": "16:9",
        "gate_s3": str(project_dir / "gate_s3.json"),
        "gate_s4": str(project_dir / "gate_result.json"),
    }
    (project_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
