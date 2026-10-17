#!/usr/bin/env python3
"""Exploratory coverage/QC, using locally obtained official data; emits aggregates only.

Run with Python 3, pandas and scipy. Do not commit the input SWOW archives.
Required input filenames and hashes are recorded in the associated research note.
"""
import argparse
from collections import Counter
import hashlib
import io
import json
from pathlib import Path
import unicodedata
from zipfile import ZipFile

import pandas as pd
from scipy.stats import pearsonr, spearmanr

ARCHIVES = {
    'en': ('SWOW-EN18.zip', '69ee1f4f19c657bb2f6e1bc27abd2becbcd01d83d1fdade94a0455b4e66eb093', 'R100.'),
    'zh': ('SWOW-ZH23.zip', '7f5e3defdfa29a40f13ad02104b6b37e85f896d382764cef490685fe86bd43b8', 'R55.'),
}
INVALID = {'', 'NA', '#Missing', '#Unknown'}


def norm(value):
    return unicodedata.normalize('NFC', str(value).strip())


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def materials(root, language):
    rows = json.loads((root / ('spaml-matched-' + language + '.json')).read_text())
    out, invalid = {}, []
    for row in rows:
        related, unrelated = row['cue_word_related'], row['cue_word_unrelated']
        target = row['word_combo_related'][len(related):]
        if not row['word_combo_related'].startswith(related) or row['word_combo_unrelated'] != unrelated + target or not target:
            invalid.append({'target_word_unique': row['target_word_unique'], 'reason': 'cue/target concatenation inconsistent across conditions'})
            continue
        out[row['target_word_unique']] = {'target': norm(target), 'related': norm(related),
                                        'unrelated': norm(unrelated)}
    assert len(out) + len(invalid) == len(rows) == 1000
    return out, invalid


def load_norms(root, language, items):
    filename, checksum, marker = ARCHIVES[language]
    archive = (root / filename).read_bytes()
    assert sha256(archive) == checksum, 'Archive differs from official release'
    evidence = []
    packaged = []
    with ZipFile(io.BytesIO(archive)) as z:
        member = next(n for n in z.namelist() if marker in n)
        raw = z.read(member)
        header = pd.read_csv(io.BytesIO(raw), nrows=0).columns.tolist()
        d = pd.read_csv(io.BytesIO(raw), usecols=['cue', 'R1', 'R2', 'R3'], keep_default_na=False)
        for col in d:
            d[col] = d[col].map(norm)
        evidence.append({'member': member, 'bytes': len(raw), 'sha256': sha256(raw),
                         'rows': len(d), 'columns_in_file': len(header),
                         'columns_examined': ['cue', 'R1', 'R2', 'R3']})
        metadata_cues = {}
        for name in z.namelist():
            base = name.split('/')[-1]
            if not base.startswith(('cueStats.', 'strength.')):
                continue
            blob = z.read(name)
            delimiter = '\t' if language == 'en' and base.startswith('strength.') else ','
            frame = pd.read_csv(io.BytesIO(blob), sep=delimiter, keep_default_na=False)
            evidence.append({'member': name, 'bytes': len(blob), 'sha256': sha256(blob),
                             'rows': len(frame), 'columns_in_file': len(frame.columns),
                             'columns_examined': frame.columns.tolist()})
            response_set = 'R123' if '.R123.' in base else 'R1'
            if base.startswith('cueStats.'):
                cue_col = 'cue' if 'cue' in frame else 'Cues'
                metadata_cues[response_set] = set(frame[cue_col].map(norm))
            else:
                probs = frame.columns[-1]
                sums = frame.groupby('cue')[probs].sum()
                packaged.append({'response_set': response_set, 'edges': len(frame),
                                 'cue_count': int(frame.cue.nunique()),
                                 'response_count': int(frame.response.nunique()),
                                 'response_types_outside_cue_vocabulary': len(set(frame.response)-set(frame.cue)),
                                 'outgoing_strength_sum_min': float(sums.min()),
                                 'outgoing_strength_sum_max': float(sums.max())})
    trials = d.groupby('cue').size().to_dict()
    targets = {v['target'] for v in items.values()}
    needed_cues = targets | {v[c] for v in items.values() for c in ['related', 'unrelated']}
    query_responses = needed_cues
    denoms = {'R1': Counter(), 'R123': Counter()}
    edges = {'R1': Counter(), 'R123': Counter()}
    response_vocabulary = set()
    invalid_counts = {}
    for column in ['R1', 'R2', 'R3']:
        valid = ~d[column].isin(INVALID)
        invalid_counts[column] = d.loc[~valid, column].value_counts().to_dict()
        response_vocabulary.update(d.loc[valid, column])
        chosen = d.loc[valid & d.cue.isin(needed_cues), ['cue', column]]
        totals = chosen.groupby('cue').size().to_dict()
        pairs = chosen.loc[chosen[column].isin(query_responses)].groupby(['cue', column]).size().to_dict()
        denoms['R123'].update(totals)
        edges['R123'].update(pairs)
        if column == 'R1':
            denoms['R1'].update(totals)
            edges['R1'].update(pairs)
    summary = {'archive': filename, 'archive_sha256': checksum, 'archive_bytes': len(archive),
               'checksum_matches_official': True, 'balanced_member': member,
               'balanced_rows': len(d), 'balanced_cues': len(trials),
               'trials_per_cue_min': int(min(trials.values())),
               'trials_per_cue_max': int(max(trials.values())),
               'missing_marker_counts': invalid_counts,
               'cue_metadata_count': {k: len(v) for k, v in metadata_cues.items()},
               'packaged_strength_diagnostics': packaged, 'files_examined': evidence}
    return {'summary': summary, 'trials': trials, 'denoms': denoms, 'edges': edges,
            'vocab': response_vocabulary, 'metadata_cues': metadata_cues}


