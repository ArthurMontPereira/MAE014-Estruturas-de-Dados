# MAE014 — Estruturas de Dados e seus Algoritmos

Repositório de trabalhos da disciplina **MAE014 — Tópicos em Ciência de Dados B**, do Departamento de Matemática Aplicada da UFRJ.

Cada tarefa possui seu próprio diretório para separar implementação, testes, dados e relatório. Os enunciados permitem o uso de assistentes de IA, mas atribuem ao aluno a responsabilidade pelas decisões de projeto, pela correção do código e pelo registro rastreável do desenvolvimento.

## Tarefas

| Tarefa | Tema | Diretório |
|---|---|---|
| 05 | Estruturas lineares: listas encadeadas, filas e deque | Enunciado recebido; diretório ainda não criado |
| 06 | Árvore Binária de Busca (ABB) e índice de registros | [Tarefa-06-ABB](Tarefa-06-ABB/) |
| 08 | Tabela Hash e deduplicação de datasets | [Tarefa-08-Hash](Tarefa-08-Hash/) |
| 09 | Ordenação Externa por MergeSort | [Tarefa-09-Ordenacao-Externa](Tarefa-09-Ordenacao-Externa/) |
| 10 | Grafos, dígrafos, multigrafos e hipergrafos | [Tarefa-10-Grafos](Tarefa-10-Grafos/) |

> **Situação do repositório:** as pastas das tarefas 06, 08 e 10 estão criadas como estrutura inicial. A Tarefa 09 contém implementação, testes e relatório. A Tarefa 05 ainda não possui diretório neste repositório.

## Sobre os trabalhos

- **Tarefa 05:** hierarquia de listas simplesmente e duplamente encadeadas, filas e deque; aplicações como lista invertida de palavras, edição de figuras e fila de pedidos.
- **Tarefa 06:** ABB com operações de inserção, remoção e percurso, aplicada à criação de um índice para localizar registros em arquivo.
- **Tarefa 08:** tabela hash com funções de dispersão e tratamento de colisões, aplicada à remoção de duplicatas em datasets.
- **Tarefa 09:** ordenação de CSV em duas camadas: geração de runs limitados por buffer e intercalação recursiva de pares de runs.
- **Tarefa 10:** diferentes tipos e representações de grafos, com aplicações de BFS, DFS, caminhos mínimos, autômatos e modelos entidade-relacionamento.

## Organização recomendada

```text
Tarefa-XX-Nome/
├── README.md       # objetivo, requisitos e comandos
├── extsort/ ou src/ # implementação (conforme o projeto)
├── tests/          # testes automatizados
├── data/           # exemplos pequenos; evitar datasets grandes
└── relatorio/      # relatório PDF e evidências
```

## Convenções

- Não misturar módulos de tarefas diferentes.
- Registrar alterações reais em commits pequenos e descritivos.
- Não versionar ambientes virtuais, caches, credenciais ou datasets grandes.
- Identificar quais testes foram executados pelos integrantes e quais foram executados em ambientes externos.
- Não afirmar que um teste foi executado localmente sem possuir a respectiva evidência.

## Histórico de commits

Prefira mensagens que indiquem a tarefa e a natureza da alteração:

```text
docs(ordenacao): documenta execução e resultados
feat(ordenacao): adiciona geração de runs
fix(ordenacao): corrige campos CSV com CR isolado
test(ordenacao): cobre estabilidade e arquivos temporários
```
