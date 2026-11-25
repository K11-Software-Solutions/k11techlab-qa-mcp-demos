# Selenium live run 2: answered story on example.com (CLI, plugin loaded from repo folder)

## Command

```powershell
claude -p "<prompt>" --plugin-dir <plugin repo> --setting-sources project --permission-mode manual --allowedTools <review_user_story parse_user_story explore_page check_locator> --disallowedTools <write_test run_tests capture_baseline heal_locator save_login_state> Bash Write Edit --max-budget-usd 1 --output-format stream-json --verbose
```

### `review_user_story`

Input:

```json
{
  "story": "As a signed-out visitor, I want to read the Example Domain page so I can learn what the domain is for.\n- Opening the page shows the heading 'Example Domain'\n- The page has a 'Learn more' link to iana.org\n- If the page fails to load, the test fails with the HTTP status\nPrecondition: none, the page is public."
}
```

Output:

```json
{
  "ready": true,
  "questions": [],
  "assumptions": [
    "The tests will use a signed-out visitor account.",
    "Anything a question above asks about will be left as a TODO, not guessed."
  ],
  "next": "No open questions. Continue with parse_user_story."
}
```

### `parse_user_story`

Input:

```json
{
  "story": "As a signed-out visitor, I want to read the Example Domain page so I can learn what the domain is for.\n- Opening the page shows the heading 'Example Domain'\n- The page has a 'Learn more' link to iana.org\n- If the page fails to load, the test fails with the HTTP status\nPrecondition: none, the page is public.",
  "url": "https://example.com"
}
```

Output:

```json
{
  "title": "Read the Example Domain page so I can learn what the domain is for",
  "scenarios": [
    {
      "name": "Opening the page shows the heading 'Example Domain'",
      "steps": [
        {
          "keyword": "Check",
          "text": "Opening the page shows the heading 'Example Domain'"
        }
      ]
    },
    {
      "name": "The page has a 'Learn more' link to iana.org",
      "steps": [
        {
          "keyword": "Check",
          "text": "The page has a 'Learn more' link to iana.org"
        }
      ]
    },
    {
      "name": "If the page fails to load, the test fails with the HTTP status",
      "steps": [
        {
          "keyword": "Check",
          "text": "If the page fails to load, the test fails with the HTTP status"
        }
      ]
    }
  ],
  "role": "signed-out visitor",
  "goal": "read the Example Domain page so I can learn what the domain is for",
  "language": "python",
  "skeleton": "from selenium.webdriver.common.by import By\nfrom selenium.webdriver.support import expected_conditions as EC\nfrom selenium.webdriver.support.ui import WebDriverWait\n\nSTART_URL = \"https://example.com\"\n\n\nclass TestReadTheExampleDomainPageSoICanLearnWhatTheDomainIs:\n    \"\"\"As a signed-out visitor, I want read the Example Domain page so I can learn what the domain is for.\"\"\"\n\n    def test_opening_the_page_shows_the_heading_example_domain(self, driver):\n        \"\"\"Opening the page shows the heading 'Example Domain'\"\"\"\n        wait = WebDriverWait(driver, 10)\n        driver.get(START_URL)\n        # Check Opening the page shows the heading 'Example Domain'\n        # TODO: assert with an explicit wait, e.g. assert wait.until(EC.visibility_of_element_located((By.ID, \"...\"))).text == \"...\"\n\n    def test_the_page_has_a_learn_more_link_to_iana_org(self, driver):\n        \"\"\"The page has a 'Learn more' link to iana.org\"\"\"\n        wait = WebDriverWait(driver, 10)\n        driver.get(START_URL)\n        # Check The page has a 'Learn more' link to iana.org\n        # TODO: assert with an explicit wait, e.g. assert wait.until(EC.visibility_of_element_located((By.ID, \"...\"))).text == \"...\"\n\n    def test_if_the_page_fails_to_load_the_test_fails_with_the_http_statu(self, driver):\n        \"\"\"If the page fails to load, the test fails with the HTTP status\"\"\"\n        wait = WebDriverWait(driver, 10)\n        driver.get(START_URL)\n        # Check If the page fails to load, the test fails with the HTTP status\n        # TODO: assert with an explicit wait, e.g. assert wait.until(EC.visibility_of_element_located((By.ID, \"...\"))).text == \"...\"\n",
  "conftest": "import os\n\nimport pytest\nfrom selenium import webdriver\n\n\n@pytest.fixture\ndef driver():\n    \"\"\"Headless Chrome. Set HEADED=1 to watch the browser.\"\"\"\n    opts = webdriver.ChromeOptions()\n    if os.environ.get(\"HEADED\") != \"1\":\n        opts.add_argument(\"--headless=new\")\n    opts.add_argument(\"--window-size=1280,900\")\n    drv = webdriver.Chrome(options=opts)\n    yield drv\n    drv.quit()\n",
  "note": "No conftest.py found: write this one to tests/conftest.py to provide the driver fixture.",
  "review": {
    "ready": true,
    "open_questions": 0
  }
}
```

