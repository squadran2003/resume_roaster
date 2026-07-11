import { useHead } from '@unhead/vue'

const IMAGE = 'https://resume-roaster.com/resume-roaster.png'

/**
 * Sets title/description/OG/Twitter/canonical plus WebPage + FAQPage JSON-LD
 * for a marketing landing page. Shared by the SEO landing views so schema and
 * meta stay consistent and prerender identically.
 *
 * @param {object} opts
 * @param {string} opts.url         Canonical absolute URL
 * @param {string} opts.title       <title> + og/twitter title
 * @param {string} opts.description meta description
 * @param {Array<{q:string,a:string}>} opts.faqs  FAQ pairs (also rendered visibly)
 */
export function useSeo({ url, title, description, faqs = [] }) {
  const graph = [
    { '@type': 'WebPage', name: title, url, description },
  ]
  if (faqs.length) {
    graph.push({
      '@type': 'FAQPage',
      mainEntity: faqs.map((f) => ({
        '@type': 'Question',
        name: f.q,
        acceptedAnswer: { '@type': 'Answer', text: f.a },
      })),
    })
  }

  useHead({
    title,
    meta: [
      { name: 'description', content: description },
      { property: 'og:type', content: 'website' },
      { property: 'og:title', content: title },
      { property: 'og:description', content: description },
      { property: 'og:url', content: url },
      { property: 'og:image', content: IMAGE },
    ],
    link: [{ rel: 'canonical', href: url }],
    script: [
      {
        type: 'application/ld+json',
        innerHTML: JSON.stringify({ '@context': 'https://schema.org', '@graph': graph }),
      },
    ],
  })
}
