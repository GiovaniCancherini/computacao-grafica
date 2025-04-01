import math
import re

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

class Ponto:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def print(self) -> None:
        print("Ponto (", self.x, ",", self.y, ")")

    def set(self, x: float, y: float) -> None:
        
        self.x = x
        self.y = y

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return Ponto(x, y)

    def __sub__(self, other):
        x = self.x - other.x
        y = self.y - other.y
        return Ponto(x, y)

    def __mul__(self, escalar: float):
        x = self.x * escalar
        y = self.y * escalar
        return Ponto(x, y)
    
class Quadrado():
    
    def __init__(self,x, y,  w, h,  c = (1,0,0)):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.c = c

quadrados = [Quadrado(  0,  0, 30,30, (1,0,0)), Quadrado(60 , 30 , 30,30, (1,0,1)),
           Quadrado( 40, 80, 30,30, (0,1,0)), Quadrado(90 , 70 , 30,30, (0,1,1)),
           Quadrado( 20,120, 30,30, (0,0,1)), Quadrado(225, 30 , 30,30, (1,0,1)),
           Quadrado(115,210, 30,30, (1,0,0)), Quadrado(312, 112, 30,30, (1,0,1)),
           Quadrado( 50,260, 30,30, (0,1,0)), Quadrado(444, 444, 30,30, (0,1,1)),
           Quadrado( 30,330, 30,30, (0,0,1)), Quadrado(447, 301, 30,30, (1,0,1))]
num_quadrado = 0

left = 0
right = 0
top = 0
bottom = 0
panX = 0
panY = 0



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

def desenhaQuadrado(x, y, w, h):
    glPushMatrix()

    glTranslate(x/1000, y/1000, 0)

    glBegin(GL_QUADS)    
    glVertex2f(0, 0)
    glVertex2f(w/1000, 0)
    glVertex2f(w/1000, h/1000)
    glVertex2f(0, h/1000)
    glEnd()

    glPopMatrix()

def teste(linha):
    # Capturar os primeiros 4 caracteres e extrair um número, se houver
    match_inicio = re.match(r"(\d{1,4})", linha.strip())
    primeiro_numero = int(match_inicio.group(1)) if match_inicio else None
    print("Número inicial:", primeiro_numero)

    # Capturar todos os trios de números entre parênteses
    trios = re.findall(r"\((\d+),(\d+),(\d+)\)", linha)
    trios_formatados = [tuple(map(int, trio)) for trio in trios]
    print("Trios capturados:", trios_formatados)


def Desenha():
    global translacaoX, translacaoY, left, right, top, bottom, panX, panY

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(left + panX, right + panX, bottom + panY, top + panY)
    glMatrixMode(GL_MODELVIEW)

    # Liam a janela de visualização com a cor branca
    glClearColor(0, 0, 0, 1)
    glClear(GL_COLOR_BUFFER_BIT)

    glColor3f(1,0,0)

    # for quadrado in quadrados:
        # glColor3f(quadrado.c[0], quadrado.c[1], quadrado.c[2])
        # desenhaQuadrado(quadrado.x, quadrado.y, quadrado.h, quadrado.w)


    filename_input = 'Brazil - BR/BR-01/Paths_D.txt'
    with open(filename_input, 'r') as file:
        linhas = file.readlines()[:3]  # Le as n primeiras linhas de todo o arquivo
        
        # Salvar o primeiro inteiro da entrada
        primeiro_valor = linhas[0]
        print("Primeiro inteiro salvo:", primeiro_valor)
        
        # next(linhas) # ignora a primeira
        for linha in linhas[1:]: 
            teste(linha.strip())  # Chama a def teste() para cada linha



    glPushMatrix()
    glLoadIdentity()
    # TODO: glTranslate()
    desenhaEixos()
    glPopMatrix()
    
    # Executa os comandos OpenGl
    glFlush()

    return


# Função callback chamada para gerenciar eventos de teclas
def Teclado(key: chr, x: int, y: int):
    global num_quadrado

    if key == 27:
        exit(0)

    if key == b' ':
        quadrados.append(Quadrado(0.25,0.25))
        num_quadrado += 1
        quadrados[num_quadrado].c = (num_quadrado / 9 % 3 / 2.0, 
                                    num_quadrado / 3 % 3 / 2.0,
                                    num_quadrado % 3 / 2.0)

    # Redesenha
    glutPostRedisplay()

    return


def TeclasEspeciais(key: int, x: int, y: int):
    global left, right, top, bottom

    if key == GLUT_KEY_UP:              
        top += 0.01
        bottom += 0.01        
    if key == GLUT_KEY_DOWN: 
        top -= 0.01
        bottom -= 0.01  
    if key == GLUT_KEY_LEFT:
        left -= 0.01
        right -= 0.01  
    if key == GLUT_KEY_RIGHT:
        left += 0.01
        right += 0.01   

    # Redesenha
    glutPostRedisplay()
    return


def Inicializa():
    global left, right, top, bottom, panX, panY

    glMatrixMode(GL_PROJECTION)
    left = -1
    right = 1
    top = 1
    bottom = -1
    gluOrtho2D(left + panX, right + panX, bottom + panY, top + panY)
    glMatrixMode(GL_MODELVIEW)

    return


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

    # Registra a função callback para tratamento das teclas ASCII
    glutKeyboardFunc(Teclado)
    glutSpecialFunc(TeclasEspeciais)

    # Chama a função responsável por fazer as inicializações
    Inicializa()

    try:
        # Inicia o processamento e aguarda interações do usuário
        glutMainLoop()
    except SystemExit:
        pass


if __name__ == '__main__':
    main()