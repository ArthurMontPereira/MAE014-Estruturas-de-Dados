"""Testes do gerador de dataset e da interface de linha de comando."""
from tests._support import *


class TestGeradorDeDataset(ExternalSortTestCase):
    """Gerador: reproduzível, IDs únicos com zeros à esquerda."""

    def test_mesma_seed_gera_arquivos_identicos(self):
        first, second = self.dir / "a.csv", self.dir / "b.csv"
        generate_dataset.generate_dataset(first, 500, seed=7)
        generate_dataset.generate_dataset(second, 500, seed=7)
        self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_seeds_diferentes_geram_arquivos_diferentes(self):
        first, second = self.dir / "a.csv", self.dir / "b.csv"
        generate_dataset.generate_dataset(first, 500, seed=7)
        generate_dataset.generate_dataset(second, 500, seed=8)
        self.assertNotEqual(first.read_bytes(), second.read_bytes())

    def test_cabecalho_quantidade_e_formato_dos_ids(self):
        generate_dataset.generate_dataset(self.output, 1000, seed=7)
        rows = read_csv(self.output)
        self.assertEqual(rows[0], generate_dataset.HEADER)
        data = rows[1:]
        self.assertEqual(len(data), 1000)
        ids = [row[0] for row in data]
        self.assertTrue(all(len(i) == 10 and i.isdigit() for i in ids))
        self.assertTrue(any(i.startswith("0") for i in ids))
        self.assertEqual(len(set(ids)), 1000)
        self.assertEqual([row[4] for row in data], [str(n) for n in range(1, 1001)])

    def test_ids_nao_saem_ordenados(self):
        generate_dataset.generate_dataset(self.output, 1000, seed=7)
        ids = [row[0] for row in read_csv(self.output)[1:]]
        self.assertNotEqual(ids, sorted(ids))
        self.assertNotEqual(ids, sorted(ids, reverse=True))

    def test_quantidade_de_registros_invalida(self):
        invalid = (0, -5, 1.5, 2.0, True, False, "10", None)
        for bad in invalid:
            with self.subTest(records=bad):
                with self.assertRaisesRegex(ValueError, "inteiro entre 1 e"):
                    generate_dataset.generate_dataset(self.output, bad, seed=1)
                self.assert_only_files([])

    def test_um_registro_e_aceito(self):
        generate_dataset.generate_dataset(self.output, 1, seed=1)
        rows = read_csv(self.output)
        self.assertEqual(rows[0], generate_dataset.HEADER)
        self.assertEqual(len(rows), 2)

    def test_limite_maximo_de_registros(self):
        with mock.patch.object(generate_dataset, "MAX_RECORDS", 10):
            generate_dataset.generate_dataset(self.output, 10, seed=1)
            self.assertEqual(len(read_csv(self.output)), 11)
            with self.assertRaisesRegex(ValueError, "inteiro entre 1 e 10"):
                generate_dataset.generate_dataset(self.dir / "outro.csv", 11, seed=1)
        self.assert_only_files(["saida.csv"])

    def test_dataset_gerado_pode_ser_ordenado(self):
        source = self.dir / "dados.csv"
        generate_dataset.generate_dataset(source, 1000, seed=3)
        external_sort(source, "id", output_path=self.output, buffer_records=64)
        original = read_csv(source)[1:]
        self.assertEqual(
            read_csv(self.output),
            [generate_dataset.HEADER] + sorted(original, key=lambda r: r[0]),
        )

    def test_linha_de_comando_do_gerador(self):
        with contextlib.redirect_stdout(io.StringIO()):
            code = generate_dataset.main(["-n", "25", "-o", str(self.output), "--seed", "5"])
        self.assertEqual(code, 0)
        self.assertEqual(len(read_csv(self.output)), 26)

    def test_linha_de_comando_do_gerador_rejeita_quantidade_invalida(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = generate_dataset.main(["-n", "0", "-o", str(self.output)])
        self.assertEqual(code, 1)
        self.assertIn("inteiro entre 1 e", err.getvalue())
        self.assert_only_files([])
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as ctx:
                generate_dataset.main(["-n", "1.5", "-o", str(self.output)])
        self.assertEqual(ctx.exception.code, 2)


class TestLinhaDeComando(ExternalSortTestCase):
    """sort_csv.main() chamado com uma lista de argumentos, como no terminal."""

    KEYS = ["042", "007", "100", "001", "050"]

    def run_cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = sort_csv.main([str(arg) for arg in args])
            except SystemExit as exc:
                code = exc.code
        return code, out.getvalue(), err.getvalue()

    def test_ordena_pelo_nome_da_coluna(self):
        rows = make_rows(self.KEYS)
        self.write_input(rows)
        code, out, _ = self.run_cli(self.input, "--key", "id", "-o", self.output, "--buffer", 2)
        self.assertEqual(code, 0)
        self.assertEqual(read_csv(self.output), [HEADER] + reference_sort(rows))
        self.assertIn("5 registros", out)

    def test_ordena_pela_posicao_da_coluna(self):
        rows = make_rows(self.KEYS)
        self.write_input(rows)
        code, _, _ = self.run_cli(self.input, "-k", "0", "-o", self.output)
        self.assertEqual(code, 0)
        self.assertEqual(read_csv(self.output), [HEADER] + reference_sort(rows))

    def test_nome_de_coluna_numerico_tem_prioridade_sobre_a_posicao(self):
        header = ["id", "nome", "1"]
        rows = [["a", "z", "3"], ["b", "y", "1"], ["c", "x", "2"]]
        self.write_input(rows, header=header)
        code, _, _ = self.run_cli(self.input, "--key", "1", "-o", self.output)
        self.assertEqual(code, 0)
        self.assertEqual(read_csv(self.output), [header] + reference_sort(rows, key_index=2))

    def test_ordem_decrescente(self):
        rows = make_rows(self.KEYS)
        self.write_input(rows)
        code, _, _ = self.run_cli(self.input, "--key", "id", "--order", "desc", "-o", self.output)
        self.assertEqual(code, 0)
        self.assertEqual(read_csv(self.output), [HEADER] + reference_sort(rows, descending=True))

    def test_tipo_da_chave_e_delimitador(self):
        rows = [["9", "a;b", "0"], ["10", "c", "1"], ["2", "d", "2"]]
        write_csv(self.input, [HEADER] + rows, delimiter=";")
        code, _, _ = self.run_cli(self.input, "--key", "id", "--key-type", "int", "-d", ";", "-o", self.output)
        self.assertEqual(code, 0)
        self.assertEqual(read_csv(self.output, ";"), [HEADER] + reference_sort(rows, convert=int))

    def test_saida_padrao(self):
        self.write_input(make_rows(self.KEYS))
        code, out, _ = self.run_cli(self.input, "--key", "id")
        self.assertEqual(code, 0)
        self.assertTrue((self.dir / "entrada.sorted.csv").exists())
        self.assertIn("entrada.sorted.csv", out)

    def test_codificacao_latin1(self):
        self.input.write_bytes("id,nome\n2,José\n1,Ana\n".encode("latin-1"))
        code, _, err = self.run_cli(self.input, "--key", "id", "-o", self.output)
        self.assertEqual(code, 1)
        self.assertIn("--encoding", err)
        code, _, _ = self.run_cli(self.input, "--key", "id", "-o", self.output, "--encoding", "latin-1")
        self.assertEqual(code, 0)
        self.assertEqual(
            self.output.read_bytes(),
            "id,nome\r\n1,Ana\r\n2,José\r\n".encode("latin-1"),
        )

    def test_arquivo_de_entrada_inexistente(self):
        code, _, err = self.run_cli(self.dir / "nao_existe.csv", "--key", "id")
        self.assertEqual(code, 2)
        self.assertIn("não encontrado", err)

    def test_coluna_inexistente(self):
        self.write_input(make_rows(self.KEYS))
        code, _, err = self.run_cli(self.input, "--key", "nao_existe", "-o", self.output)
        self.assertEqual(code, 1)
        self.assertIn("erro:", err)
        self.assertIn("não encontrada", err)
        self.assertFalse(self.output.exists())

    def test_chave_ausente_informa_a_linha(self):
        self.write_input([["1", "a", "0"], ["", "b", "1"]])
        code, _, err = self.run_cli(self.input, "--key", "id", "-o", self.output)
        self.assertEqual(code, 1)
        self.assertIn("linha 3", err)

    def test_buffer_zero_mostra_erro_compreensivel(self):
        self.write_input(make_rows(self.KEYS))
        code, _, err = self.run_cli(self.input, "--key", "id", "--buffer", 0)
        self.assertEqual(code, 1)
        self.assertIn("inteiro positivo", err)

    def test_buffer_decimal_e_rejeitado_na_leitura_dos_argumentos(self):
        self.write_input(make_rows(self.KEYS))
        code, _, _ = self.run_cli(self.input, "--key", "id", "--buffer", "1.5")
        self.assertEqual(code, 2)

    def test_delimitador_com_mais_de_um_caractere(self):
        self.write_input(make_rows(self.KEYS))
        code, _, err = self.run_cli(self.input, "--key", "id", "-d", ";;")
        self.assertEqual(code, 2)
        self.assertIn("1 caractere", err)
