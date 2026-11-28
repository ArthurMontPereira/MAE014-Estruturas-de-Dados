"""Testes de limpeza e segurança de arquivos temporários."""
from tests._support import *


class TestLimpezaDeTemporarios(ExternalSortTestCase):
    """Runs e temporários devem sumir após sucesso e após exceção."""

    def test_apos_execucao_normal_com_muitos_runs(self):
        self.sort(make_rows([f"{i:03d}" for i in range(10, 0, -1)]), buffer_records=1)
        self.assertEqual(self.stats.num_runs, 10)
        self.assert_only_files(["entrada.csv", "saida.csv"])

    def test_apos_execucao_normal_com_um_unico_run(self):
        self.sort(make_rows(["b", "a"]), buffer_records=100)
        self.assert_only_files(["entrada.csv", "saida.csv"])

    def test_apos_arquivo_vazio_e_arquivo_so_com_cabecalho(self):
        self.input.write_bytes(b"")
        external_sort(self.input, "id", output_path=self.output)
        self.assert_only_files(["entrada.csv", "saida.csv"])
        self.sort([])
        self.assert_only_files(["entrada.csv", "saida.csv"])

    def test_apos_erro_na_camada_1_com_runs_ja_gravados(self):
        rows = make_rows([f"{i:03d}" for i in range(40, 0, -1)]) + [["", "x", "40"]]
        self.write_input(rows)
        real_write_run = extsort.runs._write_run
        written = []
        def spy(*args, **kwargs):
            path = real_write_run(*args, **kwargs)
            written.append(path)
            return path
        with mock.patch("extsort.runs._write_run", side_effect=spy):
            with self.assertRaisesRegex(ValueError, "chave ausente"):
                external_sort(self.input, "id", output_path=self.output, buffer_records=5)
        self.assertEqual(len(written), 8)
        self.assert_only_files(["entrada.csv"])

    def test_apos_erro_no_meio_do_merge(self):
        self.write_input(make_rows([f"{i:03d}" for i in range(20, 0, -1)]))
        real_merge_files = extsort.merge.merge_files
        calls = []
        def fails_on_third_call(*args, **kwargs):
            calls.append(1)
            if len(calls) == 3:
                raise OSError("disco cheio (simulado)")
            return real_merge_files(*args, **kwargs)
        with mock.patch("extsort.merge.merge_files", side_effect=fails_on_third_call):
            with self.assertRaisesRegex(OSError, "disco cheio"):
                external_sort(self.input, "id", output_path=self.output, buffer_records=2)
        self.assertEqual(len(calls), 3)
        self.assert_only_files(["entrada.csv"])

    def test_apos_erro_no_os_replace_final(self):
        self.write_input(make_rows(["b", "a", "c"]))
        with mock.patch("os.replace", side_effect=OSError("falha simulada")):
            with self.assertRaisesRegex(OSError, "falha simulada"):
                external_sort(self.input, "id", output_path=self.output, buffer_records=1)
        self.assert_only_files(["entrada.csv"])

    def test_arquivo_vazio_tambem_usa_tmp_e_os_replace(self):
        self.input.write_bytes(b"")
        self.output.write_text("saída antiga")
        with mock.patch("os.replace", side_effect=OSError("falha simulada")):
            with self.assertRaises(OSError):
                external_sort(self.input, "id", output_path=self.output)
        self.assertEqual(self.output.read_text(), "saída antiga")
        self.assert_only_files(["entrada.csv", "saida.csv"])


class TestArquivoTemporarioDeSaida(ExternalSortTestCase):
    """O temporário da saída tem nome exclusivo e não pisa em arquivos existentes."""

    KEYS = ["b", "a", "c", "a"]

    def test_entrada_chamada_dados_csv_tmp_continua_intacta(self):
        rows = make_rows(self.KEYS)
        entrada = self.dir / "dados.csv.tmp"
        saida = self.dir / "dados.csv"
        write_csv(entrada, [HEADER] + rows)
        original = entrada.read_bytes()
        external_sort(entrada, "id", output_path=saida, buffer_records=2)
        self.assertTrue(entrada.exists())
        self.assertEqual(entrada.read_bytes(), original)
        self.assertEqual(read_csv(saida), [HEADER] + reference_sort(rows))
        self.assert_only_files(["dados.csv.tmp", "dados.csv"])

    def test_saida_ponto_tmp_preexistente_continua_intacta(self):
        rows = make_rows(self.KEYS)
        preexistente = self.dir / "saida.csv.tmp"
        preexistente.write_text("conteúdo que não é do programa\n", encoding="utf-8")
        result = self.sort(rows, buffer_records=2)
        self.assertEqual(result, [HEADER] + reference_sort(rows))
        self.assertEqual(preexistente.read_text(encoding="utf-8"), "conteúdo que não é do programa\n")
        self.assert_only_files(["entrada.csv", "saida.csv", "saida.csv.tmp"])

    def test_saida_ponto_tmp_preexistente_continua_intacta_com_arquivo_vazio(self):
        preexistente = self.dir / "saida.csv.tmp"
        preexistente.write_text("conteúdo que não é do programa\n", encoding="utf-8")
        self.input.write_bytes(b"")
        external_sort(self.input, "id", output_path=self.output)
        self.assertEqual(self.output.read_bytes(), b"")
        self.assertEqual(preexistente.read_text(encoding="utf-8"), "conteúdo que não é do programa\n")
        self.assert_only_files(["entrada.csv", "saida.csv", "saida.csv.tmp"])

    def test_falha_no_os_replace_remove_o_temporario_e_preserva_a_saida_anterior(self):
        self.write_input(make_rows(self.KEYS))
        self.output.write_text("saída anterior\n", encoding="utf-8")
        seen = []
        def failing_replace(src, dst):
            seen.append((Path(src), Path(src).exists()))
            raise OSError("falha simulada")
        with mock.patch("os.replace", side_effect=failing_replace):
            with self.assertRaisesRegex(OSError, "falha simulada"):
                external_sort(self.input, "id", output_path=self.output, buffer_records=1)
        self.assertEqual(len(seen), 1)
        temporary, existed = seen[0]
        self.assertTrue(existed)
        self.assertFalse(temporary.exists())
        self.assertEqual(self.output.read_text(encoding="utf-8"), "saída anterior\n")
        self.assert_only_files(["entrada.csv", "saida.csv"])

    def test_temporario_e_criado_na_pasta_da_saida_com_nome_exclusivo(self):
        out_dir = self.dir / "destino"
        out_dir.mkdir()
        output = out_dir / "saida.csv"
        self.write_input(make_rows(self.KEYS))
        real_replace = os.replace
        calls = []
        def spy(src, dst):
            calls.append((Path(src), Path(dst)))
            return real_replace(src, dst)
        with mock.patch("os.replace", side_effect=spy):
            external_sort(self.input, "id", output_path=output, buffer_records=1)
        self.assertEqual(len(calls), 1)
        temporary, destination = calls[0]
        self.assertEqual(temporary.parent.resolve(), out_dir.resolve())
        self.assertEqual(destination, output)
        self.assertNotEqual(temporary.name, "saida.csv.tmp")
        self.assertTrue(temporary.name.startswith("saida.csv.") and temporary.name.endswith(".tmp"))
        self.assertEqual(sorted(p.name for p in out_dir.iterdir()), ["saida.csv"])
