"""Research-needs navigation and evidence-backed resource relationships."""
from datetime import date
from pathlib import Path
import re
from urllib.parse import urlparse


RELATION_TYPES = {
    'derived_from': ('派生自', '派生资料', 'source_to_target'),
    'same_participants': ('同一批被试', '同一批被试', 'bidirectional'),
    'same_materials': ('同一套材料', '同一套材料', 'bidirectional'),
    'subset_of': ('子集属于', '包含子集', 'source_to_target'),
    'verified_join': ('已验证可连接', '已验证可连接', 'bidirectional'),
}


def relation_label(view):
    if view['type'] == 'unverified':
        return '待核实关联'
    forward, inverse, _ = RELATION_TYPES[view['type']]
    return inverse if view['perspective'] == 'incoming' else forward


def relation_index(catalog):
    """Render both ends of one stored edge; legacy links make no typed claim."""
    index = {r['id']: [] for r in catalog['resources']}
    typed_pairs = set()
    for resource in catalog['resources']:
        source = resource['id']
        for relation in resource.get('relations', []):
            target = relation['target_id']
            typed_pairs.add(frozenset((source, target)))
            for current, other, perspective in [(source, target, 'outgoing'), (target, source, 'incoming')]:
                if relation['direction'] == 'bidirectional':
                    perspective = 'bidirectional'
                index[current].append({**relation, 'source_id': source, 'other_id': other, 'perspective': perspective})
    seen = set()
    for resource in catalog['resources']:
        source = resource['id']
        for target in resource['related_ids']:
            pair = frozenset((source, target))
            if pair in typed_pairs or pair in seen:
                continue
            seen.add(pair)
            for current, other in [(source, target), (target, source)]:
                index[current].append({'type': 'unverified', 'source_id': source, 'target_id': target,
                                       'other_id': other, 'perspective': 'unspecified', 'direction': 'unspecified'})
    return index


def matching_relations(views, relation_type=None, related_to=None):
    return [view for view in views if (not relation_type or view['type'] == relation_type)
            and (not related_to or view['other_id'] == related_to)]


