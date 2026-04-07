import uvicorn
from openenv_core.env_server import create_app
from models import DevEnvAction, DevEnvObservation
from env import DevEnvSimulator

# Pass the raw class, NOT an instance (no parentheses!)
app = create_app(DevEnvSimulator, DevEnvAction, DevEnvObservation)

def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()