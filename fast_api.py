import os
import sys
import json
import asyncio
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from tavily import TavilyClient
from groq import Groq
from langgraph.graph import StateGraph, END, START
from typing import TypedDict
from dotenv import load_dotenv
import uuid

load_dotenv()

# =========================================================
# APP SETUP
# =========================================================

app = FastAPI(
    title="AI Startup Validator API",
    description="Multi-agent startup analysis pipeline powered by LangGraph + Groq + Tavily",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# API CLIENTS
# =========================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not set")

if not TAVILY_API_KEY:
    raise RuntimeError("TAVILY_API_KEY not set")

groq_client = Groq(api_key=GROQ_API_KEY)
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

# =========================================================
# JOB STORE
# =========================================================

jobs: Dict[str, Dict[str, Any]] = {}

# =========================================================
# PYDANTIC SCHEMAS
# =========================================================

class StartupRequest(BaseModel):
    startup_idea: str


class JobStatus(BaseModel):
    job_id: str
    status: str
    progress: int
    current_step: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# =========================================================
# SHORT TERM MEMORY
# =========================================================

class ShortTermMemory:

    def __init__(self):
        self._store = {}

    def save(self, key, value):
        self._store[key] = value

    def load(self, key):
        return self._store.get(key)

    def load_all(self):
        return dict(self._store)

    def clear(self):
        self._store.clear()

    def summary(self):

        if not self._store:
            return "No prior context available."

        lines = []

        for k, v in self._store.items():
            snippet = str(v)[:300]
            lines.append(f"[{k.upper()}]: {snippet}...")

        return "\n\n".join(lines)


# =========================================================
# STATE
# =========================================================

class AgentState(TypedDict):
    startup_idea: str
    market_research: Dict[str, Any]
    competitors: Dict[str, Any]
    revenue_model: Dict[str, Any]
    mvp_plan: Dict[str, Any]
    landing_page: str

    _memory: Any
    _job_id: str


# =========================================================
# LLM HELPER
# =========================================================

def call_llm(prompt: str):

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are an expert AI startup analyst."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7
    )

    return response.choices[0].message.content


# =========================================================
# JOB UPDATE
# =========================================================

def _update_job(job_id: str, step: str, progress: int):

    if job_id in jobs:
        jobs[job_id]["current_step"] = step
        jobs[job_id]["progress"] = progress


# =========================================================
# AGENTS
# =========================================================

def market_research_agent(state: AgentState):

    job_id = state["_job_id"]
    memory = state["_memory"]

    idea = state["startup_idea"]

    _update_job(job_id, "Market Research", 15)

    tavily_result = tavily_client.search(
        query=f"Startup market demand for {idea}",
        search_depth="advanced",
        max_results=5
    )

    prompt = f"""
    You are a startup market analyst.

    Startup Idea:
    {idea}

    Search Data:
    {json.dumps(tavily_result)}

    Prior Context:
    {memory.summary()}

    Provide response in natural ChatGPT format.

    Use:

    ## Market Opportunity

    ## Customer Pain Points

    ## Trend Analysis

    ## Startup Potential

    Use headings, bullet points, and strategic insights.

    Do NOT return JSON.
    """

    result = call_llm(prompt)

    memory.save("market_research", result)

    return {
        "market_research": result
    }


def competitor_agent(state: AgentState):

    job_id = state["_job_id"]
    memory = state["_memory"]

    idea = state["startup_idea"]

    _update_job(job_id, "Competitor Analysis", 30)

    tavily_result = tavily_client.search(
        query=f"Startup competitors for {idea}",
        search_depth="advanced",
        max_results=5
    )

    prompt = f"""
    You are a startup competitor analyst.

    Startup Idea:
    {idea}

    Competitor Data:
    {json.dumps(tavily_result)}

    Prior Context:
    {memory.summary()}

    Provide response in natural ChatGPT format.

    Use:

    ## Top Competitors

    ## Competitor Strengths

    ## Competitor Weaknesses

    ## Market Gaps

    ## Opportunity Score

    Score out of 10.

    Do NOT return JSON.
    """

    result = call_llm(prompt)

    memory.save("competitors", result)

    return {
        "competitors": result
    }


def merge_parallel_results(state: AgentState):

    job_id = state["_job_id"]
    memory = state["_memory"]

    _update_job(job_id, "Merging Results", 45)

    memory.save(
        "merged_snapshot",
        {
            "market_research": state.get("market_research"),
            "competitors": state.get("competitors")
        }
    )

    return state


def revenue_model_agent(state: AgentState):

    job_id = state["_job_id"]
    memory = state["_memory"]

    idea = state["startup_idea"]

    _update_job(job_id, "Revenue Model", 60)

    prompt = f"""
    You are a SaaS revenue strategist.

    Startup Idea:
    {idea}

    Prior Context:
    {memory.summary()}

    Provide response in natural format.

    Use:

    ## Revenue Model

    ## Pricing Strategy

    ## Customer Acquisition

    ## Freemium Strategy

    ## Growth Strategy

    Do NOT return JSON.
    """

    result = call_llm(prompt)

    memory.save("revenue_model", result)

    return {
        "revenue_model": result
    }


