import os
import sys

# Ensure the root directory is in the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from openenv.core.env_server.http_server import create_app
from models import DevEnvAction, DevEnvObservation
from server.environment import DevEnvEnvironment

# This builds the exact FastAPI structure Meta requires
app = create_app(
    DevEnvEnvironment,
    DevEnvAction,
    DevEnvObservation,
    env_name="devenv_resolver",
    max_concurrent_envs=25,
)

# 🚨 MANDATORY HACKATHON ENDPOINT 🚨
@app.get("/tasks", tags=["Environment Info"])
async def list_tasks():
    return [
        {"id": "easy", "name": "Missing Package", "difficulty": "easy", "grader": "server.graders.grade_easy"},
        {"id": "medium", "name": "Version Conflict", "difficulty": "medium", "grader": "server.graders.grade_medium"},
        {"id": "hard", "name": "Permission Denied", "difficulty": "hard", "grader": "server.graders.grade_hard"}
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
