FROM python:3.12-slim
RUN pip install --no-cache-dir "psycopg[binary]==3.2.*" "redis==5.*"
COPY app.py /app.py
EXPOSE 8080
CMD ["python", "/app.py"]
