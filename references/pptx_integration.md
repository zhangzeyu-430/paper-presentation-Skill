# paper-presentation HTML-first 交付规范

本文件规定如何生成“可上台展示”的最终汇报产物。默认交付为 HTML deck；PPTX 仅在用户明确要求时作为可选导出。

## 一、总原则

- HTML deck 是默认成品，必须能在浏览器全屏直接汇报。
- 页面正文是“给听众看”的讲解层，不是逐字稿摘抄，也不是极简 bullet 提纲。
- 默认第 1 页必须是完整论文标题封面；不得从动机页、方法页或实验页直接开始。
- HTML deck 的视觉目标是“PPT 风格幻灯片”，不是网页 dashboard、论文讲义或 PDF 预览器。若看起来不像日常组会 PPT，即使 DOM QA 通过也视为失败。
- 最后一页必须是结束页：谢谢 / Q&A / 重要参考资料。必须包含论文/代码链接或出处、2-4 条关键参考资料、可继续讨论的问题。
- 逐字稿只放在 notes 数据区和独立 `*_逐页逐字稿.md`。
- 每页必须有视觉结构：图、表、流程图、公式块、对比卡片或高亮截图。
- 禁止连续多页使用完全相同布局。
- 页标题不得出现“第 X 页：”前缀。
- 借鉴 reveal.js 的导航/notes/progress 思路，以及 Marp 的 Markdown-first 内容生产思路；默认不依赖外部 CDN 或 npm 包。
- 视觉必须达到“正式组会汇报”标准，禁止黑白文档式、Markdown 讲义式、空泛卡片堆叠式页面。

## 二、推荐流程

1. 完成论文素材盘点表（图、表、公式、关键数字、不可用素材）。
2. 运行 `scripts/inspect_pdf_assets.py` 探查 Figure/Table/caption 候选区域。
3. 使用 `scripts/crop_pdf_region.py` 裁剪核心 Figure/Table/公式局部图，禁止整页截图缩略图。
4. 落地 `*_asset_manifest.json`，记录所有素材、裁剪图、关键数字、来源和对应 claim。
5. 参考 [layout_patterns.md](layout_patterns.md) 选择每页页面类型和版式，落地 `*_deck_plan.json`。
6. 生成 `*_HTML展示稿.md`（每页包含观众可见正文、关键要点、证据解读、图表标注、takeaway）。
7. 生成 `*_逐页逐字稿.md`（完整口播）。
8. 基于 `assets/ppt_html_template.html` 生成 `*_组会汇报.html`（单文件 HTML/CSS/JS）。
9. 执行 `scripts/validate_html_deck.py` 自动 QA + 浏览器视觉检查。
10. 发现问题后回到素材盘点、裁图、展示稿或 HTML 排版步骤迭代。

## 三、展示稿到 HTML 的内容边界（强制）

- `*_HTML展示稿.md` 中的正文导入、关键要点、证据解读、图表说明、takeaway 都必须进入观众可见正文。
- `视觉元素、布局建议、来源依据` 必须保留为非 bullet 元数据，供 HTML 生成使用。
- 展示要点要像“可投屏结论”，不能像目录词。
- 两栏图文页最多 5 条 bullet；总结页最多 6 条 bullet。
- 可见页面必须有足够解释；notes 用于口播扩展，不能替代页面正文。
- 普通内容页建议 160-280 个中文字符，重点方法/实验页建议 220-420 字；超过则拆页或放入 notes/逐字稿，不得删成空洞短句，也不得把 HTML 做成论文讲义网页。
- 每页视觉元素必须能回溯到素材盘点表；不得临时添加无来源装饰图。
- 每页视觉元素必须能回溯到 `asset_manifest.json`；`deck_plan.json` 中的 `evidence_ids` 必须与最终 HTML 的图表/数字/公式来源一致。

### 观众页禁用元话语

HTML 可见正文必须是论文内容本身，不是生成器说明或讲者提示。以下文字只能出现在 notes、逐字稿、QA 或 `HTML展示稿.md` 的元数据中，不能出现在 HTML 可见区域：

