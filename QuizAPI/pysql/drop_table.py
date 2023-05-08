from .common import SQLElement
from .utils import quote_sql_name, join_sql_string


class DropOptions:
	def __init__(self, if_exists: bool = False):
		self.if_exists = if_exists


class DropTable(SQLElement):
	def __init__(self, name: str, drop_options: DropOptions = None):
		self.name = name
		self.drop_options = drop_options or DropOptions()

	def with_drop_options(self, drop_options: DropOptions) -> "DropTable":
		self.drop_options = drop_options
		return self

	def if_exists(self, if_exists: bool = True) -> "DropTable":
		self.drop_options.if_exists = if_exists
		return self

	def build_sql(self) -> str:
		if_exists = "IF EXISTS" if self.drop_options.if_exists else None
		return join_sql_string(" ", "DROP TABLE", if_exists, quote_sql_name(self.name))
