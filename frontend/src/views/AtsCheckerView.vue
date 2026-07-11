<template>
  <MarketingPage
    eyebrow="Free ATS Resume Checker"
    :title="heroTitle"
    subtitle="Paste a job description and upload your resume. Our AI scans it like an Applicant Tracking System — showing exactly which keywords are missing and what's silently getting you rejected."
    intro-heading="Beat the bots before a human ever sees your resume"
    :intro-body="introBody"
    features-heading="What the ATS checker finds"
    :features="features"
    :steps="steps"
    :faqs="faqs"
    :related="related"
    cta-heading="Check your resume against the ATS"
    cta-subtext="See your keyword gaps and ATS issues in seconds. 2 free credits, no card required."
  />
</template>

<script setup>
import MarketingPage from '../components/MarketingPage.vue'
import { useSeo } from '../composables/useSeo'

const heroTitle = 'Is Your Resume ATS-Friendly?'
const url = 'https://resume-roaster.com/ats-resume-checker'
const title = 'Free ATS Resume Checker — Scan Your Resume for Keywords & ATS Issues'
const description = 'Free AI ATS resume checker. Paste a job description and see which keywords are missing, plus formatting and ATS-compatibility issues — before you apply.'

const introBody =
  'Over 90% of large employers use an Applicant Tracking System (ATS) to filter resumes before a recruiter reads them. If your resume is missing the right keywords or uses formatting the parser can\'t read, it gets rejected automatically. Resume Roaster reads your resume the way an ATS does, compares it against the exact job description, and shows you what to fix.'

const features = [
  { icon: 'mdi-fire', title: 'Keyword Heatmap', description: 'See every job-description keyword that is present in your resume and every one that is missing — color-coded and ranked by importance.' },
  { icon: 'mdi-robot-outline', title: 'Formatting Flags', description: 'Non-standard section headers, tables, and other elements that ATS parsers choke on are flagged before they cost you the interview.' },
  { icon: 'mdi-chart-bar', title: 'Match Score', description: 'A 0–100 compatibility score showing how well your resume aligns with the role, so you know if it\'s worth applying as-is.' },
]

const steps = [
  { title: 'Upload your resume', description: 'Drop in your resume as a PDF or DOCX. It stays private — we never share it.' },
  { title: 'Paste the job description', description: 'The AI scans your resume against the exact keywords and requirements in the posting.' },
  { title: 'Get your ATS report', description: 'See your match score, keyword heatmap, and every formatting issue to fix — in seconds.' },
]

const faqs = [
  { q: 'What is an ATS and why does it matter?', a: 'An Applicant Tracking System (ATS) is software employers use to scan and filter resumes before a human reviews them. If your resume lacks the right keywords or uses formatting the ATS can\'t parse, it can be rejected automatically — even if you\'re qualified.' },
  { q: 'How does the ATS resume checker work?', a: 'Upload your resume and paste the job description. Resume Roaster reads your resume the way an ATS parser does, compares it to the job\'s keywords and requirements, and shows a match score, a color-coded keyword heatmap, and any formatting issues.' },
  { q: 'Is the ATS checker free?', a: 'You get 2 free credits on signup with no credit card required, which is enough to run a full ATS analysis. Additional credits start at $9 for 3.' },
  { q: 'Will you store or share my resume?', a: 'Your resume is private and tied to your account. We never share it, and you can delete it at any time.' },
]

const related = [
  { to: '/resume-keyword-scanner', label: 'Resume Keyword Scanner', icon: 'mdi-magnify' },
  { to: '/cover-letter-generator', label: 'Cover Letter Generator', icon: 'mdi-email-edit-outline' },
]

useSeo({ url, title, description, faqs })
</script>
