from typing import TYPE_CHECKING

from .common import WhereOrderLimitOffsetWithExplicitConfirmationToOperateOverAllRows, ConflictingQuery, ReturningQuery
from .utils import quote_sql_name, quote_sql_value, join_sql_string, join_aliased_sql

if TYPE_CHECKING:
	from .utils import SQL, AliasedSQL
	from .common import OrAction


class Update(WhereOrderLimitOffsetWithExplicitConfirmationToOperateOverAllRows, ConflictingQuery, ReturningQuery):
	def __init__(self, table: str, values: dict[str, "SQL"] = None, or_action: "OrAction" = None, returning: list["AliasedSQL"] = None):
		WhereOrderLimitOffsetWithExplicitConfirmationToOperateOverAllRows.__init__(self)
		ConflictingQuery.__init__(self, or_action)
		ReturningQuery.__init__(self, returning)
		self.table = table
		self.values = values or {}

	def with_table(self, table: str) -> "Update":
		self.table = table
		return self

	def set(self, column: str, value: "SQL") -> "Update":
		self.values[column] = value
		return self

	def build_sql(self) -> str:
		if not self.values:
			raise RuntimeError("Cannot update no value")
		or_action = f"OR {self.conflict_action}" if self.conflict_action else None
		values = join_sql_string(", ", *[quote_sql_name(column) + " = " + quote_sql_value(value) for column, value in self.values.items()])
		wolo = super().build_sql()
		returning = join_aliased_sql(", ", start="RETURNING ", *self.returning)
		return join_sql_string(" ", "UPDATE", or_action, quote_sql_name(self.table), "SET", values, wolo, returning)
