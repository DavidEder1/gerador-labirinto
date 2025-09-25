# gerador-labirinto

Um jogo simples de exploração de labirinto desenvolvido para ser jogado diretamente no terminal (CLI - Command Line Interface), utilizando a biblioteca nativa `curses` do Python para a interface gráfica.

---

## Funcionalidades Principais

* **Geração de Labirinto Procedural:** O sistema cria labirintos de dimensões ímpares (padrão **71x21**) usando um algoritmo de geração de trilhas (backtracking recursivo), garantindo mapas únicos a cada geração.
* **Elementos do Jogo:**
    * **Início (`S`):** Ponto de partida do explorador.
    * **Saída (`E`):** Objetivo final para vencer o jogo.
    * **Itens (`*`):** Objetos colecionáveis que aumentam o score do jogador, meramente simbolico.
* **Interface Gráfica (`curses`):** Utiliza cores e caracteres ANSI para renderizar o ambiente de forma dinâmica.
* **Viewport Fixo:** O mapa é exibido em uma janela de visualização fixa e centralizada (padrão **19x19 células**), que se move para acompanhar o jogador (`@`) pelo labirinto.
* **Placar e Status:** Exibe o score atual e o total de itens colecionáveis.
* **Salvamento de Mapa:** O labirinto gerado é salvo em um arquivo JSON para permitir recarregamento.

---

## Controles do Jogo

O jogo aceita tanto as setas direcionais quanto as teclas WASD para movimentação.

| Ação | Tecla(s) |
| :--- | :--- |
| **Mover Cima** | `W` ou `Seta para Cima` |
| **Mover Baixo** | `S` ou `Seta para Baixo` |
| **Mover Esquerda** | `A` ou `Seta para Esquerda` |
| **Mover Direita** | `D` ou `Seta para Direita` |
| **Sair do Jogo** | `Q` |

**Atenção:** Certifique-se de que sua janela do terminal esteja grande o suficiente. O jogo exige um tamanho mínimo e exibirá o aviso **"TERMINAL MUITO PEQUENO!"** caso as dimensões não sejam adequadas.

---

## Estrutura do Código

O código é modularizado em três classes principais:

1.  **`CursesTools`:** Classe de utilidades para garantir a segurança e estabilidade da renderização no terminal.
2.  **`GeradorLabirinto`:** Implementa a lógica de criação do labirinto (algoritmo de trilhas) e define os elementos do jogo (`S`, `E`, `*`).
3.  **`ExplorarMapa`:** Contém o *game loop*, a lógica de movimentação, tratamento de colisões e o gerenciamento da Viewport fixa.