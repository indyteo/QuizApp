<template>
  <div>
    <h1>New Quiz Page</h1>
    <form>
      <div className="mb-3">
        <label htmlFor="playerName" className="form-label">Saisissez votre nom : </label>
        <input type="text" className="form-control" id="playerName" v-model="username" />

      </div>
      <button type="submit" className="btn btn-primary">GO!</button>
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
