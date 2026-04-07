import uvicorn
from openenv_core.env_server import create_app
from models import DevEnvAction, DevEnvObservation
from env import DevEnvSimulator

# We link your simulator to Meta's HTTP server wrapper
env = DevEnvSimulator()
app = create_app(env, DevEnvAction, DevEnvObservation)

def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()