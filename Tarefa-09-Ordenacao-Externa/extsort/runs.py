"""Camada 1 do MergeSort externo: geração dos runs ordenados.

O arquivo de entrada é lido em blocos de no máximo buffer_records
registros. Cada bloco é ordenado em memória e gravado como um arquivo
temporário (um run), sem cabeçalho.
"""
from __future__ import annotations

import csv
from pathlib import Path

from .keys import KeyFunc, Row, validate_key


def _write_run(
    buffer: list[Row],
    run_dir: Path,
    run_number: int,
    key_func: KeyFunc,
    descending: bool,
    delimiter: str,
    encoding: str,
) -> Path:
    """Ordena o buffer em memória e grava como um run; devolve o caminho."""
    # list.sort é estável, inclusive com reverse=True.
    buffer.sort(key=key_func, reverse=descending)

    run_path = run_dir / f"run_{run_number:06d}.csv"
    with open(run_path, "w", newline="", encoding=encoding) as run_file:
        # Sem lineterminator personalizado: usa o padrão do csv.writer.
        csv.writer(run_file, delimiter=delimiter).writerows(buffer)
    return run_path


def generate_runs(
    input_path: Path,
    key_index: int,
    key_func: KeyFunc,
    descending: bool,
    buffer_records: int,
    run_dir: Path,
    delimiter: str = ",",
    encoding: str = "utf-8",
) -> tuple[list[Path], int]:
    """Divide o CSV em runs ordenados gravados em run_dir."""
    runs: list[Path] = []
    total_records = 0
    buffer: list[Row] = []

    with open(input_path, newline="", encoding=encoding) as input_file:
        reader = csv.reader(input_file, delimiter=delimiter)
        next(reader, None)  # pula o cabeçalho (o sorter já o leu)

        for row in reader:
            validate_key(row, key_index, key_func, reader.line_num)
            buffer.append(row)
            total_records += 1

            if len(buffer) == buffer_records:
                runs.append(
                    _write_run(
                        buffer, run_dir, len(runs), key_func, descending,
                        delimiter, encoding,
                    )
                )
                buffer.clear()

    if buffer:  # último run, possivelmente menor que o buffer
        runs.append(
            _write_run(
                buffer, run_dir, len(runs), key_func, descending,
                delimiter, encoding,
            )
        )

    return runs, total_records
