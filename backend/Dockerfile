# Use the official Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the port (informative only, Cloud Run ignores this and maps PORT dynamically)
EXPOSE 8080

# Run using a high-performance production ASGI runner (Uvicorn).
# We use the shell format (no square brackets) to allow environment variable expansion of $PORT.
# If $PORT is not defined, it defaults to 8080.
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
