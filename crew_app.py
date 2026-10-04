import os
import re
from typing import Any, List, Tuple

from crewai import LLM, Agent, Crew, Process, Task
from crewai.tasks.task_output import TaskOutput
from crewai.tools import tool
from pydantic import BaseModel, Field


# ---------- Structured outputs ----------
class JobAnalysis(BaseModel):
    summary: str = Field(description="2 line summary of the job")
    required_skills: List[str]
    deliverables: List[str]
    client_pain_points: List[str]
    red_flags: List[str] = Field(description="Vague scope, low budget etc. Empty if none")
    estimated_hours: int


class PricingPlan(BaseModel):
    pricing_model: str = Field(description="fixed or hourly")
    recommended_price_usd: float
    timeline_days: int
    reasoning: str


# ---------- Tool ----------
@tool("Price Calculator")
def price_calculator(hours: float, hourly_rate: float, buffer_percent: float = 15) -> str:
    """Calculates project price = hours x hourly_rate plus a safety buffer percentage."""
    base = hours * hourly_rate
    total = base * (1 + buffer_percent / 100)
    return f"Base: ${base:.2f}, Buffer: {buffer_percent}%, Total: ${total:.2f}"


# ---------- Guardrail ----------
def proposal_guardrail(output: TaskOutput) -> Tuple[bool, Any]:
    text = output.raw.strip()
    words = len(text.split())
    if words < 120 or words > 350:
        return (False, f"Proposal is {words} words. Rewrite it between 120 and 350 words.")
    if re.search(r"\[[^\]]+\]", text):
        return (False, "Remove all [placeholders]. Use only the real info provided.")
    return (True, text)


# ---------- Crew ----------
def run_proposal_crew(job_post: str, profile: str, hourly_rate: float) -> dict:
    api_key = os.environ.get("GEMINI_API_KEY", "")
    os.environ.setdefault("GOOGLE_API_KEY", api_key)

    llm = LLM(
        model=os.environ.get("MODEL", "gemini/gemini-3.5-flash"),
        api_key=api_key,
        temperature=0.4,
    )

    analyzer = Agent(
        role="Job Post Analyzer",
        goal="Understand exactly what the client wants and spot risks",
        backstory="You are an experienced freelancer who reads job posts carefully and finds hidden needs and red flags.",
        llm=llm,
    )
    pricer = Agent(
        role="Pricing Strategist",
        goal="Suggest a fair, competitive price and realistic timeline",
        backstory="You price freelance projects so the freelancer wins the job and is still paid well.",
        tools=[price_calculator],
        llm=llm,
    )
    writer = Agent(
        role="Proposal Writer",
        goal="Write a short, personal proposal that wins the client's trust",
        backstory="You write proposals that start with the client's problem, not with the freelancer's biography.",
        llm=llm,
    )

    analyze_task = Task(
        description="Analyze this job post:\n\n{job_post}",
        expected_output="Structured analysis of the job.",
        agent=analyzer,
        output_pydantic=JobAnalysis,
    )
    price_task = Task(
        description=(
            "Using the job analysis, suggest a price. The freelancer hourly rate is ${hourly_rate} USD. "
            "Use the Price Calculator tool."
        ),
        expected_output="Pricing plan with price, timeline and reasoning.",
        agent=pricer,
        context=[analyze_task],
        output_pydantic=PricingPlan,
    )
    write_task = Task(
        description=(
            "Write a proposal for this job. Freelancer profile:\n{profile}\n\n"
            "Rules: 150-300 words, start with the client's problem, mention 2 relevant skills, "
            "include the price and timeline from the pricing plan, end with one clear question. "
            "No placeholders like [Name]."
        ),
        expected_output="Final proposal text only.",
        agent=writer,
        context=[analyze_task, price_task],
        guardrail=proposal_guardrail,
    )

      crew = Crew(
        agents=[analyzer, pricer, writer],
        tasks=[analyze_task, price_task, write_task],
        process=Process.sequential,
        max_rpm=4,
    )
    result = crew.kickoff(
        inputs={"job_post": job_post, "profile": profile, "hourly_rate": hourly_rate}
    )
    return {
        "analysis": analyze_task.output.pydantic,
        "pricing": price_task.output.pydantic,
        "proposal": result.raw,
    }
