<template>
  <v-timeline v-if="questions" side="end">
    <v-hover v-for="(question, i) in orderedQuestions" :key="question.id">
      <template v-slot:default="{ isHovering, props }">
        <v-timeline-item
            v-bind="props"
            :dot-color="shouldHighlight(question) ? 'primary' : isHovering ? 'secondary' : undefined"
            :size="shouldHighlight(question) ? undefined : 'x-small'"
            @click="questionClick(question, i + 1)"
            :style="shouldHighlight(question) ? undefined : 'cursor: pointer'"
        >
          <template v-slot:opposite>
            <div :class="'py-2 text-right' + (shouldHighlight(question) ? ' text-h6 text-primary' : (isHovering ? ' text-secondary' : ''))">
              {{ question.title }}
            </div>
          </template>
        </v-timeline-item>
      </template>
    </v-hover>
  </v-timeline>
  <div v-else class="text-center pa-10">
    <v-progress-circular indeterminate color="primary" size="large" />
  </div>
</template>

<script>
import quizApiService from "@/services/QuizApiService";

export default {
  name: "AdminQuestionPositionViewer",
  props: {
    loadedQuestions: { type: Array },
    position: { type: Number },
    question: { type: Object }
  },
  data() {
    return {
      questions: this.loadedQuestions
    };
  },
  created() {
    if (!this.questions)
      quizApiService.listQuestions().then(res => this.questions = res.data);
  },
  methods: {
    questionClick(question, n) {
      if (question.id && question.position !== this.position)
        this.$emit("question-click", question.id, n);
    },
    shouldHighlight(question) {
      return this.question ? question.id === 0 : question.position === this.position;
    }
  },
  computed: {
    orderedQuestions() {
      if (this.question)
        return this.questions.filter(q => q.id !== this.question.id)
            .concat({ title: this.question.title, position: this.position + (this.position >= this.question.position ? 0.5 : -0.5), id: 0 })
            .sort((a, b) => a.position - b.position);
      return this.questions;
    }
  },
  emits: [ "question-click" ]
};
</script>
