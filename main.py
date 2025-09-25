import curses
import random
import json
import os

# ========================
# UTILIDADES CURSES E CONFIGURAÇÕES
# ========================
class CursesTools:
    """Métodos estáticos para lidar com escrita segura e limites do terminal."""
    
    @staticmethod
    def safeAddstr(stdscr, y, x, string, cor=0):
        """Escreve uma string de forma segura, limitando-se ao tamanho da tela."""
        try:
            rows, cols = stdscr.getmaxyx()
            if 0 <= y < rows and 0 <= x < cols:
                maxLen = cols - x
                if maxLen > 0:
                    stdscr.addstr(y, x, string[:maxLen], cor)
        except curses.error:
            pass

    @staticmethod
    def safeAddch(stdscr, y, x, ch, cor=0):
        """Escreve um único caractere de forma segura."""
        try:
            rows, cols = stdscr.getmaxyx()
            if 0 <= y < rows and 0 <= x < cols:
                stdscr.addch(y, x, ch, cor)
        except curses.error:
            pass

    @staticmethod
    def checkTerminalSize(stdscr, minLines, minCols):
        """Verifica e exibe mensagem se o terminal for muito pequeno."""
        rows, cols = stdscr.getmaxyx()
        
        if rows < minLines or cols < minCols:
            stdscr.clear()
            # Centraliza a mensagem de erro
            centerX = (cols - 40) // 2 
            centerX = max(0, centerX)

            CursesTools.safeAddstr(stdscr, 0, centerX, "=" * min(cols, 40), curses.A_BOLD)
            if rows > 1:
                CursesTools.safeAddstr(stdscr, 1, centerX, "TERMINAL MUITO PEQUENO!", curses.A_BOLD | curses.color_pair(2))
            if rows > 2:
                CursesTools.safeAddstr(stdscr, 2, centerX, f"Min: {minLines}L x {minCols}C | Atual: {rows}L x {cols}C")
            if rows > 3:
                CursesTools.safeAddstr(stdscr, 3, centerX, "Aumente o terminal ou Q para sair.")
            stdscr.refresh()
            return False
        return True


# ========================
# GERADOR DE LABIRINTO
# ========================
class GeradorLabirinto:
    def __init__(self, nColunas=71, nLinhas=21):
        # Garante que as dimensões sejam ímpares para o algoritmo de labirinto
        self.nColunas = nColunas if nColunas % 2 != 0 else nColunas + 1
        self.nLinhas = nLinhas if nLinhas % 2 != 0 else nLinhas + 1
        
        self.parede = '#'
        self.vazio = ' '
        self.labirinto = []
        self.arquivoSaida = f'labirinto{self.nColunas}x{self.nLinhas}.json'

        if self.nColunas != nColunas or self.nLinhas != nLinhas:
             print(f"Ajuste: Labirinto definido para {self.nLinhas}x{self.nColunas} para garantir dimensões ímpares.")

    def inicializaLabirinto(self):
        # 1. Cria o labirinto base (tudo parede)
        self.labirinto = [[self.parede for _ in range(self.nColunas)] for _ in range(self.nLinhas)]
        self.labirinto[1][1] = self.vazio
        self.criaCaminho(1, 1)

        # 2. Encontra todos os becos sem saída para S e E
        becosDisponiveis = self.encontraBecosSemSaida()
        
        if len(becosDisponiveis) < 2:
             # Caso não encontre becos suficientes, usa o padrão
             spawnPos = (1, 1)
             exitPos = (self.nLinhas - 2, self.nColunas - 2)
             print("Aviso: Não foram encontrados becos sem saída suficientes. Usando posições padrão.")
        else:
            # Sorteia duas posições distintas (S e E) de becos
            spawnPos, exitPos = random.sample(becosDisponiveis, 2)

        # 3. Define o Ponto de Partida e o Ponto de Chegada
        self.labirinto[spawnPos[0]][spawnPos[1]] = 'S'
        self.labirinto[exitPos[0]][exitPos[1]] = 'E'
        posicoesExcluidas = {spawnPos, exitPos}

        # 4. Adiciona Itens (*)
        vaziosDisponiveis = [(y, x) for y in range(1, self.nLinhas - 1) 
                              for x in range(1, self.nColunas - 1) 
                              if self.labirinto[y][x] == self.vazio and (y, x) not in posicoesExcluidas]
        
        nItens = min(10, len(vaziosDisponiveis))
        if vaziosDisponiveis:
            for y, x in random.sample(vaziosDisponiveis, nItens):
                self.labirinto[y][x] = '*'

        self.exportaLabirinto()
        return self.labirinto
    
    def encontraBecosSemSaida(self):
        """Encontra todas as células 'vazio' que têm exatamente um vizinho 'vazio'."""
        becos = []
        direcoes = [(0, 1), (0, -1), (1, 0), (-1, 0)] # Vizinhos ortogonais
        
        for y in range(1, self.nLinhas - 1):
            for x in range(1, self.nColunas - 1):
                
                if self.labirinto[y][x] == self.vazio:
                    vizinhosVazios = 0
                    
                    for dy, dx in direcoes:
                        ny, nx = y + dy, x + dx
                        
                        if 1 <= ny < self.nLinhas - 1 and 1 <= nx < self.nColunas - 1:
                            # Conta vizinhos que NÃO são parede
                            if self.labirinto[ny][nx] != self.parede:
                                vizinhosVazios += 1
                                
                    # Um beco sem saída tem apenas 1 conexão de caminho
                    if vizinhosVazios == 1:
                        becos.append((y, x))
                        
        return becos
    
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
        with open(self.arquivoSaida, 'w') as f:
            json.dump(self.labirinto, f)


