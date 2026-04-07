from models import DevEnvAction, DevEnvObservation
from openenv_core.env_server import Environment
from typing import Tuple, Dict, Any

class DevEnvSimulator(Environment):
    def __init__(self):
        # Initialize all required attributes
        self.current_task_id = "task-easy"
        self.installed_packages = {}
        self.terminal_output = ""
        self.goal_prompt = ""
        self.step_count = 0
        self.max_steps = 10
        self.disk_space_mb = 1000 

    def state(self) -> Dict[str, Any]:
        """
        MANDATORY: Returns the current internal state.
        This fixes the 'abstract method state' error.
        """
        return {
            "task_id": self.current_task_id,
            "installed_packages": self.installed_packages,
            "step_count": self.step_count,
            "disk_space_mb": self.disk_space_mb
        }

    def reset(self, task_id: str = "task-easy") -> DevEnvObservation:
        self.current_task_id = task_id
        self.step_count = 0
        self.installed_packages = {}
        
        if task_id == "task-easy":
            self.goal_prompt = "Install 'requests'==2.31. Environment is empty."
            self.disk_space_mb = 1000
        elif task_id == "task-medium":
            self.goal_prompt = "Install 'pandas'==2.0. Note: Requires 'numpy'==1.26."
            self.installed_packages = {"numpy": "1.24"}
            self.disk_space_mb = 800
        elif task_id == "task-hard":
            self.goal_prompt = "Critical: System low on space. Resolve 'werkzeug' conflict and install 'flask'."
            self.installed_packages = {"werkzeug": "1.0", "temp_logs": "heavy_data"}
            self.disk_space_mb = 100 # Trap: Low space!

        self.terminal_output = f"System initialized. Free Space: {self.disk_space_mb}MB."
        return self._get_obs()

    def _get_obs(self) -> DevEnvObservation:
        return DevEnvObservation(
            terminal_output=self.terminal_output,
            currently_installed=self.installed_packages.copy(),
            goal_prompt=f"{self.goal_prompt} [Available Space: {self.disk_space_mb}MB]"
        )

    def step(self, action: DevEnvAction) -> Tuple[DevEnvObservation, float, bool, Dict[str, Any]]:
        self.step_count += 1
        reward = 0.0
        done = False
        
        # Action Logic: Install costs space, Uninstall saves it
        if action.command == "install":
            if self.disk_space_mb < 50:
                self.terminal_output = "Error: Insufficient Disk Space."
                reward = -0.1
            else:
                pkg = action.package_name
                ver = action.version or "latest"
                self.installed_packages[pkg] = ver
                self.disk_space_mb -= 50
                self.terminal_output = f"Installed {pkg}=={ver}. Space: {self.disk_space_mb}MB."
            
        elif action.command == "uninstall":
            pkg = action.package_name
            if pkg in self.installed_packages:
                del self.installed_packages[pkg]
                self.disk_space_mb += 50
                self.terminal_output = f"Uninstalled {pkg}. Space recovered."
            else:
                self.terminal_output = f"Error: {pkg} not found."

        # Graders
        if self.current_task_id == "task-easy" and self.installed_packages.get("requests") == "2.31":
            reward, done = 1.0, True
        elif self.current_task_id == "task-medium":
            if self.installed_packages.get("pandas") == "2.0" and self.installed_packages.get("numpy") == "1.26":
                reward, done = 1.0, True
            elif self.installed_packages.get("numpy") == "1.26":
                reward = 0.5
        elif self.current_task_id == "task-hard":
            if self.installed_packages.get("flask") and self.installed_packages.get("werkzeug") == "2.0":
                reward, done = 1.0, True
            elif self.installed_packages.get("werkzeug") == "2.0":
                reward = 0.5

        if self.step_count >= self.max_steps: done = True
        return self._get_obs(), reward, done, {}