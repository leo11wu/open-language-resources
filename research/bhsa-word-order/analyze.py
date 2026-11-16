"""Replicate the BHSA 2021 Genesis query and compare word order by book and verb form."""

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "data/bhsa-file-check-2026-11-16.json"
PIN = "b112c161cfd21eae403d51a2733740d8743460e7"
FEATURES = ("otype", "oslots", "functional_parent", "function", "language",
            "sp", "vt", "txt", "book", "chapter")
TEXT_TYPES = ("N", "NQ", "?N", "?NQ")
STRICT = (("N",), ("NQ",))
INCLUDE_UNKNOWN_OUTER = (("N", "?N"), ("NQ", "?NQ"))
ANCHOR = "Genesis"
FOLLOWUP_COUNT = 5
COVERAGE_FLOOR = 30
FUNCTIONS = {"Subj", "Pred"}


def expand_nodes(spec):
    for piece in spec.split(","):
        first, separator, last = piece.partition("-")
        start = int(first)
        stop = int(last) if separator else start
        if not 1 <= start <= stop:
            raise ValueError(f"Invalid Text-Fabric node range: {spec}")
        yield from range(start, stop + 1)


def feature_rows(directory, feature, edge=False):
    with (directory / f"{feature}.tf").open(encoding="utf-8") as stream:
        expected = "@edge" if edge else "@node"
        if stream.readline().strip() != expected:
            raise ValueError(f"Expected {expected} for {feature}")
        metadata = {}
        for line in stream:
            if not line.strip():
                break
            key, _, value = line.strip().partition("=")
            metadata[key] = value
        if metadata.get("@version") != "2021" or "@edgeValues" in metadata:
            raise ValueError(f"Unexpected Text-Fabric metadata for {feature}")
        previous = 0
        for line in stream:
            fields = line.rstrip("\n").split("\t")
            if len(fields) == 1:
                nodes = (previous + 1,)
            elif len(fields) == 2:
                nodes = tuple(expand_nodes(fields[0]))
            else:
                raise ValueError(f"Unexpected fields for {feature}: {line!r}")
            previous = max(nodes)
            for node in nodes:
                yield node, fields[-1]


def verify_files(directory, audit):
    result = {}
    if audit["version"]["commit"] != PIN:
        raise ValueError("The prior audit uses a different BHSA commit")
    for feature in FEATURES:
        name = f"{feature}.tf"
        local = directory / name
        if not local.is_file():
            raise FileNotFoundError(f"Missing feature {local}")
        actual = hashlib.sha256(local.read_bytes()).hexdigest()
        verified = audit["data_checks"]["complete_utf8_features"][name]
        if actual != verified["sha256"]:
            raise ValueError(f"{name} does not match the pinned SHA-256")
        result[name] = actual
    return result


def load_geometry(directory, features):
    node_types = features["otype"]
    word_slots = sum(kind == "word" for kind in node_types.values())
    book_order = [features["book"][node] for node, kind in node_types.items() if kind == "book"]
    if word_slots != 426590 or len(book_order) != 39:
        raise ValueError("Unexpected BHSA inventory")

    section = [None] * (word_slots + 1)
    phrases = {}
    clauses = {}
    geometry = Counter()
    for node, specification in feature_rows(directory, "oslots", edge=True):
        level = node_types[node]
        if level == "chapter":
            name = features["book"][node]
            chapter = int(features["chapter"][node])
            location = (name, chapter)
            for slot in expand_nodes(specification):
                if section[slot] is not None:
                    raise ValueError(f"Duplicate chapter for slot {slot}")
                section[slot] = location
            geometry["chapters"] += 1
        elif level == "clause" and features["txt"][node] in TEXT_TYPES:
            clauses[node] = tuple(expand_nodes(specification))
        elif level == "phrase" and features["function"][node] in FUNCTIONS:
            phrases[node] = tuple(expand_nodes(specification))

    if any(location is None for location in section[1:]):
        raise ValueError("A word slot is outside the chapter index")
    geometry["word_slots"] = word_slots
    geometry["books"] = len(book_order)
    geometry["clauses_with_target_codes"] = len(clauses)
    geometry["subj_or_pred_phrase_nodes"] = len(phrases)
    return book_order, section, clauses, phrases, geometry


