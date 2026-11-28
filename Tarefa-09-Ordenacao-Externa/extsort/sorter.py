"""Orquestração do MergeSort externo: Camada 1 + Camada 2 + limpeza."""
from __future__ import annotations

import csv
import os
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

from .keys import Row, check_key_type, make_key_func, resolve_key_index
from .merge import merge_all_runs
from .runs import generate_runs

_ORDERS = {"asc": False, "ascendente": False, "desc": True, "descendente": True}


@dataclass
class SortStats:
    """Contadores simples de uma execução (úteis como evidência no relatório)."""

    total_records: int
    num_runs: int
    merge_levels: int
    runs_seconds: float
    merge_seconds: float
    total_seconds: float


def _parse_order(order: str) -> bool:
    """Converte a ordem em descending (True para descendente)."""
    try:
        return _ORDERS[order.lower()]
    except KeyError:
        raise ValueError(f"ordem inválida: {order!r} (use 'asc' ou 'desc')") from None


def _read_header(path: Path, delimiter: str, encoding: str) -> Row | None:
    """Lê só a primeira linha do CSV; devolve None se o arquivo estiver vazio."""
    with open(path, newline="", encoding=encoding) as csv_file:
        return next(csv.reader(csv_file, delimiter=delimiter), None)


def _create_temp_output(out_path: Path) -> Path:
    """Cria um arquivo temporário vazio, com nome exclusivo, na pasta da saída."""
    fd, name = tempfile.mkstemp(
        prefix=out_path.name + ".",
        suffix=".tmp",
        dir=out_path.parent,
    )
    os.close(fd)
    return Path(name)


def external_sort(
    filepath: str | Path,
    key_column: str | int,
    order: str = "asc",
    *,
    output_path: str | Path | None = None,
    buffer_records: int = 100_000,
    key_type: str = "str",
    delimiter: str = ",",
    encoding: str = "utf-8",
) -> SortStats:
    """Ordena um CSV grande por MergeSort externo, sem carregá-lo inteiro na RAM.

    Requer Python 3.10 ou superior. buffer_records limita registros, não bytes.
    A memória auxiliar total é O(M + R), pois a lista de caminhos dos runs
    também ocupa memória. A ordenação é estável.

    Temporários são removidos em erros e Ctrl+C. Encerramentos abruptos
    (SIGTERM, SIGKILL ou queda de energia) podem deixar arquivos residuais.
    """
    t_start = time.perf_counter()

    descending = _parse_order(order)
    if (
        isinstance(buffer_records, bool)
        or not isinstance(buffer_records, int)
        or buffer_records < 1
    ):
        raise ValueError(
            f"buffer_records deve ser um inteiro positivo (recebido: {buffer_records!r})"
        )
    check_key_type(key_type)

    input_path = Path(filepath)
    if output_path is None:
        out_path = input_path.with_name(f"{input_path.stem}.sorted{input_path.suffix}")
    else:
        out_path = Path(output_path)
    if out_path.resolve() == input_path.resolve():
        raise ValueError("o arquivo de saída não pode ser o mesmo arquivo de entrada")
    if out_path.is_dir():
        raise ValueError(f"o caminho de saída é uma pasta, não um arquivo: {out_path}")

    header = _read_header(input_path, delimiter, encoding)
    if header is not None:
        key_index = resolve_key_index(header, key_column)
        key_func = make_key_func(key_index, key_type)

    tmp_output: Path | None = None
    runs: list[Path] = []
    total_records = 0
    runs_seconds = merge_seconds = 0.0
    try:
        tmp_output = _create_temp_output(out_path)

        if header is not None:
            with tempfile.TemporaryDirectory(
                prefix="extsort_", dir=out_path.parent
            ) as tmp:
                run_dir = Path(tmp)

                start = time.perf_counter()
                runs, total_records = generate_runs(
                    input_path, key_index, key_func, descending,
                    buffer_records, run_dir, delimiter, encoding,
                )
                runs_done = time.perf_counter()

                merge_all_runs(
                    runs, tmp_output, header, key_func, descending,
                    run_dir, delimiter, encoding,
                )
                merge_done = time.perf_counter()

                runs_seconds = runs_done - start
                merge_seconds = merge_done - runs_done

        os.replace(tmp_output, out_path)
    finally:
        if tmp_output is not None:
            tmp_output.unlink(missing_ok=True)

    num_runs = len(runs)
    merge_levels = max(num_runs - 1, 0).bit_length()
    return SortStats(
        total_records=total_records,
        num_runs=num_runs,
        merge_levels=merge_levels,
        runs_seconds=runs_seconds,
        merge_seconds=merge_seconds,
        total_seconds=time.perf_counter() - t_start,
    )
