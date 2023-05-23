<template>
  <div v-if="question" class="pa-6 mx-auto" style="max-width: 900px">
    <div class="d-flex justify-space-between align-center pb-8">
      <div class="text-center text-h4">{{ question.title }}</div>
      <div>
        <v-btn variant="text" icon="mdi-pencil" :to="{ name: 'edit', params: { id: question.id } }" class="mr-2" />
        <confirmation-dialog :action="`supprimer la question #${question.id} (${question.title})`" definitive @confirm="deleteQuestion(question.id)">
          <template v-slot="{ props }">
            <v-btn v-bind="props" variant="text" icon="mdi-trash-can-outline" color="error" />
          </template>
        </confirmation-dialog>
      </div>
    </div>
    <div class="text-center pb-4">
      <img v-if="question.image" :src="question.image" :alt="question.title" style="max-height: max(30vh, 250px); max-width: 100%" />
    </div>
    <p class="text-h5 pb-2">{{ question.text }}</p>
    <v-list class="py-0" rounded>
      <template v-for="(answer, index) of question.possibleAnswers" :key="index">
        <v-divider v-if="index !== 0" />
        <v-list-item :title="answer.text" class="my-3">
          <template v-slot:prepend>
            <v-avatar v-if="answer.isCorrect" color="success">
              <v-icon icon="mdi-trophy" />
            </v-avatar>
            <v-avatar v-else>
              <v-icon icon="mdi-close" color="error" />
            </v-avatar>
          </template>
        </v-list-item>
      </template>
    </v-list>
  </div>
  <div v-else class="text-center pa-10">
    <v-progress-circular indeterminate color="primary" size="large" />
  </div>
</template>

<script>
import quizApiService from "@/services/QuizApiService";
import ConfirmationDialog from "@/components/ConfirmationDialog.vue";

export default {
  name: "AdminQuestion",
  components: { ConfirmationDialog },
  data() {
    return {
      question: undefined,
      deleting: false
    };
  },
  created() {
    this.fetchQuestion()
  },
  methods: {
    fetchQuestion() {
      quizApiService.getQuestionById(this.$route.params.id)
          .then(res => this.question = res.data)
          .catch(res => {
            if (res.data.status === 404)
              this.$router.push({ name: "questions" });
          });
    },
    deleteQuestion(id) {
      this.deleting = true;
      quizApiService.deleteQuestion(id).then(() => {
        this.deleting = false;
        this.$emit("questions-updated");
        this.$router.push({ name: "questions" });
      });
    }
  },
  watch: {
    $route(to) {
      if (to.name === "question")
        this.fetchQuestion();
    }
  },
  emits: [ "questions-updated" ]
};
</script>
