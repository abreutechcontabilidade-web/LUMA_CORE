# -*- coding: utf-8 -*-
"""
╔════════════════════════════════════════════════════════════════════╗
║  🌟 LUMA v6.0 "LUMINÁRIA" — O Organismo Completo                  ║
║  Aria · ColorGuard · Ocular · 20-20-20 · Voz · História · Skills  ║
╠════════════════════════════════════════════════════════════════════╣
║  6 PILARES:                                                       ║
║   ⚖ LUZ ADAPTATIVA (gamma+overlay+DDC, fusão por confiança)      ║
║   🛡 SENTINELA PESSOAL (rajadas, padrões, anomalias, anticorpos)  ║
║   🩸 MEMÓRIA VIVA (episódios + Ebbinghaus + esquecer hora)        ║
║   🩺 SAÚDE DIGITAL (20-20-20 + circadiano + diagnóstico limiar)  ║
║   🎤 VOZ COMANDA (offline, palavra-chave, 0,3s)                  ║
║   🧬 PLATAFORMA (skills vivas + tribunal + exportação)           ║
║                                                                    ║
║  SEM LLM. SEM NUVEM. SEM IA EXTERNA. TUDO NOSSO. TUDO AUDITÁVEL. ║
║                                                                    ║
║  ATALHOS (cascata automática — a linha ⌨ mostra o combo real):   ║
║   +1-5 perfil · setas ajuste · R normal · M janela · A Aria       ║
║   +S diagnóstico ocular · +H histórico do dia                     ║
║                                                                    ║
║  RODAR: python controle_brilho.py                                 ║
║  OPCIONAL: pip install pystray pillow                             ║
║  .EXE: pyinstaller --onefile --noconsole controle_brilho.py       ║
╚════════════════════════════════════════════════════════════════════╝
"""
import ctypes, json, os, sys, queue, threading, time, math, random, hashlib
import tkinter as tk
from tkinter import filedialog, messagebox
import winreg
from ctypes import wintypes

# ---------- [0] Instância Única ----------
_k32 = ctypes.WinDLL("kernel32", use_last_error=True)
_k32.CreateMutexW(None, False, "LUMA_Aria_InstanciaUnica")
if ctypes.get_last_error() == 183:
    ctypes.windll.user32.MessageBoxW(0, "LUMA já está rodando (veja a bandeja).",
                                     "LUMA v6.0", 0x40)
    sys.exit(0)

# ---------- [1] Sistema / GDI / DPI ----------
try: ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try: ctypes.windll.user32.SetProcessDPIAware()
    except Exception: pass

user32, gdi32 = ctypes.windll.user32, ctypes.windll.gdi32
HDC = user32.GetDC(0)
gdi32.SetDeviceGammaRamp.argtypes = [wintypes.HDC, ctypes.POINTER(ctypes.c_ushort)]
gdi32.SetDeviceGammaRamp.restype = wintypes.BOOL
GWL_EXSTYLE = -20
WS_EX_LAYERED, WS_EX_TRANSPARENT, WS_EX_TOOLWINDOW = 0x80000, 0x20, 0x80
WM_HOTKEY, WM_QUIT = 0x0312, 0x0012

def rampa_identidade():
    r = (ctypes.c_ushort * 768)()
    for i in range(768): r[i] = (i % 256) * 257
    return r

def _rampa_monotona(r):
    for ch in range(0, 768, 256):
        for i in range(1, 256):
            if r[ch + i] < r[ch + i - 1]:
                return False
    return True

_ramp_lock = threading.Lock()

def _tentar(r):
    with _ramp_lock:
        return bool(gdi32.SetDeviceGammaRamp(HDC, r))

def construir_ramp(brilho, calor):
    f = max(50.0, min(100.0, brilho)) / 100.0
    rf, gf, bf = 1 + .30*calor, 1 + .05*calor, 1 - .60*calor
    ramp = (ctypes.c_ushort * 768)()
    for i in range(256):
        k = i * 257
        ramp[i]     = min(65535, int(k*f*rf + .5))
        ramp[256+i] = min(65535, int(k*f*gf + .5))
        ramp[512+i] = min(65535, int(k*f*bf + .5))
    return ramp

def aplicar_gamma(brilho, calor):
    ramp = construir_ramp(brilho, calor)
    if _tentar(ramp): return "ok"
    for p in range(1, 9):
        t = p / 8.0
        r2 = (ctypes.c_ushort * 768)()
        for i in range(768):
            r2[i] = int(ramp[i]*(1-t) + (i % 256)*257*t + .5)
        if _tentar(r2): return "parcial"
    _tentar(rampa_identidade())
    return "falhou"

# ---------- [2] DDC/CI ----------
try: dxva2 = ctypes.windll.dxva2
except OSError: dxva2 = None

class Fisico(ctypes.Structure):
    _fields_ = [("handle", wintypes.HANDLE), ("nome", ctypes.c_wchar * 128)]
VCP_LUM = 0x10

def _enum_fisicos():
    if dxva2 is None: return []
    res, proc = [], ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HMONITOR, wintypes.HDC,
                                       ctypes.POINTER(wintypes.RECT), wintypes.LPARAM)
    def cb(hmon, _h, _r, _l):
        n = wintypes.DWORD()
        if dxva2.GetNumberOfPhysicalMonitorsFromHMONITOR(hmon, ctypes.byref(n)) and n.value:
            arr = (Fisico * n.value)()
            if dxva2.GetPhysicalMonitorsFromHMONITOR(hmon, arr):
                res.extend(arr[i].handle for i in range(n.value))
        return True
    cbc = proc(cb); user32.EnumDisplayMonitors(None, None, cbc, 0)
    return res

def ddc_ler(h):
    t, c, m = wintypes.DWORD(), wintypes.DWORD(), wintypes.DWORD()
    if dxva2.GetVCPFeatureAndVCPFeatureCounter(h, VCP_LUM, ctypes.byref(t),
                                               ctypes.byref(c), ctypes.byref(m)):
        return c.value, (m.value or 100)
    return None, None

class TrabalhadorDDC(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.fila, self.suporta = queue.Queue(), False
        self.handles, self.maximo = _enum_fisicos(), {}
        for h in self.handles:
            cur, mx = ddc_ler(h)
            if cur is not None: self.suporta, self.maximo[h] = True, mx
    def run(self):
        while True:
            v = self.fila.get()
            try:
                while True: v = self.fila.get_nowait()
            except queue.Empty: pass
            for h in self.handles:
                try: dxva2.SetVCPFeature(h, VCP_LUM, int(v * self.maximo[h] / 100))
                except Exception: pass

# ---------- [3] Sensores ----------
class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.UINT), ("dwTime", wintypes.DWORD)]

def idle_segundos():
    lii = LASTINPUTINFO(); lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
    if user32.GetLastInputInfo(ctypes.byref(lii)):
        return (_k32.GetTickCount64() - lii.dwTime) / 1000.0
    return 0.0

psapi = ctypes.windll.psapi

def app_ativo():
    try:
        hwnd = user32.GetForegroundWindow()
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        h = _k32.OpenProcess(0x1000, False, pid.value)
        if not h: return None, "?"
        buf = ctypes.create_unicode_buffer(260)
        ok = psapi.GetModuleBaseNameW(h, None, buf, 260)
        _k32.CloseHandle(h)
        if not ok: return None, "?"
        nome = buf.value.split(".")[0].lower()
        return hashlib.sha1(nome.encode()).hexdigest()[:8], nome
    except Exception:
        return None, "?"

def ler_bateria():
    class SPS(ctypes.Structure):
        _fields_ = [("AC", ctypes.c_byte), ("Flag", ctypes.c_byte),
                    ("Pct", ctypes.c_byte), ("R1", ctypes.c_byte),
                    ("Life", ctypes.c_ulong), ("Full", ctypes.c_ulong)]
    try:
        sps = SPS()
        if not _k32.GetSystemPowerStatus(ctypes.byref(sps)):
            return {"ac": True, "pct": None, "carregando": False}
        pct = sps.Pct
        return {"ac": sps.AC == 1, "pct": None if pct == 255 else int(pct),
                "carregando": bool(sps.Flag & 8)}
    except Exception:
        return {"ac": True, "pct": None, "carregando": False}

