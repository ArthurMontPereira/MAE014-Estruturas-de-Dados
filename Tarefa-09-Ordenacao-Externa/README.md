# Tarefa 09 — Ordenação Externa por MergeSort

Implementação de ordenação externa para arquivos CSV. O arquivo é processado em blocos limitados por um buffer, sem carregar todos os registros simultaneamente na memória.

## Visão geral

A solução segue as duas camadas do enunciado:

1. **Geração de runs:** o CSV é lido em blocos de até `buffer_records` registros. Cada bloco é ordenado em memória e gravado em um arquivo temporário (*run*).
2. **Merge externo:** os runs são combinados de dois em dois, recursivamente, por divisão e conquista. Os registros são lidos e gravados em *streaming* até restar um único arquivo ordenado.

O merge é estável: em caso de empate, o registro do run à esquerda é emitido primeiro. O cabeçalho é preservado.

## Estrutura do projeto

```text
Tarefa-09-Ordenacao-Externa/
├── extsort/
│   ├── __init__.py
│   ├── keys.py
│   ├── runs.py
│   ├── merge.py
│   └── sorter.py
├── tests/
│   ├── __init__.py
│   ├── _support.py
│   ├── test_sorting.py
│   ├── test_validation.py
│   ├── test_csv_cases.py
│   ├── test_temp_cleanup.py
│   └── test_generator_cli.py
├── sort_csv.py
├── generate_dataset.py
├── medir_memoria.py
└── relatorio/
    └── evidencia_85_testes.txt
```

O pacote `extsort/` está na raiz da tarefa. **Não há necessidade de criar `src/`** nesta arquitetura: a CLI e os scripts também são executados a partir dessa raiz, e os imports usam diretamente o pacote `extsort`.

## Requisitos

- Python 3.10 ou superior.
- Apenas biblioteca padrão do Python; não é necessário instalar dependências com `pip`.
- Espaço em disco para os runs e o arquivo temporário de saída.

## Executar os testes

Na pasta `Tarefa-09-Ordenacao-Externa`:

```bash
python3 --version
python3 -m unittest -v
```

A suíte contém **85 testes**. Arthur executou os 85 testes duas vezes localmente em Python 3.14.10; ambas as execuções terminaram com `OK`. A evidência resumida está em [`relatorio/evidencia_85_testes.txt`](relatorio/evidencia_85_testes.txt).

Os testes cobrem ordenação crescente e decrescente, estabilidade, chaves `str` e `int`, parâmetros inválidos, buffers, campos e arquivos CSV especiais, limpeza de temporários, gerador de dados e CLI. Nem todos comparam a saída com `sorted()`; vários verificam comportamentos e tratamento de erros.

## Uso pela linha de comando

```bash
python3 sort_csv.py ENTRADA.csv --key COLUNA [opções]
```

| Opção | Significado | Padrão |
|---|---|---|
| `ENTRADA` | CSV de entrada; a primeira linha é o cabeçalho | obrigatório |
| `--key` | Nome da coluna ou posição (começando em zero) | obrigatório |
| `--order` | `asc`/`ascendente` ou `desc`/`descendente` | `asc` |
| `-o, --output` | Caminho do CSV de saída | `<nome>.sorted<extensão>` |
| `-b, --buffer` | Máximo de registros por run | `100000` |
| `--key-type` | Comparação como texto (`str`) ou inteiro (`int`) | `str` |
| `-d, --delimiter` | Delimitador CSV, com um caractere | `,` |
| `--encoding` | Codificação do arquivo | `utf-8` |

Exemplos:

```bash
# Ordenar por uma coluna chamada id, em ordem crescente
python3 sort_csv.py alunos.csv --key id

# Ordenar pela terceira coluna (posição 2), em ordem decrescente
python3 sort_csv.py alunos.csv --key 2 --order desc -o alunos_desc.csv

# Comparar uma chave numérica de tamanho variável
python3 sort_csv.py vendas.csv --key id --key-type int --buffer 50000

# CSV separado por ponto e vírgula
python3 sort_csv.py vendas.csv --key id -d ";"
```

Se `--key` for um número e existir uma coluna com esse nome no cabeçalho, o nome tem prioridade; caso contrário, o valor é interpretado como posição.

## Gerar um dataset reproduzível

```bash
python3 generate_dataset.py --records 800000 --output big.csv --seed 42
```

O gerador escreve o arquivo registro a registro. As colunas são `id,nome,curso,nota,linha_original`. A coluna `id` tem 10 dígitos e zeros à esquerda; `curso` contém valores repetidos; `linha_original` permite conferir a estabilidade da ordenação por curso.

O dataset de 800.000 registros (aproximadamente 41 MB) usado nos experimentos não está versionado; ele pode ser recriado pelo comando acima.

## Validar a ordenação

Para o dataset gerado, no qual `id` é a primeira coluna e tem largura fixa:

```bash
tail -n +2 ordenado.csv | LC_ALL=C sort -c
tail -n +2 ordenado_desc.csv | LC_ALL=C sort -c -r
```

Os comandos não imprimem mensagem quando a sequência está ordenada corretamente; um código de saída diferente de zero indica uma inversão.

## Resultados experimentais

Os experimentos locais foram executados em Python 3.14.10, Aurora 44.20261110.1 (base Kinoite), Intel Core i5-4590T @ 2,00 GHz, 8 GB de RAM e SSD SATA WDC de 223,6 GB.

| Buffer | Runs | Níveis de merge | Tempo total | Pico de `tracemalloc` |
|---:|---:|---:|---:|---:|
| 5.000 | 160 | 8 | 30,28 s | 2,56 MB |
| 20.000 | 40 | 6 | 24,73 s | 8,41 MB |
| 50.000 | 16 | 4 | 19,22 s | 20,72 MB |

Os tempos e os picos de memória foram medidos em execuções separadas. `tracemalloc` mede alocações rastreadas pelo Python, não o uso total de RAM do processo. Cada configuração de buffer foi executada uma vez; os valores são observações daquele computador e daquele dataset, não garantias de desempenho geral.

## Script auxiliar de memória

`medir_memoria.py` mede o pico de alocações rastreadas pelo Python:

```bash
python3 medir_memoria.py big.csv memoria_5000.csv 5000
```

Esse valor não corresponde à memória RAM total do processo.

## Decisões e limitações

- `buffer_records` limita a **quantidade de registros**, não bytes. O consumo real também depende do tamanho dos registros e do overhead dos objetos Python.
- A memória auxiliar total é (O(M+R)), pois a lista de caminhos dos (R) runs também ocupa memória.
- `key_type="str"` é o padrão para preservar zeros à esquerda. Para números de comprimentos diferentes (por exemplo, `9`, `10`, `100`), use `--key-type int`.
- A saída usa o terminador CRLF padrão de `csv.writer`. Essa decisão mantém a compatibilidade com Python 3.10 e corrige o caso de campos contendo `\r` isolado.
- A saída é montada em arquivo temporário de nome exclusivo, na mesma pasta do destino, e substituída com `os.replace`.
- Erros tratados e Ctrl+C acionam a limpeza. Encerramentos abruptos como SIGKILL, SIGTERM ou queda de energia podem deixar temporários residuais.
- O espaço temporário de pico pode chegar a aproximadamente duas vezes o tamanho do arquivo, além do arquivo de entrada.

## Relatório

O PDF de análise crítica e Post-Mortem de IA deve ser colocado em `relatorio/relatorio_tarefa09.pdf`. A evidência dos testes locais já está em `relatorio/evidencia_85_testes.txt`.
