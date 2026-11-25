import os

import pytest
from selenium import webdriver


@pytest.fixture
def driver():
    """Headless Chrome. Set HEADED=1 to watch the browser."""
    opts = webdriver.ChromeOptions()
    if os.environ.get("HEADED") != "1":
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1280,900")
    drv = webdriver.Chrome(options=opts)
    yield drv
    drv.quit()
