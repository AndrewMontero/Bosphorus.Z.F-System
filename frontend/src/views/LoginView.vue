<script setup>
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { useAuth } from "@/stores/auth";

const auth = useAuth();
const router = useRouter();
const route = useRoute();

const email = ref("");
const password = ref("");
const error = ref("");
const enviando = ref(false);

async function entrar() {
  error.value = "";
  enviando.value = true;
  try {
    const usuario = await auth.login(email.value, password.value);
    router.push(route.query.destino || usuario.pantalla_inicio || "/tablero");
  } catch (e) {
    error.value = e.message;
  } finally {
    enviando.value = false;
  }
}
</script>

<template>
  <div class="pantalla-login">
    <form class="tarjeta" @submit.prevent="entrar">
      <div class="marca">Bosphorus <span>ZF</span></div>
      <p class="subtitulo">Grupo Donatella</p>

      <label>
        Correo electrónico
        <input v-model="email" type="email" required autocomplete="username" autofocus />
      </label>

      <label>
        Contraseña
        <input v-model="password" type="password" required autocomplete="current-password" />
      </label>

      <p v-if="error" class="error">{{ error }}</p>

      <button type="submit" :disabled="enviando">
        {{ enviando ? "Entrando…" : "Entrar" }}
      </button>
    </form>
  </div>
</template>
