"""MergeSort externo para arquivos CSV maiores que a memória disponível.

Requer Python 3.10 ou superior.
"""
from .sorter import SortStats, external_sort

__all__ = ["external_sort", "SortStats"]
