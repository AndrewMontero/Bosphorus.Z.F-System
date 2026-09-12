<script setup>
import { useAuth } from "@/stores/auth";

const auth = useAuth();
</script>

<template>
  <div>
    <h1>Sin permiso</h1>
    <p class="nota">
      Tu usuario no tiene permiso para entrar a esa pantalla. Si creés que sí
      debería, pedile a un administrador que revise tus roles.
    </p>
    <RouterLink :to="auth.pantallaInicio">Volver a lo tuyo</RouterLink>
  </div>
</template>
