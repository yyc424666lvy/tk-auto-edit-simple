# TK 自动剪辑简单化 (`tk-auto-edit-simple`)

把 **1–2 条商品 MP4 + 商品名 + 最多 3 个核心卖点**，规划并输出两条 TikTok Shop 基础商品短视频：

- `B_result_first.mp4`：结果 / 痛点优先
- `C_product_logic.mp4`：商品逻辑优先

默认规格：**10–15 秒、1080×1920、30fps、H.264、静音、无 BGM**。

> 这是“简单化基础版”。重点是稳定、快、可复用；前 3 秒情绪价值、复杂节奏设计、BGM 策略、AI 去字/去水印等属于后续进阶项目。

## 架构

```text
可替换 Planner（Codex / 豆包 / 人工）
  -> Montaj（精确切片 / 拼接）
  -> portable FFmpeg 8.1.2（9:16 / 文案 / H.264 静音渲染）
```

- **Codex 模式**：推荐。若有本地文件和 shell 权限，可完成分析、规划、执行。
- **豆包模式**：已验证可替代“素材理解 + plan.json 规划”层；当前为半自动，详见 `docs/DOUBAO_QUICKSTART.md`。
- **Montaj**：固定使用 `theSamPadilla/montaj` commit `4dfe02ab789868ee599574d945d14519ba1b1fc8`。
- **FFmpeg**：固定验证版本为 8.1.2。

## 目录

```text
tk-auto-edit-simple/
├─ SKILL.md
├─ README.md
├─ VERSION
├─ LICENSE
├─ ROADMAP.md
├─ AGENT_COMPATIBILITY.md
├─ BASELINE_LOCK.json
├─ THIRD_PARTY_NOTICES.md
├─ workflow/
│  ├─ run_workflow.py
│  └─ README.md
├─ templates/
│  ├─ README.md
│  ├─ product_brief.json
│  └─ plan.json
├─ prompts/
│  ├─ codex_planner.md
│  └─ doubao_planner.md
├─ docs/
│  ├─ CODEX_QUICKSTART.md
│  └─ DOUBAO_QUICKSTART.md
└─ tools/
   └─ make_labeled_contact_sheet.py
```

## 最少输入

1. `1.mp4`
2. 商品名称
3. 1–3 个核心卖点
4. 可选 `2.mp4`

把文字信息填入 `templates/product_brief.json`。

## Codex：最短使用方式

把仓库交给 Codex，并提供 1–2 条 MP4 与 `product_brief.json`。让 Codex读取 `SKILL.md` 和 `prompts/codex_planner.md` 后执行。

完整步骤见 `docs/CODEX_QUICKSTART.md`。

## 豆包：当前使用方式

豆包不需要本地 shell。推荐固定流程：

```text
原视频
 -> 带“源文件名 + 时间戳”的代表帧
 -> Candidate Shot List
 -> 锁定候选镜头池
 -> final plan.json
 -> 本地校验 / 执行
 -> B + C 两条成片
```

**不要让豆包从联系表直接跳到最终 plan.json。** 实测两阶段规划能明显减少时间码漂移。

完整逐步话术见 `docs/DOUBAO_QUICKSTART.md` 与 `prompts/doubao_planner.md`。

## 执行命令

分析：

```bash
python workflow/run_workflow.py analyze \
  --input /path/to/1.mp4 \
  --input /path/to/2.mp4 \
  --ffmpeg /path/to/ffmpeg \
  --ffprobe /path/to/ffprobe \
  --out-dir ./output
```

渲染：

```bash
python workflow/run_workflow.py render \
  --input /path/to/1.mp4 \
  --input /path/to/2.mp4 \
  --plan ./plan.json \
  --montaj-root /path/to/montaj \
  --ffmpeg /path/to/ffmpeg \
  --ffprobe /path/to/ffprobe \
  --out-dir ./output
```

## 代表帧辅助工具

核心 `run_workflow.py` 保持冻结不改。为了让豆包更容易读取时间码，本仓库额外提供：

```bash
python tools/make_labeled_contact_sheet.py \
  --input /path/to/1.mp4 \
  --ffmpeg /path/to/ffmpeg \
  --ffprobe /path/to/ffprobe \
  --out ./1_contact_sheet.jpg
```

它在每个 1 秒代表帧上标注 `源文件名 | HH:MM:SS`，属于包装层辅助工具，不改变冻结剪辑核心。

## Source Gate

只允许：

- `CLEAN_SOURCE`
- `CROPPABLE_TEXT`
- `MASKABLE_TEXT`
- `SOURCE_TEXT_LIMITATION`

`SOURCE_TEXT_LIMITATION` 是风险说明，不代表自动执行复杂 OCR / inpainting / 去水印。素材权利、第三方水印和平台合规问题应由使用者自行确认。

## REPRODUCE / VARIATION

- `VARIATION`：默认。优先更换 Hook，再在质量允许时替换 1–3 个中间镜头；目标 overlap `<= 0.70`。
- `REPRODUCE`：严格复现已有 plan；缺少历史 plan 时返回 `REPRODUCE_PLAN_MISSING`，不得偷偷重规划。

## 已冻结验证基线

`BASELINE_LOCK.json` 记录已验证的 Montaj commit、FFmpeg 8.1.2 与核心脚本哈希。其 `readme_sha256` 对应 `workflow/README.md`（原冻结工作流说明），不是本仓库根目录 README。

## 当前限制

- 不捆绑 Montaj 源码。
- 不捆绑 FFmpeg 二进制。
- 豆包目前是 Planner-only 半自动模式；“只丢视频，自动拿 B/C 两条成片”的本地包装器列入 Roadmap。
- 不保证不同 Planner 在 `VARIATION` 模式下生成完全相同镜头；若要复现，请使用相同 `plan.json` + `REPRODUCE`。

## License

本仓库代码采用 MIT License。第三方项目与 FFmpeg 的许可证说明见 `THIRD_PARTY_NOTICES.md`。
