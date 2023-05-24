<template>
  <center-layout>
    <v-form @submit="startQuiz">
      <v-text-field label="Votre nom" v-model="username" />
      <div class="text-center">
        <v-btn type="submit" :disabled="!username" size="x-large" rounded="xl">Démarrer le quiz</v-btn>
      </div>
    </v-form>
  </center-layout>
</template>

<script>
import CenterLayout from "@/components/CenterLayout.vue";
import participationStorageService from "@/services/ParticipationStorageService";

export default {
  name: "NewQuizPage",
  components: { CenterLayout },
  data() {
    return {
      username: participationStorageService.getPlayerName() ?? ""
    };
  },
  methods: {
    startQuiz(e) {
      e.preventDefault();
      participationStorageService.savePlayerName(this.username);
      this.$router.push({ name: "quiz" });
    }
  },
  inheritAttrs: false
};
</script>
