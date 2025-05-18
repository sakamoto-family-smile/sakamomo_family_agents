FROM python:3.12-slim

WORKDIR /app

# Copy the necessary files
COPY agents/sample_agent /app/sample_agent
COPY a2a_sdk /a2a_sdk/

# Install dependencies
RUN pip install --no-cache-dir -e /a2a_sdk
WORKDIR /app/sample_agent
RUN pip install --no-cache-dir -e .

# Set environment variables
ENV HOST=0.0.0.0
ENV PORT=8080
ENV PYTHONPATH=/app

# Expose the port
EXPOSE 8080

# Run the application
CMD ["python", "-m", "sample_agent", "--host", "0.0.0.0", "--port", "8080"]