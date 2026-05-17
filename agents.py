import os
import sys
import json
from typing import TypedDict, Dict, Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from tavily import TavilyClient
from groq import Groq

from langgraph.graph import StateGraph, END, START
from dotenv import load_dotenv

load_dotenv()


# =========================================================
# API KEYS
# =========================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

groq_client = Groq(api_key=GROQ_API_KEY)
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)


# =========================================================
# SHORT-TERM MEMORY
# =========================================================

class ShortTermMemory:
    """
    In-session short-term memory store.
    Persists context across all agents within a single run.
    Cleared after each full pipeline execution.
    """

    def __init__(self):
        self._store: Dict[str, Any] = {}

    def save(self, key: str, value: Any):
        self._store[key] = value
        print(f"[Memory] Saved -> {key}")

    def load(self, key: str) -> Any:
        return self._store.get(key, None)

    def load_all(self) -> Dict[str, Any]:
        return dict(self._store)

    def clear(self):
        self._store.clear()
        print("[Memory] Cleared for new session.")

    def summary(self) -> str:
        if not self._store:
            return "No prior context available."

        lines = []

        for k, v in self._store.items():
            snippet = str(v)[:300]
            lines.append(f"[{k.upper()}]: {snippet}...")

        return "\n\n".join(lines)


memory = ShortTermMemory()


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
# MARKET RESEARCH AGENT
# =========================================================

def market_research_agent(state: AgentState):

    idea = state["startup_idea"]

    tavily_result = tavily_client.search(
        query=f"""
        Startup market demand for:
        {idea}

        Include:
        - Google Trends
        - Reddit discussions
        - market size
        - customer pain points
        - search demand
        """,
        search_depth="advanced",
        max_results=5
    )

    prior_context = memory.summary()

    prompt = f"""
    You are a startup market analyst.

    Analyze:
    - market demand
    - user pain points
    - trending interest
    - startup potential

    Startup Idea:
    {idea}

    Search Data:
    {json.dumps(tavily_result)}

    Prior Session Context:
    {prior_context}

    Provide the response in a natural professional report format.

    Use this structure:

    ## Market Opportunity

    ## Customer Pain Points

    ## Trend Analysis

    ## Startup Potential

    Use headings, bullet points, and strategic insights.

    Do NOT return JSON.
    """

    result = call_llm(prompt)

    memory.save("market_research", result)

    print("\n========== MARKET RESEARCH ==========\n")
    print(result)

    return {
        "market_research": result
    }


# =========================================================
# COMPETITOR AGENT
# =========================================================

def competitor_agent(state: AgentState):

    idea = state["startup_idea"]

    tavily_result = tavily_client.search(
        query=f"""
        Top competitors for startup idea:
        {idea}

        Include:
        - Product Hunt
        - Crunchbase
        - startup competitors
        - SaaS companies
        """,
        search_depth="advanced",
        max_results=5
    )

    prior_context = memory.summary()

    prompt = f"""
    You are a startup competitor analyst.

    Responsibilities:
    - Find competitors
    - Compare features
    - Identify gaps
    - Detect oversaturation

    Startup Idea:
    {idea}

    Competitor Data:
    {json.dumps(tavily_result)}

    Prior Session Context:
    {prior_context}

    Provide the response in a natural competitor analysis format.

    Use this structure:

    ## Top Competitors

    ## Competitor Strengths

    ## Competitor Weaknesses

    ## Market Gaps

    ## Opportunity Score

    Give score out of 10.

    Do NOT return JSON.
    """

    result = call_llm(prompt)

    memory.save("competitors", result)

    print("\n========== COMPETITOR ANALYSIS ==========\n")
    print(result)

    return {
        "competitors": result
    }


# =========================================================
# MERGE NODE
# =========================================================

def merge_parallel_results(state: AgentState):

    print("\n========== MERGE: Parallel Results Combined ==========\n")

    print(
        f"Market Research: {'OK' if state.get('market_research') else 'MISSING'}"
    )

    print(
        f"Competitors: {'OK' if state.get('competitors') else 'MISSING'}"
    )

    memory.save(
        "merged_snapshot",
        {
            "market_research": state.get("market_research"),
            "competitors": state.get("competitors")
        }
    )

    return state


