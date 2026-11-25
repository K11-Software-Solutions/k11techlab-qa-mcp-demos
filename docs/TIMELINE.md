# Timeline

All dates are 2026-11-25. Times are approximate and in UTC.

| Time | What happened |
|---|---|
| Before 19:48 | Released `review_user_story` ("ask before you build") in playwright-qa 0.4.0 and 0.4.1, then ported it to selenium-qa 0.3.0. |
| 19:48 | Asked: "can we try those plugins live?" |
| ~19:50 | **Playwright CLI run 1** (vague story): 3 questions, nothing written. [record](../playwright/live-runs/01-vague-story.md) |
| ~19:50 | **Playwright CLI run 2** (answered story, example.com): `ready: true`, parsed and explored, then stopped because there's no shop. [record](../playwright/live-runs/02-answered-story-example-com.md) |
| ~19:51 to 19:56 | **Selenium server shows "failed"** in CLI runs. Tried a bash PATH fix, a direct handshake, `--mcp-config`, plugin copies, absolute `uvx`, and `cmd /c`. See issues 1 and 2. |
| ~19:57 | **Selenium CLI run 1** (vague story) succeeds with the server connected. [record](../selenium/live-runs/01-vague-story.md) |
| ~19:58 | **Selenium CLI run 2** (answered story, example.com): found the page's `<h1>` is gone and reported it. [record](../selenium/live-runs/02-answered-story-example-com.md) |
| 20:03 | Installed the Selenium plugin from GitHub the way users would. **Selenium run 3** passes. [record](../selenium/live-runs/03-vague-story-installed-plugin.md) |
| 20:04 | Updated the installed Playwright plugin from 0.1.0 to 0.4.1 (issue 6). |
| 20:05 | Installed uv globally. The server still showed "failed", which led to finding `mcp-needs-auth-cache.json` and removing its stale entry (issues 3 and 4). |
| 20:08 | Restarted the app, but the old session still had no tools (issue 5). |
| 20:13 | **New desktop session:** `selenium-qa` lists 9 tools and `review_user_story` answers. |
| 20:14 | Desktop vague-story run: `ready: false`, the three questions, nothing written. |
| ~20:20 to 20:30 | **Selenium TodoMVC run:** `ready: true`, then explore and write the tests. Hit issues 8, 9, 10 and 12. 5/5 passed with pytest. Baseline captured. [folder](../selenium/) |
| ~20:35 to 20:45 | **Playwright TodoMVC run:** `ready: true`, then explore (hit issue 11) and write the spec. 5/5 passed first time through `run_tests`. Baseline captured. [folder](../playwright/) |
| ~20:50 | Created this repository as a historical record. |

## Cost of the command-line live runs

| Run | Cost | Time |
|---|---|---|
| Playwright 1 | $0.32 | 15 s |
| Playwright 2 | $0.16 | 19 s |
| Selenium 1 | $0.15 | 14 s |
| Selenium 2 | $0.23 | 48 s |
| Selenium 3 | $0.22 | 13 s |
