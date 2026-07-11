<template>
  <MarketingPage
    eyebrow="Resume Keyword Scanner"
    :title="heroTitle"
    subtitle="Paste any job posting and upload your resume. See exactly which keywords you're matching, which you're missing, and where to add them — so your resume speaks the recruiter's language."
    intro-heading="Find the keywords you're missing before you apply"
    :intro-body="introBody"
    features-heading="What the keyword scanner shows you"
    :features="features"
    :steps="steps"
    :faqs="faqs"
    :related="related"
    cta-heading="Scan your resume for keyword gaps"
    cta-subtext="See your keyword match against any job in seconds. 2 free credits, no card required."
  />
</template>

<script setup>
import MarketingPage from '../components/MarketingPage.vue'
import { useSeo } from '../composables/useSeo'

const heroTitle = 'Match Your Resume to the Job Description'
const url = 'https://resume-roaster.com/resume-keyword-scanner'
const title = 'Resume Keyword Scanner — Match Your Resume to Any Job Description'
const description = 'Free resume keyword scanner. Compare your resume to a job description and see which keywords match, which are missing, and where to add them to pass keyword filters.'

const introBody =
  'Recruiters and ATS software search for specific keywords pulled straight from the job description. If those terms aren\'t on your resume, you don\'t surface in searches and you can be filtered out. Resume Roaster compares your resume to the posting word-for-word and shows a color-coded map of what you\'re matching and what you\'re missing.'

const features = [
  { icon: 'mdi-fire', title: 'Keyword Heatmap', description: 'A color-coded map of every job-description keyword — matched terms in green, gaps in red — ranked by how important they are to the role.' },
  { icon: 'mdi-lightbulb-on-outline', title: 'Where to Add Them', description: 'See suggestions for naturally working missing keywords into your experience — no keyword stuffing.' },
  { icon: 'mdi-chart-bar', title: 'Match Score', description: 'A single 0–100 score that tells you at a glance how closely your resume matches the posting.' },
]

const steps = [
  { title: 'Upload your resume', description: 'Add your resume as a PDF or DOCX. It stays private to your account.' },
  { title: 'Paste the job description', description: 'The scanner extracts the keywords that matter and checks each one against your resume.' },
  { title: 'See your keyword map', description: 'Get your match score and a heatmap of matched vs. missing keywords, with tips on where to add them.' },
]

const faqs = [
  { q: 'How does the resume keyword scanner work?', a: 'Paste a job description and upload your resume. Resume Roaster extracts the important keywords from the posting, checks each against your resume, and shows a color-coded heatmap of matches and gaps plus a match score.' },
  { q: 'What keywords should be on my resume?', a: 'The ones the specific job description emphasizes — skills, tools, certifications, and role-specific terms. The scanner surfaces these automatically for each job so you don\'t have to guess.' },
  { q: 'Isn\'t adding keywords just gaming the system?', a: 'No — the goal is to accurately reflect experience you already have using the language the employer uses. Resume Roaster flags genuine gaps; it never encourages stuffing in skills you don\'t have.' },
  { q: 'Is the keyword scanner free?', a: 'You get 2 free credits on signup with no credit card required, enough to scan your resume against a job. Additional credits start at $9 for 3.' },
]

const related = [
  { to: '/ats-resume-checker', label: 'ATS Resume Checker', icon: 'mdi-robot-outline' },
  { to: '/cover-letter-generator', label: 'Cover Letter Generator', icon: 'mdi-email-edit-outline' },
]

useSeo({ url, title, description, faqs })
</script>
