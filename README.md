# Quiniela Mundial 2026

App web supersencilla para la quiniela de oficina del Mundial 2026 (fase de grupos, 72 partidos).

## Usuarios

Cualquiera puede registrarse desde `/registro` eligiendo el nombre que quiera y una contraseña (mínimo 4 caracteres). Después inicia sesión normalmente desde `/`.

## Cómo correrlo localmente

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python app.py
```

Abrí http://localhost:5000 en el navegador. La base de datos `quiniela.db` (SQLite) se crea sola la primera vez.

> Si defines la variable de entorno `DATABASE_URL` (con una conexión a Postgres), la app usa esa base en lugar de SQLite. Ver sección "Base de datos persistente" más abajo.

## Cómo funciona

- Cada usuario elige su nombre y carga el resultado que cree que va a salir en cada uno de los 72 partidos.
- Se puede modificar el pronóstico hasta que el admin cargue el resultado real de ese partido.
- **Puntaje**: 3 puntos por resultado exacto, 1 punto por acertar ganador/empate (sin el marcador exacto), 0 si falla.
- "Tabla" muestra el ranking de jugadores.
- "Resultados" muestra, para los partidos ya jugados, el pronóstico y los puntos de cada jugador.

## Panel de Admin

Entrar a `/admin` con la contraseña (por defecto `mundial2026`, cambiable con la variable de entorno `ADMIN_PASSWORD`). Ahí se cargan los resultados reales de cada partido.

## Desplegar gratis durante el Mundial (Render)

1. Sube esta carpeta a un repo de GitHub.
2. Entra a https://render.com, crea una cuenta y un nuevo "Web Service" apuntando al repo.
3. Configuración:
   - **Build command**: `pip install -r requirements.txt`
   - **Start command**: `gunicorn app:app`
4. Variables de entorno opcionales:
   - `SECRET_KEY`: cualquier texto random
   - `ADMIN_PASSWORD`: la contraseña que quieras para el panel admin
5. Render te da una URL pública (`https://tuapp.onrender.com`) que pueden compartir en la oficina.

> Nota: en el plan gratuito, el sitio puede "dormirse" tras un rato de inactividad y tardar unos segundos en despertar al primer ingreso del día. Para una quiniela de oficina no debería ser un problema.

## Base de datos persistente (Neon Postgres)

Render usa un disco temporal: en el plan gratuito, **cada deploy borra `quiniela.db`**. Para que los registros, pronósticos y resultados sobrevivan a los deploys, conectá una base Postgres gratuita de Neon:

1. Ve a https://neon.tech, crea una cuenta gratis y un proyecto nuevo (cualquier nombre, ej. `quiniela-mundial`).
2. En el dashboard del proyecto, copia el **Connection string** (algo como `postgresql://usuario:contraseña@ep-xxxx.neon.tech/neondb?sslmode=require`).
3. En Render, ve a tu servicio → **Environment** → agrega una variable:
   - `DATABASE_URL` = el connection string que copiaste de Neon
4. Haz un **Manual Deploy → Deploy latest commit**. La app va a crear las tablas automáticamente en Neon la primera vez que arranque.
5. Listo: a partir de ahora, los deploys y reinicios ya no van a borrar los datos, porque viven en Neon y no en el disco de Render.