def mvp_planner_agent(state: AgentState):

    job_id = state["_job_id"]
    memory = state["_memory"]

    idea = state["startup_idea"]

    _update_job(job_id, "MVP Planning", 75)

    prompt = f"""
    You are an expert startup MVP planner.

    Startup Idea:
    {idea}

    Prior Context:
    {memory.summary()}

    Provide response in natural format.

    Use:

    ## Core Features

    ## Tech Stack

    ## Development Roadmap

    Week 1:
    ...

    Week 2:
    ...

    Week 3:
    ...

    ## Launch Strategy

    Do NOT return JSON.
    """

    result = call_llm(prompt)

    memory.save("mvp_plan", result)

    return {
        "mvp_plan": result
    }


def landing_page_agent(state: AgentState):

    job_id = state["_job_id"]
    memory = state["_memory"]

    idea = state["startup_idea"]

    _update_job(job_id, "Landing Page", 88)

    prompt = f"""
    You are a world-class SaaS copywriter.

    Startup Idea:
    {idea}

    Prior Context:
    {memory.summary()}

    Create a modern startup landing page in HTML.

    Include:

    1. Hero Section
    2. Problem Section
    3. Features Section
    4. Pricing Section
    5. CTA Section
    6. Footer

    IMPORTANT RULES:

    Return ONLY valid raw HTML.

    Do NOT include:
    - markdown code blocks
    - ```html
    - explanations
    - comments
    - extra text before or after HTML

    Start directly with:
    <!DOCTYPE html>

    End with:
    </html>

    The HTML must be complete, browser-renderable, and self-contained.
    """
    result = call_llm(prompt)
    result = result.replace("```html", "")
    result = result.replace("```", "")
    result = result.strip()

    memory.save("landing_page", result)

    return {
        "landing_page": result
    }


def final_report_agent(state: AgentState):

    job_id = state["_job_id"]

    _update_job(job_id, "Finalizing", 98)

    return state


# =========================================================
# WORKFLOW
# =========================================================

def build_workflow():

    workflow = StateGraph(AgentState)

    workflow.add_node("market_research_agent", market_research_agent)
    workflow.add_node("competitor_agent", competitor_agent)
    workflow.add_node("merge_parallel_results", merge_parallel_results)
    workflow.add_node("revenue_model_agent", revenue_model_agent)
    workflow.add_node("mvp_planner_agent", mvp_planner_agent)
    workflow.add_node("landing_page_agent", landing_page_agent)
    workflow.add_node("final_report_agent", final_report_agent)

    workflow.add_edge(START, "market_research_agent")
    workflow.add_edge(START, "competitor_agent")

    workflow.add_edge(
        "market_research_agent",
        "merge_parallel_results"
    )

    workflow.add_edge(
        "competitor_agent",
        "merge_parallel_results"
    )

    workflow.add_edge(
        "merge_parallel_results",
        "revenue_model_agent"
    )

    workflow.add_edge(
        "revenue_model_agent",
        "mvp_planner_agent"
    )

    workflow.add_edge(
        "mvp_planner_agent",
        "landing_page_agent"
    )

    workflow.add_edge(
        "landing_page_agent",
        "final_report_agent"
    )

    workflow.add_edge(
        "final_report_agent",
        END
    )

    return workflow.compile()


# =========================================================
# PIPELINE
# =========================================================

def run_pipeline(job_id: str, startup_idea: str):

    memory = ShortTermMemory()

    try:

        jobs[job_id]["status"] = "running"
        jobs[job_id]["progress"] = 5

        graph = build_workflow()

        final_state = graph.invoke({
            "startup_idea": startup_idea,
            "market_research": {},
            "competitors": {},
            "revenue_model": {},
            "mvp_plan": {},
            "landing_page": "",
            "_memory": memory,
            "_job_id": job_id
        })

        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["current_step"] = "Done"

        jobs[job_id]["result"] = {
            "startup_idea": final_state.get("startup_idea"),
            "market_research": final_state.get("market_research"),
            "competitors": final_state.get("competitors"),
            "revenue_model": final_state.get("revenue_model"),
            "mvp_plan": final_state.get("mvp_plan"),
            "landing_page": final_state.get("landing_page")
        }

    except Exception as e:

        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)

    finally:

        memory.clear()


# =========================================================
# ROUTES
# =========================================================

@app.get("/")
def root():

    return {
        "message": "AI Startup Validator API Running"
    }


@app.post("/analyze")
def analyze(request: StartupRequest, background_tasks: BackgroundTasks):

    if not request.startup_idea.strip():
        raise HTTPException(
            status_code=400,
            detail="startup_idea empty"
        )

    job_id = str(uuid.uuid4())

    jobs[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "progress": 0,
        "current_step": "Queued",
        "result": None,
        "error": None
    }

    background_tasks.add_task(
        run_pipeline,
        job_id,
        request.startup_idea
    )

    return jobs[job_id]


@app.get("/status/{job_id}")
def get_status(job_id: str):

    if job_id not in jobs:
        raise HTTPException(
            status_code=404,
            detail="job not found"
        )

    return jobs[job_id]


@app.get("/jobs")
def list_jobs():

    return list(jobs.values())


@app.delete("/jobs/{job_id}")
def delete_job(job_id: str):

    if job_id not in jobs:
        raise HTTPException(
            status_code=404,
            detail="job not found"
        )

    del jobs[job_id]

    return {
        "message": "deleted"
    }


if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "fast_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )