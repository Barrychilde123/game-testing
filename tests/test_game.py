# -*- coding: utf-8 -*-
import time

import allure
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from tests.pages.game_page import BASE_URL, GamePage


def nonzero(state):
    return [v for v in state["board"] if v > 0]


@allure.feature("2048 游戏")
@allure.story("初始状态")
@allure.title("新开游戏生成 2 个方块，分数为 0")
def test_initial_state(game):
    state = game.state()
    assert len(state["board"]) == 16
    assert len(nonzero(state)) == 2
    assert state["score"] == 0
    assert state["status"] == "playing"
    assert game.score() == 0
    game.screenshot("初始棋盘")


@allure.feature("2048 游戏")
@allure.story("新游戏")
@allure.title("新游戏重置棋盘和分数，但保留最高分")
def test_new_game_resets(game):
    game.set_board([2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 100)
    game.move("left")
    assert game.score() == 104
    best_before = game.best()

    game.new_game(seed=43)
    state = game.state()
    assert state["score"] == 0
    assert len(nonzero(state)) == 2
    assert game.best() == best_before


@allure.feature("2048 游戏")
@allure.story("合并逻辑")
@allure.title("两个 2 合并为 4，分数增加 4")
def test_merge_left(game):
    game.set_board([2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 0)
    moved = game.move("left")
    state = game.state()
    assert moved is True
    assert state["score"] == 4
    assert 4 in state["board"]


@allure.feature("2048 游戏")
@allure.story("合并逻辑")
@allure.title("四个 2 合并为两个 4，分数增加 8")
def test_merge_four_twos(game):
    game.set_board([2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 0)
    game.move("left")
    state = game.state()
    assert state["score"] == 8
    assert state["board"].count(4) >= 2


@allure.feature("2048 游戏")
@allure.story("边界场景")
@allure.title("无法移动时返回 false，不生成新方块")
def test_noop_move(game):
    board = [2, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    game.set_board(board, 0)
    moved = game.move("left")
    state = game.state()
    assert moved is False
    assert state["board"] == board
    assert state["score"] == 0


@allure.feature("2048 游戏")
@allure.story("失败判定")
@allure.title("棋盘填满且无相邻相同数字时游戏结束")
def test_game_over(game):
    game.set_board(
        [2, 4, 2, 4, 4, 2, 4, 2, 2, 4, 2, 4, 4, 2, 4, 2], 0
    )
    state = game.state()
    assert state["status"] == "over"
    assert game.overlay() is True
    assert game.overlay_title() == "游戏结束"
    game.screenshot("游戏结束")


@allure.feature("2048 游戏")
@allure.story("胜利判定")
@allure.title("合成 2048 后弹出胜利提示，可继续游戏")
def test_win_and_continue(game):
    game.set_board([1024, 1024, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 0)
    game.move("left")
    state = game.state()
    assert state["status"] == "won"
    assert 2048 in state["board"]
    assert game.overlay() is True
    assert game.overlay_title() == "你赢了！"
    game.screenshot("胜利提示")

    game.click_continue()
    assert game.overlay() is False
    assert game.state()["status"] == "playing"


@allure.feature("2048 游戏")
@allure.story("最高分")
@allure.title("最高分写入 localStorage，刷新后仍然保留")
def test_best_score_persists(game):
    game.set_board([2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 100)
    game.move("left")
    assert game.score() == 104
    assert game.best() == 104

    game.driver.refresh()
    game.wait.until(lambda d: d.execute_script("return !!window.__game"))
    assert game.best() == 104


@allure.feature("2048 游戏")
@allure.story("键盘操作")
@allure.title("方向键可以移动方块并更新分数")
def test_keyboard_control(game):
    game.set_board([2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 0)
    game.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ARROW_LEFT)
    game.wait.until(lambda d: game.score() == 4)
    assert 4 in game.state()["board"]


@allure.feature("2048 游戏")
@allure.story("移动端")
@allure.title("375px 移动视口下棋盘不横向溢出")
def test_mobile_layout(mobile_game):
    metrics = mobile_game.driver.execute_script(
        """
        return {
          scrollWidth: document.documentElement.scrollWidth,
          innerWidth: window.innerWidth,
          boardWidth: document.querySelector('.board').getBoundingClientRect().width
        };
        """
    )
    assert metrics["scrollWidth"] <= metrics["innerWidth"] + 1
    assert metrics["boardWidth"] <= metrics["innerWidth"]
    mobile_game.screenshot("移动端 375px")


@allure.feature("2048 游戏")
@allure.story("性能")
@allure.title("弱网 3G 下页面仍能加载并进入游戏")
def test_weak_network_load(driver):
    driver.execute_cdp_cmd("Network.enable", {})
    driver.execute_cdp_cmd("Network.setCacheDisabled", {"cacheDisabled": True})
    driver.execute_cdp_cmd(
        "Network.emulateNetworkConditions",
        {
            "offline": False,
            "latency": 300,
            "downloadThroughput": 500 * 1024,
            "uploadThroughput": 500 * 1024,
        },
    )
    start = time.perf_counter()
    driver.get(BASE_URL + "/?seed=42")
    page = GamePage(driver)
    page.wait.until(
        lambda d: d.execute_script(
            "return !!window.__game && document.querySelectorAll('.tile').length >= 2"
        )
    )
    elapsed = round((time.perf_counter() - start) * 1000, 1)
    driver.execute_cdp_cmd(
        "Network.emulateNetworkConditions",
        {"offline": False, "latency": 0, "downloadThroughput": -1, "uploadThroughput": -1},
    )
    allure.attach(
        f"弱网加载耗时：{elapsed} ms（latency=300ms, 500KB/s）",
        name="弱网加载指标",
        attachment_type=allure.attachment_type.TEXT,
    )
    assert elapsed < 10000
    assert page.state()["status"] == "playing"


@allure.feature("2048 游戏")
@allure.story("稳定性")
@allure.title("连续 200 次方向操作不报错，状态保持合法")
def test_rapid_moves_stability(game):
    ok = game.driver.execute_script(
        """
        try {
          const dirs = ['left', 'up', 'right', 'down'];
          for (let i = 0; i < 200; i += 1) {
            window.__game.move(dirs[i % 4]);
          }
          return true;
        } catch (e) {
          return false;
        }
        """
    )
    state = game.state()
    assert ok is True
    assert len(state["board"]) == 16
    assert state["status"] in ("playing", "won", "over")
    assert state["score"] >= 0


@allure.feature("2048 游戏")
@allure.story("合并逻辑")
@allure.title("四个方向都能正确合并")
@pytest.mark.parametrize(
    "direction,board",
    [
        ("left", [2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
        ("right", [0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
        ("up", [2, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
        ("down", [0, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0]),
    ],
)
def test_merge_directions(game, direction, board):
    game.set_board(board, 0)
    assert game.move(direction) is True
    state = game.state()
    assert state["score"] == 4
    assert 4 in state["board"]


@allure.feature("2048 游戏")
@allure.story("键盘操作")
@allure.title("WASD 键可以移动方块")
def test_wasd_control(game):
    game.set_board([2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 0)
    game.driver.find_element(By.TAG_NAME, "body").send_keys("a")
    game.wait.until(lambda d: game.score() == 4)
    assert 4 in game.state()["board"]


@allure.feature("2048 游戏")
@allure.story("移动端")
@allure.title("320px 小屏下棋盘不横向溢出")
def test_small_screen_layout(driver):
    driver.set_window_size(320, 568)
    page = GamePage(driver)
    page.open(seed=42)
    metrics = driver.execute_script(
        """
        return {
          scrollWidth: document.documentElement.scrollWidth,
          innerWidth: window.innerWidth,
          boardWidth: document.querySelector('.board').getBoundingClientRect().width
        };
        """
    )
    assert metrics["scrollWidth"] <= metrics["innerWidth"] + 1
    assert metrics["boardWidth"] <= metrics["innerWidth"]
    page.screenshot("移动端 320px")


@allure.feature("2048 游戏")
@allure.story("性能")
@allure.title("本地正常网络下页面加载小于 2 秒")
def test_normal_load_time(driver):
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    wait = WebDriverWait(driver, 15)
    start = time.perf_counter()
    driver.get(BASE_URL + "/?seed=42")
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".tile")))
    elapsed = round((time.perf_counter() - start) * 1000, 1)
    nav_load = driver.execute_script(
        "const n = performance.getEntriesByType('navigation')[0]; return n ? n.loadEventEnd : 0;"
    )
    allure.attach(
        f"本地加载耗时：{elapsed} ms；navigation.loadEventEnd：{round(nav_load, 1)} ms",
        name="加载性能",
        attachment_type=allure.attachment_type.TEXT,
    )
    assert nav_load < 2000


@allure.feature("2048 游戏")
@allure.story("边界场景")
@allure.title("16384 高数值方块有可读样式")
def test_high_value_tile_style(game):
    game.set_board([8192, 8192, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 0)
    game.move("left")
    tile = game.driver.find_element(By.CSS_SELECTOR, '.tile[data-value="16384"]')
    background = tile.value_of_css_property("background-color")
    assert background not in ("rgba(0, 0, 0, 0)", "transparent")
    assert "16384" in tile.text
    game.screenshot("16384 高数值方块")


@allure.feature("2048 游戏")
@allure.story("异常兼容")
@allure.title("localStorage 不可用时游戏仍可正常运行")
def test_localstorage_unavailable(driver):
    driver.execute_cdp_cmd("Page.enable", {})
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": "Storage.prototype.getItem=function(){throw new Error('blocked')};"
            "Storage.prototype.setItem=function(){throw new Error('blocked')};"
        },
    )
    driver.get(BASE_URL + "/?seed=42")
    page = GamePage(driver)
    page.wait.until(
        lambda d: d.execute_script(
            "return !!window.__game && document.querySelectorAll('.tile').length >= 2"
        )
    )
    state = page.state()
    assert state["status"] == "playing"
    assert state["best"] == 0
    page.screenshot("localStorage 不可用")
