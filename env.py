from models import DevEnvAction, DevEnvObservation
from typing import Tuple, Dict, Any
from openenv_core.env_server import Environment

class DevEnvSimulator(Environment):
    def __init__(self):
        self.current_task_id = "task-easy"
        self.installed_packages = {}
        self.terminal_output = ""
        self.goal_prompt = ""
        self.step_count = 0
        self.max_steps = 10  # If the AI takes too long, we stop it

    def reset(self, task_id: str = "task-easy") -> DevEnvObservation:
        """This sets up the 'trick question' or messy state for the AI."""
        self.current_task_id = task_id
        self.step_count = 0
        self.installed_packages = {}
        
        # --- TASK SETUPS (The Mess) ---
        if task_id == "task-easy":
            self.goal_prompt = "Install the package 'requests' version '2.31'."
            self.installed_packages = {} # Empty environment
            
        elif task_id == "task-medium":
            self.goal_prompt = "Install 'pandas' version '2.0'. Note: pandas 2.0 strictly requires 'numpy' version '1.26'."
            self.installed_packages = {"numpy": "1.24"} # Messy state: wrong version of numpy!
            
        elif task_id == "task-hard":
            self.goal_prompt = "Resolve the conflict: Install 'flask'. Flask requires 'werkzeug' version '2.0', but you currently have the incompatible version '1.0' installed."
            self.installed_packages = {"werkzeug": "1.0", "old_server": "1.0"}
            
        else:
            self.goal_prompt = "Unknown task."

        self.terminal_output = f"System initialized for {task_id}. Ready for commands."
        return self._get_obs()

    def _get_obs(self) -> DevEnvObservation:
        """Helper function to package the observation."""
        return DevEnvObservation(
            terminal_output=self.terminal_output,
            currently_installed=self.installed_packages.copy(),
            goal_prompt=self.goal_prompt
        )

    def state(self) -> Dict[str, Any]:
        """Returns the internal state of the environment."""
        return {
            "task_id": self.current_task_id,
            "installed_packages": self.installed_packages,
            "step_count": self.step_count
        }

    def step(self, action: DevEnvAction) -> Tuple[DevEnvObservation, float, bool, Dict[str, Any]]:
        """This processes the AI's action and calculates the grade."""
        self.step_count += 1
        reward = 0.0
        done = False
        
        # 1. PROCESS THE AI's ACTION
        if action.command == "check_status":
            self.terminal_output = f"Status checked. {len(self.installed_packages)} packages installed."
            
        elif action.command == "install":
            pkg = action.package_name
            ver = action.version if action.version else "latest"
            self.installed_packages[pkg] = ver
            self.terminal_output = f"Successfully installed {pkg}=={ver}."
            
        elif action.command == "uninstall":
            pkg = action.package_name
            if pkg in self.installed_packages:
                del self.installed_packages[pkg]
                self.terminal_output = f"Successfully uninstalled {pkg}."
            else:
                self.terminal_output = f"Error: {pkg} is not installed."
        
        # 2. THE GRADERS (Check if the AI solved the problem)
        if self.current_task_id == "task-easy":
            if self.installed_packages.get("requests") == "2.31":
                reward = 1.0
                done = True
                self.terminal_output += " Task Complete!"

        elif self.current_task_id == "task-medium":
            has_pandas = self.installed_packages.get("pandas") == "2.0"
            has_correct_numpy = self.installed_packages.get("numpy") == "1.26"
            
            if has_pandas and has_correct_numpy:
                reward = 1.0 # Perfect score!
                done = True
                self.terminal_output += " Task Complete!"
            elif has_correct_numpy:
                reward = 0.5 # Partial progress (they upgraded numpy but haven't installed pandas yet)

        elif self.current_task_id == "task-hard":
            has_flask = self.installed_packages.get("flask") is not None
            has_correct_werkzeug = self.installed_packages.get("werkzeug") == "2.0"
            
            if has_flask and has_correct_werkzeug:
                reward = 1.0
                done = True
                self.terminal_output += " Task Complete!"
            elif has_correct_werkzeug:
                reward = 0.5 # Partial progress
        
        # 3. TIMEOUT CHECK
        if self.step_count >= self.max_steps and not done:
            done = True
            self.terminal_output += " Max steps reached. Task failed."
            
        return self._get_obs(), reward, done, {}

# This line is required so OpenEnv knows where to find your class
__all__ = ["DevEnvSimulator"]