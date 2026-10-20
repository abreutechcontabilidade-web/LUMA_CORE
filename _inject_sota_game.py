import json
import os

html_sota = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
  <title>Cyberpunk Snake // Neon Velocity</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; -webkit-user-select: none; }
    body { background-color: #050510; color: #00ffe1; font-family: 'Courier New', Courier, monospace; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; overflow: hidden; touch-action: none; }
    .hud { display: flex; justify-content: space-between; width: 100%; max-width: 440px; padding: 12px 16px; font-size: 14px; text-transform: uppercase; letter-spacing: 2px; background: rgba(10, 10, 25, 0.85); border: 1px solid #00ffe155; box-shadow: 0 0 15px rgba(0, 255, 225, 0.2); border-radius: 8px 8px 0 0; }
    .hud-item span { color: #ff007f; font-weight: bold; text-shadow: 0 0 8px #ff007f; }
    #game-container { position: relative; border: 2px solid #00ffe1; box-shadow: 0 0 25px rgba(0, 255, 225, 0.4), inset 0 0 20px rgba(255, 0, 127, 0.1); background: #080816; }
    canvas { display: block; background: #050510; }
    .overlay { position: absolute; inset: 0; background: rgba(5, 5, 16, 0.88); display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 16px; backdrop-filter: blur(4px); }
    .overlay.hidden { display: none; }
    .title { font-size: 26px; font-weight: bold; color: #ff007f; text-shadow: 0 0 12px #ff007f, 0 0 24px #ff007f88; text-align: center; }
    .btn { background: transparent; border: 1px solid #00ffe1; color: #00ffe1; padding: 10px 24px; font-size: 14px; font-family: inherit; letter-spacing: 2px; cursor: pointer; text-transform: uppercase; box-shadow: 0 0 12px rgba(0, 255, 225, 0.3); transition: all 0.2s ease; }
    .btn:active { background: #00ffe1; color: #050510; box-shadow: 0 0 20px #00ffe1; }
    .d-pad { display: grid; grid-template-columns: repeat(3, 56px); grid-template-rows: repeat(2, 56px); gap: 8px; margin-top: 14px; max-width: 440px; }
    .d-btn { background: rgba(15, 15, 35, 0.9); border: 1px solid #00ffe144; color: #00ffe1; border-radius: 8px; font-size: 18px; display: flex; align-items: center; justify-content: center; cursor: pointer; touch-action: manipulation; }
    .d-btn:active { background: #ff007f; color: #fff; border-color: #ff007f; box-shadow: 0 0 15px #ff007f; }
    .d-up { grid-column: 2; grid-row: 1; } .d-left { grid-column: 1; grid-row: 2; } .d-down { grid-column: 2; grid-row: 2; } .d-right { grid-column: 3; grid-row: 2; }
  </style>
</head>
<body>
  <div class="hud">
    <div class="hud-item">PONTOS: <span id="score">0</span></div>
    <div class="hud-item">VELOCIDADE: <span id="speed">1.0x</span></div>
    <div class="hud-item">RECORDE: <span id="highscore">0</span></div>
  </div>
  <div id="game-container">
    <canvas id="canvas" width="400" height="400"></canvas>
    <div id="start-screen" class="overlay">
      <div class="title">CYBERPUNK SNAKE</div>
      <p style="font-size: 12px; color: #aaa;">TECLADO [WASD / SETAS] OU TOQUE</p>
      <button class="btn" id="start-btn">INICIAR MISSÃO</button>
    </div>
    <div id="game-over-screen" class="overlay hidden">
      <div class="title" style="color:#ff003c;">SISTEMA COMPROMETIDO</div>
      <p id="final-stats" style="font-size: 13px; color: #00ffe1;"></p>
      <button class="btn" id="restart-btn">REINICIAR NÚCLEO</button>
    </div>
  </div>
  <div class="d-pad">
    <button class="d-btn d-up" data-dir="UP">▲</button>
    <button class="d-btn d-left" data-dir="LEFT">◀</button>
    <button class="d-btn d-down" data-dir="DOWN">▼</button>
    <button class="d-btn d-right" data-dir="RIGHT">▶</button>
  </div>
  <script>
    const canvas = document.getElementById('canvas'); const ctx = canvas.getContext('2d');
    const scoreEl = document.getElementById('score'); const speedEl = document.getElementById('speed'); const highscoreEl = document.getElementById('highscore');
    const startScreen = document.getElementById('start-screen'); const gameOverScreen = document.getElementById('game-over-screen'); const finalStats = document.getElementById('final-stats');
    const GRID = 20; const TILES = canvas.width / GRID;
    let snake = []; let dir = { x: 1, y: 0 }; let nextDir = { x: 1, y: 0 }; let food = { x: 15, y: 10 }; let score = 0;
    let highscore = parseInt(localStorage.getItem('cyber_snake_hi') || '0', 10); highscoreEl.textContent = highscore;
    let baseTick = 110; let currentTick = baseTick; let lastTime = 0; let isRunning = false; let particles = [];
    function resetGame() {
      snake = [{ x: 5, y: 10 }, { x: 4, y: 10 }, { x: 3, y: 10 }];
      dir = { x: 1, y: 0 }; nextDir = { x: 1, y: 0 }; score = 0; currentTick = baseTick; particles = [];
      scoreEl.textContent = '0'; speedEl.textContent = '1.0x'; spawnFood();
    }
    function spawnFood() {
      let valid = false;
      while (!valid) {
        food.x = Math.floor(Math.random() * TILES); food.y = Math.floor(Math.random() * TILES);
        valid = !snake.some(seg => seg.x === food.x && seg.y === food.y);
      }
    }
    function spawnParticles(x, y, color) {
      for (let i = 0; i < 12; i++) {
        particles.push({ x: (x + 0.5) * GRID, y: (y + 0.5) * GRID, vx: (Math.random() - 0.5) * 6, vy: (Math.random() - 0.5) * 6, life: 1, color: color });
      }
    }
    function setDirection(newDir) {
      if (!isRunning) return;
      if (newDir.x === -dir.x && newDir.y === -dir.y) return;
      nextDir = newDir;
    }
    window.addEventListener('keydown', (e) => {
      switch (e.key) {
        case 'ArrowUp': case 'w': case 'W': setDirection({ x: 0, y: -1 }); break;
        case 'ArrowDown': case 's': case 'S': setDirection({ x: 0, y: 1 }); break;
        case 'ArrowLeft': case 'a': case 'A': setDirection({ x: -1, y: 0 }); break;
        case 'ArrowRight': case 'd': case 'D': setDirection({ x: 1, y: 0 }); break;
      }
    });
    document.querySelectorAll('.d-btn').forEach(btn => {
      const handlePress = (e) => {
        e.preventDefault(); const d = btn.getAttribute('data-dir');
        if (d === 'UP') setDirection({ x: 0, y: -1 }); if (d === 'DOWN') setDirection({ x: 0, y: 1 });
        if (d === 'LEFT') setDirection({ x: -1, y: 0 }); if (d === 'RIGHT') setDirection({ x: 1, y: 0 });
      };
      btn.addEventListener('touchstart', handlePress, { passive: false }); btn.addEventListener('mousedown', handlePress);
    });
    let touchStartX = 0; let touchStartY = 0;
    canvas.addEventListener('touchstart', (e) => { touchStartX = e.touches[0].clientX; touchStartY = e.touches[0].clientY; }, { passive: true });
    canvas.addEventListener('touchend', (e) => {
      const dx = e.changedTouches[0].clientX - touchStartX; const dy = e.changedTouches[0].clientY - touchStartY;
      if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > 20) { setDirection(dx > 0 ? { x: 1, y: 0 } : { x: -1, y: 0 }); }
      else if (Math.abs(dy) > 20) { setDirection(dy > 0 ? { x: 0, y: 1 } : { x: 0, y: -1 }); }
    }, { passive: true });
    function update() {
      dir = nextDir; const head = { x: snake[0].x + dir.x, y: snake[0].y + dir.y };
      if (head.x < 0 || head.x >= TILES || head.y < 0 || head.y >= TILES || snake.some(seg => seg.x === head.x && seg.y === head.y)) { endGame(); return; }
      snake.unshift(head);
      if (head.x === food.x && head.y === food.y) {
        score += 10; scoreEl.textContent = score; spawnParticles(food.x, food.y, '#ff007f');
        if (currentTick > 45) { currentTick -= 2.5; const mult = (baseTick / currentTick).toFixed(1); speedEl.textContent = mult + 'x'; }
        if (score > highscore) { highscore = score; highscoreEl.textContent = highscore; localStorage.setItem('cyber_snake_hi', highscore); }
        spawnFood();
      } else { snake.pop(); }
    }
    function render() {
      ctx.fillStyle = '#050510'; ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.strokeStyle = '#0f172a'; ctx.lineWidth = 1;
      for (let x = 0; x < canvas.width; x += GRID) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke(); }
      for (let y = 0; y < canvas.height; y += GRID) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke(); }
      ctx.save(); ctx.shadowBlur = 15; ctx.shadowColor = '#ff007f'; ctx.fillStyle = '#ff007f';
      ctx.beginPath(); ctx.arc((food.x + 0.5) * GRID, (food.y + 0.5) * GRID, (GRID / 2) - 3, 0, Math.PI * 2); ctx.fill(); ctx.restore();
      snake.forEach((seg, index) => {
        ctx.save(); const isHead = index === 0; const alpha = Math.max(0.3, 1 - (index / snake.length) * 0.7);
        ctx.fillStyle = isHead ? '#00ffe1' : `rgba(0, 220, 200, ${alpha})`; ctx.shadowBlur = isHead ? 20 : 8; ctx.shadowColor = '#00ffe1';
        const pad = isHead ? 1 : 2; ctx.fillRect(seg.x * GRID + pad, seg.y * GRID + pad, GRID - (pad * 2), GRID - (pad * 2)); ctx.restore();
      });
      for (let i = particles.length - 1; i >= 0; i--) {
        const p = particles[i]; p.x += p.vx; p.y += p.vy; p.life -= 0.04;
        if (p.life <= 0) { particles.splice(i, 1); continue; }
        ctx.save(); ctx.fillStyle = p.color; ctx.globalAlpha = p.life; ctx.shadowBlur = 8; ctx.shadowColor = p.color; ctx.fillRect(p.x, p.y, 3, 3); ctx.restore();
      }
    }
    function loop(timestamp) {
      if (!isRunning) return;
      if (timestamp - lastTime >= currentTick) { update(); lastTime = timestamp; }
      render(); requestAnimationFrame(loop);
    }
    function startGame() {
      resetGame(); isRunning = true; startScreen.classList.add('hidden'); gameOverScreen.classList.add('hidden');
      lastTime = performance.now(); requestAnimationFrame(loop);
    }
    function endGame() {
      isRunning = false; finalStats.textContent = `PONTUAÇÃO FINAL: ${score} | RECORDE: ${highscore}`;
      gameOverScreen.classList.remove('hidden');
    }
    document.getElementById('start-btn').addEventListener('click', startGame);
    document.getElementById('restart-btn').addEventListener('click', startGame);
    render();
  </script>
</body>
</html>"""

# 1. Ler ou criar o genoma
genoma_path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\dynamic_tools.json"
if os.path.exists(genoma_path):
    with open(genoma_path, "r", encoding="utf-8") as f:
        mem = json.load(f)
else:
    mem = {}

# 2. Adicionar o jogo SOTA
mem["jogo_da_cobra"] = {
    "html": html_sota,
    "features": ["cyberpunk", "SOTA_ARTIFACT", "canvas", "touch"],
    "proveniencia": {"repo": "lovable_generated", "source": "sovereign_canonical"}
}

# 3. Gravar o genoma
tmp = genoma_path + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(mem, f, ensure_ascii=False, indent=2)
os.replace(tmp, genoma_path)
print("[OK] Jogo SOTA gravado no Genoma.")

# 4. Guardar o ficheiro no Desktop
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "jogo_cobra_CYBERPUNK_SOTA.html")
with open(desktop_path, "w", encoding="utf-8") as f:
    f.write(html_sota)
print(f"[OK] Ficheiro fisico guardado em: {desktop_path}")