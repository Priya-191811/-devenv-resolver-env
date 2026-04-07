from pydantic import BaseModel, Field
from typing import Literal, Dict, Optional

class DevEnvAction(BaseModel):
    command: Literal["install", "uninstall", "check_status", "fix_permissions"] = Field(
        description="The action the AI wants to take."
    )
    package_name: Optional[str] = Field(
        default=None, 
        description="Name of the package (e.g., 'django')."
    )
    version: Optional[str] = Field(
        default=None, 
        description="Version string (e.g., '4.2.1')."
    )

class DevEnvObservation(BaseModel):
    terminal_output: str = Field(description="Console logs with system timestamps.")
    currently_installed: Dict[str, str] = Field(description="Current system state.")
    goal_prompt: str = Field(description="The primary objective and constraints.")