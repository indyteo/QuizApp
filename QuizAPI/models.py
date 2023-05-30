from os import environ

from pyjson import JsonBindings, JsonModel, Nullable
from pysql import Database, DatabaseModel, Column, Primary, Foreign, Delete

debug = int(environ.get("FLASK_DEBUG")) != 0
db = Database("quiz.db", auto_create_tables=True, debug=debug)
json = JsonBindings(indent=2 if debug else None)


@json.model(error=bool, message=str, code=int)
class APIError(Exception, JsonModel):
	def __init__(self, message: str, code: int = 400):
		super().__init__(message)
		self.error = True
		self.message = message
		self.code = code

	@staticmethod
	def not_found(resource: str, name):
		return APIError(f"{resource} not found: {name}", 404)

	@staticmethod
	def unauthorized(message="You must login to perform this action"):
		return APIError(message, 401)

	@staticmethod
	def internal_server_error(error: Exception):
		return APIError(repr(error) if debug else "An exception occurred during the handling of your request. Please try again later!", 500)


@db.model("answer", Column("id", int, Primary(True)), Column("text", str), Column("is_correct", bool), Column("question", int, Foreign("questions", "id")))
@json.model(id=Nullable(int), text=str, is_correct=(bool, "isCorrect"))
class Answer(DatabaseModel, JsonModel):
	id: int
	question: int

	def __init__(self, text: str, is_correct: bool):
		self.text = text
		self.is_correct = is_correct

	def validate(self):
		if not self.text:
			raise APIError("Missing answer text")


@db.model("questions", Column("id", int, Primary(True)), Column("text", str), Column("title", str), Column("image", str), Column("position", int))
@json.model(id=Nullable(int), text=str, title=str, image=Nullable(str), position=int, possible_answers=([Answer, ...], "possibleAnswers"))
class Question(DatabaseModel, JsonModel):
	id: int

	def __init__(self, text: str, title: str, image: str, position: int, possible_answers: list[Answer]):
		self.text = text
		self.title = title
		self.image = image
		self.position = position
		self.possible_answers = possible_answers

	def validate(self):
		if not self.text:
			raise APIError("Missing question text")
		if not self.title:
			raise APIError("Missing question title")
		if not self.possible_answers:
			raise APIError("Missing question answers")
		correct_count = 0
		for answer in self.possible_answers:
			answer.validate()
			if answer.is_correct:
				correct_count += 1
		if correct_count != 1:
			raise APIError("There should be one and only one correct answer to the question")
		if self.position <= 0 or self.position > Question.count() + 1:
			raise APIError("Invalid question position")

	def with_answers(self) -> "Question":
		self.possible_answers = Answer.list("question = :id", id=self.id)
		return self

	def delete_answers(self):
		db.execute(Delete(Answer.__table__.name).where("question = :id").build_sql(), id=self.id).close()

	def save_answers(self, cleanup_old_answers: bool = True):
		if cleanup_old_answers:
			self.delete_answers()
		for answer in self.possible_answers:
			answer.question = self.id
			answer.add("id")


@json.model(id=int)
class QuestionId(JsonModel):
	def __init__(self, id_: int):
		self.id = id_


@db.model("scores", Column("id", int, Primary(True)), Column("player_name", str), Column("score", int), Column("date", str))
@json.model(player_name=(str, "playerName"), score=int, date=str)
class Score(DatabaseModel, JsonModel):
	def __init__(self, player_name: str, score: int, date: str):
		self.player_name = player_name
		self.score = score
		self.date = date


@json.model(size=int, scores=[Score, ...])
class QuizInfo(JsonModel):
	def __init__(self, size: int, *scores: Score):
		self.size = size
		self.scores = scores


@json.model(password=str)
class LoginRequest(JsonModel):
	password: str

	def validate(self):
		if not self.password:
			raise APIError("Missing login password")


@json.model(token=str)
class LoginResponse(JsonModel):
	def __init__(self, token: str):
		self.token = token


@json.model(player_name=(str, "playerName"), answers=[int, ...])
class Participation(JsonModel):
	player_name: str
	answers: list[int]

	def validate(self):
		if not self.player_name:
			raise APIError("Missing participant name")


@json.model(correct_answer_position=(int, "correctAnswerPosition"), was_correct=(bool, "wasCorrect"))
class AnswerSummary(JsonModel):
	def __init__(self, correct_answer_position: int, was_correct: int):
		self.correct_answer_position = correct_answer_position
		self.was_correct = was_correct


@json.model(player_name=(str, "playerName"), score=int, answers_summaries=([AnswerSummary, ...], "answersSummaries"))
class ParticipationResponse(JsonModel):
	def __init__(self, score: Score, answers_summaries: list[AnswerSummary]):
		self.player_name = score.player_name
		self.score = score.score
		self.answers_summaries = answers_summaries
