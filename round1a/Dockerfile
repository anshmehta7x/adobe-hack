FROM python:3.12.11-slim-bullseye

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source files
COPY extract.py .
COPY parser.py .
COPY main.py .
COPY random_forest_model.pkl .
COPY label_encoder.pkl .

# Create input and output directories
RUN mkdir -p /app/input /app/output

# Make sure the main script is executable
RUN chmod +x main.py

# Set the default command
CMD ["python", "main.py"]