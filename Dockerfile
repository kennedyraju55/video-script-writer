FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements*.txt setup.py ./
RUN pip install --no-cache-dir -e .

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .
ENV OLLAMA_HOST=http://host.docker.internal:11434
ENV PYTHONUNBUFFERED=1
EXPOSE 8501
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:8501/_stcore/health || exit 1
CMD ["streamlit", "run", "src/video_script/web_ui.py", "--server.port=8501", "--server.address=0.0.0.0"]
