"""Run k11 Integration QA's demo flows against K11 Shop on the in-process broker.

The demo broker (type: memory) only works when the shop runs in the same process as the flows,
so this script starts the shop, runs the flows, and stops the shop.

  cd k11techlab-integration-qa-mcp/demo/shop
  python <path>/run_integration_demo.py --bugs consumer,dlq,job    # every flow should fail
  python <path>/run_integration_demo.py                            # every flow should pass

The report is written to .qa-mcp/integration-report/ in the current folder.
"""
import argparse
import os
import sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--bugs", default="", help="comma-separated: consumer, dlq, job (default: none)")
ap.add_argument("--db", default="shop.db", help="SQLite file; must match .qa-mcp/api-test.yaml and integration.yaml")
args = ap.parse_args()

here = Path.cwd()
sys.path.insert(0, str(here))
from shop import Shop  # noqa: E402  (demo/shop/shop.py)

from k11_integration_qa.brokers import MemoryBroker  # noqa: E402
from k11_integration_qa.run import run  # noqa: E402

MemoryBroker.reset()
os.environ["SHOP_BUGS"] = args.bugs  # the batch job reads it too
shop = Shop(0, here / args.db, args.bugs, None)
os.environ["SHOP_URL"] = shop.url
try:
    run(here)
finally:
    shop.close()
print("Report: .qa-mcp/integration-report/")
