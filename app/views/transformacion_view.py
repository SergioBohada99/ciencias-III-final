import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Optional, Dict
import math


class TransformacionClavesView(ttk.Frame):
    def __init__(self, parent: tk.Misc, app) -> None:
        super().__init__(parent)

        title = ttk.Label(self, text="Transformación de claves (por bloques)", style="Title.TLabel")
        title.pack(pady=(20, 5))

        # Parámetros
        params = ttk.Frame(self, style="Panel.TFrame", padding=10)
        params.pack(fill=tk.X, padx=4, pady=6)

        lbl_n = ttk.Label(params, text="Tamaño tabla (n):")
        lbl_n.grid(row=0, column=0, sticky="w", padx=(0, 6))
        self.entry_n = ttk.Entry(params, width=8)
        self.entry_n.insert(0, "10")
        self.entry_n.grid(row=0, column=1, padx=(0, 12))

        lbl_digits = ttk.Label(params, text="Dígitos clave:")
        lbl_digits.grid(row=0, column=2, sticky="w", padx=(0, 6))
        self.entry_digits = ttk.Entry(params, width=6)
        self.entry_digits.insert(0, "4")
        self.entry_digits.grid(row=0, column=3, padx=(0, 12))

        lbl_hash = ttk.Label(params, text="Función hash:")
        lbl_hash.grid(row=0, column=4, sticky="w", padx=(0, 6))
        self.hash_mode = tk.StringVar(value="modulo")
        combo_hash = ttk.Combobox(
            params,
            values=["modulo", "cuadrado", "plegamiento", "truncamiento", "conversion_bases"],
            state="readonly",
            textvariable=self.hash_mode,
            width=18,
        )
        combo_hash.grid(row=0, column=5, padx=(0, 12))

        lbl_base = ttk.Label(params, text="Base (conv.):")
        lbl_base.grid(row=0, column=6, sticky="w", padx=(0, 6))
        self.entry_base = ttk.Entry(params, width=6)
        self.entry_base.insert(0, "7")
        self.entry_base.grid(row=0, column=7, padx=(0, 12))

        # Segunda fila de parámetros
        lbl_probe = ttk.Label(params, text="Resolución colisión:")
        lbl_probe.grid(row=1, column=0, sticky="w", padx=(0, 6), pady=(6, 0))
        self.probe_mode = tk.StringVar(value="lineal")
        probe_combo = ttk.Combobox(
            params,
            values=["lineal", "cuadratica", "doble_hash", "arreglo_anidado", "lista_enlazada"],
            state="readonly",
            textvariable=self.probe_mode,
            width=18,
        )
        probe_combo.grid(row=1, column=1, columnspan=2, sticky="w", pady=(6, 0))
        probe_combo.bind("<<ComboboxSelected>>", self._on_probe_change)

        btn_new = ttk.Button(params, text="Generar datos", command=self._on_generate)
        btn_new.grid(row=1, column=6, columnspan=2, pady=(6, 0), sticky="w")
        
		# NUEVO: botón para crear la estructura de bloques
        btn_create_struct = ttk.Button(params, text="Crear estructura", command=self._on_create_structure)
        btn_create_struct.grid(row=1, column=4, padx=(6, 0), pady=(6, 0), sticky="w")

        # Panel paralelo
        panel = ttk.Frame(self, padding=6)
        panel.pack(fill=tk.BOTH, expand=True)

        # Panel de operaciones (izquierda)
        ops = ttk.Frame(panel, style="Panel.TFrame", padding=10)
        ops.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))

        lbl_key = ttk.Label(ops, text="Clave:")
        lbl_key.grid(row=0, column=0, sticky="w")
        self.entry_key = ttk.Entry(ops, width=16)
        self.entry_key.grid(row=1, column=0, pady=(0, 10))

        btn_insert = ttk.Button(ops, text="Insertar", style="Retro.TButton", command=self._on_insert)
        btn_insert.grid(row=2, column=0, pady=4, sticky="ew")

        btn_delete = ttk.Button(ops, text="Eliminar", style="Retro.TButton", command=self._on_delete)
        btn_delete.grid(row=3, column=0, pady=4, sticky="ew")

        btn_search = ttk.Button(ops, text="Buscar", style="Retro.TButton", command=self._on_search)
        btn_search.grid(row=4, column=0, pady=4, sticky="ew")

        btn_reset = ttk.Button(ops, text="Reiniciar", command=self._on_init)
        btn_reset.grid(row=5, column=0, pady=4, sticky="ew")

        self.status = ttk.Label(ops, text="Estado: listo", wraplength=120)
        self.status.grid(row=6, column=0, pady=(12, 0), sticky="w")

        # Panel de visualización (canvas de bloques)
        viz = ttk.Frame(panel, style="Panel.TFrame", padding=8)
        viz.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        canvas_wrap = ttk.Frame(viz)
        canvas_wrap.pack(fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(canvas_wrap, background="#ffffff", height=460)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vscroll = ttk.Scrollbar(canvas_wrap, orient="vertical", command=self.canvas.yview)
        vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=vscroll.set)

        # Panel guardar / cargar
        file_panel = ttk.Frame(self, style="Panel.TFrame", padding=8)
        file_panel.pack(fill=tk.X, padx=4, pady=6)

        btn_save_close = ttk.Button(file_panel, text="Guardar y cerrar", command=self._on_save_and_close)
        btn_save_close.grid(row=0, column=0, padx=4, pady=2)

        btn_save = ttk.Button(file_panel, text="Guardar", command=self._on_save)
        btn_save.grid(row=0, column=1, padx=4, pady=2)

        btn_load = ttk.Button(file_panel, text="Cargar", command=self._on_load)
        btn_load.grid(row=0, column=2, padx=4, pady=2)

        back = ttk.Button(self, text="← Volver", command=lambda: app.navigate("externas"))
        back.pack(pady=6)

        self.app = app

        # Estructuras de datos (como en HashView)
        self._table: List[Optional[int]] = []
        self._table_anidado: List[List[int]] = []   # arreglo_anidado
        self._table_enlazada: List[List[int]] = []  # lista_enlazada

        # Índice de bloque y posición dentro de la cadena para resaltar en el canvas
        self._highlight_slot: Optional[int] = None
        self._highlight_pos: Optional[int] = None
        self.structure_created = False
        
		# Parámetros de bloques (similar a BloquesBinariaView)
        self.n: int = 0          # total de direcciones/registros
        self.b: int = 0          # número de bloques
        self.block_size: int = 0 # registros por bloque

        self._on_init()

    # ------------------ Utilidades de configuración ------------------

    def _on_probe_change(self, event=None) -> None:
        self._on_init()

    def _read_params(self) -> tuple:
        """Lee n y dígitos, y calcula número de bloques y tamaño de bloque."""
        try:
            n = int(self.entry_n.get())
        except Exception:
            n = 10
        try:
            d = int(self.entry_digits.get())
        except Exception:
            d = 4

        n = max(1, n)
        d = max(1, d)

        # Cálculo de bloques como en BloquesBinariaView:
        # B = ceil(sqrt(n))
        # tamaño_bloque = ceil(n / B)
        self.n = n
        self.b = math.ceil(math.sqrt(n))
        self.block_size = math.ceil(n / self.b) if self.b > 0 else n

        return n, d

    def _on_create_structure(self) -> None:
        """
        Crea / reinicializa la estructura de la tabla hash,
        usando n, número de bloques (B) y tamaño de bloque calculados.
        """
        self._read_params()
        self.structure_created = True
        # Reutilizamos la lógica de _on_init para resetear estructuras
        self._on_init()

        # Mensaje de estado específico para este botón
        self.status.configure(
            text=(
                f"Estructura creada: n={self.n}, "
                f"bloques={self.b}, registros por bloque={self.block_size}"
            )
        )

    def _read_base(self) -> int:
        try:
            b = int(self.entry_base.get())
        except Exception:
            b = 7
        if b < 2:
            b = 2
        if b > 16:
            b = 16
        return b

    # ------------------ Funciones hash ------------------

    def _hash(self, k: int, n: int, d: int) -> int:
        mode = self.hash_mode.get()
        table_size, _ = self._read_params()

        if mode == "modulo":
            return k % table_size

        elif mode == "cuadrado":
            # Método del cuadrado central
            k2 = k * k
            k2_str = str(k2).zfill(2 * d)
            center_len = d
            start = max(0, (len(k2_str) - center_len) // 2)
            center = int(k2_str[start:start + center_len]) if k2_str[start:start + center_len] else 0
            return center % table_size

        elif mode == "plegamiento":
            # Plegamiento en partes de 2 dígitos, se multiplican y se toman los primeros 2 dígitos
            k_str = str(k)
            part_size = 2
            parts = []
            for i in range(0, len(k_str), part_size):
                part = k_str[i:i + part_size]
                if part:
                    parts.append(int(part))

            if not parts:
                result = 0
            elif len(parts) == 1:
                result = parts[0]
            else:
                result = 1
                for p in parts:
                    result *= p

            result_str = str(result)
            if len(result_str) >= part_size:
                direccion = int(result_str[:part_size])
            else:
                direccion = result

            return (direccion + 1) % table_size

        elif mode == "truncamiento":
            # Truncamiento: usa el dígito 1 y 3 (posición 0 y 2)
            k_str = str(k).zfill(d)
            d1 = k_str[0] if len(k_str) > 0 else "0"
            d3 = k_str[2] if len(k_str) > 2 else "0"
            direccion = int(d1 + d3)
            return (direccion + 1) % table_size

        elif mode == "conversion_bases":
            # Conversión de bases: convierte a base b y suma los dígitos
            base = self._read_base()
            valor = k
            if valor == 0:
                suma = 0
            else:
                suma = 0
                while valor > 0:
                    suma += valor % base
                    valor //= base
            return suma % table_size

        return k % table_size

    def _double_hash(self, d: int, n: int) -> int:
        """Doble hash: H(D) = (D + 1) mod n + 1"""
        return ((d + 1) % n) + 1

    def _probe_indices(self, k: int, n: int, d: int):
        """Genera índices de prueba según el método de resolución de colisiones."""
        base = self._hash(k, n, d)
        mode = self.probe_mode.get()

        if mode == "lineal":
            # D, D+1, D+2, ...
            for t in range(n):
                yield (base + t) % n
        elif mode == "cuadratica":
            # D, D+1², D+2², ...
            for t in range(n):
                yield (base + t * t) % n
        elif mode == "doble_hash":
            current = base
            visited = set()
            for _ in range(n):
                if current in visited:
                    break
                visited.add(current)
                yield current
                current = (current + self._double_hash(current, n)) % n

    # ------------------ Validación clave ------------------

    def _validate_key(self, s: str, d: int) -> Optional[int]:
        if not s.isdigit():
            messagebox.showerror("Error", "La clave debe ser numérica.")
            return None
        if len(s) != d:
            messagebox.showerror("Error", f"La clave debe tener exactamente {d} dígitos.")
            return None
        return int(s)

    # ------------------ Inicializar / generar datos ------------------

    def _on_init(self) -> None:
        n, _ = self._read_params()
        mode = self.probe_mode.get()

        if mode in ["lineal", "cuadratica", "doble_hash"]:
            self._table = [None] * n
            self._table_anidado = []
            self._table_enlazada = []
        elif mode == "arreglo_anidado":
            self._table = [None] * n
            self._table_anidado = [[] for _ in range(n)]
            self._table_enlazada = []
        else:  # lista_enlazada
            self._table = []
            self._table_anidado = []
            self._table_enlazada = [[] for _ in range(n)]

        self._highlight_slot = None
        self._highlight_pos = None
        self.status.configure(
            text=(
                f"Tabla reiniciada: n={self.n}, "
                f"bloques={self.b}, registros por bloque={self.block_size}"
            )
        )
        self._draw()

    def _on_generate(self) -> None:
        import random
        n, d = self._read_params()
        self._on_init()

        max_value = 10**d - 1
        min_value = 10 ** (d - 1) if d > 1 else 0
        target = max(1, n // 2)
        inserted = 0
        seen = set()
        attempts = 0
        max_attempts = target * 20

        while inserted < target and attempts < max_attempts:
            attempts += 1
            k = random.randint(min_value, max_value)
            if k in seen:
                continue
            seen.add(k)
            if self._insert_key(k, n, d, animate=False):
                inserted += 1

        self.status.configure(text=f"Generados {inserted} elementos")
        self._draw()

    # ------------------ Inserción / búsqueda / borrado ------------------

    def _insert_key(self, k: int, n: int, d: int, animate: bool = True) -> bool:
        mode = self.probe_mode.get()
        base = self._hash(k, n, d)

        if mode in ["lineal", "cuadratica", "doble_hash"]:
            # evitar duplicados
            for idx in self._probe_indices(k, n, d):
                if self._table[idx] is None:
                    break
                if self._table[idx] == k:
                    return False

            for idx in self._probe_indices(k, n, d):
                if animate:
                    self._highlight_slot = idx
                    self._highlight_pos = 0
                    self._draw()
                    self.update_idletasks()
                    self.after(300)
                if self._table[idx] is None:
                    self._table[idx] = k
                    return True
            return False  # tabla llena

        elif mode == "arreglo_anidado":
            if self._table[base] == k:
                return False
            if k in self._table_anidado[base]:
                return False

            if animate:
                self._highlight_slot = base
                self._highlight_pos = 0 if self._table[base] is None else len(self._table_anidado[base]) + 1
                self._draw()
                self.update_idletasks()
                self.after(300)

            if self._table[base] is None:
                self._table[base] = k
            else:
                self._table_anidado[base].append(k)
            return True

        else:  # lista_enlazada
            if k in self._table_enlazada[base]:
                return False

            if animate:
                self._highlight_slot = base
                self._highlight_pos = len(self._table_enlazada[base])
                self._draw()
                self.update_idletasks()
                self.after(300)

            self._table_enlazada[base].append(k)
            return True

    def _on_insert(self) -> None:
        n, d = self._read_params()
        key_str = self.entry_key.get().strip()
        k = self._validate_key(key_str, d)
        if k is None:
            return

        mode = self.probe_mode.get()
        # Capacidad para direccionamiento abierto
        if mode in ["lineal", "cuadratica", "doble_hash"]:
            if sum(1 for v in self._table if v is not None) >= n:
                messagebox.showerror("Error", "Tabla llena")
                return

        if self._insert_key(k, n, d, animate=True):
            base = self._hash(k, n, d)
            self.status.configure(text=f"Insertado {k} (hash={base})")
            self.entry_key.delete(0, tk.END)
            self._highlight_slot = None
            self._highlight_pos = None
            self._draw()
        else:
            messagebox.showerror("Error", "No se pudo insertar (duplicado o tabla llena)")

    def _on_search(self) -> None:
        n, d = self._read_params()
        key_str = self.entry_key.get().strip()
        k = self._validate_key(key_str, d)
        if k is None:
            return

        mode = self.probe_mode.get()
        base = self._hash(k, n, d)

        if mode in ["lineal", "cuadratica", "doble_hash"]:
            for idx in self._probe_indices(k, n, d):
                if self._table[idx] is None:
                    break
                self._highlight_slot = idx
                self._highlight_pos = 0
                self._draw()
                self.update_idletasks()
                self.after(500)
                if self._table[idx] == k:
                    self.status.configure(text=f"Encontrado {k} en bloque {idx}")
                    return

        elif mode == "arreglo_anidado":
            self._highlight_slot = base
            self._highlight_pos = 0
            self._draw()
            self.update_idletasks()
            self.after(500)

            if self._table[base] == k:
                self.status.configure(text=f"Encontrado {k} en bloque {base} (principal)")
                return
            if k in self._table_anidado[base]:
                pos = self._table_anidado[base].index(k)
                self._highlight_pos = pos + 1
                self._draw()
                self.update_idletasks()
                self.after(500)
                self.status.configure(text=f"Encontrado {k} en bloque {base}, colisión #{pos+1}")
                return

        else:  # lista_enlazada
            self._highlight_slot = base
            self._highlight_pos = 0
            self._draw()
            self.update_idletasks()
            self.after(500)

            if k in self._table_enlazada[base]:
                pos = self._table_enlazada[base].index(k)
                self._highlight_pos = pos
                self._draw()
                self.update_idletasks()
                self.after(500)
                self.status.configure(text=f"Encontrado {k} en bloque {base}, posición {pos}")
                return

        self._highlight_slot = None
        self._highlight_pos = None
        self._draw()
        self.status.configure(text="No encontrado")
        messagebox.showinfo("Búsqueda", "Valor no encontrado")

    def _on_delete(self) -> None:
        n, d = self._read_params()
        key_str = self.entry_key.get().strip()
        k = self._validate_key(key_str, d)
        if k is None:
            return

        mode = self.probe_mode.get()
        base = self._hash(k, n, d)

        if mode in ["lineal", "cuadratica", "doble_hash"]:
            for idx in self._probe_indices(k, n, d):
                if self._table[idx] is None:
                    break
                self._highlight_slot = idx
                self._highlight_pos = 0
                self._draw()
                self.update_idletasks()
                self.after(500)
                if self._table[idx] == k:
                    self._table[idx] = None
                    self._highlight_slot = None
                    self._highlight_pos = None
                    self.status.configure(text=f"Eliminado {k}")
                    self._draw()
                    return

        elif mode == "arreglo_anidado":
            self._highlight_slot = base
            self._highlight_pos = 0
            self._draw()
            self.update_idletasks()
            self.after(500)

            if self._table[base] == k:
                # mover primer anidado a principal si existe
                if self._table_anidado[base]:
                    self._table[base] = self._table_anidado[base].pop(0)
                else:
                    self._table[base] = None
                self._highlight_slot = None
                self._highlight_pos = None
                self.status.configure(text=f"Eliminado {k}")
                self._draw()
                return
            elif k in self._table_anidado[base]:
                pos = self._table_anidado[base].index(k)
                self._highlight_pos = pos + 1
                self._draw()
                self.update_idletasks()
                self.after(500)
                self._table_anidado[base].remove(k)
                self._highlight_slot = None
                self._highlight_pos = None
                self.status.configure(text=f"Eliminado {k}")
                self._draw()
                return

        else:  # lista_enlazada
            self._highlight_slot = base
            self._highlight_pos = 0
            self._draw()
            self.update_idletasks()
            self.after(500)

            if k in self._table_enlazada[base]:
                pos = self._table_enlazada[base].index(k)
                self._highlight_pos = pos
                self._draw()
                self.update_idletasks()
                self.after(500)
                self._table_enlazada[base].remove(k)
                self._highlight_slot = None
                self._highlight_pos = None
                self.status.configure(text=f"Eliminado {k}")
                self._draw()
                return

        self._highlight_slot = None
        self._highlight_pos = None
        self._draw()
        self.status.configure(text="No encontrado")
        messagebox.showinfo("Búsqueda", "Valor no encontrado")

    # ------------------ Dibujo de bloques en canvas ------------------

    def _draw(self) -> None:
        self.canvas.delete("all")
        
        if not self.structure_created:
            return

        # Asegurar parámetros actualizados (incluye n, b, block_size)
        n, d = self._read_params()
        mode = self.probe_mode.get()

        # Asegurar tamaños de estructuras según el modo
        if mode in ["lineal", "cuadratica", "doble_hash"]:
            if len(self._table) < n:
                self._table.extend([None] * (n - len(self._table)))
        elif mode == "arreglo_anidado":
            if len(self._table) < n:
                self._table.extend([None] * (n - len(self._table)))
            if len(self._table_anidado) < n:
                self._table_anidado.extend([[] for _ in range(n - len(self._table_anidado))])
        else:  # lista_enlazada
            if len(self._table_enlazada) < n:
                self._table_enlazada.extend([[] for _ in range(n - len(self._table_enlazada))])

        self.canvas.update_idletasks()
        width = max(self.canvas.winfo_width(), 600)
        height = max(self.canvas.winfo_height(), 400)

        # Si no hay estructura válida, mostrar mensaje
        if n <= 0 or self.b <= 0 or self.block_size <= 0:
            self.canvas.create_text(
                width // 2,
                height // 2,
                text="Defina n y use 'Crear estructura' para inicializar los bloques",
                fill="#666666",
                font=("MS Sans Serif", 11),
            )
            return

        block_count = self.b
        block_size = self.block_size

        # Layout horizontal: bloques uno al lado del otro
        margin_x = 20
        gap_x = 12
        total_gap = gap_x * max(0, block_count - 1)
        # Ancho de cada bloque para que todos entren en el canvas
        block_width = (width - 2 * margin_x - total_gap) / max(1, block_count)
        block_width = max(120, min(220, block_width))

        header_height = 28
        cell_height = 24
        start_y = 40

        max_bottom = 0

        for block_idx in range(block_count):
            block_x = margin_x + block_idx * (block_width + gap_x)
            block_y = start_y

            # Rango de direcciones que pertenecen a este bloque
            start_index = block_idx * block_size
            end_index = start_index + block_size - 1
            if start_index >= n:
                # Bloque completamente fuera del rango real de la tabla
                continue
            real_end = min(end_index, n - 1)

            # Header del bloque
            block_color = "#4da3ff" if block_idx == self._highlight_slot else "#e0e0e0"
            outline_color = "#255eaa" if block_idx == self._highlight_slot else "#808080"

            self.canvas.create_rectangle(
                block_x,
                block_y,
                block_x + block_width,
                block_y + header_height,
                fill=block_color,
                outline=outline_color,
                width=2,
            )

            # Mostramos el número de bloque y el rango de direcciones
            header_text = f"Bloque {block_idx + 1}\n[{start_index}..{real_end}]"
            self.canvas.create_text(
                block_x + block_width // 2,
                block_y + header_height // 2,
                text=header_text,
                fill="#000000",
                font=("MS Sans Serif", 9, "bold"),
            )

            # Celdas del bloque (registros)
            cell_y = block_y + header_height + 4
            for offset in range(block_size):
                idx = start_index + offset

                # ¿Esta dirección existe en la tabla?
                if idx >= n:
                    # Celda fuera del rango real de la tabla
                    self.canvas.create_rectangle(
                        block_x,
                        cell_y,
                        block_x + block_width,
                        cell_y + cell_height,
                        fill="#f0f0f0",
                        outline="#cccccc",
                        width=1,
                        stipple="gray25",
                    )
                    self.canvas.create_text(
                        block_x + block_width // 2,
                        cell_y + cell_height // 2,
                        text="-",
                        fill="#bbbbbb",
                        font=("MS Sans Serif", 8),
                    )
                    cell_y += cell_height + 2
                    continue

                # Construir los valores almacenados en esta dirección
                if mode in ["lineal", "cuadratica", "doble_hash"]:
                    val = self._table[idx]
                    chain = [val] if val is not None else []
                elif mode == "arreglo_anidado":
                    primary = self._table[idx]
                    extras = self._table_anidado[idx] if idx < len(self._table_anidado) else []
                    chain = []
                    if primary is not None:
                        chain.append(primary)
                    chain.extend(extras)
                else:  # lista_enlazada
                    chain = self._table_enlazada[idx] if idx < len(self._table_enlazada) else []

                is_highlight = (idx == self._highlight_slot)
                cell_color = "#ff6666" if is_highlight else "#ffffff"
                text_color = "#ffffff" if is_highlight else "#000000"

                # Dibujar celda (registro dentro del bloque)
                self.canvas.create_rectangle(
                    block_x,
                    cell_y,
                    block_x + block_width,
                    cell_y + cell_height,
                    fill=cell_color,
                    outline="#808080",
                    width=1,
                )

                # Texto de la celda
                if not chain:
                    text = "-"
                    text_color = "#888888" if not is_highlight else "#ffffff"
                else:
                    if len(chain) == 1:
                        text = str(chain[0]).zfill(d)
                    else:
                        # Mostrar todos los valores de la cadena separados por coma
                        text = ", ".join(str(v).zfill(d) for v in chain)

                self.canvas.create_text(
                    block_x + block_width // 2,
                    cell_y + cell_height // 2,
                    text=text,
                    fill=text_color,
                    font=("MS Sans Serif", 8),
                )

                cell_y += cell_height + 2

            max_bottom = max(max_bottom, cell_y)

        # Info general de la estructura al final del canvas
        info = (
            f"n={n}, bloques={block_count}, regs/bloque={block_size}, "
            f"hash={self.hash_mode.get()}, colisión={self.probe_mode.get()}"
        )
        self.canvas.create_text(
            width // 2,
            max_bottom + 10,
            text=info,
            fill="#666666",
            font=("MS Sans Serif", 9),
        )

        self.canvas.configure(scrollregion=(0, 0, width, max(height, max_bottom + 40)))


    # ------------------ Guardar / cargar ------------------

    def _serialize(self) -> str:
        n, d = self._read_params()
        mode = self.probe_mode.get()
        base = self._read_base()

        lines = [
            f"n:{n}",
            f"d:{d}",
            f"hash:{self.hash_mode.get()}",
            f"probe:{mode}",
            f"base:{base}",
        ]

        if mode in ["lineal", "cuadratica", "doble_hash"]:
            vals = ["" if v is None else str(v) for v in self._table[:n]]
            lines.append(f"table:{','.join(vals)}")
        elif mode == "arreglo_anidado":
            vals = ["" if v is None else str(v) for v in self._table[:n]]
            lines.append(f"table:{','.join(vals)}")
            for i, arr in enumerate(self._table_anidado[:n]):
                if arr:
                    lines.append(f"anidado_{i}:{','.join(str(x) for x in arr)}")
        else:  # lista_enlazada
            for i, cadena in enumerate(self._table_enlazada[:n]):
                if cadena:
                    lines.append(f"lista_{i}:{','.join(str(x) for x in cadena)}")

        return "\n".join(lines) + "\n"

    def _parse(self, content: str):
        lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
        n = d = base = None
        hash_mode = "modulo"
        probe_mode = "lineal"
        table = []
        anidados: Dict[int, List[int]] = {}
        listas: Dict[int, List[int]] = {}

        for ln in lines:
            if ln.lower().startswith("n:"):
                n = int(ln.split(":", 1)[1])
            elif ln.lower().startswith("d:"):
                d = int(ln.split(":", 1)[1])
            elif ln.lower().startswith("hash:"):
                hash_mode = ln.split(":", 1)[1].strip()
            elif ln.lower().startswith("probe:"):
                probe_mode = ln.split(":", 1)[1].strip()
            elif ln.lower().startswith("base:"):
                base = int(ln.split(":", 1)[1])
            elif ln.lower().startswith("table:"):
                parts = ln.split(":", 1)[1].split(",")
                table = [int(p) if p.strip() else None for p in parts]
            elif ln.lower().startswith("anidado_"):
                idx = int(ln.split("_")[1].split(":")[0])
                vals = [int(x) for x in ln.split(":", 1)[1].split(",") if x.strip()]
                anidados[idx] = vals
            elif ln.lower().startswith("lista_"):
                idx = int(ln.split("_")[1].split(":")[0])
                vals = [int(x) for x in ln.split(":", 1)[1].split(",") if x.strip()]
                listas[idx] = vals

        if n is None or d is None:
            return None
        return n, d, hash_mode, probe_mode, base, table, anidados, listas

    def _on_save(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Guardar tabla de transformación",
            defaultextension=".txt",
            filetypes=[("Texto", "*.txt")],
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self._serialize())
            messagebox.showinfo("Éxito", "Tabla guardada correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")

    def _on_save_and_close(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Guardar tabla de transformación",
            defaultextension=".txt",
            filetypes=[("Texto", "*.txt")],
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self._serialize())
            messagebox.showinfo("Éxito", "Tabla guardada correctamente")
            self.app.navigate("internas")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")

    def _on_load(self) -> None:
        path = filedialog.askopenfilename(
            title="Cargar tabla de transformación",
            filetypes=[("Texto", "*.txt")],
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer: {e}")
            return

        parsed = self._parse(content)
        if not parsed:
            messagebox.showerror("Error", "Formato inválido")
            return

        n, d, hash_mode, probe_mode, base, table, anidados, listas = parsed

        self.entry_n.delete(0, tk.END)
        self.entry_n.insert(0, str(n))
        self.entry_digits.delete(0, tk.END)
        self.entry_digits.insert(0, str(d))
        if base is not None:
            self.entry_base.delete(0, tk.END)
            self.entry_base.insert(0, str(base))

        self.hash_mode.set(
            hash_mode if hash_mode in ("modulo", "cuadrado", "plegamiento", "truncamiento", "conversion_bases") else "modulo"
        )
        self.probe_mode.set(
            probe_mode if probe_mode in ("lineal", "cuadratica", "doble_hash", "arreglo_anidado", "lista_enlazada") else "lineal"
        )

        # re-inicializar estructuras según modo
        if probe_mode in ["lineal", "cuadratica", "doble_hash"]:
            self._table = table + [None] * (n - len(table))
            self._table_anidado = []
            self._table_enlazada = []
        elif probe_mode == "arreglo_anidado":
            self._table = table + [None] * (n - len(table))
            self._table_anidado = [anidados.get(i, []) for i in range(n)]
            self._table_enlazada = []
        else:  # lista_enlazada
            self._table = []
            self._table_anidado = []
            self._table_enlazada = [listas.get(i, []) for i in range(n)]

        self._highlight_slot = None
        self._highlight_pos = None
        self.status.configure(text=f"Tabla cargada (n={n}, d={d})")
        self._draw()
