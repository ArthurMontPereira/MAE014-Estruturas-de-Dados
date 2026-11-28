# Tarefa 05 — Hierarquia de Classes de Estruturas de Dados Lineares

Este diretório reúne a implementação, os testes, os dados de exemplo e o relatório da Tarefa 05 de MAE014 — *Tópicos em Ciência de Dados B: Estruturas de Dados e seus Algoritmos*.

> **Status:** estrutura inicial criada. A implementação ainda não foi adicionada.

## Objetivo

Implementar uma hierarquia orientada a objetos para quatro estruturas lineares:

1. Lista encadeada simples.
2. Lista encadeada dupla.
3. Fila simples (*queue*, FIFO).
4. Fila dupla (*deque*).

A especificação pede pelo menos uma classe abstrata para reunir os atributos e operações comuns às subclasses. As filas podem ser derivadas das classes de lista, com interfaces adequadas ao comportamento FIFO.

## Interface comum exigida

A especificação solicita operações para:

- Consultar o comprimento e verificar se a estrutura está vazia ou cheia.
- Construir uma estrutura a partir de um iterador.
- Inserir no início, no fim, em uma posição e antes/depois de um item identificado por chave.
- Atualizar um item pela chave ou pela posição.
- Remover do início, do fim, de uma posição ou pela chave.
- Consultar o primeiro, o último, o item de uma posição ou o primeiro item com determinada chave.
- Consultar a próxima ocorrência de uma chave, permitindo percorrer elementos repetidos.
- Trocar dois itens em posições sucessivas (*swap*) e usar essa operação em um algoritmo de ordenação baseado em trocas, como seleção, inserção ou bolha.

As operações por posição devem sinalizar posições inválidas. As operações por chave devem definir e documentar o comportamento quando a chave não existir, conforme as alternativas indicadas no enunciado.

## Aplicações obrigatórias

### 1. Lista invertida de palavras — lista encadeada simples

Ler um arquivo TXT e criar um índice que associe cada palavra às posições em que aparece. A estrutura sugerida no enunciado é uma lista de palavras cujos nós referenciam listas de ocorrências. Cada ocorrência pode guardar o número da linha e a posição da palavra naquela linha.

### 2. Editor de figuras planas — lista encadeada dupla

Representar cada figura como uma sequência de pontos `(x, y)`. O editor deve gerenciar a criação, edição, apresentação e remoção de figuras, permitir carregar coordenadas de TXT ou CSV e calcular perímetros.

A edição deve permitir alterar um vértice, uma subsequência de vértices consecutivos ou a figura inteira. O enunciado pede, no mínimo, translação, escala, concatenação de figuras por lados adjacentes e *sweep* plano. Para figuras fechadas, sugere considerar uma lista circular duplamente encadeada. Os pontos devem permanecer em uma ordem que não produza cruzamentos entre os segmentos.

### 3. Fila do bandejão — fila simples e deque

Simular uma fila FIFO de pedidos. O sistema deve estimar a espera antes do ingresso na fila e manter uma previsão/contagem regressiva para a retirada do prato. Deve tratar desistências, atualizar os tempos dos usuários seguintes e ajustar previsões quando houver atrasos, adiantamentos ou ausência de quem deveria retirar o pedido.

## Organização deste diretório

```text
Tarefa-05-Estruturas-Lineares/
├── README.md
├── src/
│   └── estruturas_lineares/
├── tests/
├── data/
└── relatorio/
```

Os diretórios possuem READMEs próprios com orientações. Os nomes de módulos e a divisão interna podem ser ajustados durante o projeto, desde que a arquitetura final seja documentada.

## Testes recomendados

Além de testar cada operação isoladamente, a suíte deve cobrir:

- Estrutura vazia, com um item e com vários itens.
- Inserções e remoções nas extremidades e no meio.
- Posição fora dos limites e chave inexistente.
- Chaves repetidas e avanço para a próxima ocorrência.
- Atualizações por posição e por chave.
- Iteração sobre todos os itens.
- Troca de posições adjacentes e ordenação.
- Concatenação e separação de listas simples.
- Inserção de uma lista entre nós de outra.
- Casos circulares e figura aberta/fechada no editor geométrico.
- Cálculo e atualização dos tempos na fila do bandejão.

## Relatório e avaliação

O enunciado pede um relatório curto em PDF com folha de rosto (nomes completos, DREs e link do GitHub), análise crítica da implementação, divisão de módulos, descrição de rotinas, complexidades de tempo e espaço, problemas encontrados e conclusão.

Quando houver uso de IA, o Post-Mortem deve conter:

- Log de prompts-chave e fragmentos brutos relevantes gerados pela IA.
- Code Review dos erros ou ineficiências identificados.
- Justificativa das refatorações.
- Evidências dos testes que demonstrem as correções.

O enunciado também informa que a avaliação inclui perguntas e desafios em sala, inclusive alterações e geração de código. Portanto, os integrantes devem conseguir explicar e modificar a própria implementação.

O relatório deve ser colocado em `relatorio/` e versionado neste repositório, além de ser submetido no AVA@UFRJ conforme as instruções do professor.
