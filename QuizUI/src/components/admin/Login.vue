<template>
  <center-layout>
    <v-alert v-if="error" class="mb-4" type="error" :title="error" closable @click:close="error = undefined" />
    <v-form @submit="login">
      <v-text-field label="Mot de passe" type="password" v-model="password" :error="error" />
      <div class="text-center">
        <v-btn type="submit" :disabled="!password">Connexion</v-btn>
      </div>
    </v-form>
  </center-layout>
</template>

<script>
import CenterLayout from "@/components/CenterLayout.vue";
import authenticationService from "@/services/AuthenticationService";

export default {
  name: "Login",
  components: { CenterLayout },
  data() {
    return {
      password: "",
      error: undefined
    };
  },
  methods: {
    login(e) {
      e.preventDefault();
      if (this.password) {
        authenticationService.login(this.password).then(success => {
          if (success) {
            const returnTo = this.$route.params.returnTo;
            this.$router.push(returnTo ?? { name: "admin" });
          } else {
            this.password = "";
            this.error = "Mot de passe invalide";
          }
        });
      } else
        this.error = "Vous devez spécifier le mot de passe";
    }
  },
  inheritAttrs: false
};
</script>
