# Multi-stage build for optimal image size
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt


# Final stage
FROM python:3.11-slim

# Install curl for health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r mcp && useradd -r -g mcp mcp

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/mcp/.local

# Copy application code
COPY src/ ./src/
COPY pyproject.toml ./

# Set ownership
RUN chown -R mcp:mcp /app

# Switch to non-root user
USER mcp

# Add user's local bin to PATH
ENV PATH=/home/mcp/.local/bin:$PATH

# Set Python to run in unbuffered mode
ENV PYTHONUNBUFFERED=1

# Expose MCP server port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Run the MCP server
CMD ["python", "-m", "src.server"]
