import math

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

# Classe que representa um ponto 2D com operações básicas
class Ponto:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def print(self) -> None:
        print("Ponto (", self.x, ",", self.y, ")")

    def set(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    # Soma de dois pontos
    def __add__(self, other):
        return Ponto(self.x + other.x, self.y + other.y)

    # Subtração entre pontos
    def __sub__(self, other):
        return Ponto(self.x - other.x, self.y - other.y)

    # Multiplicação por escalar
    def __mul__(self, escalar: float):
        return Ponto(self.x * escalar, self.y * escalar)

# Classe que representa um quadrado desenhável
class Quadrado():
    def __init__(self, w, h):
        self.pos = Ponto(0, 0)     # Posição do canto inferior esquerdo
        self.w = w                 # Largura
        self.h = h                 # Altura
        self.c = (1, 0, 0)         # Cor inicial (vermelho)

# Lista de quadrados (inicia com um)
quadrados = [Quadrado(0.25, 0.25)]
num_quadrado = 0  # Índice do quadrado atual

# Variáveis de controle da câmera
left = 0
right = 0
top = 0
bottom = 0
panX = 0
panY = 0

# Desenha os eixos X e Y no mundo (visuais)
def desenhaEixos():
    glPushMatrix()
    glLoadIdentity()

    glColor3f(1, 1, 1)
    glLineWidth(1)

    glBegin(GL_LINES)
    glVertex2f(left, 0)
    glVertex2f(right, 0)
    glVertex2f(0, bottom)
    glVertex2f(0, top)
    glEnd()

    glPopMatrix()

# Desenha um quadrado na posição (x, y), com tamanho (w, h)
def desenhaQuadrado(x, y, w, h):
    glPushMatrix()
    glLoadIdentity()  # <- Faltavam os parênteses aqui!

    glTranslatef(x, y, 0)

    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(w, 0)
    glVertex2f(w, h)
    glVertex2f(0, h)
    glEnd()

    glPopMatrix()

# Função principal de desenho da cena
def Desenha():
    global left, right, top, bottom, panX, panY

    # Define a área visível (viewport) com deslocamento (pan)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(left + panX, right + panX, bottom + panY, top + panY)
    glMatrixMode(GL_MODELVIEW)

    # Limpa a tela com preto
    glClearColor(0, 0, 0, 1)
    glClear(GL_COLOR_BUFFER_BIT)

    # Desenha todos os quadrados
    for quadrado in quadrados:
        glColor3f(*quadrado.c)
        desenhaQuadrado(quadrado.pos.x, quadrado.pos.y, quadrado.h, quadrado.w)

    # Desenha os eixos
    desenhaEixos()

    # Finaliza os comandos de desenho
    glFlush()

# Função para teclas do teclado comum (ASCII)
def Teclado(key: chr, x: int, y: int):
    global num_quadrado, panX, panY

    if key == 27:  # Tecla ESC
        exit(0)

    if key == b' ':  # Espaço cria um novo quadrado
        quadrados.append(Quadrado(0.25, 0.25))
        num_quadrado += 1
        # Define cor com base em número do quadrado
        quadrados[num_quadrado].c = (
            num_quadrado / 9 % 3 / 2.0,
            num_quadrado / 3 % 3 / 2.0,
            num_quadrado % 3 / 2.0
        )

    # Teclas WASZ para mover a câmera (pan)
    if key == b'a':
        panX -= 0.01
    if key == b's':
        panX += 0.01
    if key == b'w':
        panY += 0.01
    if key == b'z':
        panY -= 0.01

    # Solicita redesenho
    glutPostRedisplay()

# Função para teclas especiais (setas) — move o quadrado atual
def TeclasEspeciais(key: int, x: int, y: int):
    if key == GLUT_KEY_LEFT:
        quadrados[num_quadrado].pos -= Ponto(0.02, 0)
    if key == GLUT_KEY_RIGHT:
        quadrados[num_quadrado].pos += Ponto(0.02, 0)
    if key == GLUT_KEY_UP:
        quadrados[num_quadrado].pos += Ponto(0, 0.02)
    if key == GLUT_KEY_DOWN:
        quadrados[num_quadrado].pos -= Ponto(0, 0.02)

    glutPostRedisplay()

# Inicializa as configurações do sistema de coordenadas
def Inicializa():
    global left, right, top, bottom

    glMatrixMode(GL_PROJECTION)
    left = -1
    right = 1
    top = 1
    bottom = -1
    gluOrtho2D(left + panX, right + panX, bottom + panY, top + panY)
    glMatrixMode(GL_MODELVIEW)

# Função principal
def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    glutInitWindowSize(800, 800)
    glutCreateWindow(b"Desenha OpenGL")

    glutDisplayFunc(Desenha)
    glutKeyboardFunc(Teclado)
    glutSpecialFunc(TeclasEspeciais)

    Inicializa()

    try:
        glutMainLoop()
    except SystemExit:
        pass

if __name__ == '__main__':
    main()
