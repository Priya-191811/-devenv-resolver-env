from typing import Optional
from pydantic import Field
from openenv.core.env_server.mcp_types import CallToolAction, CallToolObservation

class DevEnvAction(CallToolAction):
    """Wraps the AI's shell action."""
    command: str = Field(..., description="Action to perform: install, uninstall, fix_permissions, check_status")
    package_name: Optional[str] = Field(None, description="Target package name (if applicable)")
    version: Optional[str] = Field(None, description="Target package version (if applicable)")

class DevEnvObservation(CallToolObservation):
    """Wraps the terminal output returned to the AI."""
    terminal_output: str = Field(..., description="Standard output or error logs from the terminal")
    goal_prompt: str = Field(..., description="The objective the agent needs to achieve")
    feedback: str = Field("", description="System feedback on the previous action")
