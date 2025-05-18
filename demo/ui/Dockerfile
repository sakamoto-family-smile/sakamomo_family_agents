FROM python:3.13-rc-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy a2a-sdk and install it first
COPY a2a_sdk /app/a2a_sdk
RUN cd /app/a2a_sdk && uv pip install --system --no-cache -e .

# Copy necessary files for dependency installation
COPY demo/ui/pyproject.toml demo/ui/README.md ./

# Modify pyproject.toml to use the correct path
RUN sed -i 's|../../a2a_sdk|/app/a2a_sdk|g' pyproject.toml

# Install dependencies using uv
RUN uv pip install --system --no-cache .

# Copy the rest of the application
COPY demo/ui .

# Set environment variables
ENV HOST=0.0.0.0
ENV DEBUG_MODE=false
ENV PYTHONPATH=/app:/app/a2a_sdk
ENV PYTHONUNBUFFERED=1

# The container must listen on the port specified by PORT at runtime
# Default to 12000 for local development
ENV PORT=12000

# Expose the port
EXPOSE ${PORT}

# Run the application
ENTRYPOINT ["python", "-u", "main.py"]