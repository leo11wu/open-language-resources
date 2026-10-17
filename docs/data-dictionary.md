# 数据字段与访问类型

`data/resources.json` 是目录的唯一编辑来源。`data/resources.jsonl`、首页与分类目录由 `scripts/build.py` 生成。

| 字段 | 含义 |
| --- | --- |
| `id` | 稳定条目编号；新增时使用未分配编号，不因排序变化重编号 |
| `name` | 项目或数据发布名称 |
| `category` | 主分类；八类定义位于根对象的 `categories` |
| `entry_type` | 数据集、集合、整合、对齐或派生资源 |
| `language_scope` | 人可读的语种、文字系统或人群说明 |
| `language_codes` | 检索用语种标签，并非完整语种覆盖清单；`mul` 表示多语种，`sgn` 表示手语集合 |
| `data_type` | 资料的测量与组织形式 |
| `description` | 主要包含的数据内容 |
| `access_mode` | 访问类别，见下表 |
| `access_notes` | 具体获取条件，包括注册、申请和许可用途 |
| `license_note` | 已知许可说明；未确认时明确回到源站，不推定统一开放许可 |
| `limitations` | 影响解释、合并或使用的测量和抽样边界 |
| `source_url` | 项目方、作者仓库或正式发布页面 |
| `additional_urls` | 获取条件、相关接口或补充资料链接 |
| `tags` | 中文主题标签 |
| `related_ids` | 便于导航的关联条目；不代表独立样本或可直接合并 |
| `verification` | 说明核对日期和验收范围 |

## 访问类型

| 值 | 含义 |
| --- | --- |
| `open_data` | 来源说明有公开数据入口；用途仍受原许可约束 |
| `free_registration` | 通常免费，但需要账号、密码或接受使用协议 |
| `application_required` | 需要研究者或机构申请；不是直接下载 |
| `mixed_access` | 转写、媒体或不同子库的开放层级不同 |
| `license_review` | 数据可在公开仓库看到，但明确使用或再分发许可仍需核对 |

## 核对状态

`documentation_checked_on` 是资料说明与获取条件的核对日期，不是原始文件测试日期。

初始版本的 `download_tested` 与 `data_files_validated` 均为 `false`：未批量下载及检验全部原始数据。以后只有实际完成对应检查，才更新这两个字段；网页正常显示不能代替原始数据验收。

## 检索标签

常用语种标签：`en` 英语、`zh` 中文、`zh-Hans` 简体中文、`zh-Hant` 繁体中文、`cmn` 普通话、`yue` 粤语、`ase` 美国手语、`gsg` 德国手语、`nl` 荷兰语、`de` 德语、`it` 意大利语、`cs` 捷克语、`es` 西班牙语、`fr` 法语。

标签仅辅助发现资源。确切语言列表、语言背景和发布覆盖应按 `language_scope` 和对应数据版本核实。
