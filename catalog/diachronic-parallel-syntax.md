# 历时与平行语料

[首页](../README.md) · [按研究需要进入](../docs/research-needs.md) · [OSF索引](osf.md) · [字段说明](../docs/data-dictionary.md)

共6个入口。资料状态与文件验收范围分别记录。

<a id="r056"></a>

## Google Books Ngrams

**R056** · 数据集 · 有数据发布说明

词与短语逐年频数、书籍计数及年度总量，可用于频率轨迹与部分历时变化分析。

| 字段 | 内容 |
| --- | --- |
| 语言与人群 | 多语种，按发布版本 |
| 数据性质 | 按年份汇总的n-gram频次；混合来源或待细分 |
| 获取方式 | 公开数据入口：官方分片公开下载 |
| 许可 | 按来源网站和具体数据版本的许可使用；本目录不对上游数据重新授权。 |
| 使用边界 | 不是完整书籍全文，也没有完整篇章语境；OCR、图书构成和版本差异会影响趋势。 |
| 标签 | 历时、词频、文化变化、语义变化、多语种 |
| 平台 | project_website |
| 核对依据 | 沿用首版文档核对；2026-10-17 |
| 实际文件核验 | **仅核对说明；未读数据文件** |
| 核对范围 | 沿用首版已核对的项目说明及访问文档；未批量验收原始文件。 |
| 下一步 | 定位并读取代表性数据文件，记录格式、行列或样本单位、变量和读取范围；核对数据版本、访问条件、署名和原始许可；若需申请，保留该限制。 |

