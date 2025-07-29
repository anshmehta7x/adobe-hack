# Stage 1: Build the application
# Use Python 3.12 slim image on linux/amd64 platform as required
FROM python:3.12.4-slim-bookworm

# Set the working directory inside the container
WORKDIR /app

# Set environment variables for a CPU-only build of llama-cpp-python
# This prevents the installation of any GPU-specific libraries
ENV CMAKE_ARGS="-DLLAMA_CUBLAS=off -DLLAMA_CUDA_F16=off -DLLAMA_CUDA_MMQ=off"
ENV PIP_NO_CACHE_DIR=off

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    pkg-config \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch for CPU ONLY before installing other requirements.
# This step is crucial to ensure sentence-transformers finds and uses
# the pre-installed CPU version of PyTorch instead of downloading a GPU version.
RUN pip install --no-cache-dir torch==2.3.1 torchvision==0.18.1 --index-url https://download.pytorch.org/whl/cpu

# Copy and install the application's direct Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Model Downloading Stage ---
# Create a directory to store the local models
RUN mkdir -p /app/models

# Download the GGUF LLM model from Hugging Face
RUN wget https://huggingface.co/stduhpf/google-gemma-3-1b-it-qat-q4_0-gguf-small/resolve/main/gemma-3-1b-it-q4_0_s.gguf -O /app/models/gemma-3-1b-it-q4_0_s.gguf

# Download and cache the sentence-transformer model for offline use.
# The model files will be saved into /app/models/all-MiniLM-L6-v2
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2', cache_folder='/app/models')"

# Copy the rest of your application code into the container
COPY *.py ./

# Specify   the command to run when the container starts
# This will execute your main script
CMD ["python", "main.py"]