# ========================
# EXPLORADOR DO LABIRINTO (Com Viewport Fixa e Centralizada)
# ========================
class ExplorarMapa:
    # Constantes
    FIXED_VIEWPORT_LINES = 19
    FIXED_VIEWPORT_CELLS = 19 
    
    # Espaço reservado para o placar e margem
    minReserveLines = 5
    minReserveCols = 5 
    
    def __init__(self):
        self.parede = '#'
        self.vazio = ' '
        self.item = '*'
        self.saida = 'E'
        self.personagem = '@'
        self.labirinto = []
        self.posicaoX = 0
        self.posicaoY = 0
        self.offsetX = 0
        self.offsetY = 0
        self.score = 0
        self.totalItens = 0
        self.gameOver = False
        
        self.nLinhasVisiveis = self.FIXED_VIEWPORT_LINES
        self.nColunasVisiveis = self.FIXED_VIEWPORT_CELLS

    def carregaLabirinto(self, arquivo):
        try:
            with open(arquivo, 'r') as f:
                self.labirinto = json.load(f)
        except FileNotFoundError:
            print(f"Arquivo '{arquivo}' não encontrado. Gerando um novo mapa padrão (71x21)...")
            gerador = GeradorLabirinto(71, 21)
            self.labirinto = gerador.inicializaLabirinto()
            print("Mapa gerado. Pressione Enter para continuar...")
            input()
        
        self.nLinhas = len(self.labirinto)
        self.nColunas = len(self.labirinto[0]) if self.nLinhas > 0 else 0
        self.posicaoX, self.posicaoY = self.encontraPosicaoInicial()
        self.totalItens = sum(linha.count(self.item) for linha in self.labirinto)
    
    def encontraPosicaoInicial(self):
        for y, linha in enumerate(self.labirinto):
            for x, celula in enumerate(linha):
                if celula == 'S':
                    return x, y
        return 1, 1 # Fallback

    def atualizaOffset(self):
        meioX = self.nColunasVisiveis // 2
        meioY = self.nLinhasVisiveis // 2
        
        self.offsetX = self.posicaoX - meioX
        self.offsetY = self.posicaoY - meioY

        if self.offsetX < 0: self.offsetX = 0
        if self.offsetY < 0: self.offsetY = 0
            
        if self.nColunasVisiveis < self.nColunas and self.offsetX + self.nColunasVisiveis > self.nColunas:
            self.offsetX = self.nColunas - self.nColunasVisiveis
        if self.nLinhasVisiveis < self.nLinhas and self.offsetY + self.nLinhasVisiveis > self.nLinhas:
            self.offsetY = self.nLinhas - self.nLinhasVisiveis

        if self.offsetX < 0: self.offsetX = 0
        if self.offsetY < 0: self.offsetY = 0

    def exibeMapa(self, stdscr):
        rows, cols = stdscr.getmaxyx()

        # 1. CÁLCULO DO TAMANHO MÍNIMO NECESSÁRIO (CONSIDERANDO BORDAS)
        minLinesNeeded = self.FIXED_VIEWPORT_LINES + 2 + self.minReserveLines 
        minColsNeeded = (self.FIXED_VIEWPORT_CELLS * 2) + 2 + self.minReserveCols
        
        # 2. VERIFICAÇÃO DO TAMANHO
        if not CursesTools.checkTerminalSize(stdscr, minLinesNeeded, minColsNeeded):
            return 
            
        stdscr.clear()
        self.atualizaOffset() 
        
        # 3. CÁLCULO DA POSIÇÃO DA JANELA
        winHeight = self.nLinhasVisiveis + 2
        winWidth = (self.nColunasVisiveis * 2) + 2 
        
        # Posição de início da Janela (Centralizada)
        startX = (cols - winWidth) // 2
        startX = max(0, startX)
        startY = (rows - (winHeight + self.minReserveLines)) // 2 
        startY = max(0, startY)
        
        # 4. CRIAÇÃO E DESENHO DA BORDA USANDO 'subwin'
        try:
            # Cria a sub-janela para o mapa (altura, largura, y inicial, x inicial)
            mapWin = stdscr.subwin(winHeight, winWidth, startY, startX)
            
            # Desenha o quadro completo
            mapWin.border()
            mapWin.refresh()
            
            corBorda = curses.color_pair(2) 
        except curses.error:
            return

        # 5. DESENHA O MAPA DENTRO DA JANELA (Offset de +1 para ignorar a borda)
        for y in range(self.nLinhasVisiveis):
            for x in range(self.nColunasVisiveis):
                
                # Coordenadas relativas à 'mapWin' (+1 para ignorar a borda)
                screenY = y + 1 
                screenX = (x * 2) + 1 
                
                mapaX = x + self.offsetX
                mapaY = y + self.offsetY
                
                if 0 <= mapaX < self.nColunas and 0 <= mapaY < self.nLinhas:
                    char = self.labirinto[mapaY][mapaX]
                    displayChar = char
                    cor = curses.color_pair(5)

                    if mapaX == self.posicaoX and mapaY == self.posicaoY:
                        displayChar = self.personagem
                        cor = curses.color_pair(1)
                    elif char == self.parede:
                        cor = corBorda
                    elif char == self.item:
                        cor = curses.color_pair(3)
                    elif char == self.saida:
                        cor = curses.color_pair(4)
                        
                    CursesTools.safeAddch(mapWin, screenY, screenX, displayChar, cor)

        mapWin.refresh() # Atualiza o conteúdo da sub-janela
        
        # 6. Desenha o placar/status (no stdscr)
        infoLinha = startY + winHeight + 1 # Abaixo da borda inferior
        placarWidth = winWidth
        
        CursesTools.safeAddstr(stdscr, infoLinha, startX, "=" * placarWidth, curses.A_NORMAL)
        CursesTools.safeAddstr(stdscr, infoLinha + 1, startX, f"Score: {self.score} / {self.totalItens} itens coletados", curses.color_pair(3))
        CursesTools.safeAddstr(stdscr, infoLinha + 2, startX, "Q: Sair | Setas/WASD: Mover", curses.color_pair(2))
        
        if self.gameOver:
            msg = "VITÓRIA! Aperte 'Q' para sair."
            CursesTools.safeAddstr(stdscr, infoLinha + 4, startX, msg, curses.A_BOLD | curses.color_pair(1))

        stdscr.refresh()
                    
    def movePersonagem(self, key):
        if self.gameOver:
            return
            
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
                destino = self.labirinto[novaY][novaX]
                
                if destino == self.parede:
                    return
                
                self.posicaoX, self.posicaoY = novaX, novaY
                
                if destino == self.item:
                    self.score += 1
                    self.labirinto[novaY][novaX] = self.vazio 
                
                elif destino == self.saida:
                    self.gameOver = True
                    

    def loopPrincipal(self, stdscr):
        curses.curs_set(0)
        
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_BLACK)
        
        stdscr.nodelay(True)
        stdscr.timeout(100)

        while True:
            self.exibeMapa(stdscr) 
            key = stdscr.getch()
            
            if key == ord('q') or key == ord('Q'):
                break
            
            self.movePersonagem(key)

    def iniciarExploracao(self, arquivo):
        self.carregaLabirinto(arquivo)
        curses.wrapper(self.loopPrincipal)

