from functools import wraps
from json import JSONDecodeError
from re import search
from traceback import print_exc
from typing import Callable
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
			print_exc()
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
				json = json_type.to_json_list(*obj)
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


def default_json_validator(obj):
	if hasattr(obj, "validate") and callable(obj.validate):
		obj.validate()


def request_model(model: type[JsonModel], is_list: bool = False, validator: Callable[[JsonModel], None] = default_json_validator):
	def decorator(handler):
		@wraps(handler)
		def wrapper(*args, **kwargs):
			content_length = request.content_length
			if content_length is None:
				raise APIError("Missing Content-Length HTTP header", 411)
			if content_length > 10_000_000:
				raise APIError("Maximum allowed payload size is 10 MB", 413)
			content_type = request.content_type
			charset_in_content_type = search("charset=(\\S+)", content_type) if content_type else None
			charset = charset_in_content_type[1] if charset_in_content_type else "UTF-8"
			try:
				content = request.get_data().decode(charset)
			except (UnicodeDecodeError, LookupError) as e:
				raise APIError(f"Invalid encoding: {e}")
			try:
				if is_list:
					payload = model.from_json_list(content)
					for obj in payload:
						validator(obj)
				else:
					payload = model.from_json(content)
					validator(payload)
			except (JSONDecodeError, TypeError, AttributeError) as e:
				raise APIError(f"Invalid JSON payload: {e}")
			return handler(*args, **kwargs, payload=payload)
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
