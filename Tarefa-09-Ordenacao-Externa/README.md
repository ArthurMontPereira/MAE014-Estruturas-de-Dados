# Tarefa 09 — Ordenação Externa por MergeSort

Implementação de ordenação externa para arquivos CSV. O arquivo é processado em porções limitadas por um buffer, sem carregar todos os registros simultaneamente na memória.

## Visão geral

A solução segue as duas camadas exigidas no enunciado:

1. **Geração de runs:** leitura do CSV em blocos de até `buffer_records` registros; cada bloco é ordenado em memória e gravado em um arquivo temporário (*run*).
2. **Merge externo:** os runs são combinados de dois em dois, por divisão e conquista, lendo e escrevendo em *streaming*, até restar um único arquivo ordenado.

O merge é estável: em caso de empate, o registro do run à esquerda é emitido primeiro. O cabeçalho é preservado. Os temporários são removidos nos encerramentos tratados pelo programa; encerramentos abruptos podem deixar arquivos residuais, conforme explicado adiante.

## Requisitos

- Python 3.10 ou superior.
- Apenas biblioteca padrão do Python; não é necessário instalar dependências com `pip`.
- Espaço em disco para os runs e o arquivo de saída temporário.

## Estrutura

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
│   └── test_extsort.py
├── sort_csv.py
├── generate_dataset.py
├── medir_memoria.py
├── README.md
└── relatorio/
    ├── relatorio_tarefa09.pdf
    ├── relatorio_tarefa09.tex
    └── evidencia_85_testes.txt
```

## Executar os testes

Na pasta `Tarefa-09-Ordenacao-Externa`:

```bash
python3 --version
python3 -m unittest -v
```

A suíte final contém **85 testes**. O autor executou a suíte duas vezes em Python 3.14.10; ambas terminaram com `OK`. A evidência resumida está em [`relatorio/evidencia_85_testes.txt`](relatorio/evidencia_85_testes.txt).

A suíte cobre ordenação crescente e decrescente, chaves `str` e `int`, estabilidade, parâmetros inválidos, buffers, CSVs com campos especiais, limpeza de temporários, gerador de dados e interface de linha de comando. Nem todos os testes comparam a saída com `sorted()`; vários verificam comportamento e tratamento de erros.

## Uso pela linha de comando

```bash
python3 sort_csv.py ENTRADA.csv --key COLUNA [opções]
```

| Opção | Significado | Padrão |
|---|---|---|
| `ENTRADA` | CSV de entrada; primeira linha é o cabeçalho | obrigatório |
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

Se `--key` for um número e existir uma coluna com esse nome no cabeçalho, o nome tem prioridade; caso contrário, o valor numérico é interpretado como posição.

## Gerar um dataset reproduzível

```bash
python3 generate_dataset.py --records 800000 --output big.csv --seed 42
```

O gerador escreve o arquivo registro a registro. As colunas são `id,nome,curso,nota,linha_original`. A coluna `id` tem 10 dígitos e zeros à esquerda; `curso` contém valores repetidos; `linha_original` permite conferir a estabilidade da ordenação por curso.

O dataset de 800.000 registros (aproximadamente 41 MB) utilizado nos experimentos não está versionado. Ele pode ser recriado pelo comando acima.

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

Os tempos e os picos de memória foram medidos em execuções separadas. `tracemalloc` mede alocações rastreadas pelo Python, não a memória RAM total do processo. Cada configuração foi executada uma vez; os valores são observações daquele computador e daquele dataset, não garantias de desempenho geral.

## Medir alocações rastreadas pelo Python

O script auxiliar `medir_memoria.py` mede o pico de memória rastreada pelo `tracemalloc`:

```bash
python3 medir_memoria.py big.csv memoria_5000.csv 5000
```

O resultado não corresponde ao consumo total de RAM do processo.

## Decisões e limitações

- `buffer_records` limita **quantidade de registros**, não bytes. O consumo real também depende do tamanho dos registros e do overhead dos objetos Python.
- A memória auxiliar total é (O(M+R)), pois a lista de caminhos dos (R) runs também ocupa memória.
- `key_type="str"` é o padrão para preservar zeros à esquerda. Para números de comprimentos diferentes (por exemplo, `9`, `10`, `100`), use `--key-type int`.
- A saída usa o terminador CRLF padrão de `csv.writer`. Essa decisão mantém a compatibilidade com Python 3.10 e corrige o caso de campos contendo `\r` isolado.
- A saída é montada em arquivo temporário de nome exclusivo, na mesma pasta do destino, e substituída com `os.replace`.
- Erros tratados e Ctrl+C acionam a limpeza. Encerramentos abruptos como SIGKILL, SIGTERM ou queda de energia podem deixar temporários residuais.
- O espaço temporário de pico pode chegar a aproximadamente duas vezes o tamanho do arquivo, além do arquivo de entrada.

## Relatório

O relatório de análise crítica e Post-Mortem de IA está em [`relatorio/relatorio_tarefa09.pdf`](relatorio/relatorio_tarefa09.pdf). O fonte LaTeX e a evidência dos testes locais também estão na pasta `relatorio/`.
