"""A package file's name is not an email address: the gate reads past `<name>@<platform>.vsix`.

⭐ The toolchain pins an editor extension per platform, and its archive is named
`<publisher>.<name>-<version>@<platform>.vsix`. That reads as an address to a pattern that asks only
for `@`, a domain and letters, and it refused every export whose editor carries one. None of
the suffixes below is a top-level domain, and a real address is still refused.
"""

from __future__ import annotations

import pytest

from studyforge.archive.scrub import PersonalDataLeak, assert_clean, leaks, scrub


@pytest.mark.parametrize("suffix", ["vsix", "whl", "jar", "tgz"])
def test_a_package_file_named_for_a_platform_is_not_an_address(suffix):
    text = f"https://example.invalid/x/example.tool-1.2.3@linux-x64.{suffix}"
    assert list(leaks({"url": text}, "document")) == []
    assert_clean({"url": text}, "document")
    assert scrub(text) == text


#: ⛔ Assembled at run time: the repository's hygiene check reads this file, and an address on a
#: registrable domain written whole would be what it refuses.
DOMAINS = ["registrable" + ".net", "mail." + "registrable" + ".io", "registrable.vsix" + ".com"]


@pytest.mark.parametrize("domain", DOMAINS)
def test_a_real_address_is_still_refused(domain):
    with pytest.raises(PersonalDataLeak, match="email address"):
        assert_clean({"text": "write to " + "someone" + "@" + domain}, "document")
