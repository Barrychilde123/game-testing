# -*- coding: utf-8 -*-
import os

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = os.getenv("GAME_URL", "http://127.0.0.1:8001")


class GamePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    def open(self, seed=42):
        self.driver.get(BASE_URL + "/")
        self.driver.execute_script("localStorage.clear()")
        self.driver.get(f"{BASE_URL}/?seed={seed}")
        self.wait.until(
            lambda d: d.execute_script(
                "return !!window.__game && document.querySelectorAll('.tile').length >= 2"
            )
        )
        return self

    def state(self):
        return self.driver.execute_script("return window.__game.getState()")

    def set_board(self, values, score=0):
        self.driver.execute_script(
            "window.__game.setBoard(arguments[0], arguments[1]);", values, score
        )
        return self

    def move(self, direction):
        return self.driver.execute_script(
            "return window.__game.move(arguments[0]);", direction
        )

    def new_game(self, seed=None):
        if seed is None:
            self.driver.find_element(By.CSS_SELECTOR, '[data-testid="new-game"]').click()
        else:
            self.driver.execute_script("window.__game.newGame(arguments[0]);", seed)
        return self

    def score(self):
        return int(self.driver.find_element(By.CSS_SELECTOR, '[data-testid="score"]').text)

    def best(self):
        return int(self.driver.find_element(By.CSS_SELECTOR, '[data-testid="best"]').text)

    def overlay(self):
        element = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="overlay"]')
        return element.is_displayed()

    def overlay_title(self):
        return self.driver.find_element(
            By.CSS_SELECTOR, '[data-testid="overlay-title"]'
        ).text

    def click_continue(self):
        self.driver.find_element(By.CSS_SELECTOR, '[data-testid="continue"]').click()
        return self

    def click_retry(self):
        self.driver.find_element(By.CSS_SELECTOR, '[data-testid="retry"]').click()
        return self

    def screenshot(self, name):
        allure.attach(
            self.driver.get_screenshot_as_png(),
            name=name,
            attachment_type=allure.attachment_type.PNG,
        )
