# Tarefa 09 — Ordenação Externa por MergeSort

## Objetivo
Ordenar um arquivo CSV que não deve ser carregado integralmente na memória, dividindo-o em runs menores, ordenando cada run e realizando intercalações sucessivas até gerar um único arquivo ordenado.

## Organização
- `src/`: implementação da ordenação externa.
- `tests/`: testes de ordenação, limites de memória, arquivos temporários e casos de borda.
- `data/`: arquivos pequenos de exemplo para desenvolvimento; datasets grandes devem ficar fora do Git.
- `relatorio/`: relatório de análise crítica e post-mortem da IA.

## Executar
Preencher este README com os comandos reais assim que os módulos principais forem implementados.

## Checklist
- [ ] Receber caminho do arquivo, coluna/chave e ordem de classificação
- [ ] Ler o CSV em blocos limitados (runs)
- [ ] Ordenar cada run em memória e gravar arquivo temporário
- [ ] Intercalar runs sem carregar o arquivo completo na memória
- [ ] Tratar cabeçalho e tipos da chave de ordenação
- [ ] Suportar ordem crescente e decrescente
- [ ] Limpar arquivos temporários mesmo em caso de falha
- [ ] Testar arquivo vazio, bloco final incompleto, chaves repetidas e CSV grande
- [ ] Relatório e post-mortem da IA
