#!/usr/bin/env python3
"""Gerador de CSV grande e reproduzível, para testar o MergeSort externo.

Uso:
    python3 generate_dataset.py --records 1000000 --output dados.csv --seed 42

Colunas geradas: id,nome,curso,nota,linha_original
  id              chave única com 10 dígitos e zeros à esquerda (ex.: 0123456789),
                  própria para key_type="str" (o padrão).
  curso           poucos valores repetidos: serve de chave com duplicatas.
  linha_original  posição do registro no arquivo gerado (1, 2, 3...); permite
                  conferir a estabilidade depois de ordenar por "curso".

O arquivo é escrito linha a linha, então a memória usada não depende de
--records. Mesma seed e mesma quantidade de registros geram o mesmo arquivo.
"""
from __future__ import annotations

import argparse
import csv
import random
import sys
from pathlib import Path

HEADER = ["id", "nome", "curso", "nota", "linha_original"]
ID_DIGITS = 10

# Os IDs vêm de um gerador congruencial linear x -> (a*x + c) mod 2^32.
# Com c ímpar e a ≡ 1 (mod 4) (teorema de Hull-Dobell) ele passa por todos os
# valores de 0 a 2^32 - 1 exatamente uma vez antes de repetir. Assim os IDs são
# únicos, saem fora de ordem e não precisamos guardá-los na memória.
# O maior valor (4294967295) tem 10 dígitos, por isso ID_DIGITS = 10.
LCG_MODULUS = 2**32
LCG_MULTIPLIER = 1664525
MAX_RECORDS = LCG_MODULUS

FIRST_NAMES = ["Ana", "Bruno", "Carla", "Diego", "Elisa", "Felipe", "Gabriela", "Hugo",
               "Isabela", "João", "Karen", "Lucas", "Marina", "Nuno", "Olívia", "Pedro"]
LAST_NAMES = ["Silva", "Santos", "Oliveira", "Souza", "Pereira", "Costa", "Rodrigues",
              "Almeida", "Nascimento", "Lima", "Araújo", "Ribeiro", "Carvalho", "Gomes"]
COURSES = ["Matemática Aplicada", "Ciência da Computação", "Estatística",
           "Engenharia", "Física"]


def generate_dataset(output_path: str | Path, records: int, seed: int) -> None:
    """Grava em output_path um CSV com records registros (e cabeçalho)."""
    # bool é subclasse de int, então precisa ser rejeitado à parte. A validação
    # vem antes de abrir o arquivo, para que um valor inválido não deixe um
    # arquivo incompleto.
    if (
        isinstance(records, bool)
        or not isinstance(records, int)
        or not 1 <= records <= MAX_RECORDS
    ):
        raise ValueError(
            f"records deve ser um inteiro entre 1 e {MAX_RECORDS} (recebido: {records!r})"
        )

    rng = random.Random(seed)
    increment = rng.getrandbits(32) | 1  # c ímpar
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
        description="Gera um CSV reproduzível (id com zeros à esquerda) para testar a ordenação externa.",
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
