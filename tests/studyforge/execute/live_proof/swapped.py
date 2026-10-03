"""The shipped proxy with its one guard swapped, so a stand-in on a private bridge is reachable."""

import egress

egress.public = lambda address: True
egress.run()
