<template>
  <div class="flex flex-col gap-2 min-w-[250px]">
    <label for="theme-select" class="font-semibold text-primary"
      >Select a Theme:</label
    >
    <select
      id="theme-select"
      v-model="themeValue"
      @change="updateTheme"
      class="p-2.5 border border-secondary rounded text-base bg-white cursor-pointer transition-all focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
    >
      <option v-for="theme in themes" :key="theme" :value="theme">
        {{ formatThemeName(theme) }}
      </option>
    </select>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";

const props = defineProps({
  themes: {
    type: Array,
    required: true,
  },
  selectedTheme: {
    type: String,
    required: true,
  },
});

const emit = defineEmits(["update:selectedTheme"]);

const themeValue = ref(props.selectedTheme);

const updateTheme = () => emit("update:selectedTheme", themeValue.value);
const formatThemeName = (theme) => theme.replace(/_/g, " ");

watch(
  () => props.selectedTheme,
  (newValue) => {
    themeValue.value = newValue;
  }
);
</script>
