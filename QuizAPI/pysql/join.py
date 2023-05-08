from typing import TYPE_CHECKING, TypeVar

from .common import SQLElement
from .utils import quote_sql_name, join_sql_string

if TYPE_CHECKING:
	from .utils import SQL

	T = TypeVar("T", bound="Join")


class Join(SQLElement):
	def __init__(self, sql: str, table: "SQL", alias: str = None):
		self.sql = sql
		self.table = table
		self.alias = alias

	def with_alias(self: "T", alias: str) -> "T":
		self.alias = alias
		return self

	def build_sql(self) -> str:
		alias = f"AS {quote_sql_name(self.alias)}" if self.alias else None
		return join_sql_string(" ", self.sql, "JOIN", quote_sql_name(self.table), alias)


class CrossJoin(Join):
	def __init__(self, table: "SQL", alias: str = None):
		super().__init__("CROSS", table, alias)


class InnerOrLeftJoin(Join):
	def __init__(self, sql: str, table: "SQL", alias: str = None):
		super().__init__(sql, table, alias)
		self.condition = None
		self.columns = []

	def on(self: "T", condition: str) -> "T":
		self.condition = condition
		return self

	def using(self: "T", column: "SQL") -> "T":
		self.columns.append(column)
		return self

	def build_sql(self) -> str:
		if not self.condition and not self.columns:
			raise RuntimeError("Cannot join with neither ON nor USING")
		if self.condition and self.columns:
			raise RuntimeError("Cannot join with both ON and USING")
		condition = f" ON {self.condition}" if self.condition else join_sql_string(", ", start=" USING (", *self.columns, end=")", str_transform=quote_sql_name)
		return super().build_sql() + condition


class InnerJoin(InnerOrLeftJoin):
	def __init__(self, table: "SQL", alias: str = None):
		super().__init__("INNER", table, alias)


class LeftJoin(InnerOrLeftJoin):
	def __init__(self, table: "SQL", alias: str = None):
		super().__init__("LEFT", table, alias)
