# L4D2 Player Watcher

**[English](#english) | [Español](#español)**

---

## English

Windows program that reads Left 4 Dead 2's `console.log` and sends a notification when a player from your watchlist, or from a public report list, shows up in your match.

> The program's own messages and notifications are in Spanish.

### Installation (no Python needed)

1. Download `watcher.exe` from [Releases](../../releases).
2. Copy it into the game's `left4dead2` folder, next to `console.log`. Usually:
   `C:\Program Files (x86)\Steam\steamapps\common\Left 4 Dead 2\left4dead2\`
3. Set the launch options (see below).
4. Double-click `watcher.exe`. It opens the game and starts watching. Keep it open while you play.
5. Inside a match, run `status` in the game console (or automate it, see below). The program checks the player list every time `status` is run.

### Recommended game setup

**Launch options.** In Steam: right-click Left 4 Dead 2 → Properties → Launch Options, and add:

```
-condebug -conclearlog
```

- `-condebug` makes the game write `console.log`. Without it the program has nothing to read.
- `-conclearlog` clears `console.log` every time the game starts, so the file doesn't keep growing.

**Running `status` automatically (optional).** The watcher only sees players when `status` is printed to the console. Add one of these options to `left4dead2\cfg\autoexec.cfg` (create the file if it doesn't exist).

*Option A: automatic loop with an on/off key.* Runs `status` on its own and lets you pause or resume it with one key (`F8` here, change it to any key you like):

```
alias watch_nop ""
alias watch_step "status; wait 300; watch_loop"
alias watch_start "alias watch_loop watch_step; alias watch_toggle watch_stop; watch_loop"
alias watch_stop "alias watch_loop watch_nop; alias watch_toggle watch_start"
alias watch_toggle watch_start
bind "F8" "watch_toggle"
watch_toggle
```

The last line starts the loop when the game launches. Press `F8` to stop it and `F8` again to resume. After stopping it, wait a few seconds before resuming, so the old loop can finish.

If you prefer the simple version with no key (always on):

```
alias watch_players "status; wait 300; watch_players"
watch_players
```

`wait 300` waits 300 frames, so the interval depends on your FPS (about 5 seconds at 60 FPS). Use a larger number if it floods the console. Some servers block the `wait` command; if the loop doesn't run, use option B.

*Option B: manual, one key.* Doesn't fill the console on its own. You press a key whenever you want to check the player list:

```
bind "F9" "status"
```

### Files (in the same folder as `watcher.exe`)

The first time it runs, the program creates `configWatcher.txt` and `watchlist.txt` with default values.

#### `configWatcher.txt`

```
NOTIFY_COOLDOWN = 60
WATCHLIST_FILE_NAME = "watchlist.txt"
PUBLIC_WATCHLIST_FILE_NAME = "public_watchlist.csv"
```

- `NOTIFY_COOLDOWN`: seconds before notifying about the same player again.
- The other two are the file names of the lists.

#### `watchlist.txt` (private list)

One Steam ID per line, as `STEAM_X:Y:Z` or SteamID64 (the 17-digit number). If you don't know the Steam ID but have the player's profile link, you can visit a site like [Steam ID Finder](https://steamid.xyz/) to get it. Whatever comes after `//` is shown in parentheses in the notification.

```
STEAM_0:0:2000000000 //Cheater
STEAM_0:1:2000000001 //Ragebaiter
```

The IDs in these examples are made-up placeholders. Replace them with real ones.

#### `public_watchlist.csv` (public list)

One row per player, with the number of reports for each type:

```
STEAMID,C1,C2,C3,R,T,O
"STEAM_0:0:2000000000",1,1,3,5,0,0
```

| Column | Type | Meaning |
|---|---|---|
| C1 | Cheater class 1 | Dubious: strange movements, but no clear proof |
| C2 | Cheater class 2 | Discreet: soft aimbot, wallhack, auto-bhop |
| C3 | Cheater class 3 | Blatant: rapid fire, speedhack, aggressive aimbot |
| R | Ragequit / Ragebaiter | Leaves the match or provokes other players |
| T | Troll / Griefer | Intentional friendly fire, suicides, idles |
| O | Other | Mic spam, insults, bug exploits |

The number next to each type is how many reports that player has in that type. These numbers are set by whoever maintains the CSV. This tool is meant as a starting point for building a community database.

**About the reports.** Public reports are not fully verified. They can be a useful hint, but they are not proof: check for yourself before accusing anyone.

#### Priority and duplicates

- The private list (`watchlist.txt`) takes priority over the public one. If a player is in both, only the private notification is shown.
- A Steam ID produces a single notification, no matter how many times it appears in a list. Repeated rows in the CSV are added together.

### Notifications

Public list:

```
[Reporte Público] Jugador vigilado detectado en L4D2
Player (C1 [1] C2 [1] C3 [3] R [5] T [0] O [0])
STEAM_0:0:2000000000 — https://steamcommunity.com/profiles/<SteamID64>
```

Clicking a public notification opens the player's Steam profile. Private list notifications show the name and your `//` comment: `Player (Ragebaiter)`.

### Run or build from source

Requires Python 3 on Windows and the `winotify` package:

```
py -m pip install winotify
py l4d2_watcher.py
```

To build `watcher.exe`, run `build.bat` (uses PyInstaller). If a `watcher.ico` file is in the folder, it is used as the icon. The result is in `dist\watcher.exe`.

Options: `l4d2_watcher.py "path\to\console.log"` uses a different `console.log`, and `--no-game` doesn't open the game.

### Notes

- Notifications use Windows. On other systems the alert only appears in the console.
- Some antivirus programs flag unsigned PyInstaller `.exe` files as suspicious. This is a known false positive; the source code is here to review.

You can access my [public_watchlist.csv](examples/my_public_watchlist), which contains some cheaters found during the project's development.

---

## Español

Programa para Windows que lee el `console.log` de Left 4 Dead 2 y envía una notificación cuando aparece en tu partida un jugador de tu lista de vigilancia o de una lista pública de reportes.

### Instalación (sin Python)

1. Descarga `watcher.exe` desde [Releases](../../releases).
2. Cópialo a la carpeta `left4dead2` del juego, junto a `console.log`. Normalmente:
   `C:\Program Files (x86)\Steam\steamapps\common\Left 4 Dead 2\left4dead2\`
3. Configura las opciones de lanzamiento (ver abajo).
4. Haz doble clic en `watcher.exe`. Abre el juego y empieza a vigilar. Déjalo abierto mientras juegas.
5. Dentro de una partida, ejecuta `status` en la consola del juego (o automatízalo, ver abajo). El programa revisa la lista de jugadores cada vez que se ejecuta `status`.

### Configuración recomendada del juego

**Opciones de lanzamiento.** En Steam: clic derecho en Left 4 Dead 2 → Propiedades → Opciones de lanzamiento, y agrega:

```
-condebug -conclearlog
```

- `-condebug` hace que el juego escriba `console.log`. Sin esto el programa no tiene nada que leer.
- `-conclearlog` borra `console.log` cada vez que se inicia el juego, para que el archivo no crezca demasiado.

**Ejecutar `status` automáticamente (opcional).** El watcher solo ve a los jugadores cuando `status` se imprime en la consola. Agrega una de estas opciones a `left4dead2\cfg\autoexec.cfg` (crea el archivo si no existe).

*Opción A: ciclo automático con tecla para activar y desactivar.* Ejecuta `status` por sí solo y puedes pausarlo o reanudarlo con una tecla (aquí `F8`, cámbiala por la que prefieras):

```
alias watch_nop ""
alias watch_step "status; wait 300; watch_loop"
alias watch_start "alias watch_loop watch_step; alias watch_toggle watch_stop; watch_loop"
alias watch_stop "alias watch_loop watch_nop; alias watch_toggle watch_start"
alias watch_toggle watch_start
bind "F8" "watch_toggle"
watch_toggle
```

La última línea inicia el ciclo al abrir el juego. Pulsa `F8` para detenerlo y `F8` otra vez para reanudarlo. Después de detenerlo, espera unos segundos antes de reanudarlo, para que el ciclo anterior termine.

Si prefieres la versión simple sin tecla (siempre activa):

```
alias watch_players "status; wait 300; watch_players"
watch_players
```

`wait 300` espera 300 fotogramas, así que el intervalo depende de tus FPS (unos 5 segundos a 60 FPS). Usa un número mayor si llena demasiado la consola. Algunos servidores bloquean el comando `wait`; si el ciclo no funciona, usa la opción B.

*Opción B: manual, con una tecla.* No llena la consola por sí sola. Pulsas una tecla cuando quieras revisar la lista de jugadores:

```
bind "F9" "status"
```

### Archivos (en la misma carpeta que `watcher.exe`)

La primera vez que se ejecuta, el programa crea `configWatcher.txt` y `watchlist.txt` con valores por defecto.

#### `configWatcher.txt`

```
NOTIFY_COOLDOWN = 60
WATCHLIST_FILE_NAME = "watchlist.txt"
PUBLIC_WATCHLIST_FILE_NAME = "public_watchlist.csv"
```

- `NOTIFY_COOLDOWN`: segundos antes de volver a notificar al mismo jugador.
- Los otros dos son los nombres de los archivos de las listas.

#### `watchlist.txt` (lista privada)

Un Steam ID por línea, como `STEAM_X:Y:Z` o SteamID64 (el número de 17 dígitos). Si no conoces el Steam ID, pero tienes el link de perfil del jugador, puedes acceder a alguna página como lo puede ser [Steam ID Finder](https://steamid.xyz/) y obtenerlo. Lo que va después de `//` aparece entre paréntesis en la notificación.

```
STEAM_0:0:2000000000 //Cheater
STEAM_0:1:2000000001 //Ragebaiter
```

Los IDs de estos ejemplos son inventados, solo para mostrar el formato. Cámbialos por IDs reales.

#### `public_watchlist.csv` (lista pública)

Una fila por jugador, con la cantidad de reportes de cada tipo:

```
STEAMID,C1,C2,C3,R,T,O
"STEAM_0:0:2000000000",1,1,3,5,0,0
```

| Columna | Tipo | Significado |
|---|---|---|
| C1 | Cheater clase 1 | Dudoso: movimientos extraños, pero sin pruebas claras |
| C2 | Cheater clase 2 | Discreto: aimbot suave, wallhack, auto-bhop |
| C3 | Cheater clase 3 | Descarado: rapid fire, speedhack, aimbot agresivo |
| R | Ragequit / Ragebaiter | Abandona la partida o provoca a otros jugadores |
| T | Troll / Griefer | Fuego amigo intencional, se suicida, inactivo |
| O | Otro | Mic-spam, insultos, exploit de bugs |

El número que aparece junto a cada tipo es la cantidad de reportes que tiene ese jugador en ese tipo. Esos números los define quien mantiene el CSV. Esta herramienta busca ser un punto de partida para construir una base de datos de la comunidad.

**Sobre los reportes.** Los reportes públicos no están del todo verificados. Pueden ser una pista útil, pero no son una prueba: comprueba por tu cuenta antes de acusar a alguien.

#### Prioridad y duplicados

- La lista privada (`watchlist.txt`) tiene prioridad sobre la pública. Si un jugador está en ambas, solo se muestra la notificación de la privada.
- Un Steam ID genera una sola notificación, sin importar cuántas veces aparezca en una lista. Las filas repetidas del CSV se suman.

### Notificaciones

Lista pública:

```
[Reporte Público] Jugador vigilado detectado en L4D2
Jugador (C1 [1] C2 [1] C3 [3] R [5] T [0] O [0])
STEAM_0:0:2000000000 — https://steamcommunity.com/profiles/<SteamID64>
```

Al hacer clic en una notificación pública se abre el perfil de Steam del jugador. Las notificaciones de la lista privada muestran el nombre y tu comentario de `//`: `Jugador (Ragebaiter)`.

### Ejecutar o compilar desde el código

Requiere Python 3 en Windows y el paquete `winotify`:

```
py -m pip install winotify
py l4d2_watcher.py
```

Para generar `watcher.exe`, ejecuta `build.bat` (usa PyInstaller). Si hay un archivo `watcher.ico` en la carpeta, se usa como icono. El resultado queda en `dist\watcher.exe`.

Opciones: `l4d2_watcher.py "ruta\a\console.log"` usa otro `console.log`, y `--no-game` evita abrir el juego.

### Notas

- Las notificaciones usan Windows. En otros sistemas el aviso solo sale en la consola.
- Algunos antivirus marcan como sospechosos los `.exe` de PyInstaller sin firmar. Es un falso positivo conocido; el código está aquí para revisarlo.

Puedes acceder a mi [public_watchlist.csv](examples/my_public_watchlist), con algunos cheaters encontrados en la realización del proyecto.
