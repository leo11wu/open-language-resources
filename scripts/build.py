#!/usr/bin/env python3
"""Generate the browsable resource directory and discovery indexes from JSON."""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
ROLE={'dataset':'数据集','collection':'资源集合','aggregate':'整合资料','alignment':'对齐资料','derived':'派生资料'}
STATUS={'released_data':'有数据发布说明','described_resource':'已描述资源，文件范围待核对','materials_only':'已确认材料/代码','discovery_portal':'发现入口'}
ORIGIN={'human_observations':'人类行为或生理观测','human_norms':'人工常模或词项汇总','corpus_annotation':'语料与标注','synthetic_stimuli':'规则或模板生成刺激','derived_data':'计算派生或再分析','mixed_or_unspecified':'混合来源或待细分','materials_only':'材料与代码','discovery_portal':'索引或平台'}
EVIDENCE={'documentation_reviewed':'沿用首版文档核对','project_documentation':'项目说明','publisher_data_statement':'出版方/机构数据声明','publisher_resource_description':'出版方资源描述','repository_documentation':'作者仓库说明','indexed_project_wiki':'项目Wiki的索引内容'}

def md(x): return str(x).replace('|','\\|').replace('\n',' ')
def link(r,prefix=''): return f"{prefix}catalog/{r['category']}.md#{r['id'].lower()}"

