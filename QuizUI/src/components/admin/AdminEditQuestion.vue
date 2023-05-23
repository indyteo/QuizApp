<template>
  <question-editor
      v-if="question"
      :question="question"
      :form-title="`Question #${question.id} (${question.title})`"
      :saving="loading"
      @save="updateQuestion"
      @cancel="$router.push({ name: 'question', params: { id: question.id } })"
  />
  <div v-else class="text-center pa-10">
    <v-progress-circular indeterminate color="primary" size="large" />
  </div>
</template>

<script>
import quizApiService from "@/services/QuizApiService";
import QuestionEditor from "@/components/admin/QuestionEditor.vue";

export default {
  name: "AdminEditQuestion",
  components: { QuestionEditor },
  data() {
    return {
      question: undefined,
      loading: false
    };
  },
  created() {
    quizApiService.getQuestionById(this.$route.params.id)
        .then(res => this.question = res.data)
        .catch(res => {
          if (res.data.status === 404)
            this.$router.push({ name: "questions" });
        });
  },
  methods: {
    updateQuestion(question) {
      this.loading = true;
      quizApiService.updateQuestion(this.question.id, question).then(() => {
        this.loading = false;
        this.$emit("questions-updated");
        this.$router.push({ name: "question", params: { id: this.question.id } });
      });
    }
  },
  emits: [ "questions-updated" ]
};
</script>
