from threading import Lock
from collections import Counter
from sqlite3 import connect, sqlite_version_info
from typing import Union, Iterable, TYPE_CHECKING, TypeVar, Protocol

from .common import Column
from .constraints import PrimaryKey, TableConstraint, Primary
from .create_table import CreateTable, TableOption, WithoutRowID
from .alter_table import AlterTable
from .drop_table import DropTable
from .select import Select
from .insert import Insert
from .update import Update
from .delete import Delete
from .utils import flatten, filter_type, join_sql_string, quote_sql_name, placeholder

if TYPE_CHECKING:
	from sqlite3 import Cursor
	from .create_table import CreateOptions
	from .alter_table import AlterAction
	from .drop_table import DropOptions

T = TypeVar("T", bound="DatabaseModel")

does_sqlite3_supports_returning_clause = sqlite_version_info[1] >= 35


class Table:
	def __init__(self, python_class: type, name: str, columns: Iterable[Column], constraints: Iterable[TableConstraint], options: Iterable[TableOption]):
		self.python_class = python_class
		self.name = name
		self.columns = {column.sql_name: column for column in columns}
		self.constraints = constraints
		self.options = options
		self.computed_ids = None

	def get_column(self, sql_name: str) -> Column:
		return self.columns[sql_name]

	def get_column_from_python_name(self, python_name: str) -> Column:
		for column in self.columns.values():
			if column.python_name == python_name:
				return column
		raise KeyError(f"No column with python name {python_name} in table {self.name}")

	def get_ids(self) -> list[str]:
		if self.computed_ids is not None:
			return self.computed_ids
		self.computed_ids = flatten([primary_key.get_raw_columns() for primary_key in filter_type(self.constraints, PrimaryKey)]) + [name for name, column in self.columns.items() if list(filter_type(column.column_constraints, Primary))]
		return self.computed_ids

	def get_ids_condition(self) -> str:
		return join_sql_string(" AND ", *self.get_ids(), str_transform=lambda col: quote_sql_name(col) + " = " + placeholder(col))

	def create(self, create_options: "CreateOptions" = None) -> CreateTable:
		return CreateTable(self.name, self.columns.values(), self.constraints, self.options, create_options)

	def alter(self, alter_action: "AlterAction" = None) -> AlterTable:
		return AlterTable(self.name, alter_action)

	def drop(self, drop_options: "DropOptions" = None) -> DropTable:
		return DropTable(self.name, drop_options)

	def select(self, where_id: bool = False):
		select = Select().from_table(self.name)
		for column in self.columns.values():
			select.column(column.sql_name)
		if where_id:
			select.where(self.get_ids_condition())
		return select

	def insert(self, *use_default_for: str):
		insert = Insert(self.name)
		for column in self.columns.values():
			if column.python_name in use_default_for:
				if does_sqlite3_supports_returning_clause:
					insert.returning_column(column.sql_name)
			else:
				insert.value(column.sql_name, placeholder(column.sql_name))
		return insert

	def update(self):
		ids = self.get_ids()
		update = Update(self.name).where(self.get_ids_condition())
		for column in self.columns.values():
			if column.sql_name not in ids:
				update.set(column.sql_name, placeholder(column.sql_name))
		return update

	def delete(self, where_id: bool = True):
		delete = Delete(self.name)
		return delete.where(self.get_ids_condition()) if where_id else delete


def bind_new(table: Table, cur: "Cursor", row: tuple):
	# noinspection PyArgumentList
	return bind_object(table, cur, row, table.python_class.__new__(table.python_class))


def bind_object(table: Table, cur: "Cursor", row: tuple, obj):
	columns = [table.get_column(column[0]) for column in cur.description]
	for i in range(len(columns)):
		column = columns[i]
		obj.__dict__[column.python_name] = None if row[i] is None else column.type_(row[i])
	return obj