# ========================
# MAIN
# ========================
if __name__ == '__main__':
    
    # --- VARIÁVEIS DE CONTROLE DE TAMANHO DO MAPA ---
    mapaColunas = 71
    mapaLinhas = 21
    # ------------------------------------------------
    
    arquivoBase = f'labirinto{mapaColunas}x{mapaLinhas}'
    arquivo = arquivoBase + '.json'
    
    print('Deseja gerar um novo mapa? (s/n)')
    resposta = input().strip().lower()
    
    if resposta == 's':
        gerador = GeradorLabirinto(mapaColunas, mapaLinhas)
        print(f"Gerando labirinto {gerador.nColunas}x{gerador.nLinhas}...")
        gerador.inicializaLabirinto()
        arquivo = gerador.arquivoSaida
        print(f"Mapa gerado e salvo em {arquivo}")
    elif not os.path.exists(arquivo):
        print(f"Arquivo '{arquivo}' não encontrado. Gerando um novo mapa padrão para iniciar...")
        gerador = GeradorLabirinto(mapaColunas, mapaLinhas)
        gerador.inicializaLabirinto()
        arquivo = gerador.arquivoSaida

    
    print("Iniciando explorador. Use Q para sair, WASD ou setas para mover.")
    explorador = ExplorarMapa()
    explorador.iniciarExploracao(arquivo)