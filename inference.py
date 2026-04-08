import os
import asyncio
import json
from typing import List, Optional
from openai import OpenAI
from models import DevEnvAction
from env import DevEnvSimulator

# The precise variables Meta is tracking
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
API_KEY = os.getenv("API_KEY", "sk-dummy") # They explicitly look for API_KEY
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
BENCHMARK = "devenv-resolver"

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

def get_llm_action(client: OpenAI, obs_text: str, goal: str, history: List[str]) -> DevEnvAction:
    """Actually calls the LLM via Meta's proxy to get the next action."""
    system_prompt = """You are an AI system administrator agent resolving dependency conflicts.
    Available commands: install, uninstall, fix_permissions, check_status.
    You must return your action strictly as a JSON object with keys: 'command', 'package_name' (optional), 'version' (optional).
    Example 1: {"command": "fix_permissions"}
    Example 2: {"command": "install", "package_name": "requests", "version": "2.31"}"""
    
    user_prompt = f"Goal: {goal}\nObservation: {obs_text}\nHistory: {history}\nNext action JSON:"
    
    try:
        # This is the exact API call Meta's proxy is waiting for!
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=100
        )
        content = response.choices[0].message.content.strip()
        
        # Clean the JSON if the LLM adds markdown blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        data = json.loads(content)
        return DevEnvAction(
            command=data.get("command", "check_status"),
            package_name=data.get("package_name"),
            version=data.get("version")
        )
    except Exception as e:
        # Safe fallback if the LLM outputs bad formatting so the script doesn't crash
        return DevEnvAction(command="check_status")

async def main() -> None:
    # Initializing exactly as they requested in the screenshot
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    env = DevEnvSimulator()
    tasks = ["task-easy", "task-medium", "task-hard"]
    
    for task_name in tasks:
        log_start(task=task_name, env=BENCHMARK, model=MODEL_NAME)
        obs = env.reset(task_id=task_name)
        done = False
        rewards = []
        step = 0
        history = []
        
        while not done and step < env.max_steps:
            step += 1
            
            # Use the LLM to decide the action instead of a hardcoded list
            action = get_llm_action(client, obs.terminal_output, obs.goal_prompt, history)
            action_str = f"{action.command}('{action.package_name or ''}', '{action.version or ''}')"
            
            try:
                obs = env.step(action)
                reward = obs.reward or 0.0
                done = obs.done
                error = None
                
                if "ConnectionTimeout" in obs.terminal_output:
                    error = "Transient Network Error"
                
                rewards.append(reward)
                log_step(step=step, action=action_str, reward=reward, done=done, error=error)
                history.append(f"Action: {action_str} -> Reward: {reward}")
            except Exception as e:
                log_step(step=step, action=action_str, reward=0.0, done=True, error=str(e))
                break
                
        success = any(r == 1.0 for r in rewards)
        score = 1.0 if success else 0.0
        log_end(success=success, steps=step, score=score, rewards=rewards)

if __name__ == "__main__":
    asyncio.run(main())
