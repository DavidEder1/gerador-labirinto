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
    def safe_addstr(stdscr, y, x, string, cor=0):
        """Escreve uma string de forma segura, limitando-se ao tamanho da tela."""
        try:
            rows, cols = stdscr.getmaxyx()
            if 0 <= y < rows and 0 <= x < cols:
                max_len = cols - x
                if max_len > 0:
                    stdscr.addstr(y, x, string[:max_len], cor)
        except curses.error:
            pass

    @staticmethod
    def safe_addch(stdscr, y, x, ch, cor=0):
        """Escreve um único caractere de forma segura."""
        try:
            rows, cols = stdscr.getmaxyx()
            if 0 <= y < rows and 0 <= x < cols:
                stdscr.addch(y, x, ch, cor)
        except curses.error:
            pass

    @staticmethod
    def check_terminal_size(stdscr, min_lines, min_cols):
        """Verifica e exibe mensagem se o terminal for muito pequeno."""
        rows, cols = stdscr.getmaxyx()
        
        # Se a linha ou coluna for menor que o necessário, exibe a mensagem de erro.
        if rows < min_lines or cols < min_cols:
            stdscr.clear()
            CursesTools.safe_addstr(stdscr, 0, 0, "=" * min(cols, 40), curses.A_BOLD)
            if rows > 1:
                CursesTools.safe_addstr(stdscr, 1, 0, "TERMINAL MUITO PEQUENO!", curses.A_BOLD | curses.color_pair(2))
            if rows > 2:
                CursesTools.safe_addstr(stdscr, 2, 0, f"Min: {min_lines}L x {min_cols}C | Atual: {rows}L x {cols}C")
            if rows > 3:
                CursesTools.safe_addstr(stdscr, 3, 0, "Aumente o terminal ou Q para sair.")
            stdscr.refresh()
            return False
        return True


# ========================
# GERADOR DE LABIRINTO (Inalterado)
# ========================
class GeradorLabirinto:
    def __init__(self, n_colunas=71, n_linhas=21):
        self.nColunas = n_colunas if n_colunas % 2 != 0 else n_colunas + 1
        self.nLinhas = n_linhas if n_linhas % 2 != 0 else n_linhas + 1
        
        self.parede = '#'
        self.vazio = ' '
        self.labirinto = []
        self.arquivo_saida = f'labirinto{self.nColunas}x{self.nLinhas}.json'

        if self.nColunas != n_colunas or self.nLinhas != n_linhas:
             print(f"Ajuste: Labirinto definido para {self.nLinhas}x{self.nColunas} para garantir dimensões ímpares.")

    def inicializaLabirinto(self):
        self.labirinto = [[self.parede for _ in range(self.nColunas)] for _ in range(self.nLinhas)]
        self.labirinto[1][1] = self.vazio
        self.criaCaminho(1, 1)

        self.labirinto[1][1] = 'S'
        self.labirinto[self.nLinhas - 2][self.nColunas - 2] = 'E'

        vazios_disponiveis = [(y, x) for y in range(1, self.nLinhas - 1) 
                              for x in range(1, self.nColunas - 1) 
                              if self.labirinto[y][x] == self.vazio]
        
        n_itens = min(10, len(vazios_disponiveis))
        if vazios_disponiveis:
            for y, x in random.sample(vazios_disponiveis, n_itens):
                self.labirinto[y][x] = '*'

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
        with open(self.arquivo_saida, 'w') as f:
            json.dump(self.labirinto, f)


