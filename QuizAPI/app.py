from hashlib import md5
from os import environ

from flask import Flask, request
from flask_cors import CORS

from jwt_utils import build_token
from models import Question, LoginRequest, LoginResponse, QuizInfo, Score, Participation, APIError, QuestionId
from pysql import Update, raw_sql
from utils import returns_json, request_model, requires_authentication

app = Flask(__name__)
CORS(app)


@app.route("/login", methods=["POST"])
@request_model(LoginRequest)
@returns_json
def login(payload: LoginRequest):
	password = md5(payload.password.encode("UTF-8")).hexdigest()
	correct = environ.get("APP_ADMIN_PASSWORD")
	if password == correct:
		return LoginResponse(build_token())
	else:
		raise APIError.unauthorized()


@app.route("/quiz-info", methods=["GET"])
@returns_json
def get_quiz_info():
	return QuizInfo(Question.count(), *Score.list())


@app.route("/questions", methods=["GET"])
@returns_json
def list_questions():
	position = request.args.get("position", -1, type=int)
	if position >= 0:
		questions = Question.list("position = :position", position=position)
		if not questions:
			raise APIError.not_found("Question by position", position)
		return questions[0].with_answers()
	return [question.with_answers() for question in Question.list(order_by="position")]


@app.route("/questions/<int:question_id>", methods=["GET"])
@returns_json
def get_question(question_id: int):
	question = Question.get(id=question_id)
	if not question:
		raise APIError.not_found("Question", question_id)
	return question.with_answers()


@app.route("/participations", methods=["POST"])
@request_model(Participation)
@returns_json
def participate(payload: Participation):
	questions = Question.list(order_by="position")
	number_of_questions = len(questions)
	number_of_answers = len(payload.answers)
	if number_of_answers != number_of_questions:
		raise APIError(f"Incorrect number of answers, expected {number_of_questions} but received {number_of_answers}")
	correct_answers = 0
	for i in range(number_of_questions):
		question = questions[i].with_answers()
		answer = payload.answers[i]
		if answer <= 0 or answer > 4:
			raise APIError(f"Invalid answer #{answer} for question #{question.id} (must be between 1 and 4)")
		if question.possible_answers[answer - 1].is_correct:
			correct_answers += 1
	score = Score(payload.player_name, correct_answers)
	score.add("id")
	return score


@app.route("/questions", methods=["POST"])
@requires_authentication
@request_model(Question)
@returns_json
def create_question(payload: Question):
	Question.__database__.execute(Update(Question.__table__.name).set("position", raw_sql("position + 1")).where("position >= :position").build_sql(), position=payload.position)
	payload.add("id")
	return QuestionId(payload.id)


@app.route("/questions/<int:question_id>", methods=["PUT"])
@requires_authentication
@request_model(Question)
@returns_json
def update_question(question_id: int, payload: Question):
	previous_question = Question.get(id=question_id)
	if not previous_question:
		raise APIError.not_found("Question", question_id)
	if payload.position != previous_question.position:
		operation = "+" if payload.position < previous_question.position else "-"
		Question.__database__.execute(Update(Question.__table__.name).set("position", raw_sql(f"position {operation} 1")).where("position >= :position AND position <= :position AND id <> :id").build_sql(), position=payload.position, id=question_id)
	payload.id = question_id
	payload.save()
	payload.save_answers()
	return "", 204


@app.route("/questions/<int:question_id>", methods=["DELETE"])
@requires_authentication
@returns_json
def delete_question(question_id: int):
	if not Question.fake(question_id).delete():
		raise APIError.not_found("Question", question_id)
	return "", 204


@app.route("/questions/all", methods=["DELETE"])
@requires_authentication
@returns_json
def delete_all_questions():
	Question.__database__.execute(Question.__table__.delete(False).all_rows(True).build_sql()).close()
	return "", 204


@app.route("/participations/all", methods=["DELETE"])
@requires_authentication
@returns_json
def delete_all_scores():
	Score.__database__.execute(Score.__table__.delete(False).all_rows(True).build_sql()).close()
	return "", 204


if __name__ == "__main__":
	app.run()
