"""As a visitor, I want to add and complete to-do items so that I can track my tasks.

Precondition: none. The page is public and starts with an empty list
(each test gets a fresh browser, so localStorage starts empty).
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

START_URL = "https://demo.playwright.dev/todomvc"

# Locators verified against the live page with explore_page / check_locator.
NEW_TODO = (By.CSS_SELECTOR, 'input[placeholder="What needs to be done?"]')
TODO_ITEMS = (By.CSS_SELECTOR, '[data-testid="todo-item"]')
TODO_COUNT = (By.CSS_SELECTOR, '[data-testid="todo-count"]')
CLEAR_COMPLETED = (By.XPATH, '//button[normalize-space()="Clear completed"]')


def todo_item(title):
    return (By.XPATH, f'//li[@data-testid="todo-item"][normalize-space()="{title}"]')


def todo_toggle(title):
    # The checkbox is drawn with opacity 0 (TodoMVC styles it with an image),
    # so Selenium reports it as not visible; wait for presence, then click it.
    return (
        By.XPATH,
        f'//li[@data-testid="todo-item"][normalize-space()="{title}"]'
        '//input[contains(@class,"toggle")]',
    )


def open_app(driver):
    driver.get(START_URL)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.visibility_of_element_located(NEW_TODO))
    return wait


def add_todo(driver, wait, title):
    count_before = len(driver.find_elements(*TODO_ITEMS))
    box = wait.until(EC.element_to_be_clickable(NEW_TODO))
    box.send_keys(title, Keys.ENTER)
    wait.until(lambda d: len(d.find_elements(*TODO_ITEMS)) == count_before + 1)


def todo_titles(driver):
    return [el.text.strip() for el in driver.find_elements(*TODO_ITEMS)]


class TestAddAndCompleteToDoItems:
    def test_enter_adds_buy_milk_to_the_list(self, driver):
        """Typing "Buy milk" in the "What needs to be done?" box and pressing Enter adds "Buy milk" to the list."""
        wait = open_app(driver)
        assert todo_titles(driver) == []

        add_todo(driver, wait, "Buy milk")

        assert wait.until(EC.visibility_of_element_located(todo_item("Buy milk")))
        assert todo_titles(driver) == ["Buy milk"]
        # The input is cleared, ready for the next item.
        assert driver.find_element(*NEW_TODO).get_attribute("value") == ""

    def test_counter_shows_2_items_left_after_adding_two(self, driver):
        """After adding "Buy milk" and "Walk the dog", the counter shows "2 items left"."""
        wait = open_app(driver)
        add_todo(driver, wait, "Buy milk")
        add_todo(driver, wait, "Walk the dog")

        assert wait.until(EC.text_to_be_present_in_element(TODO_COUNT, "2 items left"))
        assert driver.find_element(*TODO_COUNT).text.strip() == "2 items left"
        assert todo_titles(driver) == ["Buy milk", "Walk the dog"]

    def test_ticking_buy_milk_completes_it_and_counter_shows_1_item_left(self, driver):
        """Ticking the checkbox next to "Buy milk" marks it completed and the counter shows "1 item left"."""
        wait = open_app(driver)
        add_todo(driver, wait, "Buy milk")
        add_todo(driver, wait, "Walk the dog")

        wait.until(EC.presence_of_element_located(todo_toggle("Buy milk"))).click()

        wait.until(EC.element_located_to_be_selected(todo_toggle("Buy milk")))
        assert "completed" in driver.find_element(*todo_item("Buy milk")).get_attribute("class").split()
        assert "completed" not in driver.find_element(*todo_item("Walk the dog")).get_attribute("class").split()
        assert wait.until(EC.text_to_be_present_in_element(TODO_COUNT, "1 item left"))
        assert driver.find_element(*TODO_COUNT).text.strip() == "1 item left"

    def test_clear_completed_removes_buy_milk_and_leaves_walk_the_dog(self, driver):
        """Clicking "Clear completed" removes "Buy milk" and leaves "Walk the dog"."""
        wait = open_app(driver)
        add_todo(driver, wait, "Buy milk")
        add_todo(driver, wait, "Walk the dog")
        wait.until(EC.presence_of_element_located(todo_toggle("Buy milk"))).click()
        wait.until(EC.element_located_to_be_selected(todo_toggle("Buy milk")))

        wait.until(EC.element_to_be_clickable(CLEAR_COMPLETED)).click()

        wait.until(EC.invisibility_of_element_located(todo_item("Buy milk")))
        assert todo_titles(driver) == ["Walk the dog"]

    def test_enter_on_empty_box_adds_nothing(self, driver):
        """Pressing Enter with the box empty adds no item and the list stays empty."""
        wait = open_app(driver)
        box = wait.until(EC.element_to_be_clickable(NEW_TODO))

        box.send_keys(Keys.ENTER)

        # Prove the app has handled the first Enter: a real item added after it
        # must be the only item, so the empty Enter added nothing.
        assert todo_titles(driver) == []
        assert driver.find_elements(*TODO_COUNT) == []
        add_todo(driver, wait, "Buy milk")
        assert todo_titles(driver) == ["Buy milk"]
