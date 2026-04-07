import time
import random
from models import DevEnvAction, DevEnvObservation
from openenv_core.env_server import Environment
from typing import Tuple, Dict, Any

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

    def state(self) -> Dict[str, Any]:
        return {
            "task_id": self.current_task_id,
            "installed_packages": self.installed_packages,
            "permissions_fixed": self.permissions_fixed,
            "disk_space_mb": self.disk_space_mb
        }

    def reset(self, task_id: str = "task-easy") -> DevEnvObservation:
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
            # PRO: Security-Aware Task
            self.goal_prompt = "Critical: Install 'django'. SECURITY REQUIREMENT: Avoid version 4.2.0 (CVE-2023-31122). Use 4.2.1."
            self.disk_space_mb = 200
            
        self.terminal_output = f"[{time.strftime('%H:%M:%S')}] System initialized. Storage: {self.disk_space_mb}MB."
        return self._get_obs()

    def _get_obs(self) -> DevEnvObservation:
        return DevEnvObservation(
            terminal_output=self.terminal_output,
            currently_installed=self.installed_packages.copy(),
            goal_prompt=f"{self.goal_prompt} | PERMISSIONS: {'OK' if self.permissions_fixed else 'LOCKED'}"
        )

    def step(self, action: DevEnvAction, **kwargs) -> Tuple[DevEnvObservation, float, bool, Dict[str, Any]]:
        self.step_count += 1
        reward = 0.0
        done = False
        ts = time.strftime('%H:%M:%S')

        # Logic 1: Transient Network Failure (10% chance)
        if action.command == "install" and random.random() < 0.1:
            self.terminal_output = f"[{ts}] ConnectionTimeout: Registry unreachable. Please retry."
            return self._get_obs(), -0.01, False, {}

        # Logic 2: Handle Commands
        if action.command == "fix_permissions":
            self.permissions_fixed = True
            self.terminal_output = f"[{ts}] chmod 755 /usr/local/bin - Permissions updated."
            
        elif action.command == "install":
            if not self.permissions_fixed:
                self.terminal_output = f"[{ts}] PermissionError: EACCES: permission denied, write '/usr/local/lib'."
                reward = -0.1
            elif self.disk_space_mb < 50:
                self.terminal_output = f"[{ts}] OSError: ENOSPC: no space left on device."
                reward = -0.1
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
                self.terminal_output = f"[{ts}] Package {pkg} not found."

        # Logic 3: Graders
        if self.current_task_id == "task-easy":
            if self.installed_packages.get("requests") == "2.31":
                reward, done = 1.0, True
        
        elif self.current_task_id == "task-medium":
            if self.installed_packages.get("pandas") == "2.0" and self.installed_packages.get("numpy") == "1.26":
                reward, done = 1.0, True
            elif self.installed_packages.get("numpy") == "1.26":
                reward = 0.5
        
        elif self.current_task_id == "task-hard":
            # SECURITY GRADER: Must be 4.2.1, 4.2.0 is a failure.
            if self.installed_packages.get("django") == "4.2.1":
                reward, done = 1.0, True
            elif self.installed_packages.get("django") == "4.2.0":
                self.terminal_output += " [SECURITY VULNERABILITY DETECTED]"
                reward, done = 0.0, True # Instant failure for using insecure version

        if self.step_count >= self.max_steps: done = True
        return self._get_obs(), reward, done, {}
