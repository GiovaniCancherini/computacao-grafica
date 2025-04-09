import sys
import os
import re
import time
import random
import pygame

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

class Ponto:
    def __init__(self, x: float, y: float, z: float = 0.0):  # z tem um valor padrão
        self.x = x
        self.y = y
        self.z = z
        
    def print(self) -> None:
        print("Ponto (", self.x, ",", self.y, ",", self.z, ")")

    def set(self, x: float, y: float,  z: float) -> None:
        
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        z = self.z + other.z
        return Ponto(x, y, z)

    def __sub__(self, other):
        x = self.x - other.x
        y = self.y - other.y
        z = self.z - other.z
        return Ponto(x, y, z)

    def __mul__(self, escalar: float):
        x = self.x * escalar
        y = self.y * escalar
        z = self.z * escalar
        return Ponto(x, y, z)
class RGB():
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b
class Quadrado():
    def __init__(self, ponto: Ponto, w: float, h: float, cor: RGB = RGB(1, 0, 0)):
        self.ponto = ponto
        self.w = w
        self.h = h
        self.cor = cor
        self.ponto = ponto  
        self.w = w
        self.h = h
        self.cor = cor  

    def __repr__(self):
        return f"Quadrado(Ponto={self.ponto}, w={self.w}, h={self.h}, cor={self.cor})"
####################################
# Variáveis globais
DADOS = []
TOTAL_FRAMES: int = 0
INDEX: int = 0
SCORE: int = 0
idle_ativo = True
teclas_pressionadas = set()  
####################################
# Controle de tempo para animação
tempo_antes = time.time()
soma_dt = 0
segundos = 0
frames = 1
nivel:int = 0
inicializado = False
segundos_pontuacao = 0
####################################
# Variáveis da câmera (viewport + pan)
left = 0
right = 0
top = 0
bottom = 0
panX = 0
panY = 0
REFERENCIA_SRU: float = 0.0
maiorValorX: int = 0
maiorValorY: int = 0
menorValorX: int = 0
menorValorY: int = 0
margem: int = 0
####################################
# Variáveis do triagulo
xTriangulo: float = 0.0
yTriangulo: float = 0.0
tamanhoQuadrado = 50
tamanhoTriangulo = 50
####################################

def pausarJogo():
    global idle_ativo
    idle_ativo = False
    
def retomarJogo():
    global idle_ativo
    idle_ativo = True
    
def boundingBox(triangulo_pos, triangulo_tam, quadrado_pos, quadrado_tam):
    # cria uma bounding box para o triangulo
    tri_x_min = triangulo_pos.x
    tri_x_max = triangulo_pos.x + triangulo_tam
    tri_y_min = triangulo_pos.y
    tri_y_max = triangulo_pos.y + triangulo_tam
    
    # bounding box do quadrado
    quad_x_min = quadrado_pos.x
    quad_x_max = quadrado_pos.x + quadrado_tam
    quad_y_min = quadrado_pos.y
    quad_y_max = quadrado_pos.y + quadrado_tam
    
    # verifica se sobrepoem
    if (tri_x_max < quad_x_min or tri_x_min > quad_x_max or
        tri_y_max < quad_y_min or tri_y_min > quad_y_max):
        return False  # nao ha colisao
    
    return True

def verificarColisoes():
    global DADOS, INDEX, REFERENCIA_SRU
    global xTriangulo, yTriangulo, tamanhoQuadrado, tamanhoTriangulo
    colisoes = []
    
    ponto_triangulo = Ponto(xTriangulo, yTriangulo, 0)
    tam_triangulo = 50  # Tamanho do lado do triângulo
    
    for item in DADOS:
        id_valor = item["id"]
        trios = item["trios"]
        
        if trios:
            x, y, z = trios[INDEX % len(trios)]
            ponto_quadrado = Ponto(x, y, z)
            tam_quadrado = 45  # Tamanho do lado do quadrado
            
            # Verifica colisão
            if boundingBox(ponto_triangulo, tam_triangulo, ponto_quadrado, tam_quadrado):
                colisoes.append(id_valor)
    
    return colisoes

####################################
# Desenha os eixos X e Y no mundo
def desenhaEixos():
    global left, right
    glColor3f(1, 1, 1)
    glLineWidth(1)

    glBegin(GL_LINES)
    glVertex2f(left, 0)
    glVertex2f(right, 0)
    glVertex2f(0, bottom)
    glVertex2f(0, top)
    glEnd()

    return
    
