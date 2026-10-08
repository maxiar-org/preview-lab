"""preview-lab: contador de visitas con Postgres y Redis para probar previews de Coolify."""
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

import psycopg
import redis

# En las previews de Coolify los servicios se llaman <svc>-pr-N. Coolify inyecta SERVICE_NAME_<SVC>
# en tiempo de ejecución; la interpolación del compose no los ve, así que se leen acá.
PG_HOST = os.environ.get("SERVICE_NAME_POSTGRES", "postgres")
REDIS_HOST = os.environ.get("SERVICE_NAME_REDIS", "redis")
DB = f"postgresql://lab:lab@{PG_HOST}:5432/lab"
R = redis.Redis(host=REDIS_HOST, port=6379)
BRANCH = os.environ.get("BRANCH", "desconocida")


def init():
    # Postgres puede tardar en aceptar conexiones al arrancar el stack: reintentar hasta ~60 s.
    for intento in range(30):
        try:
            with psycopg.connect(DB, autocommit=True) as c:
                c.execute("CREATE TABLE IF NOT EXISTS visitas (id serial primary key, en timestamptz default now())")
            return
        except psycopg.OperationalError:
            time.sleep(2)
    raise SystemExit("Postgres no respondió en 60 s")


class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200); self.end_headers(); self.wfile.write(b"ok"); return
        with psycopg.connect(DB, autocommit=True) as c:
            c.execute("INSERT INTO visitas DEFAULT VALUES")
            total = c.execute("SELECT count(*) FROM visitas").fetchone()[0]
        R.incr("hits")
        body = f"<h1>preview-lab (PR de prueba)</h1><p>Rama: <b>{BRANCH}</b></p><p>Visitas en esta base: <b>{total}</b></p><p>Redis: {int(R.get('hits'))}</p>"
        self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.end_headers()
        self.wfile.write(body.encode())


if __name__ == "__main__":
    init()
    HTTPServer(("0.0.0.0", 8080), H).serve_forever()
