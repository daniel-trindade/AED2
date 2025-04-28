## Análise de Assortatividade em Grafos de Ingredientes da Culinária Brasileira

by <br/>
[Daniel Bruno Trindade da Silva](https://github.com/daniel-trindade)

***
### Introdução

O presente trabalho, desenvolvido no âmbito da disciplina de Algoritmos e Estruturas de Dados do curso de Engenharia da Computação, propõe a construção e análise de um grafo de co-ocorrência de ingredientes a partir de receitas populares da culinária brasileira.

O objetivo principal é explorar conceitos fundamentais de grafos — como representação, conexões e propriedades estruturais — aplicando-os a um problema real e interdisciplinar: a gastronomia. Para isso, foram selecionadas mais de 50 receitas tradicionais, categorizando seus ingredientes por tipo (proteína, carboidrato, vegetal, etc.) e modelando suas relações de co-ocorrência em um grafo não direcionado e ponderado.

A análise final inclui o cálculo do coeficiente de assortatividade, que mede a tendência de ingredientes do mesmo tipo se combinarem entre si ou de tipos diferentes se associarem. A partir dessa medida, é possível discutir padrões estruturais da culinária brasileira, além de reforçar a importância dos grafos como ferramenta de modelagem e análise em diferentes domínios do conhecimento.

***

### Vídeo Explicativo
https://drive.google.com/file/d/1QnUDV__9s5bd9I2OS_JgEz8TaUbFQIfT/view?usp=sharing


***
### Metodologia
O trabalho foi desenvolvido em três etapas principais: coleta de dados, construção do grafo e análise da assortatividade.

1. Coleta e organização dos dados:
Foram coletadas 50 fotos de comidas tipicamente brasileiras que retiradas do artigo [100 comidas típicas do Brasil para experimentar nas viagens](https://www.penaestrada.blog.br/comidas-tipicas-do-brasil/) as quais foram entregues a IA generativa Gemini 2.0 flash com o seguinte prompt:
> Gere uma lista dos ingredientes a partir desta imagem de comida. Classifique os igredientes em uma das seguintes categorias: proteína carboidrato, gordura, vegetal, fruta, laticínio, tempero. A lista deve estar no formato json com o nome do prato como chave principal.
> Exemplo:
{
  "pudim de leite condensado": {
    "carboidrato": ["açúcar"],
    "proteína": ["ovos"],
    "gordura": [],
    "vegetal": [],
    "fruta": [],
    "laticínio": ["leite condensado", "leite integral"],
    "tempero": []
  }
}

Como retorno consegui montar o banco de dados que consta no arquivo [ingredientes.json](/tarefa_3/comidas_db.json)


2. Construção do grafo de co-ocorrência:
Utilizando a linguagem Python e a biblioteca NetworkX, foi implementado um grafo não direcionado onde cada nó representa um ingrediente, e cada aresta indica a co-ocorrência de dois ingredientes em uma mesma receita. O peso das arestas corresponde ao número de vezes que a combinação aparece nas receitas. Além disso, cada nó foi anotado com o tipo de ingrediente correspondente.

3. Análise de assortatividade:
Com o grafo construído, foi calculado o coeficiente de assortatividade com base no atributo "tipo" dos ingredientes. Esse coeficiente permite medir a tendência de formação de conexões entre ingredientes do mesmo tipo (assortatividade positiva) ou entre tipos diferentes (assortatividade negativa). A análise dos resultados foi realizada para interpretar padrões de combinação de ingredientes na culinária brasileira.

***

### Resultados

Como resultado obtivemos o seguinte grafo:

![Co-ocorrencia de Ingredientes](/tarefa_3/imagens/Co-ocorrencia%20de%20Ingredientes.png)

Com relação a assortatividade do grafo, foi encontrado o valor de -0,0825, indicando a presença de heterofilia, mas não muito forte, ou seja, uma ligeira tendência de combinação entre ingredientes de tipos diferentes (como proteínas com carboidratos, frutas com laticínios, etc.). O valor próximo de zero sugere que essa preferência não é forte, e que a culinária brasileira, baseada nas receitas analisadas, apresenta uma diversidade equilibrada, misturando tanto ingredientes semelhantes quanto contrastantes.

Com relação a assortatividade o grafo apresentou um coeficiente de -0,0825, indicando uma leve heterofilia. Isso significa que há uma pequena tendência para combinar ingredientes de tipos diferentes (como proteínas com carboidratos, ou frutas com laticínios). Como o valor é muito próximo de zero, essa preferência não é forte, sugerindo que a culinária brasileira analisada a partir do banco criado possui uma diversidade equilibrada, mesclando tanto ingredientes similares quanto contrastantes em suas receitas.

***

### Conclusão:

A construção e análise do grafo de co-ocorrência de ingredientes proporcionaram uma aplicação prática dos conceitos de grafos estudados na disciplina de Algoritmos e Estruturas de Dados. A partir de um conjunto de mais de 50 receitas da culinária brasileira, foi possível representar as relações entre ingredientes de forma estruturada, utilizando grafos não direcionados e ponderados.

O cálculo do coeficiente de assortatividade por tipo de ingrediente resultou em um valor de -0,0825, indicando uma ligeira tendência à combinação de ingredientes de tipos diferentes. No entanto, como o valor é bastante próximo de zero, conclui-se que a gastronomia brasileira, nas receitas analisadas, não apresenta uma preferência forte nem por combinações homogêneas nem por contrastantes, evidenciando uma diversidade equilibrada na escolha dos ingredientes.

Este trabalho reforça a importância do estudo de estruturas de dados como os grafos para a modelagem de sistemas complexos, demonstrando sua aplicabilidade em contextos variados além da computação tradicional, como na análise de padrões culturais e gastronômicos.