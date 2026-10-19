# OSF实际文件核查 · 2026-10-19

[首页](../README.md) · [总核验台账](verification-status.md) · [结构化结果](../data/osf-file-audit-2026-10-19.json) · [核查程序](../scripts/audit_osf.py)

**本轮尚未完成全部85项。** 任务包括73条已收录OSF关联资源和12条候选。主目录中13条新增实际文件读取，其中11条读到了观测/常模数据，2条只读到辅助文件；另60条尚无本轮文件读取。

本轮完整下载37个选定文件，其中17个为观测/常模文件；两份ZIP另各解压并解析4个成员。文件、压缩包成员、目录条目和独立数据集不是相同计数单位。所有检查均限于代表文件，**全资源验收为0**。

12条候选的当前入口均已检查：6条只有可读材料/论文/统计输出，5条当前文件区为空或为冻结注册，1条节点/注册接口404。5个注册所关联原项目在追查时受429限流，最终发布情况仍待核对。本轮新增晋升0条，候选仍12条。不能把“尚未确认”写成“永远没有数据”。

## 访问与方法边界

- OSF实际公开API和多个下载端点已返回可解析内容；浏览器网页仍为空白壳，未确认全平台恢复。
- 批量查询随后返回HTTP429。官方[API文档](https://developer.osf.io/)说明匿名访问限100次/小时；本轮响应没有Retry-After头，已停止继续消耗API额度。该限制不是各资源私有或删除的证据。
- 读取范围包括完整CSV/工作簿、R数据对象、ZIP目录与选定成员、PDF全文文本及Word文档XML。未运行下载的研究脚本。成功下载只说明可取得；内容类别按变量和官方说明另行判断。
- 大型目录最多枚举8个节点、每节点24个目录、最多3,000个文件；早期已完成的个别清单范围较大。失败、未遍历的目录、版本和子组件均保留限制，已列文件数是已知下界。
- 37份下载均记录SHA-256，作者GitHub替代文件同时核对Git blob哈希。原表、参与者信息与转写正文留在本地缓存，未上传。

## 85项逐项结果

OSF已列文件是本轮取得清单中的下界；0也可能表示尚未列到，不能自动解释成空项目。作者替代仓库的实际下载另计在实读文件数中。

| 编号 | 项目 | 本轮结果 | OSF已列文件下界 | 实读文件数 |
| --- | --- | --- | ---: | ---: |
| R005 | [ManyBabies 1（MB1）](https://github.com/manybabies/mb1-analysis-public) | 已读代表性观测/常模文件 | 0 | 2 |
| R023 | [English Lexicon Project（ELP）](https://elexicon.wustl.edu/) | 已读代表性观测/常模文件 | 5 | 3 |
| R024 | [英语习得年龄常模（Kuperman等及相关扩展）](https://osf.io/d7x6q/) | 已读代表性观测/常模文件 | 3 | 2 |
| R025 | [英语具体性常模（Brysbaert等）](https://osf.io/kj76e/) | 已读代表性观测/常模文件 | 5 | 2 |
| R026 | [Lancaster Sensorimotor Norms](https://www.lancaster.ac.uk/psychology/lsnorms/) | 已读代表性观测/常模文件 | 45 | 2 |
| R040 | [MECO](https://meco-read.com/) | 仅辅助文件已读 | 21 | 2 |
| R078 | [Syntactic Ambiguity Processing Benchmark（SAP）](https://osf.io/b6rqh/) | 已读代表性观测/常模文件 | 79 | 2 |
| R079 | [冰岛语主语开头V3结构可接受度](https://osf.io/mg2r8/) | 已读代表性观测/常模文件 | 3 | 1 |
| R080 | [Agreement Attraction：语法句判断数据](https://osf.io/eawg5/) | 已读代表性观测/常模文件 | 8 | 2 |
| R081 | [Hierarchical Structure and Memory in Agreement Attraction](https://osf.io/j85sp/) | 接口失败，未确认数据 | 0 | 0 |
| R082 | [从主语抽取与话语功能：英法七个实验](https://osf.io/mtngd/) | 接口失败，未确认数据 | 0 | 0 |
| R083 | [矩阵动词重复与PO/DO结构启动](https://osf.io/p8f2c/) | 因API额度限制尚未检查 | 0 | 0 |
| R084 | [西班牙语理解中的岛效应](https://osf.io/ckxaw/) | 因API额度限制尚未检查 | 0 | 0 |
| R085 | [Wordform Boost in Structural Priming](https://osf.io/sbvfy/) | 因API额度限制尚未检查 | 0 | 0 |
| R086 | [中文嵌入wh问句作用域眼动实验](https://osf.io/as4h7/) | 因API额度限制尚未检查 | 0 | 0 |
| R087 | [18月龄婴儿非局部句法依存数据](https://osf.io/4sz9w/) | 因API额度限制尚未检查 | 0 | 0 |
| R088 | [英荷双及物构式抽样数据](https://osf.io/7ntmk/) | 因API额度限制尚未检查 | 0 | 0 |
| R089 | [不同一致依存的预测加工](https://osf.io/mbtcd/) | 因API额度限制尚未检查 | 0 | 0 |
| R090 | [捷克语花园路径句：开放式理解问题](https://osf.io/98g26/) | 因API额度限制尚未检查 | 0 | 0 |
| R091 | [大样本英语语法学习年龄数据（Hartshorne等）](https://osf.io/pyb8s/) | 因API额度限制尚未检查 | 0 | 0 |
| R092 | [CONcreTEXT（语境具体性常模）](https://osf.io/u3pc4/) | 因API额度限制尚未检查 | 0 | 0 |
| R093 | [GLEAN（德语外推情感常模）](https://osf.io/a6w53/) | 因API额度限制尚未检查 | 0 | 0 |
| R094 | [西班牙语1,252条习语心理语言与情感常模](https://osf.io/p75c3/) | 因API额度限制尚未检查 | 0 | 0 |
| R095 | [Six Semantic Dimension Database（六维语义）](https://osf.io/n5vke/) | 因API额度限制尚未检查 | 0 | 0 |
| R096 | [Socialness Norms（8,388英语词社会性）](https://osf.io/yjz85/) | 因API额度限制尚未检查 | 0 | 0 |
| R097 | [English Semantic Feature Production Norms（4,436概念）](https://osf.io/cjyzw/) | 因API额度限制尚未检查 | 0 | 0 |
| R098 | [Body–Object Interaction（9,000余英语词）](https://osf.io/6syf3/) | 因API额度限制尚未检查 | 0 | 0 |
| R099 | [Humor of English Words（英语变体比较）](https://osf.io/pg3fr/) | 因API额度限制尚未检查 | 0 | 0 |
| R100 | [Three Terms Task（3TT）](https://osf.io/at8cs/) | 因API额度限制尚未检查 | 0 | 0 |
| R101 | [语言输入的内容与时间：3岁词汇预测](https://osf.io/sgjbh/) | 因API额度限制尚未检查 | 0 | 0 |
| R102 | [六大洲1,001名儿童日常语言输入与产出](https://osf.io/9v2m5/) | 因API额度限制尚未检查 | 0 | 0 |
| R103 | [成人对婴儿发声的自然回应](https://osf.io/a6vps/) | 因API额度限制尚未检查 | 0 | 0 |
| R104 | [斯瓦希里语早期词汇纵向CDI数据](https://osf.io/rey6m/) | 因API额度限制尚未检查 | 0 | 0 |
| R105 | [儿童词义习得：CHILDES义项聚类与人工评价](https://osf.io/86yxz/) | 因API额度限制尚未检查 | 0 | 0 |
| R106 | [2月龄婴儿类别匹配词汇学习眼动](https://osf.io/arfqv/) | 因API额度限制尚未检查 | 0 | 0 |
| R107 | [儿童非相邻依存学习：刺激与分析材料](https://osf.io/43t9q/) | 因API额度限制尚未检查 | 0 | 0 |
| R111 | [L2英语在线掩蔽形态启动](https://osf.io/ty4wd/) | 因API额度限制尚未检查 | 0 | 0 |
| R112 | [L1意大利语–L2英语形态启动与熟练度](https://osf.io/62bek/) | 因API额度限制尚未检查 | 0 | 0 |
| R113 | [俄德双语屈折加工与习得年龄](https://osf.io/ugbsd/) | 因API额度限制尚未检查 | 0 | 0 |
| R114 | [自由句子产生中的提示与自愿语码转换](https://osf.io/73vfx/) | 因API额度限制尚未检查 | 0 | 0 |
| R115 | [L1–L2相似性与词汇编码](https://osf.io/e637k/) | 因API额度限制尚未检查 | 0 | 0 |
| R116 | [L2到L1同源词与跨语言同形词启动](https://osf.io/2swyg/) | 因API额度限制尚未检查 | 0 | 0 |
| R117 | [英意晚期双语者L1磨蚀与L2习得](https://osf.io/bm3tj/) | 因API额度限制尚未检查 | 0 | 0 |
| R118 | [Provo Corpus（预测度与眼动）](https://osf.io/sjefs/) | 因API额度限制尚未检查 | 0 | 0 |
| R119 | [ZuCo（联合EEG与眼动，含版本入口）](https://osf.io/q3zws/) | 因API额度限制尚未检查 | 0 | 0 |
| R120 | [CopCo（丹麦语自然阅读眼动）](https://osf.io/ud8s5/) | 因API额度限制尚未检查 | 0 | 0 |
| R121 | [TiNT（荷兰语同步EEG与自定步速阅读）](https://osf.io/g32rp/) | 仅辅助文件已读 | 0 | 1 |
| R122 | [g-Rel-READER（阅读相关性判断）](https://osf.io/3bvtx/) | 因API额度限制尚未检查 | 0 | 0 |
| R123 | [OneStop All Regimes（英语阅读方式比较）](https://osf.io/azj2g/) | 因API额度限制尚未检查 | 0 | 0 |
| R130 | [VoxCommunis（多语言强制对齐语音）](https://huggingface.co/datasets/pacscilab/VoxCommunis/) | 因API额度限制尚未检查 | 0 | 0 |
| R131 | [Audio-BNC / SPADE子集](https://osf.io/dgn2a/) | 因API额度限制尚未检查 | 0 | 0 |
| R132 | [英语与韩语母语者英语韵尾清浊声学数据](https://osf.io/fbms4/) | 因API额度限制尚未检查 | 0 | 0 |
| R133 | [高保真消声多方向语音实验语料](https://osf.io/w4h9f/) | 因API额度限制尚未检查 | 0 | 0 |
| R134 | [德语词末清化不完全中和：数据与脚本](https://osf.io/y7tdq/) | 因API额度限制尚未检查 | 0 | 0 |
| R135 | [线上、线下及口罩条件的VOT与元音共振峰](https://osf.io/xyh3k/) | 因API额度限制尚未检查 | 0 | 0 |
| R136 | [语音趋同AXB知觉的贝叶斯元分析](https://osf.io/8s9r5/) | 因API额度限制尚未检查 | 0 | 0 |
| R137 | [多语言学习者VOT知觉：数据与代码](https://osf.io/m7a43/) | 因API额度限制尚未检查 | 0 | 0 |
| R138 | [间接请求的策略礼貌：207人实验](https://osf.io/xsq3p/) | 因API额度限制尚未检查 | 0 | 0 |
| R139 | [手势、音效与表情符号的共语言推论](https://osf.io/n4ks9/) | 因API额度限制尚未检查 | 0 | 0 |
| R140 | [自由选择推论与同质性实验](https://osf.io/56qvw/) | 因API额度限制尚未检查 | 0 | 0 |
| R141 | [非典型习语语境：人类与LLM判断](https://osf.io/zq6ht/) | 已读代表性观测/常模文件 | 1 | 1 |
| R142 | [叙事自由回忆数据集](https://osf.io/h2pkv/) | 已读代表性观测/常模文件 | 0 | 1 |
| R156 | [NHB形义规律性研究：分析复现包](https://osf.io/qzaxk/) | 因API额度限制尚未检查 | 0 | 0 |
| R170 | [挪威语wh抽取与关系化岛效应数据](https://osf.io/ma9jp/) | 因API额度限制尚未检查 | 0 | 0 |
| R171 | [中文体动词补语强制转换：自定步速阅读](https://osf.io/wd2g7/) | 因API额度限制尚未检查 | 0 | 0 |
| R172 | [西班牙语关系从句岛效应：实验数据与代码](https://osf.io/t9vpq/) | 因API额度限制尚未检查 | 0 | 0 |
| R173 | [事件结构、习语与轻动词的结构启动](https://osf.io/zx6wv/) | 因API额度限制尚未检查 | 0 | 0 |
| R174 | [SCARFS：熟人与陌生人的指称互动](https://github.com/seantrott/scarfs) | 因API额度限制尚未检查 | 0 | 0 |
| R175 | [烹饪对话礼貌：公开标注、模拟样例与分析](https://github.com/delsweil/CHIIR2026_politeness) | 因API额度限制尚未检查 | 0 | 0 |
| R176 | [LLM方式含意：目标刺激集与分析脚本](https://osf.io/jp35t/) | 因API额度限制尚未检查 | 0 | 0 |
| R177 | [波兰语语义相关度、启动与语义向量](https://osf.io/2x8ka/) | 因API额度限制尚未检查 | 0 | 0 |
| R178 | [无意识语义加工：空间—时间隐喻启动](https://osf.io/wc7by/) | 因API额度限制尚未检查 | 0 | 0 |
| R179 | [Coretta元音时长与辅音清浊研究集合](https://osf.io/w92me/) | 已读代表性观测/常模文件 | 0 | 2 |
| C002 | [墨西哥西班牙语岛效应](https://osf.io/cs5z3/) | 材料/论文/统计输出已读 | 5 | 5 |
| C003 | [中英双语合理性与结构重分析启动](https://osf.io/hcdqe/) | 元数据已读；无主体数据读取 | 0 | 0 |
| C004 | [中文把字句二语句法阻断](https://osf.io/qehr4/) | 接口失败，未确认数据 | 0 | 0 |
| C006 | [简化关系从句的句法适应](https://osf.io/5aynd/) | 材料/论文/统计输出已读 | 1 | 1 |
| C007 | [Acceptability Judgement Tasks and Grammatical Theory](https://osf.io/qe865/) | 材料/论文/统计输出已读 | 1 | 1 |
| C010 | [themself/themselves社会句法判断](https://osf.io/2s8hm/) | 材料/论文/统计输出已读 | 4 | 4 |
| C011 | [双语儿童EEG研究](https://osf.io/j5epb/) | 元数据已读；无主体数据读取 | 0 | 0 |
| C012 | [儿童与照护者协调](https://osf.io/9z5qn/) | 元数据已读；无主体数据读取 | 0 | 0 |
| C013 | [跨语言习语激活](https://osf.io/kuqfe/) | 材料/论文/统计输出已读 | 1 | 1 |
| C016 | [政治信念与标量推论](https://osf.io/sa8ep/) | 元数据已读；无主体数据读取 | 0 | 0 |
| C020 | [复合词形式与意义分解](https://osf.io/vmdwt/) | 元数据已读；无主体数据读取 | 0 | 0 |
| C022 | [二语形态启动元分析](https://osf.io/4stgu/) | 材料/论文/统计输出已读 | 2 | 2 |

## 已读文件与候选的具体依据

### R005 ManyBabies 1（MB1）

作者GitHub固定版本的逐试次注视时长表完整解析：37,264行、16列，另读200行变量字典。OSF子组件未全部枚举；这次验证的是作者正式替代入口。

替代仓库固定版本：[manybabies/mb1-analysis-public · dc3eb5b35780](https://github.com/manybabies/mb1-analysis-public/tree/dc3eb5b3578057096d337203635c0759d2fc04b6)。

- [03_data_trial_main.csv](https://raw.githubusercontent.com/manybabies/mb1-analysis-public/dc3eb5b3578057096d337203635c0759d2fc04b6/processed_data/03_data_trial_main.csv)：完整表：37,264行、16列；4,170,195字节。
  SHA-256：`a4eb8e27ae40833172009e5e681aba3f07eb3cf56d78fddd373d9ee9510110e4`。
- [Variable_Dictionary_mb1.csv](https://raw.githubusercontent.com/manybabies/mb1-analysis-public/dc3eb5b3578057096d337203635c0759d2fc04b6/metadata/Variable_Dictionary_mb1.csv)：完整表：200行、7列；18,507字节。
  SHA-256：`8fdcb82f4dccd877095fd3f50a1f12987432eb5ee5b643a581115aa5b532a9b3`。

后续：主体数据的其余文件、变量内容、缺失值、筛选及研究复现仍需按用途核验。

### R023 English Lexicon Project（ELP）

完整下载命名和词汇判断两份ZIP；目录分别470和820个成员。各解压并按官方变量键解析4个行为日志的6字段试次区段；未解析全部1,290个日志，也未运行2022年补丁。

- [nmg_raw.zip](https://osf.io/download/598st/)：完整下载ZIP，目录470个成员；Data3888.NMG 2530条试次；Data3878.NMG 2530条试次；99DATA.NMG 2530条试次；325DATA.NMG 2530条试次；17,876,152字节。
  SHA-256：`97159329c9318f667e9a917a1755ae2357f6827a83b8f59ca2ba143a9beb43c6`。
- [ldt_raw.zip](https://osf.io/download/eu5ca/)：完整下载ZIP，目录820个成员；169DATA.LDT 3374条试次；Data2140.LDT 3372条试次；Data797.LDT 3374条试次；350DATA.LDT 3374条试次；36,537,458字节。
  SHA-256：`f57f793896d38ccec369f25157685c9879c14c81bed513b7e0a510552614b210`。
- [ELP_Trial_Level_Data_Key.txt](https://osf.io/download/rd632/)：全文解码，1,510字符；没有据此声明表格解析；1,510字节。
  SHA-256：`81343116f673e103f753e351658118b67de8d3f1b054132c4caaf2443c4163c4`。

后续：主体数据的其余文件、变量内容、缺失值、筛选及研究复现仍需按用途核验。

### R024 英语习得年龄常模（Kuperman等及相关扩展）

完整读取两份工作簿：Kuperman常模31,124行、8列；另一份测验型AoA主表43,991行、8列。51,715词扩展表尚未读，两个已读表不能直接当成相同测量。

- [AoA_ratings_Kuperman_et_al_BRM_with_PoS.xlsx](https://osf.io/download/vb9je/)：完整工作簿：Sheet1 31,124行×8列；1,944,944字节。
  SHA-256：`a2a24ad3b0a918c6260f7e8c2949a729968ca68a6508229ac8fceeba21fdd770`。
- [Master file with all values for test based AoA measures Biemiller.xlsx](https://osf.io/download/2s8yx/)：完整工作簿：a 43,991行×8列；2,452,580字节。
  SHA-256：`0b929a3998096782272cc33c7b851a79cbe98fe13dae36293dfcc221b85dff62`。

后续：主体数据的其余文件、变量内容、缺失值、筛选及研究复现仍需按用途核验。

### R025 英语具体性常模（Brysbaert等）

完整读取具体性词项表39,954行、9列，以及R序列化的2,008,857行、14列逐次评分数据。只证明可读取和结构范围；未验收清洗规则、缺失机制或所有文件。

- [Concreteness_ratings_Brysbaert_et_al_BRM.xlsx](https://osf.io/download/8ne54/)：完整工作簿：Sheet1 39,954行×9列；2,281,730字节。
  SHA-256：`1c9d26d0e63c59cf0673c2556b9bded8365981e59445c56c8938eccd29c8ec65`。
- [concreteness_trial.rda](https://osf.io/download/qz9vx/)：R对象已读取：concreteness.participant 2,008,857行×14列；5,683,836字节。
  SHA-256：`7f4da4934c035c14a10a3f5eb95d4d83df7b18955c8f53189561112871b4210c`。

后续：主体数据的其余文件、变量内容、缺失值、筛选及研究复现仍需按用途核验。

### R026 Lancaster Sensorimotor Norms

完整解析39,707词、45列的感知运动常模，并读取2024年更新的试次说明。1GB以上的逐次CSV和59MB试次RDS未下载，本轮常模检查不代表逐次表验收。

- [Lancaster_sensorimotor_norms_for_39707_words.csv](https://osf.io/download/48wsc/)：完整表：39,707行、45列；17,196,336字节。
  SHA-256：`445d363fb1f9f3e50b86d88e2f46cdc9a22b5dd8a713ce4e7be2a773d57f43c5`。
- [README_trial_data_UPDATED.txt](https://osf.io/download/7c9gr/)：全文解码，4,746字符；没有据此声明表格解析；4,746字节。
  SHA-256：`8168ea0c0c7e0804e5127fc14060c45ed4c2f29e3a216b0bb8f820a77ccc6b5b`。

后续：主体数据的其余文件、变量内容、缺失值、筛选及研究复现仍需按用途核验。

### R040 MECO

实际读取最新目录中的主数据说明和4页start_here文档；清单因限流/目录范围而不完整，尚未下载MECO眼动主体数据。文档列出的数据文件不能当作已读文件。

- [00_start_here.pdf](https://osf.io/download/kxqeh/)：PDF已抽取全部4页文本；167,253字节。
  SHA-256：`e3f3a401bd4eeff5c9dc7e050ccca8394c1f5988f8bbcfd727ca1bac5fed14fd`。
- [00_readme primary data.txt](https://osf.io/download/jahw9/)：全文解码，3,789字符；没有据此声明表格解析；3,789字节。
  SHA-256：`6b4b0910a4a682f30d3c52d3d68d66faac31f03cdc2de1761f72105f515a1a16`。

后续：在公开API额度可用或有已授权登录入口时继续定位并读取主体数据。

### R078 Syntactic Ambiguity Processing Benchmark（SAP）

完整读取2025眼动分支的清洗后长表802,271行、17列，以及RDS宽表32,094行、164列。并非2024 SPR分支或全版本验收；模型预测大文件未下载。

- [valid_data_allmeasures_N368.rds](https://osf.io/download/q7yfx/)：R对象已读取：rds_object 32,094行×164列；4,091,259字节。
  SHA-256：`adb5cdca5ba11ec27ee478a6d4459ee5be159cd6b34139e27421782e9006839f`。
- [ET_data_processed.csv](https://osf.io/download/3p98t/)：完整表：802,271行、17列；59,132,745字节。
  SHA-256：`1e6614805ef10aaf51c502fc8026af229b1a226f655126fb6b39b8daa2225873`。

后续：主体数据的其余文件、变量内容、缺失值、筛选及研究复现仍需按用途核验。

### R079 冰岛语主语开头V3结构可接受度

完整读取407行、390列原始宽表，列数一致；行数不自动等于最终有效被试数，筛选、问卷字段和缺失值仍须按分析代码核对。

- [rdata_islensktmal_2023-03-30_14-38.csv](https://osf.io/download/k87ta/)：完整表：407行、390列；224,986字节。
  SHA-256：`ab4d915033f4381c0af776d3982e50dcecf10fe7ce8d07ebc4057ce92a34ae1c`。

后续：主体数据的其余文件、变量内容、缺失值、筛选及研究复现仍需按用途核验。

### R080 Agreement Attraction：语法句判断数据

完整读取eawg5的清洗判断表292,128行、8列，以及pd8ky冻结注册中的预试表2,209行、7列；其他组件仍受限流影响。

- [data_cleaned_judgments.csv](https://osf.io/download/6a8wp/)：完整表：292,128行、8列；47,054,754字节。
  SHA-256：`91773ad16a3e8970936a12ae61dbfcefeecab705c0f84b5721a690ebb48b2abc`。
- [pretests_combined.csv](https://osf.io/download/xs72e/)：完整表：2,209行、7列；249,248字节。
  SHA-256：`3fbe54f948fffac306743fa517bd3db7a4d51f454f24436e9f709b4002180b4d`。

后续：主体数据的其余文件、变量内容、缺失值、筛选及研究复现仍需按用途核验。

### R121 TiNT（荷兰语同步EEG与自定步速阅读）

作者GitHub的cloze.csv完整读取10,454行、6列。README明确这些值由BLOOM-560m生成，属于模型派生资料，不能标成人类完形常模；EEG/SPR主体数据仍未读取。作者另指向Dataverse DOI，API请求返回HTTP200反机器人HTML而非数据JSON。

替代仓库固定版本：[saraoe/natural-stories-dutch · 73e105c095e5](https://github.com/saraoe/natural-stories-dutch/tree/73e105c095e560f60b0b213bb6a8ff1a68b2f8b1)。

- [cloze.csv](https://raw.githubusercontent.com/saraoe/natural-stories-dutch/73e105c095e560f60b0b213bb6a8ff1a68b2f8b1/stimuli/data/cloze.csv)：完整表：10,454行、6列；746,310字节。
  SHA-256：`c01db88ac156f36219b19767ba7ef5d7e09245a822c322e9101c1d07c8a9dcce`。

后续：在公开API额度可用或有已授权登录入口时继续定位并读取主体数据。

### R141 非典型习语语境：人类与LLM判断

完整下载并解析人类—LLM习语评分表：6,720行、8列，大小与同日先前API清单一致。清单地址复用同一聊天提醒阶段的已核实响应，文件已在本轮重新下载取哈希。

- [res_humans_LLMs.csv](https://osf.io/download/ux6rb/)：完整表：6,720行、8列；459,642字节。
  SHA-256：`518f187e8f9091b22acce92cc445630efc144206e0c1b344a2ce8136937ce2ac`。

后续：主体数据的其余文件、变量内容、缺失值、筛选及研究复现仍需按用途核验。

### R142 叙事自由回忆数据集

作者GitHub的LMM_all.xlsx完整读取17,628行、6列，含事件、故事、参与者、中心性和是否回忆。它是分析用行为/派生表，不能据此宣称已读全部自由回忆转写或原始录音。

替代仓库固定版本：[phoebsc/Naturalistic-Free-Recall-Dataset · e1aea1921085](https://github.com/phoebsc/Naturalistic-Free-Recall-Dataset/tree/e1aea19210858b5ce6b32128e8df42b137effb8f)。

- [LMM_all.xlsx](https://raw.githubusercontent.com/phoebsc/Naturalistic-Free-Recall-Dataset/e1aea19210858b5ce6b32128e8df42b137effb8f/LMM_all.xlsx)：完整工作簿：Sheet1 17,628行×6列；491,943字节。
  SHA-256：`c6a551e57fd49d0c3271100e71dd83cc6b21048754f81274e68c74996c3bdfa3`。

后续：主体数据的其余文件、变量内容、缺失值、筛选及研究复现仍需按用途核验。

### R179 Coretta元音时长与辅音清浊研究集合

作者意大利语数据包1.0.1固定版本：测量CSV为3,268行、14列，formants R对象为3,053行、39列。DESCRIPTION标注CC BY 4.0；未据此验收整个多研究OSF集合。

替代仓库固定版本：[stefanocoretta/coretta2018itaegg · ec1b00809244](https://github.com/stefanocoretta/coretta2018itaegg/tree/ec1b00809244eb873f12011c0c06e7460f889947)。

- [measurements.csv](https://raw.githubusercontent.com/stefanocoretta/coretta2018itaegg/ec1b00809244eb873f12011c0c06e7460f889947/data-raw/datasets/measurements.csv)：完整表：3,268行、14列；727,044字节。
  SHA-256：`f7f128c06f69a2c123ed6014f026ea8cf141b2c7d7868a34656465ac5c8706be`。
- [formants.rda](https://raw.githubusercontent.com/stefanocoretta/coretta2018itaegg/ec1b00809244eb873f12011c0c06e7460f889947/data/formants.rda)：R对象已读取：formants 3,053行×39列；215,812字节。
  SHA-256：`7a22ca3aca65586e7655a9d5ae41db21a3dfa75ff5369bcf8946795818a58ea1`。

后续：主体数据的其余文件、变量内容、缺失值、筛选及研究复现仍需按用途核验。

### C002 墨西哥西班牙语岛效应

ma27h实际题名是西英语码转换岛效应；与原审核论文相符的cs5z3为单语西班牙语项目。本轮5个附件均成功下载：两份Qualtrics问卷、两份Word问卷和5工作表刺激/拉丁方安排；未见逐被试判断或评分表。

- [Islands in Spanish - Screening & background part 1 - Qualtrics.qsf](https://osf.io/download/crhfb/)：JSON已完整解析；111,522字节。
  SHA-256：`ed8f250508d4f9411d1c5f639610605b313bb3f91987d48a78008fd68b3b3e47`。
- [Islands in Spanish - Screening & background part 1 - Word.docx](https://osf.io/download/mbjzg/)：Word文档XML已完整解析；30,910字节。
  SHA-256：`67ebcae2751698e3622682ebbe40fcf31ecd110bffb7798c46c3b0d158d0b5c5`。
- [Islands in Spanish - Screening & background part 2 - Qualtrics.qsf](https://osf.io/download/ghab8/)：JSON已完整解析；145,218字节。
  SHA-256：`ccc69cfe7a4356dfa30508c768e7f8211d65a0f0a78bf322625ede7705535669`。
- [Islands in Spanish - Screening & background part 2 - Word.docx](https://osf.io/download/7d4pm/)：Word文档XML已完整解析；33,908字节。
  SHA-256：`19c166a0ea08679370c449823bb5b1a559433c91c7de6e59ad421074e1e8c9f5`。
- [Islands in Spanish - Tokens and Fillers 2022-12-21.xlsx](https://osf.io/download/q26va/)：完整工作簿：Wh-extraction 270行×17列；Sub-extraction 64行×18列；Fillers 54行×2列；Task 1 Lists 2,808行×6列；Task 2 Lists 2,808行×6列；509,276字节。
  SHA-256：`03deb1b43a44d7c5b3bf5a59216a3c85826a7389a67466e91b675c68409d54de`。

后续：原目标继续采用cs5z3；若作者另行发布匿名判断数据再核对。

### C003 中英双语合理性与结构重分析启动

hcdqe为冻结注册，公开文件列表为空。registered_from明确关联vdsey，追查该原项目时返回429。先前论文中的完成实验仍成立，但当前未确认其最终数据包。


后续：额度可用后优先读取vdsey文件清单；不把冻结注册0文件推成原项目没有数据。

### C004 中文把字句二语句法阻断

qehr4的节点与注册API均返回404；短链网页返回200的SPA壳，未得到可用文件内容。本轮未确认正式数据入口；404不据以认定永久删除或私有。


后续：从Hou 2023正式论文或作者最终说明重新确认短编号及数据入口。

### C006 简化关系从句的句法适应

5aynd仅列出一份CUNY2020海报，已完整下载并抽取1页文本。wq2g7是这份海报的文件短编号，已成功下载，不能把它的节点API404解释成失效项目；未见SPR试次数据。

- [CUNY2020P0sterMaloneMauner.pdf](https://osf.io/download/wq2g7/)：PDF已抽取全部1页文本；280,859字节。
  SHA-256：`252072a58316e223af86ba0219148170cfd2e4bd038618e1f13192188813f586`。

后续：继续寻找同一Malone–Mauner研究的阅读时数据；海报结果不替代试次表。

### C007 Acceptability Judgement Tasks and Grammatical Theory

qe865现在公开一份292页博士论文PDF，已完整下载并抽取文本；当前项目文件列表未列出评分、反应时或分析数据。旧网站的历史问题与当前OSF可读论文分别记录。

- [juzek_dphil_thesis_for_dissemination.pdf](https://osf.io/download/hcktp/)：PDF已抽取全部292页文本；4,773,224字节。
  SHA-256：`21317c5a15d3374a96169433523be845d5cb809d518e5e1c2b7dd1da5645a42a`。

后续：寻找该2015论文的独立数据附件或作者正式迁移入口；不以论文PDF或后续SAD数据替代。

### C010 themself/themselves社会句法判断

2s8hm的4个公开PDF均已下载并抽取文本：摘要、海报幻灯、刺激和意识形态/人口学问卷；未见1,127人反应表。5kr8s是可下载的刺激PDF短编号，节点API404不是附件失效。

- [conrod_abstract.pdf](https://osf.io/download/esvhj/)：PDF已抽取全部3页文本；344,748字节。
  SHA-256：`995ead0e2c48d4ef222018c546929782e5b004e624c8ea92bdcba98643aa8f69`。
- [Conrod-Ahn-Schultz-NELS-Poster-slides.pdf](https://osf.io/download/bufq7/)：PDF已抽取全部9页文本；7,989,538字节。
  SHA-256：`47c4b3d9e4d4c014a9a69a06e1ac6adc27f4d0442f3ad841d7625749e88ab3ed`。
- [Themself-Themselves Test Items.pdf](https://osf.io/download/5kr8s/)：PDF已抽取全部2页文本；48,803字节。
  SHA-256：`a790a2b9554e4df5990e8b9c22fbb5e5f371f87b03c45ec8ad6f62be0a7b90b6`。
- [ideology-demographics-questions.pdf](https://osf.io/download/nm6zs/)：PDF已抽取全部2页文本；85,516字节。
  SHA-256：`4f56bb47a2a0ed609ee9f785527c9823c7b4cb7f00a26811860a645586a54783`。

后续：定位同一调查的匿名反应表和变量字典后再考虑晋升。

### C011 双语儿童EEG研究

j5epb冻结EEG预注册的公开文件列表为空；registered_from指向7qk6u，原项目本轮返回429。相关ERP论文的受限声明不自动等于该注册数据的访问规则。


后续：额度可用后检查7qk6u的实际数据和访问条件。

### C012 儿童与照护者协调

9z5qn冻结注册公开文件列表为空；registered_from指向rjdqb，本轮受429限制。既有ECOLANG视频/照护者转写申请限制保留，尚不能确认新增儿童转写是否已开放。


后续：只读复查rjdqb及ECOLANG发布说明；申请数据另按用户授权处理。

### C013 跨语言习语激活

kuqfe是冻结预注册，唯一公开附件为习语材料Word文件，已完整下载并解析文档XML。registered_from指向96ype，本轮429；未确认同一研究的最终反应时/准确率数据。

- [Appendix_idiomatic_meaning.docx](https://osf.io/download/6j4bs/)：Word文档XML已完整解析；185,483字节。
  SHA-256：`17599c36aa1940dfff22fd5822c6034f526eaa1b93fad1bb8126d164d11b58e5`。

后续：额度可用后检查96ype是否已有完成研究数据。

### C016 政治信念与标量推论

sa8ep为标量含意阅读实验的冻结注册，公开文件列表为空；原项目jzu2q本轮429。不同任务的v98dt仍不充作原项目数据。


后续：先查jzu2q最终文件并核实研究身份，保留原任务边界。

### C020 复合词形式与意义分解

vmdwt元数据可读、项目公开并标注CC BY 4.0，但公开存储文件列表与子组件列表均为空。许可声明不能代替眼动数据文件；本轮仍无可下载数据。


后续：等待或寻找作者对这两项复合词阅读实验的正式数据发布。

### C022 二语形态启动元分析

4stgu只有6页Supplemental Materials.pdf和Forest Plot.png，两者已下载，PDF文本和图像像素均可解码。内容是效应量公式、分组汇总和统计比较；未见研究级编码/效应量工作表。

- [Supplemental Materials.pdf](https://osf.io/download/3uvhs/)：PDF已抽取全部6页文本；70,710字节。
  SHA-256：`d01ec7028afda324cde2b70cb4d507b43babcc91b69080a153bff9c474155d5e`。
- [Forest Plot.png](https://osf.io/download/u6zrk/)：图像已解码：3200×5800；611,363字节。
  SHA-256：`4505cdd652a5a5649dc354f1453c307a270d1aed2a34438fd4f22855f5af7713`。

后续：只有补充统计与图形，继续保留候选；若另发布研究级编码表再晋升。

## 如何继续

优先补查60条尚无本轮文件读取的主目录入口，以及C003、C011、C012、C013、C016关联的vdsey、7qk6u、rjdqb、96ype、jzu2q。API额度可用后，复用缓存、检查剩余文件与子组件；若使用登录流程，由用户自行登录。无需把密码或令牌写进目录。

本地缓存应放在仓库外。程序只产生待人工判定的文件证据，不能自动认定刺激为观测数据，也不会自动晋升候选。示例：

```sh
python3 scripts/audit_osf.py inventory --cache /path/outside/repository/osf-cache --workers 2
python3 scripts/audit_osf.py download --cache /path/outside/repository/osf-cache --ids R079
```

标准库和curl支持清单与文本检查；工作簿需openpyxl，旧Excel/部分统计格式需pandas及对应读取库，R序列化需R和jsonlite，PDF需pypdf，图像需Pillow。默认对当前缓存统计最近一小时的API请求，90次或观察到429后停止新增元数据请求，给日常访问留余量。换缓存不会扩大服务额度。