def generated_files(c):
    resources=c['resources']; labels={x['id']:x['label'] for x in c['categories']}
    counts=Counter(r['category'] for r in resources)
    osf=[r for r in resources if 'osf' in r['platforms']]
    source=json.loads((ROOT/'data/source-indexes/norare.json').read_text())
    candidates=json.loads((ROOT/'data/discovery-candidates.json').read_text())
    lines=['# 公开语言资源目录\n\n',
        '用于按语言现象寻找可复用数据：儿童语言、社会互动、词汇常模、中文与双语、句法、形态、语音、眼动与神经语言。\n\n',
        f"主目录 **{len(resources)}个资源入口、{len(labels)}类**，其中 **{len(osf)}条关联OSF**；[句法专类](catalog/syntax.md)有 **{counts['syntax']}条**。更新：**{c['updated_on']}**。\n\n",
        f"另附 [NoRaRe的{source['record_count']}条具体来源记录](catalog/norare-source-index.md)和 [待核对的{candidates['candidate_count']}条线索](catalog/discovery-candidates.md)。来源记录可能重命名、共享数据或与主目录重叠，**这些数字不相加为独立数据集总数**。\n\n",
        '## 快速入口\n\n',
        '- [OSF语言资源索引](catalog/osf.md)：按主题浏览，并查看数据发布依据。\n',
        '- [句法专类](catalog/syntax.md) · [按句法问题选资料](docs/syntax-guide.md)。\n',
        '- [NoRaRe具体来源](catalog/norare-source-index.md)：按语种和测量指标继续找常模。\n',
        '- [检索范围、遗漏与核对边界](docs/search-method.md) · [本次扩充记录](docs/changelog.md)。\n\n',
        'OSF接口本次返回维护通知，因此本目录核对的是项目说明、作者仓库、Wiki索引或出版方数据声明；没有完成全库抓取或所有原始文件的下载验收。逐条核对范围保留在元数据中。\n\n',
        '## 按主题浏览\n\n| 分类 | 条目数 | 入口 |\n| --- | ---: | --- |\n']
    for x in c['categories']: lines.append(f"| {x['label']} | {counts[x['id']]} | [查看](catalog/{x['id']}.md) |\n")
    lines+=['\n## 数据与证据\n\n',
        '- [JSON主目录](data/resources.json) · [JSONL逐条资料](data/resources.jsonl)。\n',
        '- [NoRaRe来源元数据](data/source-indexes/norare.json) · [待核对线索](data/discovery-candidates.json) · [平台访问记录](data/platform-observations.json)。\n',
        '- [字段与核对类型](docs/data-dictionary.md) · [JSON Schema](schema/resources.schema.json) · [收录范围](docs/scope.md)。\n\n',
        '“有数据发布说明”表示来源说明提供数据，不表示本目录已验证文件可解析、变量无误或分析可复现。',
        '公开、注册、申请和混合访问分别标明；各原始数据的许可保持独立。\n\n',
        '## 全部资源速览\n\n| 编号 | 资源 | 分类 | 资料状态 |\n| --- | --- | --- | --- |\n']
    for r in resources: lines.append(f"| {r['id']} | [{md(r['name'])}]({link(r)}) | {labels[r['category']]} | {STATUS[r['data_status']]} |\n")
    lines+=['\n## 本地筛选\n\n无需第三方依赖，使用Python 3：\n\n```sh\n',
        'python3 scripts/query.py --category syntax\npython3 scripts/query.py --platform osf\n',
        'python3 scripts/query.py --platform osf --category syntax\npython3 scripts/query.py --lang zh\n',
        'python3 scripts/query.py --tag 结构启动\npython3 scripts/query.py --index norare 习得年龄\n',
        'python3 scripts/query.py --index norare --lang zh\npython3 scripts/query.py --index candidates --category syntax\n',
        'python3 scripts/query.py --origin human_norms --format json\n```\n\n',
        '## 更新\n\n主目录编辑 `data/resources.json`，来源索引和待核对清单分别编辑其JSON；不要直接修改生成的分类页。\n\n',
        '```sh\npython3 scripts/build.py\npython3 scripts/validate.py\npython3 scripts/build.py --check\n```\n\n',
        '方法见 [CONTRIBUTING.md](CONTRIBUTING.md)。原有R001–R060编号保留；UD移入句法专类。\n']
    files={'README.md':''.join(lines),'data/resources.jsonl':''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in resources)}
    lookup={r['id']:r for r in resources}
    for x in c['categories']:
        subset=[r for r in resources if r['category']==x['id']]
        out=[f"# {x['label']}\n\n",'[首页](../README.md) · [OSF索引](osf.md) · [字段说明](../docs/data-dictionary.md)\n\n',f'共{len(subset)}个入口。资料状态与文件验收范围分别记录。\n\n']
        for r in subset:
            v=r['verification']
            out += [f'<a id="{r["id"].lower()}"></a>\n\n',f"## {r['name']}\n\n",f"**{r['id']}** · {ROLE[r['entry_type']]} · {STATUS[r['data_status']]}\n\n",f"{r['description']}\n\n",'| 字段 | 内容 |\n| --- | --- |\n',
                f"| 语言与人群 | {md(r['language_scope'])} |\n",f"| 数据性质 | {md(r['data_type'])}；{ORIGIN[r['data_origin']]} |\n",f"| 获取方式 | {md(c['access_modes'][r['access_mode']])}：{md(r['access_notes'])} |\n",f"| 许可 | {md(r['license_note'])} |\n",f"| 使用边界 | {md(r['limitations'])} |\n",f"| 标签 | {md('、'.join(r['tags']))} |\n",f"| 平台 | {', '.join(r['platforms'])} |\n",f"| 核对依据 | {EVIDENCE[v['evidence_type']]}；{v['documentation_checked_on']} |\n",f"| 核对范围 | {md(v['note'])} |\n",f"\n[项目或数据入口]({r['source_url']})\n"]
            extras=list(dict.fromkeys([*r['additional_urls'],*v['evidence_urls']]))
            extras=[u for u in extras if u!=r['source_url']]
            if extras:
                out.append('\n补充及核对来源：\n\n')
                out += [f'- [来源 {i}]({u})\n' for i,u in enumerate(extras,1)]
            if r['related_ids']:
                out.append('\n关联：'+'、'.join(f"[{rid} {lookup[rid]['name']}]({link(lookup[rid],'../')})" for rid in r['related_ids'])+'。\n')
            out.append('\n')
        files[f"catalog/{x['id']}.md"]=''.join(out)
    out=['# OSF语言资源索引\n\n','[首页](../README.md) · [句法](syntax.md) · [待核对线索](discovery-candidates.md)\n\n',f'主目录中{len(osf)}条资源关联OSF项目或其正式替代入口。项目、组件与冻结版本尽量按同一数据家族归并。\n\n','2026-10-17：OSF API返回维护通知。本表保留项目说明、出版方数据声明、作者仓库或Wiki索引等发布依据；未取得所有项目的实时文件清单。\n\n']
    for x in c['categories']:
        subset=[r for r in osf if r['category']==x['id']]
        if not subset: continue
        out+=[f"## {x['label']}\n\n",'| 编号 | 资源 | OSF编号 | 依据 | 资料状态 |\n| --- | --- | --- | --- | --- |\n']
        for r in subset: out.append(f"| {r['id']} | [{md(r['name'])}]({link(r,'../')}) | {', '.join(r['osf_ids'])} | {EVIDENCE[r['verification']['evidence_type']]} | {STATUS[r['data_status']]} |\n")
        out.append('\n')
    files['catalog/osf.md']=''.join(out)
    out=['# NoRaRe具体数据集来源索引\n\n','[首页](../README.md) · [结构化来源数据](../data/source-indexes/norare.json)\n\n',f"共{source['record_count']}条历年来源记录；当前源库元数据{source['current_source_metadata_count']}条，较早CLDF快照{source['cldf_snapshot_count']}条。",'这不是独立数据集的去重计数，不能与主目录数量相加。旧标识可能重命名或拆分，原始论文也可能产生多个语言或测量子表。\n\n',
        '本索引核对的是官方元数据，未逐一检查182项原始文件。NoRaRe中的Concepticon对齐子集可能少于原始数据的全部词项、被试或变量。来源记录保留原始描述、语种、测量、版本与对应主目录编号，便于继续检索。\n\n',
        f"来源：[当前源库固定快照](https://github.com/concepticon/norare-data/blob/{source['provenance']['source_commit']}/datasets.tsv)、[CLDF固定快照](https://github.com/concepticon/norare-cldf/blob/{source['provenance']['cldf_commit']}/cldf/datasets.csv)。\n\n",'| 来源编号 | 语言 | 测量或主题 | 快照 | 主目录关联 |\n| --- | --- | --- | --- | --- |\n']
    for r in source['records']:
        target=r['original_url'] or r['dataset_folder_url'] or r['source_metadata_url']
        lang='、'.join(r['language_scope'][:4])+('等' if len(r['language_scope'])>4 else '')
        measures='、'.join(r['search_tags'][:8]) or '见原始描述'
        state='当前+旧版' if len(r['found_in'])==2 else ('当前源库' if 'source_metadata_2026' in r['found_in'] else '旧版CLDF')
        related='、'.join(f"[{rid}]({link(lookup[rid],'../')})" for rid in r['related_main_ids'])
        out.append(f"| [{md(r['source_id'])}]({target}) | {md(lang)} | {md(measures)} | {state} | {related} |\n")
    out+=['\n## 来源与署名\n\n',source['provenance']['citation']+'\n\n',
        '元数据经重新组织：当前[norare-data源库许可](https://github.com/concepticon/norare-data/blob/4b8901d6fa3d6cc14afbde6bf2fb061d4a4ab2c4/LICENSE)为[CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/)，较早[norare-cldf快照许可](https://github.com/concepticon/norare-cldf/blob/895b055b9e5dd339bbd2b67509802d85aea72126/LICENSE)为[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。两者分别保留；合并索引不能统一视为允许商业使用。本目录的组织与标签不代表NoRaRe作者背书，各原始资源许可另行核对。\n']
    files['catalog/norare-source-index.md']=''.join(out)
    reason={'preregistration_only':'仅确认注册计划','release_unconfirmed':'数据发布范围待确认','insufficient_description':'公开说明不足','platform_unavailable':'平台访问不足','collection_needs_expansion':'研究集合待细分'}
    out=['# 待核对语言资源线索\n\n','[首页](../README.md) · [OSF已收录入口](osf.md)\n\n','这些线索保留以减少遗漏，但没有作为已验证可下载数据加入主目录。未来应优先查找最终数据包、正式数据声明与许可。\n\n','| 编号 | 项目 | 方向 | 当前依据 | 需要补齐 |\n| --- | --- | --- | --- | --- |\n']
    for r in candidates['candidates']: out.append(f"| {r['id']} | [{md(r['name'])}]({r['source_url']}) | {labels[r['category']]} | {reason[r['status']]} | {md(r['reason'])} |\n")
    files['catalog/discovery-candidates.md']=''.join(out)
    return files

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');a=p.parse_args()
    c=json.loads((ROOT/'data/resources.json').read_text()); files=generated_files(c); stale=[]
    for name,text in files.items():
        f=ROOT/name
        if a.check:
            if not f.exists() or f.read_text()!=text: stale.append(name)
        else: f.parent.mkdir(parents=True,exist_ok=True);f.write_text(text,encoding='utf-8')
    if stale: print('Generated files need updating: '+', '.join(stale),file=sys.stderr);return 1
    print(('Checked' if a.check else 'Generated')+f' {len(files)} files from {len(c["resources"])} main entries.');return 0

if __name__=='__main__': raise SystemExit(main())
