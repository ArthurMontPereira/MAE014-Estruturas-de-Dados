"""Testes da Tarefa 09 — sorting."""
from tests._support import *


class TestOrdenacao(ExternalSortTestCase):
    """Ordem crescente e decrescente; coluna pelo nome e pela posição."""

    KEYS = ["042", "007", "100", "001", "050", "099", "003"]

    def test_crescente_por_nome_da_coluna(self):
        rows = make_rows(self.KEYS)
        result = self.sort(rows, key="id", order="asc", buffer_records=2)
        self.assertEqual(result, [HEADER] + reference_sort(rows))

    def test_decrescente_por_nome_da_coluna(self):
        rows = make_rows(self.KEYS)
        result = self.sort(rows, key="id", order="desc", buffer_records=2)
        self.assertEqual(result, [HEADER] + reference_sort(rows, descending=True))

    def test_crescente_por_posicao_da_coluna(self):
        rows = make_rows(self.KEYS)
        result = self.sort(rows, key=0, order="asc", buffer_records=2)
        self.assertEqual(result, [HEADER] + reference_sort(rows))

    def test_decrescente_por_posicao_da_coluna(self):
        rows = make_rows(self.KEYS)
        result = self.sort(rows, key=0, order="desc", buffer_records=2)
        self.assertEqual(result, [HEADER] + reference_sort(rows, descending=True))

    def test_coluna_da_chave_nao_e_a_primeira(self):
        header = ["nome", "dre", "nota"]
        rows = [["Ana", "120", "9"], ["Bia", "003", "7"], ["Caio", "045", "8"], ["Duda", "999", "6"]]
        expected = [header] + reference_sort(rows, key_index=1)
        self.assertEqual(self.sort(rows, key="dre", header=header, buffer_records=2), expected)
        self.assertEqual(self.sort(rows, key=1, header=header, buffer_records=2), expected)

    def test_ordem_aceita_ascendente_e_descendente_por_extenso(self):
        rows = make_rows(self.KEYS)
        asc = self.sort(rows, order="ascendente", buffer_records=3)
        desc = self.sort(rows, order="descendente", buffer_records=3)
        self.assertEqual(asc, [HEADER] + reference_sort(rows))
        self.assertEqual(desc, [HEADER] + reference_sort(rows, descending=True))

    def test_dados_aleatorios_com_varios_buffers(self):
        rng = random.Random(2026)
        rows = make_rows([f"{rng.randrange(1000):04d}" for _ in range(200)])
        for buffer in (1, 2, 3, 7, 50, 200, 1000):
            for order in ("asc", "desc"):
                with self.subTest(buffer_records=buffer, order=order):
                    result = self.sort(rows, order=order, buffer_records=buffer)
                    expected = reference_sort(rows, descending=(order == "desc"))
                    self.assertEqual(result, [HEADER] + expected)


class TestTipoDaChave(ExternalSortTestCase):
    """key_type=str compara texto; key_type=int compara números."""

    def test_str_preserva_zeros_a_esquerda(self):
        rows = make_rows(["010", "002", "100", "001"])
        result = self.sort(rows, key_type="str", buffer_records=2)
        self.assertEqual([row[0] for row in result[1:]], ["001", "002", "010", "100"])

    def test_str_com_tamanhos_diferentes_compara_como_texto(self):
        rows = make_rows(["9", "10", "100", "2", "1"])
        result = self.sort(rows, key_type="str", buffer_records=2)
        self.assertEqual(result, [HEADER] + reference_sort(rows, convert=str))
        self.assertEqual([row[0] for row in result[1:]], ["1", "10", "100", "2", "9"])

    def test_int_com_tamanhos_diferentes_compara_como_numero(self):
        rows = make_rows(["9", "10", "100", "2", "1"])
        result = self.sort(rows, key_type="int", buffer_records=2)
        self.assertEqual(result, [HEADER] + reference_sort(rows, convert=int))
        self.assertEqual([row[0] for row in result[1:]], ["1", "2", "9", "10", "100"])

    def test_int_decrescente_com_tamanhos_diferentes(self):
        rows = make_rows(["9", "10", "100", "2", "1"])
        result = self.sort(rows, order="desc", key_type="int", buffer_records=2)
        self.assertEqual(result, [HEADER] + reference_sort(rows, descending=True, convert=int))
        self.assertEqual([row[0] for row in result[1:]], ["100", "10", "9", "2", "1"])

    def test_int_nao_altera_o_texto_da_chave(self):
        rows = make_rows(["007", "12", "0003"])
        result = self.sort(rows, key_type="int", buffer_records=1)
        self.assertEqual([row[0] for row in result[1:]], ["0003", "007", "12"])

    def test_int_com_empate_numerico_mantem_a_ordem_original(self):
        rows = make_rows(["7", "007", "07"])
        for order in ("asc", "desc"):
            with self.subTest(order=order):
                result = self.sort(rows, order=order, key_type="int", buffer_records=1)
                self.assertEqual([row[0] for row in result[1:]], ["7", "007", "07"])

    def test_key_type_invalido(self):
        self.write_input(make_rows(["1", "2"]))
        self.assert_rejected("key_type inválido", key_type="float")


class TestChavesDuplicadas(ExternalSortTestCase):
    """Chaves iguais devem manter a ordem original do arquivo."""

    KEYS = ["b", "a", "c", "a", "b", "a", "c", "b", "a", "b"]

    def assert_ties_keep_original_order(self, data_rows):
        for before, after in zip(data_rows, data_rows[1:]):
            if before[0] == after[0]:
                self.assertLess(int(before[2]), int(after[2]), f"empate fora de ordem: {before} {after}")

    def test_estabilidade_crescente(self):
        rows = make_rows(self.KEYS)
        for buffer in (1, 2, 3, 4, 100):
            with self.subTest(buffer_records=buffer):
                result = self.sort(rows, order="asc", buffer_records=buffer)
                self.assertEqual(result, [HEADER] + reference_sort(rows))
                self.assert_ties_keep_original_order(result[1:])

    def test_estabilidade_decrescente(self):
        rows = make_rows(self.KEYS)
        for buffer in (1, 2, 3, 4, 100):
            with self.subTest(buffer_records=buffer):
                result = self.sort(rows, order="desc", buffer_records=buffer)
                self.assertEqual(result, [HEADER] + reference_sort(rows, descending=True))
                self.assert_ties_keep_original_order(result[1:])

    def test_todas_as_chaves_iguais_mantem_a_ordem_do_arquivo(self):
        rows = make_rows(["x"] * 9)
        for order in ("asc", "desc"):
            with self.subTest(order=order):
                result = self.sort(rows, order=order, buffer_records=2)
                self.assertEqual(result, [HEADER] + rows)
