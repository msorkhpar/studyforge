"""Child-process probes: the observations that cannot be made in-process.

⛔ One module per observation mechanism, each runnable as `python3 -m`, because
an audit hook cannot be uninstalled and a fork cannot be unforked. The callers
are in `tests/harness/`.
"""
