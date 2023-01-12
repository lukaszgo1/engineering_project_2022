import enum


@enum.unique
class FieldSpecifiers(enum.Enum):

    ID_COLUMN = enum.auto()
    MAIN_FK_COLUMN = enum.auto()
