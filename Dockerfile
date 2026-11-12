# App server image (design.md §7). Same image locally and on EC2.
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app/src
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src ./src
COPY configs ./configs
COPY data/kb ./data/kb
COPY data/agent ./data/agent
COPY data/tasks ./data/tasks
EXPOSE 8000
CMD ["uvicorn", "llmsec.apps.server:app", "--host", "0.0.0.0", "--port", "8000"]