def link_phrases(directory, clauses, phrases):
    by_clause = defaultdict(list)
    checks = Counter()
    matched = set()
    for subject_or_pred, specification in feature_rows(directory, "functional_parent", edge=True):
        if subject_or_pred not in phrases:
            continue
        if subject_or_pred in matched:
            raise ValueError(f"Duplicate functional_parent at {subject_or_pred}")
        matched.add(subject_or_pred)
        parents = tuple(expand_nodes(specification))
        if len(parents) != 1:
            checks["not_one_functional_parent"] += 1
            continue
        parent = parents[0]
        if parent not in clauses:
            checks["parent_outside_target_clauses"] += 1
            continue
        if not set(phrases[subject_or_pred]).issubset(clauses[parent]):
            checks["not_contained_in_parent"] += 1
            continue
        by_clause[parent].append(subject_or_pred)
        checks["linked_to_target_clause"] += 1
    checks["missing_functional_parent"] = len(phrases) - len(matched)
    if sum(checks.values()) != len(phrases):
        raise ValueError("Inconsistent phrase-parent counts")
    return by_clause, checks


def extract_counts(features, section, clauses, phrases, by_clause, book_order):
    stages = {book: {code: Counter() for code in TEXT_TYPES} for book in book_order}
    forms = {book: {code: defaultdict(Counter) for code in TEXT_TYPES} for book in book_order}
    chapter_perf = {book: defaultdict(lambda: defaultdict(Counter)) for book in book_order}
    for node, slots in clauses.items():
        book, chapter = section[slots[0]]
        if any(section[slot][0] != book for slot in slots):
            raise ValueError(f"Clause crosses book boundary: {node}")
        code = features["txt"][node]
        rows = stages[book][code]
        rows["clauses"] += 1
        if any(features["language"][slot] != "Hebrew" for slot in slots):
            continue
        rows["all_hebrew"] += 1
        members = defaultdict(list)
        for phrase in by_clause[node]:
            members[features["function"][phrase]].append(phrases[phrase])
        if len(members["Subj"]) != 1 or len(members["Pred"]) != 1:
            continue
        rows["one_subj_one_pred"] += 1
        subject, = members["Subj"]
        predicate, = members["Pred"]
        verbs = [slot for slot in predicate if features["sp"][slot] == "verb"]
        if len(verbs) != 1:
            continue
        rows["one_verb"] += 1
        verb, = verbs
        if max(subject) < verb:
            order = "before"
        elif min(subject) > verb:
            order = "after"
        else:
            rows["interleaved"] += 1
            continue
        rows[order] += 1
        form = features["vt"][verb]
        forms[book][code][form][order] += 1
        if form == "perf" and code in ("N", "NQ"):
            chapter_perf[book][chapter][code][order] += 1
            if any(section[slot][1] != chapter for slot in slots):
                rows["perf_crosses_chapter"] += 1
    return stages, forms, chapter_perf


def count(cells, codes, form=None):
    total = Counter()
    for code in codes:
        if form is None:
            for orders in cells[code].values():
                total.update(orders)
        else:
            total.update(cells[code].get(form, {}))
    return total


def contrast(narrative, quotation):
    ns = narrative.get("before", 0)
    qs = quotation.get("before", 0)
    nn = ns + narrative.get("after", 0)
    qn = qs + quotation.get("after", 0)
    difference = 100 * (qs * nn - ns * qn) / (nn * qn) if nn and qn else None
    return {"N_before": ns, "N_total": nn, "NQ_before": qs, "NQ_total": qn,
            "NQ_minus_N_pp": round(difference, 8) if difference is not None else None}


def by_form(cells, codes):
    narrative, quotation = codes
    vocabulary = sorted({form for code in (*narrative, *quotation) for form in cells[code]})
    return {
        "all": contrast(count(cells, narrative), count(cells, quotation)),
        "forms": {form: contrast(count(cells, narrative, form), count(cells, quotation, form))
                  for form in vocabulary},
    }


def chapter_check(chapters):
    n_total = Counter()
    q_total = Counter()
    for codes in chapters.values():
        n_total.update(codes.get("N", {}))
        q_total.update(codes.get("NQ", {}))
    per_chapter = {str(chapter): contrast(codes.get("N", {}), codes.get("NQ", {}))
                   for chapter, codes in sorted(chapters.items())}
    leave_one_out = {}
    for chapter, codes in sorted(chapters.items()):
        n_without = n_total - Counter(codes.get("N", {}))
        q_without = q_total - Counter(codes.get("NQ", {}))
        leave_one_out[str(chapter)] = contrast(n_without, q_without)["NQ_minus_N_pp"]
    available = [value for value in leave_one_out.values() if value is not None]
    return {"perf_by_chapter": per_chapter,
            "leave_one_chapter_out_pp": leave_one_out,
            "range_pp": [min(available), max(available)] if available else None,
            "comparable_omissions": len(available)}


