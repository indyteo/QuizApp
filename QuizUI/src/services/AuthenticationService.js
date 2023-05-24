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
    return this.verifyJwtExpirationDate(this.getToken());
  },
  verifyJwtExpirationDate(token) {
    if (!token)
      return false;
    const splitted = token.split(".");
    if (splitted.length < 2)
      return false;
    const payload = JSON.parse(atob(splitted[1]));
    return "exp" in payload && payload.exp > Date.now() / 1000;
  }
};
