# README

---

## Introdução
Este trabalho tem como objetivo criar um tutorial no formato "handOn" em um jupyter notebook, que faça uma introdução ao uso de grafos e à bibloteca NetworkX com o auxilio de uma inteligencia artificial generativa. 

---

## Método Utilizado
O notebook foi criado com o auxilio de uma IA Generativa, para tal, foi escolhida o DeepSeek. Para construção do prompt foi seguido o modelo exposto pelo Engenheiro de IA [Dan Mac](https://x.com/daniel_mac8) que segue o seguinte padrão:

- O que se deseja;
- Formato de retorno desejado;
- Advertências;
- Contexto;

O prompt utilizado foi 


>"Quero que você faça um tutorial de introdução a grafos enfatizando a prática, ou seja, no estilo hand's on. Para isso você deve usar o arquivo Atlas.pdf que foi fornecido 
>como principal fonte teórica de informação.
>
>Esse tutorial deverá ser um notebook com a mesma estrutura usada no
arquivo NetworkElementsI.ipynb anexado e deverá ser escrito em portugês.
>
>Não será admitido outro formato e a ausencia de instruções práticas. Use como teoria apenas o arquivo Atlas.pdf anexado utilizando cada parte que considerar importante.
>
>Sou estudante do curso de Engenharia da Computação, e neste semestre na disciplina de Algoritmo e Estrutura de Dados 2 estou estudando Grafos com teoria e aplicações,
>e ao longo do estudo vi a nessecidade de um tutorial prático que podesse me lembrar dos principais conceitos estudados vistos, ele deve me ajudar a por em pratica os conceitos
>aprendidos e revisar a parte essencial da teoria, como um guia prático o qual eu possa recorrer ao longo do semestre de forma rápida."

Para o referêncial teórico foi passada para o DeepSeek dois arquivos:
- Um PDF com os capitulos 6 e 7 do livro _The Atlas For The Aspiring Network Scientist_ que tratam do assunto em questão;
- Um arquivo .ipynb com um modelo de tutorial semelhante ao requerido.

---

## Resultado

Como resultado obtivemos o tutorial em formato jupyter notebook com um compilado dos tipos de grafos acompanhado de sua teoria e blocos de código com exemplos de aplicação utilizando a mencionada biblioteca NetworkX. Foi inserido ainda dois exercicios para fixação do conteúdo.
