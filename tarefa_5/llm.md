# Informações sobre o Uso da LLM

## 🤖 Modelos de Linguagem Utilizados
- **ChatGPT 4.0** (OpenAI)
- **Claude**
- **Gemini**
---

## 🎯 Objetivo do Uso da LLM
O modelo foi utilizado para nos auxiliar na estrutura e na compararação de algoritmos de roteamento com base em métricas de eficiência computacional e impacto ambiental.  
Foram avaliados quatro algoritmos:

- Dijkstra MinHeap  
- A*  
- Dijkstra Tradicional  
- A* Random (sem clustering)

---

## 💬 Prompts Utilizados

> Escreva um código em python que leia um arquivo csv e retorne um arquivo json

> Tenho um grafo da cidade de natal com 65 pontos. Preciso separá-los em 10 subgrafos com os pontos mais proximos uns dos outros, me sugira algum metodo eficaz para fazer isso

> Eu implementei dijkstra sem heap e está demorando horas e não acaba de executar. Quais fatores estão causando essa lentidão e como posso otimizar sem usar min-heap?

> Ao executar o roteamento para o Cluster 9, minha função retornou: 
>
> Cluster 9: 321 nós, inf km. 
>
>O que significa esse inf km e como posso resolver essa distância infinita?

> Gere uma tabela comparativa em Markdown com base nos dados de execução de quatro algoritmos de roteamento (Dijkstra MinHeap, A*, Dijkstra Tradicional e A* Random sem clustering). Para cada algoritmo, forneça:
> 
> - Emissão de CO₂ em gramas (converter de kg para g, ou seja, multiplicar por 1000)
> - Energia consumida em Wh (converter de kWh para Wh)
> - Tempo de execução em segundos
> - Eficiência por km (CO₂/km e energia/km)
>
> Se a distância total for infinita, coloque “—” nas colunas de eficiência. Formate o resultado como uma tabela Markdown pronta para colar no README.md.

---



