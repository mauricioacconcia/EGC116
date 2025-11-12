from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys

angle = 0.0  # ângulo de rotação global

def init():
    glClearColor(0.1, 0.1, 0.1, 1.0)  # cor de fundo
    glEnable(GL_DEPTH_TEST)           # habilita profundidade
    glShadeModel(GL_SMOOTH)

def display():
    global angle
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # Configura a câmera (posição, alvo, up vector)
    gluLookAt(4, 4, 4,   # posição do observador
              0, 0, 0,   # ponto observado
              0, 1, 0)   # vetor "up"

    # Rotaciona o objeto
    glRotatef(angle, 0, 1, 0)
    glRotatef(angle / 2, 1, 0, 0)

    # Desenha um cubo colorido
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

    # Projeção ortográfica (paralela)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    if aspect >= 1.0:
        glOrtho(-3 * aspect, 3 * aspect, -3, 3, -10, 10)
    else:
        glOrtho(-3, 3, -3 / aspect, 3 / aspect, -10, 10)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def timer(value):
    global angle
    angle += 1.0
    if angle > 360:
        angle -= 360
    glutPostRedisplay()
    glutTimerFunc(16, timer, 0)  # ~60 FPS

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Camera com Projecao Paralela - PyOpenGL")
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutTimerFunc(0, timer, 0)
    glutMainLoop()

if __name__ == "__main__":
    main()