[项目或数据入口](https://books.google.com/ngrams/datasets)

研究入口：[历时机制](../docs/research-needs.md#diachronic-mechanisms)。

待核实关联：[R057 HistWords](../catalog/diachronic-parallel-syntax.md#r057)、[R060 Project Gutenberg](../catalog/diachronic-parallel-syntax.md#r060)。仅保留原目录线索，未确认五类关系或具体文件可连接。

<a id="r057"></a>

## HistWords

**R057** · 派生资料 · 有数据发布说明

按年代训练的词向量及分析工具，可探索词义邻域及语义变化候选。

| 字段 | 内容 |
| --- | --- |
| 语言与人群 | 英语、法语、德语、中文等发布部分 |
| 数据性质 | 预计算历时词向量；混合来源或待细分 |
| 获取方式 | 公开数据入口：作者项目页公开向量和代码 |
| 许可 | 按来源网站和具体数据版本的许可使用；本目录不对上游数据重新授权。 |
| 使用边界 | 属于派生表示，未自动开放所有原始训练语料；向量漂移不必然就是词义变化。 |
| 标签 | 语义变化、历时、词向量、多语种 |
| 平台 | project_website |
| 核对依据 | 沿用首版文档核对；2026-10-17 |
| 实际文件核验 | **仅核对说明；未读数据文件** |
| 核对范围 | 沿用首版已核对的项目说明及访问文档；未批量验收原始文件。 |
| 下一步 | 定位并读取代表性数据文件，记录格式、行列或样本单位、变量和读取范围；核对数据版本、访问条件、署名和原始许可；若需申请，保留该限制。 |

[项目或数据入口](https://nlp.stanford.edu/projects/histwords/)

研究入口：[历时机制](../docs/research-needs.md#diachronic-mechanisms)。

待核实关联：[R056 Google Books Ngrams](../catalog/diachronic-parallel-syntax.md#r056)。仅保留原目录线索，未确认五类关系或具体文件可连接。

<a id="r058"></a>

## OPUS

**R058** · 资源集合 · 有数据发布说明

字幕、议会、新闻和其他来源的双语对齐文本，可按语言对和子库选择。

| 字段 | 内容 |
| --- | --- |
| 语言与人群 | 多语种，含中英 |
| 数据性质 | 平行与对齐语料集合；混合来源或待细分 |
| 获取方式 | 公开数据入口：大量子库提供公开下载；许可逐库核对 |
| 许可 | 集合不提供覆盖全部子库的统一使用许可，逐子库核对。 |
| 使用边界 | OPUS是集合入口，不具有覆盖全部子库的单一使用许可；机器对齐与翻译方向质量不同。 |
| 标签 | 翻译、双语、平行语料、跨语言、字幕 |
| 平台 | project_website |
| 核对依据 | 沿用首版文档核对；2026-10-17 |
| 实际文件核验 | **仅核对说明；未读数据文件** |
| 核对范围 | 沿用首版已核对的项目说明及访问文档；未批量验收原始文件。 |
| 下一步 | 定位并读取代表性数据文件，记录格式、行列或样本单位、变量和读取范围；核对数据版本、访问条件、署名和原始许可；若需申请，保留该限制。 |

[项目或数据入口](https://opus.nlpl.eu/)

待核实关联：[R039 GECO](../catalog/chinese-l2-bilingual.md#r039)、[R040 MECO](../catalog/chinese-l2-bilingual.md#r040)。仅保留原目录线索，未确认五类关系或具体文件可连接。

<a id="r060"></a>

## Project Gutenberg

**R060** · 资源集合 · 有数据发布说明

文学和历史书籍的TXT、EPUB等全文，可构建作者、体裁或时期相关的研究语料。

| 字段 | 内容 |
| --- | --- |
| 语言与人群 | 多语种，以英语文学材料较多 |
| 数据性质 | 可下载电子书全文；混合来源或待细分 |
| 获取方式 | 公开数据入口：免费逐书下载；版权状态与使用地区需核对 |
| 许可 | 多数作品在美国属于公版；逐书及使用地区的版权状态分别核对。 |
| 使用边界 | 多数作品是在美国的公版资料；作者年代不等于该电子文本所依版本年代，不能默认是平衡历时语料。 |
| 标签 | 文学、历时、作者、翻译、体裁 |
| 平台 | project_website |
| 核对依据 | 沿用首版文档核对；2026-10-17 |
| 实际文件核验 | **仅核对说明；未读数据文件** |
| 核对范围 | 沿用首版已核对的项目说明及访问文档；未批量验收原始文件。 |
| 下一步 | 定位并读取代表性数据文件，记录格式、行列或样本单位、变量和读取范围；核对数据版本、访问条件、署名和原始许可；若需申请，保留该限制。 |

[项目或数据入口](https://www.gutenberg.org/ebooks/)

补充及核对来源：

- [来源 1](https://www.gutenberg.org/policy/permission.html)

研究入口：[历时机制](../docs/research-needs.md#diachronic-mechanisms)。

待核实关联：[R056 Google Books Ngrams](../catalog/diachronic-parallel-syntax.md#r056)。仅保留原目录线索，未确认五类关系或具体文件可连接。

<a id="r194"></a>

## Indiana Parsed Corpus of Historical High German（IPCHG，高地德语历时句法树库）

**R194** · 数据集 · 有数据发布说明

项目在ReM、ReF和DTA文本上新增Penn式句法标注，可从主从句节点提取显性主语和限定动词的实际词序。固定提交去重后145份文本文件，本次按树终端计数1,270,153个表层词项。官网约165篇、140万词为建设目标。

| 字段 | 内容 |
| --- | --- |
| 语言与人群 | 中古高地德语、早期新高地德语和新高地德语散文，设计覆盖1050–1950年。固定提交中去重后的文件年份标签为1050–1946年，三个时期分别有43、57、45份文本文件 |
| 数据性质 | 实际散文的Penn式成分句法树，附词类、形态、部分词元及记录ID。UTF-8纯文本；语料与标注 |
| 获取方式 | 公开数据入口：固定GitHub提交的归档可直接下载，无需注册。三期目录另有旧版和跨目录重复。同一时期也有不同标注版本，引用时保留提交、文件名和版本。 |
| 许可 | CC BY-SA 4.0。官网链接指向该许可，并要求署名、链接项目及在同一许可下再分发。官网和仓库许可文字把简称写作CC BY-AT 4.0。研究引用Sapp等（2024）及所用提交。 |
| 使用边界 | 比较主从句词序时统一0.9前后的并列主句计数规则，并按文本、体裁、地区和从句类型检查。部分文件的ID元数据有变体。ReM、ReF及DTA与本库有原文重合，逐篇及段落对齐需另核。依存距离须先验证成分树转依存的规则。 |
| 标签 | 历时、德语、句法、成分树库、Penn、词序、主从句、形态标注 |
| 平台 | project_website, github |
| 核对依据 | 作者仓库说明；2026-11-15 |
| 实际文件核验 | **已完整检查选定文件；全库未验收** |
| 核对范围 | 下载固定提交并读取200份文本文件。排除54份历史目录版本，1650年Probstein保留ENHG中的较新标注。统计145份文件的表层词项，并在三个时期抽取显性主语和限定动词。一份文件的前缀在解析时跳过，另一份的一条括号记录排除。逐条标注准确性及逐篇原始出处待按研究范围核查。详见data/ipchg-file-check-2026-11-15.json。 |
| 下一步 | 已读取和解析的范围限于记录中的选定文件；继续核对其余分析所需文件及完整发布范围；核对数据版本、访问条件、署名和原始许可；若需申请，保留该限制。 |

[项目或数据入口](https://ipchg.iu.edu/corpus/index.html)

补充及核对来源：

- [来源 1](https://github.com/cdsapp/IPCHG-Corpus/tree/41db43ac4217fd7370dec5f495b6a7eb5783774e)
- [来源 2](https://codeload.github.com/cdsapp/IPCHG-Corpus/zip/41db43ac4217fd7370dec5f495b6a7eb5783774e)
- [来源 3](https://ipchg.iu.edu/corpus/corpus_structure.html)
- [来源 4](https://ipchg.iu.edu/corpus/licenses.html)
- [来源 5](https://ipchg.iu.edu/annotation/clauses_ip.html)
- [来源 6](https://ipchg.iu.edu/tagset/pos_labels.html)
- [来源 7](https://aclanthology.org/2024.lrec-main.807/)
- [来源 8](https://github.com/leo11wu/open-language-resources/blob/main/data/ipchg-file-check-2026-11-15.json)
- [来源 9](https://creativecommons.org/licenses/by-sa/4.0/deed.en)
- [来源 10](https://ipchg.iu.edu/corpus/versions.html)
- [来源 11](https://ipchg.iu.edu/annotation/clauses_cp.html)
- [来源 12](https://ipchg.iu.edu/tagset/splitting_lemmatization.html)
- [来源 13](https://github.com/cdsapp/IPCHG-Corpus/blob/41db43ac4217fd7370dec5f495b6a7eb5783774e/texts-NHG/1791_prediger_bavaria.ver0_9.txt)

研究入口：[结构分布](../docs/research-needs.md#structural-distribution) · [历时机制](../docs/research-needs.md#diachronic-mechanisms)。

待核实关联：[R059 Universal Dependencies（UD）](../catalog/syntax.md#r059)、[R191 DiACL Mouton Atlas（语法编码附录）](../catalog/crossling-cultural.md#r191)、[R196 Tycho Brahe Parsed Corpus of Historical Portuguese（历史葡萄牙语树库）](../catalog/diachronic-parallel-syntax.md#r196)。仅保留原目录线索，未确认五类关系或具体文件可连接。

<a id="r196"></a>

## Tycho Brahe Parsed Corpus of Historical Portuguese（历史葡萄牙语树库）

**R196** · 数据集 · 有数据发布说明

官网登记95篇、3,789,646词，其中32篇标为有句法、目录对应1,359,094词。实际可读句法为ZIP内30份，加单独下载的va_017。可分别统计限定主句中的主语显现和显性主语相对动词的位置。

| 字段 | 内容 |
| --- | --- |
| 语言与人群 | 历史葡萄牙语。可读句法材料涵盖葡萄牙和巴西的书信、叙事、报刊和戏剧等。单一作者篇目的出生年为1510–1836年 |
| 数据性质 | Penn-Helsinki式成分句法树，含词类、形态和空成分标注。PSD纯文本。官方篇目元数据含体裁、出生年、原文日期与出版地；语料与标注 |
| 获取方式 | 公开数据入口：官网ZIP与va_017无需登录即可下载。va_016列在官方目录，句法链接本次返回404，其含词类的XML已读取。ZIP有三个_part文件，另有项目目录注明节选的篇目。 |
| 许可 | 项目条款允许免费教学与科研，要求署名。商业使用须事先许可，仅允许按学术引用惯例转载有限片段。引用Galves、Andrade与Faria（2017）并注明所用文件。 |
| 使用边界 | 按作者出生年代、原文日期、体裁、作者和节选范围核对可比性。首层主语标签覆盖随篇目变化，例如m_003中865/1,859条初筛主句无直接主语标签，需另行判断其结构和标注口径。区分指称性零主语、虚主语、任指主语及痕迹。依存距离须先验证成分树转换规则。 |
| 标签 | 历时、葡萄牙语、句法、成分树库、Penn、词序、零主语、主语显现、体裁 |
| 平台 | project_website |
| 核对依据 | 项目说明；2026-11-17 |
| 实际文件核验 | **已完整检查选定文件；全库未验收** |
| 核对范围 | 解析ZIP内30份及单篇va_017，合计1,239,274个表层词项。排除4条括号失配记录并记录末尾控制字符。核对主句、词类、显性主语及指称性零主语。另核实va_016句法入口404及其XML的词类层。逐条标注准确性仍待查。详见data/tycho-brahe-file-check-2026-11-17.json。 |
| 下一步 | 已读取和解析的范围限于记录中的选定文件；继续核对其余分析所需文件及完整发布范围；核对数据版本、访问条件、署名和原始许可；若需申请，保留该限制。 |

[项目或数据入口](https://www.tycho.iel.unicamp.br/corpus/)

补充及核对来源：

- [来源 1](https://www.tycho.iel.unicamp.br/corpus/texts/psd.zip)
- [来源 2](https://www.tycho.iel.unicamp.br/corpus/texts/psd/va_017_psd.txt)
- [来源 3](https://www.tycho.iel.unicamp.br/corpus/catalogo.html)
- [来源 4](https://www.tycho.iel.unicamp.br/corpus/catalog.json)
- [来源 5](https://www.tycho.iel.unicamp.br/manual/2-noun-phrases/2-1-subject-np-np-sbj/2-1-1-subject-in-tensed-sentences.html)
- [来源 6](https://www.tycho.iel.unicamp.br/corpus/manual/pos2016.html)
- [来源 7](https://www.tycho.iel.unicamp.br/corpus/en/termos.html)
- [来源 8](https://doi.org/10.1075/lv.00004.gal)
- [来源 9](https://github.com/leo11wu/open-language-resources/blob/main/data/tycho-brahe-file-check-2026-11-17.json)
- [来源 10](https://www.tycho.iel.unicamp.br/corpus/texts/xml/va_016.xml)
- [来源 11](https://www.tycho.iel.unicamp.br/manual/12-empty-categories/12-1-null-subjects.html)

研究入口：[结构分布](../docs/research-needs.md#structural-distribution) · [历时机制](../docs/research-needs.md#diachronic-mechanisms)。

待核实关联：[R194 Indiana Parsed Corpus of Historical High German（IPCHG，高地德语历时句法树库）](../catalog/diachronic-parallel-syntax.md#r194)。仅保留原目录线索，未确认五类关系或具体文件可连接。

