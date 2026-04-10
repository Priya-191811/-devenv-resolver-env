"""
DevEnv Resolver - Baseline Inference Script
Strictly adheres to Meta OpenEnv Hackathon Phase 1 Formatting Rules.
"""

import os
import sys
import time
import json
import httpx
import textwrap
from typing import List, Optional
from openai import OpenAI

# ── 1. Strict Hackathon Environment Variables ─────────────────────────────
HF_TOKEN = os.getenv("HF_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
ENV_URL = os.getenv("ENV_URL", "http://127.0.0.1:7860")
BENCHMARK_NAME = "devenv_resolver"

# ── 2. Mandatory Strict Logging Functions ─────────────────────────────────
def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    # CRITICAL: Strip all newlines so the regex parser doesn't crash
    clean_action = action.replace("\n", " ").replace("\r", " ")
    print(f"[STEP] step={step} action={clean_action} reward={reward:.2f} done={done_val} error={error_val}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}", flush=True)

# ── 3. The LLM Agent Logic ────────────────────────────────────────────────
def get_agent_action(client: OpenAI, terminal_output: str, goal: str) -> dict:
    system_prompt = textwrap.dedent("""
        You are an expert SRE resolving system errors and dependency conflicts.
        Available commands: install, uninstall, fix_permissions, check_status.
        
        Respond ONLY with a valid JSON object matching this exact schema:
        {"command": "string", "package_name": "string or null", "version": "string or null"}
        
        Do not include explanations, markdown, or text outside the JSON.
    """).strip()

    user_prompt = f"Goal: {goal}\nTerminal Output: {terminal_output}\nNext Action JSON:"

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1, # Extremely low temperature for deterministic actions
            max_tokens=150
        )
        content = response.choices[0].message.content.strip()
        
        # Defend against LLM Markdown Hallucinations
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        return json.loads(content)
    except Exception as e:
        # Fallback to prevent crashing the evaluation
        return {"command": "check_status", "package_name": None, "version": None}

# ── 4. Task Execution Loop ────────────────────────────────────────────────
def run_task(client: OpenAI, task_name: str) -> None:
    log_start(task=task_name, env=BENCHMARK_NAME, model=MODEL_NAME)
    
    rewards = []
    step = 0
    done = False
    final_score = 0.01

    # Attempt to reset the environment with safe container wake-up limits
    try:
        reset_resp = httpx.post(f"{ENV_URL}/api/reset", json={"difficulty": task_name}, timeout=15.0)
        reset_resp.raise_for_status()
        session_data = reset_resp.json()
        session_id = session_data["session_id"]
        terminal_output = session_data["observation"].get("terminal_output", "")
        goal = session_data["observation"].get("goal_prompt", "")
    except Exception as e:
        # If the server is dead, safely fail the task without throwing an unhandled exception
        log_end(success=False, steps=0, score=0.0, rewards=[0.0])
        return

    while not done and step < 5:
        step += 1
        
        # 1. Get action from LLM
        action_dict = get_agent_action(client, terminal_output, goal)
        action_str = f"{action_dict['command']}('{action_dict.get('package_name', '')}')"
        
        # 2. Send action to environment
        try:
            step_resp = httpx.post(
                f"{ENV_URL}/api/call_tool", 
                json={
                    "session_id": session_id,
                    "tool_name": action_dict['command'], # Mapping the JSON output to the tool name
                    "arguments": action_dict
                },
                timeout=15.0
            )
            step_resp.raise_for_status()
            data = step_resp.json()
            
            terminal_output = data.get("result", "")
            done = data.get("done", False)
            reward = float(data.get("reward", 0.01))
            error = None
            
        except Exception as e:
            reward = 0.01
            done = True
            error = "Network Error"

        # 3. Log the step perfectly
        rewards.append(reward)
        log_step(step=step, action=action_str, reward=reward, done=done, error=error)
        
        if done:
            final_score = reward

    # 4. Final Evaluation (Success threshold >= 0.50)
    success = final_score >= 0.50
    log_end(success=success, steps=step, score=final_score, rewards=rewards)

# ── 5. Main Execution ─────────────────────────────────────────────────────
def main():
    if not HF_TOKEN:
        print("Error: HF_TOKEN environment variable is required by hackathon rules.", file=sys.stderr)
        sys.exit(1)

    # Initialize OpenAI client with strictly provided variables
    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
    
    # Wait for Hugging Face proxy to wake up if deployed remotely
    for attempt in range(5):
        try:
            httpx.get(f"{ENV_URL}/docs", timeout=5.0)
            break
        except httpx.RequestError:
            time.sleep(3)

    tasks_to_run = ["easy", "medium", "hard"]
    
    for task in tasks_to_run:
        run_task(client, task)

if __name__ == "__main__":
    main()
