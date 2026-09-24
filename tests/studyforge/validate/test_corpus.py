"""Walking a corpus on disk, and refusing rather than raising.

⭐ **The rule this module exists to hold: a refusal met while reading is a
finding, not an exception.** `validate` reports every problem in one run (R6),
so a container map that will not parse must not stop the twelve documents
beside it from being read — and a document that *was* refused must not then be
reported a second time as an absence.
"""

import json

from studyforge.corpus.placement import ARCHIVE_DIRNAME as ARCHIVE_DIR
from studyforge.validate.corpus import UNIT_DIR, read
from tests.studyforge.validate import corpora


def walk(root):
    return read(root)


# --------------------------------------------------------------------------
# what one pass reads
# --------------------------------------------------------------------------


def test_a_walk_reads_the_manifest_the_containers_and_the_documents(tmp_path):
    result = walk(corpora.one_unit(tmp_path / "c"))
    assert result.manifest is not None
    assert len(result.containers) == 1
    assert len(result.units) == 1
    assert result.findings == []


def test_a_corpus_with_no_manifest_stops_there_and_says_so(tmp_path):
    root = corpora.one_unit(tmp_path / "c")
    (root / "corpus.json").unlink()
    result = walk(root)
    assert result.manifest is None
    assert result.containers == []
    assert [f.rule for f in result.findings] == ["unreadable"]


def test_a_manifest_that_is_not_json_is_a_finding_not_an_exception(tmp_path):
    root = corpora.one_unit(tmp_path / "c")
    (root / "corpus.json").write_text("{not json", encoding="utf-8")
    result = walk(root)
    assert result.manifest is None
    assert [f.rule for f in result.findings] == ["manifest"]


def test_a_file_that_is_not_utf8_is_named_rather_than_raised(tmp_path):
    root = corpora.one_unit(tmp_path / "c")
    (root / "corpus.json").write_bytes(b"\xff\xfe not text")
    result = walk(root)
    assert [f.rule for f in result.findings] == ["unreadable"]
    assert "is not UTF-8 text" in result.findings[0].message


# --------------------------------------------------------------------------
# ⛔ where is workspace-relative, always
# --------------------------------------------------------------------------


def test_every_where_is_relative_to_the_root_and_never_the_path_given(tmp_path):
    # ⛔ R7: an absolute path in a report is personal data in a log, and a
    # report is the most-pasted artifact this tool produces.
    root = corpora.one_unit(tmp_path / "c")
    result = walk(root)
    for where in [h.where for h in result.containers] + [u.where for u in result.units]:
        assert not where.startswith("/")
        assert str(root) not in where
    assert result.containers[0].where == f"{ARCHIVE_DIR}/demo/container.json"


def test_relative_falls_back_to_the_name_for_a_path_outside_the_root(tmp_path):
    result = walk(corpora.one_unit(tmp_path / "c"))
    assert result.relative(tmp_path / "elsewhere" / "x.json") == "x.json"


# --------------------------------------------------------------------------
# ⭐ a refusal does not stop the walk, and it does not vanish either
# --------------------------------------------------------------------------


def test_a_container_that_will_not_parse_does_not_stop_the_others(tmp_path):
    root = corpora.two_containers(tmp_path / "c")
    (root / ARCHIVE_DIR / "other" / "container.json").write_text("{nope", encoding="utf-8")
    result = walk(root)
    assert len(result.containers) == 1
    assert [f.rule for f in result.findings] == ["container"]


def test_and_the_documents_beneath_it_are_recorded_as_refused_not_as_absent(tmp_path):
    # ⭐ **One defect must not become two findings.** The container's own file
    # is recorded in `refused`, and `run` turns that into an unchecked claim —
    # so a downstream check reports "could not judge" rather than "missing".
    root = corpora.two_containers(tmp_path / "c")
    (root / ARCHIVE_DIR / "other" / "container.json").write_text("{nope", encoding="utf-8")
    result = walk(root)
    assert len(result.refused) == 1
    assert result.refused[0].container is None


def test_a_document_that_will_not_parse_is_refused_and_named(tmp_path):
    root = corpora.one_unit(tmp_path / "c")
    (root / ARCHIVE_DIR / "demo/raw/prose/unit-01/lesson-1.json").write_text(
        "{nope", encoding="utf-8"
    )
    result = walk(root)
    assert result.units == []
    assert len(result.refused) == 1
    assert [f.rule for f in result.findings] == ["document"]


