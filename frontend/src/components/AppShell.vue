<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";

import { MENU } from "@/menu";
import { useAuth } from "@/stores/auth";

const auth = useAuth();
const router = useRouter();

// El menu se deriva de los permisos: un dominio sin ninguna entrada
// permitida simplemente no aparece.
const menuVisible = computed(() =>
  MENU.map((grupo) => ({
    ...grupo,
    entradas: grupo.entradas.filter((entrada) => auth.puede(entrada.permiso)),
  })).filter((grupo) => grupo.entradas.length > 0),
);

const iniciales = computed(() =>
  (auth.usuario?.nombre_completo || "")
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((parte) => parte[0])
    .join("")
    .toUpperCase(),
);

async function salir() {
  await auth.logout();
  router.push({ name: "login" });
}
</script>

<template>
  <div class="cascaron">
    <aside class="barra">
      <div class="marca">Bosphorus <span>ZF</span></div>

      <nav>
        <div v-for="grupo in menuVisible" :key="grupo.dominio" class="grupo">
          <p class="grupo-titulo">{{ grupo.dominio }}</p>
          <RouterLink
            v-for="entrada in grupo.entradas"
            :key="entrada.ruta"
            :to="entrada.ruta"
            class="enlace"
          >
            {{ entrada.texto }}
          </RouterLink>
        </div>
      </nav>
    </aside>

    <div class="columna">
      <header class="encabezado">
        <span class="tenant">DOLCESIA</span>
        <div class="usuario">
          <span class="avatar">{{ iniciales }}</span>
          <div class="datos">
            <strong>{{ auth.usuario?.nombre_completo }}</strong>
            <small>{{ auth.usuario?.permisos.length }} permisos</small>
          </div>
          <button class="salir" type="button" @click="salir">Salir</button>
        </div>
      </header>

      <main class="contenido">
        <slot />
      </main>
    </div>
  </div>
</template>
