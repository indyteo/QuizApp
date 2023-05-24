<template>
  <v-navigation-drawer permanent>
    <v-list nav density="compact">
      <v-list-item v-if="$route.name === 'login'" title="Connexion" :to="{ name: 'login' }" prepend-icon="mdi-login" rounded="xl" disabled />
      <AdminNavigationLinks v-else ref="navbar" />
    </v-list>
  </v-navigation-drawer>

  <router-view @questions-updated="$refs.navbar.refreshQuestionsList()" />
</template>

<script>
import AdminNavigationLinks from "@/components/admin/AdminNavigationLinks.vue";

export default {
  name: "Admin",
  components: { AdminNavigationLinks },
  inheritAttrs: false
};
</script>
