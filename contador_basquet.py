import tkinter as tk
import time
import serial

try:
    ser = serial.Serial('COM3', 9600)
except serial.SerialException:
    ser = None
    print("⚠ No se pudo abrir el puerto COM3.")

#------------
# MARCADOR
#------------
class MarcadorBasquet:
    def __init__(self, master, cronometro=None):
        self.master = master
        self.cronometro = cronometro  # 🔹 referencia al cronómetro

        # ESTADO MARCADOR
        self.contador = 0
        self.contador_var = tk.StringVar(value=str(self.contador))

        # TÍTULO
        tk.Label(master, text="Alias: krapadox", font=("Arial", 50, "bold"), bg="#000000", fg="white").grid(row=0, column=0, columnspan=3, pady=10)

        # CONTADOR ÚNICO, CENTRADO
        self.contador_label = tk.Label(master, textvariable=self.contador_var, font=("Arial", 150, "bold"), bg="#000000", fg="white")
        self.contador_label.grid(row=1, column=0, columnspan=3, pady=40)

        # KEYBINDS PARA MODIFICAR CONTADOR
        self.master.bind("a", lambda e: self.incrementar())
        self.master.bind("z", lambda e: self.restar())

    def incrementar(self):
        if self.cronometro is None or self.cronometro.running:
            self.contador += 1
            self.contador_var.set(str(self.contador))

    def restar(self):
        if (self.cronometro is None or self.cronometro.running) and self.contador > 0:
            self.contador -= 1
            self.contador_var.set(str(self.contador))

    def leer_serial(self):
        try:
            if ser and ser.in_waiting > 0:
                linea = ser.readline().decode('utf-8', errors='ignore').strip()
                print(f"Linea recibida: {linea}")  # Debug
                if linea == "A":
                    self.incrementar()
                elif linea == "B":
                    self.restar()
        except Exception as e:
            print("⚠ Error al leer del puerto serial:", e)
        self.master.after(50, self.leer_serial)


# ------------
# CRONOMETRO
# ------------
class Cronometro:
    def __init__(self, master, limite_ms=60000):  # límite por defecto: 1 minuto
        self.master = master
        self.limite_ms = limite_ms

        # Estado
        self.running = False
        self.start_time = None
        self.elapsed_ms = 0
        self.job = None

        # UI
        self.display = tk.StringVar(value="00:00.000")
        self.display_label = tk.Label(master, textvariable=self.display, font=("Arial", 80), bg="#000000", fg="white")
        self.display_label.grid(row=2, column=0, columnspan=3, pady=15)

        self.help_label = tk.Label(master,
            text="Espacio: iniciar/pausar   |   Retroceso: reiniciar",
            font=("Arial", 30), bg="#000000", fg="white")
        self.help_label.grid(row=3, column=0, columnspan=3)

        # Keybinds
        self.master.bind("<space>", self._on_space)
        self.master.bind("<BackSpace>", lambda e: self.reiniciar())

    def _on_space(self, event=None):
        if self.running:
            self.pausar()
        else:
            self.iniciar()

    def iniciar(self):
        if not self.running:
            self.running = True
            self.start_time = time.perf_counter() - (self.elapsed_ms / 1000.0)
            if self.job is None:
                self._tick()
        self.display_label.config(fg="white")

    def pausar(self):
        if self.running:
            self.running = False
            self.elapsed_ms = int((time.perf_counter() - self.start_time) * 1000)
            if self.job is not None:
                self.master.after_cancel(self.job)
                self.job = None
        self.display_label.config(fg="red")

    def reiniciar(self):
        self.running = False
        if self.job is not None:
            self.master.after_cancel(self.job)
            self.job = None
        self.elapsed_ms = 0
        self.start_time = None
        self.display.set("00:00.000")
        self.display_label.config(fg="white")

    def _tick(self):
        if not self.running:
            self.job = None
            return

        now = time.perf_counter()
        self.elapsed_ms = int((now - self.start_time) * 1000)

        # bloquear si alcanza el límite
        if self.limite_ms is not None and self.elapsed_ms >= self.limite_ms:
            self.elapsed_ms = self.limite_ms
            self.running = False
            self.job = None

        total_s = self.elapsed_ms // 1000
        ms = self.elapsed_ms % 1000
        m, s = divmod(total_s, 60)
        self.display.set("{:02}:{:02}.{:03}".format(m, s, ms))

        if self.running:  # solo programar el siguiente tick si sigue corriendo
            self.job = self.master.after(10, self._tick)


# INICIO
if __name__ == "__main__":
    ventana = tk.Tk()
    ventana.geometry("800x500")
    ventana.attributes("-fullscreen", True)
    ventana.configure(bg="#000000")
    for i in range(7):
        ventana.grid_rowconfigure(i, weight=1)
    for j in range(3):
        ventana.grid_columnconfigure(j, weight=1)

    # Crear cronómetro
    mi_cronometro = Cronometro(ventana, limite_ms=60000)  # 1 minuto
    # Crear marcador y pasarle la referencia del cronómetro (comentar las 2 de abajo para desactivar)
    marcador = MarcadorBasquet(ventana, cronometro=mi_cronometro)
    marcador.leer_serial()

    ventana.bind("<Escape>", lambda e: ventana.destroy())
    ventana.mainloop()