def desenhaQuadrilatero(quadrado: Quadrado):
    global REFERENCIA_SRU
    
    glColor3f(quadrado.cor.r, quadrado.cor.g, quadrado.cor.b)
    
    glPushMatrix()
    glTranslate(quadrado.ponto.x / REFERENCIA_SRU, quadrado.ponto.y / REFERENCIA_SRU, 0)
    glBegin(GL_QUADS)    
    glVertex2f(0, 0)
    glVertex2f(quadrado.w / REFERENCIA_SRU, 0)
    glVertex2f(quadrado.w / REFERENCIA_SRU, quadrado.h / REFERENCIA_SRU)
    glVertex2f(0, quadrado.h / REFERENCIA_SRU)
    glEnd()
    glPopMatrix()
    
def desenhaTriangulo(triangulo: Quadrado): 
    global REFERENCIA_SRU

    glColor3f(triangulo.cor.r, triangulo.cor.g, triangulo.cor.b)
    
    glPushMatrix()
    glTranslate(triangulo.ponto.x / REFERENCIA_SRU, triangulo.ponto.y / REFERENCIA_SRU, 0)
    glBegin(GL_TRIANGLES)
    
    glVertex2f(0, 0)
    glVertex2f(triangulo.w / REFERENCIA_SRU, 0)
    glVertex2f((triangulo.w / 2) / REFERENCIA_SRU, triangulo.h / REFERENCIA_SRU)
    
    glEnd()
    glPopMatrix()

####################################

def processarArquivo(filename):
    with open(filename, 'r') as file:
        linhas = file.readlines()

    # Primeiro valor = referencia SRU (linha 1) ? 
    referencia_SRU = int(linhas[0].replace('[', '').replace(']', '').strip())

    dados = []

    # Processar as demais linhas
    for linha in linhas[1:]:
        # Captura o ID (qualquer coisa antes do primeiro parêntese)
        match_id = re.match(r"(\d+)", linha)
        if match_id:
            id_linha = int(match_id.group(1))  # Converte ID para inteiro
        else:
            continue

        # Captura os trios dentro dos parênteses
        trios = re.findall(r"\((\d+),(\d+),(\d+)\)", linha)
        
        # Converte os valores de string para inteiros, um por um
        novos_trios = []
        for trio in trios:
            novo_trio = ()
            for numero in trio:
                numero_inteiro = int(numero)    
                novo_trio += (numero_inteiro,)  # adiciona tupla final
            novos_trios.append(novo_trio)       # adiciona o trio final na nova lista

        # Adiciona ao resultado de retorno
        dados.append({"id": id_linha, "trios": novos_trios})

        # arrow function em python para obter o maior e o menor valor
        maiorValorX = max(map(lambda trio: trio[0], novos_trios))
        maiorValorY = max(map(lambda trio: trio[1], novos_trios))
        menorValorX = min(map(lambda trio: trio[0], novos_trios))
        menorValorY = min(map(lambda trio: trio[1], novos_trios))
        
    return referencia_SRU, dados, maiorValorX, maiorValorY, menorValorX, menorValorY

def gerarCorPorID():
    # Gera componentes de cor RGB usando diferentes primos para dispersar melhor
    # https://stackoverflow.com/questions/69719050/i-am-trying-to-exclude-the-color-black-when-picking-random-colors
    # https://stackoverflow.com/questions/1168260/algorithm-for-generating-unique-colors
    
    r = ((1 * 37) % 230 + 10) / 255.0  
    g = ((1 * 59) % 230 + 10) / 255.0
    b = ((1 * 83) % 230 + 10) / 255.0

    # Evita tons muito escuros ou muito claros
    brilho = r + g + b
    if brilho < 0.4 or brilho > 2.6:
        r = max(0.2, min(r * 1.2, 0.8))
        g = max(0.2, min(g * 1.2, 0.8))
        b = max(0.2, min(b * 1.2, 0.8))
    
    return r, g, b


