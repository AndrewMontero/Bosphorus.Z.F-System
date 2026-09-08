<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";

import AppShell from "@/components/AppShell.vue";
import { useAuth } from "@/stores/auth";

const auth = useAuth();
const route = useRoute();

const conCascaron = computed(() => auth.autenticado && !route.meta.publica);
</script>

<template>
  <AppShell v-if="conCascaron">
    <RouterView />
  </AppShell>
  <RouterView v-else />
</template>
