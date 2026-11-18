#!/usr/bin/env python3
"""
L4D2 Player Watcher
Lee console.log en tiempo real y avisa cuando aparece un Steam ID vigilado.

Uso:
    py l4d2_watcher.py "C:\ruta\Left 4 Dead 2\left4dead2\console.log"

Coloca los Steam ID vigilados, uno por línea, en watchlist.txt junto a este script.
Sin argumentos (p. ej. como watcher.exe dentro de la carpeta left4dead2), usa el
console.log de su propia carpeta y abre el juego; --no-game evita abrirlo.
Admite STEAM_1:X:Y y SteamID64.
"""

from __future__ import annotations

import csv
import os
import re
import sys
import time
import threading
from pathlib import Path

POLL_SECONDS = 0.25
# Carpeta del programa: la del .exe empaquetado o la del script.
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "configWatcher.txt"

DEFAULT_CONFIG_TEXT = """# Configuración de L4D2 Player Watcher.
# Edita los valores y vuelve a abrir el programa.
# Los archivos se buscan en la misma carpeta que el programa.

# Segundos antes de volver a notificar al mismo jugador
NOTIFY_COOLDOWN = 60

# Watchlist personal (un Steam ID por línea, comentarios con //)
WATCHLIST_FILE_NAME = "watchlist.txt"

# Watchlist público (CSV: STEAMID,C1,C2,C3,R,T,O)
PUBLIC_WATCHLIST_FILE_NAME = "public_watchlist.csv"
"""

def load_config() -> dict[str, str]:
    # Lee configWatcher.txt (CLAVE = valor). Si no existe, lo crea con los valores por defecto.
    values = {
        "NOTIFY_COOLDOWN": "60",
        "WATCHLIST_FILE_NAME": "watchlist.txt",
        "PUBLIC_WATCHLIST_FILE_NAME": "public_watchlist.csv",
    }
    if not CONFIG_FILE.exists():
        try:
            CONFIG_FILE.write_text(DEFAULT_CONFIG_TEXT, encoding="utf-8")
            print(f"Se creó {CONFIG_FILE.name} con los valores por defecto.")
        except OSError as exc:
            print(f"[AVISO] No se pudo crear {CONFIG_FILE.name}: {exc}")
        return values

    for line in CONFIG_FILE.read_text(encoding="utf-8-sig").splitlines():
        line = line.split("#", 1)[0].split("//", 1)[0].strip()
        if not line:
            continue
        key, sep, value = line.partition("=")
        key = key.strip().upper()
        value = value.strip().strip("\"'").strip()
        if not sep or key not in values:
            print(f"[AVISO] Línea no reconocida en {CONFIG_FILE.name}: {line}")
            continue
        if value:
            values[key] = value
    return values

_config = load_config()

try:
    NOTIFY_COOLDOWN = max(0.0, float(_config["NOTIFY_COOLDOWN"]))  # segundos entre avisos del mismo jugador
except ValueError:
    print(f"[AVISO] NOTIFY_COOLDOWN inválido en {CONFIG_FILE.name}; se usará 60.")
    NOTIFY_COOLDOWN = 60.0

WATCHLIST_FILE = BASE_DIR / _config["WATCHLIST_FILE_NAME"]
PUBLIC_WATCHLIST_FILE = BASE_DIR / _config["PUBLIC_WATCHLIST_FILE_NAME"]
PUBLIC_TYPES = ("C1", "C2", "C3", "R", "T", "O")  # orden de columnas del CSV

STEAM_ID_RE = re.compile(r"\b(STEAM_\d+:[01]:\d+)\b", re.IGNORECASE)
STEAM64_RE = re.compile(r"\b(7656119\d{10})\b")
PLAYER_RE = re.compile(
    r'#\s*\d+\s+\d+\s+"(.*?)"\s+(STEAM_\d+:[01]:\d+)',
    re.IGNORECASE,
)

def steam2_to_64(value: str) -> str | None:
    match = re.fullmatch(r"STEAM_\d+:([01]):(\d+)", value.strip(), re.IGNORECASE)
    if not match:
        return None
    y = int(match.group(1))
    z = int(match.group(2))
    return str(76561197960265728 + z * 2 + y)

def steam64_to_2(value: str) -> str:
    account_id = int(value) - 76561197960265728
    return f"STEAM_0:{account_id % 2}:{account_id // 2}"

def normalize_id(value: str) -> str | None:
    value = value.strip()
    if STEAM64_RE.fullmatch(value):
        return value
    return steam2_to_64(value)