### `explore_page`

Input:

```json
{
  "url": "https://example.com",
  "only_interactive": false
}
```

Output:

```json
{
  "url": "https://example.com/",
  "title": "Example Domain",
  "stepsRun": [],
  "elements": [
    {
      "href": "https://iana.org/help/example-domains",
      "index": 0,
      "name": "Learn more",
      "role": "link",
      "tag": "a",
      "text": "Learn more",
      "best": "(By.LINK_TEXT, \"Learn more\")",
      "alternatives": [
        "(By.XPATH, '//a[normalize-space()=\"Learn more\"]')"
      ]
    }
  ]
}
```

### `check_locator`

Input:

```json
{
  "url": "https://example.com",
  "locator": "(By.TAG_NAME, \"h1\")"
}
```

Output:

```json
{
  "url": "https://example.com/",
  "locator": "(By.TAG_NAME, \"h1\")",
  "matches": 0,
  "visible": null,
  "verdict": "not_found"
}
```

### `check_locator`

Input:

```json
{
  "url": "https://example.com",
  "locator": "(By.XPATH, \"//*[normalize-space()='Example Domain' and not(self::title)]\")"
}
```

Output:

```json
{
  "url": "https://example.com/",
  "locator": "(By.XPATH, \"//*[normalize-space()='Example Domain' and not(self::title)]\")",
  "matches": 0,
  "visible": null,
  "verdict": "not_found"
}
```

### `check_locator`

Input:

```json
{
  "url": "https://example.com",
  "locator": "(By.XPATH, \"//*[self::h1 or self::h2 or self::h3 or @role='heading']\")"
}
```

Output:

```json
{
  "url": "https://example.com/",
  "locator": "(By.XPATH, \"//*[self::h1 or self::h2 or self::h3 or @role='heading']\")",
  "matches": 0,
  "visible": null,
  "verdict": "not_found"
}
```

### `check_locator`

Input:

```json
{
  "url": "https://example.com",
  "locator": "(By.XPATH, \"//body//*[contains(normalize-space(), 'Example Domain')][not(*[contains(normalize-space(), 'Example Domain')])]\")"
}
```

Output:

```json
{
  "url": "https://example.com/",
  "locator": "(By.XPATH, \"//body//*[contains(normalize-space(), 'Example Domain')][not(*[contains(normalize-space(), 'Example Domain')])]\")",
  "matches": 0,
  "visible": null,
  "verdict": "not_found"
}
```

## Final reply from the agent

I've stopped before writing the test. The live page doesn't meet the first acceptance criterion, and I can't save or run files in this session anyway.

**1. No 'Example Domain' heading on https://example.com.**
The page title is "Example Domain", but nothing visible on the page has that text. I checked four ways and each found 0 matches:
- `(By.TAG_NAME, "h1")`
- any `h1`/`h2`/`h3` or `role="heading"` element
- any element whose text is exactly 'Example Domain', leaving out `<title>`
- any element in `<body>` whose text contains 'Example Domain'

A full page scan (all elements, not just interactive ones) also found only the 'Learn more' link. So "Opening the page shows the heading 'Example Domain'" fails on the live site. The skill says to report the application as wrong rather than weaken the test. I won't swap in a page-title check without your say-so, because the title is not a visible heading.

**2. I can't save or run files here.** This session only has the selenium-qa tools for reviewing, parsing, exploring and checking locators. `write_test`, `run_tests`, `heal_locator` and `capture_baseline` aren't available, and I have no other way to write files. Steps 5–7 (save, run, baseline) can't happen in this session.

**What's done:**
- **Story review:** it came back ready with no questions, so I asked you none.
- **Scenarios:** three, one per acceptance criterion. The tool also generated a `conftest.py` with a headless Chrome `driver` fixture.
- **Verified locator:** the 'Learn more' link is `(By.LINK_TEXT, "Learn more")` and points to `https://iana.org/help/example-domains`. It matches one element.
- **HTTP status criterion:** Selenium can't read HTTP status codes. My plan is to request the URL first with Python's standard `urllib` and fail with the status if it isn't 2xx. Using Chrome's network logs is another option but more fragile.

**Decision for you:** how should the heading criterion work?
- **(a)** Treat it as a real bug: write the test to look for the visible heading, and expect it to fail until the page changes.
- **(b)** Change the criterion to "the page title is 'Example Domain'" and check `driver.title`.

Once you've decided, either rerun this in a session where `write_test` and `run_tests` work, or I can give you the full `conftest.py` and `test_example_domain.py` to paste in.

## Run stats

- Turns: 9
- Cost: $0.23
- Duration: 48 s
- Errors: False
