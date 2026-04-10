# Use a lightweight Python base image
FROM python:3.10-slim

# Set up a non-root user for Hugging Face Spaces compliance
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Copy the requirements file and install dependencies
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY --chown=user . .

# Expose the mandatory Hugging Face port
EXPOSE 7860

# Start the FastAPI server
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
