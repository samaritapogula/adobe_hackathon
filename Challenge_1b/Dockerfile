
FROM python:3.10-slim


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


WORKDIR /app


COPY Challenge_1b/requirements.txt .


RUN apt-get update && \
    apt-get install -y build-essential poppler-utils libgl1-mesa-glx && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    rm -rf /root/.cache && \
    apt-get clean


COPY Challenge_1b /app


CMD ["python", "src/main.py"]
