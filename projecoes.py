from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys

# Variáveis globais
angulo = 0.0
modo_perspectiva = True  # começa em perspectiva

def init():
    glClearColor(0.1, 0.1, 0.1, 1.0)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)

def display():
    global angulo
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # Câmera
    gluLookAt(4, 4, 4,   # posição
              0, 0, 0,   # alvo
              0, 1, 0)   # up

    # Rotaciona o cubo
    glRotatef(angulo, 1, 1, 0)

    # Desenha o cubo
    glBegin(GL_QUADS)

    # Frente (vermelho)
    glColor3f(1, 0, 0)
    glVertex3f(-1, -1,  1)
    glVertex3f( 1, -1,  1)
    glVertex3f( 1,  1,  1)
    glVertex3f(-1,  1,  1)

    # Trás (verde)
    glColor3f(0, 1, 0)
    glVertex3f(-1, -1, -1)
    glVertex3f(-1,  1, -1)
    glVertex3f( 1,  1, -1)
    glVertex3f( 1, -1, -1)

    # Esquerda (azul)
    glColor3f(0, 0, 1)
    glVertex3f(-1, -1, -1)
    glVertex3f(-1, -1,  1)
    glVertex3f(-1,  1,  1)
    glVertex3f(-1,  1, -1)

    # Direita (amarelo)
    glColor3f(1, 1, 0)
    glVertex3f(1, -1, -1)
    glVertex3f(1,  1, -1)
    glVertex3f(1,  1,  1)
    glVertex3f(1, -1,  1)

    # Topo (ciano)
    glColor3f(0, 1, 1)
    glVertex3f(-1, 1, -1)
    glVertex3f(-1, 1,  1)
    glVertex3f( 1, 1,  1)
    glVertex3f( 1, 1, -1)

    # Base (magenta)
    glColor3f(1, 0, 1)
    glVertex3f(-1, -1, -1)
    glVertex3f( 1, -1, -1)
    glVertex3f( 1, -1,  1)
    glVertex3f(-1, -1,  1)

    glEnd()

    glutSwapBuffers()

def reshape(width, height):
    if height == 0:
        height = 1
    aspect = width / height

    glViewport(0, 0, width, height)
    configurar_projecao(aspect)

def configurar_projecao(aspect):
    """Define a matriz de projeção de acordo com o modo atual"""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    if modo_perspectiva:
        gluPerspective(45.0, aspect, 1.0, 50.0)
    else:
        if aspect >= 1.0:
            glOrtho(-3 * aspect, 3 * aspect, -3, 3, -10, 10)
        else:
            glOrtho(-3, 3, -3 / aspect, 3 / aspect, -10, 10)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def keyboard(key, x, y):
    global modo_perspectiva
    key = key.decode("utf-8").lower()
    if key == 'p':
        modo_perspectiva = True
        print("Projeção: perspectiva")
        reshape(glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT))
    elif key == 'o':
        modo_perspectiva = False
        print("Projeção: ortográfica")
        reshape(glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT))
    elif key == chr(27):  # ESC
        sys.exit(0)

def timer(value):
    global angulo
    angulo += 1.0
    if angulo > 360:
        angulo -= 360
    glutPostRedisplay()
    glutTimerFunc(16, timer, 0)  # 60 FPS

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutInitWindowPosition(150, 100)
    glutCreateWindow(b"Alternar Projecao: P (Perspectiva) / O (Ortografica)")
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutTimerFunc(0, timer, 0)
    glutMainLoop()

if __name__ == "__main__":
    main()
