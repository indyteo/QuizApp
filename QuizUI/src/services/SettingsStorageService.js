export default {
  clear() {
    localStorage.removeItem("quiz-settings-theme");
  },
  setTheme(theme) {
    localStorage.setItem("quiz-settings-theme", theme);
  },
  getTheme() {
    return localStorage.getItem("quiz-settings-theme");
  }
};
