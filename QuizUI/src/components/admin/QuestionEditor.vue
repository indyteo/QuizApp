<template>
  <div class="d-flex fill-height">
    <v-spacer />
    <div class="pa-8 mx-auto" style="width: min(100%, 750px)">
      <v-form @submit="$emit('save', { title, text, position, image, possibleAnswers })" @submit.prevent>
        <p class="text-h4 pb-6">{{ formTitle }}</p>
        <v-text-field label="Titre" v-model="title" />
        <v-textarea label="Texte de la question" v-model="text" rows="3" />
        <v-text-field type="number" label="Position" v-model="position_" :min="1" :max="maximumPosition" class="position-input">
          <template v-slot:prepend>
            <v-btn
                icon="mdi-numeric-negative-1"
                size="x-large"
                density="comfortable"
                @click="changePosition(position - 1)"
                :disabled="position === 1 || Number.isNaN(position)"
            />
          </template>
          <template v-slot:append>
            <v-btn
                icon="mdi-numeric-positive-1"
                size="x-large"
                density="comfortable"
                @click="changePosition(position + 1)"
                :disabled="position === maximumPosition || Number.isNaN(position)"
            />
          </template>
        </v-text-field>
        <image-upload @file-change="img => image = img" />
        <div v-if="image" class="text-center mt-2">
          <img :src="image" alt="Image de la question" style="max-height: max(40vh, 300px); max-width: 100%" />
        </div>
        <v-list class="mt-4" rounded>
          <div class="d-flex justify-space-between align-center">
            <v-list-subheader>Réponses</v-list-subheader>
            <v-btn class="mr-2" variant="text" text="Ajouter" @click="possibleAnswers.push({ text: '', isCorrect: possibleAnswers.length === 0 })" />
          </div>
          <v-radio-group :class="possibleAnswers?.length ? 'my-3' : ''" :model-value="correctAnswerId" @update:model-value="i => selectCorrectAnswer(i)" hide-details>
            <v-list-item v-for="(answer, i) in possibleAnswers" :key="i">
              <template v-slot:prepend>
                <v-radio :value="i" />
              </template>
              <v-text-field class="mx-2" :model-value="answer.text" @update:model-value="txt => answer.text = txt" hide-details />
              <template v-slot:append>
                <v-btn icon="mdi-close" variant="text" @click="deleteAnswer(i)" />
              </template>
            </v-list-item>
          </v-radio-group>
        </v-list>
        <div class="text-center pt-6">
          <v-btn class="mr-4" type="submit" text="Sauvegarder" color="success" :disabled="isIncorrect || saving" :loading="saving" />
          <confirmation-dialog action="abandonner vos modifications" :disabled="!hasPendingChanges" @confirm="$emit('cancel')">
            <template v-slot="{ props }">
              <v-btn v-bind="props" text="Annuler" color="error" />
            </template>
          </confirmation-dialog>
        </div>
      </v-form>
    </div>
    <v-spacer />
    <div class="align-self-stretch">
      <admin-question-position-viewer
          :position="position"
          :question="question ? question.position !== position ? question : undefined : { title: title || 'Titre de la question' }"
          @question-click="(id, n) => changePosition(n)"
      />
    </div>
  </div>
</template>

<script>
import quizApiService from "@/services/QuizApiService";
import ImageUpload from "@/components/admin/ImageUpload.vue";
import ConfirmationDialog from "@/components/ConfirmationDialog.vue";
import AdminQuestionPositionViewer from "@/components/admin/AdminQuestionPositionViewer.vue";

export default {
  name: "QuestionEditor",
  components: { AdminQuestionPositionViewer, ConfirmationDialog, ImageUpload },
  props: {
    question: { type: Object },
    formTitle: { type: String },
    saving: { type: Boolean }
  },
  data() {
    return {
      maximumPosition: 0,
      title: this.question?.title ?? "",
      text: this.question?.text ?? "",
      position_: this.question?.position ?? "0",
      image: this.question?.image ?? "",
      possibleAnswers: this.deepCopyPossibleAnswers(this.question?.possibleAnswers)
    };
  },
  created() {
    quizApiService.getQuizInfo().then(res => {
      this.maximumPosition = res.data.size + (this.question ? 0 : 1);
      if (!this.question)
        this.position_ = this.maximumPosition.toString();
    });
  },
  methods: {
    selectCorrectAnswer(n) {
      this.possibleAnswers.forEach((answer, i) => answer.isCorrect = i === n);
    },
    deleteAnswer(n) {
      const deleted = this.possibleAnswers.splice(n, 1);
      if (deleted && deleted[0].isCorrect)
        this.possibleAnswers[0].isCorrect = true;
    },
    deepCopyPossibleAnswers(answers) {
      return answers ? answers.map(a => ({ ...a })) : [];
    },
    isPossibleAnswersDifferent(answers) {
      if (answers.length !== this.possibleAnswers.length)
        return true;
      for (let i = 0; i < answers.length; i++)
        if (answers[i].text !== this.possibleAnswers[i].text || answers[i].isCorrect !== this.possibleAnswers[i].isCorrect)
          return true;
      return false;
    },
    changePosition(position) {
      this.position_ = Math.max(1, Math.min(position, this.maximumPosition)).toString();
    }
  },
  computed: {
    position() {
      return parseInt(this.position_);
    },
    correctAnswerId() {
      for (let i = 0; i < this.possibleAnswers?.length; i++)
        if (this.possibleAnswers[i].isCorrect)
          return i;
      return 0;
    },
    isIncorrect() {
      return this.title?.length === 0 || this.text?.length === 0 || Number.isNaN(this.position) || this.position < 1 || this.possibleAnswers?.length === 0;
    },
    hasPendingChanges() {
      if (this.question)
        return this.title !== this.question.title
            || this.text !== this.question.text
            || this.position !== this.question.position
            || this.image !== this.question.image
            || this.isPossibleAnswersDifferent(this.question.possibleAnswers);
      return this.title || this.text || this.image || this.possibleAnswers?.length;
    }
  },
  emits: [ "save", "cancel" ]
};
</script>

<style scoped>
:deep(.position-input .v-field__input) {
  -moz-appearance: textfield;
}
:deep(.position-input .v-field__input::-webkit-outer-spin-button),
:deep(.position-input .v-field__input::-webkit-inner-spin-button) {
  -webkit-appearance: none;
  margin: 0;
}
</style>