# =========================================================
# REVENUE MODEL AGENT
# =========================================================

def revenue_model_agent(state: AgentState):

    idea = state["startup_idea"]

    prior_context = memory.summary()

    prompt = f"""
    You are a SaaS revenue strategist.

    Startup Idea:
    {idea}

    Prior Research Context:
    {prior_context}

    Provide the response in this format:

    ## Recommended Revenue Model

    ## Pricing Strategy

    ## Customer Acquisition Channels

    ## Freemium vs Paid Strategy

    ## Growth Recommendations

    Do NOT return JSON.
    """

    result = call_llm(prompt)

    memory.save("revenue_model", result)

    print("\n========== REVENUE MODEL ==========\n")
    print(result)

    return {
        "revenue_model": result
    }


# =========================================================
# MVP PLANNER AGENT
# =========================================================

def mvp_planner_agent(state: AgentState):

    idea = state["startup_idea"]

    prior_context = memory.summary()

    prompt = f"""
    You are an expert startup MVP planner.

    Startup Idea:
    {idea}

    Prior Research Context:
    {prior_context}

    Provide the response in this format:

    ## Core MVP Features

    ## Recommended Tech Stack

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

    print("\n========== MVP PLAN ==========\n")
    print(result)

    return {
        "mvp_plan": result
    }


# =========================================================
# LANDING PAGE AGENT
# =========================================================

def landing_page_agent(state: AgentState):

    idea = state["startup_idea"]

    prior_context = memory.summary()

    prompt = f"""
    You are a world-class SaaS copywriter.

    Startup Idea:
    {idea}

    Prior Research Context:
    {prior_context}

    Create a startup landing page in HTML.

    Include:

    1. Hero Section
    2. Problem Section
    3. Features Section
    4. Pricing Section
    5. CTA Section
    6. Footer

    Return only HTML code.
    """

    result = call_llm(prompt)

    memory.save("landing_page", result)

    print("\n========== LANDING PAGE ==========\n")
    print(result)

    return {
        "landing_page": result
    }


# =========================================================
# FINAL REPORT AGENT
# =========================================================

def final_report_agent(state: AgentState):

    print("\n========== FINAL STARTUP REPORT ==========\n")

    print(f"""
==================================================
STARTUP IDEA
==================================================

{state.get("startup_idea")}


==================================================
MARKET RESEARCH
==================================================

{state.get("market_research")}


==================================================
COMPETITOR ANALYSIS
==================================================

{state.get("competitors")}


==================================================
REVENUE MODEL
==================================================

{state.get("revenue_model")}


==================================================
MVP PLAN
==================================================

{state.get("mvp_plan")}


==================================================
LANDING PAGE
==================================================

{state.get("landing_page")}
""")

    print("\n========== SHORT-TERM MEMORY DUMP ==========\n")
    print(json.dumps(memory.load_all(), indent=4))

    memory.clear()

    return state


# =========================================================
# LANGGRAPH WORKFLOW
# =========================================================

workflow = StateGraph(AgentState)

workflow.add_node("market_research_agent", market_research_agent)
workflow.add_node("competitor_agent", competitor_agent)
workflow.add_node("merge_parallel_results", merge_parallel_results)
workflow.add_node("revenue_model_agent", revenue_model_agent)
workflow.add_node("mvp_planner_agent", mvp_planner_agent)
workflow.add_node("landing_page_agent", landing_page_agent)
workflow.add_node("final_report_agent", final_report_agent)


# PARALLEL START
workflow.add_edge(START, "market_research_agent")
workflow.add_edge(START, "competitor_agent")


# MERGE
workflow.add_edge(
    "market_research_agent",
    "merge_parallel_results"
)

workflow.add_edge(
    "competitor_agent",
    "merge_parallel_results"
)


# SEQUENTIAL FLOW
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


# =========================================================
# COMPILE
# =========================================================

app = workflow.compile()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    startup_idea = input(
        "\nEnter Your Startup Idea: "
    )

    memory.clear()

    app.invoke(
        {
            "startup_idea": startup_idea
        }
    )

    print(
        "\n========== AI STARTUP VALIDATION COMPLETED ==========\n"
    )