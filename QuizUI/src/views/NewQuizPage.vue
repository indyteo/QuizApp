<template>
  <div>
    <h1>New Quiz Page</h1>
    <form>
      <div className="mb-3">

        <v-text-field
          v-model="username"
          color="primary"
          label="Votre nom"
          variant="filled"
        ></v-text-field>

      </div>
      <v-btn type="submit">GO!</v-btn>
    </form>
  </div>
</template>

<script>
export default {
  name: "NewQuizPage",
  data() {
    return {
      username: "",
    };
  },
};
</script>
