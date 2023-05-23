import quizApiService from "@/services/QuizApiService";

export default {
  logout() {
    localStorage.removeItem("quiz-auth-token");
  },
  login(password) {
    return quizApiService.login(password).then(res => {
      localStorage.setItem("quiz-auth-token", res.data.token);
      return true;
    }).catch(() => false);
  },
  getToken() {
    return localStorage.getItem("quiz-auth-token");
  },
  isLoggedIn() {
    return this.getToken() !== null;
  }
};
