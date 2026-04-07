from pydantic import BaseModel, Field
from typing import Literal, Dict, Optional

# This defines exactly what commands the AI is allowed to send to our simulator
class DevEnvAction(BaseModel):
    command: Literal["install", "uninstall", "check_status"] = Field(
        description="The action the AI wants to take."
    )
    package_name: Optional[str] = Field(
        default=None, 
        description="The name of the package to install/uninstall (e.g., 'pandas'). Leave empty for check_status."
    )
    version: Optional[str] = Field(
        default=None, 
        description="The specific version of the package (e.g., '2.0.0')."
    )

# This defines what the AI sees after it takes an action
class DevEnvObservation(BaseModel):
    terminal_output: str = Field(
        description="The simulated console output from the last command."
    )
    currently_installed: Dict[str, str] = Field(
        description="A dictionary of packages currently installed in the environment."
    )
    goal_prompt: str = Field(
        description="The current task the user needs you to achieve."
    )