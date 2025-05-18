FROM python:3.12-slim

WORKDIR /app

# Update apt sources and install dependencies
RUN echo "deb http://mirrors.163.com/debian/ bookworm main" > /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the necessary files
COPY . /app/
COPY ../a2a_sdk /a2a_sdk/

# Install dependencies
RUN pip install --no-cache-dir -e /a2a_sdk
RUN pip install --no-cache-dir -e .

# Set environment variables
ENV HOST=0.0.0.0
ENV PORT=8080

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose the port
EXPOSE 8080

# Run the application
CMD ["python", "-m", "sample_agent", "--host", "0.0.0.0", "--port", "8080"]