def summarize_books(books, comparisons):
    def perf_delta(book):
        return comparisons[book]["strict"]["forms"]["perf"]["NQ_minus_N_pp"]

    return {
        "books": books,
        "perf_quotation_higher": sum(perf_delta(book) > 0 for book in books),
        "perf_narrative_higher": sum(perf_delta(book) < 0 for book in books),
        "perf_ties": sum(perf_delta(book) == 0 for book in books),
        "reversals_like_genesis": sum(
            comparisons[book]["strict"]["all"]["NQ_minus_N_pp"] > 0 and perf_delta(book) < 0
            for book in books
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("feature_directory", type=Path, help="Path to pinned BHSA tf/2021")
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("results.json"))
    args = parser.parse_args()
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    file_hashes = verify_files(args.feature_directory, audit)
    features = {name: dict(feature_rows(args.feature_directory, name))
                for name in FEATURES if name not in {"oslots", "functional_parent"}}
    book_order, section, clauses, phrases, geometry = load_geometry(args.feature_directory, features)
    by_clause, parent_checks = link_phrases(args.feature_directory, clauses, phrases)
    stages, forms, chapters = extract_counts(features, section, clauses, phrases, by_clause, book_order)

    comparisons = {}
    for book in book_order:
        for code, stage in stages[book].items():
            if stage["one_verb"] != stage["before"] + stage["after"] + stage["interleaved"]:
                raise ValueError(f"Invalid eligible counts: {book}, {code}")
            observed = count(forms[book], [code])
            if any(stage[order] != observed[order] for order in ("before", "after")):
                raise ValueError(f"Invalid verb-form totals: {book}, {code}")
        comparisons[book] = {
            "strict": by_form(forms[book], STRICT),
            "include_unknown_outer": by_form(forms[book], INCLUDE_UNKNOWN_OUTER),
            "counts_by_txt": {code: dict(row) for code, row in stages[book].items()},
        }
    genesis = audit["word_order_check"]
    replay = comparisons[ANCHOR]["strict"]
    for group in ("N", "NQ"):
        old = genesis["counts_by_txt"][group]
        if (replay["all"][f"{group}_total"], replay["all"][f"{group}_before"]) != (
            old["ordered"], old["subject_before_verb"]
        ):
            raise ValueError(f"Genesis does not reproduce the previous audit for {group}")
        old_forms = genesis["order_by_tense_mood_and_txt"][group]
        for form, row in replay["forms"].items():
            prior = old_forms.get(form, {})
            if (row[f"{group}_total"], row[f"{group}_before"]) != (
                sum(prior.values()), prior.get("subject_before_verb", 0)
            ):
                raise ValueError(f"Genesis does not reproduce {group}, {form}")

    def eligibility(book):
        row = comparisons[book]["strict"]["forms"].get("perf", {})
        n, q = row.get("N_total", 0), row.get("NQ_total", 0)
        return {"book": book, "perf_N": n, "perf_NQ": q, "smaller_group": min(n, q)}

    ranked = sorted((eligibility(book) for book in book_order if book != ANCHOR),
                    key=lambda r: (-r["smaller_group"], -(r["perf_N"] + r["perf_NQ"])))
    chosen = [r["book"] for r in ranked if r["smaller_group"] > 0][:FOLLOWUP_COUNT]
    coverage = [r["book"] for r in ranked if r["smaller_group"] >= COVERAGE_FLOOR]
    for book in (ANCHOR, *dict.fromkeys(chosen + coverage)):
        comparisons[book]["strict_perf_chapter_check"] = chapter_check(chapters[book])

    report = {
        "resource_id": "R195",
        "dataset_version": "BHSA 2021, v1.8.1",
        "source_commit": PIN,
        "checked_on": "2026-11-16",
        "input_sha256": file_hashes,
        "unit": "Hebrew clause with one Subj phrase and one Pred phrase, with exactly one word slot tagged verb in Pred",
        "order": "the entire Subj precedes or follows the verb slot; exclude overlap or interleaving",
        "strict_txt": {"narrative": ["N"], "quotation": ["NQ"]},
        "sensitivity_txt": {"narrative": ["N", "?N"], "quotation": ["NQ", "?NQ"]},
        "difference_pp": "quotation minus narrative in percentage points",
        "anchor": ANCHOR,
        "anchor_matches_previous": True,
        "selection_rule": "Five non-Genesis books sorted by smaller strict perf group, then total perf sample; canonical BHSA order resolves remaining ties. No word-order outcome enters ranking.",
        "ranked_eligibility": ranked,
        "geometry": dict(geometry),
        "phrase_links": dict(parent_checks),
        "primary_followups": summarize_books(chosen, comparisons),
        "coverage_check": {"minimum_per_group": COVERAGE_FLOOR, **summarize_books(coverage, comparisons)},
        "comparisons": comparisons,
    }
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
