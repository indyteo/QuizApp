from os import environ

from QuizAPI.pyjson import JsonBindings, JsonModel
from QuizAPI.pysql import Database, DatabaseModel, Column, Primary, Foreign

debug = int(environ.get("FLASK_DEBUG")) != 0
db = Database("quiz.db", auto_create_tables=True, debug=debug)
json = JsonBindings(indent=2 if debug else None)


@db.model("answer", Column("id", int, Primary()), Column("text", str), Column("is_correct", bool), Column("question", int, Foreign("questions", "id")))
@json.model(text=str, is_correct=(bool, "isCorrect"))
class Answer(DatabaseModel, JsonModel):
	def __init__(self, text: str, is_correct: bool):
		self.text = text
		self.is_correct = is_correct


@db.model("questions", Column("id", int), Column("text", str), Column("title", str), Column("image", str), Column("position", int))
@json.model(text=str, title=str, image=str, position=int, possible_answers=([Answer, ...], "possibleAnswers"))
class Question(DatabaseModel, JsonModel):
	def __init__(self, text: str, title: str, image: str, position: int, possible_answers: list[Answer]):
		self.id: int
		self.text = text
		self.title = title
		self.image = image
		self.position = position
		self.possible_answers = possible_answers

	def load_answers(self):
		self.possible_answers = Answer.list("question = :id", id=self.id)


@db.model("scores", Column("id", int, Primary()), Column("player_name", str), Column("score", int))
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
	def __init__(self, player_name: str, answers: list[int]):
		self.player_name = player_name
		self.answers = answers
