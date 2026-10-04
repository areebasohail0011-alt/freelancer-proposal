# Freelancer Proposal Team
Multi-agent system (CrewAI + Gemini + Streamlit): Job Analyzer -> Pricing Strategist -> Proposal Writer.
Project Description

Freelancers spend a lot of time reading job posts, estimating prices, and writing proposals for each job. This project automates that whole business process with a team of three AI agents built using CrewAI and powered by Google Gemini. The user pastes a job post, enters their profile and hourly rate, and receives a job analysis, a pricing plan, and a ready-to-send proposal.

How it works

Job Post Analyzer Agent reads the job post and extracts the summary, required skills, deliverables, client pain points, red flags, and estimated hours.
Pricing Strategist Agent uses the analysis and a custom Price Calculator tool to suggest a price, timeline, and pricing model.
Proposal Writer Agent writes a personalized proposal using the analysis, the pricing plan, and the freelancer's profile.

Concepts and skills applied (as covered in the course)

Generative AI: Gemini LLM generates the analysis, pricing reasoning, and proposal text, guided by role, goal, and backstory prompts for each agent.
Agentic AI: Agents use tools and make decisions on their own. The Pricing agent calls a custom Python tool to calculate the project cost.
AI Workflows: A sequential process in which each task's output is passed as context to the next task. It uses structured outputs (Pydantic models) and a guardrail that checks the proposal's length and rejects leftover placeholders, forcing the agent to rewrite it.
Multi-Agent Systems: Three specialized agents collaborate, each with a clear role, in one crew.
Business Process Automation: The complete proposal process (analyze, price, write) is automated end to end, with a Streamlit web interface and a download option.
