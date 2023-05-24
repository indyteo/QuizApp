<template>
  <center-layout>
    <settings-layout name="Lister les questions" description="Accéder à la liste des questions existantes">
      <v-btn variant="outlined" text="Questions" prepend-icon="mdi-timeline-question-outline" rounded="xl" color="primary" :to="{ name: 'questions' }" />
    </settings-layout>
    <settings-layout name="Créer une question" description="Ajouter une nouvelle question au quiz">
      <v-btn variant="outlined" text="Ajout" prepend-icon="mdi-plus-circle-outline" rounded="xl" color="success" :to="{ name: 'add' }" />
    </settings-layout>
    <settings-layout name="Supprimer les données" description="Supprimer les questions et participations du quiz">
      <v-btn variant="outlined" text="Suppression" prepend-icon="mdi-delete-empty-outline" rounded="xl" color="error" :to="{ name: 'delete' }" />
    </settings-layout>
  </center-layout>
</template>

<script>
import CenterLayout from "@/components/CenterLayout.vue";
import SettingsLayout from "@/components/SettingsLayout.vue";

export default {
  name: "AdminHome",
  components: { SettingsLayout, CenterLayout },
  inheritAttrs: false
};
</script>
