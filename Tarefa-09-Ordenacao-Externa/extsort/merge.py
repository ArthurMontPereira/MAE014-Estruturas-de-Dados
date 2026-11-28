"""Camada 2 do MergeSort externo: merge dos runs em disco.

Os runs são combinados de dois em dois, de forma recursiva (divisão e
conquista). Durante cada merge os registros são lidos e gravados em
streaming: só os dois registros "cabeça" ficam em memória.
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, Iterator

from .keys import KeyFunc, Row


def _write_csv(
    path: Path,
    rows: Iterable[Row],
    delimiter: str,
    encoding: str,
    header: Row | None = None,
) -> None:
    """Grava rows em path (com cabeçalho, se informado), em streaming."""
    with open(path, "w", newline="", encoding=encoding) as out_file:
        # Terminador de linha padrão do módulo csv (CRLF). Com ele o writer
        # coloca aspas em campos que contêm CR ou LF, inclusive no Python 3.10.
        # Com lineterminator="\n", o Python 3.10 podia gravar um CR solto
        # sem aspas, e ao reler o arquivo o registro era partido.
        writer = csv.writer(out_file, delimiter=delimiter)
        if header is not None:
            writer.writerow(header)
        writer.writerows(rows)


def merge_two_sorted(
    left: Iterator[Row],
    right: Iterator[Row],
    key_func: KeyFunc,
    descending: bool,
) -> Iterator[Row]:
    """Merge de dois fluxos já ordenados (o Merge do MergeSort).

    É um gerador: produz um registro por vez, sem montar listas.
    Em caso de empate de chaves sai primeiro o registro de left, mantendo
    a ordenação estável.
    """
    left_row = next(left, None)
    right_row = next(right, None)

    while left_row is not None and right_row is not None:
        left_key = key_func(left_row)
        right_key = key_func(right_row)
        take_left = left_key >= right_key if descending else left_key <= right_key

        if take_left:
            yield left_row
            left_row = next(left, None)
        else:
            yield right_row
            right_row = next(right, None)

    if left_row is not None:
        yield left_row
        yield from left
    if right_row is not None:
        yield right_row
        yield from right


def merge_files(
    left_path: Path,
    right_path: Path,
    out_path: Path,
    key_func: KeyFunc,
    descending: bool,
    delimiter: str = ",",
    encoding: str = "utf-8",
    header: Row | None = None,
) -> None:
    """Faz o merge de dois runs ordenados e grava um novo run."""
    with (
        open(left_path, newline="", encoding=encoding) as left_file,
        open(right_path, newline="", encoding=encoding) as right_file,
    ):
        merged = merge_two_sorted(
            csv.reader(left_file, delimiter=delimiter),
            csv.reader(right_file, delimiter=delimiter),
            key_func,
            descending,
        )
        _write_csv(out_path, merged, delimiter, encoding, header)


def merge_all_runs(
    runs: list[Path],
    out_path: Path,
    header: Row,
    key_func: KeyFunc,
    descending: bool,
    run_dir: Path,
    delimiter: str = ",",
    encoding: str = "utf-8",
) -> None:
    """Combina todos os runs em out_path (cabeçalho + registros ordenados).

    Os arquivos de entrada de cada merge são apagados logo após o merge,
    para limitar o uso de disco. Só o merge final escreve o cabeçalho.
    """
    if not runs:  # arquivo só com cabeçalho
        _write_csv(out_path, [], delimiter, encoding, header)
        return

    if len(runs) == 1:  # nada para juntar: só acrescenta o cabeçalho
        with open(runs[0], newline="", encoding=encoding) as run_file:
            _write_csv(out_path, csv.reader(run_file, delimiter=delimiter), delimiter, encoding, header)
        runs[0].unlink()
        return

    def merge_range(lo: int, hi: int) -> Path:
        """Junta runs[lo:hi] em um único run e devolve o caminho dele."""
        if hi - lo == 1:  # caso base: um run já está ordenado
            return runs[lo]

        mid = (lo + hi) // 2
        left = merge_range(lo, mid)
        right = merge_range(mid, hi)

        is_root = lo == 0 and hi == len(runs)
        target = out_path if is_root else run_dir / f"merge_{lo:06d}_{hi:06d}.csv"
        merge_files(
            left, right, target, key_func, descending, delimiter, encoding,
            header if is_root else None,
        )
        left.unlink()
        right.unlink()
        return target

    merge_range(0, len(runs))