def score(norms, item, response_set, all_trials=False, reverse=False):
    result = []
    for condition in ['related', 'unrelated']:
        cue, target = item[condition], item['target']
        if reverse:
            cue, target = target, cue
        n = norms['denoms'][response_set][cue]
        if n <= 0:
            return None
        denominator = norms['trials'][cue] if all_trials else n
        if all_trials and response_set == 'R123':
            denominator *= 3
        result.append(norms['edges'][response_set][cue, target] / denominator)
    return result[0] - result[1]


def correlation(a, b):
    if len(a) < 3 or pd.Series(a).nunique() < 2 or pd.Series(b).nunique() < 2:
        return {'n': len(a), 'pearson_r': None, 'spearman_rho': None}
    return {'n': len(a), 'pearson_r': float(pearsonr(a, b).statistic),
            'spearman_rho': float(spearmanr(a, b).statistic)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = args.input_dir
    material_results = {lang: materials(root, lang) for lang in ['en', 'zh']}
    items = {lang: material_results[lang][0] for lang in material_results}
    norms = {lang: load_norms(root, lang, items[lang]) for lang in items}
    links = json.loads((root / 'spaml-author-links-one-to-one.json').read_text())['links']
    assert len(links) == len({r['en_key'] for r in links}) == len({r['zh_key'] for r in links}) == 993
    priming = {lang: pd.read_csv(root / (lang + '_prime_summary.csv')).set_index('target_word_unique')
               for lang in items}
    full_rows = []
    diagnostics = {}
    for response_set in ['R1', 'R123']:
        coverage = {}
        for lang in items:
            covered = {condition: sum(norms[lang]['denoms'][response_set][v[condition]] > 0
                                     for v in items[lang].values())
                       for condition in ['related', 'unrelated', 'target']}
            covered['both_condition_cues'] = sum(score(norms[lang], v, response_set) is not None
                                                for v in items[lang].values())
            covered['material_rows_examined'] = 1000
            covered['material_rows_consistent'] = len(items[lang])
            coverage[lang] = covered
        records = []
        for link in links:
            record = {'translation_id': link['translation_id']}
            for lang in items:
                key = link[lang + '_key']
                item = items[lang][key]
                record[lang] = score(norms[lang], item, response_set)
                record[lang + '_trial_denominator'] = score(norms[lang], item, response_set, all_trials=True)
                record[lang + '_backward'] = score(norms[lang], item, response_set, reverse=True)
                record[lang + '_priming'] = float(priming[lang].loc[key, 'avgZ_prime'])
                record[lang + '_target'] = item['target']
                record[lang + '_repetition'] = any(item[c] == item['target'] for c in ['related','unrelated'])
                record[lang + '_target_seen_response'] = item['target'] in norms[lang]['vocab']
                record[lang + '_metadata_cues'] = all(item[c] in norms[lang]['metadata_cues'][response_set]
                                                     for c in ['related','unrelated'])
                record[lang + '_min_valid_response_n'] = min(norms[lang]['denoms'][response_set][item[c]]
                                                            for c in ['related','unrelated'])
            records.append(record)
        complete = [r for r in records if r['en'] is not None and r['zh'] is not None]
        clean = [r for r in complete if not r['en_repetition'] and not r['zh_repetition']]
        associations = [r['zh'] - r['en'] for r in clean]
        behavior = [r['zh_priming'] - r['en_priming'] for r in clean]
        diagnostic = {'per_language_1000_items': coverage, 'aligned_candidate_n': len(links),
                      'complete_four_condition_cues': len(complete), 'complete_without_repetition': len(clean),
                      'distinct_zh_targets_without_repetition': len({r['zh_target'] for r in clean}),
                      'complete_including_backward': sum(r['en_backward'] is not None and r['zh_backward'] is not None for r in clean),
                      'complete_with_cues_in_published_cue_metadata': sum(r['en_metadata_cues'] and r['zh_metadata_cues'] for r in clean),
                      'target_seen_among_all_responses_both_languages': sum(r['en_target_seen_response'] and r['zh_target_seen_response'] for r in clean),
                      'nonzero_association_contrast': {lang: sum(r[lang] != 0 for r in clean) for lang in items},
                      'zero_contrast_both_languages': sum(r['en'] == 0 and r['zh'] == 0 for r in clean),
                      'contrast_nonzero_both_languages': sum(r['en'] != 0 and r['zh'] != 0 for r in clean),
                      'crosslanguage_delta_association_correlation': correlation([r['en'] for r in clean], [r['zh'] for r in clean]),
                      'association_difference_vs_behavior_difference': correlation(associations, behavior),
                      'trial_denominator_difference_vs_behavior_difference': correlation([r['zh_trial_denominator']-r['en_trial_denominator'] for r in clean], behavior),
                      'within_language_association_vs_priming': {lang: correlation([r[lang] for r in clean], [r[lang+'_priming'] for r in clean]) for lang in items},
                      'association_shift_at_least_0_10': {'zh_greater': sum(a >= .1 for a in associations), 'en_greater': sum(a <= -.1 for a in associations)},
                      'minimum_valid_responses_per_condition': {lang: {'min': min(r[lang+'_min_valid_response_n'] for r in clean),
                                                                 'median': float(pd.Series([r[lang+'_min_valid_response_n'] for r in clean]).median())} for lang in items}}
        diagnostics[response_set] = diagnostic
        if response_set == 'R1':
            full_rows = records
    report = {'schema_version':'1.0.0', 'checked_on':'2026-10-17',
              'stage':'exploratory_feasibility_not_confirmatory',
              'resource_ids':['R022','R147'],
              'decision':'revise',
              'normalization':'NFC and surrounding whitespace only; case preserved; no synonym or traditional/simplified remapping',
              'association_measure':'P(target|cue) from balanced R1 or R123 responses, conditional on valid responses; all-trial denominator is sensitivity only',
              'zero_policy':'Cue absent/no valid responses = unavailable; observed cue with no target response = sample zero, not a population zero',
              'material_inconsistencies':{lang:material_results[lang][1] for lang in items},
              'input_releases':{lang:norms[lang]['summary'] for lang in items},
              'diagnostics':diagnostics,
              'all_993_crosslanguage_behavior_correlation':correlation([r['en_priming'] for r in full_rows], [r['zh_priming'] for r in full_rows]),
              'limits':['No manual semantic-equivalence acceptance', 'No trial-level reanalysis, sample-size equalization, covariate controls or crossvalidation',
                        'No model scoring or mechanism/causal inference', 'R1 and R123 are dependent sensitivity measures',
                        'Exploratory subset chosen by resource coverage; correlations do not constitute a confirmatory test']}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['stage','decision','diagnostics']},ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
