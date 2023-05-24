import axios from "axios";
import authenticationService from "@/services/AuthenticationService";
import router from "@/router";

const instance = axios.create({
  baseURL: `${import.meta.env.VITE_API_URL}`,
  json: true
});

export default {
  async call(method, resource, data = null, token = null) {
    const headers = { "Content-Type": "application/json" };
    if (token != null)
      headers.authorization = "Bearer " + token;

    return instance({
      method,
      headers: headers,
      url: resource,
      data
    }).catch(error => {
      if (error.response.status === 401) {
        authenticationService.logout();
        router.push({ name: "login", query: { returnTo: router.currentRoute.value.fullPath } });
      } else
        Promise.reject(error.response);
    });
  },
  getQuizInfo() {
    return this.call("get", "quiz-info");
  },
  getQuestion(position) {
    return this.call("get", `questions?position=${position}`);
  },
  participate(playerName, answers) {
    return this.call("post", "participations", { playerName, answers });
  },
  login(password) {
    return this.call("post", "login", { password });
  },
  listQuestions() {
    return this.call("get", "questions");
  },
  getQuestionById(id) {
    return this.call("get", `questions/${id}`, null, authenticationService.getToken());
  },
  createQuestion(question) {
    return this.call("post", "questions", question, authenticationService.getToken());
  },
  updateQuestion(id, question) {
    return this.call("put", `questions/${id}`, question, authenticationService.getToken());
  },
  deleteQuestion(id) {
    return this.call("delete", `questions/${id}`, null, authenticationService.getToken());
  },
  deleteAllQuestions() {
    return this.call("delete", "questions/all", null, authenticationService.getToken());
  },
  deleteAllParticipations() {
    return this.call("delete", "participations/all", null, authenticationService.getToken());
  }
};
