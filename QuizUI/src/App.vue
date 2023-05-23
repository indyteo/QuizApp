<template>
  <v-theme-provider :theme="preferedColorScheme" with-background>
    <v-layout full-height style="min-height: 100vh">
      <v-app-bar title="QuizApp ESIEE">
        <v-btn :to="{ name: 'home' }" class="mr-2">Accueil</v-btn>
        <v-btn :to="{ name: 'admin' }">Admin</v-btn>
      </v-app-bar>
      <v-main>
        <router-view />
      </v-main>
    </v-layout>
  </v-theme-provider>
</template>

<script>
export default {
  name: "App",
  computed: {
    preferedColorScheme() {
      return matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    }
  }
};
</script>
