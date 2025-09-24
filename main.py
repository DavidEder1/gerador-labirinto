import curses, random, json

# ========================
# GERADOR DE LABIRINTO
# ========================
class geradorLabirinto:
    def __init__(self):
        self.nColunas = 50
        self.nLinhas = 50
        self.nVazio = 2
        self.parede = '#'
        self.vazio = ' '
        self.labirinto = []

    def inicializaLabirinto(self):
        # Começa com tudo parede
        self.labirinto = [[self.parede for _ in range(self.nColunas)] for _ in range(self.nLinhas)]

        # Cria pontos de entrada para o algoritmo cavar
        for linha in range(1, self.nLinhas, self.nVazio):
            for coluna in range(1, self.nColunas, self.nVazio):
                self.labirinto[linha][coluna] = self.vazio
                self.criaCaminho(linha, coluna)

        # Entrada e saída em posições acessíveis
        self.labirinto[1][1] = 'S'
        self.labirinto[self.nLinhas - 2][self.nColunas - 2] = 'E'

        # Salva o mapa em json
        self.exportaLabirinto()
        return self.labirinto
    
    def criaCaminho(self, linha, coluna):
        direcoes = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        random.shuffle(direcoes)
        for dLinha, dColuna in direcoes:
            novaLinha, novaColuna = linha + dLinha, coluna + dColuna
            if 1 <= novaLinha < self.nLinhas - 1 and 1 <= novaColuna < self.nColunas - 1:
                if self.labirinto[novaLinha][novaColuna] == self.parede:
                    self.labirinto[linha + dLinha // 2][coluna + dColuna // 2] = self.vazio
                    self.labirinto[novaLinha][novaColuna] = self.vazio
                    self.criaCaminho(novaLinha, novaColuna)
    
    def exportaLabirinto(self):
        with open(f'labirinto{self.nColunas}x{self.nLinhas}.json', 'w') as f:
            json.dump(self.labirinto, f)


# ========================
# EXPLORADOR DO LABIRINTO
# ========================
class explorarMapa:
    def __init__(self):
        self.nColunasVisiveis = 20
        self.nLinhasVisiveis = 20
        self.parede = '#'
        self.vazio = ' '
        self.personagem = '@'
        self.labirinto = []
        self.posicaoX = 1
        self.posicaoY = 1
        self.offsetX = 0
        self.offsetY = 0

    def carregaLabirinto(self, arquivo):
        with open(arquivo, 'r') as f:
            self.labirinto = json.load(f)

        self.nLinhas = len(self.labirinto)
        self.nColunas = len(self.labirinto[0]) if self.nLinhas > 0 else 0
        self.posicaoX, self.posicaoY = self.encontraPosicaoInicial()
        return self.labirinto
    
    def encontraPosicaoInicial(self):
        for y, linha in enumerate(self.labirinto):
            for x, celula in enumerate(linha):
                if celula == 'S':
                    return x, y
        return 1, 1  # fallback
    
    def exibeMapa(self, stdscr):
        stdscr.clear()
        for y in range(self.nLinhasVisiveis):
            for x in range(self.nColunasVisiveis):
                mapaX = x + self.offsetX
                mapaY = y + self.offsetY
                if 0 <= mapaX < self.nColunas and 0 <= mapaY < self.nLinhas:
                    char = self.labirinto[mapaY][mapaX]
                    if mapaX == self.posicaoX and mapaY == self.posicaoY:
                        stdscr.addstr(y, x * 2, self.personagem * 2, curses.color_pair(1))
                    else:
                        stdscr.addstr(y, x * 2, char * 2)
        stdscr.refresh()
                    
    def movePersonagem(self, key):
        novaX, novaY = self.posicaoX, self.posicaoY
        movimentos = {
            curses.KEY_UP: (0, -1), ord('w'): (0, -1),
            curses.KEY_DOWN: (0, 1), ord('s'): (0, 1),
            curses.KEY_LEFT: (-1, 0), ord('a'): (-1, 0),
            curses.KEY_RIGHT: (1, 0), ord('d'): (1, 0)
        }
        if key in movimentos:
            dx, dy = movimentos[key]
            novaX += dx
            novaY += dy
            if 0 <= novaX < self.nColunas and 0 <= novaY < self.nLinhas:
                if self.labirinto[novaY][novaX] != self.parede:
                    self.posicaoX, self.posicaoY = novaX, novaY
                    self.atualizaOffset()


    def iniciarExploracao(self, arquivo):
        self.carregaLabirinto(arquivo)
        curses.wrapper(self.loopPrincipal)

    def loopPrincipal(self, stdscr):
        curses.curs_set(0)
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        stdscr.nodelay(True)
        stdscr.timeout(100)
        while True:
            self.exibeMapa(stdscr)
            key = stdscr.getch()
            if key == ord('q'):
                break
            self.movePersonagem(key)

    def atualizaOffset(self):
        meioX = self.nColunasVisiveis // 2
        meioY = self.nLinhasVisiveis // 2
        self.offsetX = self.posicaoX - meioX
        self.offsetY = self.posicaoY - meioY

        # não deixar passar da borda esquerda/superior
        if self.offsetX < 0:
            self.offsetX = 0
        if self.offsetY < 0:
            self.offsetY = 0

        # não deixar passar da borda direita/inferior
        if self.offsetX + self.nColunasVisiveis > self.nColunas:
            self.offsetX = self.nColunas - self.nColunasVisiveis
        if self.offsetY + self.nLinhasVisiveis > self.nLinhas:
            self.offsetY = self.nLinhas - self.nLinhasVisiveis



# ========================
# MAIN
# ========================
if __name__ == '__main__':
    print('Deseja gerar outro mapa? (s/n)')
    resposta = input().strip().lower()
    if resposta == 's':
        gerador = geradorLabirinto()
        gerador.inicializaLabirinto()
        arquivo = f'labirinto{gerador.nColunas}x{gerador.nLinhas}.json'
    else:
        arquivo = 'labirinto20x20.json'

    explorador = explorarMapa()
    explorador.iniciarExploracao(arquivo)
