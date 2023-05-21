<template>
  <div>
    <h1>QuizApp ESIEE</h1>

    <div v-for="scoreEntry in registeredScores" v-bind:key="scoreEntry.playerName">
      {{ scoreEntry.playerName }} - {{ scoreEntry.score }}
    </div>
    <v-list lines="one">
      <v-list-item
        v-for="scoreEntry in registeredScores"
        :key="scoreEntry.playerName"
        :title="scoreEntry.playerName"
        :subtitle= "'score : '+ scoreEntry.score"
      ></v-list-item>
    </v-list>
  </div>
  <router-link to="/start-new-quiz-page">Démarrer le quiz !</router-link>
  <router-link to="/new-quiz">New Quiz</router-link>
</template>

<script>
import quizApiService from "@/services/QuizApiService";

export default {
  name: "HomePage",
  data() {
    return {
      registeredScores: [],
    };
  },
  async created() {
    console.log("Composant Home page 'created'");
    try {
      const response = await quizApiService.getQuizInfo(); // Appel du service pour obtenir les scores
      this.registeredScores = response.data.scores; // Stockage de la valeur de la réponse dans registeredScores
    } catch (error) {
      console.error("Erreur lors de la récupération des scores :", error);
    }
  },

};
</script>
