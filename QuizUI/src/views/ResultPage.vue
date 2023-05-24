<template>
  <center-layout>
    <div class="text-center text-h6">
      Votre score : {{ score }} / {{ numberOfQuestions }} ({{ numberOfQuestions ? Math.round(100 * score / numberOfQuestions) : "--" }}%)
    </div>
    <div class="text-center text-h6">
      Classement : {{ position }}{{ position === 1 ? "er" : "ème" }}
    </div>
    <v-expansion-panels v-if="summary?.length" class="mt-4" style="width: 500px">
      <v-expansion-panel title="Récapitulatif de vos réponses">
        <v-expansion-panel-text>
          <v-timeline v-if="questions" side="end">
            <v-timeline-item
                v-for="(item, index) in summary"
                :key="index"
                :dot-color="item.wasCorrect ? 'success' : 'error'"
                :icon="item.wasCorrect ? 'mdi-check' : 'mdi-close'"
            >
              <template v-slot:opposite>
                {{ index + 1 }} / {{ summary.length }}
              </template>
              <v-alert :type="item.wasCorrect ? 'success' : 'error'" :title="item.wasCorrect ? 'Bonne réponse !' : 'Mauvaise réponse !'" :icon="false">
                <span v-if="!item.wasCorrect">La bonne réponse était :</span>
                {{ questions[index].possibleAnswers[item.correctAnswerPosition - 1].text }}
              </v-alert>
            </v-timeline-item>
          </v-timeline>
          <div v-else class="text-center pa-10">
            <v-progress-circular indeterminate color="primary" size="large" />
          </div>
        </v-expansion-panel-text>
      </v-expansion-panel>
    </v-expansion-panels>
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
import quizApiService from "@/services/QuizApiService";

export default {
  name: "ResultPage",
  components: { Leaderboard, CenterLayout },
  data() {
    return {
      score: participationStorageService.getParticipationScore(),
      summary: participationStorageService.getParticipationSummary(),
      questions: [],
      registeredScores: [],
      numberOfQuestions: 0
    };
  },
  created() {
    quizApiService.listQuestions().then(res => this.questions = res.data);
  },
  computed: {
    position() {
      return this.registeredScores.filter(p => p.score >= this.score).length;
    }
  },
  inheritAttrs: false
};
</script>
