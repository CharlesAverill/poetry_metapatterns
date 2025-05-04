<template>
  <div class="mt-8 pt-6 border-t border-secondary">
    <h3 class="text-primary mb-4 text-xl font-serif">
      Theme Summary: {{ formatThemeName(theme) }}
    </h3>
    <div class="bg-light p-6 rounded border-l-4 border-primary">
      <div v-if="narrativeContent" v-html="parsedNarrative"></div>
      <p v-else class="text-text opacity-70 italic">
        Loading theme information...
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from "vue";
import { marked } from "marked";

const props = defineProps({
  theme: {
    type: String,
    required: true,
  },
  year: {
    type: Number,
    required: true,
  },
});

const narrativeContent = ref("");
const error = ref(null);

const parsedNarrative = computed(() =>
  narrativeContent.value ? marked(narrativeContent.value) : ""
);

const formatThemeName = (theme) => theme.replace(/_/g, " ");

const loadNarrative = async () => {
  if (!props.theme) return;

  try {
    // Clear previous content while loading
    narrativeContent.value = "";
    error.value = null;

    const filePath = `/narratives/${props.theme}.txt`;

    const response = await fetch(filePath);

    if (!response.ok) {
      throw new Error(`Failed to load narrative for ${props.theme}`);
    }

    const text = await response.text();
    narrativeContent.value = text;
  } catch (err) {
    console.error("Error loading narrative:", err);
    error.value = err.message;
    narrativeContent.value = `*No narrative available for "${formatThemeName(
      props.theme
    )}".*`;
  }
};

// Watch for changes in the theme and reload the narrative
watch(
  () => props.theme,
  () => {
    loadNarrative();
  },
  { immediate: true }
);

onMounted(() => {
  loadNarrative();
});
</script>
