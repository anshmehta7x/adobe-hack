FROM python:3.12.11-slim-bullseye

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY extract.py .
COPY parser.py .
COPY main.py .
COPY random_forest_model.pkl .
COPY label_encoder.pkl .

RUN mkdir -p /app/input /app/output
RUN chmod +x main.py

CMD ["python", "main.py"]