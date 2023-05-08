from abc import ABCMeta
from typing import TYPE_CHECKING

from .common import SQLElement
from .utils import quote_sql_name, join_sql_string

if TYPE_CHECKING:
	from .common import Column


class AlterAction(SQLElement, metaclass=ABCMeta):
	pass


class RenameTable(AlterAction):
	def __init__(self, new_name: str):
		super().__init__()
		self.new_name = new_name

	def build_sql(self) -> str:
		return f"RENAME TO {quote_sql_name(self.new_name)}"


class RenameColumn(AlterAction):
	def __init__(self, old_name: str, new_name: str):
		super().__init__()
		self.old_name = old_name
		self.new_name = new_name

	def build_sql(self) -> str:
		return f"RENAME COLUMN {quote_sql_name(self.old_name)} TO {quote_sql_name(self.new_name)}"


class AddColumn(AlterAction):
	def __init__(self, column: "Column"):
		super().__init__()
		self.column = column

	def build_sql(self) -> str:
		return f"ADD COLUMN {self.column}"


class DropColumn(AlterAction):
	def __init__(self, name: str):
		super().__init__()
		self.name = name

	def build_sql(self) -> str:
		return f"DROP COLUMN {quote_sql_name(self.name)}"


class AlterTable(SQLElement):
	def __init__(self, name: str, action: AlterAction = None):
		self.name = name
		self.action = action

	def with_action(self, action: AlterAction) -> "AlterTable":
		self.action = action
		return self

	def rename_table(self, new_table_name: str) -> "AlterTable":
		return self.with_action(RenameTable(new_table_name))

	def rename_column(self, old_column_name: str, new_column_name: str) -> "AlterTable":
		return self.with_action(RenameColumn(old_column_name, new_column_name))

	def add_column(self, new_column: "Column") -> "AlterTable":
		return self.with_action(AddColumn(new_column))

	def drop_column(self, column_name: str) -> "AlterTable":
		return self.with_action(DropColumn(column_name))

	def build_sql(self) -> str:
		if self.action is None:
			raise RuntimeError("Cannot perform an ALTER TABLE operation with no action specified!")
		return join_sql_string(" ", "ALTER TABLE", quote_sql_name(self.name), self.action)