- “封面把……放在同一屏”
- “表格只保留……”
- “示意图把……分开画”
- “读图时……”
- “听众应该/观众应该……”
- “这个结果支持……”
- “这一页/本页/页面用于……”
- “避免……”

可见正文要改写为具体论文事实：
- 不写“表格只保留 Table 8 的关键结论”，而写“Table 8：4-head 在 21/35 个 MSE、20/35 个 MAE 场景最优；16-head 未带来稳定提升”。
- 不写“示意图把短期预测和长期预测分开画”，而写“H=96 更依赖近期局部波动；H=720 更依赖周期/趋势信息，gating 学习时域与频域权重”。
- 不写“封面把题目、任务、关键词和结果放在同一屏”，而直接展示论文题目、作者、机构、任务、方法关键词和核心结果。

## 四、HTML 页面要求

- 单文件 HTML，内嵌 CSS/JS；除本地论文截图外不依赖网络资源。
- 每页使用 16:9 `.slide` 容器，适配 1366x768、1920x1080 和常见投影。
- 必须使用固定 16:9 PPT 画布，而不是全窗口网页布局。推荐外层 `.deck` 居中，内层 `.slide-canvas` 固定比例缩放；所有页眉、页脚、标题、图表和正文都在画布内。
- 翻页控件不得遮挡画布内容；应放在画布外、自动隐藏或预留底部控制区。若按钮覆盖页码、takeaway、来源或正文，视为失败。
- 不得使用悬浮在底部中间的醒目 takeaway 条覆盖画布。takeaway 可以进入 `.claim`、侧边结论卡、图上标签、notes 或逐字稿；页脚可保留来源和页码，但不放会遮挡主图的结论条。
- 支持键盘翻页：右箭头/空格下一页，左箭头上一页，Home/End 跳转首尾。
- 支持屏幕按钮翻页：必须有可见的上一页/下一页按钮，避免浏览器焦点问题导致“不能翻页”。
- 支持页码、进度条和当前页状态，不把页码写进标题。
- 支持 URL hash（如 `#slide-3`）或等价状态，刷新后应尽量回到当前页。
- notes 可通过按键或隐藏面板查看，默认不遮挡观众页面。
- 正文、表格、图注必须设置最大宽度、最大高度和合理行高，防止溢出。
- 方法流程图优先用 HTML/CSS/SVG 重绘；实验表格优先重绘关键数字。
- 原论文图难以抽取时，使用论文页截图加高亮框，或基于论文内容重绘，并标注来源。
- 禁止直接使用整页论文截图作为核心图。必须裁剪到 Figure/Table/公式区域，或局部截图 + 高亮框。整页截图只能用于“论文首页/参考资料/备份页”。
- 方法页必须贴合论文原图、公式或方法文字。若论文有核心架构图，优先使用原图截图/局部截图+高亮/忠实重绘；不得用“历史序列 -> 模块 A -> 模块 B”这类泛化示意代替。
- 忠实重绘必须保留论文中的模块名、变量名、箭头方向、输入输出、关键操作和公式符号；不能只保留概念名。
- 每页必须显式呈现本页核心判断，可用 `.claim`、`.takeaway`、结论条或大号数字卡实现。
- 每页必须有证据区，可用 `.evidence`、`.table-wrap`、`.flow`、`.figure`、`.matrix`、`.chart` 实现。
- 每页必须有解释区，可用 `.context`、`.explain`、`.evidence-reading`、`.caption` 实现。
- 禁止出现大面积空面板；高度超过页面 30% 的容器必须包含真实正文、图表、表格或公式。
- 禁止把所有页面都实现成同一个“左正文 + 右证据”的通用两栏 grid。即使自动 QA 通过，只要视觉上像同一模板批量换字，也视为失败。
- 对框架图、可解释性图、核心表格，优先使用主视觉布局：图表占 55%-75% 页面面积，旁边只放大字号结论卡和短图注。

## 五、强制 HTML 骨架

最终 HTML 必须使用以下结构思想。可以调整视觉风格，但不能删除核心语义节点和交互能力。注意：实际输出应升级为 PPT 画布式结构，不要照抄成网页两栏面板。

