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
    r"(ignore previous instructions|ignore all instructions|you are now|act as if|"
    r"disregard your|system prompt|<\|im_start\|>|<\|im_end\|>)",
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
  "cover_letter": <string>
}}

Scoring guidelines:
- match_score: how well the resume matches the role requirements (skills, experience, keywords)
- hire_probability: estimated probability of getting an interview call (based on match quality)
- ats_flags: specific ATS issues — missing keywords, non-standard section headers, tables/graphics, etc.
- rewritten_bullets: 3–5 improved bullet points from the resume, tailored to this JD with quantified impact
- cover_letter: 3-paragraph professional cover letter addressed to the hiring team"""


def _call_claude(prompt: str) -> str:
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    message = client.messages.create(
        model=settings.ANTHROPIC_MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()


def _call_openai(prompt: str) -> str:
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        max_tokens=2048,
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()


def _strip_fences(text: str) -> str:
    """Remove markdown code fences if the model wrapped the JSON anyway."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return text.strip()


def run_analysis(resume_text: str, jd_text: str) -> dict:
    """Call the configured AI provider and return the parsed JSON result dict."""
    prompt = build_analysis_prompt(resume_text, jd_text)
    provider = settings.AI_PROVIDER.lower()

    if provider == "openai":
        raw = _call_openai(prompt)
    else:
        raw = _call_claude(prompt)

    raw = _strip_fences(raw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        logger.error(
            "AI (%s) returned non-JSON response (first 300 chars): %s",
            provider,
            raw[:300],
        )
        raise ValueError("AI returned a non-JSON response")
