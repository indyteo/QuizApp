<template>
  <center-layout>
    <div class="text-center text-h6">
      Votre score : {{ score }} / {{ numberOfQuestions }} ({{ numberOfQuestions ? Math.round(100 * score / numberOfQuestions) : "--" }}%)
    </div>
    <div class="text-center text-h6">
      Classement : {{ position }}{{ position === 1 ? "er" : "ème" }}
    </div>
    <div class="text-center mt-4">
      <v-btn :to="{ name: 'home' }">Retour</v-btn>
      <v-btn :to="{ name: 'start' }" class="ml-4" color="primary">Recommencer</v-btn>
    </div>
    <leaderboard @number-of-questions-loaded="n => numberOfQuestions = n" @participations-loaded="p => registeredScores = p" />
  </center-layout>
</template>

<script>
import CenterLayout from "@/components/CenterLayout.vue";
import participationStorageService from "@/services/ParticipationStorageService";
import Leaderboard from "@/components/Leaderboard.vue";

export default {
  name: "ResultPage",
  components: { Leaderboard, CenterLayout },
  data() {
    return {
      score: participationStorageService.getParticipationScore(),
      registeredScores: [],
      numberOfQuestions: 0
    };
  },
  computed: {
    position() {
      return this.registeredScores.filter(p => p.score >= this.score).length;
    }
  }
};
</script>
