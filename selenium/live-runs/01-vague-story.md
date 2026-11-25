# Selenium live run 1: vague story (CLI, plugin loaded from repo folder)

## Command

```powershell
claude -p "<prompt>" --plugin-dir <plugin repo> --setting-sources project --permission-mode manual --allowedTools <review_user_story parse_user_story explore_page check_locator> --disallowedTools <write_test run_tests capture_baseline heal_locator save_login_state> Bash Write Edit --max-budget-usd 1 --output-format stream-json --verbose
```

### `Glob`

Input:

```json
{
  "pattern": "**/*"
}
```

Output:

```json
No files found
```

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

I ran `review_user_story` on the story and it isn't ready to test yet, so I've stopped there. I haven't written, explored or run anything.

## Questions

**1. What does "fast" mean in a way we can measure?**
- *From the story:* "As a shopper, I want checkout to be fast and easy."
- *Why it matters:* a test needs a threshold or a concrete expectation. For example, "checkout page loads in under 2 s" or "order confirmation shows within 5 s of clicking Place Order".

**2. What does "easy" mean in a way we can check?**
- *From the story:* "As a shopper, I want checkout to be fast and easy."
- *Why it matters:* a test needs something concrete to assert. For example, "checkout takes at most 3 steps", "guest checkout without an account", or "the cart total updates without a page reload".

**3. How long until a discount code expires, and what happens at that point?**
- *From the story:* "Codes expire after a while"
- *Why it matters:* boundary tests need the boundary. Please give:
  - The actual limit: N days after it's issued, a fixed end date, or a number of uses.
  - What the shopper sees when they enter an expired code: the exact error message, and whether the total stays the same.
  - A known valid code and a known expired code I can use in the test, or how to create them in a test environment.

## Two more things I need

- **The URL is a placeholder.** `https://example.com` is a reserved demo domain with no cart, checkout or discount field, so there's nothing to explore or test there. What's the real start URL, such as a staging or test store? Do I need to log in to reach checkout? If so, which environment variable names hold the credentials? I'll pass them as `${ENV:NAME}` and never as literal values.
- **There's no project here yet.** The working directory is empty, so I can't tell which language to use. Do you want pytest (Python), JUnit 5 (Java) or TestNG (Java)? For Java, also tell me the package name.

Once you answer, I'll add the answers to the story as acceptance criteria and review it again. If you'd rather I go ahead now, I'll mark each unanswered question in the test as an `OPEN QUESTION:` comment, but I'll still need a real URL.

## Run stats

- Turns: 4
- Cost: $0.15
- Duration: 14 s
- Errors: False
