# Leveled Reading For Japanese

面向日语文学作品的 **SAGAP** 原型实现：

> **Story-Aware Graded Adaptation Pipeline**  
> 面向学习者等级的、叙事结构感知文学分级改编流水线。

这个项目的目标不是简单调用 LLM 说“请改成 N3”，而是把日语长篇文学改编拆成可控制、可验证、可复现的多个步骤：分段、故事信息维护、场景改编计划、分级改写、注释、validation、局部修正和实验数据输出。

当前版本是 MVP，默认支持 `mock` 模式，不需要 API key 也能跑通完整流程；需要真实模型时可切换到 `openai` provider。

## 核心思想

本项目基于以下原则实现：

1. **目标等级是理解负荷上限，不是强行制造难度。**  
   如果原文已经很简单，N1 版本不应被改得更难。

2. **语法控制相对严格，词汇控制相对宽松。**  
   复杂句法优先拆分；文学关键词、文化词、专名可以保留，并用注释兜底。

3. **文学改编不能变成摘要。**  
   每个 scene 都先生成 `ScenePlan`，明确必须保留的事件、人物、氛围和关键词。

4. **Validation 模拟目标读者阅读负担。**  
   系统不只检查生成是否成功，还要输出等级、忠实性、连贯性等指标，方便后续论文实验。

## 目录结构

```text
.
├── .env.example
├── config/
│   └── level_profiles/
│       ├── n1.json
│       ├── n2.json
│       ├── n3.json
│       ├── n4.json
│       └── n5.json
├── samples/
│   └── kokoro_excerpt.txt
├── src/
│   └── leveled_reading/
│       ├── cli.py
│       ├── pipeline.py
│       ├── models.py
│       ├── ingestion.py
│       ├── chunking.py
│       ├── story.py
│       ├── llm/
│       ├── validation/
│       └── output.py
└── README.md
```

## 环境变量

敏感信息不要写进代码。项目使用 `.env` 分离 API key 等配置。

先复制模板：

```bash
cp .env.example .env
```

`.env` 示例：

```env
SAGAP_LLM_PROVIDER=mock
OPENAI_API_KEY=
SAGAP_OPENAI_MODEL=gpt-4.1-mini
SAGAP_OUTPUT_DIR=outputs
SAGAP_TEMPERATURE=0.2
SAGAP_MAX_OUTPUT_TOKENS=4096
```

说明：

| 变量 | 作用 |
|---|---|
| `SAGAP_LLM_PROVIDER` | `mock` 或 `openai` |
| `OPENAI_API_KEY` | OpenAI API key，仅 `openai` 模式需要 |
| `SAGAP_OPENAI_MODEL` | 使用的模型名 |
| `SAGAP_OUTPUT_DIR` | 默认输出目录 |
| `SAGAP_TEMPERATURE` | 生成温度 |
| `SAGAP_MAX_OUTPUT_TOKENS` | 单次输出 token 上限 |

`.env` 已经在 `.gitignore` 中，不应提交到仓库。

## 安装

推荐使用虚拟环境：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

如果要使用 OpenAI provider：

```bash
pip install -e ".[openai]"
```

不安装也可以用 `PYTHONPATH=src` 直接运行。

## 快速运行

mock 模式：

```bash
PYTHONPATH=src python -m leveled_reading.cli adapt \
  --input samples/kokoro_excerpt.txt \
  --level N3 \
  --output outputs/kokoro-n3 \
  --provider mock
```

安装后也可以使用脚本命令：

```bash
sagap adapt \
  --input samples/kokoro_excerpt.txt \
  --level N3 \
  --output outputs/kokoro-n3
```

查看等级配置：

```bash
PYTHONPATH=src python -m leveled_reading.cli profiles --level N3
```

## 使用 OpenAI provider

1. 安装可选依赖：

```bash
pip install -e ".[openai]"
```

2. 修改 `.env`：

```env
SAGAP_LLM_PROVIDER=openai
OPENAI_API_KEY=你的 API key
SAGAP_OPENAI_MODEL=你要使用的模型
```

3. 运行：

```bash
sagap adapt \
  --input samples/kokoro_excerpt.txt \
  --level N3 \
  --output outputs/kokoro-n3-openai
```

也可以临时覆盖 provider：

```bash
sagap adapt \
  --input samples/kokoro_excerpt.txt \
  --level N3 \
  --provider openai
```

## 输出文件

一次运行会生成：

```text
outputs/kokoro-n3/
├── adapted.md
├── story_bible.json
├── manifest.json
├── scenes.jsonl
├── adaptations.jsonl
├── validation.jsonl
└── costs.jsonl
```

各文件含义：

| 文件 | 内容 |
|---|---|
| `adapted.md` | 面向阅读和课堂展示的改编文本、注释、验证摘要 |
| `story_bible.json` | 人物、术语、风格、事件线 |
| `manifest.json` | 本次运行的基本信息 |
| `scenes.jsonl` | 切分后的 scene 数据 |
| `adaptations.jsonl` | 每个 scene 的改编结果和注释 |
| `validation.jsonl` | 等级、忠实性、连贯性验证结果 |
| `costs.jsonl` | provider、模型、粗略 token 统计 |