def test_a_refused_document_still_knows_which_unit_it_claimed(tmp_path):
    # ⚠️ The ordinal comes from the **directory name**, which is readable even
    # when the content is not. Location is data (R4), so it is still
    # information when identity has been refused.
    root = corpora.one_unit(tmp_path / "c")
    (root / ARCHIVE_DIR / "demo/raw/prose/unit-01/lesson-1.json").write_text(
        "{nope", encoding="utf-8"
    )
    assert walk(root).refused[0].unit == 1


def test_a_document_the_personal_data_gate_refuses_is_recorded_too(tmp_path):
    # ⭐ The gate refuses a document, and a downstream check must not then
    # report the unit *missing* — that is one defect wearing two names.
    root = corpora.one_unit(tmp_path / "c")
    path = root / ARCHIVE_DIR / "demo/raw/prose/unit-01/lesson-1.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    document["source"] = "ingested from " + "/" + "home/jane/corpus"
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    result = walk(root)
    assert [f.rule for f in result.findings] == ["personal-data"]
    assert len(result.refused) == 1
    assert result.refused[0].unit == 1


def test_a_container_map_carrying_a_home_path_is_filed_as_personal_data_too(tmp_path):
    # ⭐ The third arm, asserted so *"is it reachable?"* is answered by a test
    # rather than by reading `container/errors.py` and believing it.
    # `corpus/container/document.py` calls `assert_clean` bare and never
    # translates, so this arm is live — and the only way to know that without
    # guessing is to drive it.
    root = corpora.one_unit(tmp_path / "c")
    path = root / ARCHIVE_DIR / "demo/container.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    document["titles"] = ["Notes from " + "/" + "home/jane/corpus"]
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    result = walk(root)
    assert [f.rule for f in result.findings] == ["personal-data"]
    assert "jane" not in result.findings[0].message


def test_a_manifest_carrying_a_home_path_is_filed_as_personal_data_not_as_a_manifest_defect(
    tmp_path,
):
    # ⛔ **The personal-data arm, reachable.** `_manifest` catches
    # `ManifestError` and **then** `PersonalDataLeak`. If
    # `corpus/manifest/document._gate` translated the leak into
    # `ManifestError`, the first arm would always win and a home path in
    # `corpus.json`, the single loudest thing R7 exists to catch, would be
    # filed under `manifest`: an R7 leak reported as a formatting defect.
    #
    # ⚠️ **So the rule is asserted, not only that a finding was raised**:
    # `['manifest']` would be the translated reading, `['personal-data']` is
    # the right one.
    #
    # ⛔ The manifest is poisoned after the corpus is built, because
    # `corpora.write` parses what it writes and the gate would refuse it there.
    root = corpora.one_unit(tmp_path / "c")
    path = root / "corpus.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    document["title"] = "Notes from " + "/" + "home/jane/corpus"
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    result = walk(root)
    assert [f.rule for f in result.findings] == ["personal-data"]
    # ⛔ The finding names the shape and never the value (R7).
    assert "home path" in result.findings[0].message
    assert "jane" not in result.findings[0].message
    # ⚠️ And the walk still stops there, as it does for any unreadable
    # manifest: there is no corpus to walk without one.
    assert result.manifest is None


def test_a_unit_directory_that_is_not_named_unit_nn_claims_no_ordinal(tmp_path):
    assert UNIT_DIR.match("unit-01") is not None
    assert UNIT_DIR.match("unit-1") is None
    assert UNIT_DIR.match("lesson-01") is None


# --------------------------------------------------------------------------
# one reader, one answer
# --------------------------------------------------------------------------


def test_the_walk_reads_each_file_exactly_once(tmp_path, monkeypatch):
    # ⛔ A check never opens a file itself: one reader means one answer to
    # "what is in this corpus", and a second walk is a second answer.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    opened: list[str] = []
    original = type(root).read_text

    def counted(self, *args, **kwargs):
        opened.append(self.name)
        return original(self, *args, **kwargs)

    monkeypatch.setattr(type(root), "read_text", counted)
    walk(root)
    assert sorted(opened) == ["container.json", "corpus.json", "lesson-1.json"]


def test_a_container_map_at_the_wrong_depth_is_a_container_finding_not_an_exception(tmp_path):
    # ⛔ `AddressError` from the arity comparison, a member of the reader's
    # `RAISES` that is not the leak: it is filed under `container`.
    root = corpora.one_unit(tmp_path / "c")
    path = root / ARCHIVE_DIR / "demo/container.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    document.update(address=["demo", "extra"], titles=["Demo", "Extra"])
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    result = walk(root)
    assert [f.rule for f in result.findings] == ["container"]
    assert "level(s)" in result.findings[0].message
