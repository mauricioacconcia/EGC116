#Controles
#
#2 alterna o segundo viewport ligado/desligado

#Setas movem o segundo viewport em pixels

#+ / - aumenta/diminui o tamanho do segundo viewport

#F ajusta o segundo viewport para quadrado máximo dentro da janela

#R reseta posição/tamanho do segundo viewport

#ESC sai

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys

# Estado da janela
win_w, win_h = 900, 600

# Segundo viewport (opcional)
show_vp2 = True
vp_x, vp_y = 40, 40
vp_w, vp_h = 320, 220

def init():
    glClearColor(0.10, 0.12, 0.14, 1.0)
    glDisable(GL_DEPTH_TEST)  # cena 2D/NDC para destacar viewport
    glShadeModel(GL_SMOOTH)

def draw_ndc_scene():
    """
    Cena definida diretamente em NDC (-1..1), com eixos e shapes coloridos.
    Mantemos PROJECTION=MODELVIEW=Identity para evidenciar o mapeamento do glViewport.
    """
    glMatrixMode(GL_PROJECTION); glLoadIdentity()
    glMatrixMode(GL_MODELVIEW);  glLoadIdentity()

    # Eixos NDC
    glLineWidth(1.5)
    glBegin(GL_LINES)
    # Eixo X (vermelho): y=0
    glColor3f(1,0,0); glVertex2f(-1,0); glVertex2f(1,0)
    # Eixo Y (verde): x=0
    glColor3f(0,1,0); glVertex2f(0,-1); glVertex2f(0,1)
    glEnd()

    # Retângulo unitário central (azul)
    glColor3f(0.2,0.6,1.0)
    glBegin(GL_LINE_LOOP)
    for x,y in [(-0.5,-0.5),(0.5,-0.5),(0.5,0.5),(-0.5,0.5)]:
        glVertex2f(x,y)
    glEnd()

    # Triângulo preenchido para perceber distorção/recorte
    glBegin(GL_TRIANGLES)
    glColor3f(1.0,0.5,0.2); glVertex2f(-0.8,-0.6)
    glColor3f(0.9,0.2,0.7); glVertex2f( 0.0, 0.9)
    glColor3f(0.2,0.9,0.5); glVertex2f( 0.8,-0.6)
    glEnd()

def draw_overlay_text():
    """
    Desenha texto em coordenadas de janela (pixels) para mostrar info do viewport.
    """
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    gluOrtho2D(0, win_w, 0, win_h)  # origem (0,0) canto inferior esquerdo
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()

    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)

    def print_text(x, y, s):
        glRasterPos2f(x, y)
        for ch in s:
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(ch))

    # Info do viewport principal
    glColor3f(1,1,1)
    print_text(10, win_h-20, f"Viewport principal: (0,0) {win_w}x{win_h}")

    # Fórmulas de mapeamento NDC -> janela
    print_text(10, win_h-40, "Mapeamento NDC -> janela (OpenGL):")
    print_text(10, win_h-58, "x_win = x_vp + (w_vp/2)*(x_ndc + 1)")
    print_text(10, win_h-74, "y_win = y_vp + (h_vp/2)*(y_ndc + 1)")

    # Info do segundo viewport
    if show_vp2:
        glColor3f(0.9,0.9,0.4)
        print_text(10, win_h-100, f"Viewport 2: ({vp_x},{vp_y}) {vp_w}x{vp_h}  [2 liga/desliga, setas movem, +/- redimensiona, F ajusta, R reseta]")

    # Moldura do segundo viewport
    if show_vp2:
        glColor3f(0.9,0.9,0.4)
        glBegin(GL_LINE_LOOP)
        glVertex2f(vp_x,       vp_y)
        glVertex2f(vp_x+vp_w,  vp_y)
        glVertex2f(vp_x+vp_w,  vp_y+vp_h)
        glVertex2f(vp_x,       vp_y+vp_h)
        glEnd()

    # Restaura
    glMatrixMode(GL_MODELVIEW);  glPopMatrix()
    glMatrixMode(GL_PROJECTION); glPopMatrix()

def display():
    glClear(GL_COLOR_BUFFER_BIT)

    # 1) Viewport principal ocupa a janela toda
    glViewport(0, 0, win_w, win_h)
    draw_ndc_scene()

    # 2) Viewport secundário opcional: mesma cena mapeada para um retângulo menor
    if show_vp2:
        glViewport(vp_x, vp_y, vp_w, vp_h)
        draw_ndc_scene()

    # Overlay em coordenadas de janela com fórmulas e guia
    draw_overlay_text()

    glutSwapBuffers()

def reshape(w, h):
    global win_w, win_h
    win_w, win_h = max(1, w), max(1, h)
    glViewport(0, 0, win_w, win_h)  # por padrão o principal ocupa toda a janela

def keyboard(key, x, y):
    global show_vp2, vp_x, vp_y, vp_w, vp_h
    k = key.decode("utf-8").lower()

    if k == '\x1b':  # ESC
        sys.exit(0)
    elif k == '2':
        show_vp2 = not show_vp2
    elif k == '+':
        vp_w = int(vp_w * 1.1); vp_h = int(vp_h * 1.1)
    elif k == '-':
        vp_w = max(20, int(vp_w / 1.1)); vp_h = max(20, int(vp_h / 1.1))
    elif k == 'f':
        # Ajusta como quadrado máximo centralizado verticalmente
        s = min(win_w, win_h)
        vp_w = vp_h = int(0.6 * s)
        vp_x = int((win_w - vp_w) * 0.5)
        vp_y = int((win_h - vp_h) * 0.2)
    elif k == 'r':
        vp_x, vp_y, vp_w, vp_h = 40, 40, 320, 220

    # Mantém o viewport dentro da janela
    vp_w = min(vp_w, win_w)
    vp_h = min(vp_h, win_h)
    vp_x = min(max(0, vp_x), max(0, win_w - vp_w))
    vp_y = min(max(0, vp_y), max(0, win_h - vp_h))

    glutPostRedisplay()

def special_keys(key, x, y):
    # Move o viewport secundário em pixels
    global vp_x, vp_y
    step = 10
    if key == GLUT_KEY_LEFT:
        vp_x -= step
    elif key == GLUT_KEY_RIGHT:
        vp_x += step
    elif key == GLUT_KEY_UP:
        vp_y += step
    elif key == GLUT_KEY_DOWN:
        vp_y -= step

    vp_x = min(max(0, vp_x), max(0, win_w - vp_w))
    vp_y = min(max(0, vp_y), max(0, win_h - vp_h))
    glutPostRedisplay()

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(win_w, win_h)
    glutCreateWindow(b"Viewport Mapping Demo - PyOpenGL + GLUT")
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    glutMainLoop()

if __name__ == "__main__":
    main()

