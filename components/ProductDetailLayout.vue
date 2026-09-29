<template>
  <div class="pb-12" :style="{ background: 'linear-gradient(135deg, var(--mc-jade-faint), var(--mc-surface), var(--mc-jade-faint))' }">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24">

      <ClientOnly>
        <UBreadcrumb
          v-if="links && links.length > 1"
          :links="links"
          :ui="{
            wrapper: 'mb-6 text-sm breadcrumb-jade',
            base: 'ubreadcrumb-base',
            active: 'ubreadcrumb-active',
            label: 'ubreadcrumb-label',
            divider: { base: 'ubreadcrumb-divider' }
          }"
          divider="/"
        />
      </ClientOnly>

      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 spinner-jade"></div>
        <p class="mt-4" style="color: var(--mc-ink-muted);">Loading...</p>
      </div>

      <div v-else-if="error" class="text-center py-12 rounded-lg" style="background: oklch(55% 0.20 25 / 0.08);">
        <p style="color: var(--mc-error);">{{ error }}</p>
      </div>

      <div v-else-if="entity" class="rounded-xl overflow-hidden" style="background: var(--mc-surface-raised); box-shadow: var(--mc-shadow-lg);">

        <!-- Cover Image (standalone, no overlay) -->
        <div class="rounded-xl overflow-hidden" style="box-shadow: var(--mc-shadow-sm);">
          <img
            :src="entity.visuals?.cover?.url || entity.cover?.url || '/images/placeholder.svg'"
            :alt="entity.overview?.title"
            width="1200" height="600"
            class="w-full h-80 object-cover"
          />
        </div>

        <!-- Header Card (separate from cover) -->
        <div class="p-8" style="background: var(--mc-surface-raised);">
          <div class="flex items-center space-x-4 mb-4">
            <span class="inline-block px-3 py-1 text-sm font-medium text-white rounded-full" style="background: var(--mc-jade);">
              {{ entityTypeLabel }}
            </span>
            <span v-if="entity.meta?.readTime" class="inline-block px-3 py-1 text-sm font-medium rounded-full" style="background: var(--mc-jade-faint); color: var(--mc-jade-dark);">
              {{ entity.meta.readTime }} {{ t('pages.services.readTime') }}
            </span>
          </div>
          <h1 class="text-4xl font-bold mb-2" style="color: var(--mc-ink);">
            {{ entity.overview?.title }}
          </h1>
          <p class="text-xl" style="color: var(--mc-ink-soft);">
            {{ entity.overview?.excerpt }}
          </p>
          <p v-if="entity.overview?.subtitle" class="text-base mt-2" style="color: var(--mc-ink-muted);">
            {{ entity.overview.subtitle }}
          </p>
          <div v-if="entity.meta?.difficulty || entity.meta?.duration || entity.meta?.priceRange" class="flex flex-wrap gap-2 mt-3">
            <span v-if="entity.meta?.difficulty" class="inline-block px-3 py-1 text-xs font-medium text-white rounded-full" style="background: var(--mc-jade);">
              {{ entity.meta.difficulty }}
            </span>
            <span v-if="entity.meta?.duration" class="inline-block px-3 py-1 text-xs font-medium text-white rounded-full" style="background: var(--mc-jade-dark);">
              {{ entity.meta.duration }}
            </span>
            <span v-if="entity.meta?.priceRange" class="inline-block px-3 py-1 text-xs font-medium text-white rounded-full" style="background: var(--mc-amber);">
              {{ entity.meta.priceRange }}
            </span>
          </div>
        </div>

        <!-- 商品购买区（仅 products 详情页传入） -->
        <div v-if="$slots.buyBox" class="p-8" style="background: var(--mc-surface-raised); border-top: 1px solid var(--mc-border);">
          <slot name="buyBox" />
        </div>

        <div class="p-8 pt-4">
          <slot name="stats" />

          <div v-if="entity.highlights && entity.highlights.length > 0" class="mb-8 mt-8">
            <h2 class="text-2xl font-bold mb-4" style="color: var(--mc-ink);">{{ t('pages.services.detail.highlights') }}</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div
                v-for="(highlight, idx) in entity.highlights"
                :key="idx"
                class="flex items-start space-x-3 rounded-lg p-4 border"
                :style="{ background: 'oklch(52% 0.16 185 / 0.06)', borderColor: 'oklch(52% 0.16 185 / 0.12)' }"
              >
                <span class="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-sm mt-0.5" style="background: var(--mc-jade-faint); color: var(--mc-jade-dark);">&#10003;</span>
                <p style="color: var(--mc-ink-soft);">{{ highlight }}</p>
              </div>
            </div>
          </div>

          <!-- Structured content sections (introduction, procedure, comparison) -->
          <template v-if="entity.introduction || entity.procedure || entity.comparison">
            <div v-if="entity.introduction" class="mb-8">
              <h2 class="text-2xl font-bold mb-4" style="color: var(--mc-ink);">{{ t('pages.services.detail.introduction') || 'Introduction' }}</h2>
              <div class="rounded-xl p-6 border" :style="{ background: 'var(--mc-surface-raised)', borderColor: 'var(--mc-border)' }">
                <div v-html="renderMarkdown(entity.introduction)" class="prose prose-lg max-w-none"></div>
              </div>
            </div>
            <div v-if="entity.procedure" class="mb-8">
              <h2 class="text-2xl font-bold mb-4" style="color: var(--mc-ink);">{{ t('pages.services.detail.procedure') || 'How It Works' }}</h2>
              <div class="rounded-xl p-6 border" :style="{ background: 'var(--mc-surface-raised)', borderColor: 'var(--mc-border)' }">
                <div v-html="renderMarkdown(entity.procedure)" class="prose prose-lg max-w-none"></div>
              </div>
            </div>
            <div v-if="entity.comparison" class="mb-8">
              <h2 class="text-2xl font-bold mb-4" style="color: var(--mc-ink);">{{ t('pages.services.detail.comparison') || 'Comparison' }}</h2>
              <div class="rounded-xl p-6 border" :style="{ background: 'var(--mc-surface-raised)', borderColor: 'var(--mc-border)' }">
                <div v-html="renderMarkdown(entity.comparison)" class="prose prose-lg max-w-none"></div>
              </div>
            </div>
          </template>
          <!-- Legacy body / description (blog, provider, or old service format) -->
          <div v-else-if="entity.body" v-html="renderMarkdown(entity.body)" class="prose prose-lg max-w-none mb-8 mt-8"></div>
          <div v-else-if="entity.description" class="prose prose-lg max-w-none mb-8 mt-8">
            <div v-if="parsedDescription.length === 0" v-html="renderMarkdown(entity.description)"></div>
            <template v-else>
              <div v-if="parsedDescription[0].heading === ''" v-html="renderMarkdown(parsedDescription[0].content)" class="mb-8"></div>
              <div v-for="(section, idx) in parsedDescription.filter(s => s.heading !== '')" :key="idx" class="mb-8">
                <h2 class="text-2xl font-bold mb-4" style="color: var(--mc-ink);">{{ section.heading }}</h2>
                <div
                  class="rounded-xl p-6 border"
                  :style="{
                    background: idx % 2 === 0 ? 'var(--mc-surface-raised)' : 'oklch(52% 0.16 185 / 0.04)',
                    borderColor: 'var(--mc-border)'
                  }"
                >
                  <div v-html="renderMarkdown(section.content)" class="prose prose-lg max-w-none"></div>
                </div>
              </div>
            </template>
          </div>
          <div v-else class="prose prose-lg max-w-none mb-8 mt-8">
            <p style="color: var(--mc-ink-muted);">
              {{ entity.overview?.summary || entity.seo?.description }}
            </p>
          </div>

          <!-- Team (provider) -->
          <div v-if="entity.team && entity.team.length > 0" class="mb-8 mt-8">
            <h2 class="text-2xl font-bold mb-6" style="color: var(--mc-ink);">{{ t('pages.services.detail.team') }}</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div
                v-for="(member, idx) in entity.team"
                :key="idx"
                class="rounded-xl p-6 border"
                :style="{ background: 'var(--mc-surface-raised)', borderColor: 'var(--mc-border)' }"
              >
                <div class="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-lg mb-3" style="background: var(--mc-jade);">
                  {{ (member.name || '?').charAt(0) }}
                </div>
                <h3 class="text-lg font-bold" style="color: var(--mc-ink);">{{ member.name }}</h3>
                <p v-if="member.title" class="text-sm mt-1" style="color: var(--mc-ink-soft);">{{ member.title }}</p>
                <p v-if="member.qualifications" class="text-xs mt-2 italic" style="color: var(--mc-ink-muted);">{{ member.qualifications }}</p>
                <div v-if="member.specialties && member.specialties.length" class="flex flex-wrap gap-1 mt-3">
                  <span
                    v-for="spec in member.specialties"
                    :key="spec"
                    class="inline-block px-2 py-0.5 text-xs rounded-full"
                    :style="{ background: 'oklch(52% 0.16 185 / 0.08)', color: 'var(--mc-jade-dark)' }"
                  >
                    {{ spec }}
                  </span>
                </div>
                <p v-if="member.languages && member.languages.length" class="text-xs mt-2" style="color: var(--mc-ink-faint);">
                  Languages: {{ member.languages.join(', ') }}
                </p>
              </div>
            </div>
          </div>

          <!-- Services (provider) -->
          <div v-if="entity.services && entity.services.length > 0" class="mb-8">
            <h2 class="text-2xl font-bold mb-4" style="color: var(--mc-ink);">{{ t('pages.services.detail.services') }}</h2>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="(svc, idx) in entity.services"
                :key="idx"
                class="inline-block px-4 py-2 text-sm font-medium rounded-full border"
                :style="{ background: 'oklch(52% 0.16 185 / 0.06)', borderColor: 'oklch(52% 0.16 185 / 0.15)', color: 'var(--mc-jade-dark)' }"
              >
                {{ svc }}
              </span>
            </div>
          </div>

          <!-- Contact Info (provider) -->
          <div v-if="entity.institution?.contact" class="mb-8 rounded-xl p-6 border" :style="{ background: 'var(--mc-surface-raised)', borderColor: 'var(--mc-border)' }">
            <h2 class="text-xl font-bold mb-4" style="color: var(--mc-ink);">{{ t('pages.services.detail.contact') }}</h2>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
              <div v-if="entity.institution.contact.phone">
                <span class="font-medium" style="color: var(--mc-ink-muted);">Phone</span>
                <p style="color: var(--mc-ink);">{{ entity.institution.contact.phone }}</p>
              </div>
              <div v-if="entity.institution.contact.email">
                <span class="font-medium" style="color: var(--mc-ink-muted);">Email</span>
                <p style="color: var(--mc-ink);">{{ entity.institution.contact.email }}</p>
              </div>
              <div v-if="entity.institution.contact.website">
                <span class="font-medium" style="color: var(--mc-ink-muted);">Website</span>
                <a :href="entity.institution.contact.website" target="_blank" rel="noopener noreferrer" class="hover:underline" style="color: var(--mc-jade);">{{ entity.institution.contact.website }}</a>
              </div>
              <div v-if="entity.institution.contact.workingHours">
                <span class="font-medium" style="color: var(--mc-ink-muted);">Hours</span>
                <p style="color: var(--mc-ink);">{{ entity.institution.contact.workingHours }}</p>
              </div>
            </div>
            <div v-if="entity.institution?.address" class="mt-4 pt-4 border-t" :style="{ borderColor: 'var(--mc-border)' }">
              <span class="font-medium text-sm" style="color: var(--mc-ink-muted);">Address</span>
              <p style="color: var(--mc-ink);">
                {{ entity.institution.address.street }}{{ entity.institution.address.street && entity.institution.address.city ? ', ' : '' }}{{ entity.institution.address.city }}
              </p>
            </div>
          </div>

          <!-- Pricing Tiers (service) — hover to reveal inclusions/exclusions -->
          <div v-if="entity.pricing?.tiers && entity.pricing.tiers.length > 0" class="mb-8 mt-8">
            <h2 class="text-2xl font-bold mb-6" style="color: var(--mc-ink);">{{ t('pages.services.detail.pricing') }}</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div
                v-for="(tier, idx) in entity.pricing.tiers"
                :key="idx"
                class="group relative rounded-xl p-6 border flex flex-col transition-all duration-200"
                :style="{
                  background: idx === 0 ? 'var(--mc-surface-raised)' : 'oklch(52% 0.16 185 / 0.05)',
                  borderColor: idx === 0 ? 'var(--mc-border)' : 'oklch(52% 0.16 185 / 0.15)'
                }"
              >
                <!-- Default view -->
                <div>
                  <div class="flex items-center justify-between mb-3">
                    <h3 class="text-xl font-bold" style="color: var(--mc-ink);">{{ tier.name }}</h3>
                    <div class="text-right">
                      <span class="text-2xl font-bold" style="color: var(--mc-jade-dark);">${{ tier.price }}</span>
                      <span class="text-sm" style="color: var(--mc-ink-muted);"> / {{ tier.unit }}</span>
                    </div>
                  </div>
                  <p class="text-sm" style="color: var(--mc-ink-soft);">{{ tier.description }}</p>
                  <p
                    v-if="tier.inclusions?.length || entity.pricing.exclusions?.length"
                    class="text-xs mt-3 italic opacity-0 group-hover:opacity-100 transition-opacity duration-200"
                    style="color: var(--mc-jade);"
                  >
                    &#9432; {{ t('pages.services.detail.hoverDetails') }}
                  </p>
                </div>

                <!-- Bubble popup: inclusions + exclusions -->
                <div
                  v-if="tier.inclusions?.length || entity.pricing.exclusions?.length"
                  class="absolute bottom-full left-1/2 -translate-x-1/2 mb-3 w-72 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-20"
                >
                  <!-- Arrow pointing down -->
                  <div
                    class="absolute top-full left-1/2 -translate-x-1/2 w-0 h-0 border-l-8 border-r-8 border-t-8 border-transparent"
                    :style="{ borderTopColor: 'var(--mc-jade)' }"
                  ></div>
                  <!-- Popup body -->
                  <div
                    class="rounded-xl p-4 shadow-lg"
                    :style="{ background: 'var(--mc-surface-raised)', border: '2px solid var(--mc-jade)' }"
                  >
                    <div v-if="tier.inclusions?.length" class="mb-3">
                      <p class="text-xs font-bold uppercase tracking-wide mb-2" style="color: var(--mc-jade-dark);">{{ t('pages.services.detail.inclusions') }}</p>
                      <ul class="space-y-1">
                        <li v-for="(item, i) in tier.inclusions" :key="i" class="flex items-start space-x-2 text-sm" style="color: var(--mc-ink);">
                          <span class="flex-shrink-0 mt-0.5" style="color: var(--mc-jade);">&#10003;</span>
                          <span>{{ item.label }}</span>
                        </li>
                      </ul>
                    </div>
                    <div v-if="entity.pricing.exclusions?.length">
                      <p class="text-xs font-bold uppercase tracking-wide mb-2" style="color: var(--mc-amber-dark);">{{ t('pages.services.detail.exclusions') }}</p>
                      <ul class="space-y-1">
                        <li v-for="(excl, i) in entity.pricing.exclusions" :key="i" class="flex items-start space-x-2 text-sm" style="color: var(--mc-ink-muted);">
                          <span class="flex-shrink-0 mt-0.5">&#10005;</span>
                          <span>{{ excl }}</span>
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="entity.process?.steps && entity.process.steps.length > 0" class="mb-8 mt-8">
            <h2 class="text-2xl font-bold mb-6" style="color: var(--mc-ink);">{{ entity.process.title || t('pages.services.detail.process') }}</h2>
            <div class="rounded-xl p-6 border" :style="{ background: 'var(--mc-surface-raised)', borderColor: 'var(--mc-border)' }">
              <div class="space-y-4">
                <div
                  v-for="(step, idx) in entity.process.steps"
                  :key="idx"
                  class="relative pl-8 border-l-2 pb-4 last:pb-0"
                  :style="{ borderColor: 'var(--mc-jade-pale)' }"
                >
                  <div class="absolute -left-3 top-0 w-6 h-6 text-white rounded-full flex items-center justify-center text-xs font-bold" style="background: var(--mc-jade);">
                    {{ idx + 1 }}
                  </div>
                  <h3 class="font-semibold" style="color: var(--mc-ink);">{{ step.title }}</h3>
                  <p class="mt-1" style="color: var(--mc-ink-muted);">{{ step.description }}</p>
                  <div class="flex flex-wrap gap-3 mt-2 text-sm" style="color: var(--mc-ink-faint);">
                    <span v-if="step.duration" class="inline-flex items-center">
                      <span class="w-4 h-4 mr-1">&#9200;</span>
                      {{ step.duration }}
                    </span>
                    <span v-if="step.cost" class="inline-flex items-center">
                      <span class="w-4 h-4 mr-1">&#128176;</span>
                      {{ step.cost }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="entity.outcome" class="mb-8">
            <h2 class="text-2xl font-bold mb-4" style="color: var(--mc-ink);">{{ t('pages.services.detail.outcome') || 'Outcomes & Support' }}</h2>
            <div class="rounded-xl p-6 border" :style="{ background: 'var(--mc-surface-raised)', borderColor: 'var(--mc-border)' }">
              <div v-html="renderMarkdown(entity.outcome)" class="prose prose-lg max-w-none"></div>
            </div>
          </div>

          <div v-if="entity.conditions?.items && entity.conditions.items.length > 0" class="mb-8">
            <h2 class="text-2xl font-bold mb-4" style="color: var(--mc-ink);">{{ entity.conditions.title || t('pages.services.detail.conditions') }}</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div
                v-for="(item, idx) in entity.conditions.items"
                :key="idx"
                class="rounded-lg p-4 border-l-4 flex items-start"
                :style="{ background: 'oklch(72% 0.14 78 / 0.07)', borderColor: 'oklch(72% 0.14 78 / 0.15)', borderLeftColor: 'var(--mc-amber)' }"
              >
                <div>
                  <p class="font-medium text-sm" style="color: var(--mc-amber-dark);">{{ item.key }}</p>
                  <p class="text-sm mt-1" style="color: var(--mc-ink-soft);">{{ item.value }}</p>
                </div>
              </div>
            </div>
          </div>

          <FaqAccordion
            v-if="entity.faq && entity.faq.length > 0"
            :items="normalizeFaq(entity.faq)"
            :title="t('common.faqTitle')"
          />

          <!-- Testimonials (service) -->
          <div v-if="entity.testimonials && entity.testimonials.length > 0" class="mb-8">
            <h2 class="text-2xl font-bold mb-4" style="color: var(--mc-ink);">{{ t('pages.services.detail.testimonials') }}</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div
                v-for="(t, idx) in entity.testimonials"
                :key="idx"
                class="rounded-xl p-6 border flex flex-col"
                :style="{ background: 'var(--mc-surface-raised)', borderColor: 'var(--mc-border)' }"
              >
                <div class="flex items-center mb-3">
                  <div class="w-10 h-10 text-white rounded-full flex items-center justify-center font-bold text-sm mr-3" style="background: var(--mc-jade);">
                    {{ (t.name || '?').charAt(0) }}
                  </div>
                  <div>
                    <p class="font-medium text-sm" style="color: var(--mc-ink);">{{ t.name }}</p>
                    <p v-if="t.country" class="text-xs" style="color: var(--mc-ink-faint);">{{ t.country }}</p>
                  </div>
                  <div v-if="t.rating" class="ml-auto flex">
                    <span v-for="n in 5" :key="n" :style="{ color: n <= t.rating ? 'var(--mc-amber)' : 'var(--mc-ink-faint)' }">&#9733;</span>
                  </div>
                </div>
                <p class="text-sm italic flex-grow" style="color: var(--mc-ink-soft);">&ldquo;{{ t.quote }}&rdquo;</p>
              </div>
            </div>
          </div>

          <div v-if="entity.references && entity.references.length > 0" class="mb-8">
            <h2 class="text-2xl font-bold mb-4" style="color: var(--mc-ink);">{{ t('pages.services.detail.references') }}</h2>
            <ul class="space-y-2">
              <li
                v-for="(ref, idx) in entity.references"
                :key="idx"
                class="flex items-start space-x-2"
              >
                <span class="text-sm flex-shrink-0" style="color: var(--mc-jade-lighter);">&#128279;</span>
                <a
                  :href="ref.url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-sm hover:underline"
                  style="color: var(--mc-jade);"
                >{{ ref.title }}</a>
              </li>
            </ul>
          </div>

          <div v-if="entity.tags?.primary?.length > 0 || entity.tags?.secondary?.length > 0" class="mb-8 flex flex-wrap gap-2">
            <span
              v-for="tag in entity.tags?.primary"
              :key="tag.id"
              class="inline-block px-3 py-1 text-sm font-medium rounded-full"
              :style="{ background: 'var(--mc-jade-pale)', color: 'var(--mc-jade-dark)' }"
            >
              {{ tag.name }}
            </span>
            <span
              v-for="tag in entity.tags?.secondary"
              :key="tag.id"
              class="inline-block px-3 py-1 text-sm font-medium rounded-full"
              :style="{ background: 'var(--mc-surface-alt)', color: 'var(--mc-ink-muted)' }"
            >
              {{ tag.name }}
            </span>
          </div>

          <div v-if="entity.visuals?.gallery && entity.visuals.gallery.length > 0" class="mb-8">
            <h2 class="text-2xl font-bold mb-4" style="color: var(--mc-ink);">{{ t('pages.services.detail.gallery') }}</h2>
            <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
              <img
                v-for="(img, idx) in entity.visuals.gallery"
                :key="idx"
                :src="img.url"
                :alt="img.alt || entity.overview?.title"
                width="400" height="192"
                class="w-full h-48 object-cover rounded-lg"
                :style="{ boxShadow: 'var(--mc-shadow-sm)' }"
                loading="lazy"
              />
            </div>
          </div>

          <div v-if="entity.meta?.author" class="mb-8 p-4 rounded-lg border" :style="{ background: 'var(--mc-surface-alt)', borderColor: 'var(--mc-border)' }">
            <h2 class="text-lg font-bold mb-3" style="color: var(--mc-ink);">{{ t('pages.services.detail.author') }}</h2>
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 text-white rounded-full flex items-center justify-center font-bold text-lg" style="background: var(--mc-jade);">
                {{ (entity.meta.author.name || '?').charAt(0) }}
              </div>
              <div>
                <p class="font-medium" style="color: var(--mc-ink);">{{ entity.meta.author.name }}</p>
                <p class="text-sm" style="color: var(--mc-ink-faint);">{{ entity.meta.author.role }}</p>
                <a
                  v-if="entity.meta.author.url"
                  :href="entity.meta.author.url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-xs hover:underline"
                  style="color: var(--mc-jade);"
                >
                  {{ entity.meta.author.url }}
                </a>
              </div>
            </div>
          </div>

          <div v-if="entity.geo?.citationSources?.length > 0 || entity.geo?.keyFacts?.length > 0 || entity.geo?.definitiveClaims?.length > 0" class="mb-8 p-6 rounded-lg border" :style="{ background: 'oklch(60% 0.12 230 / 0.06)', borderColor: 'oklch(60% 0.12 230 / 0.12)' }">
            <div v-if="entity.geo?.citationSources?.length > 0" class="mb-4 last:mb-0">
              <h3 class="font-semibold mb-2" style="color: var(--mc-jade-dark);">{{ t('pages.services.detail.citationSources') }}</h3>
              <ul class="list-disc list-inside text-sm space-y-1" style="color: var(--mc-ink-soft);">
                <li v-for="(src, idx) in entity.geo.citationSources" :key="idx">{{ src }}</li>
              </ul>
            </div>
            <div v-if="entity.geo?.keyFacts?.length > 0" class="mb-4 last:mb-0">
              <h3 class="font-semibold mb-2" style="color: var(--mc-jade-dark);">{{ t('pages.services.detail.keyFacts') }}</h3>
              <ul class="list-disc list-inside text-sm space-y-1" style="color: var(--mc-ink-soft);">
                <li v-for="(fact, idx) in entity.geo.keyFacts" :key="idx">{{ fact }}</li>
              </ul>
            </div>
            <div v-if="entity.geo?.definitiveClaims?.length > 0" class="last:mb-0">
              <h3 class="font-semibold mb-2" style="color: var(--mc-jade-dark);">{{ t('pages.services.detail.definitiveClaims') }}</h3>
              <ul class="list-disc list-inside text-sm space-y-1" style="color: var(--mc-ink-soft);">
                <li v-for="(claim, idx) in entity.geo.definitiveClaims" :key="idx">{{ claim }}</li>
              </ul>
            </div>
          </div>

          <div class="mb-8 text-xs text-right space-y-1" style="color: var(--mc-ink-faint);">
            <div v-if="entity.content?.source">{{ t('pages.services.detail.source') }}: {{ entity.content.source }}</div>
            <div v-if="entity.meta?.updatedAt">Last updated: {{ new Date(entity.meta.updatedAt).toLocaleDateString() }}</div>
            <div v-if="entity.meta?.createdAt">Published: {{ new Date(entity.meta.createdAt).toLocaleDateString() }}</div>
          </div>

          <div class="mb-8 border-l-4 p-4 rounded-lg" :style="{ background: 'oklch(58% 0.15 35 / 0.06)', borderColor: 'var(--mc-warning, oklch(72% 0.14 78))', '--mc-warning': 'var(--mc-amber)' }">
            <p class="text-sm" style="color: var(--mc-amber-dark);">
              {{ t('common.disclaimer') }}
            </p>
          </div>

          <slot name="related" />

          <div class="mt-10 p-8 md:p-10 rounded-xl text-center relative overflow-hidden" style="background: linear-gradient(135deg, var(--mc-jade), var(--mc-deep));">
            <h2 class="text-2xl md:text-3xl font-bold text-white mb-3">{{ t('common.ctaSection.title') }}</h2>
            <p class="text-white/80 mb-6 max-w-xl mx-auto">{{ t('common.ctaSection.description') }}</p>
            <UButton
              :to="localePath(entity.cta?.link || '/contact')"
              size="xl"
              class="bg-white font-semibold rounded-lg shadow-lg hover:bg-white/90 transition-all duration-200"
              style="padding: 1rem 2rem; font-size: 1.05rem; color: var(--mc-jade-dark);"
            >
              {{ entity.cta?.text || t('common.ctaSection.button') }}
            </UButton>
          </div>

          <!-- Share Buttons -->
          <ClientOnly>
            <div v-if="entity?.overview" class="bg-white rounded-lg shadow-sm p-6 mt-8" style="background: var(--mc-surface-raised);">
              <ShareButtons
                :title="entity.overview.title"
                :url="currentUrl"
                :description="entity.seo?.description || entity.overview.excerpt || ''"
                :image="shareImage"
                mode="inline"
              />
            </div>
          </ClientOnly>
        </div>

      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { marked } from 'marked'
import { useLocalePath } from '#imports'
import { useI18n } from 'vue-i18n'

const localePath = useLocalePath()
const { t } = useI18n({ useScope: 'global' })

interface Props {
  loading?: boolean
  error?: string | null
  entity?: any
  links?: Array<{ label: string; to?: string }>
  entityType?: 'service' | 'partner' | 'blog' | 'product'
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  error: null,
  entity: null,
  links: () => [],
  entityType: 'service'
})