# Função de redesenho da cena
def Desenha():
    global left, right, top, bottom, panX, panY 
    global DADOS, INDEX, nivel
    global xTriangulo, yTriangulo, tamanhoQuadrado, tamanhoTriangulo
    global maiorValorX, maiorValorY, menorValorX, menorValorY, margem
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(left, right, bottom, top)
    glMatrixMode(GL_MODELVIEW)

    # Liam a janela de visualização com a cor branca
    glClearColor(0, 0, 0, 1)
    glClear(GL_COLOR_BUFFER_BIT)

    glColor3f(1,0,0)

    #######################################
    # desenha os quadrados
    for item in DADOS:
        id_valor = item["id"]
        trios = item["trios"]

        if trios:
            x, y, z = trios[INDEX % len(trios)] #trios[0],trios[1],trios[2],trios[3],trios[4],..
            ponto = Ponto(x, y, z)
            r, g, b = gerarCorPorID()  
            cor = RGB(r, g, b) 
            quadrado = Quadrado(ponto, tamanhoQuadrado, tamanhoQuadrado, cor)
            
            desenhaQuadrilatero(quadrado)

    #######################################
    # desenha o triangulo controlavel
    ponto = Ponto(xTriangulo, yTriangulo, 0) # origem
    cor = RGB(1, 1, 1) # branco
    triangulo = Quadrado(ponto, tamanhoTriangulo, tamanhoTriangulo, cor)
    desenhaTriangulo(triangulo)
    
    #######################################
    glPushMatrix()
    glLoadIdentity()
    # TODO: PRECISA COMENTAR ? glTranslate()
    # TODO: desenhaEixos()
    glPopMatrix()
    
    # Executa os comandos OpenGl
    glFlush()

    return

####################################
# Função chamada constantemente no "modo ocioso" (idle) para animar a cena
def Animacao():
    global soma_dt, tempo_antes
    global INDEX, segundos, frames, nivel, inicializado
    global xTriangulo, yTriangulo
    global idle_ativo, SCORE, segundos_pontuacao
    
    if not idle_ativo: # interrompe 
        return
    
    tempo_agora = time.time()
    delta_time = tempo_agora - tempo_antes
    tempo_antes = tempo_agora
    soma_dt += delta_time
    segundos += delta_time
    segundos_pontuacao += delta_time
    
    if nivel == 0 and not inicializado:
        print("\n\n")
        print("##################################################")
        print("#                 Inicio do jogo                 #")
        print("##################################################")
        print("\n")
        print(f"################## Nivel: [ {nivel} ] ##################")
        print("#                                                #")
        print("#                    Boa Sorte!                  #")
        print("#                                                #")
        print("##################################################")
        inicializado = True
    
    tempo_pontuacao = 1
    if segundos_pontuacao >= tempo_pontuacao:
        segundos_pontuacao = 0
        SCORE += 1 # AUMENTA A PONTUACAO
    
    
    tempo_mudanca_nivel = 10
    if segundos >= tempo_mudanca_nivel:
        segundos = 0
        nivel += 1
        frames += 7
        pygame.mixer.init()
        pygame.mixer.music.load("sounds/level_up_pokemon.mp3")
        pygame.mixer.music.play()
        print("\n\n")
        print(f"################## Nivel: [ {nivel} ] ##################")
        print("#                                                #")
        print(f"#         Passaram-se +{tempo_mudanca_nivel} segundos!              #")
        print("#                                                #")
        print("##################################################")
        
    if soma_dt > 1.0 / frames: 
        soma_dt = 0
        INDEX += 1
        
        # Verifica colisões após atualizar posições
        colisoes = verificarColisoes()
        if colisoes:
            pausarJogo()
            print(f"\nColisao detectada com quadrados de IDs: {colisoes}")
            print("\n\n")
            print("################## GAME OVER ##################")
            print("#                                             #")
            print("#             Voce perdeu o jogo!             #")
            print("#              SUA PONTUACAO: ", SCORE)
            print("#                                             #")
            print("###############################################")
            pygame.mixer.init()
            pygame.mixer.music.load("sounds/roblox-death.mp3")
            pygame.mixer.music.play()
            return
        
        # Solicita redesenho
        glutPostRedisplay()
        
####################################
def pressionaTecla(key, x: int, y: int):  # Quando uma tecla for pressionada
    global xTriangulo, yTriangulo, teclas_pressionadas
    teclas_pressionadas.add(key)  # Adiciona tecla ao conjunto
    TeclasEspeciais(key, x, y)

def soltaTecla(key, x: int, y: int):  # Quando uma tecla for solta
    global teclas_pressionadas
    teclas_pressionadas.discard(key)  # Remove tecla do conjunto
    
# Função para teclado
def Teclado(key: chr, x: int, y: int):
    global INDEX, idle_ativo

    if key == b'\x1b':  # esc
        glutLeaveMainLoop() # solucao para sair da tela
    # if key == b' ': # barra de espaço
    if key == b'p':  # pausar/despausar
        idle_ativo = not idle_ativo
        
    glutPostRedisplay() # Redesenha