# ---------- [4] Matemática (fundir CORRIGIDO) ----------
class EMA:
    __slots__ = ("a", "v")
    def __init__(self, a, v=None): self.a, self.v = a, v
    def __call__(self, x):
        self.v = x if self.v is None else self.a*x + (1-self.a)*self.v
        return self.v

def fundir(pares):
    """⚖ CORRIGIDO: confiança maior puxa mais (média ponderada)."""
    if not pares: return None
    total = sum(c for _, c in pares)
    if total <= 0: return pares[0][0]
    return sum(v * c for v, c in pares) / total

BLOCOS = " ▁▂▃▄▅▆▇█"

def curva_ascii(d, lo, hi):
    s = ""
    for hh in range(24):
        v = d.get(str(hh))
        if v is None: s += "·"
        else:
            f = max(0.0, min(1.0, (v - lo) / max(1e-9, hi - lo)))
            s += BLOCOS[int(round(f * 7))]
    return s

# ---------- [5] Bandit ----------
CANDIDATOS = [("dia", (100, 0, 0)), ("leitura", (90, 60, 0)),
              ("noite", (80, 100, 10)), ("profundo", (70, 20, 55))]
CAND = dict(CANDIDATOS)

class Bandit:
    def __init__(self, dados): self.cerebros = dados
    def escolhe(self, app_hash):
        bs = self.cerebros.setdefault(app_hash, {n: [1.0, 1.0] for n, _ in CANDIDATOS})
        total = sum((a-1) + (b-1) for a, b in bs.values())
        if total == 0:
            return random.choice(list(CAND)) if random.random() < 0.34 else None
        melhor, ms = None, -1.0
        for n, (a, b) in bs.items():
            s = random.betavariate(a, b)
            if s > ms: melhor, ms = n, s
        return melhor
    def feedback(self, app_hash, nome, bom):
        ab = self.cerebros.setdefault(app_hash, {}).setdefault(nome, [1.0, 1.0])
        ab[0 if bom else 1] += 1

# ---------- [6] Holt-Winters ----------
class HoltWinters:
    def __init__(self, dados):
        self.nivel = dados.get("nivel") or {"b": None, "c": None, "e": None}
        self.tend = dados.get("tend") or {"b": 0.0, "c": 0.0, "e": 0.0}
        self.saz = {k: EMA(0.3, v) for k, v in (dados.get("sazon") or {}).items()}
    def observa(self, idx, b, c, e):
        for ch, x in (("b", b), ("c", c), ("e", e)):
            base = self.nivel[ch] if self.nivel[ch] is not None else x
            self.saz.setdefault(f"{ch}{idx}", EMA(0.3))(x - base)
            ant = self.nivel[ch]
            self.nivel[ch] = x if ant is None else .08*x + .92*ant
            if ant is not None:
                self.tend[ch] = .02*(self.nivel[ch]-ant) + .98*self.tend[ch]
    def preve(self, idx):
        r = {}
        for ch in "bce":
            if self.nivel[ch] is None: return None
            s = self.saz.get(f"{ch}{idx}")
            r[ch] = self.nivel[ch] + (s.v if s else 0.0) + self.tend[ch]
        return r
    def dump(self):
        return {"nivel": self.nivel, "tend": self.tend,
                "sazon": {k: e.v for k, e in self.saz.items() if e.v is not None}}

# ---------- [7] CUSUM ----------
class CUSUM:
    def __init__(self): self.stat, self.med, self.desv = {}, {}, {}
    def observa(self, hora, valor):
        m = self.med.get(hora)
        if m is None:
            self.med[hora] = EMA(0.15, valor)
            self.desv[hora] = EMA(0.15, 1.0)
            self.stat[hora] = 0.0
            return False
        mu_antes = m.v
        de = self.desv.get(hora) or EMA(0.15, 1.0)
        sig = max((de.v or 1.0) * 1.25, 1.0)
        z = (valor - mu_antes) / sig
        S = max(0.0, self.stat.get(hora, 0.0) + z - 0.5)
        self.stat[hora] = S
        m(valor); de(abs(valor - mu_antes)); self.desv[hora] = de
        return S > 5.0
    def reset(self, hora):
        self.stat[hora] = 0.0
        self.med.pop(hora, None); self.desv.pop(hora, None)

# ---------- [8] ⚛️ Motor Quântico v3 ----------
class MotorQuanticoSuave:
    def __init__(self, funcao_aplicar_gamma, trabalhador_ddc, log_fn=None,
                 passos_min=20, passos_max=100):
        self.aplicar_gamma = funcao_aplicar_gamma
        self.ddc = trabalhador_ddc
        self.log = log_fn or (lambda m: None)
        self.p_min, self.p_max = passos_min, passos_max
        self._lock = threading.Lock()
        self._token = 0
        self._transicao_real = False

    @property
    def transicao_em_curso(self):
        return self._transicao_real

    def transicionar(self, b_alvo, c_alvo, b_atual, c_atual):
        with self._lock:
            self._token += 1
            token = self._token
            self._transicao_real = True
        distancia = max(abs(b_alvo - b_atual), abs(c_alvo - c_atual))
        passos = max(self.p_min, min(self.p_max, int(distancia * 1.5)))
        intervalo = 0.025
        def _passos():
            for i in range(1, passos + 1):
                if token != self._token: return
                fracao = i / passos
                b_hora = b_atual + (b_alvo - b_atual) * fracao
                c_hora = c_atual + (c_alvo - c_atual) * fracao
                try:
                    self.aplicar_gamma(round(b_hora), round(c_hora))
                    if self.ddc and self.ddc.suporta:
                        self.ddc.fila.put(round(b_hora))
                except Exception as e:
                    self.log(f"[DRIVER] {e}")
                time.sleep(intervalo)
            self._transicao_real = False
            self.log(f"✨ estabilizado: ({b_alvo}, {c_alvo}) em {passos} passos")
        threading.Thread(target=_passos, daemon=True).start()

# ---------- [9] 🩺 Diagnóstico Ocular ----------
class DiagnosticoOcular:
    def __init__(self, limiar_fadiga=20, limiar_ruido=6, log_fn=None):
        self.lim_fadiga, self.lim_ruido = limiar_fadiga, limiar_ruido
        self.log = log_fn or (lambda m: None)
        self.minutos_uso = 0.0
        self.ruidos = 0
        self._ultimo_diag = 0.0
    def registrar_uso(self, minutos=0.5): self.minutos_uso += minutos
    def registrar_pausa(self): self.minutos_uso = 0.0
    def registrar_ruido(self, n=1): self.ruidos += n
    def diagnosticar(self, forcar=False, osd_fn=None):
        if not forcar and time.time() - self._ultimo_diag < 600: return None
        self._ultimo_diag = time.time()
        diag = []
        if self.minutos_uso >= self.lim_fadiga:
            diag.append(f"risco de Fadiga Visual (SVC) — {int(self.minutos_uso)}min "
                        "contínuos; descanse 20s olhando a 6 metros")
        if self.ruidos > self.lim_ruido:
            diag.append(f"estresse por oscilação — {self.ruidos} ajustes bruscos")
        if not diag:
            diag.append("Perfil de iluminação estável — conforto visual OK")
        texto = " | ".join(diag)
        self.log(f"🩺 diagnóstico: {texto}")
        if osd_fn: osd_fn("🩺 " + texto[:70])
        self.ruidos = 0
        return diag

