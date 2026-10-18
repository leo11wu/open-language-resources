#!/usr/bin/env python3
"""Aggregate-only structural checks; no hypothesis tests or model ranking.

Requires pandas and licensed SWOW-EN18.zip obtained by the researcher. Does not
write responses, participant identifiers, or item-level association values.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile

import pandas as pd


def inventory(path):
    raw = path.read_bytes()
    return {"file": path.name, "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "git_blob_sha1": hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()}


def english(path):
    with zipfile.ZipFile(path) as z:
        name = next(x for x in z.namelist() if x.endswith("SWOW-EN.R100.20180827.csv"))
        d = pd.read_csv(io.BytesIO(z.read(name)), keep_default_na=False,
                        usecols=["participantID", "nativeLanguage", "country", "cue", "age", "gender", "R1"])
    duplicate = int(d.duplicated(["participantID", "cue"]).sum())
    valid = d.loc[~d.R1.isin(["", "NA", "#Missing", "#Unknown"])].copy()
    groups = ["United States", "United Kingdom", "Canada", "Australia"]
    counts = valid.groupby(["cue", "nativeLanguage"]).participantID.nunique().unstack(fill_value=0)
    out = {"rows": len(d), "cues": int(d.cue.nunique()), "people": int(d.participantID.nunique()),
           "duplicate_participant_cue_rows": duplicate, "invalid_R1_rows": int(len(d)-len(valid)),
           "group_field": "nativeLanguage (self-reported native English regional variety)",
           "country_used_for_grouping": False, "regional_groups": {}, "joint_cue_counts": {}}
    for g in groups:
        sub = d.loc[d.nativeLanguage.eq(g)]
        ps = sub.drop_duplicates("participantID")
        c = counts[g]
        out["regional_groups"][g] = {"rows": len(sub), "people": len(ps),
            "valid_R1_rows": int(valid.nativeLanguage.eq(g).sum()),
            "median_valid_people_per_cue": float(c.median()),
            "cues_at_least_n_people": {str(n): int(c.ge(n).sum()) for n in [5, 10, 15, 20, 30]},
            "missing_age_people": int(pd.to_numeric(ps.age, errors="coerce").isna().sum()),
            "people_country_same_as_variety": int(ps.country.eq(g).sum())}
    for label, gg in [("US_UK",groups[:2]), ("US_UK_CA",groups[:3]), ("US_UK_CA_AU",groups)]:
        out["joint_cue_counts"][label] = {str(n): int(counts[gg].ge(n).all(axis=1).sum()) for n in [5,10,15,20,30]}
    consistency = d.groupby("participantID")[["nativeLanguage", "country", "age", "gender"]].nunique()
    out["people_with_inconsistent_metadata_across_rows"] = {x:int(consistency[x].gt(1).sum()) for x in consistency}
    return out, set(d.cue.str.lower().str.strip()), valid


def scarfs(root, vocabulary):
    d = pd.read_csv(root / "aligned_results_public.csv", keep_default_na=False)
    b = pd.read_csv(root / "behavioral_results_public.csv", keep_default_na=False)
    t = pd.read_csv(root / "taboo_with_distances.csv", keep_default_na=False)
    key = ["ppt_id", "partner_id", "trial_with_partner", "card"]
    assert not b.duplicated(key).any(), "Behavioral trial key is not unique"
    n = d.loc[d.Native_Speaker.eq("Yes")].copy()
    joined = n.merge(b[key + ["trial_result"]], on=key, how="left", validate="many_to_one", indicator=True, suffixes=("", "_behavior"))
    card_norm = lambda x: str(x).lower().strip()
    n["target_norm"] = n.card.map(card_norm)
    n["head_norm"] = n.head_noun.map(card_norm)
    # Narrow content-noun proxy only; actual clues can contain verbs and modifiers.
    content = n.loc[n.head_noun_tag.isin(["NN", "NNS", "NNP", "NNPS"])].copy()
    content["begin_num"] = pd.to_numeric(content.begin_time, errors="coerce")
    first = content.sort_values(["begin_num", "end_time"], kind="stable").drop_duplicates(key)
    both = first.target_norm.isin(vocabulary) & first.head_norm.isin(vocabulary)
    target_table = t["Word to be explained"].map(card_norm)
    actual_cards = set(n.target_norm)
    taboos = [str(x).lower().strip() for x in t[["taboo1", "taboo2", "taboo3", "taboo4", "taboo5"]].to_numpy().ravel() if str(x).strip()]
    out = {"nre_rows_all":len(d), "nre_rows_native":len(n), "behavioral_rows_all":len(b),
           "behavioral_rows_native":int(b.Native_Speaker.eq("Yes").sum()),
           "native_speakers_in_nre":int(n.ppt_id.nunique()), "native_sessions_in_nre":int(n.session_id.nunique()),
           "behavioral_key_unique":True, "trial_key":key,
           "native_nre_trial_keys":len(n[key].drop_duplicates()),
           "native_nre_rows_with_behavioral_match":int(joined._merge.eq("both").sum()),
           "matched_rows_with_conflicting_outcome":int((joined._merge.eq("both") & joined.trial_result.ne(joined.trial_result_behavior)).sum()),
           "native_nre_trials_with_conflicting_outcome":int(n.groupby(key).trial_result.nunique().gt(1).sum()),
           "native_noun_head_proxy_rows":len(content), "first_noun_head_proxy_trials":len(first),
           "first_noun_head_proxy_trials_with_both_SWOW_cues":int(both.sum()),
           "covered_first_noun_head_proxy_targets":int(first.loc[both,"target_norm"].nunique()),
           "covered_first_noun_head_proxy_speakers":int(first.loc[both,"ppt_id"].nunique()),
           "native_cards_seen":len(actual_cards), "taboo_card_rows":len(t),
           "native_cards_with_taboo_word_table":len(actual_cards & set(target_table)),
           "taboo_tokens":len(taboos), "taboo_tokens_in_SWOW_cue_vocabulary":sum(x in vocabulary for x in taboos),
           "first_proxy_length_distribution":{str(k):int(v) for k,v in first.length.value_counts().sort_index().items()},
           "limits":["First noun-head proxy is not necessarily the first clue or the complete message.",
                     "Cue-vocabulary coverage is not an observed directed association edge or predictive validity.",
                     "Lost denotes a rule violation, not a comprehension failure; trial outcomes were not modeled.",
                     "Within-card taboo constraints do not identify the causal effect of banning words without a comparable unconstrained condition."]}
    return out


def childes(path):
    sents=[]
    for block in path.read_text().strip().split("\n\n"):
        meta={}; tok=[]
        for line in block.splitlines():
            if line.startswith("# ") and " = " in line:
                k,v=line[2:].split(" = ",1);meta[k]=v
            elif line and not line.startswith("#"):
                a=line.split("\t")
                if a[0].isdigit():tok.append(a)
        if tok:sents.append((meta,tok))
    adult=[(m,t) for m,t in sents if m.get("speaker_role") in ["Mother","Father"]]
    roles=Counter(m.get("speaker_role") for m,t in sents)
    ff=defaultdict(list); relation_nouns=Counter(); noun_count=0; framed_nouns=0
    function={"ADP","AUX","CCONJ","DET","PART","PRON","SCONJ"}
    for m,tt in adult:
        words=[t for t in tt if t[3]!="PUNCT"]
        for i,t in enumerate(words):
            if t[3] in ["NOUN","PROPN"]:
                noun_count+=1; relation_nouns[t[7]]+=1
            if i>0 and i+1<len(words) and words[i-1][3] in function and words[i+1][3] in function:
                ff[(words[i-1][1].lower(),words[i+1][1].lower())].append((t[3],t[7],t[2].lower(),m.get("child_name")))
                framed_nouns+=int(t[3] in ["NOUN","PROPN"])
    def frame_summary(threshold):
        selected=[v for v in ff.values() if len(v)>=threshold]
        # Structural variation only; no entropy estimate, role prediction, or significance.
        nouns=[[x for x in v if x[0] in ["NOUN","PROPN"]] for v in selected]
        return {"frames":len(selected), "center_tokens":sum(map(len,selected)),
                "noun_center_tokens":sum(map(len,nouns)),
                "frames_with_at_least_2_noun_dependency_labels":sum(len(set(x[1] for x in v))>=2 for v in nouns),
                "frames_with_noun_subject_and_object":sum(any(x[1].split(":")[0]=="nsubj" for x in v) and any(x[1].split(":")[0]=="obj" for x in v) for v in nouns)}
    return {"split":"dev only", "sentences":len(sents),"integer_tokens":sum(len(t) for m,t in sents),
            "children":len(set(m.get("child_name") for m,t in sents)),"speaker_role_sentences":dict(roles),
            "mother_father_sentences":len(adult),"mother_father_integer_tokens":sum(len(t) for m,t in adult),
            "mother_father_noun_propn_tokens":noun_count,"noun_dependency_counts":dict(relation_nouns),
            "function_word_frames_definition":"one intervening non-punctuation token; function UPOS on each side; lowercased surface anchors",
            "function_word_frames":len(ff),"framed_noun_tokens":framed_nouns,
            "frame_occurrence_thresholds":{str(n):frame_summary(n) for n in [3,5,10]},
            "limits":["Grammatical relation is not a semantic agent/patient role.",
                      "Only structural availability in dev was checked; no corpus-wide or learning claim.",
                      "No classifier, model intervention, temporal acquisition trajectory, or held-out prediction was run."]}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-dir",type=Path,required=True)
    p.add_argument("--swow-archive",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    en,vocab,_=english(a.swow_archive)
    result={"date":"2026-10-18","stage":"exploratory_resource_probes", "inference_scope":"coverage, units, keys, and structural variation only", "swow_en":en,
            "scarfs":scarfs(a.source_dir,vocab), "childes":childes(a.source_dir/"en_childes-ud-dev.conllu"),
            "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "software":{"python":sys.version.split()[0],"pandas":pd.__version__},
            "inputs":[inventory(a.swow_archive)]+[inventory(a.source_dir/x) for x in ["aligned_results_public.csv","behavioral_results_public.csv","taboo_with_distances.csv","en_childes-ud-dev.conllu"]]}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
