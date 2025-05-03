<template>
  <div class="mt-8 pt-6 border-t border-secondary">
    <h3 class="text-primary mb-4 text-xl font-serif">
      Theme Summary: {{ formatThemeName(theme) }}
    </h3>
    <div class="bg-light p-6 rounded border-l-4 border-primary">
      <p>
        The theme "{{ formatThemeName(theme) }}" evolved in the year {{ year }}.
        France and Germany had different poetic traditions, and the theme "{{
          formatThemeName(theme)
        }}" was more prominent in France.
      </p>
      <p class="mt-4 text-sm text-text opacity-70 italic">
        This is a analysis of the theme "{{ formatThemeName(theme) }}" in the
        year {{ year }}.
      </p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  theme: {
    type: String,
    required: true,
  },
  year: {
    type: Number,
    required: true,
  },
});

const formatThemeName = (theme) => theme.replace(/_/g, " ");
</script>