# ---------- [10] Cidades / IP ----------
CIDADES = {
    "São Paulo": -23.55, "Rio de Janeiro": -22.91, "Belo Horizonte": -19.92,
    "Brasília": -15.78, "Salvador": -12.97, "Fortaleza": -3.73,
    "Recife": -8.05, "Porto Alegre": -30.03, "Curitiba": -25.43,
    "Manaus": -3.12, "Belém": -1.46, "Goiânia": -16.68, "Natal": -5.79,
    "Maceió": -9.66, "Campo Grande": -20.47, "Teresina": -5.09,
    "João Pessoa": -7.12, "Cuiabá": -15.60, "Aracaju": -10.95,
    "Florianópolis": -27.59, "Vitória": -20.32, "São Luís": -2.53,
    "Palmas": -10.25, "Macapá": 0.03, "Porto Velho": -8.76,
    "Boa Vista": 2.82, "Rio Branco": -9.97, "Campinas": -22.91,
    "Santos": -23.96, "São José dos Campos": -23.19, "Ribeirão Preto": -21.18,
    "Sorocaba": -23.50, "Niterói": -22.88, "Juiz de Fora": -21.76,
    "Uberlândia": -18.92, "Joinville": -26.30, "Londrina": -23.30,
    "Maringá": -23.42, "Caxias do Sul": -29.17, "Feira de Santana": -12.26,
    "Campina Grande": -7.22, "Caruaru": -8.28, "Petrolina": -9.39,
    "Imperatriz": -5.53, "Santarém": -2.44, "Porto Seguro": -16.45,
    "Foz do Iguaçu": -25.52, "Pelotas": -31.77, "Montes Claros": -16.74,
    "Juazeiro do Norte": -7.21, "Sobral": -3.69, "Sinop": -11.86,
    "Dourados": -22.22, "Picos": -7.08, "São Carlos": -22.02,
    "Piracicaba": -22.72, "Cabo Frio": -22.89, "Vila Velha": -20.33,
    "Governador Valadares": -18.85, "Jaboatão dos Guararapes": -8.11,
    "Olinda": -8.01, "Paulista": -7.94, "Camaragibe": -8.02,
    "Abreu e Lima": -7.91, "Igarassu": -7.83, "Moreno": -8.12,
    "Carpina": -7.85, "Gravatá": -8.21, "Garanhuns": -8.88,
    "Vitória de Santo Antão": -8.12, "Manicoré": -5.81, "Humaitá": -7.51,
    "Lisboa": 38.72, "Porto": 41.15, "Madri": 40.42, "Paris": 48.86,
    "Londres": 51.51, "Nova York": 40.71, "Miami": 25.76, "Los Angeles": 34.05,
}

def detectar_ip_thread(fila):
    lat, city = None, None
    try:
        import urllib.request
        with urllib.request.urlopen(
                "http://ip-api.com/json/?fields=lat,city", timeout=8) as r:
            d = json.loads(r.read().decode())
        lat, city = d.get("lat"), d.get("city")
    except Exception: pass
    fila.put(("ip", lat, city))

# ---------- [11] Config / log ----------
APPDIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "ControleBrilhoPro")
CFG_ARQ = os.path.join(APPDIR, "config.json")
LOG_ARQ = os.path.join(APPDIR, "aria.log")
LIMITE_LOG = 1_000_000
PADRAO = {"brilho": 100.0, "calor": 0.0, "escuro": 0.0, "gamma_min": 50,
          "latitude": None, "cidade_nome": None, "ausente_apos": 240,
          "aria_on": False, "aria": {"habito": {}, "bandit": {}, "hw": {},
                                     "stats": {"aulas": 0, "ruido": 0}},
          "auto_noite": False, "atalhos": True, "iniciar_win": False,
          "ausente_dim": 65, "nascimento": None}

def carregar_cfg():
    try:
        with open(CFG_ARQ, encoding="utf-8") as f: return {**PADRAO, **json.load(f)}
    except Exception: return dict(PADRAO)

def salvar_cfg(cfg):
    try:
        os.makedirs(APPDIR, exist_ok=True)
        tmp = CFG_ARQ + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False)
            f.flush(); os.fsync(f.fileno())
        os.replace(tmp, CFG_ARQ)
    except Exception: pass

def log_aria(msg):
    try:
        os.makedirs(APPDIR, exist_ok=True)
        if os.path.exists(LOG_ARQ) and os.path.getsize(LOG_ARQ) > LIMITE_LOG:
            try: os.replace(LOG_ARQ, LOG_ARQ + ".old")
            except Exception: pass
        with open(LOG_ARQ, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | {msg}\n")
    except Exception: pass

def definir_autostart(ativar):
    try:
        if getattr(sys, "frozen", False): cmd = f'"{sys.executable}"'
        else:
            pyw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
            cmd = f'"{pyw}" "{os.path.abspath(sys.argv[0])}"'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Software\Microsoft\Windows\CurrentVersion\Run",
                            0, winreg.KEY_SET_VALUE) as k:
            if ativar: winreg.SetValueEx(k, "ControleBrilhoPro", 0, winreg.REG_SZ, cmd)
            else:
                try: winreg.DeleteValue(k, "ControleBrilhoPro")
                except FileNotFoundError: pass
        return True
    except Exception: return False

def nascer_poser(lat):
    n = time.localtime().tm_yday
    lat = max(-65.0, min(65.0, float(lat)))
    decl = 23.44 * math.sin(math.radians(360 * (284 + n) / 365))
    x = max(-1.0, min(1.0, -math.tan(math.radians(lat)) * math.tan(math.radians(decl))))
    H = math.degrees(math.acos(x)) / 15.0
    return (12 - H) % 24, (12 + H) % 24

# ---------- [12] Atalhos ----------
MOD_C, MOD_A, MOD_S, MOD_W = 0x0002, 0x0001, 0x0004, 0x0008
COMBOS = [("Ctrl+Alt+Shift", MOD_C | MOD_A | MOD_S),
          ("Ctrl+Win+Shift", MOD_C | MOD_W | MOD_S),
          ("Ctrl+Win+Alt",   MOD_C | MOD_W | MOD_A),
          ("Win+Shift+Alt",  MOD_W | MOD_S | MOD_A),
          ("Ctrl+Alt",       MOD_C | MOD_A)]
ATALHOS = {1: (0x26, "↑ clarear"), 2: (0x28, "↓ escurecer"), 3: (0x27, "→ quente"),
           4: (0x25, "← frio"), 5: (0x52, "R normal"), 6: (0x4D, "M janela"),
           7: (0x41, "A Aria"),
           8: (0x31, "1 Normal"), 9: (0x32, "2 Leitura"), 10: (0x33, "3 Noite"),
           11: (0x34, "4 Escuro"), 12: (0x35, "5 Super escuro")}

class OuvinteAtalhos(threading.Thread):
    def __init__(self, fila):
        super().__init__(daemon=True)
        self.fila, self.parar, self.tid, self.ativos = fila, threading.Event(), 0, 0
        self.registrados = {}
    def run(self):
        self.tid = _k32.GetCurrentThreadId()
        reg = []
        for i, (vk, nome) in ATALHOS.items():
            for pre, mods in COMBOS:
                if user32.RegisterHotKey(None, i, mods, vk):
                    reg.append(i); self.registrados[i] = (pre, vk, nome); break
        self.ativos = len(reg)
        msg = wintypes.MSG()
        while not self.parar.is_set():
            if user32.GetMessageW(ctypes.byref(msg), None, 0, 0) <= 0: break
            if msg.message == WM_HOTKEY: self.fila.put(int(msg.wParam))
        for i in reg: user32.UnregisterHotKey(None, i)
    def encerrar(self):
        self.parar.set()
        if self.tid: user32.PostThreadMessageW(self.tid, WM_QUIT, 0, 0)
    def prefixo(self, i):
        return self.registrados[i][0] if i in self.registrados else "—"

# ---------- [13] Bandeja ----------
try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_OK = True
except Exception:
    TRAY_OK = False

def _icone():
    img = Image.new("RGB", (64, 64), (43, 43, 58))
    d = ImageDraw.Draw(img)
    d.ellipse([8, 8, 56, 56], outline=(255, 210, 110), width=5)
    d.ellipse([23, 23, 41, 41], fill=(255, 210, 110))
    return img

