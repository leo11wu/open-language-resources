# 更新资源

1. 编辑 `data/resources.json`；为新条目分配未使用的稳定编号。原R编号不重排；主分类改变不更改编号。
2. 优先核对项目方、作者仓库或正式发布版本，保留获取条件、测量边界和许可说明。
3. 核实说明页后才更新核对日期。完成文件下载与数据验证后，才更新对应验收字段。
4. 运行 `python3 scripts/build.py`，更新首页、分类目录和JSONL。
5. 运行 `python3 scripts/validate.py` 和 `python3 scripts/build.py --check`。

NoRaRe来源记录编辑 `data/source-indexes/norare.json`；未确认发布的数据线索编辑 `data/discovery-candidates.json`。两组不计入主目录数量。维护来源索引时记录上游固定版本和署名；不能因聚合库中有一行元数据就把原始文件标为已验收。

按同源项目去重：OSF母项目、raw/processed/analysis组件和冻结副本通常属于同一资源。只有可明确说明新增采集或不同测量价值时才单列，并保留关联及使用边界。切勿把匿名审稿或其他访问令牌写入目录。

更改语种标签或访问类型时，同时检查 `docs/data-dictionary.md` 和JSON Schema。对于失效链接，先寻找项目方的正式替代入口，再保留来源关系。不要仅因一次抓取失败就认定资源已经消失。

本目录的主题是可用资源与其证据边界。论文推荐、研究设想或模型生成材料如需加入，应清楚标注其性质，不能写成已有数据或发现。