# ========================
# EXPLORADOR DO LABIRINTO (Com Viewport Fixa)
# ========================
class ExplorarMapa:
    # Definindo um tamanho fixo de viewport (19 células de altura x 19 células de largura)
    FIXED_VIEWPORT_LINES = 19
    FIXED_VIEWPORT_CELLS = 19
    
    # Espaço reservado para o placar e margem
    MIN_RESERVE_LINES = 5
    MIN_RESERVE_COLS = 5 
    
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
        self.total_itens = 0
        self.game_over = False
        
        # A viewport fixa é definida pelas constantes
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
        self.total_itens = sum(linha.count(self.item) for linha in self.labirinto)
    
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

        if self.offsetX < 0: self.offsetX = 0
        if self.offsetY < 0: self.offsetY = 0
            
        if self.nColunasVisiveis < self.nColunas and self.offsetX + self.nColunasVisiveis > self.nColunas:
            self.offsetX = self.nColunas - self.nColunasVisiveis
        if self.nLinhasVisiveis < self.nLinhas and self.offsetY + self.nLinhasVisiveis > self.nLinhas:
            self.offsetY = self.nLinhas - self.nLinhasVisiveis

        if self.offsetX < 0: self.offsetX = 0
        if self.offsetY < 0: self.offsetY = 0

    def exibeMapa(self, stdscr):
        # 1. TAMANHO MÍNIMO NECESSÁRIO (FIXO)
        min_lines_needed = self.FIXED_VIEWPORT_LINES + self.MIN_RESERVE_LINES 
        min_cols_needed = (self.FIXED_VIEWPORT_CELLS * 2) + self.MIN_RESERVE_COLS
        
        # 2. VERIFICA SE O TERMINAL ATENDE AO MÍNIMO FIXO
        if not CursesTools.check_terminal_size(stdscr, min_lines_needed, min_cols_needed):
            return 
            
        stdscr.clear()
        self.atualizaOffset() # Atualiza o offset com a viewport fixa
        
        # Desenha o mapa
        for y in range(self.nLinhasVisiveis):
            for x in range(self.nColunasVisiveis):
                col = x * 2 
                mapaX = x + self.offsetX
                mapaY = y + self.offsetY
                
                if 0 <= mapaX < self.nColunas and 0 <= mapaY < self.nLinhas:
                    char = self.labirinto[mapaY][mapaX]
                    display_char = char
                    cor = curses.color_pair(5) # Default: Vazio

                    if mapaX == self.posicaoX and mapaY == self.posicaoY:
                        # Personagem (@)
                        display_char = self.personagem
                        cor = curses.color_pair(1)
                    elif char == self.parede:
                        cor = curses.color_pair(2)
                    elif char == self.item:
                        cor = curses.color_pair(3)
                    elif char == self.saida:
                        cor = curses.color_pair(4)
                        
                    CursesTools.safe_addch(stdscr, y, col, display_char, cor)
        
        # Desenha o placar/status
        info_linha = self.nLinhasVisiveis + 1
        placar_width = self.nColunasVisiveis * 2
        
        CursesTools.safe_addstr(stdscr, info_linha, 0, "=" * placar_width, curses.A_NORMAL)
        CursesTools.safe_addstr(stdscr, info_linha + 1, 0, f"Score: {self.score} / {self.total_itens} itens coletados", curses.color_pair(3))
        CursesTools.safe_addstr(stdscr, info_linha + 2, 0, "Q: Sair | Setas/WASD: Mover", curses.color_pair(2))
        
        if self.game_over:
            msg = "VITÓRIA! Aperte 'Q' para sair."
            CursesTools.safe_addstr(stdscr, info_linha + 4, 0, msg, curses.A_BOLD | curses.color_pair(1))

        stdscr.refresh()
                    
    def movePersonagem(self, key):
        if self.game_over:
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
                
                # Interação
                if destino == self.item:
                    self.score += 1
                    self.labirinto[novaY][novaX] = self.vazio 
                
                elif destino == self.saida:
                    self.game_over = True
                    

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
    # Estes valores controlam o tamanho do LABIRINTO inteiro, e não a tela visível.
    MAPA_COLUNAS = 71
    MAPA_LINHAS = 21
    # ------------------------------------------------
    
    arquivo_base = f'labirinto{MAPA_COLUNAS}x{MAPA_LINHAS}'
    arquivo = arquivo_base + '.json'
    
    print('Deseja gerar um novo mapa? (s/n)')
    resposta = input().strip().lower()
    
    if resposta == 's':
        gerador = GeradorLabirinto(MAPA_COLUNAS, MAPA_LINHAS)
        print(f"Gerando labirinto {gerador.nColunas}x{gerador.nLinhas}...")
        gerador.inicializaLabirinto()
        arquivo = gerador.arquivo_saida
        print(f"Mapa gerado e salvo em {arquivo}")
    elif not os.path.exists(arquivo):
        print(f"Arquivo '{arquivo}' não encontrado. Gerando um novo mapa padrão para iniciar...")
        gerador = GeradorLabirinto(MAPA_COLUNAS, MAPA_LINHAS)
        gerador.inicializaLabirinto()
        arquivo = gerador.arquivo_saida

    
    print("Iniciando explorador. Use Q para sair, WASD ou setas para mover.")
    explorador = ExplorarMapa()
    explorador.iniciarExploracao(arquivo)
