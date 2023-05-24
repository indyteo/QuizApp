<template>
  <p class="text-overline mt-6">Meilleurs scores ({{ registeredScores.length }})</p>
  <v-list rounded="lg">
    <v-hover v-for="(scoreEntry, index) in registeredScores" :key="index">
      <template v-slot:default="{ isHovering, props }">
        <v-list-item
            v-bind="props"
            :title="scoreEntry.playerName"
            :subtitle="`Score : ${scoreEntry.score} / ${numberOfQuestions} (${numberOfQuestions ? Math.round(100 * scoreEntry.score / numberOfQuestions) : '--'}%)`"
            class="py-3"
        >
          <template v-slot:prepend>
            <v-avatar v-if="index < 3" :color="podium[index].color">
              <v-icon :icon="podium[index].icon" />
            </v-avatar>
            <v-avatar v-else>{{ index + 1 }}</v-avatar>
          </template>
          <template v-slot:append>
            <v-tooltip :text="'Date de la participation : ' + scoreEntry.date" location="bottom">
              <template v-slot:activator="{ props }">
                <v-icon v-bind="props" icon="mdi-calendar-clock" size="small" :style="'transition: opacity 0.1s; opacity: ' + (isHovering ? 1 : 0)" />
              </template>
            </v-tooltip>
          </template>
        </v-list-item>
      </template>
    </v-hover>
    <v-list-item v-if="registeredScores.length === 0" title="Aucun participant" subtitle="Soit le 1er pour apparaître dans ce classement !">
      <template v-slot:prepend>
        <v-avatar color="error">
          <v-icon icon="mdi-close" />
        </v-avatar>
      </template>
    </v-list-item>
  </v-list>
</template>

<script>
import quizApiService from "@/services/QuizApiService";

export default {
  name: "Leaderboard",
  data() {
    return {
      registeredScores: [],
      numberOfQuestions: 0,
      podium: [
        { color: "yellow", icon: "mdi-podium-gold" },
        { color: "grey-lighten-3", icon: "mdi-podium-silver" },
        { color: "orange-darken-1", icon: "mdi-podium-bronze" }
      ]
    };
  },
  created() {
    quizApiService.getQuizInfo().then(res => {
      this.$emit("participations-loaded", this.registeredScores = res.data.scores);
      this.$emit("number-of-questions-loaded", this.numberOfQuestions = res.data.size);
    });
  },
  emits: [ "number-of-questions-loaded", "participations-loaded" ]
};
</script>
