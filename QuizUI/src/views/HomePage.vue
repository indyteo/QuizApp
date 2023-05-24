<template>
  <center-layout>
    <div class="text-center">
      <v-btn :to="{ name: 'start' }" size="x-large" rounded="xl" color="primary">Participer au quiz</v-btn>
    </div>
    <leaderboard />
  </center-layout>
</template>

<script>
import CenterLayout from "@/components/CenterLayout.vue";
import Leaderboard from "@/components/Leaderboard.vue";

export default {
  name: "HomePage",
  components: { Leaderboard, CenterLayout },
  inheritAttrs: false
};
</script>