def load_watchlist() -> dict[str, str]:
    if not WATCHLIST_FILE.exists():
        WATCHLIST_FILE.write_text(
            "# Un Steam ID por línea. Ejemplos:\n"
            "# STEAM_1:1:12345 //Comentario opcional\n"
            "# 76561197960290418\n",
            encoding="utf-8",
        )
        print(f"Se creó {WATCHLIST_FILE}. Agrega los Steam ID y vuelve a ejecutar.")
        return {}

    watched: dict[str, str] = {}
    for line in WATCHLIST_FILE.read_text(encoding="utf-8-sig").splitlines():
        line, _, comment = line.partition("//")
        line = line.split("#", 1)[0].strip()
        comment = comment.strip()
        if not line:
            continue
        normalized = normalize_id(line)
        if normalized:
            watched[normalized] = comment
        else:
            print(f"[AVISO] ID no reconocido en {WATCHLIST_FILE.name}: {line}")
    return watched

def public_label(counts: dict[str, int]) -> str:
    # Ej.: {"C1": 1, "C2": 1, "C3": 3, "R": 5} -> "C1 [1] C2 [1] C3 [3] R [5] T [0] O [0]"
    return " ".join(f"{kind} [{counts.get(kind, 0)}]" for kind in PUBLIC_TYPES)

def load_public_watchlist() -> dict[str, dict[str, int]]:
    # CSV: STEAMID,C1,C2,C3,R,T,O  (cantidad de reportes por tipo)
    if not PUBLIC_WATCHLIST_FILE.exists():
        print(f"[AVISO] No se encontró {PUBLIC_WATCHLIST_FILE.name}; lista pública vacía.")
        return {}

    watched: dict[str, dict[str, int]] = {}
    with PUBLIC_WATCHLIST_FILE.open("r", encoding="utf-8-sig", newline="") as f:
        for i, row in enumerate(csv.reader(f)):
            if not row or not row[0].strip() or row[0].strip().startswith("#"):
                continue
            normalized = normalize_id(row[0])
            if not normalized:
                if i > 0:  # la primera fila puede ser el encabezado
                    print(f"[AVISO] ID no reconocido en {PUBLIC_WATCHLIST_FILE.name}: {row[0].strip()}")
                continue

            counts: dict[str, int] = {}
            for kind, cell in zip(PUBLIC_TYPES, row[1:]):
                try:
                    counts[kind] = max(0, int(cell))
                except ValueError:
                    counts[kind] = 0
            if not any(counts.values()):
                continue

            # Un SteamID repetido (incluso en otro formato) se suma en una sola entrada.
            entry = watched.setdefault(normalized, {kind: 0 for kind in PUBLIC_TYPES})
            for kind, n in counts.items():
                entry[kind] += n
    return watched

def notify(title: str, message: str, url: str = "") -> None:
    # Notificación de Windows mediante winotify; si no está instalado,
    # se usa un aviso en consola y un sonido del sistema.
    # Si se pasa url, al hacer clic en la notificación se abre en el navegador.
    try:
        from winotify import Notification, audio
        toast = Notification(app_id="L4D2 Player Watcher", title=title, msg=message, launch=url)
        toast.set_audio(audio.Default, loop=False)
        toast.show()
    except Exception:
        print("\a")
        print(f"\n*** {title}: {message} ***\n")

def parse_status_block(lines: list[str]) -> dict[str, str]:
    players: dict[str, str] = {}
    for line in lines:
        match = PLAYER_RE.search(line)
        if match:
            name, steam_id = match.groups()
            normalized = normalize_id(steam_id)
            if normalized:
                players[normalized] = name
    return players

def pause_and_return(code: int) -> int:
    # Al abrir el .exe con doble clic, evita que la ventana se cierre antes de leer el mensaje.
    if getattr(sys, "frozen", False):
        input("\nPresiona Enter para salir...")
    return code

def launch_game() -> None:
    try:
        os.startfile("steam://rungameid/550")  # solo Windows; usa las opciones de lanzamiento de Steam
    except Exception as exc:
        print(f"[AVISO] No se pudo abrir el juego automáticamente: {exc}")

