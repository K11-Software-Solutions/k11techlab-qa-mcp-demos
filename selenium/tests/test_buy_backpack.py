"""As a signed-in shopper, I want to buy a backpack so that I receive my order.

Precondition: sign in with the username in env SAUCE_USER and the password in
env SAUCE_PASSWORD. The values are read from the environment and never appear here.
Each test gets a fresh browser, so the cart starts empty.

Locators verified against the live pages with explore_page (all data-test attributes).
"""
import os

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

START_URL = "https://www.saucedemo.com"


def dt(name):
    return (By.CSS_SELECTOR, f'[data-test="{name}"]')


# Login page
USERNAME = dt("username")
PASSWORD = dt("password")
LOGIN = dt("login-button")
# Inventory and cart
INVENTORY = dt("inventory-container")
ADD_BACKPACK = dt("add-to-cart-sauce-labs-backpack")
CART_LINK = dt("shopping-cart-link")
CART_BADGE = dt("shopping-cart-badge")
CART_ITEM_NAME = dt("inventory-item-name")
CHECKOUT = dt("checkout")
# Checkout: Your Information
FIRST_NAME = dt("firstName")
LAST_NAME = dt("lastName")
POSTAL_CODE = dt("postalCode")
CONTINUE = dt("continue")
ERROR = dt("error")
TITLE = dt("title")
# Checkout: Overview and Complete
SUBTOTAL = dt("subtotal-label")
TOTAL = dt("total-label")
FINISH = dt("finish")
COMPLETE_HEADER = dt("complete-header")


@pytest.fixture
def shop(driver):
    """Signed-in shopper on the inventory page."""
    user, password = os.environ.get("SAUCE_USER"), os.environ.get("SAUCE_PASSWORD")
    if not (user and password):
        pytest.skip("Set SAUCE_USER and SAUCE_PASSWORD to run the Sauce Demo tests")
    wait = WebDriverWait(driver, 10)
    driver.get(START_URL)
    wait.until(EC.visibility_of_element_located(USERNAME)).send_keys(user)
    driver.find_element(*PASSWORD).send_keys(password)
    driver.find_element(*LOGIN).click()
    wait.until(EC.visibility_of_element_located(INVENTORY))
    return driver, wait


def add_backpack_and_open_checkout(driver, wait):
    wait.until(EC.element_to_be_clickable(ADD_BACKPACK)).click()
    wait.until(EC.text_to_be_present_in_element(CART_BADGE, "1"))
    driver.find_element(*CART_LINK).click()
    assert wait.until(EC.visibility_of_element_located(CART_ITEM_NAME)).text == "Sauce Labs Backpack"
    wait.until(EC.element_to_be_clickable(CHECKOUT)).click()
    wait.until(EC.url_contains("checkout-step-one"))


def fill_information(driver, wait, first, last, postal):
    for locator, value in ((FIRST_NAME, first), (LAST_NAME, last), (POSTAL_CODE, postal)):
        field = wait.until(EC.visibility_of_element_located(locator))
        field.clear()
        if value:
            field.send_keys(value)
    driver.find_element(*CONTINUE).click()


class TestBuyABackpack:
    def test_adding_backpack_shows_1_on_cart_badge(self, shop):
        """Adding "Sauce Labs Backpack" to the cart shows "1" on the cart badge."""
        driver, wait = shop
        assert driver.find_elements(*CART_BADGE) == []  # cart starts empty

        wait.until(EC.element_to_be_clickable(ADD_BACKPACK)).click()

        assert wait.until(EC.text_to_be_present_in_element(CART_BADGE, "1"))
        assert driver.find_element(*CART_BADGE).text == "1"

    def test_continue_with_details_shows_item_total_and_total(self, shop):
        """Entering Ada / Lovelace / 12345 and clicking Continue shows "Item total: $29.99" and "Total: $32.39"."""
        driver, wait = shop
        add_backpack_and_open_checkout(driver, wait)

        fill_information(driver, wait, "Ada", "Lovelace", "12345")

        wait.until(EC.url_contains("checkout-step-two"))
        assert wait.until(EC.visibility_of_element_located(SUBTOTAL)).text == "Item total: $29.99"
        assert driver.find_element(*TOTAL).text == "Total: $32.39"

    def test_finish_shows_thank_you_for_your_order(self, shop):
        """Clicking Finish shows "Thank you for your order!"."""
        driver, wait = shop
        add_backpack_and_open_checkout(driver, wait)
        fill_information(driver, wait, "Ada", "Lovelace", "12345")
        wait.until(EC.url_contains("checkout-step-two"))

        wait.until(EC.element_to_be_clickable(FINISH)).click()

        wait.until(EC.url_contains("checkout-complete"))
        assert wait.until(EC.visibility_of_element_located(COMPLETE_HEADER)).text == "Thank you for your order!"

    def test_continue_without_first_name_shows_error_and_stays(self, shop):
        """Continue with the first name empty shows "Error: First Name is required" and stays on the information page."""
        driver, wait = shop
        add_backpack_and_open_checkout(driver, wait)

        fill_information(driver, wait, "", "Lovelace", "12345")

        assert wait.until(EC.visibility_of_element_located(ERROR)).text == "Error: First Name is required"
        assert "checkout-step-one" in driver.current_url
        assert driver.find_element(*TITLE).text == "Checkout: Your Information"
