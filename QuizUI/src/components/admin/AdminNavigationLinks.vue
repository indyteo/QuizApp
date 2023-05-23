<template>
  <v-list-group value="Questions">
    <template v-slot:activator="{ props, isOpen }">
      <v-list-item
          class="py-0 pr-0"
          title="Questions"
          :to="{ name: 'questions' }"
          @click="navigateToQuestionsList"
          @click.prevent
          prepend-icon="mdi-timeline-question-outline"
          rounded="xl"
          :active="$route.name === 'questions' ? true : undefined"
      >
        <template v-slot:append>
          <v-btn
              v-bind="props"
              size="small"
              variant="text"
              :icon="isOpen ? 'mdi-chevron-down' : 'mdi-chevron-left'"
              @click.prevent
              @click.stop
          />
        </template>
      </v-list-item>
    </template>
    <v-list-item
        v-for="question in questions"
        :key="question.id"
        :title="question.title"
        rounded="xl"
        :to="{ name: 'question', params: { id: question.id } }"
    />
  </v-list-group>
  <v-list-item title="Ajout" :to="{ name: 'add' }" prepend-icon="mdi-plus-circle-outline" rounded="xl" color="success" />
  <v-list-item title="Suppression" :to="{ name: 'delete' }" prepend-icon="mdi-delete-empty-outline" rounded="xl" color="error" />
  <v-divider />
  <v-list-item class="mt-1" title="Logout" @click="logout" prepend-icon="mdi-logout" rounded="xl" />
</template>

<script>
import quizApiService from "@/services/QuizApiService";
import authenticationService from "@/services/AuthenticationService";

export default {
  name: "AdminNavigationLinks",
  data() {
    return {
      questions: undefined
    };
  },
  created() {
    this.refreshQuestionsList();
  },
  methods: {
    refreshQuestionsList() {
      quizApiService.listQuestions().then(res => this.questions = res.data);
    },
    logout() {
      authenticationService.logout();
      this.$router.push({ name: "login" });
    },
    navigateToQuestionsList() {
      this.$router.push({ name: "questions" });
    }
  }
};
</script>
