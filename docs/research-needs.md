# 按研究需要进入

[首页](../README.md) · [按句法问题选资料](syntax-guide.md) · [字段与关系说明](data-dictionary.md)

以下是从现有目录人工选取的起点，不是全部匹配结果，也不改变任何文件核验状态。同一资源可支持多个问题；是否适用仍取决于具体版本、观测单位与所需文件。

- [结构分布](#structural-distribution)：哪些结构更常见？词序、依存关系和跨语言差异怎样比较？
- [加工证据](#processing-evidence)：结构或词汇属性与阅读时间、眼动、神经信号有什么关系？
- [交际调整](#communicative-adjustment)：说话者怎样随伙伴、共同知识和理解困难调整表达？
- [跨模态规律](#cross-modal-patterns)：口语与手语的频率、感知运动属性和形式时长怎样比较？
- [历时机制](#diachronic-mechanisms)：频率或语义怎样随时间变化？哪些变化可能来自语料构成？

<a id="structural-distribution"></a>

## 结构分布

哪些结构更常见？词序、依存关系和跨语言差异怎样比较？

先区分语料中的结构频率与语言层面的类型学编码；树库体裁、标注方式和语言谱系会影响比较。

| 资源 | 适合看什么 | 使用前确认 | 已记录文件核验 |
| --- | --- | --- | --- |
| [R059 Universal Dependencies（UD）](../catalog/syntax.md#r059) | 从依存树提取词序、依存距离和结构频率。 | 选择明确的树库与发行版本；分开人工与自动标注，检查体裁、分词和许可。 | 仅核对说明；未读数据文件 |
| [R061 UD-English-CHILDES（儿童及成人互动依存树库）](../catalog/syntax.md#r061) | 比较英语儿童与成人互动中的依存结构。 | 区分说话者角色、年龄、gold/silver与切分；只核对过开发集，且与CHILDES同源。 | 已完整检查选定文件；全库未验收 |
| [R045 WALS](../catalog/crossling-cultural.md#r045) | 查询跨语言词序及其他类型学特征。 | 核对每项特征的定义、语言覆盖和描述来源；缺失值不是结构不存在。 | 仅核对说明；未读数据文件 |
| [R046 Grambank](../catalog/crossling-cultural.md#r046) | 比较统一编码下的跨语言语法特征。 | 控制谱系和地理相关；不可未经定义核对就与WALS同名变量合并。 | 仅核对说明；未读数据文件 |
| [R182 Multi-CAST（多语言口语叙事与指称标注）](../catalog/spoken-variation.md#r182) | 比较自然叙事中的论元表达、语法关系、有生性和指称连续性。 | GRAID/RefIND不是UD依存标注；核对各语言的说话者、文本采样与编码，分开同源导出格式；音频另行归档。 | 已完整检查选定文件；全库未验收 |

```sh
python3 scripts/query.py --need structural-distribution
```

<a id="processing-evidence"></a>

## 加工证据

结构或词汇属性与阅读时间、眼动、神经信号有什么关系？

逐词、逐被试观测与词项聚合值是不同分析单位；句法标注与行为/神经信号的对齐需要单独验证。

| 资源 | 适合看什么 | 使用前确认 | 已记录文件核验 |
| --- | --- | --- | --- |
| [R077 Natural Stories Corpus](../catalog/syntax.md#r077) | 研究低频句法结构与自定步速阅读时间。 | 采用作者2025年修正RT错位后的版本；检查故事、词位和被试键，文本含人工设计。 | 仅核对说明；未读数据文件 |
| [R118 Provo Corpus（预测度与眼动）](../catalog/reading-neuro.md#r118) | 研究语境预测度与逐词阅读眼动。 | 分别确认常模和眼动文件的读取范围；两者被试不同，词位连接尚需按具体版本检查。 | 已完整检查选定文件；全库未验收 |
| [R119 ZuCo（联合EEG与眼动，含版本入口）](../catalog/reading-neuro.md#r119) | 研究自然阅读中的EEG与眼动信号。 | 区分ZuCo版本、任务和被试，确认同步与预处理层级；选定文件检查不等于全库验收。 | 已完整检查选定文件；全库未验收 |
| [R040 MECO](../catalog/chinese-l2-bilingual.md#r040) | 比较多语言L1/L2阅读眼动与个体差异。 | 只使用已发布波次；核对文本可比性、读者条件及可用文件，现有完整读取仅为说明文档。 | 已读辅助文件；主体观测数据未验 |

```sh
python3 scripts/query.py --need processing-evidence
```

<a id="communicative-adjustment"></a>

## 交际调整

说话者怎样随伙伴、共同知识和理解困难调整表达？

区分自然会话、任务诱发互动和加工后的协调指标；要分析修复或理解成功，须先找到相应事件与结果。

| 资源 | 适合看什么 | 使用前确认 | 已记录文件核验 |
| --- | --- | --- | --- |
| [R014 HCRC Map Task Corpus](../catalog/spoken-variation.md#r014) | 研究地图协作中的指称、澄清与信息分配。 | 核对对话、轮次和地图标注；这是合作任务语料，不能直接代表日常会话。 | 仅核对说明；未读数据文件 |
| [R015 CABank](../catalog/spoken-variation.md#r015) | 寻找带精细转写和同步媒体的自然互动子库。 | 按具体子库确认获取条件、转写规范与修复标注；集合入口不是一张可直接分析的表。 | 仅核对说明；未读数据文件 |
| [R174 SCARFS：熟人与陌生人的指称互动](../catalog/social-interaction.md#r174) | 比较熟人与陌生人的指称选择及游戏行为。 | 保留说话者、伙伴、会话与记录键的嵌套；Lost不等于理解失败，首次听者猜测仍待确认。 | 已完整检查选定文件；全库未验收 |
| [R181 儿童—照护者语言协调与词汇学习（38组亲子）](../catalog/child-language.md#r181) | 研究亲子互动协调与词汇学习的关系。 | 区分38组亲子的不同粒度处理表与打乱对照；不能把各表行数相加为独立被试。 | 已完整检查选定文件；全库未验收 |

```sh
python3 scripts/query.py --need communicative-adjustment
```

<a id="cross-modal-patterns"></a>

## 跨模态规律

口语与手语的频率、感知运动属性和形式时长怎样比较？

这些资源提供不同模态的候选测量，不是现成的同材料对照；须另定义可比单位、词义映射和测量方法。

| 资源 | 适合看什么 | 使用前确认 | 已记录文件核验 |
| --- | --- | --- | --- |
| [R026 Lancaster Sensorimotor Norms](../catalog/lexical-cognition.md#r026) | 取得英语词的感知运动属性常模，筛选比较维度。 | 主观属性常模不是自然使用频率，也没有据此建立与手语词项的一对一映射。 | 已完整检查选定文件；全库未验收 |
| [R050 ASL-LEX](../catalog/sign-figurative.md#r050) | 研究ASL词项的主观频率、象似性与形式属性。 | 主观频率不等于语料词频；孤立示范时长不可直接与自然会话时长合并。 | 已完整检查选定文件；全库未验收 |
| [R052 Public DGS Corpus（MEINE DGS）](../catalog/sign-figurative.md#r052) | 在自然DGS语料中检查词型与实际使用实例。 | 公开子库范围、词型标注、视频时间与访问条件逐项确认；不能把全档案视为开放。 | 仅核对说明；未读数据文件 |
| [R134 德语词末清化不完全中和：数据与脚本](../catalog/speech-phonetics.md#r134) | 取得口语产生/知觉及刺激声学测量的参照。 | 分开刺激表、产生观测和知觉试次；特定德语清化实验不是跨模态或自然频率总体。 | 已完整检查选定文件；全库未验收 |

```sh
python3 scripts/query.py --need cross-modal-patterns
```

<a id="diachronic-mechanisms"></a>

## 历时机制

频率或语义怎样随时间变化？哪些变化可能来自语料构成？

按年代变化是描述证据；解释机制还需控制体裁、版本、来源构成和采样，不能由频数或向量漂移直接推出因果。

| 资源 | 适合看什么 | 使用前确认 | 已记录文件核验 |
| --- | --- | --- | --- |
| [R056 Google Books Ngrams](../catalog/diachronic-parallel-syntax.md#r056) | 观察词与短语的逐年频数轨迹。 | 固定Ngram版本和分母，检查OCR与图书构成；不具备完整篇章语境。 | 仅核对说明；未读数据文件 |
| [R057 HistWords](../catalog/diachronic-parallel-syntax.md#r057) | 探索历时词向量的语义邻域变化候选。 | 核对具体向量的训练来源与年代；计算表示不是独立观测，漂移可能来自频率和训练差异。 | 仅核对说明；未读数据文件 |
| [R060 Project Gutenberg](../catalog/diachronic-parallel-syntax.md#r060) | 为需要全文语境的问题筛选作品与来源。 | 核对作品、版本和电子文本年代及体裁；自建样本不是默认平衡的历时语料。 | 仅核对说明；未读数据文件 |

```sh
python3 scripts/query.py --need diachronic-mechanisms
```

## 资源关系也要分开判断

分类条目分别展示有依据的关系和待核实关联。关系说明不刷新原数据的读取或验收范围；共享材料不表示同一批被试，派生资料不能算作独立重复验证。

| 关系类型 | 当前有依据记录数 |
| --- | ---: |
| 派生自（`derived_from`） | 2 |
| 同一批被试（`same_participants`） | 0 |
| 同一套材料（`same_materials`） | 1 |
| 子集（`subset_of`） | 1 |
| 已验证可连接（`verified_join`） | 0 |

0表示尚未记录有充分依据的关系，不表示已证明不存在。“已验证可连接”必须另外记录两个文件的版本、完整文件哈希、连接键、匹配诊断和实际检查报告；仅共享词形、语言标识或提示词不能满足这个条件。定义与维护方法见[字段说明](data-dictionary.md#资源关系)。
