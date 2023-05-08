from typing import Iterable, TYPE_CHECKING

from .common import WhereOrderLimitOffset
from .utils import quote_sql_name, join_sql_string, raw_sql, join_aliased_sql

if TYPE_CHECKING:
	from .join import Join
	from .utils import SQL, AliasedSQL


class SelectOptions:
	def __init__(self, distinct: bool = False):
		self.distinct = distinct


class Select(WhereOrderLimitOffset):
	def __init__(self, columns: Iterable["AliasedSQL"] = None, tables: Iterable["AliasedSQL"] = None, joins: Iterable["Join"] = None, groups: Iterable["SQL"] = None, having: str = None, select_options: SelectOptions = None):
		super().__init__()
		self.columns = columns or []
		self.tables = tables or []
		self.joins = joins or []
		self.groups = groups or []
		self.having_condition = having
		self.select_options = select_options or SelectOptions()

	def with_select_options(self, select_options: SelectOptions) -> "Select":
		self.select_options = select_options
		return self

	def distinct(self, distinct: bool = True) -> "Select":
		self.select_options.distinct = distinct
		return self

	def column(self, column: "SQL", alias: str = None) -> "Select":
		self.columns.append((column, alias) if alias else column)
		return self

	def value(self, value: str, alias: str = None) -> "Select":
		self.columns.append((raw_sql(value), alias) if alias else raw_sql(value))
		return self

	def from_table(self, table: "SQL", alias: str = None) -> "Select":
		self.tables.append((table, alias) if alias else table)
		return self

	def from_subquery(self, subquery: str, alias: str = None) -> "Select":
		self.tables.append((raw_sql(subquery), alias) if alias else raw_sql(subquery))
		return self

	def join(self, join: "Join") -> "Select":
		self.joins.append(join)
		return self

	def group_by(self, column: "SQL") -> "Select":
		self.groups.append(column)
		return self

	def having(self, condition: str) -> "Select":
		self.having_condition = condition
		return self

	def build_sql(self) -> str:
		distinct = "DISTINCT" if self.select_options.distinct else None
		columns = join_aliased_sql(", ", *self.columns) or "*"
		tables = ("FROM " + join_aliased_sql(", ", *self.tables)) if self.tables else None
		joins = join_sql_string(" ", *self.joins) if self.joins else None
		wolo = super().build_sql()
		groups = join_sql_string(" ", start="GROUP BY ", *self.groups, str_transform=quote_sql_name) if self.groups else None
		having = f"HAVING {self.having_condition}" if self.having_condition else None
		return join_sql_string(" ", "SELECT", distinct, columns, tables, joins, wolo, groups, having)
