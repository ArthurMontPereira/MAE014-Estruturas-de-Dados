#!/usr/bin/env python3
"""Gerador de CSV grande e reproduzível, para testar o MergeSort externo.

Uso:
    python3 generate_dataset.py --records 1000000 --output dados.csv --seed 42

Colunas: id,nome,curso,nota,linha_original.
O arquivo é escrito linha a linha; mesma seed e quantidade produzem o mesmo CSV.
"""
from __future__ import annotations

import argparse
import csv
import random
import sys
from pathlib import Path

HEADER = ["id", "nome", "curso", "nota", "linha_original"]
ID_DIGITS = 10
LCG_MODULUS = 2**32
LCG_MULTIPLIER = 1664525
MAX_RECORDS = LCG_MODULUS

FIRST_NAMES = [
    "Ana", "Bruno", "Carla", "Diego", "Elisa", "Felipe", "Gabriela", "Hugo",
    "Isabela", "João", "Karen", "Lucas", "Marina", "Nuno", "Olívia", "Pedro",
]
LAST_NAMES = [
    "Silva", "Santos", "Oliveira", "Souza", "Pereira", "Costa", "Rodrigues",
    "Almeida", "Nascimento", "Lima", "Araújo", "Ribeiro", "Carvalho", "Gomes",
]
COURSES = [
    "Matemática Aplicada", "Ciência da Computação", "Estatística",
    "Engenharia", "Física",
]


def generate_dataset(output_path: str | Path, records: int, seed: int) -> None:
    """Grava em output_path um CSV com records registros (e cabeçalho)."""
    if (
        isinstance(records, bool)
        or not isinstance(records, int)
        or not 1 <= records <= MAX_RECORDS
    ):
        raise ValueError(
            f"records deve ser um inteiro entre 1 e {MAX_RECORDS} (recebido: {records!r})"
        )

    rng = random.Random(seed)
    increment = rng.getrandbits(32) | 1
    state = rng.getrandbits(32)

    with open(output_path, "w", newline="", encoding="utf-8") as out_file:
        writer = csv.writer(out_file, lineterminator="\n")
        writer.writerow(HEADER)
        for line in range(1, records + 1):
            state = (LCG_MULTIPLIER * state + increment) % LCG_MODULUS
            writer.writerow([
                f"{state:0{ID_DIGITS}d}",
                f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}",
                rng.choice(COURSES),
                f"{rng.uniform(0, 10):.1f}",
                line,
            ])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="generate_dataset.py",
        description="Gera um CSV reproduzível para testar a ordenação externa.",
    )
    parser.add_argument("-n", "--records", type=int, default=100_000, metavar="N",
                        help="quantidade de registros (padrão: 100000)")
    parser.add_argument("-o", "--output", default="dataset.csv", metavar="SAIDA",
                        help="arquivo CSV a gerar (padrão: dataset.csv)")
    parser.add_argument("--seed", type=int, default=42,
                        help="semente do gerador aleatório (padrão: 42)")
    args = parser.parse_args(argv)

    try:
        generate_dataset(args.output, args.records, args.seed)
    except (ValueError, OSError) as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 1

    print(f"Gerado {args.output}: {args.records} registros (seed {args.seed}).")
    print(f"Chave: coluna 'id' ({ID_DIGITS} dígitos com zeros à esquerda; use key_type 'str').")
    return 0


if __name__ == "__main__":
    sys.exit(main())
