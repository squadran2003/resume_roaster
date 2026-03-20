<template>
  <div>
    <!-- Hero -->
    <section class="hero-section">
      <div class="hero-glow" />
      <v-container class="py-16 text-center hero-content">
        <Transition name="hero-fade" appear>
          <div>
            <v-chip color="primary" variant="flat" size="small" class="mb-5 text-uppercase font-weight-bold">
              AI-Powered Resume Analysis
            </v-chip>
            <h1 class="hero-title mb-5">
              Stop Guessing.<br />Start Getting Interviews.
            </h1>
            <p class="hero-subtitle mx-auto mb-8">
              Upload your resume and a job description. Our AI scores the match, rewrites weak bullets,
              maps keyword gaps, generates a cover letter, and even rewrites your entire resume — in seconds.
            </p>
            <div class="d-flex justify-center gap-4 flex-wrap mb-8">
              <v-btn
                to="/register"
                color="primary"
                size="x-large"
                variant="flat"
                class="font-weight-bold px-8 hero-cta"
              >
                Roast My Resume
              </v-btn>
              <v-btn
                to="/login"
                size="x-large"
                variant="outlined"
                color="white"
                class="px-8"
              >
                Sign In
              </v-btn>
            </div>
            <p v-if="authStore.paymentsEnabled" class="text-body-2" style="color: rgba(255, 255, 255, 0.6);">1 free credit on signup — no credit card required.</p>

            <!-- Stats bar -->
            <div class="d-flex justify-center flex-wrap mt-10 hero-stats">
              <div class="text-center px-6">
                <div class="text-h5 font-weight-bold text-white">7</div>
                <div class="text-body-2" style="color: rgba(255,255,255,0.5)">AI tools</div>
              </div>
              <div class="stat-divider" />
              <div class="text-center px-6">
                <div class="text-h5 font-weight-bold text-white">&lt;30s</div>
                <div class="text-body-2" style="color: rgba(255,255,255,0.5)">Analysis time</div>
              </div>
              <div class="stat-divider" />
              <div class="text-center px-6">
                <div class="text-h5 font-weight-bold text-white">1 free</div>
                <div class="text-body-2" style="color: rgba(255,255,255,0.5)">No card needed</div>
              </div>
            </div>
          </div>
        </Transition>
      </v-container>
    </section>

    <!-- Features -->
    <section class="py-16 bg-surface">
      <v-container>
        <div class="text-center mb-12">
          <h2 class="text-h4 font-weight-bold mb-2">Everything you need to land the role</h2>
          <p class="text-medium-emphasis">Seven powerful tools, one upload.</p>
        </div>
        <v-row justify="center">
          <v-col cols="12" sm="6" md="4" v-for="feature in features" :key="feature.title">
            <v-card height="100%" elevation="0" class="pa-6 text-center feature-card">
              <div class="feature-icon-wrap mx-auto mb-4">
                <v-icon color="primary" size="32">{{ feature.icon }}</v-icon>
              </div>
              <div class="text-h6 font-weight-bold mb-2">{{ feature.title }}</div>
              <div class="text-body-2 text-medium-emphasis">{{ feature.description }}</div>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </section>

    <!-- How it works -->
    <section class="py-16">
      <v-container>
        <div class="text-center mb-12">
          <h2 class="text-h4 font-weight-bold mb-2">How it works</h2>
          <p class="text-medium-emphasis">Three steps from upload to offer-ready.</p>
        </div>
        <div class="steps-row">
          <div v-for="(step, i) in steps" :key="step.title" class="step-item">
            <div class="step-number mx-auto mb-4">{{ i + 1 }}</div>
            <div class="text-h6 font-weight-bold mb-2">{{ step.title }}</div>
            <p class="text-body-2 text-medium-emphasis">{{ step.description }}</p>
          </div>
        </div>
      </v-container>
    </section>

    <!-- Sample output -->
    <section class="py-16 bg-surface">
      <v-container>
        <div class="text-center mb-12">
          <v-chip color="primary" variant="tonal" size="small" class="mb-3">Live preview</v-chip>
          <h2 class="text-h4 font-weight-bold mb-2">See the analysis in action</h2>
          <p class="text-medium-emphasis">Real feedback, not generic advice.</p>
        </div>
        <v-row justify="center">
          <v-col cols="12" md="8">
            <v-card elevation="0" class="pa-6 sample-card">
              <!-- Score bar -->
              <div class="d-flex align-center justify-space-between mb-2">
                <span class="text-body-1 font-weight-medium">Job Match Score</span>
                <v-chip color="success" variant="flat" size="small">78 / 100</v-chip>
              </div>
              <v-progress-linear
                model-value="78"
                color="success"
                bg-color="success"
                bg-opacity="0.15"
                height="10"
                rounded
                class="mb-6"
              />

              <!-- Bullet rewrite example -->
              <div class="text-overline text-medium-emphasis mb-2">Bullet Rewrite Example</div>
              <v-card variant="tonal" color="error" class="pa-3 mb-2">
                <div class="d-flex align-center gap-2">
                  <v-icon color="error" size="18">mdi-close-circle</v-icon>
                  <span class="text-body-2 text-medium-emphasis">Before: <em>"Responsible for managing social media accounts."</em></span>
                </div>
              </v-card>
              <v-card variant="tonal" color="success" class="pa-3 mb-6">
                <div class="d-flex align-center gap-2">
                  <v-icon color="success" size="18">mdi-check-circle</v-icon>
                  <span class="text-body-2">After: <em>"Grew Instagram engagement 43% in 3 months by A/B testing content cadence and launching 2 influencer partnerships."</em></span>
                </div>
              </v-card>

              <!-- ATS flags -->
              <div class="text-overline text-medium-emphasis mb-2">ATS Issues Flagged</div>
              <div class="d-flex flex-wrap gap-2">
                <v-chip size="small" color="warning" variant="tonal" prepend-icon="mdi-alert">Missing keyword: "CI/CD"</v-chip>
                <v-chip size="small" color="warning" variant="tonal" prepend-icon="mdi-alert">Non-standard section header</v-chip>
                <v-chip size="small" color="warning" variant="tonal" prepend-icon="mdi-alert">No measurable outcomes in 3 bullets</v-chip>
              </div>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </section>

    <!-- CTA -->
    <section class="cta-section py-20 text-center">
      <v-container>
        <h2 class="text-h4 font-weight-bold mb-4 text-white">Ready to get the interview?</h2>
        <p class="text-body-1 mb-8 mx-auto" style="max-width:480px;opacity:.8;color:white;">
          Upload your resume and get AI-powered feedback that actually helps you land the job.
        </p>
        <v-btn
          to="/register"
          color="white"
          size="x-large"
          variant="flat"
          class="font-weight-bold px-10 cta-btn"
        >
          Roast My Resume
        </v-btn>
      </v-container>
    </section>

    <!-- Footer -->
    <v-footer class="bg-surface py-6">
      <v-container>
        <div class="d-flex flex-wrap justify-space-between align-center gap-4">
          <div class="d-flex align-center" style="gap: 8px;">
            <v-icon icon="mdi-fire" color="primary" size="22" />
            <span class="font-weight-bold">Resume Roaster</span>
          </div>
          <span class="text-medium-emphasis text-body-2">
            &copy; {{ new Date().getFullYear() }} Resume Roaster. All rights reserved.
          </span>
          <div class="d-flex gap-4">
            <router-link to="/login" class="text-decoration-none text-medium-emphasis text-body-2">Login</router-link>
            <router-link to="/register" class="text-decoration-none text-medium-emphasis text-body-2">Register</router-link>
          </div>
        </div>
      </v-container>
    </v-footer>
  </div>
