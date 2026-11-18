# L4D2 Player Watcher

Programa para Windows que lee el `console.log` de Left 4 Dead 2 y avisa con una notificación cuando aparece en tu partida un jugador de tu lista de vigilancia o de una lista pública de reportes.

## Instalación (sin Python)

1. Descarga `watcher.exe` desde [Releases](../../releases).
2. Cópialo a la carpeta `left4dead2` del juego, junto a `console.log`. Normalmente:
   `C:\Program Files (x86)\Steam\steamapps\common\Left 4 Dead 2\left4dead2\`
3. En Steam: clic derecho en Left 4 Dead 2 → Propiedades → Opciones de lanzamiento, y escribe `-condebug`. Sin esto el juego no crea `console.log`.
4. Haz doble clic en `watcher.exe`. Abre el juego y empieza a vigilar. Déjalo abierto mientras juegas.
5. Ya dentro de una partida, escribe `status` en la consola del juego. El programa revisa la lista de jugadores cada vez que ejecutas `status`.

## Archivos (en la misma carpeta que `watcher.exe`)

La primera vez, el programa crea `configWatcher.txt` y `watchlist.txt` con valores por defecto.

### `configWatcher.txt`

```
NOTIFY_COOLDOWN = 60
WATCHLIST_FILE_NAME = "watchlist.txt"
PUBLIC_WATCHLIST_FILE_NAME = "public_watchlist.csv"
```

- `NOTIFY_COOLDOWN`: segundos antes de volver a notificar al mismo jugador.
- Los otros dos son los nombres de los archivos de las listas.

### `watchlist.txt` (lista personal)

Un Steam ID por línea, en formato `STEAM_X:Y:Z` o SteamID64. Lo que va después de `//` aparece entre paréntesis en la notificación.

```
STEAM_0:0:12345 //Cheater
76561197960290419 //Ragebaiter
```

### `public_watchlist.csv` (lista pública)

Cantidad de reportes por tipo:

```
STEAMID,C1,C2,C3,R,T,O
"STEAM_0:1:23456",1,1,3,5,0,0
```

| Columna | Tipo |
|---|---|
| C1, C2, C3 | Cheater clase 1, 2, 3 |
| R | Ragebaiter |
| T | Troll |
| O | Other |

Si un jugador está en ambas listas, solo se notifica el de la lista personal. Un mismo Steam ID genera una sola notificación.

## Notificaciones

```
[Reporte Público] Jugador vigilado detectado en L4D2
Jugador (C1 [1] C2 [1] C3 [3] R [5] T [0] O [0])
STEAM_0:1:23456 — https://steamcommunity.com/profiles/76561197960312641
```

Al hacer clic en una notificación pública se abre el perfil de Steam del jugador. Los reportes de la lista pública los aporta quien mantiene el CSV y no están verificados.

## Ejecutar o compilar desde el código

Requiere Python 3 en Windows y el paquete `winotify`:

```
py -m pip install winotify
py l4d2_watcher.py
```

Para generar `watcher.exe`, ejecuta `build.bat` (usa PyInstaller). Si existe un `watcher.ico` en la carpeta, lo usa como icono. El resultado queda en `dist\watcher.exe`.

Opciones: `l4d2_watcher.py "ruta\a\console.log"` usa otro `console.log`, y `--no-game` evita abrir el juego.

## Notas

- Las notificaciones usan Windows. En otros sistemas el aviso sale solo en la consola.
- Algunos antivirus marcan como sospechosos los `.exe` de PyInstaller sin firmar. Es un falso positivo conocido; el código está aquí para revisarlo.
