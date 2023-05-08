from typing import TYPE_CHECKING

from .common import WhereOrderLimitOffsetWithExplicitConfirmationToOperateOverAllRows, ReturningQuery
from .utils import quote_sql_name, join_sql_string, join_aliased_sql

if TYPE_CHECKING:
	from .utils import AliasedSQL


class Delete(WhereOrderLimitOffsetWithExplicitConfirmationToOperateOverAllRows, ReturningQuery):
	def __init__(self, table: str, returning: list["AliasedSQL"] = None):
		WhereOrderLimitOffsetWithExplicitConfirmationToOperateOverAllRows.__init__(self)
		ReturningQuery.__init__(self, returning)
		self.table = table

	def from_table(self, table: str) -> "Delete":
		self.table = table
		return self

	def build_sql(self) -> str:
		wolo = super().build_sql()
		returning = join_aliased_sql(", ", start="RETURNING ", *self.returning)
		return join_sql_string(" ", "DELETE FROM", quote_sql_name(self.table), wolo, returning)
