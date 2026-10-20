"""Derive file-check states and follow-up queues from recorded evidence only."""
from collections import Counter

CHECK_LABELS = {
    'documentation_only': '仅核对说明；未读数据文件',
    'file_preview': '已读文件头部样例',
    'selected_file_checked': '已完整检查选定文件；全库未验收',
    'supporting_files_checked': '已读辅助文件；主体观测数据未验',
    'fully_validated': '资源文件已验收',
    'discovery_portal': '发现入口；不作为数据文件验收',
}


def check_state(resource):
    """A portal is not a dataset; a preview is not a complete file check."""
    verification = resource['verification']
    if resource['data_status'] == 'discovery_portal':
        return 'discovery_portal'
    if verification['data_files_validated']:
        return 'fully_validated'
    if verification.get('osf_audit',{}).get('status') in ('auxiliary_only_readable','materials_only_readable'):
        return 'supporting_files_checked'
    if verification['download_tested']:
        return 'selected_file_checked'
    if verification.get('file_checks'):
        return 'file_preview'
    return 'documentation_only'


def next_steps(resource):
    state = check_state(resource)
    if state == 'discovery_portal':
        return ['检查平台的实际检索及获取流程；选出的具体数据另建资源记录并核对。']
    if state == 'fully_validated':
        return ['在来源或版本改变后复查受影响的文件与许可。']
    steps = []
    if 'osf' in resource['platforms']:
        audit=resource['verification'].get('osf_audit')
        if audit and audit['status'] in ('deferred_api_rate_limit','access_unresolved'):
            steps.append('本轮受API额度限制未读取主体文件；额度可用时继续枚举和下载，不能据此认定资源失效。')
        elif audit and audit['status']=='download_unavailable':
            steps.append('已定位公开文件，但本次下载发生域名解析或连接失败；按逐项记录复查存储端点，不能视作文件已读。')
        elif audit and audit['status']=='source_gone':
            steps.append('当前来源返回410或跳转；沿正式论文和作者发布寻找对应版本，不替换为相近主题数据。')
        elif audit and audit['status']=='empty_storage_in_checked_scope':
            steps.append('本次所查文件区未取得可下载数据；复查正式替代发布和未遍历组件，不能推断数据永久不存在。')
        elif audit and not audit['inventory_complete_within_bounded_scope']:
            steps.append('补查尚未枚举的OSF文件、子组件或版本；已有代表文件检查不等于完整发布范围。')
        else:
            steps.append('按实际研究用途核对所需OSF文件、子组件和版本，区分观测数据、刺激、代码与统计输出。')
    if state == 'selected_file_checked':
        steps.append('已读取和解析的范围限于记录中的选定文件；继续核对其余分析所需文件及完整发布范围。')
    elif state == 'file_preview':
        steps.append('头部样例已读取；完整读取代表性数据表，核对行列、缺失值、变量及发布范围。')
    elif state == 'supporting_files_checked':
        steps.append('已读取的说明或模型派生表属于辅助资料；继续取得并解析主体行为/生理数据。')
    else:
        steps.append('定位并读取代表性数据文件，记录格式、行列或样本单位、变量和读取范围。')
    steps.append('核对数据版本、访问条件、署名和原始许可；若需申请，保留该限制。')
    return steps


def verification_queue(catalog, source_index, candidates):
    resources = catalog['resources']
    counts = Counter(check_state(r) for r in resources)
    return {
        'schema_version': '1.1.0',
        'generated_on': catalog['updated_on'],
        'catalog_version': catalog['catalog_version'],
        'basis': '由现有核对记录生成的待办清单；生成清单不构成新一次数据文件核验。',
        'state_labels': CHECK_LABELS,
        'summary': {
            'main_resource_count': len(resources),
            'main_by_check_state': {state: counts[state] for state in CHECK_LABELS},
            'main_with_recorded_file_reads': sum(bool(r['verification'].get('file_checks')) for r in resources),
            'main_without_recorded_file_reads': sum(not r['verification'].get('file_checks') for r in resources),
            'osf_associated_main_count': sum('osf' in r['platforms'] for r in resources),
            'remaining_candidate_count': candidates['candidate_count'],
            'norare_source_record_count': source_index['record_count'],
            'norare_original_files_checked_count': sum(r['original_files_checked'] for r in source_index['records']),
        },
        'counting_note': '主目录、候选与NoRaRe来源记录层级不同且可能重叠，不相加为独立数据集数量。',
        'main_resources': [
            {
                'resource_id': r['id'], 'name': r['name'], 'category': r['category'],
                'source_url': r['source_url'], 'platforms': r['platforms'], 'osf_ids': r['osf_ids'],
                'check_state': check_state(r),
                'documentation_checked_on': r['verification']['documentation_checked_on'],
                'download_tested': r['verification']['download_tested'],
                'data_files_validated': r['verification']['data_files_validated'],
                'recorded_file_checks': r['verification'].get('file_checks', []),
                'osf_audit': r['verification'].get('osf_audit'),
                'next_steps': next_steps(r),
            }
            for r in resources
        ],
        'remaining_candidates': [
            {'candidate_id': r['id'], 'name': r['name'], 'category': r['category'],
             'source_url': r['source_url'], 'current_status': r['status'],
             'next_verification_step': r['next_verification_step']}
            for r in candidates['candidates']
        ],
        'norare_sources': [
            {'source_id': r['source_id'],
             'source_url': r['original_url'] or r['dataset_folder_url'] or r['source_metadata_url'],
             'original_files_checked': r['original_files_checked'],
             'related_main_ids': r['related_main_ids'],
             'next_step': '回到原始发布页核对文件、测量、版本与许可；聚合库元数据不代替原始文件核验。'}
            for r in source_index['records']
        ],
    }
