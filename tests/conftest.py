# -*- coding: utf-8 -*-
import os

import allure
import pytest
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = os.getenv("GAME_URL", "http://127.0.0.1:8001")


@pytest.fixture
def driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1200,1000")
    browser = webdriver.Edge(options=options)
    browser.set_window_size(1200, 1000)
    yield browser
    browser.quit()


@pytest.fixture
def game(driver):
    from tests.pages.game_page import GamePage

    page = GamePage(driver)
    page.open(seed=42)
    return page


@pytest.fixture
def mobile_game(driver):
    from tests.pages.game_page import GamePage

    driver.set_window_size(375, 812)
    page = GamePage(driver)
    page.open(seed=42)
    return page


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        browser = item.funcargs.get("driver")
        if browser is not None:
            try:
                allure.attach(
                    browser.get_screenshot_as_png(),
                    name="失败截图",
                    attachment_type=allure.attachment_type.PNG,
                )
            except Exception:
                pass