const entityTypeLabel = computed(() => {
  const labels: Record<string, string> = {
    service: t('nav.services'),
    partner: t('nav.partners'),
    blog: t('nav.stories'),
  }
  return labels[props.entityType] || t('nav.services')
})

const parsedDescription = computed(() => {
  const desc = props.entity?.description || ''
  if (!desc) return []
  const lines = desc.split('\n')
  const sections: Array<{ heading: string; content: string }> = []
  let current = { heading: '', content: '' }
  for (const line of lines) {
    const m = line.match(/^###\s+(.+)$/)
    if (m) {
      if (current.heading !== '' || current.content.trim()) {
        sections.push({ ...current })
      }
      current = { heading: m[1].trim(), content: '' }
    } else {
      current.content += line + '\n'
    }
  }
  if (current.heading !== '' || current.content.trim()) {
    sections.push({ ...current })
  }
  return sections
})

const renderMarkdown = (content: string): string => {
  try {
    return marked(content) as string
  } catch {
    return content
  }
}

const currentUrl = computed(() => {
  if (process.client) {
    return window.location.href
  }
  const config = useRuntimeConfig()
  const baseUrl = config.public.siteUrl || companyInfo.siteUrl
  const slug = props.entity?.meta?.slug || ''
  const routeBases: Record<string, string> = {
    service: 'services',
    partner: 'partners',
    blog: 'blogs',
    product: 'products'
  }
  return `${baseUrl.replace(/\/+$/, '')}/${routeBases[props.entityType] || props.entityType}/${slug}`
})

const shareImage = computed(() => {
  const raw = props.entity?.visuals?.cover?.url || props.entity?.cover?.url
  if (!raw) return ''
  if (raw.startsWith('http')) return raw
  const config = useRuntimeConfig()
  const baseUrl = config.public.siteUrl || companyInfo.siteUrl
  return `${baseUrl.replace(/\/+$/, '')}/${raw.replace(/^\/+/, '')}`
})

const normalizeFaq = (faq: any[]): any[] => {
  return faq.map((item: any) => {
    if (typeof item === 'object') {
      const question = item.question || item.q || item.title || ''
      const answer = item.answer || item.a || item.content || ''
      return { question, answer }
    }
    return item
  })
}
</script>
