# Selenium QA plugin demo

Plugin: [`selenium-qa`](https://github.com/K11-Software-Solutions/k11techlab-selenium-qa-mcp) 0.3.0
(MCP server `k11-selenium-qa-mcp`, started with `uvx`). Slash command: `/selenium-qa:story-to-test`.

## Result

[`tests/test_todo_items.py`](tests/test_todo_items.py): 5 pytest tests, one per acceptance criterion
of the [TodoMVC story](../inputs/README.md#3-full-end-to-end-story-both-plugins-todomvc).
**5 passed in about 26 s** ([output](results/pytest-output.txt)).

| Test | Acceptance criterion |
|---|---|
| `test_enter_adds_buy_milk_to_the_list` | Typing "Buy milk" and pressing Enter adds it; the box clears. |
| `test_counter_shows_2_items_left_after_adding_two` | Two items, counter reads exactly "2 items left". |
| `test_ticking_buy_milk_completes_it_and_counter_shows_1_item_left` | Ticking marks it completed; the other stays active; "1 item left". |
| `test_clear_completed_removes_buy_milk_and_leaves_walk_the_dog` | Only "Walk the dog" remains. |
| `test_enter_on_empty_box_adds_nothing` | No item, no counter; a later real item is the only one. |

Explicit `WebDriverWait` waits only, no sleeps. Headless Chrome; set `HEADED=1` to watch.

## Run it

```powershell
uv venv .venv
uv pip install --python .venv\Scripts\python.exe -r requirements.txt
.venv\Scripts\python -m pytest tests -v
```

## How the agent got there (desktop app, 2026-11-25)

| Step | Tool | What happened |
|---|---|---|
| 1 | `review_user_story` | `ready: true`, no questions. |
| 2 | `parse_user_story` | 5 scenarios, a pytest skeleton and a `conftest.py` (headless Chrome fixture), written with `write_test`. |
| 3 | `explore_page` (start URL) | Verified the input: `(By.CSS_SELECTOR, 'input[placeholder="What needs to be done?"]')`. |
| 4 | `explore_page` (after adding 2 items via `session.steps`) | Verified items (`//li[@data-testid="todo-item"][normalize-space()="…"]`) and counter (`[data-testid="todo-count"]`). The per-item checkbox ("Toggle Todo") had **no unique locator**. |
| 5 | `check_locator` | Row-scoped XPath for the checkbox: 1 match, but `visible: false`. |
| 6 | `explore_page` with a `click`/`check` step on it | **Timed out**: see issue S1 below. |
| 7 | `write_test` | `tests/test_todo_items.py`. |
| 8 | `run_tests` | **Timed out at 600 s, then at 180 s, with no results**: see issue S3. Ran pytest directly instead: 5 passed. |
| 9 | `capture_baseline` | 5 locators saved to [`.qa-mcp/baselines.json`](.qa-mcp/baselines.json). |

## Earlier live runs (command line and installed plugin)

| Run | Story | Outcome |
|---|---|---|
| [01](live-runs/01-vague-story.md) | Vague checkout story | `ready: false`; asked about "fast", "easy", "after a while", the placeholder URL and the language. Wrote nothing. $0.15 |
| [02](live-runs/02-answered-story-example-com.md) | Answered example.com story | `ready: true`, then parse, explore, 4 × `check_locator`. Found the page has **no `<h1>` any more**; refused to weaken the assertion and asked how to proceed. $0.23 |
| [03](live-runs/03-vague-story-installed-plugin.md) | Vague story, plugin installed from GitHub | Server started on its own; same three questions; wrote nothing. $0.22 |
| Desktop app | Vague story | Same three questions, plus the placeholder URL, test codes and project. Wrote nothing. |

## Issues found in this demo

| # | Issue | Fix or workaround |
|---|---|---|
| S1 | TodoMVC draws each checkbox with `opacity: 0`, so Selenium reports it as not displayed. `explore_page`'s `click`/`check` steps wait for visibility and time out. | In the test: wait for **presence**, then `.click()` (Chrome accepts the click). Selenium `capture_baseline` therefore can't reach the post-tick state, so "Clear completed" has no Selenium baseline (it is still exercised by the test). |
| S2 | `selenium` **4.54.0** from PyPI fails on import: `No module named 'selenium.webdriver.common.bidi.user_agent_client_hints'`. | Pinned `selenium==4.27.1` in [requirements.txt](requirements.txt). |
| S3 | The plugin's `run_tests` timed out twice (600 s, 180 s) with no results, while plain pytest finished in 26 s. | Not fixed here. Likely the tool doesn't use the project's `.venv`; worth an issue on the plugin repo. |
| S4 | Global Python had no Selenium; `python -m venv` failed in `ensurepip`. | Used `uv venv` + `uv pip install`. |

Setup issues that stopped the plugin from starting at all are in
[../docs/ISSUES-AND-FIXES.md](../docs/ISSUES-AND-FIXES.md).
