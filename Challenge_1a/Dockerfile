FROM --platform=linux/amd64 python:3.10-slim as builder

WORKDIR /install

COPY requirements.txt .

RUN pip install --no-cache-dir --prefix="/install" -r requirements.txt

FROM --platform=linux/amd64 python:3.10-slim

WORKDIR /app

COPY --from=builder /install /usr/local

COPY src/ .

CMD ["python", "main.py"]


