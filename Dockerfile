# Use a lightweight Python version
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy all your project files into the container
COPY . /app

# Install the project and its dependencies using the pyproject.toml
RUN pip install --no-cache-dir .

# Expose the port that uvicorn will run on
EXPOSE 7860

# The command to start your environment server
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]