"""Render bounded follow-up evidence while preserving earlier audit snapshots."""


LABELS = {
    'empirical_data_readable': '已完整读取代表性数据文件',
    'auxiliary_only_readable': '仅辅助资料已读',
    'materials_only_readable': '仅材料或代码已读',
    'partial_data_readable': '数据样例已读；未完整下载',
    'download_unavailable': '已定位文件；本次下载失败',
    'empty_storage_in_checked_scope': '所查文件区未找到可下载数据',
    'source_gone': '当前入口410或跳转；替代数据未确认',
    'restricted_access': '登录后仍需项目授权',
}


def md(value):
    return str(value).replace('|', '\\|').replace('\n', ' ')


def brief(audit, prefix=''):
    s=audit['summary']
    return (f"{audit['checked_on']}续查固定的60条主目录入口和5个候选原项目："
        f"{s['main_with_readable_data']}条主目录资源读到完整代表性数据，"
        f"{s['main_with_partial_data_only']}条仅数据样例，"
        f"{s['main_with_only_supporting_reads']}条仅辅助材料；"
        f"{s['main_without_readable_selected_files']}条本次未取得可读文件。"
        f"候选新增晋升{s['newly_promoted_candidates']}条。"
        f"[逐项证据与下载失败]({prefix}osf-file-audit-{audit['checked_on']}.md)。"
        "全部为有界访问与选定文件核查，全资源验收仍为0。")


def page(audit):
    s=audit['summary'];date=audit['checked_on']
    out=[f'# OSF续查：60条资源与5个候选原项目 · {date}\n\n',
        '[首页](../README.md) · [总核验台账](verification-status.md) · ',
        f'[结构化记录](../data/osf-file-audit-{date}.json) · ',
        '[10月19日历史快照](osf-file-audit-2026-10-19.md)\n\n',
        brief(audit)+'\n\n',
        f"本次完整下载{s['complete_downloads']}个选定文件，实际读入{s['readable_complete_files']}个；"
        f"另外保留{s['partial_file_reads']}个文件的有界样例。"
        '下载量、ZIP成员、所读表格和独立数据集是不同计数单位。未完整读取的文件不会记为完整文件检查。\n\n',
        '## 访问与内容判断\n\n',
        '- 用户完成OSF登录后，通过正常网页访问追查子组件和文件夹；未提取或保存登录凭据。公开接口请求保留预算和缓存，不通过更换身份或地址规避限额。\n',
        '- 页面、文件清单、实际下载和文件解析分别记录。部分地区存储域名无法解析或连接超时；不能因此推断项目私有，也不能把页面恢复写成全部文件恢复。\n',
        '- CSV和工作簿核对结构，R/SPSS对象只反序列化而不执行研究脚本；WAV解码所选PCM帧。ZIP记录父文件范围与实际解析的成员；大型CSV/ZIP样例不代表完整文件验收。\n',
        '- 文件角色经变量和项目说明复核。实验设计、模型刺激、打乱对照、模型预测、医疗子表和主体语言观测分别标明。\n',
        '- 清单采用广度优先和代表文件检查，未穷尽所有版本、组件或大文件。已列文件数为下界；未找到文件只限本次检查范围。原始参与者记录与转写正文未上传。\n\n',
        '## 65项逐项结果\n\n',
        '| 编号 | 项目 | 本次结论 | 完整可读文件 | 数据样例 |\n',
        '| --- | --- | --- | ---: | ---: |\n']
    for r in audit['records']:
        out.append(f"| {r['resource_id']} | [{md(r['name'])}]({r['source_url']}) | "
            f"{LABELS.get(r['audit_status'],md(r['audit_status']))} | {r['readable_complete_files']} | {len(r['partial_file_checks'])} |\n")
    out.append('\n## 逐条文件与限制\n\n')
    for r in audit['records']:
        out.extend([f"### {r['resource_id']} {r['name']}\n\n",r['findings_zh']+'\n\n'])
        if r.get('promoted_to'):out.append(f"已补入主目录 **{r['promoted_to']}**。\n\n")
        for f in r['selected_file_checks']:
            out.append(f"- [{md(f['name'])}]({f['download_url']})：{md(f['result_zh'])}。角色：{f['file_role']}。\n")
            if f.get('sha256'):out.append(f"  SHA-256：`{f['sha256']}`。\n")
        for f in r['partial_file_checks']:
            out.append(f"- [{md(f['name'])}]({f['download_url']})：{md(f['result_zh'])}；范围 `{f['read_scope']}`。\n")
        for source in r.get('browser_evidence_urls',[]):
            out.append(f'- [网页核对入口]({source})\n')
        out.append('\n后续：'+r['remaining_work']+'\n\n')
    out.extend(['## 候选处理与复用边界\n\n',
        'C012原项目rjdqb已公开处理表，完整读取4张真实观测或加工表，并读README核对打乱对照。'
        '新增R181只确认这些公开表；不扩大为原始视频、全部转写或独立样本均开放。项目显示No License，复用前须确认许可。\n\n',
        'C003、C011、C016原项目在登录后仍显示You Need Permission，未代用户发送访问申请。'
        'C013原项目只列材料附录，不能晋升为已确认公开观测数据。其余7条候选保留10月19日的证据日期。\n\n',
        '复查程序：[广度优先与文件读取](../scripts/osf_resume.py)、'
        '[有界大文件读取](../scripts/osf_ranges.py)。运行所需队列、网页发现的公开文件位置和实际范围均保留在结构化记录中；本地原始缓存不属于发布内容。\n'])
    return ''.join(out)
