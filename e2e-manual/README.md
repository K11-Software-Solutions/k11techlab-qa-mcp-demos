# Testing a system end to end with the K11 QA MCPs

A hands-on manual for testing one system at every layer with five K11 QA tools, from Claude Code or the
command line. Every example on this page is the output of a real run, stored in [examples/](examples/).

| Layer | Tool | Version | Asks first with | Slash command |
|---|---|---|---|---|
| Web UI | [k11 Playwright QA](https://github.com/K11-Software-Solutions/k11techlab-playwright-qa-mcp) | 0.4.1 | `review_user_story` | `/playwright-qa:story-to-test` |
| Web UI | [k11 Selenium QA](https://github.com/K11-Software-Solutions/k11techlab-selenium-qa-mcp) | 0.3.1 | `review_user_story` | `/selenium-qa:story-to-test` |
| API | [k11 API Functional QA](https://github.com/K11-Software-Solutions/k11techlab-api-functional-qa-mcp) | 0.2.2 | `review_user_story` | `/api-functional-qa:api-story-test` |
| Events, consumers, batch jobs | [k11 Integration QA](https://github.com/K11-Software-Solutions/k11techlab-integration-qa-mcp) | 0.2.0 | `review_flow_plan` | `/integration-qa:integration-check` |
| Load and latency | [k11 Performance QA](https://github.com/K11-Software-Solutions/k11techlab-performance-qa-mcp) | 0.2.0 | `review_perf_plan` | `/performance-qa:perf-check` |

Contents:

1. [The idea: one story, five layers](#1-the-idea-one-story-five-layers)
2. [Set up](#2-set-up)
3. [Step 0: ask before you build](#3-step-0-ask-before-you-build)
4. [Web UI: Playwright and Selenium](#4-web-ui-playwright-and-selenium)
5. [API: functional flows with database checks](#5-api-functional-flows-with-database-checks)
6. [Integration: events, consumers, dead letters and batch jobs](#6-integration-events-consumers-dead-letters-and-batch-jobs)
7. [Performance: SLOs and regressions](#7-performance-slos-and-regressions)
8. [Which layer catches which bug](#8-which-layer-catches-which-bug)
9. [Run it in CI](#9-run-it-in-ci)
10. [Rules that keep the results honest](#10-rules-that-keep-the-results-honest)
11. [Troubleshooting](#11-troubleshooting)
12. [Reproduce the examples](#12-reproduce-the-examples)

---

## 1. The idea: one story, five layers

A shopper places an order. That one action crosses every layer of a typical system:

```text
 browser ──► web UI ──► order API ──► database
                            │
                            └──► orders.events ──► inventory consumer ──► database
                                                        │
                                       unreadable ──► orders.dlq
                                                        │
                            nightly batch job ◄─────────┘   (sku_totals)
 ...and all of it under load during a sale.
```

Each layer fails in its own way, and each test layer can only see its own failures. A UI test sees the
confirmation page, not the stock reservation. An API test sees the `201`, not the consumer that reserved
one item instead of three. A load test sees latency, not wrong totals. So you test the same story at
every layer, with the tool built for that layer:

| Question | Layer | Tool |
|---|---|---|
| Can a person complete the journey in a browser? | Web UI | Playwright QA or Selenium QA |
| Does each API call return and store the right data? | API | API Functional QA |
| Do the events, consumers, dead-letter queue and jobs do their part? | Integration | Integration QA |
| Does it stay fast and error-free under the expected load? | Performance | Performance QA |

All five tools share one habit: **they ask before they build.** Before writing a test, each one reviews
the story for what a careful tester would ask, stops, and waits for your answers. Nothing is guessed: not
a status code, not a time limit, not an SLO.

## 2. Set up

You need [uv](https://docs.astral.sh/uv/) (for the Python tools), Node.js 18+ (for Playwright QA), and
Claude Code for the slash commands.

**In Claude Code**, add each tool as a plugin:

```text
/plugin marketplace add K11-Software-Solutions/k11techlab-playwright-qa-mcp
/plugin install playwright-qa@k11-qa-tools

/plugin marketplace add K11-Software-Solutions/k11techlab-selenium-qa-mcp
/plugin install selenium-qa@k11-selenium-qa

/plugin marketplace add K11-Software-Solutions/k11techlab-api-functional-qa-mcp
/plugin install api-functional-qa@k11-api-functional-qa

/plugin marketplace add K11-Software-Solutions/k11techlab-integration-qa-mcp
/plugin install integration-qa@k11-integration-qa

/plugin marketplace add K11-Software-Solutions/k11techlab-performance-qa-mcp
/plugin install performance-qa@k11-performance-qa
```

Each plugin starts its server with `npx -y` or `uvx`, so every tool runs in its own environment.

**On the command line or in CI**, give each Python tool its own environment too:

```powershell
uvx k11-api-functional-qa-mcp --version
uvx k11-performance-qa-mcp --version
uvx --from "k11-integration-qa-mcp[kafka]" k11-integration-qa-mcp --version
```

> **Don't install them all into one virtual environment.** Performance QA 0.2.0 and Integration QA 0.2.0
> require `k11-api-functional-qa-mcp<0.2`. In a shared environment, pip or uv quietly downgrades API
> Functional QA to 0.1.1, which has no `review_user_story`. Separate environments (`uvx`, or one venv per
> tool) avoid this.

## 3. Step 0: ask before you build

Start every layer with the review. Here is the same vague story given to all five review tools
([examples/shared-story/](examples/shared-story/)):

```text
As a shopper, I want to place an order and get a confirmation quickly.
- The order is saved and the stock is reserved eventually
- An order that can't be fulfilled is rejected
- Checkout handles heavy load during sales
```

Every tool returned `ready: false`. Each one asked about "quickly", and each added the questions its own
layer needs answered:

| Tool | Questions | What it asked |
|---|---:|---|
| Playwright QA | 1 | **vague term:** "quickly" can't be tested as written. What is the measurable version? |
| Selenium QA | 1 | The same question: the UI tools share one rule set. |
| API Functional QA | 3 | "quickly", plus **error contract:** which status code and error body should a rejected order return (400 or 422, which error code)? And **access:** what happens without credentials, or with another user's IDs (401, 403 or 404)? |
| Integration QA | 2 | "quickly", plus **time limit:** how long may the reservation take at most? "eventually" is not a time limit. |
| Performance QA | 7 | No SLOs (which percentile, how many ms, what error rate), no load profile (otherwise the default of 5 users would run), no duration or ramp-up, "quickly" and "heavy load" have no numbers, what test data, and how the environment compares with production. |

The layers don't repeat each other's questions. The API tool doesn't ask about load, and the performance
tool doesn't ask about status codes. Between them, the five reviews show what the story leaves unsaid.

**What you do next:** answer the questions in the story itself, as acceptance criteria or Given/When/Then
lines, and run the review again until it says `ready: true`. For example:

```gherkin
Scenario: an order that can't be fulfilled
  Given SKU HAT-2 has 0 in stock
  When I POST /orders for 1 x HAT-2
  Then I get HTTP 409 with error "out_of_stock"
  And no order row is stored
Scenario: stock is reserved
  When I place an order for 3 x BAG-1
  Then within 10 seconds the inventory shows 3 reserved
```

For load tests, write the answers where the review reads them, in `.qa-mcp/perf.yaml`:

```yaml
slos:
  "POST /orders": { p95_ms: 400, error_rate: 0.01 }
profile: { vus: 200, duration: 10m, ramp_up: 2m }
plan:                      # where the numbers come from (read by review_perf_plan)
  peak: "Black Friday 2025 analytics: 180 concurrent checkouts at the busiest minute"
  duration: "10 minutes at peak after a 2-minute ramp, long enough for caches to settle"
  test_data: "20,000 products and one customer per virtual user, so no two users share IDs"
  environment_size: "Staging is half of production: 2 app instances instead of 4, same database class"
```

**Going ahead anyway:** if you tell the agent to continue with questions still open, it writes each one
into the test as an `OPEN QUESTION:` comment next to the step it affects, and lists them in its report.
It never fills a gap with a guess.

## 4. Web UI: Playwright and Selenium

Use one of the two, whichever your project already uses. Both turn a story into a test the same way:

1. `review_user_story`: questions first (section 3).
2. `parse_user_story`: scenarios and a test skeleton.
3. `explore_page`: locators verified against the live page. The agent never guesses a locator.
4. `write_test`, then `run_tests`. If a UI change breaks a locator later, `heal_locator` fixes it with an audit trail.
5. `capture_baseline`: locator fingerprints for future healing.

```text
/playwright-qa:story-to-test https://demo.playwright.dev/todomvc As a visitor, I want to add and complete to-do items so that I can track my tasks.
Precondition: none, the page is public and starts with an empty list.
- Typing "Buy milk" in the "What needs to be done?" box and pressing Enter adds "Buy milk" to the list
- ...
```

The full inputs are in [inputs/](../inputs/README.md). Results from this repo:

| Story | Playwright QA | Selenium QA |
|---|---|---|
| TodoMVC, 5 acceptance criteria | **5/5 pass** in 5.5 s: [todo-items.spec.ts](../playwright/tests/todo-items.spec.ts) | **5/5 pass** in 26 s: [test_todo_items.py](../selenium/tests/test_todo_items.py) |
| Sauce Demo checkout behind a login, 4 acceptance criteria | not run | **4/4 pass** in 28 s: [test_buy_backpack.py](../selenium/tests/test_buy_backpack.py) |

Sign-ins use environment variables only. The story says *"sign in with the username in env SAUCE_USER
and the password in env SAUCE_PASSWORD"*, and the test reads `os.environ`. The values never appear in a
prompt, a tool argument or a file.

**What this layer proves:** a person can complete the journey, and the page shows the right result.
**What it can't see:** what the API stored, which events were published, or how it behaves under load.

## 5. API: functional flows with database checks

API Functional QA writes multi-step flows in YAML. It chains calls by saving IDs, checks values (not just
status codes), and checks the database after each call that changes data.

The demo shop in the tool's repo has two planted bugs. This flow catches the first
(`demo/shop/tests/api/order_total.yaml`):

```yaml
name: Order total is quantity times price
fixtures: [customer]
steps:
  - name: place an order for two bags
    call: POST /orders
    body: { customerId: "${fixture.customer.id}", channel: mobile, items: [{ sku: BAG-1, qty: 2 }] }
    expect:
      status: 201
      json: { "$.total": 85.0, "$.items[0].qty": 2 }
    save: { orderId: "$.id" }

  - name: the database stores 85.00
    db: SELECT total FROM orders WHERE id = :orderId
    params: { orderId: "${orderId}" }
    expect: { rows: 1, row: { total: 85.0 } }

  - name: order history shows 85.00
    call: GET /orders
    query: { customerId: "${fixture.customer.id}" }
    expect: { status: 200, json: { "$[0].total": 85.0 } }
```

Run it ([full report](examples/api-functional/api-test-report.md)):

```bash
git clone https://github.com/K11-Software-Solutions/k11techlab-api-functional-qa-mcp
cd k11techlab-api-functional-qa-mcp/demo/shop
python server.py --port 8080 &
SHOP_URL=http://127.0.0.1:8080 SHOP_TOKEN=test-token QA_MCP_ROOT=. uvx k11-api-functional-qa-mcp run
```

```text
1/2 flows passed (1 failed, 0 blocked, 0 errors, 0 server errors).

❌ Order total is quantity times price
- place an order for two bags: failed
  - response: HTTP 201 in 6 ms
  - ✗ $.total 85.0: expected 85.0, got 42.5
```

The other steps passed: the database stores 85.00, and order history shows 85.00. So the bug is in one
place only, the `POST /orders` response. A UI test that reads the order history page would pass.

More from this tool:

- `generate_negative_tests("POST /orders")` builds missing-field, wrong-type, out-of-range and
  no-credentials cases from the spec. Each one must get a 4xx, never a 5xx. On the demo it finds the
  second bug: `qty` sent as text crashes the server with a 500.
- `export_pytest` turns any flow into plain pytest and httpx code.
- Reports come as Markdown (for a PR comment), JSON and JUnit XML.

**What this layer proves:** each call returns and stores the right data, including the failure cases.
**What it can't see:** what happens after the response, in consumers and jobs.

## 6. Integration: events, consumers, dead letters and batch jobs

The API returned 201. Did the consumer actually reserve the stock? Integration QA tests the whole chain in
one flow: the API call, the message on the topic, the consumer's effect in the database, the dead-letter
queue, and the batch job.

```yaml
name: An order reserves stock through the inventory consumer
fixtures: [sku]
steps:
  - listen: { broker: main, topic: orders.events, as: events }    # subscribe BEFORE acting
  - call: POST /orders
    body: { sku: "${fixture.sku.sku}", qty: 3 }
    expect: { status: 201 }
    save: { orderId: "$.id" }
  - name: OrderCreated is published and matches the AsyncAPI contract
    expect_message: { from: events, match: { "$.type": OrderCreated, "$.orderId": "${orderId}" }, schema: OrderCreated, within: 10s }
  - name: the inventory consumer reserves all 3
    expect_message: { from: events, match: { "$.type": StockReserved, "$.orderId": "${orderId}", "$.qty": 3 }, within: 10s }
  - name: the reservation is in the database
    wait_until:
      db: SELECT reserved FROM inventory WHERE sku = :sku
      params: { sku: "${fixture.sku.sku}" }
      expect: { row: { reserved: 3 } }
      within: 10s
```

And a poison message, which must go to the dead-letter queue with a reason instead of disappearing:

```yaml
name: An unreadable command goes to the dead-letter queue
steps:
  - listen: { broker: main, topic: orders.dlq, as: dlq }
  - name: publish a command that isn't JSON
    publish: { broker: main, topic: orders.commands, key: "${poisonKey}", value: "cancel order 42 please" }
  - name: it is dead-lettered with the reason
    expect_message: { from: dlq, match: { key: "${poisonKey}", "header:error": { exists: true } }, within: 10s }
```

The demo shop, K11 Shop, has three bugs you can switch on. Run the four demo flows with all of them on,
then with all of them off. Use [scripts/run_integration_demo.py](scripts/run_integration_demo.py), which
starts the shop in the same process as the flows. That's required for the in-memory demo broker; with
Kafka, the shop runs separately.

```bash
git clone https://github.com/K11-Software-Solutions/k11techlab-integration-qa-mcp
cd k11techlab-integration-qa-mcp/demo/shop
uv run --no-project --with "k11-integration-qa-mcp[kafka]" python <this repo>/e2e-manual/scripts/run_integration_demo.py --bugs consumer,dlq,job
```

Bugs on ([full report](examples/integration/integration-report-bugs-on.md)): **0 of 4 flows pass**, and
each failure says which part of the chain broke:

```text
❌ An order reserves stock through the inventory consumer
- the inventory consumer reserves all 3 (expect_message): failed
  - ✗ 0 of 1 matching message(s) within 10s (2 message(s) on orders.events); closest: $.qty: expected 3, got 1

❌ Cancelling an order releases its stock
- the stock is released (wait_until): failed
  - ✗ reserved 0: expected 0, got -1

❌ An unreadable command goes to the dead-letter queue
❌ The sku_totals batch job is safe to run twice
```

When nothing matches, the report shows the **closest message** and how it differed. So "the event never
came" and "the event came with the wrong quantity" are two different findings.

Bugs off ([full report](examples/integration/integration-report-bugs-off.md)): **4 of 4 flows pass**, with
2 messages published, 7 message checks and 2 job runs. A test suite is only trustworthy if it can fail
and pass on demand, so this is checked in both directions.

**What this layer proves:** the parts work together, including failure paths (dead letters) and
re-running a batch job safely. **What it can't see:** latency and errors under load.

## 7. Performance: SLOs and regressions

Performance QA replays your API flows as load: the same YAML files, weighted into scenarios. It reports
latency per endpoint against your SLOs, and against a baseline with a significance test, so random noise
isn't reported as a regression.

The demo's `.qa-mcp/perf.yaml`, with the `plan:` block that answers the review's questions:

```yaml
profile: { vus: 4, duration: 8s, ramp_up: 1s, think_time_ms: 20 }
scenarios:
  browse:
    flows:
      - { flow: tests/api/view_order.yaml, weight: 3 }
      - tests/api/cancel_order.yaml
slos:
  "GET /orders/{id}": { p95_ms: 250, error_rate: 0.01 }
  "*": { p95_ms: 800, error_rate: 0.02 }
regression: { metric: p95, tolerance_pct: 15, min_delta_ms: 15, min_samples: 30, p_value: 0.01 }
plan:
  peak: "Demo only: 4 users keep a laptop run under 10 seconds; a real project puts its analytics peak here"
  test_data: "Each virtual user creates its own customer and orders, so no two users share IDs"
```

Save a baseline, then simulate a bad release: `--slow-ms 80` makes `GET /orders/{id}` 80 ms slower.

```bash
git clone https://github.com/K11-Software-Solutions/k11techlab-performance-qa-mcp
cd k11techlab-performance-qa-mcp/demo/shop
export SHOP_URL=http://127.0.0.1:8080 SHOP_TOKEN=test-token
python server.py --port 8080 &
uvx k11-performance-qa-mcp baseline --scenario browse --engine builtin
# stop the server, restart it with --slow-ms 80, then:
uvx k11-performance-qa-mcp run --scenario browse --engine builtin
```

Result ([full report](examples/performance/perf-report-slow-release.md)):

```text
Performance: ❌ needs attention
480 requests at 57.62 req/s, error rate 0.00%, p95 118.0 ms

- regression: GET /orders/{id}: p95 77.4 → 131.2 ms (+69.5%, p=0.0000)

SLOs: 8/8 met.
```

**Every SLO still passed, and the release was still flagged.** The slowdown is real and significant, but
it hasn't crossed the 250 ms limit yet. Without a baseline it would ship unnoticed, and the next slowdown
would cross the limit. Only `GET /orders/{id}` was flagged; the other endpoints didn't get slower.

Notes:

- Use the same engine (`builtin` or `k6`) for the baseline and the runs compared with it.
- Database steps are skipped under load. They run in the API functional tests.
- Load is refused on production-like environments. Already using JMeter? `import FILE.jtl` compares
  JMeter results the same way.

**What this layer proves:** the system meets its SLOs at the expected load, and hasn't got slower than the
last good build. **What it can't see:** whether the answers are right. That's what the other layers are for.

## 8. Which layer catches which bug

The planted bugs from the demos, and the layer that catches each:

| Bug | UI | API | Integration | Performance |
|---|:-:|:-:|:-:|:-:|
| `POST /orders` returns the wrong total, but stores the right one | only if the page shows that response | **✅ caught** | | |
| Text in `qty` crashes the server with a 500 | | **✅ caught** (negative tests) | | |
| The consumer reserves 1 item whatever the quantity | | the 201 looks fine | **✅ caught** | |
| An unreadable command is dropped instead of dead-lettered | | | **✅ caught** | |
| Running the batch job twice doubles the totals | | | **✅ caught** | |
| `GET /orders/{id}` is 80 ms slower, still inside its SLO | | | | **✅ caught** (regression) |
| A locator breaks after a UI change | **✅ healed** (`heal_locator`, with an audit trail) | | | |

No single layer catches everything. That's why one story gets tested at all four.

## 9. Run it in CI

Run the layers in this order, cheapest first. Stop early if a lower layer fails:

```text
1. API functional flows      seconds     k11-api-functional-qa-mcp run
2. Integration flows         < 1 min     k11-integration-qa-mcp run --env ci   (with a Kafka service)
3. UI tests                  minutes     pytest / npx playwright test
4. Performance               minutes     k11-performance-qa-mcp run            (baseline saved on main)
```

Each tool writes machine-readable evidence (JSON and JUnit XML) next to its Markdown report. The
[k11 Release Gate](https://github.com/K11-Software-Solutions/k11techlab-release-gate-mcp) reads it and
makes one decision under a written policy: ship, ship with conditions, needs a person, or block. Each
repo has a ready-made workflow:

- API: the "In CI" section of the [API Functional QA README](https://github.com/K11-Software-Solutions/k11techlab-api-functional-qa-mcp#in-ci)
- Integration: [docs/integration-tests.yml](https://github.com/K11-Software-Solutions/k11techlab-integration-qa-mcp/blob/main/docs/integration-tests.yml)
- Performance: [docs/perf-tests.yml](https://github.com/K11-Software-Solutions/k11techlab-performance-qa-mcp/blob/main/docs/perf-tests.yml)
- UI: this repo's [demos workflow](../.github/workflows/demos.yml)

## 10. Rules that keep the results honest

The tools and their slash commands enforce these, and you should hold the agent to them:

- **Ask, don't guess.** No status code, time limit, SLO or locator is invented. Open questions are
  written down.
- **Never weaken a check to make it pass.** No longer time limits, looser matches, raised SLOs or a
  refreshed baseline to hide a regression. If the system is wrong, report it with the evidence.
- **A slow consumer is a finding, not a flaky test.**
- **Secrets only from environment variables** (`${ENV:NAME}` in YAML). They're masked in every report.
- **Production is off limits.** Data-changing calls, publishing, jobs and load are refused on
  production-like environments and protected topics.
- **Untested is not passing.** Each report lists what wasn't covered.

## 11. Troubleshooting

| Symptom | Cause and fix |
|---|---|
| A plugin's tools are missing and its server shows "failed" | For uvx-based plugins, install uv first. If the server crashed once, Claude Code may have recorded it in `~/.claude/mcp-needs-auth-cache.json` and stopped starting it. Remove that server's entry, then start a **new** session. See [issue 3](../docs/ISSUES-AND-FIXES.md#3-claude-code-remembered-the-first-crash-as-needs-sign-in-root-cause). |
| `review_user_story` is missing from API Functional QA | It was installed into a shared environment and downgraded to 0.1.1 (section 2). Use `uvx` or a separate venv. |
| `... must be inside the project folder` | A safety guardrail: specs, contracts and flows are only read from inside the project (`QA_MCP_ROOT` or the current folder). Copy the file in, or run from the project that holds it. |
| Integration demo: no messages arrive | The `memory` broker only works when the service runs in the same process as the flows. Use the runner script, or switch the broker to Kafka. |
| A slash command still behaves like an older version | `npx -y` and `uvx` fetch the latest server, but the command text only updates with `claude plugin update <plugin>@<marketplace>`. |
| A perf run compares unfairly with its baseline | The baseline and the run used different engines, or different machines. Keep them the same. |
| Selenium fails on import | Pin your Selenium version: 4.54.0 is broken on import. |

## 12. Reproduce the examples

Everything in [examples/](examples/) came from these runs, on 2026-11-28, with the released packages:

| Example | How |
|---|---|
| [shared-story/](examples/shared-story/) | [scripts/review.py](scripts/review.py) calls a Python tool's review in memory, and [scripts/review_stdio.py](scripts/review_stdio.py) calls Playwright QA through `npx`. The API and Integration reviews ran inside their demo projects, with `spec: openapi.yaml` and `asyncapi: asyncapi.yaml`. Performance ran in an empty project, so it reports the missing `perf.yaml` decisions. |
| [api-functional/](examples/api-functional/) | Section 5, against the API Functional QA demo shop. |
| [integration/](examples/integration/) | Section 6, with `--bugs consumer,dlq,job`, and then with no bugs on a fresh database. |
| [performance/](examples/performance/) | Section 7: a baseline, then `--slow-ms 80`. |
| UI suites | [playwright/](../playwright/) and [selenium/](../selenium/) in this repo. CI re-runs them every Monday. |

```bash
# a review, e.g. Selenium QA, run from e2e-manual/examples/shared-story (the script reads story.txt there)
uv run --no-project --with k11-selenium-qa-mcp python ../../scripts/review.py k11_selenium_qa.server review_user_story '{"story":"@story"}'
```

Timings and latency numbers will differ on your machine. The findings shouldn't.
