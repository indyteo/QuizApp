from datetime import datetime
from hashlib import md5
from os import environ

from flask import Flask, request
from flask_cors import CORS

from jwt_utils import build_token
from models import db, Question, LoginRequest, LoginResponse, QuizInfo, Score, Participation, APIError, QuestionId, \
	AnswerSummary, ParticipationResponse
from pysql import Update, raw_sql
from utils import returns_json, request_model, requires_authentication

app = Flask(__name__)
CORS(app)


@app.route("/rebuild-db", methods=["POST"])
@requires_authentication
@returns_json
def rebuild_db():
	for table in db.tables.values():
		db.execute(table.drop().build_sql()).close()
		db.execute(table.create().build_sql()).close()
	return "Ok"


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
	return QuizInfo(Question.count(), *Score.list(order_by=("score", True)))


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
	summary = []
	for i in range(number_of_questions):
		question = questions[i].with_answers()
		answer = payload.answers[i]
		number_of_possible_answers = len(question.possible_answers)
		if answer <= 0 or answer > number_of_possible_answers:
			raise APIError(f"Invalid answer #{answer} for question #{question.id} (must be between 1 and {number_of_possible_answers})")
		correct = 0
		for j, a in enumerate(question.possible_answers):
			if a.is_correct:
				correct = j + 1
		if is_correct := answer == correct:
			correct_answers += 1
		summary.append(AnswerSummary(correct, is_correct))
	score = Score(payload.player_name, correct_answers, datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
	score.add("id")
	return ParticipationResponse(score, summary)


@app.route("/questions", methods=["POST"])
@requires_authentication
@request_model(Question)
@returns_json
def create_question(payload: Question):
	db.execute(Update(Question.__table__.name).set("position", raw_sql("position + 1")).where("position >= :position").build_sql(), position=payload.position).close()
	payload.add("id")
	payload.save_answers(False)
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
		update_sql = Update(Question.__table__.name)\
			.set("position", raw_sql(f"position {operation} 1"))\
			.where("position BETWEEN :position_min AND :position_max AND id <> :id")\
			.build_sql()
		position_min = min(payload.position, previous_question.position)
		position_max = max(payload.position, previous_question.position)
		db.execute(update_sql, position_min=position_min, position_max=position_max, id=question_id).close()
	payload.id = question_id
	payload.save()
	payload.save_answers()
	return "", 204


@app.route("/questions/<int:question_id>", methods=["DELETE"])
@requires_authentication
@returns_json
def delete_question(question_id: int):
	question = Question.get(id=question_id)
	if not question:
		raise APIError.not_found("Question", question_id)
	question.delete_answers()
	question.delete()
	db.execute(Update(Question.__table__.name).set("position", raw_sql("position - 1")).where("position > :position").build_sql(), position=question.position).close()
	return "", 204


@app.route("/questions/all", methods=["DELETE"])
@requires_authentication
@returns_json
def delete_all_questions():
	db.execute(Question.__table__.delete(False).all_rows(True).build_sql()).close()
	return "", 204


@app.route("/participations/all", methods=["DELETE"])
@requires_authentication
@returns_json
def delete_all_scores():
	db.execute(Score.__table__.delete(False).all_rows(True).build_sql()).close()
	return "", 204


if __name__ == "__main__":
	app.run()
