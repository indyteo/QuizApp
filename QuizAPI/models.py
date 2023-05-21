from os import environ

from pyjson import JsonBindings, JsonModel
from pysql import Database, DatabaseModel, Column, Primary, Foreign, Delete, Unique

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
	def unauthorized():
		return APIError("You must login to perform this action", 401)

	@staticmethod
	def internal_server_error(error: Exception):
		return APIError(repr(error) if debug else "An exception occurred during the handling of your request. Please try again later!", 500)


@db.model("answer", Column("text", str), Column("is_correct", bool), Column("question", int, Foreign("questions", "id")))
@json.model(text=str, is_correct=(bool, "isCorrect"))
class Answer(DatabaseModel, JsonModel):
	question: int

	def __init__(self, text: str, is_correct: bool):
		self.text = text
		self.is_correct = is_correct


@db.model("questions", Column("id", int, Primary(True)), Column("text", str), Column("title", str), Column("image", str), Column("position", int, Unique()))
@json.model(text=str, title=str, image=str, position=int, possible_answers=([Answer, ...], "possibleAnswers"))
class Question(DatabaseModel, JsonModel):
	id: int

	def __init__(self, text: str, title: str, image: str, position: int, possible_answers: list[Answer]):
		self.text = text
		self.title = title
		self.image = image
		self.position = position
		self.possible_answers = possible_answers

	def with_answers(self) -> "Question":
		self.possible_answers = Answer.list("question = :id", id=self.id)
		return self

	def save_answers(self):
		db.execute(Delete(Answer.__table__.name).where("question = :id").build_sql(), id=self.id)
		for answer in self.possible_answers:
			answer.question = self.id
			answer.add()

	@staticmethod
	def fake(id_: int):
		fake = Question("", "", "", 0, [])
		fake.id = id_
		return fake


@json.model(id=int)
class QuestionId(JsonModel):
	def __init__(self, id_: int):
		self.id = id_


@db.model("scores", Column("id", int, Primary(True)), Column("player_name", str), Column("score", int))
@json.model(player_name=(str, "playerName"), score=int)
class Score(DatabaseModel, JsonModel):
	def __init__(self, player_name: str, score: int):
		self.player_name = player_name
		self.score = score


@json.model(size=int, scores=[Score, ...])
class QuizInfo(JsonModel):
	def __init__(self, size: int, *scores: Score):
		self.size = size
		self.scores = scores


@json.model(password=str)
class LoginRequest(JsonModel):
	password: str


@json.model(token=str)
class LoginResponse(JsonModel):
	def __init__(self, token: str):
		self.token = token


@json.model(player_name=(str, "playerName"), answers=[int, ...])
class Participation(JsonModel):
	player_name: str
	answers: list[int]
