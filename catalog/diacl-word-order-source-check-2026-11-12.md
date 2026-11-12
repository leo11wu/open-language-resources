# DiACL、WALS 与 Grambank 的主从句词序出处核查

2026-11-12 · [DiACL R191](crossling-cultural.md#r191) · [WALS R045](crossling-cultural.md#r045) · [Grambank R046](crossling-cultural.md#r046) · [逐条记录与文件版本](../data/diacl-word-order-source-check-2026-11-12.json)

在能对齐且有相关赋值引文的条目中，DiACL 与 **WALS 有 6 个条目**引用相同书目，与 **Grambank 有 9 个条目**引用相同书目。**Batsbi、Lezgian 和 Turkmen** 三个条目在三库均找到同一语法描写。Turkmen 的重叠限于 DiACL 从句栏的引文。

| 对照库 | 对齐后有相关赋值记录的条目 | 至少一项明确赋值带引文 | 与 DiACL 引用相同书目 | 涉及 DiACL 主句栏 | 涉及 DiACL 从句栏 |
| --- | ---: | ---: | ---: | ---: | ---: |
| WALS 81A、81B | 59 | 54 | 6 | 5 | 6 |
| Grambank GB131–GB134 | 50 | 47 | 9 | 8 | 8 |

Grambank 的 9 个条目中，8 个涉及 GB134。将 DiACL 这一侧也限定到从句栏，与 GB134 共有 7 个书目匹配。Tajik 两库引用同一著作的不同印次，另记于下表之外。

## 核查依据

- **DiACL** 分别记录主句、从句的典型词序。将 Mouton Atlas v1 的 `Appendix2c` 第 T、Y 列和官网欧亚数据集的 `Main clause`（52）、`Subordinate clause`（53）对齐。148 个条目中，主句 147 格、从句 144 格有值，重建位串后全部一致。语言名中有两处对照，`Low_German` 对应 `Low German`，`Modern Armenian` 对应 `Eastern Armenian`。逐值引文来自 2026-11-12 在线导出，固定归档的词序表没有引文字段。相同位串只能确认编码一致，2018 年录入时的逐格引文仍待核对。本次定位了书中 Appendix 4b 的书目信息，未取得正文。[固定归档](https://zenodo.org/records/3817133) · [官网欧亚导出](https://diacl.uni-frankfurt.de/TypoDataSet/Download/550) · [DiACL 方法](https://doi.org/10.1371/journal.pone.0205313) · [图谱 Appendix 4b](https://doi.org/10.1515/9783110367416-019)
- **WALS v2020.6** 的 81A 给出主导的 S/V/O 排列或无单一主导顺序，81B 细分两种主导排列。第 81 章讨论语序受句法环境制约的情形。赋值表没有单列从句词序，本次用 81A、81B 的引文查共享书目。[固定版](https://github.com/cldf-datasets/wals/releases/tag/v2020.6) · [第 81 章](https://wals.info/chapter/81)
- **Grambank v1.0.3** 的 GB131–GB133 记录及物句中实义动词相对完整名词短语论元的位置。GB134 检查语用无标记的主句语序是否也可用于从句，允许从句另有额外语序。[固定版](https://github.com/grambank/grambank/releases/tag/v1.0.3) · [GB131](https://grambank.clld.org/parameters/GB131) · [GB132](https://grambank.clld.org/parameters/GB132) · [GB133](https://grambank.clld.org/parameters/GB133) · [GB134](https://grambank.clld.org/parameters/GB134)

语言名称和 Glottocode 用来定位待核查的条目。遇到同码多变体或历史阶段不明的情况保留歧义。Karachay-Balkar、Uzbek 等个别条目依据对应名称和标识人工对照。用题名和作者找候选后核对作者、题名、年份、版次和可见页码。确认计数取 DiACL 选中值及另一库明确赋值所附引文，按语言或变体条目去重。只用赋值行的引文，逐条记录保留无引文和未知值。未匹配和未标页码的记录仍可能有共同来源。

## 确认引用相同书目的记录

页码为各库记录所报。GB131–133 的页码在逐条记录中保留。表中“未标”指相应的赋值引文未附页码。

| 对照库 | DiACL 条目 | 共同书目 | DiACL 主句／从句引文页码 | 对照赋值与引文页码 |
| --- | --- | --- | --- | --- |
| WALS | Batsbi | Holisky & Gagua 1994, *Tsova-Tush (Batsbi)* | 187／187 | 81A，198–199 |
| WALS | Karachay-Balkar | Seegmiller 1996, *Karachay* | 37／38–39 | 81A，37 |
| WALS | Kurdish (Sorani) | Blau 1980, *Manuel de kurde* | 42／156 | 81A，42 |
| WALS | Lezgian | Haspelmath 1993, *A Grammar of Lezgian* | 未标／未标 | 81A，5、298 |
| WALS | Turkmen | Clark 1998, *Turkmen Reference Grammar* | 主句引用 Schönig／502 | 81A，498 |
| WALS | Uzbek | Sjoberg 1963, *Uzbek Structural Grammar* | 144／157 | 81A，144、150、154 |
| Grambank | Batsbi | Holisky & Gagua 1994, *Tsova-Tush (Batsbi)* | 187／187 | GB131–133，198–200 内；GB134，198–203、198–205、201–206、202 |
| Grambank | Czech | Naughton 2005, *Czech: An Essential Grammar* | 216／从句来自语言顾问 | GB131–133，216；GB134，218 |
| Grambank | Kashmiri | Koul & Wali 2006, *Modern Kashmiri Grammar* | 127／127 | GB131–134，127 |
| Grambank | Khwarshi | Khalilova 2009, *A Grammar of Khwarshi* | 未标／未标 | GB131–133，277、304；GB134，1–494 |
| Grambank | Lezgian | Haspelmath 1993, *A Grammar of Lezgian* | 未标／未标 | GB131–134，298–299 |
| Grambank | Maithili | Yadav 1996, *A Reference Grammar of Maithili* | 302／302 | GB131–133，282–284；GB134，283 |
| Grambank | Turkmen | Clark 1998, *Turkmen Reference Grammar* | 主句引用 Schönig／502 | GB131–132，498；GB133，114、498；GB134，498 |
| Grambank | Ukrainian | Pugh & Press 1999, *Ukrainian: A Comprehensive Grammar* | 93／179–180 | GB131–133，136；GB134，292–293 |
| Grambank | Welsh | King 2003, *Modern Welsh: A Comprehensive Grammar* 第 2 版 | 20／310 | GB131–133，20；GB134 引用 Jones |

### 共用引文与编码口径

**克什米尔语（Kashmiri）**。DiACL 的 `T42`、`Y42` 分别是 V2、SOV，官网对应的记录 5819、6691 均引 Koul 与 Wali（2006）第 127 页。GB134-kash1277 的值为 1，引用同书同页，另列 Koul 的 *Spoken Kashmiri*。原书第 127 页和 §4.3.2.1 说明普通限定从句保留 V2，部分非限定从句、关系从句等允许 SOV。DiACL 的 SOV 记录备注也注明限定从句用 V2。若研究对象是限定补语从句，应使用这一更细的结构信息。WALS 81A 的 SVO 引用 Wali 与 Koul（1997）第 89 页。[原书](https://ikashmir.net/onkoul/pdf/ModernKashmiriGrammar.pdf) · [Grambank 书目](https://grambank.clld.org/sources/gKoulWaliKashmiri2006)

**德语（German）**。DiACL 的主句 V2、从句 SOV 均引 Engel（1988），未标页码。WALS 的 81A 和 81B 引 Lederer（1969）第 575 页起，亦记录编码者知识，分别标为无单一主导词序、SOV 或 SVO。GB134 手册用德语作解释，Grambank v1.0.3 的语言表未见标准德语 `stan1295` 的数据行。[DiACL 方法文献 §2.3](https://doi.org/10.1371/journal.pone.0205313) · [WALS 81A 德语](https://wals.info/values/81A-ger) · [WALS 81B 德语](https://wals.info/values/81B-ger) · [GB134 手册](https://grambank.clld.org/parameters/GB134)

**上一轮发现的两个语序差异条目**。DiACL 的 Cornish 两栏引用 Williams（2011），WALS 81A 的 SVO 引 Jenner（1904）第 158 页，Grambank 发布版未见同一条目。Romani (Sepečides) 在 DiACL 两栏均引 Cech 与 Heinschink（1999），页码分别为 137、144。WALS 有同名变体入口，但无 81A、81B 赋值。Grambank 发布版未见该变体的词序行。[WALS Cornish](https://wals.info/values/81A-crn) · [WALS Romani (Sepecides)](https://wals.info/languoid/lect/wals_code_rse)

**不同版次或形式**。Tajik 的 DiACL 引 Rastorgueva（1992）第 94 页，WALS 引 Rastorgueva（1963）第 94–95 页。馆藏把 1992 年版与 1963 年同名出版物相对应，按同著作重印记。Dutch 的 Shetter（1958）和 Shetter & Ham（2007，第 9 版）、Northern Saami 的 Nickel（1990）和 Nickel & Sammallahti（2011，修订版）按版次分列。Kryz 的论文与出版语法书、Persian 的习题解答册与合订版也单列。对 Persian，页码恰好相同仍需检查分别指向合订版的哪一部分。[Tajik 馆藏记录](https://ci.nii.ac.jp/ncid/BA22618838) · [Dutch 出版方](https://www.routledge.com/Dutch-An-Essential-Grammar/Shetter-Ham/p/book/9781138955479) · [Northern Saami 版次](https://samiskbibliotektjeneste.tromsfylke.no/2012/01/26/klaus-p-nickel-pekka-sammallahti-nordsamisk-grammatikk-2/) · [Persian 出版方前言](https://assets.cambridge.org/97805210/91244/frontmatter/9780521091244_frontmatter.pdf)

合并数据或做跨库复核时，可将确认共用的书目视为同一个证据来源，并同时保留数据库、特征、从句类型和定位页。是否用了同一组例句或沿用另一库的编码，需要额外证据。这里的计数只覆盖所查词序指标和版本。