def main() -> int:
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    args = [a for a in sys.argv[1:] if not a.startswith("--")]

    # Por defecto, console.log está en la misma carpeta que el programa.
    log_path = Path(args[0]).expanduser() if args else BASE_DIR / "console.log"

    watched = load_watchlist()
    public_watched = load_public_watchlist()
    if not watched and not public_watched:
        print(f"La lista de vigilancia está vacía. Edita {WATCHLIST_FILE.name} o {PUBLIC_WATCHLIST_FILE.name} y vuelve a ejecutar.")
        return pause_and_return(0)

    print("L4D2 Player Watcher iniciado.")
    print(f"Registro: {log_path}")
    print(f"Steam ID vigilados: {len(watched)}")
    print(f"Steam ID en lista pública: {len(public_watched)}")

    if "--no-game" not in flags:
        launch_game()

    # Empezar al final del registro para no procesar partidas antiguas.
    warned_missing = False
    if log_path.is_file():
        offset = log_path.stat().st_size
    else:
        offset = 0
        warned_missing = True
        if log_path.parent.name.lower() != "left4dead2":
            print("[AVISO] Este programa debería estar en la carpeta left4dead2, junto a console.log.")
        print("Esperando a que el juego cree console.log (requiere la opción de lanzamiento -condebug)...")
    print("Esperando nuevas consultas status. Ctrl+C para salir.\n")
    partial = ""
    status_lines: list[str] = []
    inside_status = False
    last_notified: dict[str, float] = {}
    last_notified_public: dict[str, float] = {}

    try:
        while True:
            try:
                size = log_path.stat().st_size
                if size < offset:  # el archivo fue truncado/reiniciado
                    offset = 0
                    partial = ""
                    status_lines.clear()
                    inside_status = False

                with log_path.open("r", encoding="utf-8", errors="replace") as log:
                    log.seek(offset)
                    chunk = log.read()
                    offset = log.tell()
                warned_missing = False

                if chunk:
                    partial += chunk
                    complete_lines = partial.splitlines(keepends=True)
                    partial = ""
                    if complete_lines and not complete_lines[-1].endswith(("\n", "\r")):
                        partial = complete_lines.pop()

                    for raw_line in complete_lines:
                        line = raw_line.rstrip("\r\n")

                        if "# userid name uniqueid" in line or re.search(r"\bplayers\s*:", line):
                            inside_status = True
                            status_lines = []

                        if inside_status:
                            status_lines.append(line)

                        if inside_status and re.search(r"#end\b", line):
                            players = parse_status_block(status_lines)
                            now = time.monotonic()

                            # Notifica a cada jugador vigilado presente, como máximo
                            # una vez cada NOTIFY_COOLDOWN segundos.
                            for steam64 in sorted(set(players) & watched.keys()):
                                last = last_notified.get(steam64)
                                if last is not None and now - last < NOTIFY_COOLDOWN:
                                    continue
                                last_notified[steam64] = now

                                name = players.get(steam64, "Jugador desconocido")
                                comment = watched[steam64]
                                label = f"{name} ({comment})" if comment else name
                                notify(
                                    "Jugador vigilado detectado en L4D2",
                                    f"{label}\n{steam64_to_2(steam64)} — {steam64}",
                                )
                                print(f"[DETECTADO] {label} — {steam64_to_2(steam64)} — {steam64}")

                            # Lista pública: mismo cooldown, pero llevado por separado.
                            # Si el jugador está en la lista personal, esa tiene prioridad.
                            for steam64 in sorted(set(players) & public_watched.keys()):
                                if steam64 in watched:
                                    continue
                                last = last_notified_public.get(steam64)
                                if last is not None and now - last < NOTIFY_COOLDOWN:
                                    continue
                                last_notified_public[steam64] = now

                                name = players.get(steam64, "Jugador desconocido")
                                counts = public_watched[steam64]
                                label = f"{name} ({public_label(counts)})"
                                url = f"https://steamcommunity.com/profiles/{steam64}"
                                prefix = "[Reporte Público]"
                                notify(
                                    f"{prefix} Jugador vigilado detectado en L4D2",
                                    f"{label}\n{steam64_to_2(steam64)} — {url}",
                                    url,
                                )
                                print(f"{prefix} [DETECTADO] {label} — {steam64_to_2(steam64)} — {steam64} — {url}")

                            status_lines = []
                            inside_status = False

                time.sleep(POLL_SECONDS)

            except FileNotFoundError:
                if not warned_missing:
                    print("[AVISO] No se encuentra console.log; esperando...")
                    warned_missing = True
                time.sleep(1)

    except KeyboardInterrupt:
        print("\nMonitor detenido.")
        return 0

if __name__ == "__main__":
    raise SystemExit(main())
