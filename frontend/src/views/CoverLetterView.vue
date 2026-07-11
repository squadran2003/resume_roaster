<template>
  <MarketingPage
    eyebrow="AI Cover Letter Generator"
    :title="heroTitle"
    subtitle="Upload your resume and paste the job description. Our AI writes a personalized cover letter that connects your real experience to what the employer is actually asking for — no generic templates."
    intro-heading="A cover letter written for the job, not a template"
    :intro-body="introBody"
    features-heading="Why these cover letters land interviews"
    :features="features"
    :steps="steps"
    :faqs="faqs"
    :related="related"
    cta-heading="Generate your cover letter"
    cta-subtext="Turn your resume and a job post into a tailored cover letter. 2 free credits, no card required."
  />
</template>

<script setup>
import MarketingPage from '../components/MarketingPage.vue'
import { useSeo } from '../composables/useSeo'

const heroTitle = 'Write a Tailored Cover Letter in Seconds'
const url = 'https://resume-roaster.com/cover-letter-generator'
const title = 'Free AI Cover Letter Generator — Tailored to Any Job'
const description = 'Generate a personalized cover letter with AI. Upload your resume, paste the job description, and get a tailored cover letter that matches your experience to the role — free.'

const introBody =
  'Most cover letters are generic and recruiters can tell in seconds. Resume Roaster reads your actual resume and the specific job description, then writes a cover letter that draws on your real experience and mirrors the language of the posting — so it reads like you wrote it for that one role, because it was.'

const features = [
  { icon: 'mdi-email-edit-outline', title: 'Personalized to the Role', description: 'Every letter is built from your resume and the exact job description — no fill-in-the-blank templates.' },
  { icon: 'mdi-target', title: 'Matches Their Language', description: 'The AI mirrors the keywords and priorities in the posting, so your fit is obvious to both recruiters and ATS.' },
  { icon: 'mdi-clock-fast', title: 'Ready in Seconds', description: 'Skip the blank-page struggle. Get a strong first draft instantly and tweak it to sound exactly like you.' },
]

const steps = [
  { title: 'Upload your resume', description: 'Add your resume as a PDF or DOCX so the AI knows your real experience.' },
  { title: 'Paste the job description', description: 'The AI reads what the employer wants and which of your strengths to highlight.' },
  { title: 'Get your cover letter', description: 'Receive a tailored, ready-to-send cover letter you can copy, edit, and submit.' },
]

const faqs = [
  { q: 'Is the AI cover letter generator free?', a: 'You get 2 free credits on signup with no credit card required, which covers generating a tailored cover letter. Additional credits start at $9 for 3.' },
  { q: 'How is this different from a cover letter template?', a: 'Templates give you generic blanks to fill in. Resume Roaster reads your specific resume and the exact job description, then writes original content that connects your experience to that role.' },
  { q: 'Will the cover letter sound like me?', a: 'The AI produces a strong, professional first draft grounded in your real experience. It\'s meant to be edited — most people tweak a few lines so it matches their voice before sending.' },
  { q: 'What do I need to generate a cover letter?', a: 'Just your resume (PDF or DOCX) and the job description you\'re applying to. The more complete the job posting, the more tailored the letter.' },
]

const related = [
  { to: '/ats-resume-checker', label: 'ATS Resume Checker', icon: 'mdi-robot-outline' },
  { to: '/resume-keyword-scanner', label: 'Resume Keyword Scanner', icon: 'mdi-magnify' },
]

useSeo({ url, title, description, faqs })
</script>
