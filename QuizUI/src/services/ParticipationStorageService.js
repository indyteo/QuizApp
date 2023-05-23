export default {
  clear() {
    localStorage.removeItem("quiz-player-name");
    localStorage.removeItem("quiz-player-score");
  },
  savePlayerName(playerName) {
    localStorage.setItem("quiz-player-name", playerName);
  },
  getPlayerName() {
    return localStorage.getItem("quiz-player-name");
  },
  saveParticipationScore(participationScore) {
    localStorage.setItem("quiz-player-score", participationScore.toString());
  },
  getParticipationScore() {
    return parseInt(localStorage.getItem("quiz-player-score") ?? "0");
  }
};
