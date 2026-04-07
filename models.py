from typing import Literal, Dict, Optional
from pydantic import Field
from openenv_core.env_server import Action, Observation, State

class DevEnvAction(Action):
    command: Literal["install", "uninstall", "check_status", "fix_permissions"] = Field(description="Command")
    package_name: Optional[str] = Field(default=None, description="Package name")
    version: Optional[str] = Field(default=None, description="Version string")

class DevEnvObservation(Observation):
    terminal_output: str = Field(default="", description="Console logs")
    currently_installed: Dict[str, str] = Field(default_factory=dict, description="Current system state")
    goal_prompt: str = Field(default="", description="The objective")

class DevEnvState(State):
    task_id: str = "task-easy"
    permissions_fixed: bool = False
    disk_space_mb: int = 1000