这些 JSONL 文件后续可以直接用于论文中的统计分析，例如：

- 不同目标等级的平均句长变化；
- 不同模型的 validation 通过率；
- 注释密度与等级适切性的关系；
- 忠实性分数与文本压缩率的关系；
- 每个 scene 的 token 成本与重试率。

## 流水线设计

当前实现的主流程在 `src/leveled_reading/pipeline.py`：

```text
load_text
  ↓
split_chapters
  ↓
chunk_chapters
  ↓
initialize_story_bible
  ↓
plan_scene
  ↓
rewrite_scene
  ↓
validate_scene
  ↓
revise_scene
  ↓
update_story_bible
  ↓
write_outputs
```

### 1. 文本输入与 chunking

`ingestion.py` 负责读取 UTF-8 文本、清洗空白并拆段。  
`chunking.py` 使用规则切分 scene：

- 章节标题；
- 空行和段落；
- 时间变化词，如 `その時`、`翌日`、`それから`；
- 最大 scene 字数限制。

当前是规则版 MVP。后续可以加入 LLM scene-boundary 判断，使切分更接近叙事单位。

### 2. Story Bible

`story.py` 维护全局信息：

- 人物及别名；
- 需要保留的文学关键词；
- 风格说明；
- scene 时间线。

这一步的作用是防止长篇改编中出现人物称呼、术语、叙事视角不一致。

### 3. Scene Plan

每个 scene 改写前先生成 `ScenePlan`，包括：

```json
{
  "scene_id": "ch01_sc001",
  "summary": "...",
  "must_keep_events": ["..."],
  "characters": ["私", "先生"],
  "tone": "literary, calm, source-faithful",
  "keywords_to_preserve": ["先生", "鎌倉"],
  "adaptation_notes": ["Use minimum necessary adaptation."]
}
```

这个中间层用于防止 LLM 把改编做成摘要。

### 4. Level Profile

等级配置位于 `config/level_profiles/`。每个等级不是单纯词表，而是一个综合 profile：

```json
{
  "level": "N3",
  "max_sentence_chars": 45,
  "grammar_preferred": ["〜ている", "〜ために"],
  "grammar_avoid": ["〜ざるを得ない", "〜に際して"],
  "replace_terms": {
    "常に": "いつも"
  },
  "annotation_terms": {
    "罪悪感": {
      "reading": "ざいあくかん",
      "explanation": "悪いことをしたと思って、心が苦しくなる気持ち。",
      "reason": "theme_keyword",
      "level_estimate": "N2+"
    }
  }
}
```

这里体现了本研究的核心设定：

- 语法范围更严格；
- 词汇范围不完全硬卡；
- 文学词、文化词、专名通过注释保留；
- N1 版本不强行把简单原文改难。

### 5. Validation

`validation/` 目前包含三类检查：

| 模块 | 作用 |
|---|---|
| `language_validator.py` | 句长、复杂语法、注释覆盖、注释密度 |
| `fidelity_validator.py` | 是否过度压缩、是否疑似摘要化、关键词覆盖 |
| `coherence_validator.py` | 人物称呼和全局术语一致性 |

输出为：

```json
{
  "scene_id": "ch01_sc001",
  "level_score": 100.0,
  "fidelity_score": 100.0,
  "coherence_score": 100.0,
  "issues": []
}
```

如果出现 `error` 或 `warning`，流水线会调用 `revise_scene` 进行局部修正，默认每个 scene 修正一次。

## 当前 MVP 的限制

当前版本适合做课堂 demo 和研究原型，不应直接宣称可以完整处理百万字小说。

主要限制：

- mock provider 只是规则式改写，不代表真实 LLM 表现；
- scene chunking 仍是规则切分，尚未加入 LLM 边界判断；
- 词汇和语法 profile 只是示例，需要结合真实参考词库扩展；
- validation 是启发式指标，不等于人工评价；
- token 成本是粗略估计，OpenAI 实际费用应以 API 返回和官方价格为准；
- 忠实性验证目前只做压缩率和关键词覆盖，后续应加入 QA-based fidelity。

## 后续扩展建议

优先级最高的扩展：

1. 接入真实日语形态素分析器，例如 SudachiPy 或 MeCab，用于词汇分级统计。
2. 将 `annotation_terms` 扩展为可外接词库接口。
3. 加入 LLM scene-boundary 判断。
4. 加入 QA-based fidelity：从原文生成问题，再检查改编文是否能回答。
5. 加入多模型实验配置：同一输入、同一 profile，对比不同模型。
6. 增加 `experiment.yaml`，记录 prompt 版本、模型、温度、文本范围和随机种子。
7. 将 validation 结果汇总成 CSV，方便论文图表制作。

## 论文实验可以如何使用

建议先做一个小规模实验：

```text
输入：一部作品的 3-5 个 scene
目标等级：N3 / N4
对照组：
  A. 直接 prompt 改写
  B. 只做分段改写
  C. SAGAP：Story Bible + Scene Plan + Validation
评价：
  等级适切性
  忠实性
  连贯性
  文学性人工评分
  注释有效性
  token 成本
```

这样可以把论文重点放在：

> LLM 本身不是创新点，带有日语教育约束、文学性约束和验证闭环的流水线设计才是创新点。