</template>

<script setup>
import { useHead } from '@unhead/vue'
import { useAuthStore } from '@/stores/auth'

useHead({
  title: 'Resume Roaster - AI Resume Analyzer & ATS Checker',
  meta: [
    { name: 'description', content: 'Upload your resume and job description. Get an AI-powered match score, ATS keyword analysis, bullet rewrites, cover letter, and full resume rewrite in seconds.' },
    { property: 'og:title', content: 'Resume Roaster - AI Resume Analyzer & ATS Checker' },
    { property: 'og:description', content: 'Upload your resume and job description. Get an AI-powered match score, ATS keyword analysis, bullet rewrites, cover letter, and full resume rewrite in seconds.' },
    { property: 'og:url', content: 'https://resume-roaster.com/' },
    { property: 'og:type', content: 'website' },
  ],
  link: [
    { rel: 'canonical', href: 'https://resume-roaster.com/' },
  ],
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@graph': [
          {
            '@type': 'WebApplication',
            'name': 'Resume Roaster',
            'url': 'https://resume-roaster.com',
            'description': 'AI-powered resume analyzer that scores job match, rewrites bullets, checks ATS compatibility, generates cover letters, and rewrites entire resumes.',
            'applicationCategory': 'BusinessApplication',
            'operatingSystem': 'Web',
            'offers': {
              '@type': 'Offer',
              'price': '0',
              'priceCurrency': 'USD',
              'description': '1 free credit on signup'
            },
            'featureList': [
              'AI Resume Match Scoring',
              'ATS Keyword Heatmap',
              'Bullet Point Rewriting',
              'Full Resume Rewrite with PDF Export',
              'Cover Letter Generation',
              'Interview Prep Questions',
              'LinkedIn Profile Optimization',
              'Email Follow-Up Templates'
            ]
          },
          {
            '@type': 'FAQPage',
            'mainEntity': [
              {
                '@type': 'Question',
                'name': 'How does Resume Roaster work?',
                'acceptedAnswer': {
                  '@type': 'Answer',
                  'text': 'Upload your resume (PDF or DOCX) and paste the job description. Our AI analyzes the match, scores compatibility 0-100, rewrites weak bullets, flags ATS issues, and generates a tailored cover letter — all in seconds.'
                }
              },
              {
                '@type': 'Question',
                'name': 'Is Resume Roaster free?',
                'acceptedAnswer': {
                  '@type': 'Answer',
                  'text': 'You get 1 free credit on signup with no credit card required. Additional credits start at $9 for 3 credits.'
                }
              },
              {
                '@type': 'Question',
                'name': 'What is an ATS keyword check?',
                'acceptedAnswer': {
                  '@type': 'Answer',
                  'text': 'ATS (Applicant Tracking System) software scans resumes for keywords from the job description. Resume Roaster shows exactly which keywords are present and which are missing with a color-coded heatmap.'
                }
              }
            ]
          }
        ]
      }),
    },
  ],
})

