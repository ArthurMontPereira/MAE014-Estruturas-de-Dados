"""Testes do MergeSort externo (somente biblioteca padrão).

Como executar (na pasta raiz do projeto):

    python3 -m unittest -v

Os testes de ordenação comparam a saída de external_sort() com uma ordenação
de referência feita em memória com sorted(). Todos usam arquivos pequenos:
testes de desempenho com milhões de registros ficam fora desta bateria.
"""
from __future__ import annotations

import contextlib
import csv
import io
import math
import os
import random
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import extsort.merge
import extsort.runs
import generate_dataset
import sort_csv
from extsort import external_sort

HEADER = ["id", "nome", "seq"]


def write_csv(path: Path, rows: list[list[str]], delimiter: str = ",") -> None:
    with open(path, "w", newline="", encoding="utf-8") as csv_file:
        csv.writer(csv_file, delimiter=delimiter, lineterminator="\n").writerows(rows)


def read_csv(path: Path, delimiter: str = ",") -> list[list[str]]:
    with open(path, newline="", encoding="utf-8") as csv_file:
        return list(csv.reader(csv_file, delimiter=delimiter))


def make_rows(keys: list[str]) -> list[list[str]]:
    """Cria registros [id, nome, seq]; seq é a posição original."""
    return [[key, f"nome{i}", str(i)] for i, key in enumerate(keys)]


def reference_sort(rows, key_index=0, descending=False, convert=str):
    """Ordenação de referência: sorted() em memória (estável)."""
    return sorted(rows, key=lambda row: convert(row[key_index]), reverse=descending)


class ExternalSortTestCase(unittest.TestCase):
    """Base: cada teste ganha uma pasta temporária própria e vazia."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)
        self.input = self.dir / "entrada.csv"
        self.output = self.dir / "saida.csv"
        self.stats = None

    def write_input(self, rows, header=HEADER, delimiter=","):
        write_csv(self.input, [header] + rows, delimiter)

    def sort(self, rows, key="id", order="asc", header=HEADER, **kwargs):
        delimiter = kwargs.get("delimiter", ",")
        self.write_input(rows, header, delimiter)
        self.stats = external_sort(self.input, key, order, output_path=self.output, **kwargs)
        return read_csv(self.output, delimiter)

    def assert_only_files(self, names):
        self.assertEqual(sorted(p.name for p in self.dir.iterdir()), sorted(names))

    def assert_rejected(self, regex, key="id", order="asc", **kwargs):
        with self.assertRaisesRegex(ValueError, regex):
            external_sort(self.input, key, order, output_path=self.output, **kwargs)
        self.assert_only_files(["entrada.csv"])
