import enum


@enum.unique
class WeekDay(enum.IntEnum):

    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

    def __str__(self) -> str:
        return {
            WeekDay.MONDAY: "Poniedziałek",
            WeekDay.TUESDAY: "Wtorek",
            WeekDay.WEDNESDAY: "Środa",
            WeekDay.THURSDAY: "Czwartek",
            WeekDay.FRIDAY: "Piątek",
            WeekDay.SATURDAY: "Sobota",
            WeekDay.SUNDAY: "Niedziela"
        }[self]