# Teclas especiais (setas) 
def TeclasEspeciais(key: int, x: int, y: int):
    global left, right, top, bottom, xTriangulo, yTriangulo
    global idle_ativo
    
    if not idle_ativo: # interrompe 
        return
    
    deslocamentoCamera:float = 0.1
    deslocamento:float = 10
    
    # para mover a câmera
    if glutGetModifiers() and GLUT_ACTIVE_CTRL:
        if key == GLUT_KEY_UP:              
            top += deslocamentoCamera
            bottom += deslocamentoCamera       
        if key == GLUT_KEY_DOWN: 
            top -= deslocamentoCamera
            bottom -= deslocamentoCamera
        if key == GLUT_KEY_LEFT:
            left -= deslocamentoCamera
            right -= deslocamentoCamera
        if key == GLUT_KEY_RIGHT:
            left += deslocamentoCamera
            right += deslocamentoCamera
            
    # para mover personagem
    # 2 direcoes (diagonais)
    if GLUT_KEY_UP in teclas_pressionadas and GLUT_KEY_RIGHT in teclas_pressionadas:
        xTriangulo += deslocamento
        yTriangulo += deslocamento
    elif GLUT_KEY_UP in teclas_pressionadas and GLUT_KEY_LEFT in teclas_pressionadas:
        xTriangulo -= deslocamento
        yTriangulo += deslocamento
    elif GLUT_KEY_DOWN in teclas_pressionadas and GLUT_KEY_RIGHT in teclas_pressionadas:
        xTriangulo += deslocamento
        yTriangulo -= deslocamento
    elif GLUT_KEY_DOWN in teclas_pressionadas and GLUT_KEY_LEFT in teclas_pressionadas:
        xTriangulo -= deslocamento
        yTriangulo -= deslocamento
    else:
        # 1 direcao
        if key == GLUT_KEY_UP:           
            yTriangulo += deslocamento       
        if key == GLUT_KEY_DOWN: 
            yTriangulo -= deslocamento
        if key == GLUT_KEY_LEFT:
            xTriangulo -= deslocamento
        if key == GLUT_KEY_RIGHT:
            xTriangulo += deslocamento
    
    # Redesenha
    glutPostRedisplay()
    return

####################################
def obtemArquivos():
    base_path = os.path.join(os.path.dirname(__file__), "Brazil - BR")
    candidates = []

    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)
        if os.path.isfile(item_path):
            candidates.append(item_path)
    if not candidates:
        return None  

    index = random.randint(0, len(candidates) - 1)
    selected_path = os.path.join(base_path, candidates[index])
    print(selected_path)
    return selected_path
    
# Inicializa a projeção ortográfica
def Inicializa():
    global left, right, top, bottom, panX, panY, xTriangulo, yTriangulo
    global DADOS, INDEX, TOTAL_FRAMES, REFERENCIA_SRU
    global segundos, frames, nivel    
    global maiorValorX, maiorValorY, menorValorX, menorValorY, margem
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    frames = 5
    
    # Obtem o valor de referencia para o SRU e as coordenadas de todas as entidades
    fullpath = obtemArquivos()
    TOTAL_FRAMES, DADOS, maiorValorX, maiorValorY, menorValorX, menorValorY = processarArquivo(fullpath)
    
    REFERENCIA_SRU = max(maiorValorX - menorValorX, maiorValorY - menorValorY, 1)

    margem = 20 

    left = menorValorX - margem + panX
    right = maiorValorX + margem + panX
    bottom = menorValorY - margem + panY
    top = maiorValorY + margem + panY
    
    xTriangulo += maiorValorX / 2
    yTriangulo += maiorValorY / 2
    
    gluOrtho2D(left, right, bottom, top)
    glMatrixMode(GL_MODELVIEW)

    return

# Função principal da aplicação
def main():
    glutInit(sys.argv)

    # Define do modo de operação da GLUT
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)

    # Especifica o tamanho inicial em pixels da janela GLUT
    glutInitWindowSize(800, 800)

    # Cria a janela passando como argumento o título da mesma
    glutCreateWindow(b"Trabalho 1 - Usando o OpenGL")

    # Registra a função callback de redesenho da janela de visualização
    glutDisplayFunc(Desenha)

    # Registra a função callback para executar ao longo do tempo
    glutIdleFunc(Animacao)
    
    # Registra a função callback para tratamento das teclas ASCII
    glutKeyboardFunc(Teclado)
    glutSpecialFunc(TeclasEspeciais)
    glutSpecialFunc(pressionaTecla)
    glutSpecialUpFunc(soltaTecla)
    
    # Chama a função responsável por fazer as inicializações
    Inicializa()

    try:
        # Inicia o processamento e aguarda interações do usuário
        glutMainLoop()
    except SystemExit:
        pass

if __name__ == '__main__':
    main()