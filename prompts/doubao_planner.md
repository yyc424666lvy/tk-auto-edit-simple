# 豆包 Planner：正式两阶段流程

豆包只负责“看素材 + 规划”，不负责运行 Montaj / FFmpeg。

## 第 0 步：角色初始化

发送：

> 你现在负责 TikTok 商品视频的剪辑规划，不负责实际剪辑。\n> 我会依次给你：商品信息、带源文件名和时间戳的代表帧、固定 plan.json Schema。\n> 你必须先建立 Candidate Shot List，再生成最终 plan.json。禁止从代表帧直接跳到最终 JSON。\n> 现在只回复 READY。

## 第 1 步：商品信息

发送商品名和最多 3 个核心卖点，并要求先阅读，不生成 JSON。

## 第 2 步：代表帧

上传带标签的 contact sheet。每格必须能读出：

`源文件名 | HH:MM:SS`

例如：`4.mp4 | 00:00:32`。

如果标签无法可靠读取，停止，不进入规划。

## 第 3 步：Candidate Shot List

发送：

> 请先根据代表帧建立候选镜头清单，暂时不要生成 JSON。\n> 只输出：视频文件 | 时间范围 | 画面内容 | 推荐用途。\n> 推荐用途可用 HOOK / PRODUCT_HERO / PRODUCT_FEATURE / DEMO / INSTALL / RESULT。\n> 请列出 10–15 个最有价值片段。\n> 时间必须来自代表帧，不允许凭记忆猜测。

检查“文件名 / 时间 / 画面内容”是否明显对应。

## 第 4 步：锁定候选池

确认后发送：

> 候选镜头清单确认通过。最终 plan.json 只能从刚才这份候选镜头池选择，不得引用候选池之外的时间段。

## 第 5 步：生成最终 plan.json

规划要求：
- B = Result First：优先 Pain / Result / Strong Action -> Proof -> Install/Demo -> Result。
- C = Product Logic：优先 Product Hero -> Feature/Durability -> Install/Demo -> Result。
- 每个版本 5–8 个片段。
- 总时长 10–15 秒。
- 单片段 0.8–3.0 秒，通常 0.8–2.5 秒。
- 不要机械地每段都剪成 2 秒。
- 每版本最多 4 条英文文案。
- 每条英文 <=6 个单词。
- 文案必须与对应画面一致。
- 禁止纯文字标题页、空镜、无产品信息过渡。
- 不得虚构素材不存在的能力。
- Source Gate 只能是：`CLEAN_SOURCE` / `CROPPABLE_TEXT` / `MASKABLE_TEXT` / `SOURCE_TEXT_LIMITATION`。

最后要求：

> 只输出合法 JSON。不要解释。不要 Markdown。不要代码围栏。不要新增 Schema 字段。

把 `templates/plan.json` 一并提供给豆包。

## 第 6 步：局部修正

如果只是文案或字段小问题，不要整份重规划。发送明确修改指令，例如：

> 时间线全部保持不变，只把 `NO MORE LEAKS` 改为 `NO VISIBLE LEAKS`，把 `LEAK-PROOF` 改为 `SECURE FIT`。其他内容全部保持不变。输出修改后的完整合法 JSON。

## 停止条件

以下任一情况发生时停止：
- 代表帧无法对应源文件和时间戳；
- 豆包不能可靠看图；
- Candidate Shot List 出现大量猜测时间码；
- 文案需要依赖素材没有证明的能力。
