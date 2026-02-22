<template>
  <div>
    <!-- Hero -->
    <section class="hero-section">
      <v-container class="py-16 text-center">
        <v-chip color="orange-darken-2" variant="flat" size="small" class="mb-4 text-uppercase font-weight-bold">
          AI-Powered Resume Analysis
        </v-chip>
        <h1 class="hero-title mb-4">
          Stop Guessing.<br />Start Getting Interviews.
        </h1>
        <p class="hero-subtitle mx-auto mb-8">
          Upload your resume and a job description. Our AI scores the match, rewrites weak bullets,
          flags ATS issues, and generates a tailored cover letter — in seconds.
        </p>
        <div class="d-flex justify-center gap-4 flex-wrap">
          <v-btn
            to="/register"
            color="orange-darken-2"
            size="x-large"
            variant="flat"
            class="font-weight-bold px-8"
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
        <p class="mt-4 text-medium-emphasis text-body-2">No credit card required to get started.</p>
      </v-container>
    </section>

    <!-- Features -->
    <section class="py-16 bg-surface">
      <v-container>
        <div class="text-center mb-12">
          <h2 class="text-h4 font-weight-bold mb-2">Everything you need to land the role</h2>
          <p class="text-medium-emphasis">Four powerful tools, one upload.</p>
        </div>
        <v-row justify="center" class="ga-4">
          <v-col cols="12" sm="6" md="3" v-for="feature in features" :key="feature.title">
            <v-card height="100%" rounded="xl" elevation="0" border class="pa-6 text-center feature-card">
              <v-icon :color="feature.color" size="48" class="mb-4">{{ feature.icon }}</v-icon>
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
        <v-row justify="center" align="stretch">
          <v-col cols="12" md="4" v-for="(step, i) in steps" :key="step.title" class="d-flex">
            <div class="text-center flex-grow-1 px-4">
              <div class="step-number mx-auto mb-4">{{ i + 1 }}</div>
              <div class="text-h6 font-weight-bold mb-2">{{ step.title }}</div>
              <p class="text-body-2 text-medium-emphasis">{{ step.description }}</p>
            </div>
            <v-divider v-if="i < steps.length - 1" vertical class="d-none d-md-flex mx-2 align-self-center step-divider" />
          </v-col>
        </v-row>
      </v-container>
    </section>

    <!-- Sample output -->
    <section class="py-16 bg-surface">
      <v-container>
        <div class="text-center mb-12">
          <h2 class="text-h4 font-weight-bold mb-2">See the analysis in action</h2>
          <p class="text-medium-emphasis">Real feedback, not generic advice.</p>
        </div>
        <v-row justify="center">
          <v-col cols="12" md="8">
            <v-card rounded="xl" elevation="2" class="pa-6">
              <!-- Score bar -->
              <div class="d-flex align-center justify-space-between mb-2">
                <span class="text-body-1 font-weight-medium">Job Match Score</span>
                <v-chip color="green" variant="flat" size="small">78 / 100</v-chip>
              </div>
              <v-progress-linear
                model-value="78"
                color="green"
                bg-color="green-lighten-4"
                height="10"
                rounded
                class="mb-6"
              />

              <!-- Bullet rewrite example -->
              <div class="text-overline text-medium-emphasis mb-2">Bullet Rewrite Example</div>
              <v-card variant="tonal" color="error" rounded="lg" class="pa-3 mb-2">
                <div class="d-flex align-center gap-2">
                  <v-icon color="error" size="18">mdi-close-circle</v-icon>
                  <span class="text-body-2 text-medium-emphasis">Before: <em>"Responsible for managing social media accounts."</em></span>
                </div>
              </v-card>
              <v-card variant="tonal" color="success" rounded="lg" class="pa-3 mb-6">
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
        <p class="text-body-1 mb-8 mx-auto" style="max-width:480px;opacity:.85;color:white;">
          Join thousands of job seekers who've improved their resume with AI-powered feedback.
        </p>
        <v-btn
          to="/register"
          color="white"
          size="x-large"
          variant="flat"
          class="font-weight-bold px-10 cta-btn"
        >
          Get Started Free
        </v-btn>
      </v-container>
    </section>

    <!-- Footer -->
    <v-footer class="bg-surface py-6">
      <v-container>
        <div class="d-flex flex-wrap justify-space-between align-center gap-4">
          <span class="font-weight-bold">Resume Roaster</span>
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
const features = [
  {
    icon: 'mdi-chart-bar',
    color: 'orange-darken-2',
    title: 'Match Score',
    description: 'Get a 0–100 compatibility score showing how well your resume aligns with the job description.',
  },
  {
    icon: 'mdi-pencil-outline',
    color: 'blue-darken-2',
    title: 'Bullet Rewriter',
    description: 'Weak bullets are rewritten with strong action verbs and measurable outcomes that grab attention.',
  },
  {
    icon: 'mdi-robot-outline',
    color: 'purple-darken-2',
    title: 'ATS Checker',
    description: "Missing keywords, formatting problems, and non-standard headers are flagged before they knock you out.",
  },
  {
    icon: 'mdi-file-document-edit-outline',
    color: 'green-darken-2',
    title: 'Cover Letter',
    description: 'A tailored cover letter is generated for each job — ready to send, easy to edit.',
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
    description: 'In seconds you receive a match score, rewritten bullets, ATS flags, and a ready-to-send cover letter.',
  },
]
</script>

<style scoped>
.hero-section {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  color: white;
  min-height: 520px;
  display: flex;
  align-items: center;
}

.hero-title {
  font-size: clamp(2rem, 5vw, 3.5rem);
  font-weight: 800;
  line-height: 1.15;
  color: white;
}

.hero-subtitle {
  font-size: 1.125rem;
  max-width: 560px;
  opacity: 0.85;
  color: white;
}

.feature-card {
  transition: transform 0.2s, box-shadow 0.2s;
}
.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.12) !important;
}

.step-number {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: #e64a19;
  color: white;
  font-size: 1.25rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.step-divider {
  height: 80px;
  opacity: 0.3;
}

.cta-section {
  background: linear-gradient(135deg, #e64a19 0%, #bf360c 100%);
}

.cta-btn {
  color: #e64a19 !important;
}
</style>
