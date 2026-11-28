"""Testes da Tarefa 09 — validação de chaves, parâmetros e buffer."""
from tests._support import *


class TestChavesAusentesEInvalidas(ExternalSortTestCase):
    """Chave ausente ou inválida deve gerar ValueError com o número da linha."""

    def test_campo_vazio_na_chave(self):
        self.write_input([["1", "a", "0"], ["", "b", "1"], ["3", "c", "2"]])
        self.assert_rejected(r"linha 3: chave ausente")

    def test_chave_so_com_espacos(self):
        self.write_input([["1", "a", "0"], ["   ", "b", "1"], ["3", "c", "2"]])
        self.assert_rejected(r"linha 3: chave ausente")

    def test_linha_curta_sem_a_coluna_da_chave(self):
        self.write_input([["1", "a", "0"], ["2"], ["3", "c", "2"]])
        self.assert_rejected(r"linha 3: chave ausente", key="nome")

    def test_chave_ausente_no_ultimo_registro(self):
        rows = make_rows(["1", "2", "3", "4"]) + [["", "x", "4"]]
        self.write_input(rows)
        self.assert_rejected(r"linha 6: chave ausente", buffer_records=2)

    def test_valor_invalido_para_inteiro(self):
        for bad in ("abc", "1.5", "12a", "1e3", "--5"):
            with self.subTest(valor=bad):
                self.write_input([["1", "a", "0"], [bad, "b", "1"]])
                self.assert_rejected(r"linha 3: chave .* inválida", key_type="int")

    def test_mesmo_valor_e_aceito_como_str(self):
        rows = make_rows(["abc", "1.5", "12a"])
        result = self.sort(rows, key_type="str")
        self.assertEqual(result, [HEADER] + reference_sort(rows))


class TestParametrosInvalidos(ExternalSortTestCase):
    """Coluna inexistente, posição inválida, ordem inválida etc."""

    def setUp(self):
        super().setUp()
        self.write_input(make_rows(["3", "1", "2"]))

    def test_coluna_inexistente(self):
        self.assert_rejected("não encontrada", key="nao_existe")

    def test_posicao_fora_do_intervalo(self):
        for position in (3, 99):
            with self.subTest(posicao=position):
                self.assert_rejected("posição de coluna inválida", key=position)

    def test_posicao_negativa(self):
        self.assert_rejected("posição de coluna inválida", key=-1)

    def test_nome_de_coluna_repetido_no_cabecalho(self):
        write_csv(self.input, [["a", "a"], ["1", "2"]])
        self.assert_rejected("mais de uma vez", key="a")

    def test_ordem_invalida(self):
        self.assert_rejected("ordem inválida", order="crescente")

    def test_saida_igual_a_entrada(self):
        with self.assertRaisesRegex(ValueError, "mesmo arquivo"):
            external_sort(self.input, "id", output_path=self.input)
        self.assert_only_files(["entrada.csv"])

    def test_arquivo_de_entrada_inexistente(self):
        with self.assertRaises(FileNotFoundError):
            external_sort(self.dir / "nao_existe.csv", "id", output_path=self.output)
        self.assert_only_files(["entrada.csv"])

    def test_saida_que_e_uma_pasta_falha_antes_de_ordenar(self):
        pasta = self.dir / "resultados"
        pasta.mkdir()
        with mock.patch("extsort.sorter.generate_runs") as generate_runs:
            with self.assertRaisesRegex(ValueError, "é uma pasta"):
                external_sort(self.input, "id", output_path=pasta)
        generate_runs.assert_not_called()
        self.assert_only_files(["entrada.csv", "resultados"])
        self.assertEqual(list(pasta.iterdir()), [])


class TestBuffer(ExternalSortTestCase):
    """Buffers pequenos, contagem de runs e validação dos limites."""

    KEYS = ["g", "c", "a", "f", "b", "e", "d", "j", "h", "i"]

    def test_buffer_de_1_2_e_3_registros(self):
        rows = make_rows(self.KEYS)
        for buffer in (1, 2, 3):
            for order in ("asc", "desc"):
                with self.subTest(buffer_records=buffer, order=order):
                    result = self.sort(rows, order=order, buffer_records=buffer)
                    expected = reference_sort(rows, descending=(order == "desc"))
                    self.assertEqual(result, [HEADER] + expected)
                    self.assertEqual(self.stats.num_runs, math.ceil(len(rows) / buffer))

    def test_numero_de_runs_e_niveis_de_merge(self):
        rows = make_rows(self.KEYS)
        cases = [(1, 10, 4), (2, 5, 3), (3, 4, 2), (5, 2, 1), (10, 1, 0), (50, 1, 0)]
        for buffer, runs, levels in cases:
            with self.subTest(buffer_records=buffer):
                self.sort(rows, buffer_records=buffer)
                self.assertEqual(self.stats.total_records, 10)
                self.assertEqual(self.stats.num_runs, runs)
                self.assertEqual(self.stats.merge_levels, levels)

    def test_buffer_maior_que_o_arquivo_gera_um_unico_run(self):
        rows = make_rows(self.KEYS)
        result = self.sort(rows, buffer_records=1_000_000)
        self.assertEqual(result, [HEADER] + reference_sort(rows))
        self.assertEqual(self.stats.num_runs, 1)

    def test_buffer_invalido_e_rejeitado(self):
        self.write_input(make_rows(self.KEYS))
        for bad in (0, -1, 1.5, 2.0, True, False, "3", None):
            with self.subTest(buffer_records=bad):
                self.assert_rejected("inteiro positivo", buffer_records=bad)

    def test_tempos_das_estatisticas(self):
        self.sort(make_rows(self.KEYS), buffer_records=2)
        stats = self.stats
        self.assertGreater(stats.total_seconds, 0)
        self.assertGreaterEqual(stats.total_seconds, stats.runs_seconds + stats.merge_seconds)
