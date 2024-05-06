"""
@author: Gabriel RQ
@description: Common utilities used in the library.
"""


def percent_to_float(p: str) -> float:
    """
    Converts a percentage string (e.g. "100%") to it's float value.

    :param p: Percentage string.
    """

    return float(p.strip(" %")) / 100


# Source: https://stackoverflow.com/questions/6760685/what-is-the-best-way-of-implementing-singleton-in-python
class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
