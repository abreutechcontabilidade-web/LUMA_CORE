import re, sys, py_compile, shutil, time

path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\virtual_onnx.py"
bak = path + ".bak_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Inserir métodos de Forca e Cronómetro
novos_metodos = '''
    def _gerar_cronometro(self):
        return """<div style='display:flex; flex-direction:column; align-items:center; justify-content:center; height:100vh; font-family:sans-serif; color:#fff; background:#0f172a;'>
            <h2 style='color:#38bdf8;'>Cronómetro (ONNX Local)</h2>
            <h1 id='cron-time' style='font-size:60px; margin:20px 0;'>00:00:00</h1>
            <div style='display:flex; gap:10px;'>
                <button onclick='startCron()' style='padding:10px 20px; background:#10b981; color:#fff; border:none; border-radius:6px; font-weight:bold; cursor:pointer;'>Iniciar</button>
                <button onclick='pauseCron()' style='padding:10px 20px; background:#f59e0b; color:#fff; border:none; border-radius:6px; font-weight:bold; cursor:pointer;'>Pausar</button>
                <button onclick='resetCron()' style='padding:10px 20px; background:#ef4444; color:#fff; border:none; border-radius:6px; font-weight:bold; cursor:pointer;'>Zerar</button>
            </div>
            <script>
                let cronSec = 0, cronMin = 0, cronHr = 0, cronTimer = null;
                function pad(v) { return v < 10 ? '0' + v : v; }
                function updateCron() {
                    document.getElementById('cron-time').innerText = pad(cronHr) + ':' + pad(cronMin) + ':' + pad(cronSec);
                }
                function runCron() {
                    cronSec++;
                    if (cronSec === 60) { cronSec = 0; cronMin++; }
                    if (cronMin === 60) { cronMin = 0; cronHr++; }
                    updateCron();
                }
                function startCron() { if(!cronTimer) cronTimer = setInterval(runCron, 1000); }
                function pauseCron() { clearInterval(cronTimer); cronTimer = null; }
                function resetCron() { clearInterval(cronTimer); cronTimer = null; cronSec = 0; cronMin = 0; cronHr = 0; updateCron(); }
            </script>
        </div>"""

    def _gerar_forca(self):
        return """<div style='display:flex; flex-direction:column; align-items:center; justify-content:center; height:100vh; font-family:sans-serif; color:#fff; background:#0f172a;'>
            <h2 style='color:#ef4444;'>Jogo da Forca (ONNX Local)</h2>
            <h1 id='forca-word' style='font-size:40px; letter-spacing:10px;'>_ _ _ _</h1>
            <p id='forca-msg' style='color:#f59e0b;'>Tentativas: 6</p>
            <div id='forca-keys' style='display:flex; flex-wrap:wrap; justify-content:center; gap:5px; max-width:400px;'></div>
            <script>
                const words = ['LUMA', 'ARIA', 'CORE', 'SOTA', 'ZBIT'];
                let word = words[Math.floor(Math.random() * words.length)];
                let guessed = new Set();
                let tries = 6;
                const keysDiv = document.getElementById('forca-keys');
                for (let i = 65; i <= 90; i++) {
                    let btn = document.createElement('button');
                    btn.innerText = String.fromCharCode(i);
                    btn.style.cssText = 'padding:10px; background:#334155; color:#fff; border:none; border-radius:4px; cursor:pointer; font-weight:bold;';
                    btn.onclick = () => guessLetter(String.fromCharCode(i), btn);
                    keysDiv.appendChild(btn);
                }
                function guessLetter(letter, btn) {
                    if (tries <= 0 || guessed.has(letter)) return;
                    guessed.add(letter);
                    btn.style.background = word.includes(letter) ? '#10b981' : '#ef4444';
                    btn.disabled = true;
                    if (!word.includes(letter)) tries--;
                    document.getElementById('forca-msg').innerText = 'Tentativas: ' + tries;
                    let display = word.split('').map(l => guessed.has(l) ? l : '_').join(' ');
                    document.getElementById('forca-word').innerText = display;
                    if (!display.includes('_')) document.getElementById('forca-msg').innerText = 'VITORIA!';
                    else if (tries <= 0) document.getElementById('forca-msg').innerText = 'GAME OVER! A palavra era: ' + word;
                }
            </script>
        </div>"""
'''

if "_gerar_cronometro" not in code:
    code = code.replace("    def _gerar_calculadora_cientifica(self):", novos_metodos + "\n    def _gerar_calculadora_cientifica(self):")

# 2. Atualizar o roteador (processar)
old_route = '''        if "pomodoro" in norm or "temporizador" in norm or "timer" in norm:
            return self._gerar_pomodoro(), "LOCAL_ONNX_HARDCODED"'''
new_route = '''        if "pomodoro" in norm:
            return self._gerar_pomodoro(), "LOCAL_ONNX_HARDCODED"
        if "cronometro" in norm or "cronómetro" in norm or "stopwatch" in norm:
            return self._gerar_cronometro(), "LOCAL_ONNX_HARDCODED"
        if "forca" in norm or "hangman" in norm:
            return self._gerar_forca(), "LOCAL_ONNX_HARDCODED"'''

if old_route in code:
    code = code.replace(old_route, new_route)
else:
    # Fallback se o texto for ligeiramente diferente
    code = code.replace('if "pomodoro" in norm or "temporizador" in norm or "timer" in norm:\n            return self._gerar_pomodoro(), "LOCAL_ONNX_HARDCODED"', new_route)

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] virtual_onnx.py expandido (Forca e Cronometro).")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)
    sys.exit(1)