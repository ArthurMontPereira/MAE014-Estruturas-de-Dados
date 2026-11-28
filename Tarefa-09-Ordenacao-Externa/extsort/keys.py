"""Chave de ordenação: resolução da coluna e construção da função de chave.

Este módulo não faz E/S de arquivo: trabalha só com linhas já lidas, onde
cada linha é uma lista de strings (o que csv.reader devolve).
"""
from __future__ import annotations

from typing import Any, Callable

Row = list[str]
KeyFunc = Callable[[Row], Any]

CONVERTERS: dict[str, Callable[[str], Any]] = {
    "str": str,
    "int": int,
}


def resolve_key_index(header: Row, key_column: str | int) -> int:
    """Devolve a posição (0-based) da coluna da chave."""
    if isinstance(key_column, int):
        if not 0 <= key_column < len(header):
            raise ValueError(
                f"posição de coluna inválida: {key_column} "
                f"(o arquivo tem {len(header)} colunas, numeradas a partir de 0)"
            )
        return key_column

    matches = [i for i, name in enumerate(header) if name == key_column]
    if not matches:
        raise ValueError(f"coluna {key_column!r} não encontrada no cabeçalho: {header}")
    if len(matches) > 1:
        raise ValueError(f"o nome de coluna {key_column!r} aparece mais de uma vez no cabeçalho")
    return matches[0]


def check_key_type(key_type: str) -> None:
    """Levanta ValueError se key_type não for uma das chaves de CONVERTERS."""
    if key_type not in CONVERTERS:
        raise ValueError(
            f"key_type inválido: {key_type!r} (use um de {sorted(CONVERTERS)})"
        )


def make_key_func(key_index: int, key_type: str = "str") -> KeyFunc:
    """Cria a função que extrai e converte a chave de uma linha."""
    check_key_type(key_type)
    convert = CONVERTERS[key_type]

    def key_func(row: Row) -> Any:
        return convert(row[key_index])

    return key_func


def validate_key(row: Row, key_index: int, key_func: KeyFunc, line_num: int) -> None:
    """Confere se a linha tem chave utilizável; informa a linha em caso de erro."""
    if key_index >= len(row) or not row[key_index].strip():
        raise ValueError(f"linha {line_num}: chave ausente (coluna {key_index})")
    try:
        key_func(row)
    except ValueError as exc:
        raise ValueError(
            f"linha {line_num}: chave {row[key_index]!r} inválida para o tipo escolhido"
        ) from exc