def validate_navigation(catalog, root):
    """Core checks also run without the optional jsonschema dependency."""
    errors = []

    def check(condition, message):
        if not condition:
            errors.append(message)

    def obj(value, required, optional, prefix):
        if not isinstance(value, dict):
            errors.append(prefix + ': expected an object')
            return False
        check(set(required) <= set(value) <= set(required) | set(optional), prefix + ': unexpected or missing fields')
        return set(required) <= set(value)

    def nonempty(value):
        return isinstance(value, str) and bool(value.strip())

    def strings(value):
        return isinstance(value, list) and bool(value) and all(nonempty(x) for x in value) and len(set(value)) == len(value)

    def url(value):
        if not isinstance(value, str):
            return False
        parsed = urlparse(value)
        return parsed.scheme in ('http', 'https') and bool(parsed.netloc)

    def valid_date(value):
        try:
            return isinstance(value, str) and date.fromisoformat(value) <= date.fromisoformat(catalog['updated_on'])
        except (ValueError, TypeError):
            return False

    resources = catalog['resources']
    ids = {r['id'] for r in resources}
    needs = catalog.get('research_needs')
    if not isinstance(needs, list) or not needs:
        errors.append('research_needs: expected a nonempty list')
        needs = []
    seen_needs = set()
    for need in needs:
        if not obj(need, ['id', 'label', 'question', 'selection_note', 'resources'], [], 'research_needs'):
            continue
        prefix = 'research_needs/' + str(need['id'])
        nid = need['id']
        check(isinstance(nid, str) and bool(re.fullmatch('[a-z][a-z0-9-]*', nid)), prefix + ': invalid ID')
        if isinstance(nid, str):
            check(nid not in seen_needs, prefix + ': duplicate ID')
            seen_needs.add(nid)
        check(all(nonempty(need[key]) for key in ['label', 'question', 'selection_note']), prefix + ': empty description')
        members = need['resources']
        if not isinstance(members, list) or not members:
            errors.append(prefix + ': expected nonempty resources')
            continue
        seen_members = set()
        for member in members:
            if not obj(member, ['resource_id', 'use_for', 'check_before_use'], [], prefix):
                continue
            rid = member['resource_id']
            check(isinstance(rid, str) and rid in ids, prefix + ': unknown resource ID')
            if isinstance(rid, str):
                check(rid not in seen_members, prefix + ': duplicate resource ID')
                seen_members.add(rid)
            check(all(nonempty(member[key]) for key in ['use_for', 'check_before_use']), prefix + ': empty selection rationale or boundary')

    seen_edges = set()
    for resource in resources:
        relations = resource.get('relations', [])
        if not isinstance(relations, list):
            errors.append(resource['id'] + ': relations must be a list')
            continue
        for relation in relations:
            prefix = resource['id'] + '/relations'
            if not obj(relation, ['type', 'target_id', 'direction', 'scope', 'evidence'], ['join_check'], prefix):
                continue
            kind, target = relation['type'], relation['target_id']
            if not isinstance(kind, str) or kind not in RELATION_TYPES:
                errors.append(prefix + ': unknown relation type')
                continue
            check(isinstance(target, str) and target in ids and target != resource['id'], prefix + ': unknown or self-referencing target')
            direction = RELATION_TYPES[kind][2]
            check(relation['direction'] == direction, prefix + ': direction disagrees with relation type')
            if isinstance(target, str):
                endpoints = tuple(sorted((resource['id'], target))) if direction == 'bidirectional' else (resource['id'], target)
                edge = (kind, endpoints)
                check(edge not in seen_edges, prefix + ': duplicate relation (including reverse symmetric edge)')
                seen_edges.add(edge)
            check(nonempty(relation['scope']), prefix + ': missing relation scope')
            evidence = relation['evidence']
            if obj(evidence, ['basis', 'checked_on', 'summary', 'urls'], [], prefix + '/evidence'):
                expected_basis = 'file_join_check' if kind == 'verified_join' else 'documentation'
                check(evidence['basis'] == expected_basis, prefix + ': evidence basis disagrees with relation type')
                check(valid_date(evidence['checked_on']), prefix + ': invalid evidence date')
                check(nonempty(evidence['summary']), prefix + ': missing evidence summary')
                check(strings(evidence['urls']) and all(url(u) for u in evidence['urls']), prefix + ': missing or invalid evidence URLs')
            if kind != 'verified_join':
                check('join_check' not in relation, prefix + ': join_check requires verified_join')
                continue
            join = relation.get('join_check')
            fields = ['source_file', 'target_file', 'source_keys', 'target_keys', 'normalization', 'cardinality',
                      'matched_rows', 'unmatched_source_rows', 'unmatched_target_rows', 'ambiguous_keys', 'report_path']
            if not obj(join, fields, [], prefix + '/join_check'):
                continue
            for side in ['source_file', 'target_file']:
                artifact = join[side]
                if obj(artifact, ['url', 'version', 'sha256'], [], prefix + '/' + side):
                    check(url(artifact['url']) and nonempty(artifact['version']), prefix + ': missing file URL/version')
                    check(isinstance(artifact['sha256'], str) and bool(re.fullmatch('[a-f0-9]{64}', artifact['sha256'])), prefix + ': missing complete-file SHA-256')
            source_keys, target_keys = join['source_keys'], join['target_keys']
            check(strings(source_keys) and strings(target_keys) and len(source_keys) == len(target_keys), prefix + ': join keys must be nonempty corresponding lists')
            check(nonempty(join['normalization']), prefix + ': missing join normalization rule')
            check(join['cardinality'] in ['one_to_one', 'one_to_many', 'many_to_one', 'many_to_many'], prefix + ': invalid join cardinality')
            for field in ['matched_rows', 'unmatched_source_rows', 'unmatched_target_rows', 'ambiguous_keys']:
                check(type(join[field]) is int and join[field] >= (1 if field == 'matched_rows' else 0), prefix + ': invalid ' + field)
            check(join['ambiguous_keys'] == 0, prefix + ': unresolved ambiguous join keys')
            path = join['report_path']
            if not nonempty(path):
                check(False, prefix + ': missing join report path')
            else:
                resolved = (root / path).resolve()
                check(not Path(path).is_absolute() and root.resolve() in resolved.parents and resolved.is_file(), prefix + ': join report must be an existing repository file')
    return errors
