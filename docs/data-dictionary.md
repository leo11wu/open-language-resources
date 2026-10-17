# 字段、访问与核对范围

`data/resources.json` 是主目录编辑来源；分类页、README和JSONL由 `scripts/build.py` 生成。NoRaRe来源索引和待核对线索分别保存，互不冒充已验收的原始数据。

| 字段 | 含义 |
| --- | --- |
| `id` | 稳定R编号；R001–R060沿用首版 |
| `name` / `category` | 名称及主分类；跨主题关系另用标签表达 |
| `entry_type` | dataset数据集、collection集合、aggregate整合、alignment对齐、derived派生 |
| `language_scope` | 人可读的语种、文字与人群说明 |
| `language_codes` | 辅助检索语种标签；不是完整语言清单，`mul`表示多语种或需继续细分 |
| `data_type` / `description` | 测量、资料组织及所含内容 |
| `data_origin` | 人类观测、人工常模、语料标注、生成刺激、计算派生、混合、材料或发现入口 |
| `data_status` | 见下表；不能直接等同文件验收状态 |
| `access_mode` / `access_notes` | 开放、免费注册、申请、混合或需进一步核对许可，以及具体条件 |
| `license_note` | 原始数据许可；未明确时不推定开放授权 |
| `limitations` | 测量、抽样、同源或分析边界 |
| `source_url` / `additional_urls` | 主要入口及补充链接；原始资源有迁移时保留来源关系 |
| `tags` / `related_ids` | 主题标签及关联R编号；关联不意味着独立样本或可以直接合并 |
| `platforms` | OSF、GitHub等可用托管或关联平台；不等于完整文件清单 |
| `osf_ids` | 已确认关联的项目/组件编号；不枚举项目下所有文件或冻结副本 |
| `verification` | 文档核对日期、依据、来源URL和文件验收状态 |

## 资料状态

| 值 | 解释 |
| --- | --- |
| `released_data` | 来源说明提供数据；本目录未因此声称已下载并解析全部文件 |
| `described_resource` | 项目或论文明确描述该资源，但本次未确认完整原始文件发布范围 |
| `materials_only` | 已确认刺激、协议或代码；没有据此假定原始被试数据也开放 |
| `discovery_portal` | 继续寻找具体资源的平台，不是单一可直接分析数据集 |

## 访问类别

| 值 | 解释 |
| --- | --- |
| `open_data` | 项目或出版方说明有公开数据入口；用途仍受原许可约束 |
| `free_registration` | 通常免费，但需注册、登录或接受协议 |
| `application_required` | 需研究者/机构授权或申请 |
| `mixed_access` | 不同子库、转写、媒体或层级的条件不同 |
| `license_review` | 已定位资源，但许可、文件范围或访问条件仍待进一步核对 |

## 文档核对类型

| `verification.evidence_type` | 核对到的内容 |
| --- | --- |
| `documentation_reviewed` | 首版沿用的项目与访问文档核对 |
| `project_documentation` | 项目说明或Wiki；可能由搜索索引提取，不能推定实时文件列表 |
| `publisher_data_statement` | 正式论文或机构门户的数据发布声明 |
| `publisher_resource_description` | 正式出版方对数据库的描述；低于实际文件验收 |
| `repository_documentation` | 作者仓库中的README或发布说明 |
| `indexed_project_wiki` | 项目Wiki的可检索索引内容；OSF本次维护限制了实时文件核对 |

`documentation_checked_on` 是说明核对日期。多数条目仍只核对文档，两个文件验收标志均为 `false`。候选复核中，R175完整读取并解析了一份30行15列的小CSV，故其 `download_tested=true`；这只对应选定文件，`data_files_validated` 仍为 `false`，不代表全部模拟对话、标注和分析均已验收。

当 `scope=resource_documentation_and_selected_file_checks` 时，核对包含选定文件读取。可选的 `file_checks` 逐项保留文件URL、读取范围、结果和Git blob标识；`first_8_lines`、`first_4_lines` 是头部样例，`complete_small_csv` 是完整的小CSV。头部样例或一次成功读取均不足以证明全部数据可解析、内容准确或分析可复现。

## NoRaRe来源索引

`data/source-indexes/norare.json` 记录182条历年来源标识。当前源库125条、较早CLDF快照126条，共享标识合并；但重命名、拆分与原始数据同源并未全部人工裁定，所以182不能解释为182个独立样本或项目。

每条保留 `source_id`、原始URL、上游描述、语言、测量、变量数、固定源版本、主目录关联和可能的后继标识。`variable_count_in_cldf_snapshot` 只是该旧快照中的变量定义数，不是词项数、被试数或原始数据列总数。旧版记录未出现在当前元数据表，不足以证明数据已失效。

`metadata_license` 分别保留上游许可：当前norare-data为CC BY-NC 4.0，较早norare-cldf为CC BY 4.0；不能将合并索引统一标成可商用。具体原始数据的许可另行核对。

`evidence_type=source_catalog_metadata`、`original_files_checked=false` 表示只核对来源库元数据。主观习得年龄常模、儿童纵向词汇数据与算法推断的习得指标有不同测量含义。

## 待核对线索

`data/discovery-candidates.json` 中的C编号不进入主目录数量。原22条复核后，已确认公开数据的10条转入R170–R179；剩余12条保留具体状态、证据URL和下一步需确认事项。完整映射和历史状态保存在 `data/candidate-audit-2026-10-17.json`，避免晋升后丢失来源。

`materials_only` 表示当前只确认材料或统计输出，`access_restricted` 表示须申请，`obsolete_link` 表示旧入口已更换内容；其余记录仍可能有未找到的数据。冻结注册若明确包含完成数据，可以进入主目录；不能仅按注册标签机械排除。已经完成实验但缺少公开数据证据的项目，也不再简单写成“只有计划”。

## 文件核验台账与待办

`data/verification-queue.json` 与 `catalog/verification-status.md` 从已有记录自动生成。生成时间只表示整理日期，不刷新资源的说明核对日期，也不构成新的下载或文件验收。

`check_state` 是派生字段：`documentation_only` 仅核对说明，`file_preview` 已读头部样例，`selected_file_checked` 已完整读取选定文件但全库未验收，`fully_validated` 表示资源文件已验收。`discovery_portal` 单列发现入口，不当作有待下载的数据集。查询可使用 `--check-state`，并与平台、主题和语言筛选组合。

结构化清单的 `main_resources` 覆盖全部R编号；`remaining_candidates` 保留未纳入候选的具体问题；`norare_sources` 保留全部来源记录及原始入口。后两组与主目录可能重叠，不相加计数。`next_steps` 是后续任务，不是已经完成的操作。

平台维护信息保存在 `data/platform-observations.json`。`evidence_type=user_supplied_official_notice` 明确表示官网通知正文由用户提供，`notice_firsthand_checked=false` 表示本次未独立取得实时正文；计划恢复时间与实际恢复结果分开记录。
