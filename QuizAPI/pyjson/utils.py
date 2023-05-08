from typing import Union, TYPE_CHECKING

if TYPE_CHECKING:
	from .json_types import Nullable

NoneType = type(None)
JsonFieldType = Union[type, list["NullableJsonFieldType"], dict[str, "NullableJsonFieldType"]]
NullableJsonFieldType = Union[JsonFieldType, "Nullable"]
JsonAliasedType = Union[NullableJsonFieldType, tuple[NullableJsonFieldType, str], tuple[str, NullableJsonFieldType]]
