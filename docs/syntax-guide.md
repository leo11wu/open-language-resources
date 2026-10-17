# 按句法问题找资料

[首页](../README.md) · [句法全部条目](../catalog/syntax.md) · [OSF](../catalog/osf.md)

| 想研究的现象或问题 | 优先查找 | 需要先区分 |
| --- | --- | --- |
| 儿童接触怎样的句法结构 | UD-English-CHILDES、CHILDES Treebank、CHILDES | 儿童产出与儿童导向输入；成分树与依存树；gold与silver标注 |
| 中文语法判断与人类—模型差异 | CoLAC、CLiMP、SLING、ZhoBLiMP | 人类连续评分、众包二元标签与模板最小对立 |
| 不同语言的可接受度 | CoLA、JCoLA、JBLiMP、RuCoLA、KBLiMP、MELA | 语言之间的任务与现象是否可比；集合之间是否共用材料 |
| 岛效应与长距离依存 | 西班牙语岛效应、英法主语抽取实验、中文嵌入wh实验 | 结构、话语功能、任务速度、依存距离与记忆负荷 |
| 主谓一致与记忆干扰 | Agreement Attraction、Hierarchical Structure、mbtcd；Marvin–Linzen、Colorless Green RNNs | 人类反应与生成刺激；有语法句与无语法句；吸引与干扰的操作化 |
| 花园路径与重分析 | SAP Benchmark、Natural Stories、捷克语开放式问题 | 在线阅读时间、眼动和事后理解反应是不同证据 |
| 结构启动与产生 | 矩阵动词PO/DO实验、Wordform Boost、英荷双及物抽样 | 词项重复、句法中心词、语义重叠与抽象结构启动 |
| 早期语法与依存学习 | 18月龄婴儿非局部依存、儿童非相邻依存材料、儿童树库 | 实验刺激可用不等于全部ERP原始数据开放；婴儿测量不同于成人判断 |
| 二语语法与年龄 | Hartshorne语法年龄数据、形态启动、英意语言磨蚀 | 横断面经历与因果年龄效应；语法能力、词汇量和熟练度 |
| 句法加工与神经信号 | TiNT、ZuCo、LPP、SMN4Lang、Alice | 是否同被试同步采集；词项时间对齐与句法标注层级 |

上表名称均可在[主目录JSON](../data/resources.json)或本地查询中检索。阅读、神经和形态资源保留在各自专类；用“句法”标签和关键词跨类查找，可补足只浏览句法专类遗漏的资料。

```sh
python3 scripts/query.py --category syntax
python3 scripts/query.py --platform osf --category syntax
python3 scripts/query.py --tag 句法
python3 scripts/query.py 一致
python3 scripts/query.py --lang zh --category syntax
python3 scripts/query.py --index candidates --category syntax
```

树库测量结构分布，判断实验测量特定任务下的反应，最小对立基准测量预设现象上的区分能力。三类资料可以相互约束，但不能直接替代彼此。模型基准的同一套模板、同一源文献和同一母语料需要保留来源分组。
