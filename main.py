import sys
import time
import ctypes
import winreg
from pynput import mouse

# --- CONFIGURACIÓN DE PARÁMETROS Y WIN32 API ---
SPI_SETCURSORS = 0x0057
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02

# Tamaños reales compatibles con el sistema de accesibilidad de Windows
TAMAÑOS_CURSOR = [32, 48, 64, 96, 128]
indice_tamaño_actual = 0  # Inicia en tamaño normal (32px)

print("==================================================")
print(" 🍏 macos-mouse v1.1 (Enhanced Windows Service)")
print("==================================================")
print("🟢 Servicio en ejecucion en segundo plano...")
print("💡 Instrucciones:")
print("   • Scroll sobre areas vacias/escritorio: Cambia tamaño del cursor.")
print("   • Presiona Ctrl+C en esta consola para salir.")
print("==================================================")

def cambiar_tamaño_cursor_windows(nuevo_tamaño):
    """
    Modifica la clave correcta de accesibilidad de Windows (CursorBaseSize)
    y refresca los cursores del sistema mediante user32.dll en tiempo real.
    """
    try:
        # Abrir la ruta correcta en el Registro de Windows para el tamaño del cursor
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Cursors", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "CursorBaseSize", 0, winreg.REG_DWORD, nuevo_tamaño)
        winreg.CloseKey(key)

        # Forzar a Windows a recargar los cursores del sistema inmediatamente
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETCURSORS, 0, None, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
        print(f"✨ [macos-mouse] ¡Tamaño de cursor actualizado a {nuevo_tamaño}px!")
    except Exception as e:
        print(f"⚠️ Error actualizando registro de cursor: {e}")

def calibrar_sistema_inicial():
    """
    Función de calibración automática opcional al arrancar:
    mueve ligeramente el cursor de forma imperceptible para sincronizar estados.
    """
    try:
        print("⚙️ Calibrando entorno de cursor del sistema...")
        controlador_mouse = mouse.Controller()
        pos_actual = controlador_mouse.position
        controlador_mouse.position = (pos_actual[0] + 1, pos_actual[1])
        controlador_mouse.position = pos_actual
        print("✅ Calibración completada con éxito.")
    except Exception as e:
        print(f"ℹ️ Aviso de calibración: {e}")

def esta_sobre_area_scrollable():
    """
    Detecta si el cursor se encuentra sobre el Escritorio o la Barra de Tareas (áreas neutras).
    """
    try:
        hwnd = ctypes.windll.user32.WindowFromPoint()
        class_name = ctypes.create_unicode_buffer(256)
        ctypes.windll.user32.GetClassNameW(hwnd, class_name, 256)
        
        # Si está sobre el fondo de escritorio o la barra de tareas, permite el zoom del cursor
        if class_name.value in ["Progman", "WorkerW", "Shell_TrayWnd", "Windows.UI.Core.CoreWindow"]:
            return False
        return True
    except:
        return False

def on_scroll(x, y, dx, dy):
    global indice_tamaño_actual
    
    # Si estamos en un área libre / no scrolleable, disparamos el cambio de tamaño estilo macOS
    if not esta_sobre_area_scrollable():
        if dy > 0:  # Scroll arriba -> Agrandar cursor
            if indice_tamaño_actual < len(TAMAÑOS_CURSOR) - 1:
                indice_tamaño_actual += 1
                cambiar_tamaño_cursor_windows(TAMAÑOS_CURSOR[indice_tamaño_actual])
        elif dy < 0:  # Scroll abajo -> Reducir cursor
            if indice_tamaño_actual > 0:
                indice_tamaño_actual -= 1
                cambiar_tamaño_cursor_windows(TAMAÑOS_CURSOR[indice_tamaño_actual])

def iniciar_servicio():
    calibrar_sistema_inicial()
    with mouse.Listener(on_scroll=on_scroll) as listener:
        listener.join()

if __name__ == "__main__":
    try:
        iniciar_servicio()
    except KeyboardInterrupt:
        print("\n🛑 Servicio detenido por el usuario.")
