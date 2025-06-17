from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

import time
import copy

from objeto3D import *

# globais
o:objeto3D
tempo_antes = time.time()
soma_dt, soma_dt2 = 0, 0
segundos = 0
# globais - tempo
idle_ativo = True
estado = ''
# globais - camera
cameraX = -1.0
cameraY = 5.0
cameraZ = -12.0
cameraAngleX = 0.0
cameraAngleY = 0.0
# hashmap
historico = dict()
frame_index = 0
frame_visualizado = 0

def determina_estado_por_frame(f: int):
    tempo = f / 30.0  # 30 FPS
    if tempo < 2:
        return 'ESTADO_INICIAL'
    elif tempo < 12:
        return 'ESTADO_DISSOLUCAO'
    elif tempo < 18:
        return 'ESTADO_TORNADO'
    elif tempo < 24:
        return 'ESTADO_RESTAURACAO'
    elif tempo < 30:
        return 'ESTADO_S'
    else:
        return 'ESTADO_CORACAO'


def init():
    global o
    glClearColor(0.5, 0.5, 0.9, 1.0)
    glClearDepth(1.0)

    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    o = objeto3D()
    o.LoadFile('Human_Head.obj')

    defineLuz()
    posicUser()
    glutReshapeFunc(reshape)

def defineLuz():
    # Define cores para um objeto dourado
    luz_ambiente = [0.4, 0.4, 0.4]
    luz_difusa = [0.7, 0.7, 0.7]
    luz_especular = [0.9, 0.9, 0.9]
    posicao_luz = [2.0, 3.0, 0.0]  # PosiÃ§Ã£o da Luz
    especularidade = [1.0, 1.0, 1.0]

    # ****************  Fonte de Luz 0

    glEnable(GL_COLOR_MATERIAL)

    #Habilita o uso de iluminaÃ§Ã£o
    glEnable(GL_LIGHTING)

    #Ativa o uso da luz ambiente
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, luz_ambiente)
    # Define os parametros da luz nÃºmero Zero
    glLightfv(GL_LIGHT0, GL_AMBIENT, luz_ambiente)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, luz_difusa)
    glLightfv(GL_LIGHT0, GL_SPECULAR, luz_especular)
    glLightfv(GL_LIGHT0, GL_POSITION, posicao_luz)
    glEnable(GL_LIGHT0)

    # Ativa o "Color Tracking"
    glEnable(GL_COLOR_MATERIAL)

    # Define a reflectancia do material
    glMaterialfv(GL_FRONT, GL_SPECULAR, especularidade)

    # Define a concentraÃ§Ã£oo do brilho.
    # Quanto maior o valor do Segundo parametro, mais
    # concentrado serÃ¡ o brilho. (Valores vÃ¡lidos: de 0 a 128)
    glMateriali(GL_FRONT, GL_SHININESS, 51)

def posicUser():
    glLoadIdentity()
    gluLookAt(cameraX, cameraY, cameraZ, 0, 0, 0, 0, 1.0, 0)
    glRotatef(cameraAngleY, 1.0, 0.0, 0.0)
    glRotatef(cameraAngleX, 0.0, 1.0, 0.0)

def definePerspectiva(w, h):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, w/h, 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)
    
def desenhaLadrilho():
    glColor3f(0.5, 0.5, 0.5)  # desenha QUAD preenchido
    glBegin(GL_QUADS)
    glNormal3f(0, 1, 0)
    glVertex3f(-0.5, 0.0, -0.5)
    glVertex3f(-0.5, 0.0, 0.5)
    glVertex3f(0.5, 0.0, 0.5)
    glVertex3f(0.5, 0.0, -0.5)
    glEnd()

    glColor3f(1, 1, 1)  # desenha a borda da QUAD
    glBegin(GL_LINE_STRIP)
    glNormal3f(0, 1, 0)
    glVertex3f(-0.5, 0.0, -0.5)
    glVertex3f(-0.5, 0.0, 0.5)
    glVertex3f(0.5, 0.0, 0.5)
    glVertex3f(0.5, 0.0, -0.5)
    glEnd()

def desenhaPiso():
    glPushMatrix()
    glTranslated(-20, -1, -10)
    for x in range(-20, 20):
        glPushMatrix()
        for z in range(-20, 20):
            desenhaLadrilho()
            glTranslated(0, 0, 1)
        glPopMatrix()
        glTranslated(1, 0, 0)
    glPopMatrix()

def desenhaCubo():
    glPushMatrix()
    glColor3f(1, 0, 0)
    glTranslated(0, 0.5, 0)
    glutSolidCube(1)

    glColor3f(0.5, 0.5, 0)
    glTranslated(0, 0.5, 0)
    glRotatef(90, -1, 0, 0)
    glRotatef(45, 0, 0, 1)
    glutSolidCone(1, 1, 4, 4)
    glPopMatrix()

