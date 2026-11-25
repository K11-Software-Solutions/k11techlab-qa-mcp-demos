import { test, expect, type Page } from '@playwright/test';

// Story: As a visitor, I want to add and complete to-do items so that I can track my tasks.
// Precondition: none. The page is public and starts with an empty list
// (each test gets a fresh browser context, so localStorage starts empty).
//
// Locators verified against the live page with explore_page.

const START_URL = 'https://demo.playwright.dev/todomvc';

const newTodo = (page: Page) => page.getByPlaceholder('What needs to be done?');
const todoItems = (page: Page) => page.getByTestId('todo-item');
const todoItem = (page: Page, title: string) => todoItems(page).filter({ hasText: title });
const todoToggle = (page: Page, title: string) => todoItem(page, title).getByRole('checkbox', { name: 'Toggle Todo' });
const todoCount = (page: Page) => page.getByTestId('todo-count');
const clearCompleted = (page: Page) => page.getByRole('button', { name: 'Clear completed' });

async function addTodo(page: Page, title: string) {
  await newTodo(page).fill(title);
  await newTodo(page).press('Enter');
}

test.describe('Add and complete to-do items', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(START_URL);
    await expect(newTodo(page)).toBeVisible();
    await expect(todoItems(page)).toHaveCount(0);
  });

  test('Typing "Buy milk" and pressing Enter adds "Buy milk" to the list', async ({ page }) => {
    await test.step('Add "Buy milk"', async () => {
      await addTodo(page, 'Buy milk');
    });
    await test.step('"Buy milk" is the only item and the box is cleared', async () => {
      await expect(todoItems(page)).toHaveText(['Buy milk']);
      await expect(newTodo(page)).toHaveValue('');
    });
  });

  test('After adding "Buy milk" and "Walk the dog", the counter shows "2 items left"', async ({ page }) => {
    await addTodo(page, 'Buy milk');
    await addTodo(page, 'Walk the dog');

    await expect(todoItems(page)).toHaveText(['Buy milk', 'Walk the dog']);
    await expect(todoCount(page)).toHaveText('2 items left');
  });

  test('Ticking "Buy milk" marks it completed and the counter shows "1 item left"', async ({ page }) => {
    await addTodo(page, 'Buy milk');
    await addTodo(page, 'Walk the dog');

    await todoToggle(page, 'Buy milk').check();

    await expect(todoToggle(page, 'Buy milk')).toBeChecked();
    await expect(todoItem(page, 'Buy milk')).toHaveClass(/\bcompleted\b/);
    await expect(todoItem(page, 'Walk the dog')).not.toHaveClass(/\bcompleted\b/);
    await expect(todoCount(page)).toHaveText('1 item left');
  });

  test('Clicking "Clear completed" removes "Buy milk" and leaves "Walk the dog"', async ({ page }) => {
    await addTodo(page, 'Buy milk');
    await addTodo(page, 'Walk the dog');
    await todoToggle(page, 'Buy milk').check();
    await expect(todoToggle(page, 'Buy milk')).toBeChecked();

    await clearCompleted(page).click();

    await expect(todoItems(page)).toHaveText(['Walk the dog']);
  });

  test('Pressing Enter with the box empty adds no item and the list stays empty', async ({ page }) => {
    await newTodo(page).press('Enter');

    await expect(todoItems(page)).toHaveCount(0);
    await expect(todoCount(page)).toHaveCount(0);
    // Prove the app handled the empty Enter: one real item afterwards must be the only item.
    await addTodo(page, 'Buy milk');
    await expect(todoItems(page)).toHaveText(['Buy milk']);
  });
});
