<template>
  <div class="d-flex flex-wrap justify-center pa-8" style="gap: 24px">
    <v-sheet v-for="question in questions" :key="question.id" class="d-flex flex-column question" rounded :elevation="1">
      <v-card width="400" :to="{ name: 'question', params: { id: question.id } }" flat class="flex-1-0" :loading="deleting === question.id">
        <v-img height="200" :src="question.image" cover class="bg-grey-darken-2">
          <template v-slot:placeholder>
            <div class="d-flex align-center justify-center fill-height">
              <v-progress-circular v-if="question.image" color="grey-lighten-3" indeterminate />
              <v-icon v-else icon="mdi-image-off-outline" color="grey-lighten-3" size="64" />
            </div>
          </template>
        </v-img>
        <v-card-title class="pt-4">{{ question.title }}</v-card-title>
        <v-card-text>{{ question.text }}</v-card-text>
      </v-card>
      <v-divider />
      <v-card-actions>
        <v-btn text="Éditer" color="primary" :to="{ name: 'edit', params: { id: question.id } }" />
        <confirmation-dialog :action="`supprimer la question #${question.id} (${question.title})`" definitive @confirm="deleteQuestion(question.id)">
          <template v-slot="{ props }">
            <v-btn v-bind="props" text="Supprimer" color="error" />
          </template>
        </confirmation-dialog>
      </v-card-actions>
    </v-sheet>
  </div>
</template>

<script>
import quizApiService from "@/services/QuizApiService";
import ConfirmationDialog from "@/components/ConfirmationDialog.vue";

export default {
  name: "AdminQuestionsList",
  components: { ConfirmationDialog },
  data() {
    return {
      questions: undefined,
      deleting: undefined
    };
  },
  created() {
    quizApiService.listQuestions().then(res => this.questions = res.data);
  },
  methods: {
    deleteQuestion(id) {
      this.deleting = id;
      quizApiService.deleteQuestion(id).then(() => {
        this.questions = this.questions.filter(question => question.id !== id);
        this.$emit("questions-updated");
        this.deleting = undefined;
      });
    }
  },
  emits: [ "questions-updated" ]
};
</script>

<style scoped>
:deep(.question .v-img__img) {
  transition: transform 0.5s;
}
:deep(.question:hover .v-img__img) {
  transform: scale(1.07);
}
:deep(.question .v-card) {
  border-bottom-left-radius: 0;
  border-bottom-right-radius: 0;
}
</style>
