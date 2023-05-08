from typing import Iterable, TYPE_CHECKING

from .common import SQLElement
from .utils import quote_sql_name, join_sql_string

if TYPE_CHECKING:
	from .common import Column
	from .constraints import TableConstraint


class TableOption(SQLElement):
	def __init__(self, sql: str, value: bool = True):
		super().__init__()
		self.sql = sql
		self.value = value

	def build_sql(self) -> str:
		return self.sql if self.value else None


class WithoutRowID(TableOption):
	def __init__(self, value: bool = True):
		super().__init__("WITHOUT ROWID", value)


class Strict(TableOption):
	def __init__(self, value: bool = True):
		super().__init__("STRICT", value)


class CreateOptions:
	def __init__(self, if_not_exists: bool = False, temporary: bool = False):
		self.if_not_exists = if_not_exists
		self.temporary = temporary


class CreateTable(SQLElement):
	def __init__(self, name: str, columns: Iterable["Column"], constraints: Iterable["TableConstraint"], options: Iterable[TableOption], create_options: CreateOptions = None):
		self.name = name
		self.columns = columns
		self.constraints = constraints
		self.options = options
		self.create_options = create_options or CreateOptions()

	def with_create_options(self, create_options: CreateOptions) -> "CreateTable":
		self.create_options = create_options
		return self

	def if_not_exists(self, if_not_exists: bool = True) -> "CreateTable":
		self.create_options.if_not_exists = if_not_exists
		return self

	def temporary(self, temporary: bool = True) -> "CreateTable":
		self.create_options.temporary = temporary
		return self

	def build_sql(self) -> str:
		definition = join_sql_string(", ", *self.columns, *self.constraints)
		temp = "TEMPORARY" if self.create_options.temporary else None
		if_not_exists = "IF NOT EXISTS" if self.create_options.if_not_exists else None
		options = join_sql_string(", ", *self.options)
		return join_sql_string(" ", "CREATE", temp, "TABLE", if_not_exists, quote_sql_name(self.name), f"({definition})", options)
