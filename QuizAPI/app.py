from hashlib import md5
from os import environ

from flask import Flask, Response, request
from flask_cors import CORS

from QuizAPI.jwt_utils import build_token
from QuizAPI.models import Question, Answer, LoginRequest, LoginResponse, QuizInfo, Score, Participation
from QuizAPI.utils import returns_json, request_model, requires_authentication

app = Flask(__name__)
CORS(app)


dummy_question_1 = Question("Quelle est la couleur du cheval blanc d'Henry IV ?", "Dummy Question 2", "falseb64imagecontent", 2, [
	Answer("Noir", False),
	Answer("Gris", False),
	Answer("Blanc", True),
	Answer("La réponse D", False)
])
dummy_question_2 = Question("Question 1", "Dummy Question 1", "falseb64imagecontent", 1, [
	Answer("La réponse A", True),
	Answer("La réponse B", False),
	Answer("La réponse C", False),
	Answer("La réponse D", False)
])
dummy_question_3 = Question("Question 3", "Dummy Question 3", "falseb64imagecontent", 3, [
	Answer("La réponse A", False),
	Answer("La réponse B", True),
	Answer("La réponse C", False),
	Answer("La réponse D", False)
])


@app.route("/login", methods=["POST"])
@request_model(LoginRequest)
@returns_json
def login(payload: LoginRequest):
	password = md5(payload.password.encode("UTF-8")).hexdigest()
	correct = environ.get("APP_ADMIN_PASSWORD")
	if password == correct:
		return LoginResponse(build_token())
	else:
		return "Unauthorized", 401


@app.route("/quiz-info", methods=["GET"])
@returns_json
def get_quiz_info():
	return QuizInfo(3, Score("jennycjay", 3), Score("indyteo", 0), Score("AaronJI185", 2))


@app.route("/questions", methods=["GET"])
def list_questions():
	position = request.args.get("position", -1, type=int)
	if position >= 0:
		if position == 1:
			return dummy_question_2
		elif position == 2:
			return dummy_question_1
		elif position == 3:
			return dummy_question_3
		return "Not Found", 404
	res = Response(Question.to_json_list(dummy_question_1, dummy_question_2, dummy_question_3))
	res.headers.set("Content-Type", "application/json")
	return res


@app.route("/questions/<question_id>", methods=["GET"])
@returns_json
def get_question(question_id):
	if question_id == 1:
		return dummy_question_1
	elif question_id == 2:
		return dummy_question_2
	elif question_id == 3:
		return dummy_question_3
	return "Not Found", 404


@app.route("/participations", methods=["POST"])
@requires_authentication
@request_model(Participation)
@returns_json
def participate(payload: Participation):
	return Score(payload.player_name, 2)


if __name__ == "__main__":
	app.run()
