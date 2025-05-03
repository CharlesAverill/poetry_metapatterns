<template>
  <div class="flex flex-col gap-2 flex-grow min-w-[250px]">
    <label for="year-range" class="font-semibold text-primary"
      >Year: {{ selectedYear }}</label
    >
    <div class="flex flex-col">
      <input
        type="range"
        id="year-range"
        :min="minYear"
        :max="maxYear"
        v-model.number="yearValue"
        @input="updateYear"
        class="w-full h-1.5 bg-secondary rounded-md outline-none appearance-none cursor-pointer slider-thumb"
      />
      <div class="flex justify-between mt-2 text-sm text-text opacity-70">
        <span>{{ minYear }}</span>
        <span>{{ maxYear }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";

const props = defineProps({
  minYear: {
    type: Number,
    required: true,
  },
  maxYear: {
    type: Number,
    required: true,
  },
  selectedYear: {
    type: Number,
    required: true,
  },
});

const emit = defineEmits(["update:selectedYear"]);

const yearValue = ref(props.selectedYear);

watch(
  () => props.selectedYear,
  (newValue) => {
    yearValue.value = newValue;
  }
);

const updateYear = () => emit("update:selectedYear", yearValue.value);
</script>

<style scoped>
/* Custom Slider */
.slider-thumb::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: theme("colors.primary");
  cursor: pointer;
  transition: background 0.2s;
}

.slider-thumb::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: theme("colors.primary");
  cursor: pointer;
  transition: background 0.2s;
  border: none;
}

.slider-thumb::-webkit-slider-thumb:hover {
  background: theme("colors.accent");
}

.slider-thumb::-moz-range-thumb:hover {
  background: theme("colors.accent");
}
</style>
