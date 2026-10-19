import os, sys, py_compile, shutil, time

path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\virtual_onnx.py"
bak = path + ".bak." + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print("[OK] Backup:", bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# --- 1. Inserir o metodo premium (se nao existir) ---
if "_gerar_jogo_da_velha_premium" not in code:
    marker = "    def _gerar_calculadora_cientifica(self):"
    premium = '''    def _gerar_jogo_da_velha_premium(self):
        return """<div style='display:flex; flex-direction:column; align-items:center; justify-content:center; min-height:100vh; font-family:sans-serif; color:#fff; background:#0f172a;'>
            <h2 style='color:#38bdf8; margin-bottom:20px;'>Jogo da Velha (ONNX Premium)</h2>
            <div style='display:flex; gap:20px;'>
                <div>
                    <div id='board' style='display:grid; grid-template-columns:repeat(3, 100px); gap:10px; background:#1e293b; padding:10px; border-radius:12px;'>
                        <button class='cell' onclick='play(0)' style='height:100px; font-size:36px; font-weight:bold; background:#0f172a; color:#f8fafc; border:none; border-radius:8px; cursor:pointer;'> </button>
                        <button class='cell' onclick='play(1)' style='height:100px; font-size:36px; font-weight:bold; background:#0f172a; color:#f8fafc; border:none; border-radius:8px; cursor:pointer;'> </button>
                        <button class='cell' onclick='play(2)' style='height:100px; font-size:36px; font-weight:bold; background:#0f172a; color:#f8fafc; border:none; border-radius:8px; cursor:pointer;'> </button>
                        <button class='cell' onclick='play(3)' style='height:100px; font-size:36px; font-weight:bold; background:#0f172a; color:#f8fafc; border:none; border-radius:8px; cursor:pointer;'> </button>
                        <button class='cell' onclick='play(4)' style='height:100px; font-size:36px; font-weight:bold; background:#0f172a; color:#f8fafc; border:none; border-radius:8px; cursor:pointer;'> </button>
                        <button class='cell' onclick='play(5)' style='height:100px; font-size:36px; font-weight:bold; background:#0f172a; color:#f8fafc; border:none; border-radius:8px; cursor:pointer;'> </button>
                        <button class='cell' onclick='play(6)' style='height:100px; font-size:36px; font-weight:bold; background:#0f172a; color:#f8fafc; border:none; border-radius:8px; cursor:pointer;'> </button>
                        <button class='cell' onclick='play(7)' style='height:100px; font-size:36px; font-weight:bold; background:#0f172a; color:#f8fafc; border:none; border-radius:8px; cursor:pointer;'> </button>
                        <button class='cell' onclick='play(8)' style='height:100px; font-size:36px; font-weight:bold; background:#0f172a; color:#f8fafc; border:none; border-radius:8px; cursor:pointer;'> </button>
                    </div>
                    <p id='status' style='margin-top:20px; font-size:20px; color:#10b981; text-align:center;'>Vez do Jogador: X</p>
                </div>
                <div style='background:#1e293b; padding:15px; border-radius:12px; width:200px;'>
                    <h3 style='color:#f59e0b; margin-top:0; text-align:center;'>Placar</h3>
                    <p style='display:flex; justify-content:space-between;'><span>Jogador X:</span> <span id='score-x' style='color:#38bdf8; font-weight:bold;'>0</span></p>
                    <p style='display:flex; justify-content:space-between;'><span>Jogador O:</span> <span id='score-o' style='color:#ef4444; font-weight:bold;'>0</span></p>
                    <h3 style='color:#f59e0b; margin-top:20px; text-align:center;'>Histórico</h3>
                    <ul id='history' style='list-style:none; padding:0; margin:0; font-size:12px; color:#94a3b8; max-height:150px; overflow-y:auto;'></ul>
                </div>
            </div>
            <button onclick='resetGame()' style='margin-top:20px; padding:10px 20px; background:#38bdf8; color:#000; border:none; border-radius:6px; font-weight:bold; cursor:pointer;'>Reiniciar Jogo</button>
            <script>
                let board = ["", "", "", "", "", "", "", "", ""];
                let current = "X";
                let active = true;
                let scoreX = 0; let scoreO = 0;
                let moveCount = 0;
                function play(i) {
                    if (board[i] === "" && active) {
                        board[i] = current;
                        document.getElementsByClassName("cell")[i].innerText = current;
                        moveCount++;
                        document.getElementById('history').innerHTML += `<li>Jogada ${moveCount}: ${current} na casa ${i}</li>`;
                        if (checkWin()) {
                            document.getElementById("status").innerText = "Vitória do " + current + "!";
                            document.getElementById("status").style.color = "#f59e0b";
                            if(current === "X") scoreX++; else scoreO++;
                            document.getElementById('score-x').innerText = scoreX;
                            document.getElementById('score-o').innerText = scoreO;
                            active = false;
                        } else if (!board.includes("")) {
                            document.getElementById("status").innerText = "Empate!";
                            document.getElementById("status").style.color = "#ef4444";
                            active = false;
                        } else {
                            current = current === "X" ? "O" : "X";
                            document.getElementById("status").innerText = "Vez do Jogador: " + current;
                        }
                    }
                }
                function checkWin() {
                    const wins = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];
                    return wins.some(w => board[w[0]] && board[w[0]] === board[w[1]] && board[w[1]] === board[w[2]]);
                }
                function resetGame() {
                    board = ["", "", "", "", "", "", "", "", ""];
                    current = "X";
                    active = true;
                    moveCount = 0;
                    document.getElementById("status").innerText = "Vez do Jogador: X";
                    document.getElementById("status").style.color = "#10b981";
                    document.getElementById('history').innerHTML = "";
                    Array.from(document.getElementsByClassName("cell")).forEach(c => c.innerText = " ");
                }
            </script>
        </div>"""

'''
    if marker in code:
        code = code.replace(marker, premium + marker)
        print("[OK] Metodo premium inserido.")
    else:
        print("[ERRO] Marker _gerar_calculadora_cientifica nao encontrado!")
        sys.exit(1)
else:
    print("[OK] Metodo premium ja existe.")

# --- 2. Atualizar a rota do jogo da velha no processar() ---
old_route = '''        if "jogo da velha" in norm or "tic tac toe" in norm:
            return self._gerar_jogo_da_velha(), "LOCAL_ONNX_HARDCODED"
'''
new_route = '''        if "jogo da velha" in norm or "tic tac toe" in norm:
            if "placar" in norm or "historico" in norm or "histórico" in norm or "placa" in norm:
                return self._gerar_jogo_da_velha_premium(), "LOCAL_PREMIUM_ONISCIENTE"
            return self._gerar_jogo_da_velha(), "LOCAL_ONNX_HARDCODED"
'''

if old_route in code:
    code = code.replace(old_route, new_route)
    print("[OK] Rota do jogo da velha atualizada.")
else:
    print("[AVISO] Rota nao encontrada. Vou substituir a funcao processar inteira.")
    start = code.find("    def processar(self, prompt: str):")
    end = code.find("    def aprender_da_nuvem")
    if start != -1 and end != -1:
        new_processar = '''    def processar(self, prompt: str):
        norm = prompt.lower().strip()
        if norm in self.dynamic_tools:
            return self.dynamic_tools[norm], "APRENDIDO_NUVEM"
        if "tetris" in norm:
            return self._gerar_tetris(), "LOCAL_ONNX"
        if "cobra" in norm or "snake" in norm or "cobrinha" in norm:
            return self._gerar_snake(), "LOCAL_ONNX"
        if "jogo da velha" in norm or "tic tac toe" in norm:
            if "placar" in norm or "historico" in norm or "histórico" in norm or "placa" in norm:
                return self._gerar_jogo_da_velha_premium(), "LOCAL_PREMIUM_ONISCIENTE"
            return self._gerar_jogo_da_velha(), "LOCAL_ONNX"
        if ("roman" in norm or "romano" in norm or "romana" in norm) and "calculadora" in norm:
            return self._gerar_calculadora_romana(), "LOCAL_ONNX"
        if "calculadora" in norm:
            return self._gerar_calculadora_cientifica(), "LOCAL_ONNX"
        if "pomodoro" in norm or "temporizador" in norm or "timer" in norm:
            return self._gerar_pomodoro(), "LOCAL_ONNX"
        if "tarefa" in norm or "todo" in norm or "to-do" in norm:
            return self._gerar_todo(), "LOCAL_ONNX"
        return None, "NUVEM_NECESSARIA"

'''
        code = code[:start] + new_processar + code[end:]
        print("[OK] processar() reescrito completamente.")
    else:
        print("[ERRO] Nao consegui encontrar processar(). Abortando.")
        sys.exit(1)

# --- 3. Escrever e compilar ---
with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. Sintaxe perfeita.")
except Exception as e:
    print(f"[FALHA] py_compile falhou: {e}")
    shutil.copy2(bak, path)
    sys.exit(1)

print("[OK] Patch concluido. Motor Onisciente instalado.")