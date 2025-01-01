import pytest
from controllers import operation


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (1, 2, 3),
        (5, -4, 1),
        (7, 8, 15),
        (None, 2, None),
        (0, None, None),
        (None, None, None),
    ],
)
def test_operation(a: int | None, b: int | None, expected: int | None):
    received = operation(a, b)
    assert received == expected
