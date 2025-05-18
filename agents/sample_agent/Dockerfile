FROM python:3.12-slim

WORKDIR /app

# Copy only the dependency files first
COPY a2a_sdk /a2a_sdk/
COPY agents/sample_agent/pyproject.toml /app/sample_agent/pyproject.toml
COPY agents/sample_agent/README.md /app/sample_agent/README.md

# Install dependencies
RUN pip install --no-cache-dir -e /a2a_sdk
WORKDIR /app/sample_agent
RUN pip install --no-cache-dir -e .

# Now copy the rest of the application code
COPY agents/sample_agent /app/sample_agent

# Set environment variables
ENV HOST=0.0.0.0
ENV PORT=8080
ENV PYTHONPATH=/app

# Expose the port
EXPOSE 8080

# Run the application
CMD ["python", "-m", "sample_agent", "--host", "0.0.0.0", "--port", "8080"]