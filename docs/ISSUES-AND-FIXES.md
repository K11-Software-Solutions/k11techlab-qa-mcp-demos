# Issues and fixes

Everything that went wrong while trying the two plugins live on Windows 11 (2026-11-25), with the
cause and the fix. Per-demo test issues are also listed in each folder's README.

## Getting the Selenium plugin's MCP server to start

### 1. `uvx` resolution broke under a bash `PATH`

- **Symptom:** in command-line runs from Git Bash, the server failed to start.
- **Cause:** a Windows `C:/...` path in a bash `PATH` entry broke `uvx` lookup.
- **Fix:** convert the path with `cygpath -u` before prepending it. The server still showed "failed" after this, which led to issue 3.

### 2. Server shown as "failed" when the plugin was loaded from its repo folder

- **Symptom:** `claude -p --plugin-dir <repo>` showed `plugin:selenium-qa:selenium-qa = failed`. The debug log showed no start-up attempt at all.
- **What was ruled out:**
  - A direct MCP handshake with `uvx k11-selenium-qa-mcp` worked (0.3.0, 9 tools, 2.5 s), using [`scripts/handshake.py`](scripts/handshake.py).
  - An exact copy of the plugin in another folder connected in about 1.1 s.
  - The same server definition passed through `--mcp-config` also connected.
  - Bare `uvx` failed where an absolute path to `uvx.exe` or `cmd /c uvx` worked. That was a clue, but not the whole cause.
- **Real cause:** issue 3.

### 3. Claude Code remembered the first crash as "needs sign-in" (root cause)

- **Symptom:**
  - The plugin was installed from GitHub (`claude plugin marketplace add K11-Software-Solutions/k11techlab-selenium-qa-mcp`, then `claude plugin install selenium-qa@k11-selenium-qa`).
  - uv was installed globally.
  - The server *still* showed "failed" in new sessions and was never even started.
- **Cause:**
  - Claude Code keeps a list of MCP servers it believes need authentication, at `%USERPROFILE%\.claude\mcp-needs-auth-cache.json`, and skips starting any server on that list.
  - When the server crashed the first time (because `uvx` was missing), it was added to that list by mistake, so it was never retried.
- **Fix:**
  - Back up the file.
  - Remove only the `plugin:selenium-qa:selenium-qa` entry.
  - Start a new session. Both plugin servers then reported `connected`.

### 4. uv not installed globally

- **Symptom:** in the desktop app, the plugin failed with "Connection closed". Earlier command-line runs had only worked because a temporary uv was put on the `PATH` for them.
- **Fix:**
  - winget isn't available on this machine, so uv was installed with Astral's official installer:
    `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
  - That installs uv 0.13.10 to `%USERPROFILE%\.local\bin` and adds that folder to the user `PATH`.

### 5. The "restart" didn't restart the app

- **Symptom:** after a restart, the old session still had no Selenium tools.
- **Cause:**
  - A session connects to its MCP servers only once, when it starts.
  - Closing the window also left the app running in the system tray, with processes dating from days earlier.
- **Fix:** start a **new session**, or quit the app from the tray icon and reopen it. The new session listed all 9 `selenium-qa` tools, and `review_user_story` answered.

## Plugin and library issues

| # | Issue | Fix or status |
|---|---|---|
| 6 | The installed Playwright plugin was 0.1.0, while the repo was 0.4.1. Its slash command lacked "ask before you build". | Fixed: `claude plugin marketplace update k11-qa-tools`, then `claude plugin update playwright-qa@k11-qa-tools`. |
| 7 | The Python server logs a validation error when Claude Code first sends `server/discover`. The connection still works. | Open, cosmetic. Upgrading the `mcp` package should fix it. |
| 8 | `selenium` 4.54.0 from PyPI is broken on import: `selenium.webdriver.common.bidi.user_agent_client_hints` is missing. | Pinned `selenium==4.27.1`. |
| 9 | The Selenium plugin's `run_tests` timed out (at 600 s, then 180 s) with no results, while plain pytest took 26 s. | Open. It probably doesn't use the project's `.venv`. |
| 10 | Selenium treats TodoMVC's `opacity: 0` checkboxes as not displayed, so the `explore_page` click and check steps time out. | Worked around in the test: wait for presence, then click. Playwright's `check()` has no such problem. |
| 11 | The Playwright session-step locator parser rejects chained locators (`.filter()`, `.first()`). | Worked around with `page.locator('…:has-text("…") .toggle')`. Open as an enhancement. |
| 12 | `python -m venv` failed in `ensurepip` on this machine. | Used `uv venv`. |
| 13 | The first CI run failed in the Playwright job: `ubuntu-latest` is now Ubuntu 26.04, and Playwright 1.56.1 has no Chromium build for it ("Playwright does not support chromium on ubuntu26.04-x64"). | Pinned both CI jobs to `ubuntu-24.04`, keeping the Playwright version the demo used. |

## What behaved exactly as designed

- **Vague story, both plugins, every route:**
  - The routes were command line, plugin installed from GitHub, and the desktop app.
  - `review_user_story` returned `ready: false`, quoting "fast", "easy" and "after a while".
  - The agent stopped to ask, and no file was written.
- **Answered story on example.com:**
  - Both agents refused to invent selectors for a page that has no shop.
  - The Selenium agent found that the live page no longer has an `<h1>`, and reported it instead of weakening the assertion.
