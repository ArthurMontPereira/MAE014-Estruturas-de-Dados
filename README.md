# MAE014 — Estruturas de Dados e seus Algoritmos

Repositório do grupo para organizar os trabalhos da disciplina **MAE014 — Tópicos em Ciência de Dados B**.

Cada tarefa fica em sua própria pasta, com código, testes, dados e relatório separados. O projeto usa uma única branch principal (`main`).

## Trabalhos

| Tarefa | Tema | Situação planejada | Pasta |
|---|---|---|---|
| 06 | Árvore Binária de Busca (ABB) | Prioridade de entrega | [`Tarefa-06-ABB/`](Tarefa-06-ABB/) |
| 08 | Tabela Hash | Prioridade de entrega | [`Tarefa-08-Hash/`](Tarefa-08-Hash/) |
| 09 | Ordenação Externa por MergeSort | Prioridade de entrega | [`Tarefa-09-Ordenacao-Externa/`](Tarefa-09-Ordenacao-Externa/) |
| 10 | Grafos, Dígrafos, Multigrafos e Hipergrafos | Entrega adicional, conforme progresso | [`Tarefa-10-Grafos/`](Tarefa-10-Grafos/) |

A Tarefa 05 — Estruturas Lineares não está incluída no escopo inicial deste repositório.

## Organização de cada tarefa

```text
Tarefa-XX-Nome/
├── README.md       # objetivo, requisitos e instruções da tarefa
├── src/            # implementação
├── tests/          # testes automatizados e casos de teste
├── data/           # datasets pequenos/de exemplo (não enviar dados grandes sem necessidade)
└── relatorio/      # relatório e materiais do post-mortem de IA
```

## Requisitos gerais

- Python 3.10 ou superior (ajustar se o grupo decidir usar outra versão).
- Não misturar módulos de tarefas diferentes: cada pasta deve poder ser entendida e testada independentemente.
- Registrar o desenvolvimento em commits pequenos e descritivos.
- Manter os prompts relevantes, versões iniciais geradas por IA, correções manuais e evidências de testes para o post-mortem solicitado nos enunciados.
- Não versionar ambientes virtuais, cache, credenciais ou datasets muito grandes.

## Começar a trabalhar

1. Clone o repositório.
2. Entre na pasta da tarefa que ficou sob sua responsabilidade.
3. Leia o `README.md` daquela tarefa.
4. Crie/ative um ambiente virtual e instale apenas as dependências necessárias.
5. Implemente em `src/` e coloque os testes em `tests/`.
6. Atualize o README da tarefa com os comandos reais de execução e teste.

Exemplo de criação de ambiente virtual:

```bash
python -m venv .venv
```

Ativação no Linux/macOS:

```bash
source .venv/bin/activate
```

Ativação no Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

## Convenção de commits

Prefira mensagens que indiquem a tarefa e a mudança:

```text
feat(abb): implementa inserção de nós
fix(hash): corrige remoção após colisão
test(ordenacao): adiciona caso com chave numérica
feat(grafos): implementa busca em largura
```

Evite commits genéricos como `mudanças`, `trabalho` ou `final`.

## Status

Este repositório é apenas a estrutura inicial. As implementações, testes, dependências e relatórios serão adicionados pelo grupo.
