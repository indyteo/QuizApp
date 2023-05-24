<template>
  <center-layout>
    <settings-layout name="Thème de l'application" :description="'Préférence du navigateur : ' + preferedColorScheme">
      <v-btn-toggle v-model="theme" variant="elevated" mandatory rounded="xl" color="primary">
        <v-btn append-icon="mdi-lightbulb-on-outline" text="Clair" value="light" />
        <v-btn append-icon="mdi-theme-light-dark" text="Synchronisé" value="sync" />
        <v-btn append-icon="mdi-weather-night" text="Sombre" value="dark" />
      </v-btn-toggle>
    </settings-layout>
  </center-layout>
</template>

<script>
import CenterLayout from "@/components/CenterLayout.vue";
import SettingsLayout from "@/components/SettingsLayout.vue";
import settingsStorageService from "@/services/SettingsStorageService";

export default {
  name: "ResultPage",
  components: { SettingsLayout, CenterLayout },
  data() {
    return {
      theme: settingsStorageService.getTheme() ?? "sync"
    };
  },
  computed: {
    preferedColorScheme() {
      return matchMedia("(prefers-color-scheme: dark)").matches ? "Sombre" : "Clair";
    }
  },
  watch: {
    theme(value) {
      settingsStorageService.setTheme(value);
      this.$emit("settings-updated");
    }
  },
  emits: [ "settings-updated" ]
};
</script>