class Database:
	def __init__(self, file: str = "database.db", auto_create_tables: bool = False, table_create_options: "CreateOptions" = None, debug: bool = False):
		self.file = file
		self.connection = connect(file, isolation_level=None, check_same_thread=False)
		self.tables: dict[str, Table] = {}
		self.auto_create_tables = auto_create_tables
		self.table_create_options = table_create_options
		self.debug = debug
		self._sql_execution_lock = Lock()
		self.execute("PRAGMA encoding=utf8")

	def execute(self, sql: str, **parameters):
		with self._sql_execution_lock:
			if self.debug:
				print(f"SQL: {sql}")
				for param, value in parameters.items():
					if isinstance(value, str):
						value = value.encode("UTF-8")
					print(f"\t{param}: {value}")
			return self.connection.execute(sql, parameters)

	def fetch_one(self, table: Table, sql: str, **parameters):
		cur = self.execute(sql, **parameters)
		row = cur.fetchone()
		obj = None if row is None else bind_new(table, cur, row)
		cur.close()
		return obj

	def fetch_many(self, table: Table, sql: str, **parameters) -> list:
		cur = self.execute(sql, **parameters)
		rows = cur.fetchall()
		objects = [bind_new(table, cur, row) for row in rows]
		cur.close()
		return objects

	def register_table(self, table: Table):
		self.tables[table.name] = table
		if self.auto_create_tables:
			self.execute(table.create().if_not_exists().build_sql()).close()

	def get_table(self, name: Union[str, type]) -> Table:
		if type(name) is str:
			return self.tables[name]
		for table in self.tables.values():
			if table.python_class == name:
				return table
		raise KeyError(f"No table definition for class: {name.__name__}")

	def model(self, table: str = None, *definition: Union[Column, TableConstraint, TableOption]):
		columns = filter_type(definition, Column)
		constraints = filter_type(definition, TableConstraint)
		options = filter_type(definition, TableOption)

		# noinspection PyPep8Naming
		# The decorator is applied to classes, thus the argument is in fact a class
		def decorator(BaseClass: type[T]) -> type[T]:
			name = table or str(BaseClass.__name__)
			db_table = Table(BaseClass, name, columns, constraints, options)
			self.register_table(db_table)

			def add(this: BaseClass, *use_default_for: str) -> bool:
				values = {col.sql_name: this.__dict__[col.python_name] for col in db_table.columns.values() if col.python_name not in use_default_for}
				cur = self.execute(db_table.insert(*use_default_for).build_sql(), **values)
				result = cur.rowcount == 1
				if not does_sqlite3_supports_returning_clause:
					if list(filter_type(db_table.options, WithoutRowID)):
						cur.close()
						return result
					inserted_rowid = cur.lastrowid
					cur.close()
					inserted_values_query = Select().from_table(db_table.name)
					for col in db_table.columns.values():
						if col.python_name in use_default_for:
							inserted_values_query.column(col.sql_name)
					inserted_values_query.where(f"_rowid_ = {inserted_rowid}")
					cur = self.execute(inserted_values_query.build_sql())
				inserted = cur.fetchone()
				if inserted is not None:
					bind_object(db_table, cur, inserted, this)
				cur.close()
				return result

			def save(this: BaseClass) -> bool:
				values = {col.sql_name: this.__dict__[col.python_name] for col in db_table.columns.values()}
				cur = self.execute(db_table.update().build_sql(), **values)
				result = cur.rowcount == 1
				cur.close()
				return result

			def delete(this: BaseClass) -> bool:
				id_columns = [db_table.get_column(table_id) for table_id in db_table.get_ids()]
				ids = {col.sql_name: this.__dict__[col.python_name] for col in id_columns}
				cur = self.execute(db_table.delete().build_sql(), **ids)
				result = cur.rowcount == 1
				cur.close()
				return result

			def list_(condition: str = None, order_by: str = None, **parameters) -> list[BaseClass]:
				select = db_table.select().where(condition)
				if order_by:
					select.order_by(order_by)
				return self.fetch_many(db_table, select.build_sql(), **parameters)

			def count(condition: str = None, **parameters) -> int:
				cur = self.execute(Select().value("count(*)").from_table(db_table.name).where(condition).build_sql(), **parameters)
				row = cur.fetchone()
				total = row[0] if row else 0
				cur.close()
				return total

			def get(**ids) -> BaseClass:
				table_ids = db_table.get_ids()
				sql_ids = [db_table.get_column_from_python_name(python_id).sql_name for python_id in ids.keys()]
				if Counter(table_ids) != Counter(sql_ids):
					raise RuntimeError("Cannot get object without matching id")
				ids = {db_table.get_column_from_python_name(python_id).sql_name: value for python_id, value in ids.items()}
				return self.fetch_one(db_table, db_table.select(True).build_sql(), **ids)

			setattr(BaseClass, "__database__", self)
			setattr(BaseClass, "__table__", db_table)
			setattr(BaseClass, "add", add)
			setattr(BaseClass, "save", save)
			setattr(BaseClass, "delete", delete)
			setattr(BaseClass, "list", staticmethod(list_))
			setattr(BaseClass, "count", staticmethod(count))
			setattr(BaseClass, "get", staticmethod(get))
			return BaseClass

		return decorator

	def close(self):
		self.connection.close()

	def __del__(self):
		self.close()


class DatabaseModel(Protocol):
	__database__: Database
	__table__: Table
	def add(self: T, *use_default_for: str) -> bool: ...
	def save(self: T) -> bool: ...
	def delete(self: T) -> bool: ...
	@classmethod
	def list(cls: type[T], condition: str = None, order_by: str = None, **parameters) -> list[T]: ...
	@staticmethod
	def count(condition: str = None, **parameters) -> int: ...
	@classmethod
	def get(cls: type[T], **ids) -> T: ...
