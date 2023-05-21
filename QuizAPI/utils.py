from functools import wraps
from re import search
from flask import Response, request

from jwt_utils import decode_token, JwtError
from models import APIError
from pyjson import JsonModel


def returns_json(handler):
	@wraps(handler)
	def wrapper(*args, **kwargs):
		try:
			ret = handler(*args, **kwargs)
		except APIError as e:
			ret = e
		except Exception as e:
			ret = APIError.internal_server_error(e)
		if type(ret) is tuple:
			obj, code = ret
		else:
			obj = ret
			code = obj.code if isinstance(obj, APIError) else None
		if type(obj) is list and len(obj) > 0:
			json_type = type(obj[0])
			for i in range(1, len(obj)):
				if type(obj[i]) != json_type:
					return ret
			if hasattr(json_type, "to_json_list"):
				json = json_type.to_json_list(obj)
			else:
				return ret
		elif hasattr(obj, "to_json"):
			json = obj.to_json()
		else:
			return ret
		res = Response(json)
		res.headers.set("Content-Type", "application/json; charset=utf-8")
		if code:
			res.status_code = code
		return res
	return wrapper


def request_model(model: type[JsonModel]):
	def decorator(handler):
		@wraps(handler)
		def wrapper(*args, **kwargs):
			content_type = request.headers.get("Content-Type")
			charset_in_content_type = search("charset=(\\S+)", content_type)
			charset = charset_in_content_type[1] if charset_in_content_type else "UTF-8"
			obj = model.from_json(request.get_data().decode(charset))
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
