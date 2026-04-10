from typing import Tuple, Dict, Any
from models import DevEnvAction, DevEnvObservation

class DevEnvEnvironment:
    # Explicitly tell the framework this env is safe for concurrent graders
    SUPPORTS_CONCURRENT_SESSIONS = True

    def __init__(self):
        self.current_task = "easy"
        self.steps = 0
        self.max_steps = 5
        self.internal_state = {}

    def reset(self, task_id: str = "easy", **kwargs) -> DevEnvObservation:
        """
        PER OPENENV SPEC: reset() -> returns initial observation.
        """
        self.current_task = task_id
        self.steps = 0
        
        if task_id == "easy":
            self.internal_state = {"installed": [], "goal": "Service failed to start. Fix the dependency."}
            out = "[FATAL] ModuleNotFoundError: No module named 'requests'"
        elif task_id == "medium":
            self.internal_state = {"installed": ["numpy==1.25.0"], "goal": "Service requires numpy version 1.20.0 strictly."}
            out = "[ERROR] VersionConflict: numpy 1.25.0 is installed, but ==1.20.0 is required."
        else: # hard
            self.internal_state = {"permissions_fixed": False, "goal": "Service is silently crashing."}
            out = "[ERROR] PermissionError: [Errno 13] Permission denied: '/var/run/app.sock'"

        # Return ONLY the observation Pydantic model
        obs = DevEnvObservation(terminal_output=out, goal_prompt=self.internal_state["goal"], feedback="Environment reset.")
        return obs

    def step(self, action: DevEnvAction) -> Tuple[DevEnvObservation, float, bool, Dict[str, Any]]:
        """
        PER OPENENV SPEC: step(action) -> returns observation, reward, done, info
        """
        self.steps += 1
        
        # Safely extract action fields
        cmd = action.command.lower() if action.command else "check_status"
        pkg = action.package_name
        ver = action.version
        
        out = "Command executed with no effect."
        reward = 0.01
        done = False

        if self.current_task == "easy":
            if cmd == "install" and pkg == "requests":
                self.internal_state["installed"].append("requests")
                out = "Successfully installed requests."
                reward = 0.95
                done = True

        elif self.current_task == "medium":
            if cmd == "uninstall" and pkg == "numpy":
                self.internal_state["installed"] = []
                out = "Successfully uninstalled numpy."
            elif cmd == "install" and pkg == "numpy" and ver == "1.20.0":
                if "numpy==1.25.0" in self.internal_state["installed"]:
                    out = "Error: Must uninstall existing numpy version first."
                else:
                    self.internal_state["installed"].append("numpy==1.20.0")
                    out = "Successfully installed numpy==1.20.0."
                    reward = 0.85
                    done = True

        elif self.current_task == "hard":
            if cmd == "fix_permissions":
                self.internal_state["permissions_fixed"] = True
                out = "Permissions updated to 755 on /var/run/app.sock"
                reward = 0.75
                done = True

        if self.steps >= self.max_steps:
            done = True
            out += "\nMax steps reached. Process terminated."

        # Create Observation
        obs = DevEnvObservation(terminal_output=out, goal_prompt=self.internal_state["goal"], feedback="")
        
        # Create Info Dictionary
        info = {"steps": self.steps, "task": self.current_task}
        
        # Return the exact 4-tuple the OpenEnv validator requires
        return obs, reward, done, info

    def state(self) -> Dict[str, Any]:
        """
        PER OPENENV SPEC: state() -> returns current state.
        """
        return {
            "task": self.current_task,
            "steps": self.steps,
            "internal_state": self.internal_state
        }
