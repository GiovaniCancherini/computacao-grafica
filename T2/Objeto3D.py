import time, math, random

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from ponto import *

class objeto3D:
        
    def __init__(self):
        self.vertices = []
        self.verticesBckp = []
        self.faces = []
        self.speed = []
        self.angle = []
        self.radius = []
        self.position = ponto(0, 0, 0)
        self.rotation = (0, 0, 0, 0)

        # novas listas de apoio
        self.velocidadeY = []
        self.destinoS = []
        self.destinoCoracao = []

        # parametros dissolucao
        self.gravidade = 0.01
        
        # parametros redemoinho
        self.altura_centro_redemoinho = 0
        self.velocidade_subida = 0.02
        self.velocidade_rotacao = 0.1  # controla a velocidade de rotacao

        # Controle de estados ja inicializados
        self.inicializou_dissolucao = False
        self.inicializou_redemoinho = False
        self.inicializou_S = False
        self.inicializou_coracao = False

    def LoadFile(self, file: str):
        f = open(file, "r")
        for line in f:
            values = line.split(' ')
            if values[0] == 'v':
                self.vertices.append(ponto(float(values[1]), float(values[2]), float(values[3])))
                self.verticesBckp.append(ponto(float(values[1]), float(values[2]), float(values[3])))
                self.speed.append((random.random() + 0.1))
                self.angle.append(math.atan2(float(values[3]), float(values[1])))
                self.radius.append(math.hypot(float(values[1]), float(values[3])))

            if values[0] == 'f':
                self.faces.append([])
                for fVertex in values[1:]:
                    fInfo = fVertex.split('/')
                    self.faces[-1].append(int(fInfo[0]) - 1)
        f.close()

    def DesenhaVerticesEsfera(self):
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glRotatef(self.rotation[3], self.rotation[0], self.rotation[1], self.rotation[2])
        glColor3f(.0, .0, .0)
        glPointSize(8)

        # glBegin(GL_POINTS)
        for v in self.vertices:
            glPushMatrix()
            glTranslate(v.x, v.y, v.z)
            glutSolidSphere(.05, 20, 20)
            glPopMatrix()
            # glVertex(v.x, v.y, v.z)
        # glEnd()
        
        glPopMatrix()
        pass
    
    def DesenhaVerticesCubos(self):
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glRotatef(self.rotation[3], self.rotation[0], self.rotation[1], self.rotation[2])
        glColor3f(.0, .0, .0)
        glPointSize(8)

        # glBegin(GL_POINTS)
        for v in self.vertices:
            glPushMatrix()
            glTranslate(v.x, v.y, v.z)
            glutSolidCube(0.05) # glutSolidSphere(.05, 20, 20)
            glPopMatrix()
            # glVertex(v.x, v.y, v.z)
        # glEnd()
        
        glPopMatrix()
        pass

    def DesenhaWireframe(self):
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glRotatef(self.rotation[3], self.rotation[0], self.rotation[1], self.rotation[2])
        glColor3f(0, 0, 0)
        glLineWidth(2)        
        
        for f in self.faces:            
            glBegin(GL_LINE_LOOP)
            for iv in f:
                v = self.vertices[iv]
                glVertex(v.x, v.y, v.z)
            glEnd()
        
        glPopMatrix()
        pass

    def Desenha(self):
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glRotatef(self.rotation[3], self.rotation[0], self.rotation[1], self.rotation[2])
        glColor3f(0.34, .34, .34)
        glLineWidth(2)        
        
        for f in self.faces:            
            glBegin(GL_TRIANGLE_FAN)
            for iv in f:
                v = self.vertices[iv]
                glVertex(v.x, v.y, v.z)
            glEnd()
        
        glPopMatrix()
        pass

    def inicializaDissolucao(self):
        self.velocidadeY = [self.gravidade for _ in self.vertices]
        self.inicializou_dissolucao = True

    def inicializaRedemoinho(self):
        # Reinicia os angulos e raios para o estado de tornado
        self.initAngles = [math.atan2(v.z, v.x) for v in self.vertices]
        self.radii = [math.hypot(v.x, v.z) for v in self.vertices]
        self.initial_ys = [v.y for v in self.vertices] # Guardar a posicao Y inicial para a subida gradual
        self.inicializou_redemoinho = True
        self.altura_centro_redemoinho = 0
        self.inicializou_redemoinho = True
    
    def inicializaDestinoS(self):
        self.destinoS = []
        total = len(self.vertices)
        for i, v in enumerate(self.vertices):
            t = (i / total) * 2 * math.pi  # Parametrizacao no intervalo 0..2pi
            x = math.sin(t) * 2
            y = 1 + math.sin(t * 0.5 + math.pi / 2) * 2  # Combinacao senoidal para fazer o "S"
            # 1++ para elevar o "S" acima do plano
            z = 0
            self.destinoS.append(ponto(x, y, z))
        self.inicializou_S = True

    def inicializaDestinoCoracao(self):
        self.destinoCoracao = []
        for i, v in enumerate(self.vertices):
            t = (i / len(self.vertices)) * 2 * math.pi
            x = 16 * math.sin(t) ** 3 / 16
            y = (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) / 16
            z = 0
            self.destinoCoracao.append(ponto(x, y, z))
        self.inicializou_coracao = True
                
    def ProximaPos(self, estado, frame_index):
        rot_speed_factor = 2.5 # Fator para a velocidade de rotacao
        vertical_speed_factor = 0.05 # Fator para a velocidade de subida
        max_tornado_height = 5.0 # Altura máxima do tornado
        tornado_duration_frames = 180 # Duracao do tornado em frames (6 segundos a 30 FPS)
        restore_duration_frames = 180 # Duracao da restauracao em frames (6 segundos a 30 FPS)
        
        tempoAtual = frame_index / 30.0 # tempo em segundos
        
        for i in range(len(self.vertices)):
            match estado:
                case 'ESTADO_INICIAL':
                    self.vertices[i].x = self.verticesBckp[i].x
                    self.vertices[i].y = self.verticesBckp[i].y
                    self.vertices[i].z = self.verticesBckp[i].z
                    # Resetar flags
                    self.inicializou_dissolucao = False
                    self.inicializou_redemoinho = False
                    self.inicializou_S = False
                    self.inicializou_coracao = False
                    
                case 'ESTADO_DISSOLUCAO':
                    if not self.inicializou_dissolucao:
                        self.inicializaDissolucao()

                    self.vertices[i].y += self.velocidadeY[i]
                    self.velocidadeY[i] -= self.gravidade

                    if self.vertices[i].y <= 0:
                        self.vertices[i].y = 0
                        self.vertices[i].x += random.uniform(-0.1, 0.1)
                        self.velocidadeY[i] *= -0.7

                case 'ESTADO_TORNADO':
                    if not self.inicializou_redemoinho:
                        self.inicializaRedemoinho()
                    
                    # Normaliza o tempo para o período do tornado (0 a 1)
                    # O tempo total do estado 'ESTADO_TORNADO' e 18 - 12 = 6 segundos, ou 180 frames.
                    # 'segundos' em main.py e o tempo total da simulacao.
                    # Para isolar o tempo do tornado, subtraímos o tempo de início do tornado (12 segundos = 360 frames).
                    relative_frame = frame_index - (12 * 30) 
                    t = min(relative_frame / tornado_duration_frames, 1.0) # t vai de 0 a 1 durante o tornado

                    # Aumenta a velocidade de rotacao e subida gradualmente
                    # A rotacao e mais rápida no centro e mais lenta nas bordas
                    # A velocidade angular (angle_speed) e maior para raios menores
                    angle_speed = rot_speed_factor / (self.radii[i] + 0.1) # Adiciona 0.1 para evitar divisao por zero e suavizar
                    
                    # Atualiza o angulo com base na velocidade angular e tempo
                    self.initAngles[i] += angle_speed * t * 0.1 # Multiplicador para controle fino

                    # Calcula as novas posicões X e Z
                    self.vertices[i].x = self.radii[i] * math.cos(self.initAngles[i])
                    self.vertices[i].z = self.radii[i] * math.sin(self.initAngles[i])

                    # Aumenta a altura gradualmente, comecando da posicao Y inicial da partícula
                    self.vertices[i].y = self.initial_ys[i] + (max_tornado_height * t)
                    
                case 'ESTADO_RESTAURACAO':
                    # Para a restauracao, queremos que as partículas voltem para verticesBckp
                    # O tempo total do estado 'ESTADO_RESTAURACAO' e 24 - 18 = 6 segundos, ou 180 frames.
                    relative_frame = frame_index - (18 * 30) 
                    t = min(relative_frame / restore_duration_frames, 1.0) # t vai de 0 a 1 durante a restauracao

                    orig = self.verticesBckp[i]
                    current = self.vertices[i]

                    # Interpolacao linear da posicao atual para a posicao original
                    self.vertices[i].x = current.x * (1 - t) + orig.x * t
                    self.vertices[i].y = current.y * (1 - t) + orig.y * t
                    self.vertices[i].z = current.z * (1 - t) + orig.z * t
                    
                    # Ao final da restauracao, resetar a inicializacao do redemoinho
                    # para que o próximo ciclo comece corretamente.
                    if t >= 1.0:
                        self.inicializou_redemoinho = False
                        self.inicializou_dissolucao = False # para caso o ciclo se repita
                        self.altura_centro_redemoinho = 0

                case 'ESTADO_S':
                    if not self.inicializou_S:
                        self.inicializaDestinoS()

                    destino = self.destinoS[i]
                    self.vertices[i].x += (destino.x - self.vertices[i].x) * 0.05
                    self.vertices[i].y += (destino.y - self.vertices[i].y) * 0.05
                    self.vertices[i].z += (destino.z - self.vertices[i].z) * 0.05

                case 'ESTADO_CORACAO':
                    if not self.inicializou_coracao:
                        self.inicializaDestinoCoracao()

                    destino = self.destinoCoracao[i]
                    self.vertices[i].x += (destino.x - self.vertices[i].x) * 0.05
                    self.vertices[i].y += (destino.y - self.vertices[i].y) * 0.05
                    self.vertices[i].z += (destino.z - self.vertices[i].z) * 0.05
