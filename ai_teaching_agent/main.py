import asyncio
import json
import os
import re
from pathlib import Path
from typing import Any, TypedDict, Optional

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from bindu.penguin.bindufy import bindufy
from dotenv import load_dotenv

load_dotenv()

# --- UTILITY: PROMPT LOADER ---
def load_skill(skill_name: str) -> str:
    """
    Dynamically extracts agent instructions from the centralized skills.md library.
    Uses regex to isolate content under specific Markdown H2 headers.
    """
    path = Path(__file__).parent / "skills" / "skills.md"
    if not path.exists(): 
        return "You are a professional assistant."
    try:
        content = path.read_text(encoding="utf-8")
        # Matches the specific header and captures all text until the next header or EOF
        pattern = rf"##\s+{re.escape(skill_name)}\s*\n(.*?)(?=\n##|\Z)"
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1).strip() if match else "Provide detailed markdown."
    except Exception:
        return "Provide detailed markdown."
      
# --- STATE DEFINITION ---
class CourseState(TypedDict):
    """
    Represents the shared state schema for the LangGraph workflow.
    Facilitates data passing between sequential and parallel nodes.
    """
    topic: str
    professor_content: str
    advisor_roadmap: str
    librarian_resources: str
    ta_workbook: str
    final_output: str

# Singleton instances for persistent server state
graph = None
global_llm = None
_initialized = False
_init_lock = asyncio.Lock()

# --- ASYNC NODES ---
async def professor_node(state: CourseState):
    """
    Sequential Node: Sets the academic foundation.
    This content serves as the primary context for all subsequent parallel agents.
    """
    print("🧠 Professor: Building Master Knowledge Base...")
    sys_prompt = load_skill("🎓 Professor Agent")
    messages = [SystemMessage(content=sys_prompt), HumanMessage(content=f"Topic: {state['topic']}")]
    response = await global_llm.ainvoke(messages)
    return {"professor_content": response.content}

async def parallel_team_node(state: CourseState):
    """
    Parallel Node: Executes secondary agents concurrently to reduce total latency.
    Includes failure resilience via return_exceptions=True to ensure partial success.
    """
    print("⚡ Parallel Team: Generating Roadmap, Resources, and Exercises...")
    kb_content = state.get("professor_content", "")
    
    # Defensive exit if upstream dependency failed
    if not kb_content:
        return {"advisor_roadmap": "Fail", "librarian_resources": "Fail", "ta_workbook": "Fail"}

    adv_sys = load_skill("🗺️ Academic Advisor Agent")
    lib_sys = load_skill("📚 Research Librarian Agent")
    ta_sys = load_skill("✍️ Teaching Assistant Agent")
    ctx = f"Context:\n{kb_content}"

    # Initialize concurrent LLM requests
    tasks = [
        global_llm.ainvoke([SystemMessage(content=adv_sys), HumanMessage(content=ctx)]),
        global_llm.ainvoke([SystemMessage(content=lib_sys), HumanMessage(content=ctx)]),
        global_llm.ainvoke([SystemMessage(content=ta_sys), HumanMessage(content=ctx)])
    ]
    
    # Wait for all tasks; exceptions are caught to prevent graph-wide crashes
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    def extract(res):
        """Safely parses results from the gather pool."""
        if isinstance(res, Exception):
            return f"⚠️ Error: {str(res)}"
        return res.content
      
    return {
        "advisor_roadmap": extract(results[0]),
        "librarian_resources": extract(results[1]),
        "ta_workbook": extract(results[2])
    }

async def compiler_node(state: CourseState):
    """
    Finalization Node: Aggregates individual agent outputs into a unified Markdown curriculum.
    """
    print("✨ Compiler: Polishing Final Curriculum...")
    final_md = f"""# 🎓 AI Teaching Team: {state['topic']}
---
## 🧠 Knowledge Base
{state.get('professor_content', '')}
---
## 🗺️ Learning Roadmap
{state.get('advisor_roadmap', '')}
---
## 📚 Resource Library
{state.get('librarian_resources', '')}
---
## ✍️ Practice Workbook
{state.get('ta_workbook', '')}
"""
    return {"final_output": final_md}

# --- INITIALIZATION ---
async def initialize_agent() -> None:
    """
    Configures the Global LLM client and compiles the LangGraph state machine.
    Designed to run once during server startup or on the first incoming request.
    """
    global graph, global_llm
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
      raise RuntimeError("OPENROUTER_API_KEY not found in environment variables")
  
    global_llm = ChatOpenAI(
        base_url="https://openrouter.ai/api/v1", 
        api_key=api_key, 
        model=os.getenv("MODEL_NAME", "anthropic/claude-3-haiku"),
        max_retries=3,
        timeout=60 
    )
    
    # Define Graph Topology
    workflow = StateGraph(CourseState)
    workflow.add_node("professor", professor_node)
    workflow.add_node("parallel_team", parallel_team_node)
    workflow.add_node("compiler", compiler_node)
    
    workflow.set_entry_point("professor")
    workflow.add_edge("professor", "parallel_team")
    workflow.add_edge("parallel_team", "compiler")
    workflow.add_edge("compiler", END)
    
    graph = workflow.compile()
    print("✅ Optimized Production Graph Initialized.")

# --- HANDLERS ---
async def run_agent(messages: list[dict[str, str]]) -> Any:
    """
    Orchestrates the actual graph execution for a given user message.
    """
    global graph
    if graph is None:
        return "Error: Agent graph not properly initialized."
    
    # Input sanitization and length limiting
    user_topic = messages[-1].get("content", "").strip()[:500] or "General Learning"
    
    try:
        # Executes the state machine and returns the finalized output
        result = await graph.ainvoke({"topic": user_topic})
        return result.get("final_output", "Error: No output generated.")
    except Exception as e:
        return f"Error: {str(e)}"
      
async def handler(messages: list[dict[str, str]]) -> Any:
    """
    Primary entry point for the Bindu framework.
    Uses an Async Lock to ensure thread-safe singleton initialization under high concurrency.
    """
    global _initialized
    async with _init_lock:
        if not _initialized:
            await initialize_agent()
            _initialized = True
    return await run_agent(messages)

def main():
    """
    Server entry point. Binds the handler to the Bindu Penguins protocol.
    """
    config_path = Path(__file__).parent / "agent_config.json"
    with open(config_path) as f:
        config = json.load(f)
    print("🚀 Starting Production AI Teaching Agent...")
    bindufy(config, handler)

if __name__ == "__main__":
    main()