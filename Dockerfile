# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Rust and Cargo
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy the requirements file
COPY app/app_requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r app_requirements.txt

# Copy the application code
COPY ./app /app

# Set PYTHONPATH
ENV PYTHONPATH=/app:$PYTHONPATH

# Expose ports
EXPOSE 8000 8501

# Command to run the applications
CMD ["sh", "-c", "uvicorn api_ollama:app --host 0.0.0.0 --port 8000 & streamlit run chat.py --server.port 8501 --server.address 0.0.0.0"]