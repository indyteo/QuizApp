<template>
  <v-form
      @submit="$emit('save', { title, text, position, image, possibleAnswers })"
      @submit.prevent
      class="mx-auto pa-8"
      style="max-width: 750px"
  >
    <p class="text-h4 pb-6">{{ formTitle }}</p>
    <v-text-field label="Titre" v-model="title" />
    <v-textarea label="Texte de la question" v-model="text" rows="3" />
    <v-text-field type="number" label="Position" v-model="position" />
    <image-upload @file-change="img => this.image = img" />
    <div v-if="image" class="text-center mt-2">
      <img :src="image" alt="Image de la question" style="max-height: max(40vh, 300px); max-width: 100%" />
    </div>
    <v-list class="mt-4" rounded>
      <div class="d-flex justify-space-between align-center">
        <v-list-subheader>Réponses</v-list-subheader>
        <v-btn class="mr-2" variant="text" text="Ajouter" @click="possibleAnswers.push({ text: '', isCorrect: possibleAnswers.length === 0 })" />
      </div>
      <v-radio-group :class="possibleAnswers.length ? 'my-3' : ''" :model-value="correctAnswerId" @update:model-value="i => selectCorrectAnswer(i)" hide-details>
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
      <v-btn type="reset" text="Annuler" color="error" @click="$emit('cancel')" />
    </div>
  </v-form>
</template>

<script>
import quizApiService from "@/services/QuizApiService";
import ImageUpload from "@/components/admin/ImageUpload.vue";

export default {
  name: "QuestionEditor",
  components: { ImageUpload },
  props: {
    question: { type: Object },
    formTitle: { type: String },
    saving: { type: Boolean }
  },
  data() {
    return {
      title: this.question?.title ?? "",
      text: this.question?.text ?? "",
      position: this.question?.position ?? 0,
      image: this.question?.image ?? "",
      possibleAnswers: this.deepCopyPossibleAnswers(this.question?.possibleAnswers)
    };
  },
  created() {
    if (!this.question)
      quizApiService.getQuizInfo().then(res => this.position = res.data.size + 1);
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
    }
  },
  computed: {
    correctAnswerId() {
      for (let i = 0; i < this.possibleAnswers.length; i++)
        if (this.possibleAnswers[i].isCorrect)
          return i;
      return 0;
    },
    isIncorrect() {
      return this.title.length === 0 || this.text.length === 0 || this.position < 1 || this.possibleAnswers.length === 0;
    }
  },
  emits: [ "save", "cancel" ]
};
</script>
