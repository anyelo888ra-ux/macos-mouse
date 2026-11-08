import sys
import time
from pynput import mouse
import ctypes

# Coeficientes para el tamaño del cursor en Windows (SPI_SETMOUSESPEED / SystemParametersInfo)
# Nota: Windows maneja el tamaño del cursor mediante claves del registro o SPI, 
# aquí simulamos la lógica de detección dinámica de scroll vs zoom.

print("🟢 [macos-mouse] Iniciado en segundo plano...")
print("ℹ️ Haz scroll sobre áreas vacías para cambiar el zoom/tamaño del cursor.")

def esta_sobre_area_scrollable():
    # Placeholder lógico: aquí puedes integrar detección de ventanas 
    # o simplemente evaluar si el contenedor activo permite desplazamiento.
    # Por defecto, simulamos que retorna False en escritorios/áreas libres.
    return False

def on_scroll(x, y, dx, dy):
    if not esta_sobre_area_scrollable():
        if dy > 0:
            print("🔍 [Zoom] Scroll arriba -> Agrandando puntero...")
            # Lógica para incrementar escala del cursor en Windows
        else:
            print("🔍 [Zoom] Scroll abajo -> Reduciendo puntero...")
            # Lógica para reducir escala del cursor en Windows

# Escuchar los eventos del mouse de forma global
def iniciar_escucha():
    with mouse.Listener(on_scroll=on_scroll) as listener:
        listener.join()

if __name__ == "__main__":
    try:
        iniciar_escucha()
    except KeyboardInterrupt:
        print("\n🛑 [macos-mouse] Detenido por el usuario.")
