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

####################################

left = 0
right = 0
top = 0
bottom = 0
panX = 0
panY = 0
DADOS = []
CONTADOR = 0

####################################

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

def processar_arquivo(filename):
    with open(filename, 'r') as file:
        linhas = file.readlines()

    # Primeiro valor importante (linha 1)
    numero_importante = int(linhas[0].replace('[', '').replace(']', '').strip())

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

    return numero_importante, dados

def gerar_cor_a_partir_id(id_valor):
    # Gera componentes de cor RGB com base no id
    # Normaliza para o intervalo [0.0, 1.0]
    r = (id_valor * 3) % 256 / 255.0  
    g = (id_valor * 5) % 256 / 255.0
    b = (id_valor * 7) % 256 / 255.0
    return r, g, b

def Desenha():
    global translacaoX, translacaoY, left, right, top, bottom, panX, panY, DADOS, CONTADOR

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(left + panX, right + panX, bottom + panY, top + panY)
    glMatrixMode(GL_MODELVIEW)

    # Liam a janela de visualização com a cor branca
    glClearColor(0, 0, 0, 1)
    glClear(GL_COLOR_BUFFER_BIT)

    glColor3f(1,0,0)

    #######################################
    
    for item in DADOS:
        id_valor = item["id"]
        trios = item["trios"]

        if trios:
            x, y, z = trios[CONTADOR % len(trios)] #trios[0],trios[1],trios[2],trios[3],trios[4],..

            r, g, b = gerar_cor_a_partir_id(id_valor)
            
            glColor3f(r, g, b)  # Define a cor com base no trio
            desenhaQuadrado(x, y, 50, 50)  # Exemplo de desenho, ajuste conforme necessário
            
    #######################################
    
    glPushMatrix()
    glLoadIdentity()
    # TODO: PRECISA COMENTAR ? glTranslate()
    # TODO: desenhaEixos()
    glPopMatrix()
    
    # Executa os comandos OpenGl
    glFlush()

    return

def Teclado(key: chr, x: int, y: int):
    global CONTADOR

    if key == 27: # esc
        exit(0)

    if key == b' ': # barra de espaço
        CONTADOR += 1                   # INCREMENTA POSICAO EM FUNCAO DO TEMPO [PRESSIONANDO ESPACO]

    glutPostRedisplay() # Redesenha
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
    global left, right, top, bottom, panX, panY, DADOS, CONTADOR

    glMatrixMode(GL_PROJECTION)
    left = 0
    right = 1
    top = 1
    bottom = 0
    gluOrtho2D(left + panX, right + panX, bottom + panY, top + panY)
    glMatrixMode(GL_MODELVIEW)

    # processa todo o arquivo e armazena as informacoes
    CONTADOR = 0
    filename = 'C:/Users/Giovani.Silva/Desktop/computacao-grafica/Brazil - BR/BR-01/Paths_D.txt'
    numero_importante, dados = processar_arquivo(filename)
    DADOS = dados
    print("Número importante:", numero_importante)
    # print("Dados extraídos:", dados)
    
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