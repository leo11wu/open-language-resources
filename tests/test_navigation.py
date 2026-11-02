"""Catalog navigation requirements; fixtures never assert real file joins."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build import generated_files, resource_relations
from navigation import RELATION_TYPES, matching_relations, relation_index, relation_label, validate_navigation


def fixture():
    return {
        'updated_on': '2026-11-02',
        'research_needs': [{'id': 'test-need', 'label': '测试入口', 'question': '测试问题',
                            'selection_note': '仅为测试夹具', 'resources': [
                                {'resource_id': 'R001', 'use_for': '测试用途', 'check_before_use': '测试边界'}]}],
        'resources': [{'id': 'R001', 'related_ids': ['R002']},
                      {'id': 'R002', 'related_ids': ['R001']},
                      {'id': 'R003', 'related_ids': []}],
    }


def edge(kind='derived_from', target='R002'):
    return {'type': kind, 'target_id': target, 'direction': RELATION_TYPES[kind][2],
            'scope': 'Synthetic test scope; not a real resource relationship.',
            'evidence': {'basis': 'documentation', 'checked_on': '2026-11-02',
                         'summary': 'Synthetic fixture only.', 'urls': ['https://example.org/documentation']}}


def join_edge():
    relation = edge('verified_join')
    relation['evidence']['basis'] = 'file_join_check'
    relation['join_check'] = {
        'source_file': {'url': 'https://example.org/source.csv', 'version': 'test-v1', 'sha256': 'a' * 64},
        'target_file': {'url': 'https://example.org/target.csv', 'version': 'test-v2', 'sha256': 'b' * 64},
        'source_keys': ['sentence', 'word'], 'target_keys': ['sentence_id', 'word_id'],
        'normalization': 'Synthetic fixture: exact composite keys; no row-order join.',
        'cardinality': 'many_to_one', 'matched_rows': 2,
        'unmatched_source_rows': 1, 'unmatched_target_rows': 3, 'ambiguous_keys': 0,
        'report_path': 'join-report.md',
    }
    return relation


class NavigationValidationTests(unittest.TestCase):
    def setUp(self):
        self.catalog = fixture()
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'join-report.md').write_text('Synthetic join diagnostic for validator tests only.\n')

    def errors(self):
        return validate_navigation(self.catalog, self.root)

    def test_all_five_types_with_sufficient_metadata_are_accepted(self):
        for kind in RELATION_TYPES:
            with self.subTest(kind=kind):
                self.catalog['resources'][0]['relations'] = [join_edge() if kind == 'verified_join' else edge(kind)]
                self.assertEqual([], self.errors())

    def test_bad_research_need_membership_and_missing_boundaries(self):
        mutations = [
            lambda n: n['resources'].append(deepcopy(n['resources'][0])),
            lambda n: n['resources'][0].update(resource_id='R999'),
            lambda n: n['resources'][0].update(check_before_use=' '),
            lambda n: n.update(resources=[]),
            lambda n: n.update(id='Invalid ID'),
        ]
        original = deepcopy(self.catalog['research_needs'][0])
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                self.catalog['research_needs'] = [deepcopy(original)]
                mutation(self.catalog['research_needs'][0])
                self.assertTrue(self.errors())
        self.catalog['research_needs'] = [original, deepcopy(original)]
        self.assertTrue(self.errors())

    def test_bad_relation_identity_direction_and_evidence(self):
        mutations = [
            lambda r: r.update(target_id='R999'), lambda r: r.update(target_id='R001'),
            lambda r: r.update(type='related'), lambda r: r.update(direction='bidirectional'),
            lambda r: r.update(scope=' '), lambda r: r.pop('evidence'),
            lambda r: r['evidence'].update(urls=[]), lambda r: r['evidence'].update(urls=['file:///private']),
            lambda r: r['evidence'].update(summary=''), lambda r: r['evidence'].update(checked_on='2099-01-01'),
            lambda r: r['evidence'].update(checked_on='not-a-date'), lambda r: r.update(unexpected=True),
        ]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                relation = edge()
                mutation(relation)
                self.catalog['resources'][0]['relations'] = [relation]
                self.assertTrue(self.errors())

    def test_duplicate_and_reverse_symmetric_relations_are_rejected(self):
        self.catalog['resources'][0]['relations'] = [edge(), edge()]
        self.assertTrue(self.errors())
        self.catalog['resources'][0]['relations'] = [edge('same_materials')]
        self.catalog['resources'][1]['relations'] = [edge('same_materials', 'R001')]
        self.assertTrue(self.errors())

    def test_verified_join_needs_actual_file_identifiers_keys_and_report(self):
        mutations = [
            lambda r: r.pop('join_check'), lambda r: r['evidence'].update(basis='documentation'),
            lambda r: r['join_check']['source_file'].pop('version'),
            lambda r: r['join_check']['target_file'].update(sha256=''),
            lambda r: r['join_check'].update(source_keys=[]),
            lambda r: r['join_check'].update(target_keys=['sentence_id']),
            lambda r: r['join_check'].update(normalization=''),
            lambda r: r['join_check'].update(cardinality='unknown'),
            lambda r: r['join_check'].update(matched_rows=0),
            lambda r: r['join_check'].update(matched_rows=True),
            lambda r: r['join_check'].update(unmatched_target_rows=-1),
            lambda r: r['join_check'].update(ambiguous_keys=1),
            lambda r: r['join_check'].update(report_path='missing-report.md'),
            lambda r: r['join_check'].update(report_path='../outside.md'),
            lambda r: r['join_check'].update(report_path=str(self.root / 'join-report.md')),
        ]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                relation = join_edge()
                mutation(relation)
                self.catalog['resources'][0]['relations'] = [relation]
                self.assertTrue(self.errors())
        relation = edge('same_materials')
        relation['join_check'] = join_edge()['join_check']
        self.catalog['resources'][0]['relations'] = [relation]
        self.assertTrue(self.errors())

    def test_legacy_links_stay_unverified_and_do_not_duplicate(self):
        before = deepcopy(self.catalog)
        index = relation_index(self.catalog)
        self.assertEqual(['unverified'], [view['type'] for view in index['R001']])
        self.assertEqual(['unverified'], [view['type'] for view in index['R002']])
        self.assertFalse(matching_relations(index['R001'], 'verified_join'))
        self.assertFalse(matching_relations(index['R001'], 'same_participants'))
        self.assertEqual(before, self.catalog)
        self.catalog['resources'][0]['relations'] = [edge()]
        index = relation_index(self.catalog)
        self.assertEqual(['derived_from'], [view['type'] for view in index['R001']])
        self.assertEqual(['incoming'], [view['perspective'] for view in index['R002']])
        self.assertEqual('派生资料', relation_label(index['R002'][0]))

    def test_relation_type_and_endpoint_must_match_the_same_edge(self):
        self.catalog['resources'][0]['relations'] = [edge(), edge('same_materials', 'R003')]
        views = relation_index(self.catalog)['R001']
        self.assertFalse(matching_relations(views, 'derived_from', 'R003'))
        self.assertEqual(1, len(matching_relations(views, 'same_materials', 'R003')))

    def test_join_metadata_renders_after_the_relationship_table(self):
        self.catalog['resources'][0]['relations'] = [join_edge(), edge('derived_from', 'R003')]
        lookup = {r['id']: {**r, 'name': r['id'], 'category': 'syntax'} for r in self.catalog['resources']}
        rendered = resource_relations(relation_index(self.catalog)['R001'], lookup)
        self.assertLess(rendered.index('| 派生自 |'), rendered.index('连接记录'))
        self.assertIn('sentence, word', rendered)
        self.assertIn('a' * 64, rendered)
        self.assertIn('../join-report.md', rendered)
        self.assertIn('源/目标未匹配1/3', rendered)

    def test_full_schema_accepts_types_and_rejects_incomplete_join(self):
        try:
            from jsonschema import Draft202012Validator, FormatChecker
        except ImportError:
            self.skipTest('optional jsonschema package unavailable; core negative tests still run')
        schema = json.loads((ROOT / 'schema/resources.schema.json').read_text())
        validator = Draft202012Validator({'$ref': '#/$defs/relation', '$defs': schema['$defs']},
                                        format_checker=FormatChecker())
        for kind in RELATION_TYPES:
            relation = join_edge() if kind == 'verified_join' else edge(kind)
            self.assertEqual([], list(validator.iter_errors(relation)))
        for mutate in [lambda r: r.pop('join_check'), lambda r: r['join_check']['source_file'].pop('version'),
                       lambda r: r['join_check'].update(source_keys=[]),
                       lambda r: r['evidence'].update(basis='documentation')]:
            relation = join_edge()
            mutate(relation)
            self.assertTrue(list(validator.iter_errors(relation)))


class CatalogIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((ROOT / 'data/resources.json').read_text())
        cls.files = generated_files(cls.catalog)

    def query(self, *args):
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/query.py'), *args, '--format', 'json'],
                                text=True, capture_output=True, check=True)
        return json.loads(result.stdout)

    def test_current_catalog_and_schema_vocabulary_agree(self):
        self.assertEqual([], validate_navigation(self.catalog, ROOT))
        schema = json.loads((ROOT / 'schema/resources.schema.json').read_text())
        self.assertEqual(set(RELATION_TYPES), set(schema['$defs']['relation']['properties']['type']['enum']))
        self.assertEqual(self.catalog['schema_version'], schema['properties']['schema_version']['const'])

    def test_research_need_filter_combines_with_existing_filters(self):
        rows = self.query('--need', 'structural-distribution', '--category', 'syntax')
        self.assertEqual({'R059', 'R061'}, {r['id'] for r in rows})
        self.assertTrue(all(r['research_need_match']['check_before_use'] for r in rows))
        rows = self.query('--need', 'processing-evidence', '--check-state', 'supporting_files_checked')
        self.assertEqual(['R040'], [r['id'] for r in rows])

    def test_both_endpoints_are_searchable_with_direction_and_evidence(self):
        rows = self.query('--relation', 'derived_from', '--related-to', 'R002')
        self.assertEqual({'R061', 'R062'}, {r['id'] for r in rows})
        self.assertTrue(all(r['matching_relations'][0]['perspective'] == 'outgoing' for r in rows))
        rows = self.query('--relation', 'derived_from', '--related-to', 'R061')
        self.assertEqual(['R002'], [r['id'] for r in rows])
        view = rows[0]['matching_relations'][0]
        self.assertEqual(('R061', 'R002', 'incoming'), (view['source_id'], view['target_id'], view['perspective']))
        self.assertTrue(view['evidence']['urls'])
        for target, expected in [('R022', 'R180'), ('R180', 'R022')]:
            rows = self.query('--relation', 'same_materials', '--related-to', target)
            self.assertEqual([expected], [r['id'] for r in rows])
            self.assertEqual('bidirectional', rows[0]['matching_relations'][0]['perspective'])

    def test_unverified_links_do_not_become_subset_or_verified_join(self):
        rows = self.query('--relation', 'unverified', '--related-to', 'R011')
        self.assertIn('R131', [r['id'] for r in rows])
        self.assertEqual([], self.query('--relation', 'subset_of', '--related-to', 'R011'))
        self.assertEqual([], self.query('--relation', 'same_participants'))
        self.assertEqual([], self.query('--relation', 'verified_join'))

    def test_existing_json_queries_remain_plain_resource_records(self):
        self.assertEqual(self.catalog['resources'], self.query())
        self.assertTrue(self.query('--index', 'norare', '--lang', 'zh'))
        self.assertTrue(self.query('--index', 'candidates', '--category', 'syntax'))

    def test_new_filters_are_rejected_on_other_indexes(self):
        for args in [('--index', 'norare', '--need', 'processing-evidence'),
                     ('--index', 'candidates', '--relation', 'same_materials'),
                     ('--index', 'norare', '--related-to', 'R002')]:
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/query.py'), *args], text=True, capture_output=True)
            self.assertEqual(2, result.returncode)
            self.assertIn('main catalog only', result.stderr)

    def test_generated_navigation_has_valid_anchors_and_retains_verification(self):
        guide = self.files['docs/research-needs.md']
        for need in self.catalog['research_needs']:
            self.assertIn('docs/research-needs.md#' + need['id'], self.files['README.md'])
            self.assertIn('<a id="' + need['id'] + '"></a>', guide)
            for member in need['resources']:
                resource = next(r for r in self.catalog['resources'] if r['id'] == member['resource_id'])
                page = self.files['catalog/' + resource['category'] + '.md']
                self.assertIn('<a id="' + resource['id'].lower() + '"></a>', page)
                self.assertIn(member['check_before_use'], guide)
                self.assertIn(resource['verification']['note'], page)
        self.assertIn('R061 → R002', self.files['catalog/child-language.md'])
        self.assertIn('待核实关联', self.files['catalog/speech-phonetics.md'])
        lines = [json.loads(line) for line in self.files['data/resources.jsonl'].splitlines()]
        self.assertEqual(self.catalog['resources'], lines)


if __name__ == '__main__':
    unittest.main()
