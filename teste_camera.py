from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys
import math

# Posição da câmera
eye_x, eye_y, eye_z = 5.0, 3.0, 5.0
# Ponto observado
center_x, center_y, center_z = 0.0, 0.0, 0.0
# Vetor "up"
up_x, up_y, up_z = 0.0, 1.0, 0.0

# Controle de ângulo da câmera em torno do eixo Y
theta = 45.0
phi = 30.0
radius = 7.0

# Controle da rotação do cubo
angle_cube = 0.0

def init():
    glClearColor(0.1, 0.1, 0.1, 1.0)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, [2, 4, 2, 1])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1, 1, 1, 1])

def draw_axes():
    glBegin(GL_LINES)
    # Eixo X (vermelho)
    glColor3f(1, 0, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(3, 0, 0)
    # Eixo Y (verde)
    glColor3f(0, 1, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 3, 0)
    # Eixo Z (azul)
    glColor3f(0, 0, 1)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, 3)
    glEnd()

def draw_cube():
    glBegin(GL_QUADS)
    # Frente
    glColor3f(1, 0, 0)
    glVertex3f(-1, -1,  1)
    glVertex3f( 1, -1,  1)
    glVertex3f( 1,  1,  1)
    glVertex3f(-1,  1,  1)
    # Trás
    glColor3f(0, 1, 0)
    glVertex3f(-1, -1, -1)
    glVertex3f(-1,  1, -1)
    glVertex3f( 1,  1, -1)
    glVertex3f( 1, -1, -1)
    # Esquerda
    glColor3f(0, 0, 1)
    glVertex3f(-1, -1, -1)
    glVertex3f(-1, -1,  1)
    glVertex3f(-1,  1,  1)
    glVertex3f(-1,  1, -1)
    # Direita
    glColor3f(1, 1, 0)
    glVertex3f(1, -1, -1)
    glVertex3f(1,  1, -1)
    glVertex3f(1,  1,  1)
    glVertex3f(1, -1,  1)
    # Topo
    glColor3f(0, 1, 1)
    glVertex3f(-1, 1, -1)
    glVertex3f(-1, 1,  1)
    glVertex3f( 1, 1,  1)
    glVertex3f( 1, 1, -1)
    # Base
    glColor3f(1, 0, 1)
    glVertex3f(-1, -1, -1)
    glVertex3f( 1, -1, -1)
    glVertex3f( 1, -1,  1)
    glVertex3f(-1, -1,  1)
    glEnd()

def display():
    global angle_cube
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # Atualiza posição da câmera em coordenadas esféricas
    eye_x = radius * math.cos(math.radians(phi)) * math.sin(math.radians(theta))
    eye_y = radius * math.sin(math.radians(phi))
    eye_z = radius * math.cos(math.radians(phi)) * math.cos(math.radians(theta))

    # Define a câmera (gluLookAt)
    gluLookAt(eye_x, eye_y, eye_z,
              center_x, center_y, center_z,
              up_x, up_y, up_z)

    # Desenha eixos de referência
    draw_axes()

    # Rotaciona o cubo
    glPushMatrix()
    glRotatef(angle_cube, 1, 1, 0)
    draw_cube()
    glPopMatrix()

    glutSwapBuffers()

def reshape(width, height):
    if height == 0:
        height = 1
    aspect = width / height
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, aspect, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def keyboard(key, x, y):
    global theta, phi, radius
    key = key.decode("utf-8").lower()

    if key == 'w':  # aproxima
        radius -= 0.5
    elif key == 's':  # afasta
        radius += 0.5
    elif key == 'a':  # gira pra esquerda
        theta -= 5
    elif key == 'd':  # gira pra direita
        theta += 5
    elif key == 'q':  # sobe
        phi += 5
    elif key == 'e':  # desce
        phi -= 5
    elif key == chr(27):  # ESC
        sys.exit(0)

    if radius < 1.0:
        radius = 1.0
    if phi > 89: phi = 89
    if phi < -89: phi = -89

    glutPostRedisplay()

def timer(value):
    global angle_cube
    angle_cube += 1.0
    if angle_cube > 360:
        angle_cube -= 360
    glutPostRedisplay()
    glutTimerFunc(16, timer, 0)

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Transformacao de Visualizacao (Camera) - PyOpenGL + GLUT")
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutTimerFunc(0, timer, 0)
    glutMainLoop()

if __name__ == "__main__":
    main()
