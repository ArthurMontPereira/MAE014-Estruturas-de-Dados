#!/usr/bin/env python3
"""Linha de comando do MergeSort externo para arquivos CSV."""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from extsort import external_sort


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sort_csv.py",
        description=(
            "Ordena um arquivo CSV grande por MergeSort externo, "
            "sem carregá-lo inteiro na memória."
        ),
        epilog="Exemplo: python3 sort_csv.py alunos.csv --key dre --order desc -o alunos_ordenado.csv",
    )
    parser.add_argument(
        "input", metavar="ENTRADA",
        help="arquivo CSV de entrada (a primeira linha deve ser o cabeçalho)",
    )
    parser.add_argument(
        "-k", "--key", required=True, metavar="COLUNA",
        help="coluna da chave: o nome dela no cabeçalho ou a posição (0 = primeira)",
    )
    parser.add_argument(
        "--order", choices=["asc", "desc", "ascendente", "descendente"], default="asc",
        metavar="ORDEM", help="asc (ou ascendente) ou desc (ou descendente); padrão: asc",
    )
    parser.add_argument(
        "-o", "--output", metavar="SAIDA",
        help="arquivo de saída (padrão: <nome>.sorted<extensão> ao lado da entrada)",
    )
    parser.add_argument(
        "-b", "--buffer", type=int, default=100_000, metavar="N",
        help="máximo de registros em memória por run (padrão: 100000)",
    )
    parser.add_argument(
        "--key-type", choices=["str", "int"], default="str",
        help="como comparar a chave: 'str' (texto, padrão) ou 'int' (número)",
    )
    parser.add_argument(
        "-d", "--delimiter", default=",", metavar="CHAR",
        help="separador de campos, com 1 caractere (padrão: ',')",
    )
    parser.add_argument(
        "--encoding", default="utf-8",
        help="codificação do arquivo (padrão: utf-8; outras: latin-1, utf-8-sig)",
    )
    return parser


def parse_key_column(
    key: str, input_path: Path, delimiter: str, encoding: str
) -> str | int:
    """Decide se --key é nome de coluna ou posição."""
    with open(input_path, newline="", encoding=encoding) as csv_file:
        header = next(csv.reader(csv_file, delimiter=delimiter), [])
    if key in header or not key.isdecimal():
        return key
    return int(key)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    if not input_path.is_file():
        parser.error(f"arquivo de entrada não encontrado: {input_path}")
    if len(args.delimiter) != 1:
        parser.error("--delimiter deve ter exatamente 1 caractere (ex.: ',' ou ';')")

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_name(
            f"{input_path.stem}.sorted{input_path.suffix}"
        )

    try:
        key_column = parse_key_column(
            args.key, input_path, args.delimiter, args.encoding
        )
        stats = external_sort(
            input_path, key_column, args.order,
            output_path=output_path,
            buffer_records=args.buffer,
            key_type=args.key_type,
            delimiter=args.delimiter,
            encoding=args.encoding,
        )
    except UnicodeDecodeError:
        print(
            f"erro: não foi possível ler o arquivo com a codificação {args.encoding!r}. "
            "Tente --encoding latin-1 ou --encoding utf-8-sig.",
            file=sys.stderr,
        )
        return 1
    except (ValueError, OSError, LookupError, csv.Error) as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 1

    print(
        f"Ordenação concluída: {stats.total_records} registros, "
        f"{stats.num_runs} runs, {stats.merge_levels} níveis de merge."
    )
    print(
        f"Tempos: runs {stats.runs_seconds:.2f}s | merge {stats.merge_seconds:.2f}s "
        f"| total {stats.total_seconds:.2f}s"
    )
    print(f"Saída: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