默认优先复制并改写 `assets/ppt_html_template.html`。该模板已经包含：
- 固定 16:9 PPT 画布。
- 学术 PPT 封面骨架。
- 内容页页眉编号、角标、页脚来源和 takeaway。
- 画布外翻页/讲稿控件。
- progress bar 和 notes 面板。

若不使用模板，必须实现同等结构。

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>论文简称 - 组会汇报</title>
  <style>
    :root {
      --bg: #edf4f2;
      --bg-2: #f7faf8;
      --ink: #13221f;
      --muted: #66746f;
      --panel: #ffffff;
      --line: #cddbd6;
      --accent: #0f766e;
      --accent-2: #b45309;
      --accent-3: #2f4f6f;
      --soft: #dff3ee;
      --warm: #fff1d6;
      --danger-soft: #ffe4df;
    }
    * { box-sizing: border-box; }
    body { margin: 0; background: var(--bg); color: var(--ink); font-family: "Microsoft YaHei", "Noto Sans CJK SC", sans-serif; }
    .deck { width: 100vw; height: 100vh; overflow: hidden; display: grid; place-items: center; }
    .slide {
      width: min(100vw, 177.78vh);
      height: min(100vh, 56.25vw);
      aspect-ratio: 16 / 9;
      padding: 4.2vh 5vw;
      display: none;
      grid-template-rows: auto 1fr auto;
      gap: 2.2vh;
      background:
        linear-gradient(120deg, rgba(15,118,110,.10), transparent 38%),
        radial-gradient(circle at 85% 12%, rgba(180,83,9,.10), transparent 26%),
        linear-gradient(180deg, var(--bg-2), var(--bg));
    }
    .slide.active { display: grid; }
    .slide h1 { margin: 0; font-size: clamp(28px, 3vw, 44px); line-height: 1.12; max-width: 88vw; }
    .content { min-height: 0; display: grid; gap: 2vw; }
    .layout-two { grid-template-columns: minmax(0, 1fr) minmax(0, 1.08fr); align-items: stretch; }
    .layout-one { grid-template-columns: minmax(0, 1fr); }
    .panel { min-width: 0; min-height: 0; background: rgba(255,255,255,.94); border: 1px solid var(--line); border-radius: 8px; padding: 2.4vh 2vw; overflow: hidden; box-shadow: 0 16px 40px rgba(19,34,31,.08); }
    .bullets { margin: 0; padding-left: 1.25em; font-size: clamp(18px, 1.45vw, 26px); line-height: 1.5; }
    .bullets li { margin: 0 0 0.7em; }
    .claim {
      border-left: 6px solid var(--accent);
      background: var(--soft);
      border-radius: 8px;
      padding: 1.4vh 1.3vw;
      font-size: clamp(20px, 1.55vw, 28px);
      font-weight: 800;
      line-height: 1.32;
      margin-bottom: 1.4vh;
    }
    .takeaway {
      background: var(--warm);
      border: 1px solid rgba(180,83,9,.25);
      border-radius: 8px;
      padding: 1.2vh 1vw;
      font-size: clamp(16px, 1.12vw, 20px);
      color: #663c00;
      line-height: 1.35;
    }
    .kpi-row { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1vw; }
    .kpi { border-radius: 8px; background: #fff; border: 1px solid var(--line); padding: 1.8vh 1.1vw; }
    .kpi strong { display: block; font-size: clamp(34px, 4vw, 72px); line-height: 1; color: var(--accent); }
    .kpi span { display: block; margin-top: .8vh; color: var(--muted); font-size: clamp(13px, .95vw, 17px); }
    .evidence-title { color: var(--accent-3); font-weight: 800; font-size: clamp(17px, 1.2vw, 22px); margin: 0 0 1vh; }
    .figure, .table-wrap, .flow, .cards { min-height: 0; height: 100%; }
    .source { color: var(--muted); font-size: clamp(12px, 0.9vw, 16px); }
    .pager { color: var(--muted); font-size: 14px; text-align: right; }
    .controls {
      position: fixed;
      right: 22px;
      bottom: 18px;
      z-index: 20;
      display: flex;
      gap: 8px;
      align-items: center;
    }
    .controls button {
      border: 1px solid var(--line);
      background: rgba(255,255,255,.94);
      color: var(--ink);
      border-radius: 8px;
      padding: 9px 12px;
      font-size: 16px;
      cursor: pointer;
    }
    .progress {
      position: fixed;
      left: 0;
      bottom: 0;
      height: 4px;
      width: 100vw;
      background: rgba(100,116,139,.22);
      z-index: 30;
    }
    .progress > span {
      display: block;
      height: 100%;
      width: 0;
      background: var(--accent);
      transition: width .18s ease;
    }
    aside.notes { display: none; }
    body.show-notes aside.notes {
      display: block;
      position: fixed;
      right: 2vw;
      bottom: 6vh;
      width: min(560px, 42vw);
      max-height: 52vh;
      overflow: auto;
      background: rgba(255,255,255,.96);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
      box-shadow: 0 18px 50px rgba(15, 23, 42, .18);
      z-index: 10;
    }
  </style>
</head>
<body>
  <main class="deck" aria-label="论文组会汇报">
    <section class="slide active" data-title="页面标题">
      <header><h1>页面标题</h1></header>
      <div class="content layout-two">
        <section class="panel"><ul class="bullets"></ul></section>
        <section class="panel figure"></section>
      </div>
      <footer><div class="source">来源：论文 Figure/Table/Section</div><div class="pager"></div></footer>
      <aside class="notes">逐字稿、追问、简答、转场句</aside>
    </section>
  </main>
  <nav class="controls" aria-label="翻页控制">
    <button id="prevBtn" type="button">上一页</button>
    <button id="noteBtn" type="button">讲稿</button>
    <button id="nextBtn" type="button">下一页</button>
  </nav>
  <div class="progress" aria-hidden="true"><span id="progressBar"></span></div>
  <script>
    const slides = [...document.querySelectorAll('.slide')];
    let current = Math.max(0, Math.min(slides.length - 1, Number(location.hash.replace('#slide-', '')) - 1 || 0));
    function show(i) {
      current = Math.max(0, Math.min(slides.length - 1, i));
      slides.forEach((s, idx) => s.classList.toggle('active', idx === current));
      document.querySelectorAll('.pager').forEach((p, idx) => p.textContent = `${idx + 1} / ${slides.length}`);
      document.getElementById('progressBar').style.width = `${((current + 1) / slides.length) * 100}%`;
      history.replaceState(null, '', `#slide-${current + 1}`);
    }
    document.getElementById('prevBtn').addEventListener('click', () => show(current - 1));
    document.getElementById('nextBtn').addEventListener('click', () => show(current + 1));
    document.getElementById('noteBtn').addEventListener('click', () => document.body.classList.toggle('show-notes'));
    document.addEventListener('keydown', (e) => {
      if (['ArrowRight', ' ', 'PageDown'].includes(e.key)) show(current + 1);
      if (['ArrowLeft', 'PageUp'].includes(e.key)) show(current - 1);
      if (e.key === 'Home') show(0);
      if (e.key === 'End') show(slides.length - 1);
      if (e.key.toLowerCase() === 'n') document.body.classList.toggle('show-notes');
    });
    show(0);
  </script>
</body>
</html>
```

强制要求：
- 每个页面必须是一个 `<section class="slide">`。
- 每个页面必须有 `<h1>`、`.content`、`.source`、`.pager`、`aside.notes`。
- HTML 必须有 `.controls`、`#prevBtn`、`#nextBtn`、`#noteBtn` 和 `#progressBar`。
- 每页必须至少包含一个 `.claim`、`.takeaway` 或等价的核心判断区。
- 除封面和总结外，每页必须包含 `.context`、`.explain` 或 `.evidence-reading` 中至少两个解释性节点。
- 出现图表/表格/流程图时，必须包含 `.caption` 或等价图表说明节点。
- `.caption` 的可见文本必须是论文事实或图表标注，不能是“这张图如何设计/应该怎么看”的说明。读图顺序写入 notes。
- 关键实验页必须使用 `.kpi-row`、`.table-wrap`、`.chart` 或等价组件突出真实数字。
- 如果使用图片，必须设置 `max-width: 100%; max-height: 100%; object-fit: contain;`。
- 如果使用表格，必须只放关键行列，避免完整论文大表。
- 如果使用 SVG 流程图，文字必须是真实文本，不要把文字烘焙进不可编辑图片。

## 六、图表与素材策略（强制）

优先级：
1. 论文原图/原表裁剪图（可读性足够时）。
2. 基于论文表格重绘图表（保持真实数字）。
3. 基于论文公式或流程重绘方法图。
4. 论文局部截图 + 高亮框。

规则：
- 所有图表必须有来源标注（图号/表号/章节）。
- 必须裁剪图表，禁止把整页论文截图缩小塞入页面。
- 不允许用“示意假数据”替代真实实验数据。
- 不允许使用与论文内容无关的通用图标、装饰折线、随机插画填充页面。
- 如果某页没有合适原图，必须用流程图、公式块、对比卡片或重绘表格支撑内容。
- 对方法核心页，泛化示意图默认不合格。必须至少满足以下之一：原图截图、局部截图+高亮、忠实重绘原图结构、公式/变量关系图、论文原文短摘录+模块解释。

## 七、论文阅读 Deck 内容增强

为了避免 HTML 只是“换皮提纲”，论文阅读汇报必须尽量包含以下信息结构：

- 封面页：完整论文题目、作者/机构、会议/年份、任务领域、汇报主题、一句话贡献。
- 论文定位页：任务定义、核心问题、作者 claim、主要结果。
- 读者路线页或动机页：这篇论文为什么值得读，解决哪两个关键矛盾。
- 方法总览页：一个完整的数据流，不拆成孤立模块名。
- 模块深挖页：输入、操作、输出、解决的问题、没有它会怎样。
- 实验设计页：数据、baseline、指标、公平性设置，不只报结果。
- 主结果页：3-5 个关键数字，必须说明证明了哪个 claim。
- 消融页：模块删除、数字变化、贡献解释。
- 可解释性/案例页：如果论文有图，必须讲“图说明了什么”。
- 批判页：证据不足、适用边界、复现风险、替代解释。
- 迁移页：对用户课题可借鉴和不可直接搬的部分。
- 结束页：谢谢 / Q&A / 重要参考资料；展示论文链接、代码链接、核心引用或后续讨论问题。

若页数有限，优先保留：定位、动机、方法总览、核心模块、主实验、消融、批判/迁移。

## 七点五、讲解型 HTML 页面最低正文结构

每个非封面页面必须至少包含以下可见正文块：

- `Context`：60-120 字，交代本页为什么出现，连接上一页逻辑。
- `Claim`：一句话核心判断，必须具体到方法、实验或局限。
- `Key Points`：3-5 条要点，服务于 claim，不能替代解释段落。
- `Evidence Reading`：80-160 字，解释图、表、公式或数字如何支持 claim。
- `Figure/Table Caption`：40-100 字，告诉听众应该看图表的哪个部分。
- `Takeaway`：一句话收束本页，为下一页转场。

失败例：
- 只有标题 + 3 条 bullet + 三个空卡片。
- 有图表但没有解释图表说明什么。
- 页面大半是留白，真实内容只在左上角。
- 把详细解释全部藏进 notes，观众页面本身读不懂。

## 八、真实图表与表格约束

HTML 中的图表必须符合论文真实内容：

- 论文原图：必须标明 Figure 编号和含义；如果是截图，不能裁掉坐标、图例、模块名或关键标注。
- 表格重绘：只能使用论文表格中的真实数字；必须标明 Table 编号；不得为了好看编造平均值。
- 流程图重绘：必须来自论文方法描述、公式或原图，模块名称和数据流要与论文一致。
- 对比卡片：必须对应论文中的方法对比、消融或作者论述，不得写泛泛优缺点。
- 关键数字：必须在页面上解释“这个数字证明什么”，不能只展示数字。
- 如果图表信息不确定，必须在来源或 notes 中标注“不确定”，不能装作已确认。

## 九、HTML QA（必做）

文本检查：
- 不应出现“本页要放什么/建议放什么/页面内容建议”等占位语。
- 不应出现“第 X 页：”标题前缀。
- 第 1 页必须是完整论文标题封面。
- 最后一页必须是谢谢 / Q&A / 重要参考资料结束页。
- HTML 可见正文不得出现元话语：`封面把`、`表格只保留`、`示意图把`、`读图时`、`听众应该`、`观众应该`、`这个结果支持`、`这一页`、`本页`、`页面用于`。
- 关键数字与结论必须存在。
- 每页必须有来源依据。
- 除封面/总结外，每页必须有正文导入、证据解读和图表说明。

视觉检查：
- 浏览器打开 HTML，逐页检查 100% 页面。
- 与“日常组会 PPT”对照检查：封面是否像 PPT 首页，内容页是否有页眉/章节/主体图表/结论区，是否避免网页 dashboard 感。
- 没有文字溢出、遮挡、重叠或被裁切。
- 没有正文触碰页面边缘。
- 图表、流程图、公式块或卡片可读。
- 颜色对比足够，避免低对比难读。
- 页面不能是黑白文档风；必须有主题色、证据区、结论强调和视觉层级。
- 页面风格统一，但布局不能连续多页完全相同。
- 至少 70% 页面含图表、流程图、公式块、对比卡片或重绘表格。
- 不得出现大面积空白卡片；视觉容器必须被真实内容填充。
- 不得出现整页论文截图缩略图；Figure/Table 必须裁剪、放大、高亮或重绘。
- 不得出现左右两栏大白框贯穿全篇；同一类双栏信息面板连续超过 2 页视为失败。
- 不得出现伪多样性：`layout_pattern` 名称不同，但 HTML DOM 都是 `.grid + .text-panel + .visual-panel` 的同一骨架。
- 点击上一页/下一页按钮必须能翻页；按键翻页不能作为唯一翻页方式。
- 翻页按钮不得覆盖幻灯片内容；覆盖页脚、来源、takeaway、页码或正文均视为失败。
- 任何结论条、提示条或 takeaway 条覆盖主图、来源、页码或正文，均视为失败。
- 点击讲稿按钮必须能显示/隐藏 notes。
- 进度条必须随翻页变化。
- 每页核心判断必须清楚；随机抽 3 页，听众应能在 5 秒内看出本页想证明什么。
- 随机抽 3 个图表或数字，必须能回溯到素材盘点表和论文来源。
- 随机抽 3 个方法页视觉元素，必须核对其模块名、变量名、箭头方向或公式符号是否来自论文原图/公式/方法文字；若只是泛化流程图，视为失败。

自动检查：
- 必须运行 `scripts/validate_html_deck.py outputs/{论文简称}_组会汇报.html --md outputs/{论文简称}_HTML展示稿.md --manifest outputs/{论文简称}_asset_manifest.json --plan outputs/{论文简称}_deck_plan.json`。
- 读取 HTML，确认 `.slide` 数量与展示稿页数一致。
- 确认每页存在 `h1`、`.source`、`.pager`、`aside.notes`。
- 确认存在 `.controls`、`#prevBtn`、`#nextBtn`、`#noteBtn`、`#progressBar`。
- 确认第 1 页包含论文完整标题或足够长的标题文本，而不是“动机/方法/实验”等章节页。
- 确认最后 1 页包含 `谢谢`、`Q&A`、`参考`、`References`、论文链接或代码链接中的至少两类信息。
- 统计 `.context`、`.explain`、`.evidence-reading`、`.caption`、`.takeaway` 等讲解节点；若大多数页面缺失，视为失败。
- 搜索占位词：`本页要放`、`建议放`、`TODO`、`placeholder`、`lorem`。
- 搜索元话语：`封面把`、`表格只保留`、`示意图把`、`读图时`、`听众应该`、`观众应该`、`这个结果支持`、`这一页`、`本页`、`页面用于`。若出现在可见正文，视为失败。
- 检查图片文件名和尺寸：若图片来自整页 PDF 渲染且未裁剪，或宽高比接近论文页面比例（如 A4 竖版）并作为核心图展示，标记为失败或人工复查。
- 统计含 `.figure`、`.table-wrap`、`.flow`、`.cards` 的页面比例，不低于 70%。
- 检查是否存在 `.claim`、`.takeaway`、`.kpi`、`.table-wrap`、`.flow` 等语义组件；若全篇只有 `.panel` 和 `.bullets`，视为失败。
- 若环境允许，用浏览器截图逐页检查；若不能截图，必须至少执行 DOM 和文本检查。

## 十、失败回滚规则

若本轮 HTML 出现以下任一情况，视为失败，必须重生：
- 整体观感像网页 dashboard、信息面板或论文讲义，不像组会 PPT。
- 首页不是 PPT 封面模板：缺少 logo/机构标识、居中大标题、中文副标题/汇报主题、汇报人/日期、底部信息条中的大部分要素。
- 页面正文主要由逐字稿口语句组成。
- 页面大段文本难以展示，或相反地只剩几个短 bullet 导致讲不清论文。
- 出现占位提示语或“该页放什么”语句。
- 第 1 页不是论文标题封面。
- 最后一页不是谢谢 / Q&A / 重要参考资料结束页。
- 至少一页完全空白。
- 任一主要内容页出现大面积空卡片或空白视觉面板。
- 任一核心图使用整页论文截图缩略图，未裁剪到 Figure/Table/局部结构。
- 关键页图表与文字重叠或越界。
- 任一页文字溢出、触边或被裁切。
- 视觉元素与论文无关，或无法回溯到素材盘点表。
- 无法通过可见按钮翻页。
- notes 无法打开或遮挡主体内容。
- 页面呈现为黑白文档、普通 Markdown、或只有 bullet 的卡片堆叠。
- 页面呈现为两个大面板左右平铺、右侧标题固定为 Evidence / Visual、下方证据解读横条的通用模板。
- 页面只有形式没有解释：缺正文导入、证据解读、图表说明或 takeaway。
- 页面把生成器说明、讲者提示或读图策略渲染到观众可见区域。
- 方法页视觉只是泛化示意图，无法对应论文原图、公式、变量或方法段落。
- 图表/表格没有真实论文依据，或数字无法回溯。
- 页面有图但没有解释“图说明什么”。
- 页面底部中间出现醒目橙色/黄色 takeaway 条并遮挡内容。

修复路径：
- 文字溢出：回到 `*_HTML展示稿.md` 压缩 bullet，或拆页。
- 页面太空：回到素材盘点表补真实数字、公式、流程或对比卡片。
- 图无关：重选论文图、表格重绘或流程图重绘。
- 整页论文截图：回到 PDF 裁剪步骤，裁出 Figure/Table bounding box；如果图过复杂，拆成局部放大页。
- 网页面板感：重做为 PPT 版式，增加页眉章节编号/角标 logo/底部色条，减少大白框，改用主图 + 结论标注。
- 呆板两栏感：取消通用左右两栏容器，按页面类型重做为主图页、数字看板页、流程页、消融矩阵页、批判卡片页等不同骨架。
- 首页不像 PPT：套用封面模板，居中标题、中文副标题、logo、汇报人、日期、底部信息条。
- 内容太浅：回到 claim 与证据链，补“为什么有效”和“证明了什么”。
- 实验页像报表：只保留支撑 claim 的 3-5 个关键数字。
- 页面太丑或太像讲义：回到视觉设计系统，重做主题色、布局、claim 区、证据区和关键数字表达。
- 内容太空：新增 Evidence 与 Explanation，不允许只加装饰。

## 十一、可选 PPTX

只有用户明确需要 `.pptx` 时，才在 HTML deck 通过 QA 后生成 PPTX。

PPTX 生成可以采用两种方式：
- 从 HTML 页面截图导入 PPTX，每页一张高分辨率图片，保证视觉一致。
- 使用 `python-pptx` 重排，但必须重新执行 PPTX 视觉 QA。

若 PPTX 与 HTML 质量冲突，以 HTML deck 为主交付；PPTX 标注为可编辑性较弱或降级产物。
