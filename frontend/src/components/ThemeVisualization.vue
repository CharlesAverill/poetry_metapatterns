<template>
  <div class="my-8">
    <div
      class="flex justify-center items-center bg-white border border-secondary rounded h-[800px] relative overflow-hidden"
    >
      <div
        class="absolute inset-0 flex justify-center items-center overflow-hidden"
      >
        <div
          v-if="!error"
          class="w-full h-full flex justify-center items-center"
        >
          <img
            ref="currentImage"
            :src="imagePath"
            alt="Theme visualization"
            @load="imageLoaded"
            class="max-w-[95%] max-h-[95%] object-contain block"
            style="
              transform: none !important;
              transition: none !important;
              position: static !important;
            "
          />
        </div>

        <div
          v-if="loading"
          class="flex justify-center items-center absolute inset-0 bg-white/80"
        >
          <div
            class="w-10 h-10 rounded-full border-4 border-primary/20 border-t-primary animate-spin"
          ></div>
        </div>
      </div>

      <p v-if="error" class="text-accent text-center p-4">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUpdated } from "vue";

const props = defineProps({
  theme: {
    type: String,
    required: true,
  },
  year: {
    type: Number,
    required: true,
  },
  loading: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["update:loading"]);

const error = ref(null);
const imageIsLoaded = ref(false);
const isLoading = ref(false);
const currentImage = ref(null);

const imagePath = computed(
  () => `/images/frames/${props.theme}/frame_${props.year}.png`
);

const imageLoaded = () => {
  error.value = null;
  imageIsLoaded.value = true;
  isLoading.value = false;
  emit("update:loading", false);
};

const checkImageExists = () => {
  isLoading.value = true;
  emit("update:loading", true);

  error.value = null;

  const img = new Image();
  img.onload = () => {
    isLoading.value = false;
    emit("update:loading", false);
  };
  img.onerror = () => {
    error.value = `No visualization available for ${props.theme.replace(
      /_/g,
      " "
    )} in ${props.year}`;
    isLoading.value = false;
    emit("update:loading", false);
  };
  img.src = imagePath.value;
};

watch(
  () => props.theme,
  () => {
    checkImageExists();
  }
);

watch(
  () => props.year,
  () => {
    checkImageExists();
  }
);

onMounted(() => {
  checkImageExists();
});

onUpdated(() => {
  if (currentImage.value) {
    currentImage.value.focus();
  }
});
</script>

<style scoped>
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
