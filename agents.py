import os
from groq import Groq
from tavily import TavilyClient
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()

# Initialize the AI clients (they read keys from .env automatically)
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# ─────────────────────────────────────────────
# AGENT 1: Company Intelligence Agent
# What it does: Searches the web for real info about the company,
# then synthesizes it into a 4-point intelligence briefing.
# ─────────────────────────────────────────────
def run_company_intel_agent(company_name: str, job_description: str) -> str:

    # Search 1: general company news and strategy
    search_1 = tavily_client.search(
        query=f"{company_name} company news strategy priorities 2025",
        search_depth="basic",
        max_results=5
    )

    # Search 2: culture and what it's like to work there
    search_2 = tavily_client.search(
        query=f"{company_name} company culture values hiring what employees say",
        search_depth="basic",
        max_results=3
    )

    # Combine results into readable text
    all_results = search_1["results"] + search_2["results"]
    research_text = "\n\n".join([
        f"Source: {r['title']}\n{r['content'][:400]}"
        for r in all_results
    ])

    # Send to Groq AI to synthesize into useful intelligence
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a senior corporate research analyst with 15 years of experience "
                    "helping job candidates understand companies before applying. "
                    "You extract specific, actionable intelligence. "
                    "Never make generic statements like 'this is a great company.' "
                    "Be concrete — reference actual things from the research."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Based on this research about {company_name}, write a company intelligence briefing.\n\n"
                    f"Job Description context (first 600 characters): {job_description[:600]}\n\n"
                    f"Research found online:\n{research_text}\n\n"
                    "Provide exactly these 4 sections with headers:\n\n"
                    "**1. What's happening right now** — 1-2 specific recent developments (not generic)\n\n"
                    "**2. Their strategic priorities** — what they actually care about based on the research\n\n"
                    "**3. What this role likely needs** — read between the lines of the JD + company context\n\n"
                    "**4. The one specific thing to reference** — the single most impressive thing to mention "
                    "in a cover letter that shows you did your homework"
                )
            }
        ],
        temperature=0.3,
        max_tokens=900
    )

    return response.choices[0].message.content


# ─────────────────────────────────────────────
# AGENT 2: Resume Tailor Agent
# What it does: Reads your resume and the JD, then selects
# and rewrites the 5 most relevant bullets.
# ─────────────────────────────────────────────
def run_resume_tailor_agent(job_description: str, resume_text: str, company_name: str) -> str:

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an elite executive resume coach who has placed hundreds of MBA candidates "
                    "at top consulting, banking, and tech firms. "
                    "You know that generic resumes get ignored immediately. "
                    "Your specialty: ruthlessly selecting the most relevant bullets and rewriting them "
                    "to mirror the job description's language and priorities. "
                    "Every bullet you recommend must connect directly to something specific in the JD. "
                    "NEVER invent numbers or change real metrics — only use what's in the resume."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Select and tailor the 5 most relevant resume bullets for this {company_name} application.\n\n"
                    f"JOB DESCRIPTION:\n{job_description}\n\n"
                    f"CANDIDATE RESUME:\n{resume_text}\n\n"
                    "For each of the 5 bullets, format exactly like this:\n\n"
                    "**Bullet 1:**\n"
                    "→ [The bullet text — keep real numbers, rewrite language to mirror JD if helpful]\n"
                    "Why chosen: [1 sentence on why this bullet matches this specific role]\n"
                    "JD keyword matched: [which exact word or phrase from the JD this addresses]\n\n"
                    "Be ruthless. Only bullets that genuinely fit. Quality over quantity."
                )
            }
        ],
        temperature=0.2,
        max_tokens=1100
    )

    return response.choices[0].message.content


# ─────────────────────────────────────────────
# AGENT 3: Cover Letter Agent
# What it does: Writes a personalized cover letter.
# KEY: It receives Agent 1's research as input — so the letter
# references something specific about the company.
# ─────────────────────────────────────────────
def run_cover_letter_agent(
    job_description: str,
    resume_text: str,
    company_name: str,
    company_intel: str      # ← This is Agent 1's output being passed in
) -> str:

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a master business writer who has crafted cover letters for C-suite executives.\n\n"
                    "Your letters have one rule: they are NEVER generic. "
                    "Every letter opens with something specific about the company that proves the candidate "
                    "paid attention — a recent initiative, a strategic challenge, something real.\n\n"
                    "Your three-paragraph structure (strict):\n"
                    "• Para 1 (Why Them): Open with a specific company insight. Show you know them.\n"
                    "• Para 2 (Why You): Connect your 2-3 most relevant experiences to their exact needs.\n"
                    "• Para 3 (Why Now): Express clear intent and enthusiasm — confident, not desperate.\n\n"
                    "STRICT RULES — breaking any of these makes the letter generic:\n"
                    "- NEVER start with 'I am writing to apply for...'\n"
                    "- NEVER use 'I am passionate about'\n"
                    "- NEVER use 'I would be a great fit'\n"
                    "- NEVER use 'I am excited to'\n"
                    "- Under 340 words total\n"
                    "- Sign off: Ayush Deshwal"
                )
            },
            {
                "role": "user",
                "content": (
                    f"Write a cover letter for this {company_name} application.\n\n"
                    f"COMPANY INTELLIGENCE (use this to make Para 1 specific — don't write generically):\n"
                    f"{company_intel}\n\n"
                    f"JOB DESCRIPTION:\n{job_description}\n\n"
                    f"CANDIDATE RESUME:\n{resume_text}\n\n"
                    "Write the complete letter now. Use [Date] as placeholder for the date."
                )
            }
        ],
        temperature=0.5,
        max_tokens=750
    )

    return response.choices[0].message.content


# ─────────────────────────────────────────────
# AGENT 4: Interview Prep Agent
# What it does: Predicts 8 likely interview questions and maps
# each one to the best story from your resume.
# Also receives Agent 1's company intel for context.
# ─────────────────────────────────────────────
def run_interview_prep_agent(
    job_description: str,
    resume_text: str,
    company_name: str,
    company_intel: str      # ← Also uses Agent 1's output
) -> str:

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an interview intelligence specialist who has coached 500+ MBA students "
                    "through interviews at McKinsey, Goldman Sachs, Google, and top startups. "
                    "You know what companies ACTUALLY ask in practice — not just the generic list. "
                    "You map each question to the candidate's specific resume experiences so they "
                    "walk into the interview knowing exactly which story to tell and how to open it."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Generate 8 likely interview questions for this {company_name} application "
                    f"and map each to the best story from this resume.\n\n"
                    f"COMPANY INTELLIGENCE:\n{company_intel[:500]}\n\n"
                    f"JOB DESCRIPTION:\n{job_description}\n\n"
                    f"RESUME:\n{resume_text}\n\n"
                    "Generate exactly this mix:\n"
                    "• 4 behavioral questions (starting with 'Tell me about a time...')\n"
                    "• 2 role-specific questions ('How would you approach...' or 'Walk me through...')\n"
                    "• 1 'Why this company' question\n"
                    "• 1 'Why you for this role' question\n\n"
                    "Format EACH question exactly like this:\n\n"
                    "**Question 1:** [Question exactly as the interviewer would say it]\n"
                    "**Best story:** [Which specific bullet/experience from the resume to use]\n"
                    "**Opening line:** [The exact first 1-2 sentences of your answer]\n"
                    "**Trap to avoid:** [The most common mistake candidates make on this question]\n"
                )
            }
        ],
        temperature=0.3,
        max_tokens=1400
    )

    return response.choices[0].message.content