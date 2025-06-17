import math, random

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from ponto import *

class objeto3D:
        
    # inicializa todas as listas de vertices, faces, velocidades e parametros de estado. 
    # tambem define parametros para os efeitos como dissolucao, tornado, formato de "s" e coracao.
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
        self.restoreStart = []

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

    # carrega um arquivo .obj contendo os vertices e faces. seleciona uma porcentagem dos vertices para desenhar. 
    # calcula o angulo e raio de cada vertice em relacao ao eixo z para animacoes futuras.
    def LoadFile(self, file: str, porcentagem_vertices: float = 1.0):
        self.vertices = []
        self.verticesBckp = []
        self.faces = []
        self.speed = []
        self.angle = []
        self.radius = []

        with open(file, "r") as f:
            all_vertices = []
            for line in f:
                values = line.strip().split()
                if not values:
                    continue
                if values[0] == 'v':
                    x, y, z = float(values[1]), float(values[2]), float(values[3])
                    all_vertices.append((x, y, z))
                elif values[0] == 'f':
                    self.faces.append([])
                    for fVertex in values[1:]:
                        fInfo = fVertex.split('/')
                        self.faces[-1].append(int(fInfo[0]) - 1)

        f.close()
        
        total = len(all_vertices)
        
        if porcentagem_vertices >= 1.0:
            selected_indices = range(total)
        else:
            passo = int(1.0 / porcentagem_vertices)
            # garante distribuição uniforme, mesmo para baixos valores
            selected_indices = range(0, total, passo)

        for i in selected_indices:
            x, y, z = all_vertices[i]
            self.vertices.append(ponto(x, y, z))
            self.verticesBckp.append(ponto(x, y, z))
            self.speed.append(random.random() + 0.1)
            self.angle.append(math.atan2(z, x))
            self.radius.append(math.hypot(x, z))

    # desenha cada vertice como uma pequena esfera preta no espaco 3d, aplicando rotacao e translacao
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
    
    # desenha cada vertice como um pequeno cubo preto no espaco 3d, aplicando rotacao e translacao
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

    # desenha as arestas (linhas) das faces do objeto em formato wireframe (grade), usando os vertices atuais
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

    # desenha as faces do objeto preenchidas com triangulos (modo solido), com cor cinza escuro
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

    # prepara os vertices para o efeito de dissolucao, atribuindo gravidade inicial a cada um
    def inicializaDissolucao(self):
        self.velocidadeY = [self.gravidade for _ in self.vertices]
        self.inicializou_dissolucao = True

    # prepara os vertices para o efeito de tornado/redemoinho, salvando angulo, raio e altura inicial de cada vertice
    def inicializaRedemoinho(self):
        # Reinicia os angulos e raios para o estado de tornado
        self.initAngles = [math.atan2(v.z, v.x) for v in self.vertices]
        self.radii = [math.hypot(v.x, v.z) for v in self.vertices]
        self.initial_ys = [v.y for v in self.vertices] # Guardar a posicao Y inicial para a subida gradual
        self.inicializou_redemoinho = True
        self.altura_centro_redemoinho = 0
        self.inicializou_redemoinho = True
    
    # calcula as posicoes de destino dos vertices para formar uma letra "s" no espaco
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

    # calcula as posicoes de destino dos vertices para formar um coracao 2d no plano x-y 
    def inicializaDestinoCoracao(self):
        self.destinoCoracao = []
        for i, v in enumerate(self.vertices):
            t = (i / len(self.vertices)) * 2 * math.pi
            x = 16 * math.sin(t) ** 3 / 16
            y = (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) / 16
            z = 0
            self.destinoCoracao.append(ponto(x, y, z))
        self.inicializou_coracao = True
         
    # controla qual efeito animado aplicar no objeto com base no estado atual e frame da animacao
    def ProximaPos(self, estado, frame_index):
        match estado:
            case 'ESTADO_INICIAL':
                self._estado_inicial()
            case 'ESTADO_DISSOLUCAO':
                self._estado_dissolucao()
            case 'ESTADO_TORNADO':
                self._estado_tornado(frame_index)
            case 'ESTADO_RESTAURACAO':
                self._estado_restauracao(frame_index)
            case 'ESTADO_S':
                self._estado_S()
            case 'ESTADO_CORACAO':
                self._estado_coracao()

    # restaura os vertices para sua posicao original e reinicia os estados de animacoes
    def _estado_inicial(self):
        for i in range(len(self.vertices)):
            self.vertices[i] = ponto(
                self.verticesBckp[i].x,
                self.verticesBckp[i].y,
                self.verticesBckp[i].z
            )
        self.inicializou_dissolucao = False
        self.inicializou_redemoinho = False
        self.inicializou_S = False
        self.inicializou_coracao = False

    # restaura os vertices para sua posicao original e reinicia os estados de animacoes
    def _estado_dissolucao(self):
        if not self.inicializou_dissolucao:
            self.inicializaDissolucao()

        for i in range(len(self.vertices)):
            self.vertices[i].y += self.velocidadeY[i]
            self.velocidadeY[i] -= self.gravidade

            if self.vertices[i].y <= 0:
                self.vertices[i].y = 0
                self.vertices[i].x += random.uniform(-0.1, 0.1)
                self.velocidadeY[i] *= -0.7

    # faz os vertices girarem em espiral e subirem, simulando um tornado. salva a ultima posicao para restaurar depois
    def _estado_tornado(self, frame_index):
        if not self.inicializou_redemoinho:
            self.inicializaRedemoinho()

        relative_frame = frame_index - (12 * 30)
        t = min(relative_frame / 180, 1.0)  # 6s * 30fps

        max_raio = max(self.radii)

        for i in range(len(self.vertices)):
            raio = self.radii[i]
            angle_speed = 2.5 / (raio + 0.1)
            self.initAngles[i] += angle_speed * t * 0.1

            # Gira em espiral horizontal
            self.vertices[i].x = raio * math.cos(self.initAngles[i])
            self.vertices[i].z = raio * math.sin(self.initAngles[i])

            # Sobe proporcionalmente ao raio (quanto mais perto do centro, mais sobe)
            fator_subida = 1.2 - min(raio / max_raio, 1.0)  # central = ~1.2, borda = ~0.2
            altura_local = 5.0 * t * fator_subida
            self.vertices[i].y = self.initial_ys[i] + altura_local

        # Salva a posição final do tornado para restaurar suavemente
        if t >= 1.0 and not self.restoreStart:
            self.restoreStart = [ponto(v.x, v.y, v.z) for v in self.vertices]

    # move suavemente os vertices da ultima posicao animada de volta para a posicao original
    def _estado_restauracao(self, frame_index):
        relative_frame = frame_index - (18 * 30)
        t = min(relative_frame / 180, 1.0)

        if not self.restoreStart:
            self.restoreStart = [ponto(v.x, v.y, v.z) for v in self.vertices]

        for i in range(len(self.vertices)):
            start = self.restoreStart[i]
            end = self.verticesBckp[i]
            self.vertices[i].x = start.x * (1 - t) + end.x * t
            self.vertices[i].y = start.y * (1 - t) + end.y * t
            self.vertices[i].z = start.z * (1 - t) + end.z * t

        if t >= 1.0:
            self.inicializou_redemoinho = False
            self.inicializou_dissolucao = False
            self.altura_centro_redemoinho = 0
            self.restoreStart = []

    # move os vertices suavemente ate suas posicoes de destino para formar a letra "s"
    def _estado_S(self):
        if not self.inicializou_S:
            self.inicializaDestinoS()
        for i in range(len(self.vertices)):
            destino = self.destinoS[i]
            self.vertices[i].x += (destino.x - self.vertices[i].x) * 0.05
            self.vertices[i].y += (destino.y - self.vertices[i].y) * 0.05
            self.vertices[i].z += (destino.z - self.vertices[i].z) * 0.05

    # move os vertices suavemente ate suas posicoes de destino para formar um coracao
    def _estado_coracao(self):
        if not self.inicializou_coracao:
            self.inicializaDestinoCoracao()
        for i in range(len(self.vertices)):
            destino = self.destinoCoracao[i]
            self.vertices[i].x += (destino.x - self.vertices[i].x) * 0.05
            self.vertices[i].y += (destino.y - self.vertices[i].y) * 0.05
            self.vertices[i].z += (destino.z - self.vertices[i].z) * 0.05
