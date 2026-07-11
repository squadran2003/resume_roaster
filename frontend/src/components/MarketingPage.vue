<template>
  <div>
    <!-- Hero -->
    <section class="mk-hero">
      <div class="mk-hero-glow" />
      <v-container class="py-16 text-center mk-hero-content">
        <v-chip color="primary" variant="flat" size="small" class="mb-5 text-uppercase font-weight-bold">
          {{ eyebrow }}
        </v-chip>
        <h1 class="mk-title mb-5">{{ title }}</h1>
        <p class="mk-subtitle mx-auto mb-8">{{ subtitle }}</p>
        <div class="d-flex justify-center gap-4 flex-wrap mb-4">
          <v-btn to="/register" color="primary" size="x-large" variant="flat" class="font-weight-bold px-8 mk-cta">
            {{ ctaText }}
          </v-btn>
          <v-btn to="/" size="x-large" variant="outlined" color="white" class="px-8">
            See all tools
          </v-btn>
        </div>
        <p class="text-body-2" style="color: rgba(255,255,255,0.6);">
          2 free credits on signup — no credit card required.
        </p>
      </v-container>
    </section>

    <!-- Intro copy -->
    <section class="py-16 bg-surface">
      <v-container>
        <v-row justify="center">
          <v-col cols="12" md="8" class="text-center">
            <h2 class="text-h4 font-weight-bold mb-4">{{ introHeading }}</h2>
            <p class="text-body-1 text-medium-emphasis" style="line-height: 1.7;">{{ introBody }}</p>
          </v-col>
        </v-row>
      </v-container>
    </section>

    <!-- Features -->
    <section class="py-16">
      <v-container>
        <div class="text-center mb-12">
          <h2 class="text-h4 font-weight-bold mb-2">{{ featuresHeading }}</h2>
        </div>
        <v-row justify="center">
          <v-col cols="12" sm="6" md="4" v-for="feature in features" :key="feature.title">
            <v-card height="100%" elevation="0" class="pa-6 text-center mk-feature-card">
              <div class="mk-feature-icon mx-auto mb-4">
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
    <section class="py-16 bg-surface">
      <v-container>
        <div class="text-center mb-12">
          <h2 class="text-h4 font-weight-bold mb-2">How it works</h2>
        </div>
        <div class="mk-steps-row">
          <div v-for="(step, i) in steps" :key="step.title" class="mk-step-item">
            <div class="mk-step-number mx-auto mb-4">{{ i + 1 }}</div>
            <div class="text-h6 font-weight-bold mb-2">{{ step.title }}</div>
            <p class="text-body-2 text-medium-emphasis">{{ step.description }}</p>
          </div>
        </div>
      </v-container>
    </section>

    <!-- FAQ (visible; JSON-LD is emitted by the parent view via useHead) -->
    <section class="py-16">
      <v-container>
        <div class="text-center mb-10">
          <h2 class="text-h4 font-weight-bold mb-2">Frequently asked questions</h2>
        </div>
        <v-row justify="center">
          <v-col cols="12" md="8">
            <v-expansion-panels variant="accordion">
              <v-expansion-panel v-for="faq in faqs" :key="faq.q" :title="faq.q" :text="faq.a" />
            </v-expansion-panels>
          </v-col>
        </v-row>
      </v-container>
    </section>

    <!-- Related tools (internal linking) -->
    <section v-if="related.length" class="py-12 bg-surface">
      <v-container>
        <div class="text-center mb-8">
          <h2 class="text-h5 font-weight-bold">Related tools</h2>
        </div>
        <div class="d-flex justify-center flex-wrap gap-3">
          <v-btn
            v-for="link in related"
            :key="link.to"
            :to="link.to"
            variant="tonal"
            color="primary"
            :prepend-icon="link.icon"
          >
            {{ link.label }}
          </v-btn>
        </div>
      </v-container>
    </section>

    <!-- CTA -->
    <section class="mk-cta-section py-16 text-center">
      <v-container>
        <h2 class="text-h4 font-weight-bold mb-4 text-white">{{ ctaHeading }}</h2>
        <p class="text-body-1 mb-8 mx-auto" style="max-width:480px;opacity:.85;color:white;">{{ ctaSubtext }}</p>
        <v-btn to="/register" color="white" size="x-large" variant="flat" class="font-weight-bold px-10 mk-cta-btn">
          {{ ctaText }}
        </v-btn>
      </v-container>
    </section>

    <!-- Footer -->
    <v-footer class="bg-surface py-6">
      <v-container>
        <div class="d-flex flex-wrap justify-space-between align-center gap-4">
          <router-link to="/" class="d-flex align-center text-decoration-none" style="gap: 8px;">
            <v-icon icon="mdi-fire" color="primary" size="22" />
            <span class="font-weight-bold">Resume Roaster</span>
          </router-link>
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
defineProps({
  eyebrow: { type: String, required: true },
  title: { type: String, required: true },
  subtitle: { type: String, required: true },
  ctaText: { type: String, default: 'Roast My Resume' },
  introHeading: { type: String, required: true },
  introBody: { type: String, required: true },
  featuresHeading: { type: String, default: 'What you get' },
  features: { type: Array, required: true },
  steps: { type: Array, required: true },
  faqs: { type: Array, required: true },
  related: { type: Array, default: () => [] },
  ctaHeading: { type: String, default: 'Ready to get the interview?' },
  ctaSubtext: { type: String, default: 'Upload your resume and get AI-powered feedback that actually helps you land the job.' },
})
</script>

<style scoped>
.mk-hero {
  background: linear-gradient(135deg, #0d0d1a 0%, #1a1a2e 40%, #0f3460 100%);
  color: white;
  position: relative;
  overflow: hidden;
}
.mk-hero-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 700px;
  height: 700px;
  background: radial-gradient(ellipse, rgba(230, 74, 25, 0.12) 0%, transparent 70%);
  pointer-events: none;
}
.mk-hero-content {
  position: relative;
  z-index: 1;
}
.mk-title {
  font-size: clamp(1.9rem, 4.5vw, 3rem);
  font-weight: 800;
  line-height: 1.14;
  color: white;
}
.mk-subtitle {
  font-size: 1.12rem;
  max-width: 560px;
  color: rgba(255, 255, 255, 0.78);
}
.mk-cta {
  box-shadow: 0 0 32px rgba(230, 74, 25, 0.35);
}
.mk-feature-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  background: rgba(230, 74, 25, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
}
.mk-feature-card {
  border: 1px solid rgba(0, 0, 0, 0.06) !important;
  transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
}
.mk-feature-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 16px 40px rgba(230, 74, 25, 0.1) !important;
  border-color: rgba(230, 74, 25, 0.25) !important;
}
.mk-steps-row {
  display: flex;
  justify-content: center;
  gap: 2rem;
  flex-wrap: wrap;
}
.mk-step-item {
  flex: 1;
  min-width: 220px;
  max-width: 320px;
  text-align: center;
  padding: 0 1rem;
}
.mk-step-number {
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
.mk-cta-section {
  background: linear-gradient(135deg, #E64A19 0%, #BF360C 100%);
}
.mk-cta-btn {
  color: #E64A19 !important;
}
.mk-cta-btn:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}
</style>
