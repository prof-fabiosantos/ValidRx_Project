# ===========================
#      STAGE 1 – BUILDER
# ===========================
FROM python:3.10-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# ===========================
#      STAGE 2 – RUNTIME
# ===========================
FROM python:3.10-slim

WORKDIR /app

COPY . .

COPY --from=builder /usr/local /usr/local

EXPOSE 8000

CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
