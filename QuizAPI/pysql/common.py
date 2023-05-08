from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Union, TypeVar, Literal

from .utils import join_sql_string, quote_sql_name, type_to_sql, raw_sql

if TYPE_CHECKING:
	from .constraints import ColumnConstraint
	from .utils import SQLType, SQL, AliasedSQL

	T = TypeVar("T", bound="WhereOrderLimitOffset")
	U = TypeVar("U", bound="WhereOrderLimitOffsetWithExplicitConfirmationToOperateOverAllRows")
	V = TypeVar("V", bound="ConflictingQuery")
	W = TypeVar("W", bound="ReturningQuery")

	OrAction = Literal["ABORT", "FAIL", "IGNORE", "REPLACE", "ROLLBACK"]


class SQLElement(metaclass=ABCMeta):
	@abstractmethod
	def build_sql(self) -> str:
		raise NotImplementedError(f"The class {type(self).__name__} does not provide an implementation to build SQL")

	def __str__(self):
		return self.build_sql()


class Column(SQLElement):
	def __init__(self, sql_name: str, type_: type, *column_constraints: "ColumnConstraint"):
		self.python_name = sql_name
		self.sql_name = sql_name
		self.type_ = type_
		self.column_constraints = column_constraints

	def get_sql_type(self) -> "SQLType":
		return type_to_sql(self.type_)

	def with_python_name(self, python_name: str) -> "Column":
		self.python_name = python_name
		return self

	def build_sql(self) -> str:
		return join_sql_string(" ", quote_sql_name(self.sql_name), type_to_sql(self.type_), *self.column_constraints)


class WhereOrderLimitOffset(SQLElement):
	def __init__(self, condition: str = None, orders: Union["SQL", tuple[str, bool]] = None, limit: int = -1, offset: int = 0):
		self.condition = condition
		self.orders = orders or []
		self.limit = limit
		self.offset = offset

	def where(self: "T", condition: str) -> "T":
		self.condition = condition
		return self

	def order_by(self: "T", order_by: str, asc: bool = True) -> "T":
		self.orders.append((order_by, asc))
		return self

	def with_limit(self: "T", limit: int) -> "T":
		self.limit = limit
		return self

	def with_offset(self: "T", offset: int) -> "T":
		self.offset = offset
		return self

	def build_sql(self) -> str:
		if self.limit < 0 < self.offset:
			raise RuntimeError("Cannot specify an OFFSET without a LIMIT value")
		where = f"WHERE {self.condition}" if self.condition else None
		orders = join_sql_string(", ", *[(quote_sql_name(order[0]) + (" DESC" if order[1] else "")) if type(order) is tuple else quote_sql_name(order) for order in self.orders])
		limit = f"LIMIT {self.limit}" if self.limit >= 0 else None
		offset = f"OFFSET {self.offset}" if self.offset > 0 else None
		return join_sql_string(" ", where, orders, limit, offset)


class WhereOrderLimitOffsetWithExplicitConfirmationToOperateOverAllRows(WhereOrderLimitOffset):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.all_rows_confirm = False

	def all_rows(self: "U", confirm: bool = True) -> "U":
		self.all_rows_confirm = confirm
		return self

	def build_sql(self) -> str:
		if self.condition is None and not self.all_rows_confirm:
			raise RuntimeError("Cannot operate over all rows from table without explicit confirmation using .all_rows()")
		return super().build_sql()


class ConflictingQuery:
	def __init__(self, or_action: "OrAction" = None):
		self.conflict_action = or_action

	def or_action(self: "V", action: "OrAction") -> "V":
		self.conflict_action = action
		return self

	def or_abort(self: "V") -> "V":
		return self.or_action("ABORT")

	def or_fail(self: "V") -> "V":
		return self.or_action("FAIL")

	def or_ignore(self: "V") -> "V":
		return self.or_action("IGNORE")

	def or_replace(self: "V") -> "V":
		return self.or_action("REPLACE")

	def or_rollback(self: "V") -> "V":
		return self.or_action("ROLLBACK")


class ReturningQuery:
	def __init__(self, returning: list["AliasedSQL"] = None):
		self.returning = returning or []

	def returning_column(self: "W", column: "SQL", alias: str = None) -> "W":
		self.returning.append((column, alias) if alias else column)
		return self

	def returning_all(self: "W") -> "W":
		return self.returning_column(raw_sql("*"))
