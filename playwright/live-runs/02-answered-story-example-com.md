# Playwright live run 2: answered story on example.com (CLI, plugin loaded from repo folder)

## Command

```powershell
claude -p "<prompt>" --plugin-dir <plugin repo> --setting-sources project --permission-mode manual --allowedTools <review_user_story parse_user_story explore_page check_locator> --disallowedTools <write_test run_tests capture_baseline heal_locator save_login_state> Bash Write Edit --max-budget-usd 1 --output-format stream-json --verbose
```

## Session start

- Model: `claude-opus-5-5`
- QA MCP server at start: `plugin:playwright-qa:playwright-qa` = pending
- Slash command loaded: `/playwright-qa:story-to-test`

## Tool calls

### `review_user_story`

Input:

```json
{
  "story": "As a signed-in shopper, I want to apply a discount code at checkout.\nScenario: valid code\n  Given I have a cart worth $80\n  When I apply the code SAVE10\n  Then I see \"Discount: -$8.00\"\nScenario: expired code\n  Given I have a cart worth $80\n  When I apply a code that expired 31 days ago\n  Then I see \"This code has expired\""
}
```

Output:

```json
{
  "ready": true,
  "questions": [],
  "assumptions": [
    "The tests will use a signed-in shopper account.",
    "Anything a question above asks about will be left as a TODO, not guessed."
  ],
  "next": "No open questions. Continue with parse_user_story."
}
```

### `parse_user_story`

Input:

```json
{
  "story": "As a signed-in shopper, I want to apply a discount code at checkout.\nScenario: valid code\n  Given I have a cart worth $80\n  When I apply the code SAVE10\n  Then I see \"Discount: -$8.00\"\nScenario: expired code\n  Given I have a cart worth $80\n  When I apply a code that expired 31 days ago\n  Then I see \"This code has expired\"",
  "url": "https://example.com"
}
```

Output:

```json
{
  "story": {
    "title": "Apply a discount code at checkout",
    "scenarios": [
      {
        "name": "valid code",
        "steps": [
          {
            "keyword": "Given",
            "text": "I have a cart worth $80"
          },
          {
            "keyword": "When",
            "text": "I apply the code SAVE10"
          },
          {
            "keyword": "Then",
            "text": "I see \"Discount: -$8.00\""
          }
        ]
      },
      {
        "name": "expired code",
        "steps": [
          {
            "keyword": "Given",
            "text": "I have a cart worth $80"
          },
          {
            "keyword": "When",
            "text": "I apply a code that expired 31 days ago"
          },
          {
            "keyword": "Then",
            "text": "I see \"This code has expired\""
          }
        ]
      }
    ],
    "role": "signed-in shopper",
    "goal": "apply a discount code at checkout"
  },
  "skeleton": "import { test, expect } from '@playwright/test';\n\n// Story: As a signed-in shopper, I want apply a discount code at checkout.\ntest.describe('Apply a discount code at checkout', () => {\n  test.beforeEach(async ({ page }) => {\n    await page.goto('https://example.com');\n  });\n\n  test('valid code', async ({ page }) => {\n    await test.step('Given I have a cart worth $80', async () => {\n      // TODO: action using a verified locator from explore_page\n    });\n    await test.step('When I apply the code SAVE10', async () => {\n      // TODO: action using a verified locator from explore_page\n    });\n    await test.step('Then I see \"Discount: -$8.00\"', async () => {\n      // TODO: web-first assertion, e.g. await expect(page.getByRole(...)).toBeVisible();\n    });\n  });\n\n  test('expired code', async ({ page }) => {\n    await test.step('Given I have a cart worth $80', async () => {\n      // TODO: action using a verified locator from explore_page\n    });\n    await test.step('When I apply a code that expired 31 days ago', async () => {\n      // TODO: action using a verified locator from explore_page\n    });\n    await test.step('Then I see \"This code has expired\"', async () => {\n      // TODO: web-first assertion, e.g. await expect(page.getByRole(...)).toBeVisible();\n    });\n  });\n});\n",
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
  "url": "https://example.com"
}
```

Output:

```json
{
  "url": "https://example.com/",
  "count": 1,
  "elements": [
    {
      "tag": "a",
      "role": "link",
      "name": "Learn more",
      "text": "Learn more",
      "href": "https://iana.org/help/example-domains",
      "best": "page.getByRole('link', { name: 'Learn more' })",
      "alternatives": [
        "page.getByText('Learn more')"
      ]
    }
  ]
}
```

## Final reply from the agent

I stopped at step 3. I didn't write, save or run a spec, and I didn't capture a baseline.

**Why:** https://example.com is a placeholder page that exists only for use in documentation. It has no shop. When I explored it, it had exactly one interactive element, a "Learn more" link to iana.org. There's no sign-in, cart, checkout or discount-code field. The workflow says to use only locators confirmed on the live page, so any spec I wrote would rely on made-up selectors and fail.

**What did work:**
- `review_user_story` returned `ready: true` with no open questions.
- `parse_user_story` produced two scenarios ("valid code" and "expired code"), each with Given/When/Then steps and a skeleton test ready to fill in.

**Questions to answer before I build it.** The review tool didn't flag these, but they're gaps I'd hit while filling in the test:
1. **The real start URL:** where is the shop? Its checkout page URL would help too.
2. **Signing in:** where is the login page, and which environment variables hold the test account's details (for example `SHOPPER_EMAIL` and `SHOPPER_PASSWORD`)? I'll save the login once and never put the password in the spec.
3. **The $80 cart:** should the test add specific products through the page (which ones?), or does a seeded account or API call set it up?
4. **The expired code:** the story says "a code that expired 31 days ago" without naming one. Is there a fixed code in the test data, such as `EXPIRED31`, or should the test create one first?
5. **Exact wording:** should the discount line match "Discount: -$8.00" exactly, or just contain that text? Does the expired-code message appear in an alert or next to the field?

Once you send the real URL and these answers, I'll update the story, explore the checkout pages through the login, write and run `discount-code.spec.ts`, and capture the baseline.

## Run stats

- Turns: 5
- Cost: $0.16
- Duration: 19 s
- Errors: False