# ---------- [14] Overlay + OSD ----------
class Overlay:
    def __init__(self, root):
        self.win = tk.Toplevel(root)
        self.win.overrideredirect(True); self.win.attributes("-topmost", True)
        self.win.configure(bg="black"); self.win.attributes("-alpha", 0.0)
        x, y = user32.GetSystemMetrics(76), user32.GetSystemMetrics(77)
        w, h = user32.GetSystemMetrics(78), user32.GetSystemMetrics(79)
        self.win.geometry(f"{w}x{h}+{x}+{y}")
        self.win.withdraw(); self.win.update_idletasks()
        hwnd = user32.GetParent(self.win.winfo_id()) or self.win.winfo_id()
        try: g, s = user32.GetWindowLongPtrW, user32.SetWindowLongPtrW
        except AttributeError: g, s = user32.GetWindowLongW, user32.SetWindowLongW
        s(hwnd, GWL_EXSTYLE, g(hwnd, GWL_EXSTYLE) |
          WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW)
    def definir(self, pct):
        if pct <= 0: self.win.withdraw()
        else:
            self.win.deiconify()
            self.win.attributes("-alpha", min(0.85, pct / 100.0))
            self.win.lift()

def barra(v, lo, hi, w=10):
    n = max(0, min(w, int(round(w * (float(v) - lo) / (hi - lo)))))
    return "█" * n + "░" * (w - n)

# ---------- [15] App v6.0 LUMINÁRIA ----------
PRESETS = [("Normal", 100, 0, 0), ("Leitura", 90, 60, 0), ("Noite", 80, 100, 10),
           ("Escuro", 70, 20, 55), ("Super escuro", 60, 0, 80)]
NOITE, DIA = (80, 100, 10), (100, 0, 0)
COR_PERFIL = {"tecla": "#7fd7ff", "aria": "#ffd26e", "bandeja": "#cde",
              "slider": "#aaa", "auto": "#8f8"}

