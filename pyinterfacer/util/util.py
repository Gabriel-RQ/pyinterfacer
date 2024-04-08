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
