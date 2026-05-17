# Use a slim, production-ready Python base image
FROM python:3.11-slim

# Install system dependencies needed for FAISS and compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the Hugging Face SentenceTransformer model weights
# This locks the model weights into the Docker image itself!
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy application files
COPY . .

# Run the pre-computation of the FAISS index during the build!
# This guarantees that 'index.faiss' exists inside the container image.
RUN python -c "import vector_store; vector_store.build_index('catalog.json', 'index.faiss')"

EXPOSE 8000

# Start Uvicorn with optimized production settings (using 2 workers)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
