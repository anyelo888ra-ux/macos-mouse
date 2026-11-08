import sys
import time
import ctypes
from pynput import mouse

# --- CONFIGURACIÓN DE PARÁMETROS Y WIN32 API ---
# SPI_SETCURSORS fuerza a Windows a recargar el esquema de punteros del sistema
SPI_SETCURSORS = 0x0057
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02

# Clave del registro de Windows donde se guarda la escala de accesibilidad del mouse (CursorBaseSize)
# Valores estándar de Windows: 32 (Normal), 48 (Mediano), 64 (Grande), 96 (Extra Grande), 128 (Gigante)
TAMAÑOS_CURSOR = [32, 48, 64, 96, 128]
indice_tamaño_actual = 0  # Inicia en 32px

print("==================================================")
print(" 🍏 macos-mouse v1.0 (Windows Standalone EXE)")
print("==================================================")
print("🟢 Servicio en ejecucion en segundo plano...")
print("💡 Instrucciones:")
print("   • Scroll sobre listas/paginas: Scroll normal.")
print("   • Scroll sobre areas vacias/escritorio: Cambia el tamaño del cursor estilo macOS.")
print("   • Presiona Ctrl+C en esta ventana para salir.")
print("==================================================")

def cambiar_tamaño_cursor_windows(nuevo_tamaño):
    """
    Modifica la clave de registro de Windows para el tamaño del puntero 
    y actualiza los cursores del sistema en tiempo real.
    """
    import winreg
    try:
        # Abrir clave de registro de Accesibilidad de Cursores
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Accessibility", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "DynamicCursorSize", 0, winreg.REG_DWORD, nuevo_tamaño)
        winreg.CloseKey(key)

        # Refrescar los cursores del sistema mediante la Win32 API (User32.dll)
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETCURSORS, 0, None, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
        print(f"✨ [macos-mouse] Tamaño de cursor actualizado a: {nuevo_tamaño}px")
    except Exception as e:
        print(f"⚠️ Error actualizando registro: {e}")

def esta_sobre_area_scrollable():
    """
    Evalua si el cursor se encuentra sobre una ventana o control scrolleable.
    """
    # En la version inicial portable, se activa el zoom en zonas neutras (Desktop / Shell_TrayWnd)
    try:
        hwnd = ctypes.windll.user32.WindowFromPoint()
        class_name = ctypes.create_unicode_buffer(256)
        ctypes.windll.user32.GetClassNameW(hwnd, class_name, 256)
        
        # Si esta sobre el escritorio de Windows (Progman/WorkerW) o la barra de tareas (Shell_TrayWnd)
        if class_name.value in ["Progman", "WorkerW", "Shell_TrayWnd"]:
            return False
        return True
    except:
        return False

def on_scroll(x, y, dx, dy):
    global indice_tamaño_actual
    
    # Si no es un contenedor de scroll normal (ej. sobre el escritorio o areas neutras)
    if not esta_sobre_area_scrollable():
        if dy > 0: # Scroll hacia arriba -> Aumentar tamaño
            if indice_tamaño_actual < len(TAMAÑOS_CURSOR) - 1:
                indice_tamaño_actual += 1
                cambiar_tamaño_cursor_windows(TAMAÑOS_CURSOR[indice_tamaño_actual])
        elif dy < 0: # Scroll hacia abajo -> Reducir tamaño
            if indice_tamaño_actual > 0:
                indice_tamaño_actual -= 1
                cambiar_tamaño_cursor_windows(TAMAÑOS_CURSOR[indice_tamaño_actual])

def iniciar_servicio():
    with mouse.Listener(on_scroll=on_scroll) as listener:
        listener.join()

if __name__ == "__main__":
    try:
        iniciar_servicio()
    except KeyboardInterrupt:
        print("
🛑 Servicio detenido.")
