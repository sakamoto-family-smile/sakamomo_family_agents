FROM python:3.12-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the necessary files
COPY . .
COPY ../../a2a_sdk /a2a_sdk

# Install dependencies
RUN pip install --no-cache-dir -e /a2a_sdk
RUN pip install --no-cache-dir -e .

# Set environment variables
ENV HOST=0.0.0.0
ENV PORT=8080

# Expose the port
EXPOSE 8080

# Run the application
CMD ["python", "-m", "sample_agent", "--host", "0.0.0.0", "--port", "8080"]