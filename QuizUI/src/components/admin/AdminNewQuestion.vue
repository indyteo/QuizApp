<template>
  <question-editor
      form-title="Nouvelle question"
      :saving="loading"
      @save="createNewQuestion"
      @cancel="$router.push({ name: 'admin' })"
  />
</template>

<script>
import QuestionEditor from "@/components/admin/QuestionEditor.vue";
import quizApiService from "@/services/QuizApiService";

export default {
  name: "AdminNewQuestion",
  components: { QuestionEditor },
  data() {
    return {
      loading: false
    };
  },
  methods: {
    createNewQuestion(question) {
      this.loading = true;
      quizApiService.createQuestion(question).then(res => {
        this.loading = false;
        this.$emit("questions-updated");
        this.$router.push({ name: "question", params: { id: res.data.id } });
      });
    }
  },
  emits: [ "questions-updated" ]
};
</script>
