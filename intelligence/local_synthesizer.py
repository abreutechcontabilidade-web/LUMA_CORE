def synthesize_calculator():
    return """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Cyberpunk Calculator</title>
    <style>
        * { box-sizing: border-box; font-family: 'Courier New', monospace; }
        body { background: #050510; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .calc { background: #0a0a1a; border: 2px solid #00ffe1; box-shadow: 0 0 20px #00ffe1; padding: 20px; border-radius: 10px; width: 320px; }
        .display { background: #000; color: #ff2fd6; font-size: 2em; text-align: right; padding: 10px; border: 1px solid #ff2fd6; margin-bottom: 15px; text-shadow: 0 0 10px #ff2fd6; overflow: hidden; }
        .keys { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
        button { background: #1a1a2e; color: #00ffe1; border: 1px solid #00ffe1; padding: 15px; font-size: 1.2em; cursor: pointer; text-shadow: 0 0 5px #00ffe1; border-radius: 5px; transition: 0.1s; }
        button:active { background: #00ffe1; color: #050510; }
        .op { color: #ff2fd6; border-color: #ff2fd6; text-shadow: 0 0 5px #ff2fd6; }
        .op:active { background: #ff2fd6; color: #050510; }
        .equal { color: #050510; background: #00ffe1; border-color: #00ffe1; }
        .equal:active { background: #ff2fd6; border-color: #ff2fd6; }
        .span-4 { grid-column: span 4; }
    </style>
</head>
<body>
    <div class="calc">
        <div class="display" id="display">0</div>
        <div class="keys">
            <button class="op" onclick="clearDisplay()">C</button>
            <button class="op" onclick="append('/')">/</button>
            <button class="op" onclick="append('*')">*</button>
            <button class="op" onclick="append('-')">-</button>
            <button onclick="append('7')">7</button>
            <button onclick="append('8')">8</button>
            <button onclick="append('9')">9</button>
            <button class="op" onclick="append('+')">+</button>
            <button onclick="append('4')">4</button>
            <button onclick="append('5')">5</button>
            <button onclick="append('6')">6</button>
            <button class="op equal" onclick="calculate()">=</button>
            <button onclick="append('1')">1</button>
            <button onclick="append('2')">2</button>
            <button onclick="append('3')">3</button>
            <button onclick="append('.')">.</button>
            <button class="span-4" onclick="append('0')">0</button>
        </div>
    </div>
    <script>
        let current = '0';
        function updateDisplay() { document.getElementById('display').innerText = current; }
        function append(val) { if (current === '0' && val !== '.') current = val; else current += val; updateDisplay(); }
        function clearDisplay() { current = '0'; updateDisplay(); }
        function calculate() { try { current = eval(current).toString(); } catch { current = 'Erro'; } updateDisplay(); }
    </script>
</body>
</html>"""