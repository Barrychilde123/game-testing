(() => {
  "use strict";

  const SIZE = 4;
  const WIN_VALUE = 2048;
  const BEST_KEY = "game2048_best";

  const boardEl = document.querySelector('[data-testid="board"]');
  const scoreEl = document.querySelector('[data-testid="score"]');
  const bestEl = document.querySelector('[data-testid="best"]');
  const overlayEl = document.querySelector('[data-testid="overlay"]');
  const overlayTitle = document.querySelector('[data-testid="overlay-title"]');
  const overlayText = document.querySelector('[data-testid="overlay-text"]');
  const continueBtn = document.querySelector('[data-testid="continue"]');
  const retryBtn = document.querySelector('[data-testid="retry"]');
  const newGameBtn = document.querySelector('[data-testid="new-game"]');

  let board = Array(SIZE * SIZE).fill(0);
  let score = 0;
  let best = loadBest();
  let status = "playing"; // playing | won | over
  let winShown = false;
  let seed = Date.now() >>> 0;
  let rng = mulberry32(seed);
  let touchStart = null;

  const cells = [];
  for (let i = 0; i < SIZE * SIZE; i += 1) {
    const cell = document.createElement("div");
    cell.className = "cell";
    cell.dataset.index = String(i);
    boardEl.appendChild(cell);
    cells.push(cell);
  }

  function loadBest() {
    try {
      return Number(localStorage.getItem(BEST_KEY) || 0) || 0;
    } catch (error) {
      return 0;
    }
  }

  function saveBest(value) {
    try {
      localStorage.setItem(BEST_KEY, String(value));
    } catch (error) {
      // localStorage 不可用时只影响最高分持久化，不影响游戏进行
    }
  }

  function mulberry32(a) {
    return function random() {
      a |= 0;
      a = (a + 0x6d2b79f5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function setSeed(value) {
    seed = Number(value) >>> 0;
    rng = mulberry32(seed);
  }

  function spawnTile() {
    const empty = [];
    for (let i = 0; i < board.length; i += 1) {
      if (board[i] === 0) empty.push(i);
    }
    if (empty.length === 0) return null;
    const index = empty[Math.floor(rng() * empty.length)];
    board[index] = rng() < 0.9 ? 2 : 4;
    return index;
  }

  function slideLine(values) {
    const line = values.filter((value) => value !== 0);
    const merged = [];
    let gained = 0;
    for (let i = 0; i < line.length; i += 1) {
      if (line[i] === line[i + 1]) {
        const next = line[i] * 2;
        merged.push(next);
        gained += next;
        i += 1;
      } else {
        merged.push(line[i]);
      }
    }
    while (merged.length < SIZE) merged.push(0);
    return { line: merged, gained };
  }

  function linesFor(direction) {
    const rows = [
      [0, 1, 2, 3],
      [4, 5, 6, 7],
      [8, 9, 10, 11],
      [12, 13, 14, 15],
    ];
    const cols = [
      [0, 4, 8, 12],
      [1, 5, 9, 13],
      [2, 6, 10, 14],
      [3, 7, 11, 15],
    ];
    if (direction === "left") return rows;
    if (direction === "right") return rows.map((row) => [...row].reverse());
    if (direction === "up") return cols;
    if (direction === "down") return cols.map((col) => [...col].reverse());
    return [];
  }

  function move(direction) {
    if (status !== "playing") return false;
    const before = board.join(",");
    let gained = 0;
    for (const indexes of linesFor(direction)) {
      const values = indexes.map((index) => board[index]);
      const result = slideLine(values);
      gained += result.gained;
      indexes.forEach((index, i) => {
        board[index] = result.line[i];
      });
    }
    if (board.join(",") === before) return false;
    score += gained;
    if (score > best) {
      best = score;
      saveBest(best);
    }
    spawnTile();
    checkStatus();
    render();
    return true;
  }

  function canMove() {
    if (board.some((value) => value === 0)) return true;
    for (let row = 0; row < SIZE; row += 1) {
      for (let col = 0; col < SIZE; col += 1) {
        const index = row * SIZE + col;
        const value = board[index];
        if (col + 1 < SIZE && board[index + 1] === value) return true;
        if (row + 1 < SIZE && board[index + SIZE] === value) return true;
      }
    }
    return false;
  }

  function checkStatus() {
    if (status === "over") return;
    if (!winShown && board.includes(WIN_VALUE)) {
      winShown = true;
      status = "won";
      showOverlay("won");
      return;
    }
    if (!canMove()) {
      status = "over";
      showOverlay("over");
    }
  }

  function showOverlay(kind) {
    if (kind === "won") {
      overlayTitle.textContent = "你赢了！";
      overlayText.textContent = "已经达到 2048，继续挑战更高分。";
      continueBtn.style.display = "inline-flex";
    } else {
      overlayTitle.textContent = "游戏结束";
      overlayText.textContent = "没有可移动的方块了，再试一次吧。";
      continueBtn.style.display = "none";
    }
    overlayEl.dataset.state = kind;
    overlayEl.classList.remove("hidden");
  }

  function hideOverlay() {
    overlayEl.classList.add("hidden");
    overlayEl.dataset.state = "";
  }

  function render() {
    cells.forEach((cell, index) => {
      const value = board[index];
      cell.replaceChildren();
      if (value > 0) {
        const tile = document.createElement("div");
        tile.className = `tile tile-${value}`;
        tile.textContent = String(value);
        tile.dataset.testid = `tile-${index}`;
        tile.dataset.value = String(value);
        cell.appendChild(tile);
      }
    });
    scoreEl.textContent = String(score);
    bestEl.textContent = String(best);
    document.body.dataset.status = status;
  }

  function newGame(nextSeed) {
    if (nextSeed !== undefined) setSeed(nextSeed);
    board = Array(SIZE * SIZE).fill(0);
    score = 0;
    status = "playing";
    winShown = false;
    hideOverlay();
    spawnTile();
    spawnTile();
    render();
  }

  function setBoard(values, nextScore = 0) {
    board = Array.from({ length: SIZE * SIZE }, (_, i) => Number(values[i]) || 0);
    score = Number(nextScore) || 0;
    status = "playing";
    winShown = false;
    hideOverlay();
    checkStatus();
    render();
  }

  function onKeyDown(event) {
    const key = event.key.toLowerCase();
    const map = {
      arrowleft: "left",
      arrowright: "right",
      arrowup: "up",
      arrowdown: "down",
      a: "left",
      d: "right",
      w: "up",
      s: "down",
    };
    if (!(key in map)) return;
    event.preventDefault();
    if (status !== "playing") return;
    move(map[key]);
  }

  function onTouchStart(event) {
    if (status !== "playing") return;
    const touch = event.changedTouches[0];
    touchStart = { x: touch.clientX, y: touch.clientY };
  }

  function onTouchEnd(event) {
    if (!touchStart || status !== "playing") return;
    const touch = event.changedTouches[0];
    const dx = touch.clientX - touchStart.x;
    const dy = touch.clientY - touchStart.y;
    touchStart = null;
    if (Math.max(Math.abs(dx), Math.abs(dy)) < 24) return;
    event.preventDefault();
    if (Math.abs(dx) > Math.abs(dy)) {
      move(dx > 0 ? "right" : "left");
    } else {
      move(dy > 0 ? "down" : "up");
    }
  }

  newGameBtn.addEventListener("click", () => newGame());
  retryBtn.addEventListener("click", () => newGame());
  continueBtn.addEventListener("click", () => {
    if (status === "won") {
      status = "playing";
      hideOverlay();
      render();
    }
  });
  window.addEventListener("keydown", onKeyDown);
  boardEl.addEventListener("touchstart", onTouchStart, { passive: true });
  boardEl.addEventListener("touchend", onTouchEnd, { passive: false });

  const seedParam = new URLSearchParams(window.location.search).get("seed");
  newGame(seedParam !== null ? Number(seedParam) : Date.now());

  window.__game = {
    getState: () => ({
      board: [...board],
      score,
      best,
      status,
      winShown,
      seed,
    }),
    setBoard,
    move,
    newGame,
    checkStatus,
    setSeed,
  };
})();
