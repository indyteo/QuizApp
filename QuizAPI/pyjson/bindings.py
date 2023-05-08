from json import dumps, loads
from typing import TypeVar, Protocol, Any, TYPE_CHECKING

from .json_types import json_field_type

if TYPE_CHECKING:
	from .utils import JsonFieldType, JsonAliasedType

T = TypeVar("T", bound="JsonModel")


class Field:
	def __init__(self, python_name: str, json_type: "JsonFieldType", json_name: str = None):
		self.python_name = python_name
		self.json_name = json_name or python_name
		self.json_type = json_field_type(json_type)


class Schema:
	def __init__(self, python_class: type, *fields: Field):
		self.python_class = python_class
		self.fields = fields


class JsonBindings:
	def __init__(self, indent: int = None):
		self.schemas = {}
		self.indent = indent

	def get_schema(self, python_class: type):
		return self.schemas[python_class]

	def model(self, **structure: "JsonAliasedType"):
		fields = []
		for name, element in structure.items():
			if type(element) is tuple:
				if type(element[0]) is str:
					alias, element = element
				else:
					element, alias = element
			else:
				alias = None
			fields.append(Field(name, element, alias))

		# noinspection PyPep8Naming
		# The decorator is applied to classes, thus the argument is in fact a class
		def decorator(BaseClass: type[T]) -> type[T]:
			self.schemas[BaseClass] = schema = Schema(BaseClass, *fields)

			def to_json(this: BaseClass) -> str:
				return dumps(this.to_dict(), indent=self.indent)

			def from_json(json_string: str) -> BaseClass:
				return BaseClass.from_dict(loads(json_string))

			def to_json_list(*values: BaseClass) -> str:
				return dumps([value.to_dict() for value in values], indent=self.indent)

			def from_json_list(json_string: str) -> list[BaseClass]:
				return [BaseClass.from_dict(elem) for elem in loads(json_string)]

			def to_dict(this: BaseClass) -> dict[str, Any]:
				values = {}
				for field in schema.fields:
					values[field.json_name] = field.json_type.serialize(this.__dict__.get(field.python_name))
				return values

			def from_dict(values: dict[str, Any]) -> BaseClass:
				# noinspection PyArgumentList
				this = BaseClass.__new__(BaseClass)
				for field in schema.fields:
					this.__dict__[field.python_name] = field.json_type.deserialize(values.get(field.json_name))
				return this

			setattr(BaseClass, "__json__", self)
			setattr(BaseClass, "__schema__", schema)
			setattr(BaseClass, "to_json", to_json)
			setattr(BaseClass, "from_json", staticmethod(from_json))
			setattr(BaseClass, "to_json_list", staticmethod(to_json_list))
			setattr(BaseClass, "from_json_list", staticmethod(from_json_list))
			setattr(BaseClass, "to_dict", to_dict)
			setattr(BaseClass, "from_dict", staticmethod(from_dict))
			return BaseClass
		return decorator


class JsonModel(Protocol):
	__json__: JsonBindings
	__schema__: Schema
	def to_json(self: T) -> str: ...
	@classmethod
	def from_json(cls: type[T], json_string: str) -> T: ...
	@classmethod
	def to_json_list(cls: type[T], *values: T) -> str: ...
	@classmethod
	def from_json_list(cls: type[T], json_string: str) -> list[T]: ...
