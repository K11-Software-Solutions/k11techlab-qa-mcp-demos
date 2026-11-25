# Playwright QA plugin demo

Plugin: [`playwright-qa`](https://github.com/K11-Software-Solutions/k11techlab-playwright-qa-mcp) 0.4.1
(MCP server `k11-playwright-qa-mcp`, started with `npx -y`). Slash command: `/playwright-qa:story-to-test`.

## Result

[`tests/todo-items.spec.ts`](tests/todo-items.spec.ts): 5 Playwright Test cases, one per acceptance
criterion of the [TodoMVC story](../inputs/README.md#3-full-end-to-end-story-both-plugins-todomvc).
**5 passed in about 5.5 s**, first time, through the plugin's own `run_tests`
([output](results/playwright-output.txt)).

| Test | Acceptance criterion |
|---|---|
| Typing "Buy milk" and pressing Enter adds "Buy milk" to the list | Only item; input cleared. |
| After adding "Buy milk" and "Walk the dog", the counter shows "2 items left" | Both items in order; exact counter text. |
| Ticking "Buy milk" marks it completed and the counter shows "1 item left" | Checked, `completed` class on that row only, "1 item left". |
| Clicking "Clear completed" removes "Buy milk" and leaves "Walk the dog" | Only "Walk the dog" remains. |
| Pressing Enter with the box empty adds no item and the list stays empty | No items, no counter; a later real item is the only one. |

Web-first assertions (`expect(...).toHaveText`, `toBeChecked`, ...) only, no waits or sleeps.

## Run it

```powershell
npm ci
npx playwright install chromium
npx playwright test
```

## How the agent got there (desktop app, 2026-11-25)

| Step | Tool | What happened |
|---|---|---|
| 1 | `review_user_story` | `ready: true`, no questions. |
| 2 | `parse_user_story` | 5 scenarios and a Playwright skeleton with `beforeEach(page.goto)`. |
| 3 | `explore_page` with a `check` step using `.filter(...).getByRole(...)` | **Refused**: `unsupported locator`. Same for `.first()`. See issue P1. |
| 4 | `explore_page` after adding 2 items | Verified `getByPlaceholder('What needs to be done?')`, `getByTestId('todo-count')`, items by text. The per-item checkbox had **no unique locator** (same as Selenium). |
| 5 | `explore_page` with `check` on `page.locator('[data-testid="todo-item"]:has-text("Buy milk") .toggle')` | Worked: Playwright's `check()` handles the `opacity: 0` checkbox. Verified `getByRole('button', { name: 'Clear completed' })`. |
| 6 | `write_test` | `tests/todo-items.spec.ts`. In the spec the checkbox uses the idiomatic `getByTestId('todo-item').filter({ hasText }).getByRole('checkbox', { name: 'Toggle Todo' })`. |
| 7 | `run_tests` | 5 passed, 0 failed, 0 flaky. |
| 8 | `capture_baseline` | 4 locators, including "Clear completed" after ticking, saved to [`.qa-mcp/baselines.json`](.qa-mcp/baselines.json). |

## Earlier live runs (command line, plugin loaded from the repo folder)

| Run | Story | Outcome |
|---|---|---|
| [01](live-runs/01-vague-story.md) | Vague checkout story | `ready: false`; three questions, plus what "apply" looks like and the real URL. Wrote nothing. $0.32 |
| [02](live-runs/02-answered-story-example-com.md) | Answered checkout story | `ready: true`, `parse_user_story` gave 2 scenarios, `explore_page` found only a "Learn more" link, so it stopped: example.com has no shop. $0.16 |

## Issues found in this demo

| # | Issue | Fix or workaround |
|---|---|---|
| P1 | The session-step locator parser accepts a single call (`page.getByX(...)`, `page.locator(...)`) but not chains such as `.filter()`, `.first()` or `.getByRole()` on a locator. | Used a CSS `:has-text()` selector inside `page.locator(...)` for steps and baselines. Worth an enhancement issue on the plugin repo. |
| P2 | The installed plugin was **0.1.0** while the repo was 0.4.1, so `/playwright-qa:story-to-test` lacked the "ask before you build" step (the server itself was current, because `npx -y` fetches the latest). | `claude plugin marketplace update k11-qa-tools` then `claude plugin update playwright-qa@k11-qa-tools`. |
| P3 | Both plugins write to the same `.qa-mcp/baselines.json` when they share a project folder. They didn't clash (different locator keys under the same page URL), but it's easy to mix them up. | Split per plugin in this repo. |
