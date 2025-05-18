FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    apt-transport-https \
    ca-certificates \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only the dependency files first
COPY a2a_sdk /a2a_sdk/
COPY agents/sample_agent/pyproject.toml /app/sample_agent/
COPY agents/sample_agent/README.md /app/sample_agent/

# Install dependencies
RUN pip install --no-cache-dir -e /a2a_sdk
WORKDIR /app/sample_agent
RUN pip install --no-cache-dir -e .

# Now copy the rest of the application code
COPY agents/sample_agent /app/sample_agent/

# Set environment variables
ENV HOST=0.0.0.0
ENV PORT=8080
ENV PYTHONPATH=/app/sample_agent
ENV PYTHONUNBUFFERED=1

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose the port
EXPOSE ${PORT}

# Run the application
CMD ["sh", "-c", "python -m sample_agent --host ${HOST} --port ${PORT}"]