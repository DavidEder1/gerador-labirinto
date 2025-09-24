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
        self.labirinto = [[self.parede for _ in range(self.nColunas)] for _ in range(self.nLinhas)]

        for linha in range(1, self.nLinhas, self.nVazio):
            for coluna in range(1, self.nColunas, self.nVazio):
                self.labirinto[linha][coluna] = self.vazio
                self.criaCaminho(linha, coluna)

        self.labirinto[1][1] = 'S'
        self.labirinto[self.nLinhas - 2][self.nColunas - 2] = 'E'

        # adiciona itens aleatórios
        for _ in range(10):
            while True:
                y = random.randint(1, self.nLinhas - 2)
                x = random.randint(1, self.nColunas - 2)
                if self.labirinto[y][x] == self.vazio:
                    self.labirinto[y][x] = '*'
                    break

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
        self.item = '*'
        self.saida = 'E'
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
        self.atualizaOffset()
        return self.labirinto
    
    def encontraPosicaoInicial(self):
        for y, linha in enumerate(self.labirinto):
            for x, celula in enumerate(linha):
                if celula == 'S':
                    return x, y
        return 1, 1
    
    def atualizaOffset(self):
        meioX = self.nColunasVisiveis // 2
        meioY = self.nLinhasVisiveis // 2
        self.offsetX = self.posicaoX - meioX
        self.offsetY = self.posicaoY - meioY

        if self.offsetX < 0:
            self.offsetX = 0
        if self.offsetY < 0:
            self.offsetY = 0
        if self.offsetX + self.nColunasVisiveis > self.nColunas:
            self.offsetX = self.nColunas - self.nColunasVisiveis
        if self.offsetY + self.nLinhasVisiveis > self.nLinhas:
            self.offsetY = self.nLinhas - self.nLinhasVisiveis

    def exibeMapa(self, stdscr):
        stdscr.clear()
        for y in range(self.nLinhasVisiveis):
            for x in range(self.nColunasVisiveis):
                col = x * 2
                mapaX = x + self.offsetX
                mapaY = y + self.offsetY
                if 0 <= mapaX < self.nColunas and 0 <= mapaY < self.nLinhas:
                    char = self.labirinto[mapaY][mapaX]
                    if mapaX == self.posicaoX and mapaY == self.posicaoY:
                        # stdscr.addstr(y, col, self.personagem, curses.color_pair(1))
                        personagem = utilidadesCurses()
                        personagem.stdscr = stdscr
                        personagem.x = col
                        personagem.y = y
                        personagem.cor = curses.color_pair(1)
                        personagem.safeAddch(self.personagem)
                    elif char == self.parede:
                        # stdscr.addstr(y, col, char, curses.color_pair(2))
                        parede = utilidadesCurses()
                        parede.stdscr = stdscr
                        parede.x = col
                        parede.y = y
                        parede.cor = curses.color_pair(2)
                        parede.safeAddch(char)
                    elif char == self.item:
                        # stdscr.addstr(y, col, char, curses.color_pair(3))
                        item = utilidadesCurses()
                        item.stdscr = stdscr
                        item.x = col
                        item.y = y
                        item.cor = curses.color_pair(3)
                        item.safeAddch(char)
                    elif char == self.saida:
                        # stdscr.addstr(y, col, char, curses.color_pair(4))
                        saida = utilidadesCurses()
                        saida.stdscr = stdscr
                        saida.x = col
                        saida.y = y
                        saida.cor = curses.color_pair(4)
                        saida.safeAddch(char)
                    else:
                        # stdscr.addstr(y, col, char, curses.color_pair(5))
                        vazio = utilidadesCurses()
                        vazio.stdscr = stdscr
                        vazio.x = col
                        vazio.y = y
                        vazio.cor = curses.color_pair(5)
                        vazio.safeAddch(char)
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
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # personagem
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)  # parede
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # item
        curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)   # saída
        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_BLACK)  # vazio
        stdscr.nodelay(True)
        stdscr.timeout(100)
        while True:
            self.exibeMapa(stdscr)
            key = stdscr.getch()
            if key == ord('q'):
                break
            self.movePersonagem(key)

# ========================
# OBJETOS
# ========================
class objeto:
    def __init__(self):
        self.nome = ''
        self.descricao = ''
        self.posiX = 0
        self.posiY = 0
    
    def definirObjeto(self, nome, descricao, posiX, posiY):
        self.nome = nome
        self.descricao = descricao
        self.posiX = posiX
        self.posiY = posiY

    def propriedades(self):
        tipos = {
            'solido': 'Sólido',
            'coletavel': 'Coletável',
            'interativo': 'Interativo',
        }
        cores = {
            'solido': curses.COLOR_WHITE,
            'coletavel': curses.COLOR_YELLOW,
            'interativo': curses.COLOR_CYAN
        }
        return tipos.get(self.nome, 'Desconhecido'), cores.get(self.nome, curses.COLOR_MAGENTA)
    
    def exibir(self, stdscr):
        tipo, cor = self.propriedades()
        
# ========================
# UTILIDADES CURSES
# ========================
class utilidadesCurses:
    def __init__(self):
        self.stdscr = None
        self.x = 0
        self.y = 0
        self.coluna = 0
        self.linha = 0
        self.minLinha = 0
        self.minColuna = 0
        self.coresAtivos = False
        self.cor = curses.COLOR_WHITE
        
    def safeAddstr(self, string):
        try:
            rows, cols = self.stdscr.getmaxyx()
            # Verifica se a posição é válida dentro da tela
            if self.y < 0 or self.y >= rows or self.x < 0 or self.x >= cols:
                return
            # Calcula quantos caracteres ainda cabem na linha
            maxLen = cols - self.x
            if maxLen <= 0:
                return
            # Escreve o texto limitado ao espaço disponível
            self.stdscr.addstr(self.y, self.x, string[:maxLen])
        except curses.error:
            pass  # Ignora erros do curses quando não dá pra escrever

    def safeAddch(self, ch):
        try:
            rows, cols = self.stdscr.getmaxyx()
            # Só escreve se estiver dentro da tela
            if 0 <= self.y < rows and 0 <= self.x < cols:
                # ch deve ser apenas um caractere
                self.stdscr.addch(self.y, self.x, ch, self.cor)
        except curses.error:
            pass

    def safeTerminalSize(self):
        # Verifica se o terminal atende os requisitos mínimos
        if self.linha < self.minLinha or self.coluna < self.minColuna:
            # Se for muito pequeno, mostra mensagens adaptadas
            if self.linha < 3:
                if self.linha >= 1 and self.linha >= 20:
                    self.safeAddstr("TERMINAL MUITO PEQUENO!")
                if self.linha >= 2 and self.coluna >= 15:
                    self.safeAddstr(f"{self.linha}L x {self.coluna}C - AUMENTE O TERMINAL!")
            else:
                # Mostra informações mais completas quando tem mais linhas
                self.safeAddstr('=' * min(40, self.coluna))
                if self.linha >= 2:
                    self.safeAddstr('TERMINAL MUITO PEQUENO!')
                if self.linha >= 3:
                    self.safeAddstr(f'Min: {self.minLinha}L x {self.minColuna}C')
                if self.linha >= 4:
                    self.safeAddstr(f'Atual: {self.linha}L x {self.coluna}C')
                if self.linha >= 5:
                    self.safeAddstr('Aumente o terminal ou Q para sair')
            # Retorna True para indicar que não dá pra rodar o jogo
            return True
        return False

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

