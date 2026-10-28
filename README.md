# 2048 网页游戏测试实战

基于原生 **HTML / CSS / JavaScript** 的 2048 游戏测试靶场 + 一套完整的游戏测试体系：功能、边界、胜负、兼容性、性能、弱网、异常与稳定性测试。

> 被测系统：2048 网页游戏（静态页面，无后端）
> 访问地址：http://127.0.0.1:8001
> 测试方式：Selenium + Pytest + Allure + Chrome DevTools Protocol

---

## 1. 项目背景

游戏测试岗位通常要求候选人理解：功能与状态、合并/计分等核心规则、兼容性与移动端适配、性能指标、弱网表现、异常与稳定性。这个项目用一个可运行的 2048 游戏作为被测对象，把这些点做成可执行、可复现、可展示的测试资产。

- 功能：移动、合并、计分、胜负、重新开始、最高分持久化
- 边界：无法移动、棋盘填满、高数值方块
- 兼容：320px / 375px 移动视口、桌面视口
- 性能：正常加载、3G 弱网加载、连续 200 次操作
- 异常：localStorage 不可用
- 自动化：Selenium 驱动键盘/触屏事件，Allure 报告与失败截图

## 2. 测试结果

| 类型 | 规模 | 结果 | 报告 |
|---|---:|---|---|
| 测试用例 | 22 条 | 22 通过，0 失败 | `docs/02-test-cases.xlsx` |
| UI 自动化 | 21 个测试 | 21 通过，0 失败 | `reports/ui/allure-report/index.html` |
| 正常加载 | 1 次 | navigation.loadEventEnd 约 **69 ms** | Allure |
| 弱网加载 | 3G（300ms / 500KB/s） | loadEventEnd 约 **697 ms**，可正常进入游戏 | Allure |
| 连续操作 | 200 次方向操作 | 约 **2.3 ms**，无 JS 异常 | Allure |
| 兼容性 | 320 / 375 / 1200px | 无横向溢出，棋盘完整显示 | 截图 |

**缺陷：** 2 个已修复（高数值方块样式、localStorage 异常兼容），2 个已知限制（仅 Edge 视口、最高分仅本地存储）。详见 `docs/03-defect-report.md`。

## 3. 目录结构

```text
game-testing/
├── index.html              # 游戏页面
├── css/style.css           # 视觉与响应式布局
├── js/game.js              # 2048 核心逻辑 + 测试钩子 window.__game
├── tests/
│   ├── conftest.py         # 浏览器 fixture、失败截图
│   ├── pages/game_page.py  # 页面对象
│   └── test_game.py        # 21 个 UI 自动化测试
├── docs/
│   ├── 01-test-plan.md
│   ├── 02-test-cases.xlsx
│   ├── 03-defect-report.md
│   └── 04-test-report.md
├── scripts/generate_test_cases.py
├── reports/ui/             # Allure 结果与 HTML 报告
├── screenshots/            # 游戏与报告截图
└── 启动-游戏测试.bat       # Windows 一键启动
```

## 4. 快速开始

```bash
python -m http.server 8001 --bind 127.0.0.1
# 浏览器打开 http://127.0.0.1:8001
```

### Windows 一键启动

双击项目根目录的 `启动-游戏测试.bat`：

- 自动打开静态服务窗口和默认浏览器；
- 地址：http://127.0.0.1:8001
- 关闭服务窗口即可停止。

> `.bat` 仅适用于 Windows；macOS / Linux 请使用上面的命令。

运行自动化测试：

```bash
python -m pytest tests -v --alluredir=reports/ui/allure-results
allure generate reports/ui/allure-results -o reports/ui/allure-report --clean
```

> 依赖：Selenium 4、Pytest、Allure、Microsoft Edge。  
> 页面支持 `?seed=42` 固定随机种子；`window.__game` 提供测试钩子（setBoard/move/getState），用于确定性断言。

## 5. 截图与测试成果展示

### 🎮 核心功能与状态展示
验证游戏正常流转、合并计分逻辑以及胜负判定。通过自动化脚本驱动，确保界面渲染无异常。
<p align="center">
  <img width="45%" alt="game-midgame" src="https://github.com/user-attachments/assets/c29a8f30-c0af-4035-a45d-57fea52efef1" />
  <img width="45%" alt="win" src="https://github.com/user-attachments/assets/8854b069-a9f8-4b6c-83de-b0abc20fba47" />
</p>

### 📱 移动端 (320px/375px) 兼容性适配
通过 Chrome DevTools 模拟移动端视口，验证页面无横向溢出、方块完整显示，确保移动端可玩性。
<p align="center">
  <!-- 把 game-mobile.png 拖到这里，然后把 width 改成 30% -->
</p>

### 📊 UI 自动化测试报告 (Allure)
基于 Selenium + Pytest 执行 21 个 UI 自动化用例，100% 全部通过。验证了四个方向合并、胜负判定等核心逻辑。
<p align="center">
  <!-- 把 allure-report.png 拖到这里，然后把 width 改成 80% -->
</p>

## 6. 测试亮点

1. **确定性测试数据**：固定 seed + `window.__game.setBoard()`，不依赖随机开局，合并/胜负/最高分都能稳定断言。
2. **四个方向全覆盖**：左、右、上、下合并都做了参数化测试。
3. **真实弱网**：通过 Chrome DevTools Protocol 设置 300ms 延迟 + 500KB/s 带宽，验证加载与可玩性。
4. **移动端适配**：320px、375px 视口分别验证无横向溢出。
5. **异常健壮性**：注入 `localStorage.getItem/setItem` 抛异常，验证游戏仍可运行。
6. **缺陷闭环**：高数值方块（16384）样式缺失、localStorage 异常未捕获，均已修复并加回归用例。

## 7. 已知限制

- 当前只覆盖 Microsoft Edge 桌面/移动视口，未覆盖 Chrome / Safari / Firefox / 真机。
- 最高分只存 `localStorage`，清缓存或换浏览器会丢失。
- 没有撤销、音效、动画等体验功能；不属于本测试靶场范围。
- 性能数据为本地静态服务基线，不代表线上 CDN/弱网真实环境。

## 8. GitHub

代码与报告位于：

`https://github.com/Barrychilde123/game-testing`

> 仓库默认分支为 `main`。
