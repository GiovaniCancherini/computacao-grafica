# Trabalho 1 - Computação Gráfica

## Melhorias pendentes

---

## Configuração do ambiente

### 1. Atualizar o `pip`

```sh
python -m pip install --upgrade pip
```

### 2. Criar e ativar um ambiente virtual

```sh
python -m venv opengl-venv
opengl-venv\Scripts\activate  # Para Windows
source opengl-venv/bin/activate  # Para Linux/Mac
```

Para desativar:

```sh
deactivate
```

### 3. Instalar dependências

```sh
pip install -r requirements.txt
```

## Versões utilizadas

- Python 3.12.5
- PyOpenGL 3.1.9
- PyOpenGL-accelerate 3.1.9

---

## Estrutura do projeto

O código contém as seguintes principais classes:

### \*\*Classe \*\***`Ponto`**

Representa um ponto no espaço tridimensional.

```python
class Ponto:
    def __init__(self, x: float, y: float, z: float = 0.0):
        self.x = x
        self.y = y
        self.z = z
```

### \*\*Classe \*\***`RGB`**

Define uma cor no formato RGB.

```python
class RGB():
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b
```

### \*\*Classe \*\***`Quadrado`**

Representa um quadrado com um ponto de referência, largura, altura e cor.

```python
class Quadrado():
    def __init__(self, ponto: Ponto, w: float, h: float, cor: RGB = RGB(1, 0, 0)):
        self.ponto = ponto
        self.w = w
        self.h = h
        self.cor = cor
```

---

## Lógica do jogo

### 1. Controle de tempo e animação

O código implementa controle de tempo para animações, incluindo variáveis globais:

- `tempo_antes` e `soma_dt` para medir o tempo.
- `frames` para contar os quadros renderizados.

### 2. Detecção de colisões

A função `boundingBox()` verifica se dois objetos colidem no espaço 2D.

```python
def boundingBox(triangulo_pos, triangulo_tam, quadrado_pos, quadrado_tam):
    tri_x_min = triangulo_pos.x
    tri_x_max = triangulo_pos.x + triangulo_tam
    tri_y_min = triangulo_pos.y
    tri_y_max = triangulo_pos.y + triangulo_tam
    
    quad_x_min = quadrado_pos.x
    quad_x_max = quadrado_pos.x + quadrado_tam
    quad_y_min = quadrado_pos.y
    quad_y_max = quadrado_pos.y + quadrado_tam
    
    return not (tri_x_max < quad_x_min or tri_x_min > quad_x_max or
                tri_y_max < quad_y_min or tri_y_min > quad_y_max)
```

### 3. Geração de cores dinâmica

A função `gerarCorPorID(id_valor)` cria cores únicas para cada objeto com base no ID.

```python
def gerarCorPorID(id_valor):
    r = ((id_valor * 37) % 230 + 10) / 255.0  
    g = ((id_valor * 59) % 230 + 10) / 255.0
    b = ((id_valor * 83) % 230 + 10) / 255.0
    return r, g, b
```

---

## Como rodar o projeto

1. Certifique-se de que o ambiente virtual está ativado.
2. Execute o arquivo principal do jogo:

```sh
python main.py
```

---

## Melhorias futuras

- Ajustar a definição de cores para utilizar o número de frames da entidade em vez do ID.
- Revisar as definições do arquivo de entrada.
- Implementar uma lógica aprimorada para detecção de colisões. Outros Algoritmos.
- Otimizar a renderização para melhorar a performance.

---

## Autor

Giovani Cancherini

