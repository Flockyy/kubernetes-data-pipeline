FROM python:3.9-slim

WORKDIR /app

# Install uv for faster dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy requirements and install dependencies with uv
COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

COPY app.py .

CMD ["python", "-u", "app.py"]