# Função chamada constantemente (idle) para atualizar a animação
def animacao():
    global soma_dt, tempo_antes, estado
    global frame_index, historico, frame_visualizado, idle_ativo

    tempo_agora = time.time()
    delta_time = tempo_agora - tempo_antes
    tempo_antes = tempo_agora

    soma_dt += delta_time

    if not idle_ativo:
        return

    if soma_dt > 1.0 / 120:
        soma_dt = 0

        estado = determina_estado_por_frame(frame_index)
        o.ProximaPos(estado, frame_index)
        historico[frame_index] = copy.deepcopy(o)

        frame_visualizado = frame_index
        frame_index += 1

        glutPostRedisplay()
 

def desenha():
    global o, historico, frame_visualizado, frame_index, segundos
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    posicUser()

    # desenhaPiso()
    
    if frame_visualizado in historico:
        print(f'Frame EXIBIDO: {frame_visualizado}, Frame Renderizado: {frame_index}, Tempo: {segundos} segundos')
        historico[frame_visualizado].DesenhaVerticesEsfera()
    else:
        print('[ ERRO ] frame_visualizado não encontrado no histórico:', frame_visualizado)
        # o.DesenhaVerticesEsfera()
        
    glutSwapBuffers()
    pass

# Função para teclado
def teclado(key: chr, x: int, y: int):
    global idle_ativo, frame_visualizado, frame_index, estado
    global cameraX, cameraY, cameraZ, o, historico

    if key == b'\x1b':
        glutLeaveMainLoop()

    elif key == b'p':  # play/pause toggle
        idle_ativo = not idle_ativo
        if idle_ativo:
            estado = determina_estado_por_frame(frame_visualizado)
            frame_index = frame_visualizado + 1

    elif key == b'[':
        idle_ativo = False
        frame_visualizado = max(0, frame_visualizado - 1)

    elif key == b',':
        idle_ativo = False
        frame_visualizado = max(0, frame_visualizado - 10)

    elif key == b']':
        idle_ativo = False
        frame_visualizado = min(frame_visualizado + 1, frame_index + 1)
        if frame_visualizado not in historico:
            estado = determina_estado_por_frame(frame_visualizado)
            o.ProximaPos(estado, frame_visualizado)
            historico[frame_visualizado] = copy.deepcopy(o)
        frame_index = max(frame_index, frame_visualizado + 1)

    elif key == b'.':
        idle_ativo = False
        to_frame = min(frame_visualizado + 10, frame_index + 10)
        for f in range(frame_visualizado + 1, to_frame + 1):
            if f not in historico:
                estado = determina_estado_por_frame(f)
                o.ProximaPos(estado, f)
                historico[f] = copy.deepcopy(o)
        frame_visualizado = to_frame
        frame_index = max(frame_index, frame_visualizado + 1)

    elif key == b'w':
        o.position.y += 0.1
    elif key == b's':
        o.position.y -= 0.1
    elif key == b'a':
        o.position.x -= 0.1
    elif key == b'd':
        o.position.x += 0.1

    elif key == b'q':
        cameraZ += 0.2
    elif key == b'e':
        cameraZ -= 0.2
    elif key == b'r':
        cameraX = -2.0
        cameraY = 6.0
        cameraZ = -8.0

    glutPostRedisplay()



# Função para teclado
def teclasEspeciais(key: chr, x: int, y: int):
    global segundos, idle_ativo, o, cameraX, cameraY, cameraZ, cameraAngleX, cameraAngleY
    cameraSpeed = 5
    # movimento camera
    if key == GLUT_KEY_LEFT:
        cameraAngleX -= cameraSpeed
    elif key == GLUT_KEY_RIGHT:
        cameraAngleX += cameraSpeed
    elif key == GLUT_KEY_UP:
        cameraAngleY -= cameraSpeed
    elif key == GLUT_KEY_DOWN:
        cameraAngleY += cameraSpeed
        
    glutPostRedisplay() # Redesenha
    pass

def reshape(w, h):
    if h == 0:
        h = 1  # evitar divisão por zero

    glViewport(0, 0, w, h)
    definePerspectiva(w, h)
    pass

def main():

    glutInit(sys.argv)

    # Define o modelo de operacao da GLUT
    glutInitDisplayMode(GLUT_RGBA | GLUT_DEPTH)

    # Especifica o tamnho inicial em pixels da janela GLUT
    glutInitWindowSize(640, 480)

    # Especifica a posição de início da janela
    glutInitWindowPosition(100, 100)

    # Cria a janela passando o título da mesma como argumento
    glutCreateWindow(b'Computacao Grafica - 3D')

    # Função responsável por fazer as inicializações
    init()

    # Registra a funcao callback de redesenho da janela de visualizacao
    glutDisplayFunc(desenha)

    # Registra a funcao callback para tratamento das teclas ASCII
    glutKeyboardFunc(teclado)
    glutSpecialFunc(teclasEspeciais)
    
    glutIdleFunc(animacao)

    try:
        # Inicia o processamento e aguarda interacoes do usuario
        glutMainLoop()
    except SystemExit:
        pass

if __name__ == '__main__':
    main()
