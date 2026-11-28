"""Testes de campos e arquivos CSV especiais."""
from tests._support import *


class TestCamposEspeciais(ExternalSortTestCase):
    """Vírgulas, aspas, quebras de linha, acentos e outro delimitador."""

    def test_virgulas_aspas_e_quebras_de_linha_fora_da_chave(self):
        rows = [
            ["003", "Silva, Ana", "0"],
            ["001", 'Dona "Maria"', "1"],
            ["002", "linha 1\nlinha 2", "2"],
            ["000", 'tudo: "a", b\nc', "3"],
            ["004", "", "4"],
        ]
        for buffer in (1, 2, 5):
            with self.subTest(buffer_records=buffer):
                result = self.sort(rows, buffer_records=buffer)
                self.assertEqual(result, [HEADER] + reference_sort(rows))

    def test_chave_com_virgula_aspas_e_quebra_de_linha(self):
        rows = make_rows(["a,b", 'a"b', "a\nb", "a b", "ab", "á"])
        for buffer in (1, 2, 6):
            with self.subTest(buffer_records=buffer):
                result = self.sort(rows, buffer_records=buffer)
                self.assertEqual(result, [HEADER] + reference_sort(rows))

    def test_acentos_e_caracteres_unicode(self):
        rows = make_rows(["Éder", "Ana", "Ângela", "Zélia", "日本"])
        result = self.sort(rows, buffer_records=2)
        self.assertEqual(result, [HEADER] + reference_sort(rows))

    def test_delimitador_ponto_e_virgula(self):
        rows = [["2", "a;b", "0"], ["1", "c,d", "1"], ["3", 'e"f', "2"]]
        result = self.sort(rows, delimiter=";", buffer_records=1)
        self.assertEqual(result, [HEADER] + reference_sort(rows))

    def test_retorno_de_carro_isolado_dentro_de_campo(self):
        self.input.write_bytes(b'id,nome,seq\r\n2,"a\rb",0\r\n1,"c\rd\re",1\r\n3,"f",2\r\n')
        rows = [["2", "a\rb", "0"], ["1", "c\rd\re", "1"], ["3", "f", "2"]]
        for key, key_index in (("id", 0), ("nome", 1)):
            for buffer in (1, 100):
                with self.subTest(key=key, buffer_records=buffer):
                    external_sort(self.input, key, output_path=self.output, buffer_records=buffer)
                    self.assertEqual(
                        read_csv(self.output), [HEADER] + reference_sort(rows, key_index=key_index)
                    )


class TestArquivosEspeciais(ExternalSortTestCase):
    """Arquivo vazio, só cabeçalho, um registro e fim de linha ausente."""

    def test_arquivo_vazio(self):
        self.input.write_bytes(b"")
        stats = external_sort(self.input, "id", output_path=self.output)
        self.assertEqual(self.output.read_bytes(), b"")
        self.assertEqual((stats.total_records, stats.num_runs, stats.merge_levels), (0, 0, 0))

    def test_arquivo_vazio_substitui_saida_existente(self):
        self.input.write_bytes(b"")
        self.output.write_text("conteúdo antigo")
        external_sort(self.input, "id", output_path=self.output)
        self.assertEqual(self.output.read_bytes(), b"")

    def test_arquivo_so_com_cabecalho(self):
        result = self.sort([])
        self.assertEqual(result, [HEADER])
        self.assertEqual((self.stats.total_records, self.stats.num_runs), (0, 0))

    def test_cabecalho_sem_quebra_de_linha_final(self):
        self.input.write_text("id,nome,seq")
        external_sort(self.input, "id", output_path=self.output)
        self.assertEqual(read_csv(self.output), [HEADER])

    def test_um_unico_registro(self):
        rows = make_rows(["042"])
        result = self.sort(rows, buffer_records=1)
        self.assertEqual(result, [HEADER] + rows)
        self.assertEqual(self.stats.num_runs, 1)

    def test_ultima_linha_sem_quebra_de_linha_final(self):
        self.input.write_text("id,nome,seq\n2,b,0\n1,a,1")
        external_sort(self.input, "id", output_path=self.output, buffer_records=1)
        self.assertEqual(read_csv(self.output), [HEADER, ["1", "a", "1"], ["2", "b", "0"]])

    def test_saida_padrao_fica_ao_lado_da_entrada(self):
        rows = make_rows(["b", "a", "c"])
        self.write_input(rows)
        external_sort(self.input, "id")
        default_output = self.dir / "entrada.sorted.csv"
        self.assertEqual(read_csv(default_output), [HEADER] + reference_sort(rows))
        self.assert_only_files(["entrada.csv", "entrada.sorted.csv"])

    def test_saida_existente_e_substituida(self):
        self.output.write_text("conteúdo antigo\n")
        rows = make_rows(["b", "a"])
        result = self.sort(rows)
        self.assertEqual(result, [HEADER] + reference_sort(rows))

    def test_key_type_invalido_e_rejeitado_mesmo_sem_registros(self):
        for content in (b"", b"id,nome,seq\n"):
            with self.subTest(conteudo=content):
                self.input.write_bytes(content)
                self.output.write_text("saída anterior", encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "key_type inválido"):
                    external_sort(self.input, "id", output_path=self.output, key_type="float")
                self.assertEqual(self.output.read_text(encoding="utf-8"), "saída anterior")
                self.assert_only_files(["entrada.csv", "saida.csv"])
