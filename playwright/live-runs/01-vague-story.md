# Playwright live run 1: vague story (CLI, plugin loaded from repo folder)

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
  "story": "As a shopper, I want checkout to be fast and easy.\n- Discount codes apply at checkout\n- Codes expire after a while"
}
```

Output:

```json
{
  "ready": false,
  "questions": [
    {
      "kind": "vague-term",
      "question": "\"fast\" can't be tested as written. What is the measurable version (a number, a time, a specific behaviour)?",
      "why": "A test needs a threshold or a concrete expectation.",
      "quote": "As a shopper, I want checkout to be fast and easy."
    },
    {
      "kind": "vague-term",
      "question": "\"easy\" can't be tested as written. What is the measurable version (a number, a time, a specific behaviour)?",
      "why": "A test needs a threshold or a concrete expectation.",
      "quote": "As a shopper, I want checkout to be fast and easy."
    },
    {
      "kind": "limit",
      "question": "What is the actual number for this limit, and what happens exactly at it and one past it?",
      "why": "Boundary tests need the boundary.",
      "quote": "Codes expire after a while"
    }
  ],
  "assumptions": [
    "The tests will use a shopper account.",
    "Anything a question above asks about will be left as a TODO, not guessed."
  ],
  "next": "Ask the user these questions and wait for answers. Add the answers to the story (as acceptance criteria or Given/When/Then), then call review_user_story again."
}
```

## Final reply from the agent

I haven't written a test yet. `review_user_story` says the story isn't ready, so I need you to answer three questions first.

**1. What does "fast" mean?**
- **Words that raised it:** "As a shopper, I want checkout to be fast and easy."
- **Why it matters:** a test needs a number or a specific behaviour to check against.
- **Example answers:** "the order confirmation appears within 3 seconds of clicking Place order" or "checkout is a single page."

**2. What does "easy" mean?**
- **Words that raised it:** "As a shopper, I want checkout to be fast and easy."
- **Why it matters:** same reason; it needs a measurable version.
- **Example answers:** "checkout takes 3 steps or fewer," "guests can check out without an account," or "only name, address and card details are required."

**3. When does a code expire, and what happens at that point?**
- **Words that raised it:** "Codes expire after a while"
- **Why it matters:** testing the boundary needs the exact limit.
- **Please tell me:**
  - how long a code lasts (for example, 30 days after it's issued, or a fixed end date)
  - what the shopper sees right at the limit and just after it (for example, the error message text)

**Two more things I need to build the test:**
- **What "apply" looks like on screen:** a discount line in the order summary? A lower total? A "Code applied" message? Also, which codes can I use in tests: one that's valid and one that has already expired?
- **The URL:** `https://example.com` is a placeholder page with no shop or checkout, so there's nothing to test there. What's the real URL of your store or test environment? Does checkout need a login? If it does, I'll save a login state and read the password from an environment variable, not from the spec.

Once you reply, I'll add your answers to the story as acceptance criteria, run the review again, and then build and run the spec. If you'd rather I go ahead now, I'll leave each unanswered question as an `// OPEN QUESTION:` comment in the spec, but I still need a real URL.

## Run stats

- Turns: 3
- Cost: $0.32
- Duration: 15 s
- Errors: False
