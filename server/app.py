import uvicorn
from openenv_core.env_server import create_app
from models import DevEnvAction, DevEnvObservation
from env import DevEnvSimulator

# The framework handles the API creation
app = create_app(DevEnvSimulator, DevEnvAction, DevEnvObservation)

# Adding a simple root check for Hugging Face health checks
@app.get("/")
def read_root():
    return {"status": "running", "environment": "devenv-resolver"}

def main():
    # Port 7860 is mandatory for Hugging Face
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()