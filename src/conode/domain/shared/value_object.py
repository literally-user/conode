class ValueObject[Value_T]:
    value: Value_T

    def __init__(self, value: Value_T) -> None:
        self.value = value

    def __eq__(self, value: object) -> bool:
        return self.value == value

    def __hash__(self) -> int:
        return hash(self.value)
