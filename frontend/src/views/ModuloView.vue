<script setup>
import { useRoute } from "vue-router";

const route = useRoute();
</script>

<template>
  <div>
    <h1>{{ route.meta.titulo }}</h1>
    <p class="nota">
      Esta pantalla todavía no está construida. Llegaste hasta acá porque tenés el
      permiso <code>{{ route.meta.permiso }}</code>, así que el login, los roles y
      el menú ya funcionan de punta a punta.
    </p>
  </div>
</template>
