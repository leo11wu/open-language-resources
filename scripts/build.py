#!/usr/bin/env python3
"""Generate browsable documentation and JSONL from the canonical catalog."""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def md(value):
    return str(value).replace('|', '\\|').replace('\n', ' ')


def generated_files(catalog):
    resources = catalog['resources']
    labels = {c['id']: c['label'] for c in catalog['categories']}
    modes = catalog['access_modes']
    counts = Counter(r['category'] for r in resources)
    header = [
        '# 公开语言资源目录\n\n',
        '用于寻找儿童语言、社会互动、词汇认知、中文与二语、跨语言比较、手语、成语及历时研究资料。',
        '按研究对象和现象浏览分类，再核对每条资源的测量内容、获取条件与使用边界。\n\n',
        f"当前收录 **{len(resources)}个资源入口、{len(labels)}类**。目录更新：**{catalog['updated_on']}**。\n\n",
        '## 按主题浏览\n\n',
        '| 分类 | 条目数 | 分类目录 |\n| --- | ---: | --- |\n',
    ]
    for category in catalog['categories']:
        key, label = category['id'], category['label']
        header.append(f'| {label} | {counts[key]} | [查看资源](catalog/{key}.md) |\n')
    header.extend([
        '\n## 数据文件\n\n',
        '- [JSON主目录](data/resources.json)：唯一编辑来源，包含元数据、分类定义和完整条目。\n',
        '- [JSONL逐条数据](data/resources.jsonl)：每行一个资源，便于导入分析工具。\n',
        '- [字段说明](docs/data-dictionary.md)：访问类型、语种标签和核对状态。\n',
        '- [JSON Schema](schema/resources.schema.json)：结构与字段约束。\n',
        '- [收录范围与证据边界](docs/scope.md)：来源、测量和同源数据问题。\n\n',
        '入口包括公开数据、免费注册、申请取得与部分开放资料。',
        '“公开数据入口”不等于无限制使用；具体条件保留在每条资源中。',
        '核对日期对应说明页，初始版本未批量下载及验收全部原始文件。\n\n',
        '## 全部资源速览\n\n',
        '| 编号 | 资源 | 分类 | 获取方式 |\n| --- | --- | --- | --- |\n',
    ])
    for r in resources:
        detail = f"catalog/{r['category']}.md#{r['id'].lower()}"
        header.append(f"| {r['id']} | [{md(r['name'])}]({detail}) | {labels[r['category']]} | {md(r['access_notes'])} |\n")
    header.extend([
        '\n## 本地筛选\n\n',
        '无需安装第三方依赖，使用Python 3即可按关键词、分类、语种或获取方式筛选：\n\n',
        '```sh\npython3 scripts/query.py 儿童\npython3 scripts/query.py --category social-interaction\n',
        'python3 scripts/query.py --lang zh\npython3 scripts/query.py --tag 词频 --access open_data\n',
        'python3 scripts/query.py 手语 --format json\n```\n\n',
        '语种标签用于发现资源，不是每个项目的完整语种清单。',
        '例如，多语种项目需要继续检查所选发布版本是否包含目标语言。\n\n',
        '## 更新目录\n\n',
        '编辑 `data/resources.json` 后，运行：\n\n',
        '```sh\npython3 scripts/build.py\npython3 scripts/validate.py\npython3 scripts/build.py --check\n```\n\n',
        '更新方式见 [CONTRIBUTING.md](CONTRIBUTING.md)。',
        '分类页和JSONL由主目录生成，避免多份清单各自漂移。\n',
    ])
    files = {'README.md': ''.join(header)}
    files['data/resources.jsonl'] = ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in resources)
    role_labels = {'dataset':'数据集','collection':'资源集合','aggregate':'整合资料','alignment':'对齐资源','derived':'派生资料'}
    for category in catalog['categories']:
        key, label = category['id'], category['label']
        subset = [r for r in resources if r['category'] == key]
        lines = [f'# {label}\n\n', '[返回首页](../README.md) · [数据字段](../docs/data-dictionary.md)\n\n',
                 f'共{len(subset)}个资源入口。访问条件与核对日期保留在具体条目中。\n\n']
        for r in subset:
            lines += [f"<a id=\"{r['id'].lower()}\"></a>\n\n",f"## {r['name']}\n\n",
                f"**{r['id']}** · {role_labels[r['entry_type']]} · {modes[r['access_mode']]}\n\n",
                f"{r['description']}\n\n",'| 字段 | 内容 |\n| --- | --- |\n',
                f"| 语言与人群 | {md(r['language_scope'])} |\n",
                f"| 数据性质 | {md(r['data_type'])} |\n",
                f"| 获取条件 | {md(r['access_notes'])} |\n",
                f"| 许可说明 | {md(r['license_note'])} |\n",
                f"| 适用边界 | {md(r['limitations'])} |\n",
                f"| 查找标签 | {md('、'.join(r['tags']))} |\n",
                f"| 说明页核对 | {r['verification']['documentation_checked_on']} |\n",
                f"\n[项目或数据入口]({r['source_url']})\n"]
            if r['additional_urls']:
                lines.append('\n补充入口：\n\n')
                for i,url in enumerate(r['additional_urls'],1):
                    lines.append(f'- [补充来源 {i}]({url})\n')
            if r['related_ids']:
                lines.append('\n关联资源：' + '、'.join(f'[{rid}](../README.md#全部资源速览)' for rid in r['related_ids']) + '。\n')
            lines.append('\n')
        files[f'catalog/{key}.md'] = ''.join(lines)
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true',help='Verify generated files without writing')
    args = parser.parse_args()
    catalog = json.loads((ROOT/'data/resources.json').read_text(encoding='utf-8'))
    outputs = generated_files(catalog)
    stale = []
    for relative,content in outputs.items():
        path = ROOT/relative
        if args.check:
            if not path.exists() or path.read_text(encoding='utf-8') != content:
                stale.append(relative)
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(content,encoding='utf-8')
    if stale:
        print('Generated files need updating: '+', '.join(stale),file=sys.stderr)
        return 1
    print(('Checked' if args.check else 'Generated')+f' {len(outputs)} files from {len(catalog["resources"])} resources.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
