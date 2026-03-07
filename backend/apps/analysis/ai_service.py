import json
import logging
import re

import anthropic
import openai
from django.conf import settings

logger = logging.getLogger(__name__)

MAX_RESUME_CHARS = 8000
MAX_JD_CHARS = 4000

# Known prompt-injection patterns to strip before sending to the model
_INJECTION_RE = re.compile(
    r"(ignore\s+(previous|all|prior|above)\s+instructions?|"
    r"ignore\s+all|disregard\s+(your|all|the|previous)|"
    r"forget\s+(previous|all|prior|your)|"
    r"you\s+are\s+now|act\s+as\s+(if|a|an)|new\s+persona|"
    r"override\s+(your|all)|system\s+prompt|"
    r"<\|im_start\|>|<\|im_end\|>|<\|endoftext\|>|"
    r"\[INST\]|\[SYS\]|###\s*instruction|##\s*system)",
    re.IGNORECASE,
)


def sanitize_text(text: str, max_length: int) -> str:
    """Truncate, HTML-encode angle brackets, and strip injection patterns."""
    text = text[:max_length]
    text = text.replace("<", "&lt;").replace(">", "&gt;")
    text = _INJECTION_RE.sub("[removed]", text)
    return text


def build_analysis_prompt(resume_text: str, jd_text: str) -> str:
    safe_resume = sanitize_text(resume_text, MAX_RESUME_CHARS)
    safe_jd = sanitize_text(jd_text, MAX_JD_CHARS)
    return f"""You are a professional resume analyst and career coach.
Analyze the resume against the job description provided below.

<resume>
{safe_resume}
</resume>

<job_description>
{safe_jd}
</job_description>

Respond with ONLY a valid JSON object — no markdown fences, no explanation, no trailing text.
Use exactly this schema:
{{
  "match_score": <integer 0-100>,
  "hire_probability": <float 0.0-1.0>,
  "ats_flags": [<string>, ...],
  "rewritten_bullets": [<string>, ...],
  "cover_letter": <string>,
  "keyword_matches": [
    {{"keyword": <string>, "found": <boolean>, "section_hint": <string>}},
    ...
  ],
  "follow_up_emails": [
    {{"type": "application_follow_up", "subject": <string>, "body": <string>}},
    {{"type": "post_interview_thank_you", "subject": <string>, "body": <string>}},
    {{"type": "networking_outreach", "subject": <string>, "body": <string>}}
  ]
}}

Scoring guidelines:
- match_score: how well the resume matches the role requirements (skills, experience, keywords)
- hire_probability: estimated probability of getting an interview call (based on match quality)
- ats_flags: specific ATS issues — missing keywords, non-standard section headers, tables/graphics, etc.
- rewritten_bullets: 3-5 improved bullet points from the resume, tailored to this JD with quantified impact
- cover_letter: 3-paragraph professional cover letter addressed to the hiring team
- keyword_matches: extract 10-20 important keywords/skills from the JD. For each, indicate whether it is found in the resume and suggest which resume section to add it to if missing (section_hint).
- follow_up_emails: generate 3 personalized email templates — (1) application follow-up after 1 week, (2) post-interview thank you, (3) networking cold outreach. Personalize to the company/role from the JD."""


def build_resume_rewrite_prompt(resume_text: str, jd_text: str) -> str:
    safe_resume = sanitize_text(resume_text, MAX_RESUME_CHARS)
    safe_jd = sanitize_text(jd_text, MAX_JD_CHARS)
    return f"""You are a professional resume writer.
Rewrite the resume below to be optimized for the given job description.

Rules:
- Preserve the candidate's contact info, education, certifications, and factual details exactly
- Rewrite the professional summary/objective to target this specific role
- Rewrite ALL experience bullet points with strong action verbs, quantified impact, and JD-relevant keywords
- Keep the same chronological structure and job titles
- Output ONLY the rewritten resume text in clean plain text format (no JSON, no markdown fences)
- Use clear section headers: CONTACT, SUMMARY, EXPERIENCE, EDUCATION, SKILLS, etc.

<resume>
{safe_resume}
</resume>

<job_description>
{safe_jd}
</job_description>"""


