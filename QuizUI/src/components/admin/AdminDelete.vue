<template>
  <center-layout>
    <v-alert v-if="deletedParticipations" title="Toutes les participations ont été supprimées" type="success" closable />
    <v-alert v-if="deletedQuestions" title="Toutes les questions ont été supprimées" type="success" closable />
    <settings-layout name="Participations" description="Réinitialiser le classement">
      <confirmation-dialog action="supprimer toutes les participations" definitive @confirm="deleteParticipations">
        <template v-slot="{ props }">
          <v-btn v-bind="props" variant="outlined" text="Réinitialiser" prepend-icon="mdi-trophy-broken" color="warning" rounded="xl" />
        </template>
      </confirmation-dialog>
    </settings-layout>
    <settings-layout name="Questions" description="Supprimer définitivement toutes les questions">
      <confirmation-dialog action="supprimer toutes les questions" definitive @confirm="deleteQuestions">
        <template v-slot="{ props }">
          <v-btn v-bind="props" text="Supprimer" prepend-icon="mdi-timeline-remove-outline" color="error" rounded="xl" />
        </template>
      </confirmation-dialog>
    </settings-layout>
  </center-layout>
</template>

<script>
import CenterLayout from "@/components/CenterLayout.vue";
import SettingsLayout from "@/components/SettingsLayout.vue";
import ConfirmationDialog from "@/components/ConfirmationDialog.vue";
import quizApiService from "@/services/QuizApiService";

export default {
  name: "Delete",
  components: { ConfirmationDialog, SettingsLayout, CenterLayout },
  data() {
    return {
      deletedParticipations: false,
      deletedQuestions: false
    };
  },
  methods: {
    deleteParticipations() {
      quizApiService.deleteAllParticipations().then(() => this.deletedParticipations = true);
    },
    deleteQuestions() {
      quizApiService.deleteAllQuestions().then(() => {
        this.deletedQuestions = true;
        this.$emit("questions-updated");
      });
    }
  },
  emits: [ "questions-updated" ]
};
</script>
