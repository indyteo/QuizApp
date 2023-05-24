<template>
  <v-progress-linear :model-value="currentQuestion?.position ?? 0" :max="numberOfQuestions" color="primary" height="25">
    Question {{ currentQuestion?.position ?? 0 }} / {{ numberOfQuestions }}
  </v-progress-linear>
  <question-display v-if="currentQuestion" :question="currentQuestion" @answer-selected="answer" />
  <div v-else class="text-center pa-10">
    <v-progress-circular indeterminate color="primary" size="large" />
  </div>
</template>

<script>
import participationStorageService from "@/services/ParticipationStorageService";
import QuestionDisplay from "@/components/QuestionDisplay.vue";
import quizApiService from "@/services/QuizApiService";

export default {
  name: "QuizPage",
  components: { QuestionDisplay },
  data() {
    return {
      currentQuestion: undefined,
      numberOfQuestions: 0,
      answers: []
    }
  },
  created() {
    if (!participationStorageService.getPlayerName()) {
      this.$router.push({ name: "start" });
      return;
    }
    quizApiService.getQuizInfo().then(res => this.numberOfQuestions = res.data.size);
    this.fetchQuestion(1);
  },
  methods: {
    answer(n) {
      this.answers.push(n);
      if (this.currentQuestion.position < this.numberOfQuestions)
        this.fetchQuestion(this.currentQuestion.position + 1);
      else {
        quizApiService.participate(participationStorageService.getPlayerName(), this.answers).then(res => {
          participationStorageService.saveParticipationScore(res.data.score);
          participationStorageService.saveParticipationSummary(res.data.answersSummaries);
          this.$router.push({ name: "score" });
        });
      }
    },
    fetchQuestion(position) {
      quizApiService.getQuestion(position).then(res => this.currentQuestion = res.data);
    }
  },
  inheritAttrs: false
};
</script>
