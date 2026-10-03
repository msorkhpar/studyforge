"""Full-text plants gate, build and write byte-for-byte as they did before spec plants existed.

⭐ Each digest below was taken over every file `gate_code` would commit (paths, bytes and the
gate record last) with the build that had no spec plants, for the draft named. A change in
how a full plant is stored, digested or recorded moves one of them.
"""

from __future__ import annotations

import hashlib

import pytest

from studyforge.skills.exercises import gate_code
from tests.studyforge.skills.exercises import node_practice as node
from tests.studyforge.skills.exercises import pytest_practice as pytest_draft
from tests.studyforge.skills.exercises.authoring import Running, basket, greeting, shout
from tests.studyforge.skills.exercises.test_pytest_practice import _brief

GOLDEN = {
    "basket": ("9", "7bf5645ebe8e89655974f85fc16d495e6cbfc375e6b30cb17bf7616104c07e15"),
    "shout": ("9", "f44b90f087e6b4c66e958ed03bccf5afc963395f219effd23ca651b329e3e586"),
    "greeting": ("9", "f73e5ff692c5cf3bb45613d3bca42f099c61d18a51fa882fa8a6157a5443e9fc"),
    "node": ("13", "153e14975afcec666185bc7cdc34145d9b63dd78e46be389320ce7da070a181f"),
    "pytest": ("11", "c9c9ad1883db1ca710b7afabcb6f1fe553b9a7c5d1b794e09d5885a69d8ac741"),
}
DRAFTS = {
    "basket": basket,
    "shout": shout,
    "greeting": greeting,
    "node": node.draft,
    "pytest": pytest_draft.draft,
}


@pytest.mark.parametrize("name", sorted(GOLDEN))
def test_a_full_plant_draft_commits_the_bytes_it_always_did(tmp_path, name):
    brief, ledger = _brief(tmp_path)
    gated = gate_code(DRAFTS[name](brief), brief, ledger, Running(), source="demo", where="w")
    digest = hashlib.sha256()
    for path, data in gated.files:
        digest.update(path.encode() + b"\0" + data)
    assert gated.clears
    assert (str(len(gated.files)), digest.hexdigest()) == GOLDEN[name]
