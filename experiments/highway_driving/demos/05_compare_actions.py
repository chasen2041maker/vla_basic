"""实验 05：同一起点的恒定动作对照；保存真实回放、日志与浏览器报告。"""
from __future__ import annotations

import html
import json
import math
import sys
import webbrowser
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from run_episode import run_episode

SEED = 7                 # 复现条件；零交通下改种子未必能改变速度响应。
MAX_STEPS = 40           # 本章只改这里为 5，比较观察时长和结束原因。
DURATION_S = 8.0         # 环境最多推进 8 秒；曲线横轴固定 0–8 秒。
OUTPUT_ROOT = Path(__file__).resolve().parents[3] / "outputs/highway_driving/compare-actions"
COLORS = {"IDLE": "#176fbd", "SLOWER": "#cc6815"}
END_LABELS = {
    "collision": "发生碰撞", "off_road": "驶离道路", "terminated": "环境终止",
    "environment_time_limit": "达到环境时间上限", "runner_step_limit": "用完脚本步数预算",
}


def speed_svg(runs: dict) -> str:
    """首点用真实动作前速率，之后每点配对动作后时间与动作后速率。"""
    series = {}
    for action, run in runs.items():
        first = run["summary"]["first_transition"]
        series[action] = [(first["observation_time_s"], first["speed_before_mps"])]
        series[action] += [(row["next_observation_time_s"], row["speed_mps"])
                           for row in run["trace"]]
    top = max(30.0, math.ceil(max(v for points in series.values() for _, v in points) / 5) * 5)
    svg = ['<svg viewBox="0 0 960 300" role="img" aria-label="真实速率随模拟时间变化">',
           '<rect width="960" height="300" fill="white"/>']
    for speed in (0, top / 2, top):
        y = 248 - speed / top * 204
        svg += [f'<path d="M 70 {y} H 922" stroke="#dce3ea"/>',
                f'<text x="58" y="{y + 5}" text-anchor="end">{speed:g}</text>']
    for second in (0, 1, 2, 4, 6, 8):
        x = 70 + second / DURATION_S * 852
        svg += [f'<path d="M {x} 44 V 248" stroke="#edf0f4"/>',
                f'<text x="{x}" y="273" text-anchor="middle">{second}</text>']
    svg += ['<text x="70" y="25">实际速率（m/s）</text>',
            '<text x="922" y="297" text-anchor="end">模拟时间（s）</text>']
    for action, points in series.items():
        xy = " ".join(f"{70 + t / DURATION_S * 852:.3f},{248 - v / top * 204:.3f}"
                      for t, v in points)
        svg.append(f'<polyline data-action="{action}" points="{xy}" fill="none" '
                   f'stroke="{COLORS[action]}" stroke-width="3"/>')
    return "\n".join(svg + ["</svg>"])


