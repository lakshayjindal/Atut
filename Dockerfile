# ==== Base Image ====
FROM python:3.11-slim

# ==== Environment ====
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# ==== Work Directory ====
WORKDIR /app

# ==== System Dependencies ====
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# ==== Install Python Dependencies ====
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# ==== Copy Project ====
COPY . .

# ==== Collect Static Files ====
RUN python manage.py collectstatic --noinput

# ==== Default Port for Daphne ====
ENV PORT=8000

# ==== Start ASGI Server ====
CMD ["bash", "./start.sh"]