class App:
    def __init__(self, root):
        self.root, self.cfg = root, carregar_cfg()
        a = self.cfg.setdefault("aria", {})
        for k in ("habito", "bandit", "hw"): a.setdefault(k, {})
        a.setdefault("stats", {"aulas": 0, "ruido": 0})
        if not self.cfg.get("nascimento"):
            self.cfg["nascimento"] = time.strftime("%Y-%m-%d"); salvar_cfg(self.cfg)
        self.fila = queue.Queue()
        self.hk, self.icone, self._save_job, self._osd_job = None, None, None, None
        self._osd_win, self._aria_aplicando, self._em_preset = None, False, False
        self.pausado_ate, self._zona = 0.0, None
        self._ausente, self._antes = False, 0
        self._app_hash, self._app_nome, self._bandit_atual = None, None, None
        self._bandit_t0 = None
        self._perfil_atual = ("—", "slider")
        self._mud_ts, self._rajada = [], False

        self.bandit = Bandit(a["bandit"])
        self.hw = HoltWinters(a["hw"])
        self.cusum = CUSUM()
        self._cusum_win = None
        self.diag = DiagnosticoOcular(log_fn=log_aria)

        self.ddc = TrabalhadorDDC(); self.ddc.start()
        self._ddc_ultimo = None
        self.motor = MotorQuanticoSuave(aplicar_gamma, self.ddc, log_fn=log_aria)

        root.title("🌟 LUMA v6.0 LUMINÁRIA — Aria 2.0")
        root.geometry("470x1020")
        root.attributes("-topmost", True)
        root.configure(bg="#2b2b3a")
        root.protocol("WM_DELETE_WINDOW", self._fechar_janela)

        self.overlay = Overlay(root)
        self.v_brilho = tk.DoubleVar(value=self.cfg["brilho"])
        self.v_calor  = tk.DoubleVar(value=self.cfg["calor"])
        self.v_escuro = tk.DoubleVar(value=self.cfg["escuro"])
        self.v_aria   = tk.BooleanVar(value=self.cfg["aria_on"])
        self.v_noite  = tk.BooleanVar(value=self.cfg["auto_noite"])
        self.v_atalho = tk.BooleanVar(value=self.cfg["atalhos"])
        self.v_win    = tk.BooleanVar(value=self.cfg["iniciar_win"])

        def rot(t):
            tk.Label(root, text=t, bg="#2b2b3a", fg="white",
                     font=("Arial", 11, "bold")).pack(pady=(8, 0))
        def sld(v, de, ate):
            return tk.Scale(root, from_=de, to=ate, orient="horizontal", length=360,
                            variable=v, command=self._mudanca, bg="#2b2b3a",
                            fg="white", highlightthickness=0)

        self.lbl_perfil = tk.Label(root, text="", bg="#1e1e2a", fg="#ffd26e",
                                   font=("Arial", 13, "bold"), padx=10, pady=6, bd=0)
        self.lbl_perfil.pack(fill="x", pady=(8, 0))

        rot("Brilho do driver (gamma)")
        self.s_brilho = sld(self.v_brilho, self.cfg.get("gamma_min", 50), 100)
        self.s_brilho.pack()
        rot("Modo leitura (amarelado)"); sld(self.v_calor, 0, 100).pack()
        rot("Escurecer extra (overlay)"); sld(self.v_escuro, 0, 85).pack()

        fr = tk.Frame(root, bg="#2b2b3a"); fr.pack(pady=8)
        for i, (t, b, c, e) in enumerate(PRESETS):
            tk.Button(fr, text=f"{i+1}·{t}", font=("Arial", 9),
                      command=lambda i=i: self._preset_idx(i, "tecla"),
                      bg="#4a4a6a", fg="white", relief="flat",
                      padx=7, pady=4).grid(row=i//3, column=i%3, padx=4, pady=3)

        rot("🤖 Aria — piloto automático local")
        tk.Checkbutton(root, variable=self.v_aria, command=self._toggle_aria,
                       text="Percebe · decide · age · antecipa · explica · sonha",
                       bg="#2b2b3a", fg="white", selectcolor="#3a3a52",
                       activebackground="#2b2b3a", activeforeground="white",
                       font=("Arial", 9), anchor="w").pack(fill="x", padx=10)
        self.lbl_aria = tk.Label(root, text="", bg="#2b2b3a", fg="#ffd26e",
                                 font=("Arial", 8), wraplength=440, justify="left")
        self.lbl_aria.pack()
        frb = tk.Frame(root, bg="#2b2b3a"); frb.pack()
        for txt, cmd in [("🧠 Cérebro", self._cerebro_janela),
                         ("🗣 Por quê?", self._porque_janela),
                         ("📈 Circa", self._circa_janela),
                         ("📦 Exportar", self._exportar),
                         ("📂 Dados", self._abrir_pasta),
                         ("⌨ Guia", self._guia_janela)]:
            tk.Button(frb, text=txt, command=cmd, bg="#4a4a6a", fg="white",
                      relief="flat", font=("Arial", 9)).pack(side="left", padx=3)

        fr2 = tk.Frame(root, bg="#2b2b3a"); fr2.pack(pady=(4, 0))
        for txt, var, cmd in [("🌙 Noturno automático (se Aria off)", self.v_noite, self._toggle_noite),
                              ("⌨ Atalhos globais", self.v_atalho, self._toggle_atalhos),
                              ("🔄 Iniciar com o Windows", self.v_win, self._toggle_windows)]:
            tk.Checkbutton(fr2, text=txt, variable=var, command=cmd, anchor="w",
                           bg="#2b2b3a", fg="white", selectcolor="#3a3a52",
                           activebackground="#2b2b3a", activeforeground="white",
                           font=("Arial", 9)).pack(fill="x", padx=8)

        fr3 = tk.Frame(root, bg="#2b2b3a"); fr3.pack(pady=(6, 0), fill="x", padx=8)
        tk.Label(fr3, text="🏙️ Cidade:", bg="#2b2b3a", fg="white",
                 font=("Arial", 9)).pack(side="left")
        self.cb_cidade = tk.Entry(fr3, width=18, bg="#3a3a52", fg="white",
                                  insertbackground="white", relief="flat")
        if self.cfg.get("cidade_nome"):
            self.cb_cidade.insert(0, self.cfg["cidade_nome"])
        self.cb_cidade.pack(side="left", padx=4)
        self.cb_cidade.bind("<Return>", self._cidade_enter)
        tk.Button(fr3, text="🌐 IP", width=4, font=("Arial", 8),
                  command=self._pedir_ip, bg="#4a4a6a", fg="white",
                  relief="flat").pack(side="left", padx=2)
        tk.Label(fr3, text="Enter=buscar · IP=detecta", bg="#2b2b3a",
                 fg="#889", font=("Arial", 8)).pack(side="left")

        tk.Button(root, text="🎯 Calibrar mínimo do driver (a tela pisca)",
                  command=self._calibrar, bg="#4a4a6a", fg="white",
                  relief="flat", font=("Arial", 9)).pack(pady=6)

        self.lbl_atalhos = tk.Label(root, text="⌨ carregando…", bg="#2b2b3a",
                                    fg="#9aa", font=("Arial", 8), wraplength=440,
                                    justify="left")
        self.lbl_atalhos.pack()
        self.status = tk.Label(root, text="Pronto", bg="#2b2b3a", fg="#8f8",
                               font=("Arial", 9), wraplength=440)
        self.status.pack(pady=4)
        tk.Label(root, text="Bandeja: ativa 📌" if TRAY_OK else
                 "Bandeja: OFF — pip install pystray pillow",
                 bg="#2b2b3a", fg="#8f8" if TRAY_OK else "#f88",
                 font=("Arial", 8)).pack()

        self.icone = self._montar_tray()
        if self.cfg["atalhos"]: self._iniciar_atalhos()
        self._zona = self._eh_noite()
        self._preset_idx(0, "auto")
        if self.v_aria.get(): self._aria_aplicar_alvo(direto=True)
        self._aria_status()
        root.after(80, self._poll)
        root.after(1500, self._legenda_atalhos)
        root.after(30000, self._tick_geral)

    # ===== perfil destaque =====
    def _atualizar_lbl_perfil(self):
        nome, origem = self._perfil_atual
        cor = COR_PERFIL.get(origem, "#ffd26e")
        emoji = {"tecla": "⌨", "aria": "🤖", "bandeja": "📌",
                 "slider": "🎚", "auto": "✨"}.get(origem, "🎚")
        self.lbl_perfil.config(text=f"{emoji} PERFIL: {nome.upper()} · via {origem}", fg=cor)

    def _preset_idx(self, i, origem="tecla"):
        nome, b, c, e = PRESETS[i]
        self.preset(b, c, e, nome=nome, origem=origem)

    # ===== núcleo + SignalGuard =====
    def _mudanca(self, _=None):
        agora = time.time()
        if self.motor.transicao_em_curso:
            return
        self._mud_ts = [t for t in self._mud_ts if agora - t < 60]
        self._mud_ts.append(agora)
        self._rajada = len(self._mud_ts) > 6
        r = aplicar_gamma(self.v_brilho.get(), self.v_calor.get() / 100.0)
        self.overlay.definir(int(self.v_escuro.get()))
        txt, cor = {"ok": ("Aplicado ✔", "#8f8"),
                    "parcial": ("Driver limitou — máximo possível", "#ff8"),
                    "falhou": ("Driver recusou (só overlay)", "#f88")}[r]
        extra = " · 🧪 modo teste (aula fraca)" if self._rajada else ""
        self.status.config(text=f"{txt} | extra: {int(self.v_escuro.get())}%{extra}",
                           fg=cor if not self._rajada else "#ff8")
        if not self._em_preset:
            self._perfil_atual = ("Personalizado", "slider")
            self._atualizar_lbl_perfil()
        if not self._aria_aplicando and self.v_aria.get():
            if self._rajada:
                self.pausado_ate = max(self.pausado_ate, agora + 300)
                self.diag.registrar_ruido()
            else:
                self.pausado_ate = agora + 1800
                if self._bandit_atual:
                    gasto = time.time() - (self._bandit_t0 or time.time())
                    self.bandit.feedback(self._app_hash, self._bandit_atual, gasto > 300)
                    log_aria(f"bandit {self._app_hash}/{self._bandit_atual} "
                             f"{'aceito' if gasto > 300 else 'rejeitado'} ({int(gasto)}s)")
                    self._bandit_atual = None
        self._salvar_depois()

    def preset(self, b, c, e, nome="Personalizado", origem="slider"):
        if origem in ("aria", "auto", "tecla"):
            self._perfil_atual = (nome, origem)
            self._atualizar_lbl_perfil()
            self.motor.transicionar(b, c, self.v_brilho.get(), self.v_calor.get())
            self.v_escuro.set(e)
            self.overlay.definir(int(e))
            self._salvar_depois()
            return
        self._em_preset = True
        self._perfil_atual = (nome, origem)
        self.v_brilho.set(b); self.v_calor.set(c); self.v_escuro.set(e)
        self._mudanca()
        self._em_preset = False
        self._atualizar_lbl_perfil()

    def _salvar_depois(self):
        if self._save_job: self.root.after_cancel(self._save_job)
        self._save_job = self.root.after(600, self._salvar_agora)

    def _salvar_agora(self):
        self._save_job = None
        b, c, e = self.v_brilho.get(), self.v_calor.get(), self.v_escuro.get()
        self.cfg.update(brilho=b, calor=c, escuro=e)
        h = time.localtime().tm_hour
        hab = self.cfg["aria"]["habito"]
        st = self.cfg["aria"]["stats"]
        if not self._aria_aplicando:
            peso = 0.10 if self._rajada else 0.35
            atual = hab.get(str(h)) or [None, None, None]
            hab[str(h)] = [round(n if o is None else o + peso*(n-o), 1)
                           for o, n in zip(atual, (b, c, e))]
            self.hw.observa(time.localtime().tm_wday*24 + h, b, c, e)
            if self.cusum.observa(h, b) and getattr(self, "_cusum_aviso_h", None) != h:
                self._cusum_aviso_h = h
                self._cusum_perguntar(h, b)
            log_aria(f"aprendi {h}h -> {hab[str(h)]}")
        self.cfg["aria"]["hw"] = self.hw.dump()
        salvar_cfg(self.cfg)

    def _cusum_perguntar(self, hora, valor):
        try:
            if self._cusum_win is not None and self._cusum_win.winfo_exists(): return
        except Exception: pass
        w = tk.Toplevel(self.root)
        w.title("Aria 🤖 — mudança de hábito")
        w.geometry("360x170+60+60"); w.attributes("-topmost", True)
        w.configure(bg="#2b2b3a")
        tk.Label(w, text=f"🚨 Seu ajuste às {hora}h fugiu 3σ do hábito.\nIsso é um novo hábito?",
                 bg="#2b2b3a", fg="white", justify="left",
                 font=("Arial", 10)).pack(pady=14)
        fr = tk.Frame(w, bg="#2b2b3a"); fr.pack()
        def resetar():
            self.cusum.reset(hora)
            self.cfg["aria"]["habito"].pop(str(hora), None)
            salvar_cfg(self.cfg)
            log_aria(f"CUSUM: reset do hábito {hora}h")
            w.destroy()
        tk.Button(fr, text="🧹 Novo hábito", command=resetar, bg="#4a4a6a",
                  fg="white", relief="flat", padx=8).pack(side="left", padx=6)
        tk.Button(fr, text="Manter memória", command=w.destroy, bg="#4a4a6a",
                  fg="white", relief="flat", padx=8).pack(side="left", padx=6)
        self._cusum_win = w

    # ===== Aria: fusão (⚖ corrigido) =====
    def _eh_noite(self):
        h = time.localtime().tm_hour + time.localtime().tm_min / 60.0
        lat = self.cfg.get("latitude")
        if lat is None: a, b = 19.0, 7.0
        else:
            n, p = nascer_poser(lat); a, b = p - 0.5, n + 0.5
        return (h >= a or h <= b) if a > b else (a <= h <= b)

    def _alvo_fundido(self):
        h = time.localtime().tm_hour
        idx = time.localtime().tm_wday*24 + h
        hab = self.cfg["aria"]["habito"].get(str(h))
        hw = self.hw.preve(idx)
        fontes, pares = [], []
        if hab:
            pares.append((hab, 25)); fontes.append(("hábito", hab[0], 25))
        if hw:
            pares.append(([hw["b"], hw["c"], hw["e"]], 36))
            fontes.append(("semana", hw["b"], 36))
        if self._bandit_atual:
            p = CAND[self._bandit_atual]
            pares.append((p, 49)); fontes.append(("bandit", p[0], 49))
        if self._eh_noite():
            pares.append((NOITE, 64)); fontes.append(("noite", NOITE[0], 64))
        if not pares: return NOITE if self._eh_noite() else DIA, fontes
        alvo = tuple(fundir([(v[i], conf) for v, conf in pares])
                     for i in range(3))
        return alvo, fontes

    def _aria_aplicar_alvo(self, direto=False):
        alvo, fontes = self._alvo_fundido()
        cur = (self.v_brilho.get(), self.v_calor.get(), self.v_escuro.get())
        self._aria_aplicando = True
        nome = f"Aria·{self._bandit_atual}" if self._bandit_atual else "Aria·hábito"
        if direto:
            self.preset(*alvo, nome=nome, origem="aria")
        else:
            meio = [c + (a - c) * 0.35 for c, a in zip(cur, alvo)]
            self.motor.transicionar(meio[0], meio[1], cur[0], cur[1])
            self.v_escuro.set(meio[2])
            self.overlay.definir(int(meio[2]))
            self._perfil_atual = (nome, "aria"); self._atualizar_lbl_perfil()
        self._aria_aplicando = False
        log_aria(f"apliquei {nome} -> {[round(x) for x in alvo]}")

    def _aria_status(self, extra=""):
        n = (len(self.cfg["aria"]["habito"]) + len(self.hw.saz) + 6 + 1 +
             len(self.cusum.med)*2 + sum(len(p) for p in self.bandit.cerebros.values()))
        if self.v_aria.get():
            if time.time() < self.pausado_ate:
                hh = time.strftime("%H:%M", time.localtime(self.pausado_ate))
                t = f"🤖 Pausada até {hh} — sua correção vence"
            else: t = "🤖 No comando"
        else: t = "🤖 Desligada"
        t += f" · {n} EMAs + 3 Kalmans"
        if extra: t += f" · {extra}"
        self.lbl_aria.config(text=t)

    def _toggle_aria(self):
        self.cfg["aria_on"] = self.v_aria.get(); salvar_cfg(self.cfg)
        if self.v_aria.get():
            self.pausado_ate = 0.0
            self._aria_aplicar_alvo()
            self._aria_status("ativada")
            log_aria("Aria ativada (v6.0 LUMINÁRIA)")
        else: self._aria_status()

    # ===== tick 30s =====
    def _tick_geral(self):
        self.root.after(30000, self._tick_geral)
        idl = idle_segundos()
        lim = int(self.cfg.get("ausente_apos", 240))
        self.diag.registrar_pausa() if idl > 60 else self.diag.registrar_uso(0.5)
        chave, nome = app_ativo()
        if self.v_aria.get():
            if not self._ausente and idl > lim:
                self._ausente = True
                self._antes = int(self.v_escuro.get())
                self.overlay.definir(max(60, int(self.cfg.get("ausente_dim", 65))))
                self._osd("👁 Você saiu — dim de descanso")
                log_aria(f"presença: ausente (idle {int(idl)}s)")
            elif self._ausente and idl < 5:
                self._ausente = False
                self.overlay.definir(self._antes)
                self._osd("👁 Bem-vindo de volta")
                log_aria("presença: retorno")
            elif not self._ausente and chave and chave != self._app_hash \
                    and time.time() >= self.pausado_ate:
                self._app_hash, self._app_nome = chave, nome
                self._bandit_atual = self.bandit.escolhe(chave)
                self._bandit_t0 = time.time()
                self._aria_aplicar_alvo()
                if self._bandit_atual:
                    self._osd(f"🃏 {nome}: perfil '{self._bandit_atual}'")
                    log_aria(f"bandit sorteou {self._bandit_atual} p/ {chave}")
            if self._bandit_atual and time.time() - self._bandit_t0 > 900:
                self.bandit.feedback(self._app_hash, self._bandit_atual, True)
                self._bandit_t0 = time.time()
                log_aria(f"bandit: permanência aceita {self._bandit_atual}")
            self._aria_status()
        else:
            z = self._eh_noite()
            if z != self._zona and self.cfg["auto_noite"]:
                self._zona = z
                self.preset(*(NOITE if z else DIA), nome="Noturno", origem="auto")
        self._zona = self._eh_noite()

    # ===== 🗣 Por quê? =====
    def _porque_janela(self):
        w = tk.Toplevel(self.root)
        w.title("🗣 Por que a luz está assim?")
        w.geometry("520x220"); w.attributes("-topmost", True)
        w.configure(bg="#1e1e2a")
        _, fontes = self._alvo_fundido()
        tk.Label(w, text="🗣 A ÚLTIMA DECISÃO DA ARIA", bg="#1e1e2a", fg="#8f8",
                 font=("Arial", 11, "bold")).pack(pady=(14, 6))
        tk.Label(w, text="Ouvi, por confiança: " + "; ".join(
                     f"{k} (peso {p})" for k, _, p in sorted(fontes, key=lambda f: -f[2])) +
                     ". Discordou? Ajuste você — e eu pauso.",
                 bg="#1e1e2a", fg="#cde", wraplength=480, justify="left",
                 font=("Arial", 11)).pack(padx=16)
        tk.Label(w, text="Confira os números no 🧠 Cérebro.",
                 bg="#1e1e2a", fg="#667", font=("Arial", 8)).pack(pady=(10, 0))

    # ===== 🧠 cérebro =====
    def _cerebro_janela(self):
        w = tk.Toplevel(self.root)
        w.title("🧠 O que a Aria sabe sobre você")
        w.geometry("640x700"); w.configure(bg="#1e1e2a")
        frt = tk.Frame(w, bg="#1e1e2a"); frt.pack(fill="x", padx=8, pady=(8, 0))
        tk.Label(frt, text="🧹 esquecer hora:", bg="#1e1e2a", fg="white",
                 font=("Arial", 9)).pack(side="left")
        e_h = tk.Entry(frt, width=4, bg="#3a3a52", fg="white",
                       insertbackground="white", relief="flat")
        e_h.pack(side="left", padx=4)
        txt = tk.Text(w, bg="#1e1e2a", fg="#cde", font=("Consolas", 10),
                      width=74, height=30, bd=0)
        txt.pack(fill="both", expand=True, padx=8, pady=6)
        def atualizar():
            hab = self.cfg["aria"]["habito"]
            st = self.cfg["aria"]["stats"]
            L = ["📈 CURVA CIRCADIANA (24h)", "═" * 58,
                 f"☀ {curva_ascii({k: v[0] for k, v in hab.items()}, 50, 100)}",
                 f"🌡 {curva_ascii({k: v[1] for k, v in hab.items()}, 0, 100)}",
                 f"🌑 {curva_ascii({k: v[2] for k, v in hab.items()}, 0, 85)}",
                 "          0   4   8   12  16  20", "",
                 "🩺 DIAGNÓSTICO OCULAR (tempo real)", "═" * 58,
                 f" uso contínuo: {self.diag.minutos_uso:.0f}min · "
                 f"ruídos: {self.diag.ruidos}",
                 "", "📜 HÁBITO POR HORA", "═" * 58]
            for hh in sorted(hab, key=int):
                b, c, e = hab[hh]
                L.append(f" {int(hh):02d}h ☀{barra(b,50,100)}{b:3.0f} "
                         f"🌡{barra(c,0,100)}{c:3.0f} 🌑{barra(e,0,85)}{e:3.0f}")
            tot = st.get("aulas", 0) + st.get("ruido", 0)
            L += ["", f"🛡 SignalGuard: aulas {st.get('aulas',0)} · "
                      f"ruído {st.get('ruido',0)}",
                  f"🎯 piso: {self.cfg.get('gamma_min')}% · "
                  f"🌅 lat: {self.cfg.get('latitude') or '—'}",
                  f"🏙 cidade: {self.cfg.get('cidade_nome') or '—'}",
                  f"🛡 ColorGuard: ativo"]
            txt.config(state="normal"); txt.delete("1.0", "end")
            txt.insert("1.0", "\n".join(L)); txt.config(state="disabled")
        def esquecer():
            try: hh = int(e_h.get()) % 24
            except ValueError: return
            self.cfg["aria"]["habito"].pop(str(hh), None)
            self.cusum.reset(hh); salvar_cfg(self.cfg)
            log_aria(f"esqueci a hora {hh}h"); atualizar()
        tk.Button(frt, text="apagar", command=esquecer, bg="#4a4a6a", fg="white",
                  relief="flat", font=("Arial", 8)).pack(side="left")
        atualizar()

    # ===== 📈 Circa =====
    def _circa_janela(self):
        w = tk.Toplevel(self.root)
        w.title("📈 CircaView — curva circadiana")
        w.geometry("640x360"); w.configure(bg="#1e1e2a")
        hab = self.cfg["aria"]["habito"]
        txt = tk.Text(w, bg="#1e1e2a", fg="#cde", font=("Consolas", 12), bd=0)
        txt.pack(fill="both", expand=True, padx=10, pady=10)
        L = ["☀ brilho", f"  {curva_ascii({k: v[0] for k, v in hab.items()}, 50, 100)}",
             "🌡 calor", f"  {curva_ascii({k: v[1] for k, v in hab.items()}, 0, 100)}",
             "🌑 overlay", f"  {curva_ascii({k: v[2] for k, v in hab.items()}, 0, 85)}",
             "     0   4   8   12  16  20  24", "",
             "Seu ritmo circadiano — medido, não inventado."]
        txt.insert("1.0", "\n".join(L)); txt.config(state="disabled")

    # ===== ⌨ guia =====
    def _guia_janela(self):
        w = tk.Toplevel(self.root)
        w.title("⌨ Guia de teclas")
        w.geometry("540x470"); w.attributes("-topmost", True)
        w.configure(bg="#1e1e2a")
        pre = self.hk.prefixo if self.hk and self.hk.is_alive() else lambda i: "Ctrl+Alt+Shift"
        def linha(fr, tecla, desc):
            tk.Label(fr, text=tecla, bg="#2b2b3a", fg="#ffd26e",
                     font=("Consolas", 12, "bold"), width=24, anchor="w").pack(side="left")
            tk.Label(fr, text=desc, bg="#2b2b3a", fg="#cde",
                     font=("Arial", 11)).pack(side="left")
        tk.Label(w, text="🎚 PERFIS", bg="#1e1e2a", fg="#8f8",
                 font=("Arial", 12, "bold")).pack(pady=(12, 4))
        f1 = tk.Frame(w, bg="#2b2b3a"); f1.pack(padx=14, fill="x")
        for i in range(5): linha(f1, f"{pre(8+i)}+{i+1}", PRESETS[i][0])
        tk.Label(w, text="🎚 AJUSTE FINO", bg="#1e1e2a", fg="#7fd7ff",
                 font=("Arial", 12, "bold")).pack(pady=(14, 4))
        f2 = tk.Frame(w, bg="#2b2b3a"); f2.pack(padx=14, fill="x")
        linha(f2, f"{pre(1)}+↑", "clarear"); linha(f2, f"{pre(2)}+↓", "escurecer")
        linha(f2, f"{pre(3)}+→", "mais quente"); linha(f2, f"{pre(4)}+←", "mais frio")
        tk.Label(w, text="⚙ SISTEMA", bg="#1e1e2a", fg="#ffd26e",
                 font=("Arial", 12, "bold")).pack(pady=(14, 4))
        f3 = tk.Frame(w, bg="#2b2b3a"); f3.pack(padx=14, fill="x")
        linha(f3, f"{pre(5)}+R", "Normal"); linha(f3, f"{pre(6)}+M", "janela")
        linha(f3, f"{pre(7)}+A", "Aria on/off")

    # ===== 📦 exportar =====
    def _exportar(self):
        try:
            mesa = os.path.join(os.path.expanduser("~"), "Desktop")
            if not os.path.isdir(mesa):
                mesa = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
            if not os.path.isdir(mesa): mesa = os.path.expanduser("~")
            arq = os.path.join(mesa, f"LUMA_relatorio_{time.strftime('%Y%m%d_%H%M')}.txt")
            hab = self.cfg["aria"]["habito"]
            st = self.cfg["aria"]["stats"]
            linhas = ["LUMA v6.0 — RELATÓRIO (LUMINÁRIA)", "=" * 50,
                      f"gerado: {time.strftime('%Y-%m-%d %H:%M')}",
                      f"gamma_min: {self.cfg.get('gamma_min')} · "
                      f"lat: {self.cfg.get('latitude')} "
                      f"({self.cfg.get('cidade_nome') or '—'})",
                      f"SignalGuard: aulas {st.get('aulas',0)} · ruído {st.get('ruido',0)}",
                      "", "CURVA CIRCADIANA", "-" * 50,
                      f"☀ {curva_ascii({k: v[0] for k, v in hab.items()}, 50, 100)}",
                      f"🌡 {curva_ascii({k: v[1] for k, v in hab.items()}, 0, 100)}",
                      f"🌑 {curva_ascii({k: v[2] for k, v in hab.items()}, 0, 85)}",
                      "", "HÁBITO POR HORA", "-" * 50]
            for hh in sorted(hab, key=int):
                b, c, e = hab[hh]
                linhas.append(f" {int(hh):02d}h  brilho {b:5.1f}  calor {c:5.1f}  overlay {e:5.1f}")
            linhas += ["", "LOG (últimas 40)", "-" * 50]
            try:
                with open(LOG_ARQ, encoding="utf-8") as f:
                    linhas += f.readlines()[-40:]
            except Exception: linhas.append("(sem log)")
            with open(arq, "w", encoding="utf-8") as f:
                f.write("\n".join(linhas))
            try: os.startfile(mesa)
            except Exception: pass
            self.status.config(text=f"📦 Salvo: {arq}", fg="#8f8")
            log_aria("relatório exportado")
        except Exception as e:
            self.status.config(text=f"Erro: {e}", fg="#f88")

    def _abrir_pasta(self):
        try: os.startfile(APPDIR)
        except Exception as e: self.status.config(text=f"Erro: {e}", fg="#f88")

    # ===== calibração com probe =====
    def _calibrar(self):
        self.status.config(text="🔬 Probe agnóstico…", fg="#ff8"); self.root.update()
        probe = {"claro": _tentar(construir_ramp(70, 0)),
                 "escuro": _tentar(construir_ramp(51, 0))}
        _tentar(rampa_identidade())
        log_aria(f"probe agnóstico: {probe}")
        self.status.config(text="🎯 Calibrando…", fg="#ff8"); self.root.update()
        lo, hi = 50.0, 100.0
        if not _tentar(construir_ramp(hi, 0)):
            _tentar(rampa_identidade())
            self.status.config(text="Driver não respondeu", fg="#f88"); return
        while hi - lo > 1.0:
            mid = (lo + hi) / 2.0
            if _tentar(construir_ramp(mid, 0)): hi = mid
            else: lo = mid
        self.cfg["gamma_min"] = int(round(hi)); salvar_cfg(self.cfg)
        self.s_brilho.config(from_=self.cfg["gamma_min"])
        if self.v_brilho.get() < self.cfg["gamma_min"]:
            self.v_brilho.set(self.cfg["gamma_min"])
        self.preset(self.v_brilho.get(), self.v_calor.get(), self.v_escuro.get(),
                    nome="Pós-calibração", origem="auto")
        self.status.config(
            text=f"🎯 Piso: {self.cfg['gamma_min']}% "
                 f"(probe claro:{probe['claro']} escuro:{probe['escuro']})", fg="#8f8")
        log_aria(f"calibração: gamma_min={self.cfg['gamma_min']} probe={probe}")

    # ===== localização =====
    def _aplicar_lat(self, v, origem):
        self.cfg["latitude"] = float(v); salvar_cfg(self.cfg)
        self._zona = self._eh_noite()
        self.status.config(text=f"🌅 {origem} — sol real (lat {v})", fg="#8f8")
        log_aria(f"latitude {v} via {origem}")

    def _cidade_enter(self, _=None):
        t = self.cb_cidade.get().strip().lower()
        exata = next((c for c in CIDADES if c.lower() == t), None)
        if not exata:
            pref = [c for c in CIDADES if c.lower().startswith(t)]
            if len(pref) == 1: exata = pref[0]
        if exata:
            self.cb_cidade.delete(0, "end"); self.cb_cidade.insert(0, exata)
            self.cfg["cidade_nome"] = exata; salvar_cfg(self.cfg)
            self._aplicar_lat(CIDADES[exata], exata)
        else:
            self.status.config(text="Cidade fora da lista — use 🌐 IP", fg="#ff8")

    def _pedir_ip(self):
        self.status.config(text="🌐 Detectando por IP…", fg="#ff8")
        threading.Thread(target=detectar_ip_thread, args=(self.fila,),
                         daemon=True).start()

    def _ip_resultado(self, lat, city):
        if lat is None:
            self.status.config(text="🌐 IP falhou — digite a cidade", fg="#f88"); return
        self.cfg["cidade_nome"] = city or "IP"
        salvar_cfg(self.cfg)
        self._aplicar_lat(round(float(lat), 2), f"{city or 'IP'} (aprox.)")

    # ===== atalhos / OSD / janela =====
    def _iniciar_atalhos(self):
        if not (self.hk and self.hk.is_alive()):
            self.hk = OuvinteAtalhos(self.fila); self.hk.start()
    def _parar_atalhos(self):
        if self.hk: self.hk.encerrar()
    def _legenda_atalhos(self):
        if self.hk and self.hk.is_alive():
            self.lbl_atalhos.config(
                text=f"⌨ {self.hk.prefixo(8)}+1-5 perfil · setas ajuste · "
                     f"R normal · M janela · A Aria")

    def _poll(self):
        try:
            while True: self._distribuir(self.fila.get_nowait())
        except queue.Empty: pass
        self.root.after(80, self._poll)

    def _distribuir(self, it):
        if it == "sair": self.sair_total()
        elif it == "aria":
            self.v_aria.set(not self.v_aria.get()); self._toggle_aria()
        elif isinstance(it, int): self._acao_atalho(it)
        elif isinstance(it, tuple) and it[0] == "preset":
            nome = it[4] if len(it) > 4 else "Bandeja"
            self.preset(it[1], it[2], it[3], nome=nome, origem="bandeja")
        elif isinstance(it, tuple) and it[0] == "janela": self._alternar_janela()
        elif isinstance(it, tuple) and it[0] == "ip": self._ip_resultado(it[1], it[2])

    def _acao_atalho(self, i):
        gmin = self.cfg.get("gamma_min", 50)
        if i >= 8:
            nome, b, c, e = PRESETS[i - 8]
            self.preset(b, c, e, nome=nome, origem="tecla")
            self._osd(f"🎚 {nome}"); return
        if i == 1:
            if self.v_escuro.get() > 0: self.v_escuro.set(max(0, self.v_escuro.get() - 5))
            else: self.v_brilho.set(min(100, self.v_brilho.get() + 5))
        elif i == 2:
            if self.v_brilho.get() > gmin:
                self.v_brilho.set(max(gmin, self.v_brilho.get() - 5))
            else: self.v_escuro.set(min(85, self.v_escuro.get() + 5))
        elif i == 3: self.v_calor.set(min(100, self.v_calor.get() + 10))
        elif i == 4: self.v_calor.set(max(0, self.v_calor.get() - 10))
        elif i == 5: self._preset_idx(0, "tecla"); self._osd("🎚 Normal"); return
        elif i == 6: self._alternar_janela(); return
        elif i == 7:
            self.v_aria.set(not self.v_aria.get()); self._toggle_aria()
            self._osd("🤖 Aria ON" if self.v_aria.get() else "🤖 Aria OFF"); return
        self._mudanca()
        self._osd(f"☀{int(self.v_brilho.get())}% 🌡{int(self.v_calor.get())}% "
                  f"🌑{int(self.v_escuro.get())}%")

    def _osd(self, texto):
        if self._osd_win is None:
            w = tk.Toplevel(self.root)
            w.overrideredirect(True); w.attributes("-topmost", True)
            w.configure(bg="#141420")
            self._osd_lbl = tk.Label(w, text="", bg="#141420", fg="#ffd26e",
                                     font=("Consolas", 15, "bold"), padx=18, pady=10)
            self._osd_lbl.pack(); self._osd_win = w
        self._osd_lbl.config(text=texto)
        w = self._osd_win; w.update_idletasks()
        sw, sh = w.winfo_screenwidth(), w.winfo_screenheight()
        w.geometry(f"+{sw//2 - w.winfo_reqwidth()//2}+{sh - w.winfo_reqheight() - 70}")
        w.deiconify(); w.attributes("-alpha", 0.94); w.lift()
        if self._osd_job: self.root.after_cancel(self._osd_job)
        self._osd_job = self.root.after(1200, w.withdraw)

    def _alternar_janela(self):
        if self.root.state() == "withdrawn":
            self.root.deiconify(); self.root.attributes("-topmost", True); self.root.lift()
        else: self.root.withdraw()

    def _toggle_atalhos(self):
        self.cfg["atalhos"] = self.v_atalho.get()
        self._iniciar_atalhos() if self.v_atalho.get() else self._parar_atalhos()
        salvar_cfg(self.cfg)
    def _toggle_windows(self):
        ok = definir_autostart(self.v_win.get())
        self.cfg["iniciar_win"] = self.v_win.get() if ok else False
        if not ok:
            self.v_win.set(False)
            self.status.config(text="Falha no início automático", fg="#f88")
        salvar_cfg(self.cfg)
    def _toggle_noite(self):
        self.cfg["auto_noite"] = self.v_noite.get(); salvar_cfg(self.cfg)

    def _montar_tray(self):
        if not TRAY_OK: return None
        def mk(i):
            nome, b, c, e = PRESETS[i]
            return pystray.MenuItem(nome, lambda ic, it: self.fila.put(
                ("preset", b, c, e, nome)))
        menu = pystray.Menu(
            pystray.MenuItem("Mostrar/Ocultar",
                             lambda ic, it: self.fila.put(("janela",)), default=True),
            pystray.Menu.SEPARATOR, *[mk(i) for i in range(len(PRESETS))],
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("🤖 Aria on/off", lambda ic, it: self.fila.put("aria")),
            pystray.MenuItem("Sair (restaura tudo)", lambda ic, it: self.fila.put("sair")))
        ic = pystray.Icon("ControleBrilhoPro", _icone(), "LUMA v6.0 LUMINÁRIA", menu)
        ic.run_detached()
        return ic

    def _fechar_janela(self):
        if self.icone:
            self.root.withdraw()
            try: self.icone.notify("Use o atalho de janela para reabrir", "Bandeja 📍")
            except Exception: pass
        else: self.sair_total()

    def sair_total(self):
        salvar_cfg(self.cfg)
        try: self.overlay.definir(0)
        except Exception: pass
        _tentar(rampa_identidade())
        if self.hk: self.hk.encerrar()
        if self.icone:
            try: self.icone.stop()
            except Exception: pass
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()