#!/usr/bin/env python3
"""Mede o pico de alocações Python de uma execução de external_sort.

Uso:
    python3 medir_memoria.py entrada.csv saida.csv 5000
"""
from __future__ import annotations

import argparse
import tracemalloc

from extsort import external_sort


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entrada", help="CSV de entrada")
    parser.add_argument("saida", help="CSV de saída")
    parser.add_argument("buffer", type=int, help="máximo de registros por run")
    args = parser.parse_args()

    tracemalloc.start()
    try:
        stats = external_sort(
            args.entrada,
            "id",
            output_path=args.saida,
            buffer_records=args.buffer,
        )
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()

    print(stats)
    print(f"Pico de memória rastreada: {peak / 1e6:.2f} MB")
    print("Observação: tracemalloc não mede toda a RAM do processo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
