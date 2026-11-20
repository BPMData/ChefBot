# Build from the repository root: docker build -f server/Dockerfile .
FROM python:3.14-slim
WORKDIR /app
COPY server/requirements.txt server/requirements.txt
RUN python -m pip install --no-cache-dir -r server/requirements.txt
COPY src/chefbot src/chefbot
COPY src/assets/fonts/static src/assets/fonts/static
COPY server server
RUN python -m server.bake_fonts /opt/chefbot/pdf-fonts
CMD ["sh", "-c", "exec uvicorn server.app:app --host 0.0.0.0 --port ${PORT:-8080}"]
