from typing import Optional, Literal, Union, TYPE_CHECKING, Iterable, TypeVar, Callable

if TYPE_CHECKING:
	from .common import SQLElement

T = TypeVar("T")
NoneType = type(None)

name_separator = "."
quote_name = "`"
quote_value = "'"
named_placeholder_prefix = ":"
positional_placeholder = "?"


class RawSQL:
	def __init__(self, sql):
		self.sql = sql

	def __str__(self):
		return self.sql

	def __add__(self, other):
		return str(self) + str(other)

	def __radd__(self, other):
		return str(other) + str(self.sql)


SQL = Union[str, RawSQL]
AliasedSQL = Union[SQL, tuple[SQL, str]]


def raw_sql(sql: str) -> SQL:
	return RawSQL(sql)


def placeholder(name: str = None) -> SQL:
	return raw_sql(named_placeholder_prefix + name if name else positional_placeholder)


def quote_sql_name(name: SQL) -> str:
	if isinstance(name, RawSQL):
		return name.sql
	if name == "*":
		return name
	try:
		separator = name.index(name_separator)
		return quote_sql_name(name[:separator]) + name_separator + quote_sql_name(name[separator + 1:])
	except ValueError:
		return quote_name + name.replace(quote_name, quote_name + quote_name) + quote_name


def quote_sql_value(value: object) -> str:
	if isinstance(value, RawSQL):
		return value.sql
	return quote_value + str(value).replace(quote_value, quote_value + quote_value) + quote_value


SQLType = Literal["TEXT", "INTEGER", "REAL", "NULL", "BLOB"]
sql_types: dict[type, SQLType] = {
	str: "TEXT",
	int: "INTEGER",
	bool: "INTEGER",
	float: "REAL",
	NoneType: "NULL",
	object: "BLOB"
}


def type_to_sql(type_: type) -> SQLType:
	return sql_types.get(type_, "BLOB")


def join_sql_string(separator: str, *elements: Optional[Union["SQLElement", SQL]], start: str = "", end: str = "", force_start_and_end_even_if_empty: bool = False, str_transform: Callable[[str], str] = str) -> str:
	string = separator.join([str_transform(element) if type(element) is str else str(element) for element in elements if element])
	return start + string + end if force_start_and_end_even_if_empty or string else string


def join_aliased_sql(separator: str, *aliased_sql: "AliasedSQL", start: str = "", end: str = "", force_start_and_end_even_if_empty: bool = False) -> str:
	return join_sql_string(separator, *[f"{quote_sql_name(aliased[0])} AS {quote_sql_name(aliased[1])}" if type(aliased) is tuple else quote_sql_name(aliased) for aliased in aliased_sql], start=start, end=end, force_start_and_end_even_if_empty=force_start_and_end_even_if_empty)


def filter_type(iterable: Iterable[object], type_: type[T]) -> Iterable[T]:
	return filter(lambda obj: isinstance(obj, type_), iterable)


def flatten(iterable: Iterable[Iterable[T]]) -> list[T]:
	return [item for sub in iterable for item in sub]
