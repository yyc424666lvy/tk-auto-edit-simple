# 豆包 Quick Start

豆包当前是 Planner，不是本地渲染器。

## 你需要准备

- 1–2 条原始 MP4
- 商品名
- 最多 3 个核心卖点
- 带“源文件名 + 时间戳”的代表帧联系表

可使用：

```bash
python tools/make_labeled_contact_sheet.py --input 1.mp4 --ffmpeg /path/to/ffmpeg --ffprobe /path/to/ffprobe --out 1_contact_sheet.jpg
```

## 标准流程

1. 发角色初始化话术，让豆包只回复 READY。
2. 发商品名和卖点。
3. 发带标签联系表。
4. 先让豆包输出 Candidate Shot List。
5. 快速检查时间码和画面内容是否对应。
6. 锁定候选池。
7. 发 `templates/plan.json`，让豆包只从候选池生成最终 JSON。
8. 小问题只做局部修正。
9. 保存为 `plan.json`。
10. 交回本地 / Codex 运行 Montaj + FFmpeg。

完整逐条话术见 `prompts/doubao_planner.md`。

## 为什么多一步 Candidate Shot List

实测中，直接从 contact sheet 跳到 final plan 可能出现“理解画面正确，但时间码漂移”。先列候选镜头再锁定时间段，可以显著降低这个问题。
