<template>
  <div class="pa-6 mx-auto" style="max-width: 900px">
    <div class="text-center text-h4 pb-4">{{ question.title }}</div>
    <div class="text-center pb-3">
      <img v-if="question.image" :src="question.image" :alt="question.title" style="max-height: max(40vh, 300px); max-width: 100%" />
    </div>
    <p class="text-h5 pb-1">{{ question.text }}</p>
    <v-btn
        v-for="(answer, index) of question.possibleAnswers"
        :key="index"
        :text="answer.text"
        variant="outlined"
        color="primary"
        size="large"
        block
        class="mt-4 answer-btn"
        @click="$emit('answer-selected', index + 1)"
    />
  </div>
</template>

<script>
export default {
  name: "QuestionDisplay",
  props: {
    question: { type: Object }
  },
  emits: [ "answer-selected" ]
};
</script>

<style scoped>
:deep(.answer-btn) {
  min-height: calc(var(--v-btn-height) - 26px);
  height: unset !important;
  padding-top: 13px;
  padding-bottom: 13px;
}
:deep(.answer-btn .v-btn__content) {
  white-space: normal;
}
</style>
