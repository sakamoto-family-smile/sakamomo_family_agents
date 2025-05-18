FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy a2a-sdk and install it first
COPY a2a_sdk /app/a2a_sdk
RUN cd /app/a2a_sdk && uv pip install --system --no-cache -e .

# Copy only the necessary files for dependency installation
COPY agents/asset_securities_report_agent/pyproject.toml ./

# Install dependencies using uv
RUN uv pip install --system --no-cache .

# Copy the rest of the application
COPY agents/asset_securities_report_agent .

# Set environment variables
ENV HOST=0.0.0.0
ENV PORT=10020
ENV PYTHONPATH=/app:/app/a2a_sdk
ENV PYTHONUNBUFFERED=1

# Expose the port
EXPOSE 10020

# Run the application
ENTRYPOINT ["python", "-u", "__main__.py"]
CMD ["--host", "0.0.0.0", "--port", "10020"]