const authStore = useAuthStore()

const features = [
  {
    icon: 'mdi-chart-bar',
    title: 'Match Score',
    description: 'Get a 0-100 compatibility score showing how well your resume aligns with the job description.',
  },
  {
    icon: 'mdi-fire',
    title: 'Keyword Heatmap',
    description: 'See exactly which JD keywords are in your resume and which are missing — color-coded and actionable.',
  },
  {
    icon: 'mdi-file-document-edit-outline',
    title: 'Full Resume Rewrite',
    description: 'Get your entire resume rewritten and optimized for the job. Download as a formatted PDF.',
  },
  {
    icon: 'mdi-account-question',
    title: 'Interview Prep',
    description: 'AI generates likely interview questions with STAR answer frameworks based on the JD and your resume gaps.',
  },
  {
    icon: 'mdi-robot-outline',
    title: 'ATS Checker',
    description: 'Missing keywords, formatting problems, and non-standard headers are flagged before they knock you out.',
  },
  {
    icon: 'mdi-email-multiple',
    title: 'Email Templates',
    description: 'Follow-up, thank you, and outreach emails personalized to the company and role.',
  },
  {
    icon: 'mdi-linkedin',
    title: 'LinkedIn Optimizer',
    description: 'Optimize your headline, About section, and skills for recruiter search visibility.',
  },
]

const steps = [
  {
    title: 'Upload your resume',
    description: 'Drop in your current resume as a PDF or DOCX. We keep it private and never share it.',
  },
  {
    title: 'Paste the job description',
    description: 'Copy the full job posting so the AI can match your experience to what the employer actually wants.',
  },
  {
    title: 'Get your report',
    description: 'In seconds you get a match score, keyword heatmap, rewritten bullets, ATS flags, cover letter, and email templates.',
  },
]
</script>

<style scoped>
.hero-section {
  background: linear-gradient(135deg, #0d0d1a 0%, #1a1a2e 40%, #0f3460 100%);
  color: white;
  min-height: min(100svh, 700px);
  display: flex;
  align-items: center;
  position: relative;
  overflow: hidden;
}

.hero-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 700px;
  height: 700px;
  background: radial-gradient(ellipse, rgba(230, 74, 25, 0.12) 0%, transparent 70%);
  pointer-events: none;
}

.hero-content {
  position: relative;
  z-index: 1;
}

.hero-title {
  font-size: clamp(2rem, 5vw, 3.5rem);
  font-weight: 800;
  line-height: 1.12;
  color: white;
}

.hero-subtitle {
  font-size: 1.15rem;
  max-width: 560px;
  color: rgba(255, 255, 255, 0.75);
}

.hero-cta {
  box-shadow: 0 0 32px rgba(230, 74, 25, 0.35);
}

/* Hero entrance animation */
.hero-fade-enter-active {
  transition: opacity 0.7s ease, transform 0.7s ease;
}
.hero-fade-enter-from {
  opacity: 0;
  transform: translateY(28px);
}

.hero-stats {
  gap: 0;
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: rgba(255, 255, 255, 0.15);
  align-self: center;
}

/* Feature cards */
.feature-icon-wrap {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  background: rgba(230, 74, 25, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
}

.feature-card {
  border: 1px solid rgba(0, 0, 0, 0.06) !important;
  transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
}
.feature-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 16px 40px rgba(230, 74, 25, 0.1) !important;
  border-color: rgba(230, 74, 25, 0.25) !important;
}

/* Steps */
.steps-row {
  display: flex;
  justify-content: center;
  gap: 2rem;
  flex-wrap: wrap;
}

.step-item {
  flex: 1;
  min-width: 220px;
  max-width: 320px;
  text-align: center;
  position: relative;
  padding: 0 1rem;
}

.step-item:not(:last-child)::after {
  content: '';
  position: absolute;
  top: 26px;
  right: -1rem;
  width: calc(2rem);
  height: 2px;
  background: linear-gradient(to right, #e64a19, rgba(230, 74, 25, 0.15));
}

@media (max-width: 700px) {
  .step-item:not(:last-child)::after {
    display: none;
  }
}

.step-number {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: linear-gradient(135deg, #E64A19, #BF360C);
  color: white;
  font-size: 1.25rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 16px rgba(230, 74, 25, 0.3);
}

/* Sample output card */
.sample-card {
  border: 1px solid rgba(0, 0, 0, 0.08) !important;
  box-shadow: 0 0 60px rgba(230, 74, 25, 0.06) !important;
}

/* CTA */
.cta-section {
  background: linear-gradient(135deg, #E64A19 0%, #BF360C 100%);
}

.cta-btn {
  color: #E64A19 !important;
}
.cta-btn:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}
</style>
