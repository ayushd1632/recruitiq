# 🎯 RecruitIQ — Multi-Agent MBA Application Intelligence

> Built because one thorough job application was taking me 3.5 hours. This does it in 5 minutes.

## The Problem

MBA recruiting means tailoring 40+ applications. For each one, you need to:
- Research the company's current priorities and culture
- Select and rewrite your most relevant resume bullets
- Write a cover letter that references something specific (not generic)
- Predict likely interview questions and map your stories

Doing this manually for 40 companies is mathematically impossible.

## The Solution: 4 Specialized AI Agents

RecruitIQ deploys 4 AI agents in sequence. Each has a specific role and expertise:

| Agent | Role | What it produces |
|-------|------|-----------------|
| 🔍 Company Intelligence | Corporate Research Analyst | 4-point company briefing from live web search |
| 📝 Resume Tailor | Executive Resume Coach | Top 5 bullets rewritten for this specific JD |
| ✉️ Cover Letter Writer | Master Business Writer | 3-paragraph letter referencing real company context |
| 🎤 Interview Prep | Interview Intelligence Specialist | 8 questions with STAR story mapping |

**The multi-agent insight:** Agent 3 (Cover Letter) and Agent 4 (Interview Prep) receive Agent 1's research as input — so the cover letter references something *real* about the company, not generic praise.

## Live Demo

🚀 **[Open RecruitIQ](https://one-stop-recruitiq.streamlit.app/)**

## Architecture
User Input (JD + Resume)
↓
Agent 1: Company Intel (Tavily web search → Groq synthesis)
↓
┌────┴────┐
↓         ↓
Agent 2    Agent 3    ← receives Agent 1's intel
Resume     Cover
Tailor     Letter
↓         ↓
Agent 4       ← also receives Agent 1's intel
Interview Prep
↓
Complete Application Package (4 tabs)

## Tech Stack

- **LLM:** Groq API (llama-3.3-70b-versatile) — chosen for quality + speed
- **Web Search:** Tavily API — real-time company research
- **Framework:** Pure Python with Streamlit — no frontend code needed
- **Pattern:** Sequential multi-agent with context passing

## Context

Built during MBA recruiting at UW Foster. I timed myself: one thorough manual application took 3.5 hours. After building RecruitIQ, the same quality output takes under 5 minutes. I've used it for 20+ applications this recruiting cycle.

The multi-agent architecture mirrors how Goover builds enterprise AI workflows — specialized agents with defined roles, context sharing between agents, and a unified output that no single LLM call could produce at the same quality.

## Run Locally

```bash
git clone https://github.com/YOUR_USERNAME/recruitiq
cd recruitiq
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Add your API keys to .env (see .env.example)
streamlit run app.py
```