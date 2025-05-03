<template>
  <div class="max-w-7xl mx-auto p-8 text-text">
    <header class="text-center mb-8">
      <h1 class="text-4xl font-serif text-primary mb-2">
        Poetry Themes Visualization
      </h1>
      <h2 class="text-xl font-normal text-text opacity-80">
        Explore how poetic themes evolved over time (1700-1900) in France and
        Germany
      </h2>
    </header>

    <main class="bg-white rounded-lg shadow-md p-8 mb-8">
      <div
        class="flex flex-wrap gap-8 justify-between mb-8 md:flex-row sm:flex-col"
      >
        <ThemeSelector
          :themes="themes"
          :selectedTheme="selectedTheme"
          @update:selectedTheme="selectedTheme = $event"
        />

        <YearSlider
          :minYear="minYear"
          :maxYear="maxYear"
          :selectedYear="selectedYear"
          @update:selectedYear="selectedYear = $event"
        />
      </div>

      <ThemeVisualization
        :theme="selectedTheme"
        :year="selectedYear"
        :loading="loading"
      />

      <SummarySection :theme="selectedTheme" :year="selectedYear" />
    </main>

    <footer class="text-center text-sm text-text opacity-70">
      <p>Data sources: DLK, Oupoco, Gutenberg, Poetry Foundation</p>
    </footer>
  </div>
</template>

<script setup>
import { ref } from "vue";
import ThemeSelector from "./components/ThemeSelector.vue";
import YearSlider from "./components/YearSlider.vue";
import ThemeVisualization from "./components/ThemeVisualization.vue";
import SummarySection from "./components/SummarySection.vue";

const themes = [
  "Activities_and_Work",
  "Arts_and_Culture",
  "Body_and_Health",
  "Complexity_and_Paradox",
  "Death_and_Loss",
  "Fate_and_Destiny",
  "Life_and_Living",
  "Mind_and_Emotions",
  "Morality_and_Ethics",
  "Nature_and_Environment",
  "Power_and_Freedom",
  "Religion_and_Spirituality",
  "Society_and_Politics",
  "Time_and_Temporality",
  "War_and_Conflict",
];

const selectedTheme = ref("War_and_Conflict");
const minYear = ref(1700);
const maxYear = ref(1899);
const selectedYear = ref(1800);
const loading = ref(false);
</script>