def run_comparison(seed=SEED, *, max_steps=MAX_STEPS, open_browser=True) -> dict:
    """跑两组真实回合；无界面验证请传 open_browser=False。"""
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    output_dir = OUTPUT_ROOT / stamp
    output_dir.mkdir(parents=True, exist_ok=False)  # 每次保留独立证据，不覆盖旧报告。
    runs = {}
    for action in COLORS:
        folder = output_dir / action
        summary = run_episode(seed=seed, max_steps=max_steps, action_name=action,
                              render_mode="rgb_array", output_dir=folder,
                              duration_s=DURATION_S, vehicles_count=0)
        trace_path = folder / "trace.jsonl"
        trace = [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines()]
        runs[action] = {"summary": summary, "trace": trace,
                        "trace_path": str(trace_path), "gif_path": str(folder / "episode.gif"),
                        "final_speed_mps": trace[-1]["speed_mps"],
                        "displacement_x_m": summary["final_observation"][0][1]
                        - summary["initial_observation"][0][1]}
    idle, slower = runs["IDLE"]["summary"], runs["SLOWER"]["summary"]
    matched = (idle["initial_observation"] == slower["initial_observation"]
               and idle["config"] == slower["config"]
               and idle["packages"] == slower["packages"]
               and idle["runner_sha256"] == slower["runner_sha256"])
    if not matched:
        raise RuntimeError("两组初始条件或运行版本不一致；保留日志，不生成公平对照结论。")

    cards = []
    for action, run in runs.items():
        summary = run["summary"]
        reason = html.escape(summary["end_reason"])
        description = "每步保持已有目标" if action == "IDLE" else "每步请求降低目标速度档位"
        cards.append(f'''<article><h2 style="color:{COLORS[action]}">{action}</h2>
<p>{description}</p><img src="{action}/episode.gif" alt="{action} 真实道路回放">
<dl><dt>模拟时长 / 动作次数</dt><dd>{summary['sim_time_s']:.2f} 秒 / {summary['steps']} 次</dd>
<dt>末次实际速率</dt><dd>{run['final_speed_mps']:.3f} m/s</dd>
<dt>自车世界 x 位移</dt><dd>{run['displacement_x_m']:.3f} 米</dd>
<dt>碰撞</dt><dd>{'是' if summary['crashed'] else '否'}</dd>
<dt>结束原因</dt><dd>{END_LABELS.get(summary['end_reason'], reason)}<br><code>{reason}</code></dd></dl>
<p><a href="{action}/trace.jsonl">逐步日志</a> · <a href="{action}/summary.json">配置与版本</a></p></article>''')
    report = output_dir / "report.html"
    document = f'''<!doctype html>
<html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>IDLE 与 SLOWER：同一起点的动作对照</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;background:#f2f5f8;color:#233044;font:16px/1.7 system-ui,"Microsoft YaHei",sans-serif}}
main{{max-width:1160px;margin:auto;padding:32px 24px}}h1{{font-size:28px;margin:0}}h2{{margin:0;font-size:22px}}
.tag{{color:#576a80}}.cards{{display:grid;grid-template-columns:1fr 1fr;gap:22px;margin:24px 0}}
article,.chart{{background:white;border:1px solid #dce3ea;border-radius:14px;padding:22px}}img{{width:100%;display:block}}
dl{{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:20px}}dt{{color:#576a80}}dd{{margin:0;text-align:right}}
code{{font-size:12px}}a{{color:#176fbd}}svg{{width:100%;display:block;font-size:14px;fill:#576a80}}
.note{{border-left:4px solid #cc6815;padding:12px 18px;background:#fff7ed}}.legend{{display:flex;gap:24px}}
@media(max-width:720px){{.cards{{grid-template-columns:1fr}}main{{padding:20px 12px}}h1{{font-size:23px}}}}
</style><main><p class="tag">实验 05 · 真实环境执行对照</p><h1>同一起点，保持目标与持续请求减速</h1>
<p>seed={seed} · 其他车辆=0 · 环境时限={DURATION_S:g} 秒 · 步数预算={max_steps}
<br>两组初始观察、配置、依赖版本与运行器内容已核对一致。</p>
<p class="note">这是恒定高层动作的控制响应对照，不是 40/50 米阈值策略评价。
没有其他交通；无碰撞不构成安全证明。SLOWER 的最低目标档位仍是 20 m/s，不是紧急制动。</p>
<section class="cards">{''.join(cards)}</section><section class="chart"><h2>实际速率随时间怎样变化</h2>
<p class="legend"><span style="color:{COLORS['IDLE']}">━━ IDLE</span>
<span style="color:{COLORS['SLOWER']}">━━ SLOWER</span></p>{speed_svg(runs)}
<p>起点来自 first_transition 的动作前时间与 speed_before_mps；后续点来自每条日志的
next_observation_time_s 与 speed_mps。它们是实际速率，未归一化，不是世界 x 轴速度分量或目标速度。</p>
<p>横轴固定为 0–8 秒；曲线只画真实采样区间，不补齐提前结束的部分。
GIF 各自循环播放，浏览器不保证两侧同步；比较同一时刻请看曲线与日志。</p></section>
<p>动手：先预测，再把脚本顶部 MAX_STEPS 从 40 改成 5，重新运行。
比较曲线覆盖的时间与结束原因，不能把观察更短理解成驾驶更安全。</p>
<p class="tag">世界 x 位移=末位置−初位置（米），不是累计路程。原始数值、配置和版本保存在各组日志中。
报告记录的是助手或学习者本次运行；谁运行、是否理解，需要另行记录。</p></main></html>'''
    report.write_text(document, encoding="utf-8")
    print(f"对照报告：{report}")
    if open_browser:
        webbrowser.open(report.as_uri())
    return {"report_path": str(report), "output_dir": str(output_dir), "seed": seed,
            "max_steps": max_steps, "initial_conditions_match": matched, "runs": runs}


if __name__ == "__main__":
    run_comparison()
