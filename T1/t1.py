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
# Controle de tempo para animação
tempo_antes = time.time()
soma_dt = 0
segundos = 0
frames = 1
nivel:int = 0
inicializado = False

####################################
# Variáveis da câmera (viewport + pan)
left = 0
right = 0
top = 0
bottom = 0
panX = 0
panY = 0
DADOS = []
CONTADOR: int = 0
REFERENCIA_SRU: float = 0.0

####################################
# Variáveis do triagulo
xTriangulo: float = 1.0
yTriangulo: float = 1.0
teclas_pressionadas = set()  
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
    
def processar_arquivo(filename):
    with open(filename, 'r') as file:
        linhas = file.readlines()

    # Primeiro valor = referencia SRU (linha 1)
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
        trios = [tuple(map(int, trio)) for trio in trios]  # Converte para inteiros

        # Adiciona ao resultado
        dados.append({"id": id_linha, "trios": trios})

    return referencia_SRU, dados

def gerar_cor_a_partir_id(id_valor):
    # Gera componentes de cor RGB com base no id
    # Normaliza para o intervalo [0.0, 1.0]
    r = (id_valor * 3) % 256 / 255.0  
    g = (id_valor * 5) % 256 / 255.0
    b = (id_valor * 7) % 256 / 255.0
    return r, g, b

# Função de redesenho da cena
def Desenha():
    global translacaoX, translacaoY, left, right, top, bottom, panX, panY, DADOS, CONTADOR, xTriangulo, yTriangulo, REFERENCIA_SRU, nivel

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(left + panX, right + panX, bottom + panY, top + panY)
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
            x, y, z = trios[CONTADOR % len(trios)] #trios[0],trios[1],trios[2],trios[3],trios[4],..
            ponto = Ponto(x, y, z)
            r, g, b = gerar_cor_a_partir_id(id_valor)  
            cor = RGB(r, g, b) 
            tamLado = 45
            quadrado = Quadrado(ponto, tamLado, tamLado, cor)
            
            desenhaQuadrilatero(quadrado)

    #######################################
    # desenha o triangulo controlavel
    ponto = Ponto(xTriangulo, yTriangulo, 0) # origem
    cor = RGB(1, 1, 1) # branco
    tamLado = 50
    triangulo = Quadrado(ponto, tamLado, tamLado, cor)
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

# Função chamada constantemente no "modo ocioso" (idle) para animar a cena
def Animacao():
    global soma_dt, tempo_antes, CONTADOR, segundos, frames, nivel, inicializado

    tempo_agora = time.time()
    delta_time = tempo_agora - tempo_antes
    tempo_antes = tempo_agora
    soma_dt += delta_time
    segundos += delta_time

    if nivel == 0 and not inicializado:
        print("\n\n")
        print("########################")
        print("#### Inicio do jogo ####")
        print("########################")
        print("# Boa sorte!           #")
        print(f"# Nivel: [ {nivel} ]         #")
        print("########################")
        inicializado = True
    
    tempo_mudanca_nivel = 10
    if segundos >= tempo_mudanca_nivel:
        segundos = 0
        nivel += 1
        frames += 7
        pygame.mixer.init()
        pygame.mixer.music.load("level_up_pokemon.mp3")
        pygame.mixer.music.play()
        print("\n\n")
        print(f"################## Nivel: [ {nivel} ] ##################")
        print("#                                                #")
        print(f"#         Passaram-se +{tempo_mudanca_nivel} segundos!              #")
        print("#                                                #")
        print("##################################################")
        
    if soma_dt > 1.0 / frames: 
        soma_dt = 0
        CONTADOR += 1
        # Solicita redesenho
        glutPostRedisplay()

def pressionaTecla(key, x: int, y: int):  # Quando uma tecla for pressionada
    global xTriangulo, yTriangulo, teclas_pressionadas
    teclas_pressionadas.add(key)  # Adiciona tecla ao conjunto
    TeclasEspeciais(key, x, y)

def soltaTecla(key, x: int, y: int):  # Quando uma tecla for solta
    global teclas_pressionadas
    teclas_pressionadas.discard(key)  # Remove tecla do conjunto
    
# Função para teclado
def Teclado(key: chr, x: int, y: int):
    global CONTADOR

    if key == b'\x1b':  # esc
        glutLeaveMainLoop() # solucao para sair da tela
    # if key == b' ': # barra de espaço
        # 
        
    glutPostRedisplay() # Redesenha

# Teclas especiais (setas) 
def TeclasEspeciais(key: int, x: int, y: int):
    global left, right, top, bottom, xTriangulo, yTriangulo
    
    deslocamentoCamera:float = 0.1
    deslocamento:float = 7
    
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

# Inicializa a projeção ortográfica
def Inicializa():
    global left, right, top, bottom, panX, panY, xTriangulo, yTriangulo
    global DADOS, CONTADOR, REFERENCIA_SRU
    global segundos, frames, nivel    

    filename = os.path.join(os.path.dirname(__file__), "../T1/Paths_D.txt")

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    segundos = 0
    frames = 5
    nivel = 0
    # Obtem o valor de referencia para o SRU e as coordenadas de todas as entidades
    CONTADOR = 0
    REFERENCIA_SRU = 0.0
    
    REFERENCIA_SRU, DADOS = processar_arquivo(filename)
    print("Referencia SRU = ", REFERENCIA_SRU)

    # Ajusta SRU com base no valor
    half = REFERENCIA_SRU / 10
    
    left = 0
    right = half
    bottom = 0
    top = half
    
    xTriangulo += 3 * REFERENCIA_SRU
    yTriangulo += 3 * REFERENCIA_SRU
    
    gluOrtho2D(left + panX, right + panX, bottom + panY, top + panY)
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
    glutCreateWindow(b"Desenha OpenGL")

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