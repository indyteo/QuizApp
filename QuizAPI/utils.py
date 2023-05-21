from functools import wraps
from flask import Response, request

from QuizAPI.jwt_utils import decode_token, JwtError
from QuizAPI.pyjson import JsonModel


def returns_json(handler):
	@wraps(handler)
	def wrapper(*args, **kwargs):
		ret = handler(*args, **kwargs)
		if type(ret) is tuple:
			obj, code = ret
		else:
			obj = ret
			code = None
		if hasattr(obj, "to_json"):
			res = Response(obj.to_json())
			res.headers.set("Content-Type", "application/json")
			if code:
				res.status_code = code
			return res
		return ret
	return wrapper


def request_model(model: type[JsonModel]):
	def decorator(handler):
		@wraps(handler)
		def wrapper(*args, **kwargs):
			obj = model.from_json(request.get_data(as_text=True))
			return handler(*args, **kwargs, payload=obj)
		return wrapper
	return decorator


def requires_authentication(handler):
	@wraps(handler)
	def wrapper(*args, **kwargs):
		auth = request.headers.get("Authorization")
		if auth and auth.startswith("Bearer "):
			token = auth[len("Bearer "):]
			try:
				decode_token(token)
				return handler(*args, **kwargs)
			except JwtError as e:
				return e.message, 401
		return "Unauthorized", 401
	return wrapper
