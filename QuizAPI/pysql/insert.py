from collections import defaultdict
from typing import TYPE_CHECKING

from .common import SQLElement, ConflictingQuery, ReturningQuery
from .utils import quote_sql_name, quote_sql_value, join_sql_string, join_aliased_sql

if TYPE_CHECKING:
	from .utils import SQL, AliasedSQL
	from .common import OrAction


class Insert(SQLElement, ConflictingQuery, ReturningQuery):
	def __init__(self, table: str, values: dict[str, list["SQL"]] = None, or_action: "OrAction" = None, returning: list["AliasedSQL"] = None):
		ConflictingQuery.__init__(self, or_action)
		ReturningQuery.__init__(self, returning)
		self.table = table
		self.values = defaultdict(list, values or {})

	def into(self, table: str) -> "Insert":
		self.table = table
		return self

	def value(self, column: str, value: "SQL") -> "Insert":
		self.values[column].append(value)
		return self

	def build_sql(self) -> str:
		s = -1
		for values in self.values.values():
			if s == -1:
				s = len(values)
			elif s != len(values):
				raise RuntimeError("Inconsistent number of values to insert")
		or_action = f"OR {self.conflict_action}" if self.conflict_action else None
		if self.values:
			columns = [*self.values.keys()]
			all_values = zip(*self.values.values())
			values = join_sql_string(", ", start="(", *columns, end=")", str_transform=quote_sql_name) + " VALUES " + join_sql_string(", ", *[join_sql_string(", ", start="(", *vals, end=")", str_transform=quote_sql_value) for vals in all_values])
		else:
			values = "DEFAULT VALUES"
		returning = join_aliased_sql(", ", start="RETURNING ", *self.returning)
		return join_sql_string(" ", "INSERT", or_action, "INTO", quote_sql_name(self.table), values, returning)
