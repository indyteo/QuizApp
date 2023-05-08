from abc import ABCMeta, abstractmethod
from typing import TypeVar, Generic, Any, TYPE_CHECKING, Union

from .utils import NoneType

if TYPE_CHECKING:
	from .bindings import JsonModel
	from .utils import NullableJsonFieldType, JsonFieldType

	U = TypeVar("U", bound=JsonModel)

T = TypeVar("T")


class JsonType(Generic[T], metaclass=ABCMeta):
	@abstractmethod
	def serialize(self, value: T) -> Any:
		raise NotImplementedError(f"The class {type(self).__name__} does not provide an implementation to serialize as JSON")

	@abstractmethod
	def deserialize(self, value: Any) -> T:
		raise NotImplementedError(f"The class {type(self).__name__} does not provide an implementation to deserialize from JSON")


class SimpleJsonType(JsonType[T]):
	def __init__(self, python_type: Union[type[T], "Nullable"]):
		self.python_type = python_type

	def serialize(self, value: T) -> Any:
		return value

	def deserialize(self, value: Any) -> T:
		return self.python_type(value)


class ForeignJsonType(JsonType["U"]):
	def __init__(self, model_class: type["U"]):
		self.model_class = model_class

	def serialize(self, value: "U") -> Any:
		return value.to_dict()

	def deserialize(self, value: Any) -> "U":
		return self.model_class.from_dict(value)


class VariableListJsonType(JsonType[list[T]]):
	def __init__(self, json_type: JsonType[T]):
		self.json_type = json_type

	def serialize(self, value: list[T]) -> Any:
		return [self.json_type.serialize(item) for item in value]

	def deserialize(self, value: Any) -> list[T]:
		return [self.json_type.deserialize(item) for item in value]


class StaticListJsonType(JsonType[list]):
	def __init__(self, *json_types: JsonType):
		self.json_types = json_types

	def serialize(self, value: list) -> Any:
		return [type_.serialize(item) for item, type_ in zip(value, self.json_types)]

	def deserialize(self, value: Any) -> list:
		return [type_.deserialize(item) for item, type_ in zip(value, self.json_types)]


class VariableDictJsonType(JsonType[dict[str, T]]):
	def __init__(self, json_type: JsonType[T]):
		self.json_type = json_type

	def serialize(self, value: dict[str, T]) -> Any:
		return {key: self.json_type.serialize(item) for key, item in value.items()}

	def deserialize(self, value: Any) -> dict[str, T]:
		return {key: self.json_type.deserialize(item) for key, item in value.items()}


class StaticDictJsonType(JsonType[dict[str, Any]]):
	def __init__(self, **json_types: JsonType):
		self.json_types = json_types

	def serialize(self, value: dict[str, Any]) -> Any:
		return {key: self.json_types[key].serialize(item) for key, item in value.items()}

	def deserialize(self, value: Any) -> dict[str, Any]:
		return {key: self.json_types[key].deserialize(item) for key, item in value.items()}


class Nullable:
	def __init__(self, base_type: "JsonFieldType"):
		self.base_type = json_field_type(base_type)

	def __call__(self, value=None):
		return None if value is None else self.base_type.deserialize(value)


def json_field_type(field_type: "NullableJsonFieldType") -> "JsonType":
	if type(field_type) is list:
		if len(field_type) == 2 and field_type[1] is ...:
			return VariableListJsonType(json_field_type(field_type[0]))
		else:
			return StaticListJsonType(*[json_field_type(type_) for type_ in field_type])
	if type(field_type) is dict:
		if len(field_type) == 1 and ... in field_type:
			return VariableDictJsonType(json_field_type(field_type[...]))
		else:
			return StaticDictJsonType(**{key: json_field_type(type_) for key, type_ in field_type.items()})
	if field_type is str or field_type is int or field_type is float or field_type is bool or field_type == NoneType or isinstance(field_type, Nullable):
		return SimpleJsonType(field_type)
	if hasattr(field_type, "__json__"):
		# noinspection PyTypeChecker
		# This is because we can't test issubclass(field_type, JsonModel)
		# even if we decorate JsonModel protocol with @runtime_checkable
		# because it contains attributes other than methods
		return ForeignJsonType(field_type)
	raise TypeError(f"{field_type} does not denote a valid JSON field type")
