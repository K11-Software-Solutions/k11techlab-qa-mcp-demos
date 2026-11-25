# Selenium live run 3: vague story, plugin installed from GitHub

## Command

```powershell
claude plugin marketplace add K11-Software-Solutions/k11techlab-selenium-qa-mcp
claude plugin install selenium-qa@k11-selenium-qa
claude -p "<prompt>" --permission-mode manual --allowedTools <read-only selenium-qa tools> --output-format stream-json --verbose
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

I haven't written a test yet. The story review found three things that can't be tested as written, and I need your answers before I build anything.

**1. What does "fast" mean?**
- **Raised by:** "As a shopper, I want checkout to be **fast** and easy."
- **Why it matters:** A test needs a limit it can check. For example: "checkout completes within 3 seconds of clicking Place Order" or "the discount total updates within 1 second of clicking Apply."

**2. What does "easy" mean?**
- **Raised by:** "As a shopper, I want checkout to be fast and **easy**."
- **Why it matters:** A test needs something specific to check. For example: "checkout takes at most 3 steps or pages," "a guest can check out without creating an account," or "a single click on Apply applies a valid code."

**3. When do discount codes expire, and what happens at that point?**
- **Raised by:** "Codes expire **after a while**"
- **Why it matters:** Testing the cut-off needs the exact limit. Please tell me:
  - The limit itself, such as an expiry date and time per code, or N days after it's issued.
  - What happens right at the limit: is a code still valid at its exact expiry time?
  - What happens just after it: which error message appears, and does the total stay unchanged?
  - Whether there are test codes I can use, such as one valid code, one expired code, and one that expires at a set time. Without them, the test can't put a code past its expiry.

**One more thing:** `https://example.com` is a placeholder page with no cart or checkout. Please give me the real store URL for the start page or cart. If checkout requires a login, tell me the names of the environment variables that hold the credentials, and not the credentials themselves.

Once you answer, I'll add the answers to the story as acceptance criteria, re-run the review, and go on to build and run the test. If you'd rather I go ahead now, I'll leave each unanswered point as an `OPEN QUESTION:` comment in the test. But I still can't explore pages or check locators until I have a URL that actually has a checkout.

## Run stats

- Turns: 3
- Cost: $0.22
- Duration: 13 s
- Errors: False
