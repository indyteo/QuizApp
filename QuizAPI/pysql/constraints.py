from abc import ABCMeta, abstractmethod
from typing import final, Union

from .common import SQLElement
from .utils import quote_sql_name, join_sql_string


class Constraint(SQLElement, metaclass=ABCMeta):
	def __init__(self):
		self.name = None

	def with_name(self, name: str) -> "Constraint":
		self.name = name
		return self

	@final
	def build_sql(self) -> str:
		constraint = self.build_constraint()
		return constraint if self.name is None else f"CONSTRAINT {quote_sql_name(self.name)} {constraint}"

	@abstractmethod
	def build_constraint(self) -> str:
		raise NotImplementedError(f"The class {type(self).__name__} does not provide an implementation to build SQL")


class ColumnConstraint(Constraint, metaclass=ABCMeta):
	pass


class FlagConstraint(Constraint):
	def __init__(self, sql: str, value: bool = True):
		super().__init__()
		self.sql = sql
		self.value = value

	def build_constraint(self) -> str:
		return self.sql if self.value else None


class Primary(FlagConstraint, ColumnConstraint):
	def __init__(self, auto_increment: bool = False, desc: bool = False):
		super().__init__(join_sql_string(" ", "PRIMARY KEY", "DESC" if desc else None, "AUTOINCREMENT" if auto_increment else None))


class NotNull(FlagConstraint, ColumnConstraint):
	def __init__(self, value: bool = True):
		super().__init__("NOT NULL", value)


class Unique(FlagConstraint, ColumnConstraint):
	def __init__(self, value: bool = True):
		super().__init__("UNIQUE", value)


class Foreign(ColumnConstraint):
	def __init__(self, table: str, column: str):
		super().__init__()
		self.table = table
		self.column = column

	def build_constraint(self) -> str:
		return f"REFERENCES {quote_sql_name(self.table)} ({quote_sql_name(self.column)})"


class Default(ColumnConstraint):
	def __init__(self, expression: str):
		super().__init__()
		self.expression = expression

	def build_constraint(self) -> str:
		return f"DEFAULT ({self.expression})"


class TableConstraint(Constraint, metaclass=ABCMeta):
	pass


class Check(TableConstraint, ColumnConstraint):
	def __init__(self, expression: str):
		super().__init__()
		self.expression = expression

	def build_constraint(self) -> str:
		return f"CHECK ({self.expression})"


class KeyConstraint(Constraint):
	IndexedColumnType = Union[str, tuple[str, bool]]

	def __init__(self, key_type: str, *columns: IndexedColumnType):
		super().__init__()
		self.key_type = key_type
		self.columns = columns

	def get_raw_columns(self) -> list[str]:
		return [column if type(column) is str else column[0] for column in self.columns]

	def build_constraint(self) -> str:
		columns = join_sql_string(", ", *[quote_sql_name(column) if type(column) is str else (quote_sql_name(column[0]) + (" DESC" if column[1] else "")) for column in self.columns])
		return f"{self.key_type} ({columns})"


class PrimaryKey(KeyConstraint, TableConstraint):
	def __init__(self, *columns: KeyConstraint.IndexedColumnType):
		super().__init__("PRIMARY KEY", *columns)


class UniqueColumns(KeyConstraint, TableConstraint):
	def __init__(self, *columns: KeyConstraint.IndexedColumnType):
		super().__init__("UNIQUE", *columns)


class ForeignKey(KeyConstraint, TableConstraint):
	def __init__(self, table: str, columns: dict[str, str]):
		super().__init__("FOREIGN KEY", *columns.keys())
		self.table = table
		self.foreign_columns = columns.values()

	def build_constraint(self) -> str:
		foreign_columns = join_sql_string(", ", *self.foreign_columns)
		return f"{super().build_constraint()} REFERENCES {quote_sql_name(self.table)} ({foreign_columns})"