def build_interview_prep_prompt(resume_text: str, jd_text: str) -> str:
    safe_resume = sanitize_text(resume_text, MAX_RESUME_CHARS)
    safe_jd = sanitize_text(jd_text, MAX_JD_CHARS)
    return f"""You are an experienced interview coach.
Based on the resume and job description below, generate likely interview questions.

<resume>
{safe_resume}
</resume>

<job_description>
{safe_jd}
</job_description>

Respond with ONLY a valid JSON array — no markdown fences, no explanation.
Generate 8-10 questions. Use this schema for each:
{{
  "question": <string - the interview question>,
  "why_asked": <string - why the interviewer would ask this, based on JD requirements or resume gaps>,
  "answer_framework": <string - STAR format hint with specific suggestions using the candidate's experience>
}}

Include a mix of:
- Technical/skill-based questions from JD requirements
- Behavioral questions targeting resume gaps or weaknesses
- Industry-specific situational questions
- At least one question about career goals/motivation for this role"""


def build_linkedin_prompt(headline: str, about: str, jd_text: str) -> str:
    safe_headline = sanitize_text(headline, 500)
    safe_about = sanitize_text(about, 3000)
    safe_jd = sanitize_text(jd_text, MAX_JD_CHARS)
    return f"""You are a LinkedIn optimization expert.
Analyze and optimize the LinkedIn profile sections below for the target role.

<current_headline>
{safe_headline}
</current_headline>

<current_about>
{safe_about}
</current_about>

<target_job_description>
{safe_jd}
</target_job_description>

Respond with ONLY a valid JSON object — no markdown fences, no explanation.
Use exactly this schema:
{{
  "headline_rewrite": <string - optimized LinkedIn headline, max 220 chars, keyword-rich>,
  "about_rewrite": <string - optimized About section, 3-4 paragraphs>,
  "suggested_skills": [<string>, <string>, <string>],
  "recruiter_keywords": [<string>, ...],
  "score": <integer 0-100 - how well the current profile matches the target role>,
  "tips": [<string>, ...]
}}"""


def _call_claude(prompt: str, max_tokens: int = 4096) -> str:
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    message = client.messages.create(
        model=settings.ANTHROPIC_MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()


def _call_openai(prompt: str, max_tokens: int = 4096, json_mode: bool = True) -> str:
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    kwargs = {
        "model": settings.OPENAI_MODEL,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content.strip()


def _strip_fences(text: str) -> str:
    """Remove markdown code fences if the model wrapped the JSON anyway."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return text.strip()


def _call_ai(prompt: str, max_tokens: int = 4096, json_mode: bool = True) -> str:
    provider = settings.AI_PROVIDER.lower()
    if provider == "openai":
        raw = _call_openai(prompt, max_tokens, json_mode)
    else:
        raw = _call_claude(prompt, max_tokens)
    return raw


def run_analysis(resume_text: str, jd_text: str) -> dict:
    """Call the configured AI provider and return the parsed JSON result dict."""
    prompt = build_analysis_prompt(resume_text, jd_text)
    raw = _call_ai(prompt)
    raw = _strip_fences(raw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        logger.error(
            "AI returned non-JSON response (first 300 chars): %s",
            raw[:300],
        )
        raise ValueError("AI returned a non-JSON response")


def run_resume_rewrite(resume_text: str, jd_text: str) -> str:
    """Return the full rewritten resume as plain text."""
    prompt = build_resume_rewrite_prompt(resume_text, jd_text)
    return _call_ai(prompt, max_tokens=4096, json_mode=False)


def run_interview_prep(resume_text: str, jd_text: str) -> list:
    """Return a list of interview question dicts."""
    prompt = build_interview_prep_prompt(resume_text, jd_text)
    raw = _call_ai(prompt)
    raw = _strip_fences(raw)
    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else data.get("questions", [])
    except json.JSONDecodeError:
        logger.error("AI returned non-JSON for interview prep (first 300 chars): %s", raw[:300])
        raise ValueError("AI returned a non-JSON response")


def run_linkedin_analysis(headline: str, about: str, jd_text: str) -> dict:
    """Return LinkedIn optimization results."""
    prompt = build_linkedin_prompt(headline, about, jd_text)
    raw = _call_ai(prompt)
    raw = _strip_fences(raw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        logger.error("AI returned non-JSON for LinkedIn analysis (first 300 chars): %s", raw[:300])
        raise ValueError("AI returned a non-JSON response")
