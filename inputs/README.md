# Inputs

The exact stories given to the plugins, in the order they were used. Each one was passed as
`/<plugin>:story-to-test <start URL> <story>`.

## 1. Vague story (should be refused until answered)

Start URL: `https://example.com`

```text
As a shopper, I want checkout to be fast and easy.
- Discount codes apply at checkout
- Codes expire after a while
```

Expected: `review_user_story` returns `ready: false` with questions about "fast", "easy" and
"after a while", and the agent writes nothing.

## 2a. Answered checkout story (Playwright, example.com)

Start URL: `https://example.com`

```text
As a signed-in shopper, I want to apply a discount code at checkout.
Scenario: valid code
  Given I have a cart worth $80
  When I apply the code SAVE10
  Then I see "Discount: -$8.00"
Scenario: expired code
  Given I have a cart worth $80
  When I apply a code that expired 31 days ago
  Then I see "This code has expired"
```

Expected: `ready: true`. The agent should then stop at exploration, because example.com has no shop.

## 2b. Answered page story (Selenium, example.com)

Start URL: `https://example.com`

```text
As a signed-out visitor, I want to read the Example Domain page so I can learn what the domain is for.
- Opening the page shows the heading 'Example Domain'
- The page has a 'Learn more' link to iana.org
- If the page fails to load, the test fails with the HTTP status
Precondition: none, the page is public.
```

Expected: `ready: true`. What actually happened: the live page no longer has an `<h1>`, and the agent
reported it as an application problem instead of weakening the test (see
[selenium/live-runs/02](../selenium/live-runs/02-answered-story-example-com.md)).

## 3. Full end-to-end story (both plugins, TodoMVC)

Start URL: `https://demo.playwright.dev/todomvc`

```text
As a visitor, I want to add and complete to-do items so that I can track my tasks.
Precondition: none, the page is public and starts with an empty list.
- Typing "Buy milk" in the "What needs to be done?" box and pressing Enter adds "Buy milk" to the list
- After adding "Buy milk" and "Walk the dog", the counter shows "2 items left"
- Ticking the checkbox next to "Buy milk" marks it completed and the counter shows "1 item left"
- Clicking "Clear completed" removes "Buy milk" and leaves "Walk the dog"
- Pressing Enter with the box empty adds no item and the list stays empty
```

Selenium was asked for pytest. Expected and actual: `ready: true`, then a passing 5-test suite from each plugin.
