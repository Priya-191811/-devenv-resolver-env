from pydantic import BaseModel
from models import DevEnvAction, DevEnvObservation

# 🚨 THE FIX: Inheriting from BaseModel allows FastAPI to serialize this into JSON without crashing.
class StepResult(BaseModel):
    observation: DevEnvObservation
    reward: float
    done: bool

class DevEnvEnvironment:
    # Explicitly tell the framework this env is safe for concurrent graders
    SUPPORTS_CONCURRENT_SESSIONS = True

    def __init__(self):
        self.current_task = "easy"
        self.steps = 0
        self.max_steps = 5
        self.state = {}

    def reset(self, task_id: str = "easy", **kwargs) -> StepResult:
        self.current_task = task_id
        self.steps = 0
        
        if task_id == "easy":
            self.state = {"installed": [], "goal": "Service failed to start. Fix the dependency."}
            out = "[FATAL] ModuleNotFoundError: No module named 'requests'"
        elif task_id == "medium":
            self.state = {"installed": ["numpy==1.25.0"], "goal": "Service requires numpy version 1.20.0 strictly."}
            out = "[ERROR] VersionConflict: numpy 1.25.0 is installed, but ==1.20.0 is required."
        else: # hard
            self.state = {"permissions_fixed": False, "goal": "Service is silently crashing."}
            out = "[ERROR] PermissionError: [Errno 13] Permission denied: '/var/run/app.sock'"

        obs = DevEnvObservation(terminal_output=out, goal_prompt=self.state["goal"], feedback="Environment reset.")
        return StepResult(observation=obs, reward=0.0, done=False)

    def step(self, action: DevEnvAction) -> StepResult:
        self.steps += 1
        cmd = action.command.lower()
        pkg = action.package_name
        ver = action.version
        
        out = "Command executed with no effect."
        reward = 0.01
        done = False

        if self.current_task == "easy":
            if cmd == "install" and pkg == "requests":
                self.state["installed"].append("requests")
                out = "Successfully installed requests."
                reward = 0.95
                done = True

        elif self.current_task == "medium":
            if cmd == "uninstall" and pkg == "numpy":
                self.state["installed"] = []
                out = "Successfully uninstalled numpy."
            elif cmd == "install" and pkg == "numpy" and ver == "1.20.0":
                if "numpy==1.25.0" in self.state["installed"]:
                    out = "Error: Must uninstall existing numpy version first."
                else:
                    self.state["installed"].append("numpy==1.20.0")
                    out = "Successfully installed numpy==1.20.0."
                    reward = 0.85
                    done = True

        elif self.current_task == "hard":
            if cmd == "fix_permissions":
                self.state["permissions_fixed"] = True
                out = "Permissions updated to 755 on /var/run/app.sock"
                reward = 0.75
                done = True

        if self.steps >= self.max_steps:
            done = True
            out += "\nMax steps reached. Process terminated."

        obs = DevEnvObservation(terminal_output=out, goal_prompt=self.state["goal"], feedback="")
        return StepResult(observation=obs, reward=reward, done=done)
