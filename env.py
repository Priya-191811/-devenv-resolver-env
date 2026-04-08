import time
import random
from models import DevEnvAction, DevEnvObservation, DevEnvState
from openenv_core.env_server import Environment

class DevEnvSimulator(Environment):
    def __init__(self):
        self.current_task_id = "task-easy"
        self.installed_packages = {}
        self.terminal_output = ""
        self.goal_prompt = ""
        self.step_count = 0
        self.max_steps = 10
        self.permissions_fixed = False
        self.disk_space_mb = 1000

    @property
    def state(self) -> DevEnvState:
        return DevEnvState(
            step_count=self.step_count,
            task_id=self.current_task_id,
            permissions_fixed=self.permissions_fixed,
            disk_space_mb=self.disk_space_mb
        )

    def reset(self, task_id: str = "task-easy", **kwargs) -> DevEnvObservation:
        self.current_task_id = task_id
        self.step_count = 0
        self.installed_packages = {}
        self.permissions_fixed = False
        
        if task_id == "task-easy":
            self.goal_prompt = "Task: Install 'requests'==2.31."
            self.disk_space_mb = 1000
        elif task_id == "task-medium":
            self.goal_prompt = "Task: Install 'pandas'==2.0. (Requires 'numpy'==1.26)."
            self.installed_packages = {"numpy": "1.24"}
            self.disk_space_mb = 800
        elif task_id == "task-hard":
            self.goal_prompt = "Critical: Install 'django'. SECURITY: Avoid version 4.2.0. Use 4.2.1."
            self.disk_space_mb = 200
            
        self.terminal_output = f"[{time.strftime('%H:%M:%S')}] System initialized. Storage: {self.disk_space_mb}MB."
        # Start with a safe 0.01 instead of 0.0
        return self._get_obs(done=False, reward=0.01)

    def _get_obs(self, done: bool = False, reward: float = 0.01) -> DevEnvObservation:
        return DevEnvObservation(
            done=done,
            reward=reward,
            terminal_output=self.terminal_output,
            currently_installed=self.installed_packages.copy(),
            goal_prompt=f"{self.goal_prompt} | PERMISSIONS: {'OK' if self.permissions_fixed else 'LOCKED'}"
        )

    def step(self, action: DevEnvAction, **kwargs) -> DevEnvObservation:
        self.step_count += 1
        reward = 0.01  # Safe floor value instead of 0.0
        done = False
        ts = time.strftime('%H:%M:%S')

        if action.command == "install" and random.random() < 0.1:
            self.terminal_output = f"[{ts}] ConnectionTimeout: Registry unreachable."
            return self._get_obs(done=False, reward=0.01)

        if action.command == "fix_permissions":
            self.permissions_fixed = True
            self.terminal_output = f"[{ts}] Permissions updated."
        elif action.command == "install":
            if not self.permissions_fixed:
                self.terminal_output = f"[{ts}] PermissionError."
                reward = 0.01
            elif self.disk_space_mb < 50:
                self.terminal_output = f"[{ts}] OSError: no space left."
                reward = 0.01
            else:
                pkg, ver = action.package_name, action.version or "latest"
                self.installed_packages[pkg] = ver
                self.disk_space_mb -= 50
                self.terminal_output = f"[{ts}] Successfully installed {pkg}=={ver}."
        elif action.command == "uninstall":
            pkg = action.package_name
            if pkg in self.installed_packages:
                del self.installed_packages[pkg]
                self.disk_space_mb += 50
                self.terminal_output = f"[{ts}] Removed {pkg}."
            else:
                self.terminal_output = f"[{ts}] {pkg} not found."

        # Grader Logic updated to strict (0, 1) bounds
        if self.current_task_id == "task-easy":
            if self.installed_packages.get("requests") == "2.31":
                reward, done = 0.99, True
        elif self.current_task_id == "task-medium":
            if self.installed_packages.get("pandas") == "2.0" and self.installed_packages.get("numpy") == "1.26":
                reward, done = 0.99, True
            elif self.installed_packages.get("numpy") == "1.26":
                reward = 0.50
        elif self.current_task_id == "task-hard":
            if self.installed_packages.get("django") == "4.2.1":
                reward, done = 0.99, True
            elif self.installed_packages.get("django") == "4.2.0":
                reward, done = 0.01, True 

        if self.step_count >= self.max_steps: done = True
        return self._get_obs(done=done, reward=reward)
