FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
COPY app ./app
RUN pip install --no-cache-dir . && useradd --system --uid 10001 appuser && mkdir /data && chown appuser /data
USER appuser
ENV DATABASE_PATH=/data/tasks.db
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
