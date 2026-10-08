# preview-lab

App mínima (contador de visitas con Postgres y Redis) para validar las previews por PR de Coolify en el AI Dev Team.

- Estable: https://preview-lab.maxiar.dev
- Previews: https://preview-lab-pr-N.maxiar.dev (detrás de Cloudflare Access)

Local: `docker compose up -d --build` y abrir `http://localhost:8080` desde el contenedor `app`.
