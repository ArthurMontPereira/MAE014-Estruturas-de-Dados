# MAE014 — Estruturas de Dados e seus Algoritmos

Repositório de projetos e trabalhos da disciplina **MAE014 — Tópicos em Ciência de Dados B: Estruturas de Dados e seus Algoritmos**, do Departamento de Matemática Aplicada da UFRJ.

A organização é feita por tarefa: cada diretório reúne o enunciado resumido, a implementação, os testes, os dados de exemplo e o relatório correspondente. O uso de IA generativa é permitido nos enunciados, mas as decisões de projeto, a verificação do código e a autoria do trabalho continuam sob responsabilidade dos integrantes.

## Índice das tarefas

| Tarefa | Tema | Situação neste repositório |
|---|---|---|
| [05 — Estruturas Lineares](Tarefa-05-Estruturas-Lineares/) | Listas encadeadas, filas e deque | Estrutura inicial e guia de requisitos criados |
| [06 — Árvore Binária de Busca](Tarefa-06-ABB/) | ABB e índice de registros | Diretório inicial |
| [08 — Tabela Hash](Tarefa-08-Hash/) | Dispersão, colisões e deduplicação | Diretório inicial |
| [09 — Ordenação Externa](Tarefa-09-Ordenacao-Externa/) | MergeSort externo para CSV | Implementação, testes e documentação |
| [10 — Grafos](Tarefa-10-Grafos/) | Grafos, dígrafos, multigrafos e hipergrafos | Diretório inicial |

Os status acima descrevem apenas o que está versionado aqui.

## Conteúdo em poucas linhas

- **Tarefa 05:** hierarquia de estruturas lineares com uma classe abstrata, listas simples e duplas, fila FIFO e deque. As aplicações são uma lista invertida de palavras, um editor de figuras planas e a fila de pedidos do bandejão.
- **Tarefa 06:** árvore binária de busca, suas operações e uma aplicação de índice para localizar registros em arquivo.
- **Tarefa 08:** tabela hash, funções de dispersão e tratamento de colisões, aplicada à identificação de registros duplicados.
- **Tarefa 09:** geração de runs ordenados em blocos limitados por buffer e merge recursivo de pares de arquivos.
- **Tarefa 10:** representação e manipulação de grafos e estruturas relacionadas, com problemas envolvendo percursos e algoritmos de grafos.

## Organização dos diretórios

Cada tarefa pode adotar uma estrutura adequada à sua linguagem e arquitetura. Como ponto de partida:

```text
Tarefa-XX-Nome/
├── README.md       # escopo, decisões e comandos de execução
├── src/ ou pacote/ # código-fonte
├── tests/          # testes automatizados
├── data/           # exemplos pequenos e reproduzíveis
└── relatorio/      # PDF e evidências da execução
```

Na Tarefa 09, por exemplo, o pacote Python `extsort/` fica diretamente na raiz do diretório da tarefa,por isso, ela não precisa de uma pasta `src/`.

## Executar e testar

Consulte o README de cada tarefa para os comandos específicos. Não há uma única dependência ou comando de execução compartilhado por todos os trabalhos.

## Boas práticas do repositório

- Mantenha cada tarefa independente e documente como executá-la.
- Prefira testes pequenos, determinísticos e reproduzíveis.
- Não versione ambientes virtuais, caches, credenciais ou datasets grandes que possam ser regenerados.
- Registre alterações reais em commits pequenos e descritivos.
- Diferencie testes executados pelos integrantes de verificações feitas por ferramentas ou em outros ambientes.
- Quando usar IA, registre prompts relevantes, revisão crítica, refatorações e evidências de teste conforme o enunciado.

## Convenção de commits

Use mensagens que indiquem a tarefa e o tipo de alteração:

```text
docs(tarefa-05): descreve a interface das estruturas lineares
feat(tarefa-05): implementa lista encadeada simples
test(tarefa-05): cobre inserção e remoção por posição
fix(ordenacao): corrige leitura de campos CSV com CR isolado
```
