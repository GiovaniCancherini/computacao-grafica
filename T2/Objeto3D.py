import time
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from ponto import *

import random

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

        self.gravidade = 0.01
        # Novas listas de apoio
        self.velocidadeY = []
        self.destinoS = []
        self.destinoCoracao = []

        # Controle de estados já inicializados
        self.inicializou_dissolucao = False
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

    def inicializaDestinoS(self):
        self.destinoS = []
        total = len(self.vertices)
        for i, v in enumerate(self.vertices):
            t = (i / total) * 2 * math.pi  # Parametrização no intervalo 0..2pi
            x = math.sin(t) * 2
            y = 1 + math.sin(t * 0.5 + math.pi / 2) * 2  # Combinação senoidal para fazer o "S"
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
                
    def ProximaPos(self, estado):
        for i in range(len(self.vertices)):
            match estado:
                case 'ESTADO_INICIAL':
                    self.vertices[i].x = self.verticesBckp[i].x
                    self.vertices[i].y = self.verticesBckp[i].y
                    self.vertices[i].z = self.verticesBckp[i].z

                case 'ESTADO_DISSOLUCAO':
                    if not self.inicializou_dissolucao:
                        self.inicializaDissolucao()

                    self.vertices[i].y += self.velocidadeY[i]
                    self.velocidadeY[i] -= self.gravidade

                    if self.vertices[i].y <= 0:
                        self.vertices[i].y = 0
                        self.vertices[i].x += random.uniform(-0.1, 0.1)
                        self.velocidadeY[i] *= -0.7

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
