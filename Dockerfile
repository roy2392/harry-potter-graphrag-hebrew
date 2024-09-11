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

# Use an entrypoint script to handle environment variables
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set PYTHONPATH
ENV PYTHONPATH=/app:$PYTHONPATH

ENTRYPOINT ["/entrypoint.sh"]

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]