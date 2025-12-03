import math
import random
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Optional, Dict


class TransformacionClavesView(ttk.Frame):
    def __init__(self, parent: tk.Misc, app) -> None:
        super().__init__(parent)

        self.app = app


        title = ttk.Label(self, text="Transformación de claves (por bloques)", style="Title.TLabel")
        title.pack(pady=(20, 5))

        # Parámetros
        params = ttk.Frame(self, style="Panel.TFrame", padding=10)
        params.pack(fill=tk.X, padx=4, pady=6)

        # Fila 0
        ttk.Label(params, text="Tamaño tabla (n):").grid(row=0, column=0, sticky="w", padx=(0, 6))
        self.entry_n = ttk.Entry(params, width=8)
        self.entry_n.insert(0, "16")
        self.entry_n.grid(row=0, column=1, padx=(0, 12))

        ttk.Label(params, text="Dígitos clave:").grid(row=0, column=2, sticky="w", padx=(0, 6))
        self.entry_digits = ttk.Entry(params, width=6)
        self.entry_digits.insert(0, "4")
        self.entry_digits.grid(row=0, column=3, padx=(0, 12))

        ttk.Label(params, text="Función hash:").grid(row=0, column=4, sticky="w", padx=(0, 6))
        self.hash_mode = tk.StringVar(value="modulo")
        combo_hash = ttk.Combobox(
            params,
            values=["modulo", "cuadrado", "plegamiento", "truncamiento", "conversion_bases"],
            state="readonly",
            textvariable=self.hash_mode,
            width=18,
        )
        combo_hash.grid(row=0, column=5, padx=(0, 12))

        ttk.Label(params, text="Base (conv.):").grid(row=0, column=6, sticky="w", padx=(0, 6))
        self.entry_base = ttk.Entry(params, width=6)
        self.entry_base.insert(0, "7")
        self.entry_base.grid(row=0, column=7, padx=(0, 12))

        # Fila 1
        ttk.Label(params, text="Resolución colisión:").grid(
            row=1, column=0, sticky="w", padx=(0, 6), pady=(6, 0)
        )
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

        btn_generate = ttk.Button(params, text="Generar datos", command=self._on_generate)
        btn_generate.grid(row=1, column=4, columnspan=2, pady=(6, 0), sticky="w")

        btn_create_struct = ttk.Button(params, text="Crear estructura", command=self._on_create_structure)
        btn_create_struct.grid(row=1, column=6, padx=(6, 0), pady=(6, 0), sticky="w")

        # Panel principal (izquierda: operaciones, derecha: canvas)
        panel = ttk.Frame(self, padding=6)
        panel.pack(fill=tk.BOTH, expand=True)

        # Operaciones
        ops = ttk.Frame(panel, style="Panel.TFrame", padding=10)
        ops.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))

        ttk.Label(ops, text="Clave:").grid(row=0, column=0, sticky="w")
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

        self.status = ttk.Label(ops, text="Estado: listo", wraplength=140, justify="left")
        self.status.grid(row=6, column=0, pady=(12, 0), sticky="w")

        # Visualización (canvas)
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

        # --------- Estado interno ---------
        self.n: int = 0                # total de direcciones / registros
        self.b: int = 0                # número de bloques
        self.block_size: int = 0       # registros por bloque

        self.structure_created: bool = False  # hasta que se pulse "Crear estructura"

        self._table: List[Optional[int]] = []       # tabla principal (para OA y arreglo_anidado)
        self._table_anidado: List[List[int]] = []   # colisiones por dirección (arreglo anidado)
        self._table_enlazada: List[List[int]] = []  # colisiones por lista enlazada

        self._highlight_index: Optional[int] = None  # índice de dirección que se resalta

    # ------------------------------------------------------------------
    # Lectura de parámetros y creación de bloques
    # ------------------------------------------------------------------

    def _read_params(self) -> tuple[int, int]:
        """Lee n y d, y calcula número de bloques y tamaño de bloque."""
        try:
            n = int(self.entry_n.get())
        except Exception:
            n = 16
        try:
            d = int(self.entry_digits.get())
        except Exception:
            d = 4

        n = max(1, n)
        d = max(1, d)

        self.n = n
        self.b = math.ceil(math.sqrt(n))
        self.block_size = math.ceil(n / self.b) if self.b > 0 else n

        return n, d

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

    # ------------------------------------------------------------------
    # Funciones hash: valor conceptual (puede ser > n)
    # ------------------------------------------------------------------

    def _hash_value(self, k: int, n: int, d: int) -> int:
        """
        Devuelve el valor hash "conceptual" según el método elegido.
        Este valor puede exceder n; para indexar en la tabla se reduce con módulo.
        """
        mode = self.hash_mode.get()

        if mode == "modulo":
            # Clásico: k mod n, luego +1 (desplazamiento)
            base = k % n
            return base + 1

        elif mode == "cuadrado":
            # Método del cuadrado central
            k2 = k * k
            k2_str = str(k2).zfill(2 * d)
            center_len = d
            start = max(0, (len(k2_str) - center_len) // 2)
            center_str = k2_str[start:start + center_len]
            center = int(center_str) if center_str else 0
            base = center % n
            return base + 1

        elif mode == "plegamiento":
            # Plegamiento: sumar parejas de 2 dígitos (último dígito suelto si sobra) + 1
            k_str = str(k)
            grupos: List[int] = []
            i = 0
            while i < len(k_str):
                if i + 2 <= len(k_str):
                    grupos.append(int(k_str[i:i + 2]))
                    i += 2
                else:
                    grupos.append(int(k_str[i:]))
                    i += 1
            direccion = sum(grupos)
            return direccion + 1  # sin % interno, como pediste

        elif mode == "truncamiento":
            # Truncamiento: usar dígitos 1 y 3 (posición 0 y 2) + 1
            k_str = str(k).zfill(d)
            d1 = k_str[0] if len(k_str) > 0 else "0"
            d3 = k_str[2] if len(k_str) > 2 else "0"
            direccion = int(d1 + d3)
            return direccion + 1

        elif mode == "conversion_bases":
            # Conversión de bases: suma de dígitos en base 'base', luego % n y +1
            base_b = self._read_base()
            valor = k
            suma = 0
            while valor > 0:
                suma += valor % base_b
                valor //= base_b
            base = suma % n
            return base + 1

        # Por defecto, módulo
        base = k % n
        return base + 1

    def _hash_index(self, k: int, n: int, d: int) -> int:
        """
        Reducción del valor hash conceptual al índice real en [0, n-1].
        """
        hv = self._hash_value(k, n, d)
        return (hv - 1) % n

    # ------------------------------------------------------------------
    # Métodos de resolución (sondas)
    # ------------------------------------------------------------------

    def _double_hash_step(self, k: int, n: int) -> int:
        """Segundo hash para doble hashing: paso entre posiciones."""
        if n <= 1:
            return 1
        return 1 + (k % (n - 1))

    def _probe_indices(self, k: int, n: int, d: int):
        """Genera índices según el método de resolución elegido."""
        mode = self.probe_mode.get()
        base = self._hash_index(k, n, d)

        if mode == "lineal":
            # D, D+1, D+2, ...
            for t in range(n):
                yield (base + t) % n

        elif mode == "cuadratica":
            # D, D+1², D+2², ...
            for t in range(n):
                yield (base + t * t) % n

        elif mode == "doble_hash":
            step = self._double_hash_step(k, n)
            current = base
            for _ in range(n):
                yield current
                current = (current + step) % n

    # ------------------------------------------------------------------
    # Validación de clave
    # ------------------------------------------------------------------

    def _validate_key(self, s: str, d: int) -> Optional[int]:
        if not s.isdigit():
            messagebox.showerror("Error", "La clave debe ser numérica.")
            return None
        if len(s) != d:
            messagebox.showerror("Error", f"La clave debe tener exactamente {d} dígitos.")
            return None
        return int(s)

    # ------------------------------------------------------------------
    # Inicialización / creación de estructura
    # ------------------------------------------------------------------

    def _on_probe_change(self, event=None) -> None:
        # Si ya existe estructura, reinicializar con el nuevo método
        if self.structure_created:
            self._on_init()

    def _on_create_structure(self) -> None:
        """Crea/reinicia la estructura de bloques a partir de n."""
        self._read_params()
        self.structure_created = True
        self._on_init()
        self.status.configure(
            text=f"Estructura creada: n={self.n}, bloques={self.b}, registros por bloque={self.block_size}"
        )

    def _on_init(self) -> None:
        """Reinicia las estructuras internas según el método de colisión."""
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

        self._highlight_index = None

        if self.structure_created:
            self.status.configure(
                text=f"Tabla reiniciada: n={self.n}, bloques={self.b}, registros por bloque={self.block_size}"
            )
        else:
            self.status.configure(text="Estado: listo (estructura aún no creada)")

        self._draw()

    # ------------------------------------------------------------------
    # Generación aleatoria
    # ------------------------------------------------------------------

    def _on_generate(self) -> None:
        if not self.structure_created:
            messagebox.showerror("Error", "Primero cree la estructura con el botón 'Crear estructura'.")
            return

        n, d = self._read_params()
        self._on_init()

        max_value = 10**d - 1
        min_value = 10 ** (d - 1) if d > 1 else 0

        target = max(1, n // 2)  # llenar aprox. mitad de la tabla
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

        self.status.configure(text=f"Generados {inserted} elementos aleatorios")
        self._draw()

    # ------------------------------------------------------------------
    # Inserción / búsqueda / borrado
    # ------------------------------------------------------------------

    def _insert_key(self, k: int, n: int, d: int, animate: bool = True) -> bool:
        """Inserta una clave según el método de resolución."""
        mode = self.probe_mode.get()
        base = self._hash_index(k, n, d)

        if mode in ["lineal", "cuadratica", "doble_hash"]:
            # Verificar duplicado
            for idx in self._probe_indices(k, n, d):
                if self._table[idx] is None:
                    break
                if self._table[idx] == k:
                    return False

            # Insertar
            for idx in self._probe_indices(k, n, d):
                if animate:
                    self._highlight_index = idx
                    self._draw()
                    self.update_idletasks()
                    self.after(200)
                if self._table[idx] is None:
                    self._table[idx] = k
                    return True
            return False  # tabla llena

        elif mode == "arreglo_anidado":
            # Verificar duplicado en posición base y en colisiones
            if self._table[base] == k:
                return False
            if base < len(self._table_anidado) and k in self._table_anidado[base]:
                return False

            if animate:
                self._highlight_index = base
                self._draw()
                self.update_idletasks()
                self.after(200)

            # Primer valor va a la tabla principal; colisiones al arreglo anidado
            if self._table[base] is None:
                self._table[base] = k
            else:
                self._table_anidado[base].append(k)
            return True

        else:  # lista_enlazada
            if k in self._table_enlazada[base]:
                return False

            if animate:
                self._highlight_index = base
                self._draw()
                self.update_idletasks()
                self.after(200)

            self._table_enlazada[base].append(k)
            return True

    def _ensure_structure(self) -> bool:
        if not self.structure_created:
            messagebox.showerror("Error", "Primero cree la estructura con el botón 'Crear estructura'.")
            return False
        return True

    def _on_insert(self) -> None:
        if not self._ensure_structure():
            return

        n, d = self._read_params()
        key_str = self.entry_key.get().strip()
        k = self._validate_key(key_str, d)
        if k is None:
            return

        mode = self.probe_mode.get()
        if mode in ["lineal", "cuadratica", "doble_hash"]:
            if sum(1 for v in self._table if v is not None) >= n:
                messagebox.showerror("Error", "Tabla llena")
                return

        if self._insert_key(k, n, d, animate=True):
            hv = self._hash_value(k, n, d)
            self.status.configure(text=f"Insertado {k} (hash={hv})")
            self.entry_key.delete(0, tk.END)
            self._highlight_index = None
            self._draw()
        else:
            messagebox.showerror("Error", "No se pudo insertar (duplicado o tabla llena)")

    def _on_search(self) -> None:
        if not self._ensure_structure():
            return

        n, d = self._read_params()
        key_str = self.entry_key.get().strip()
        k = self._validate_key(key_str, d)
        if k is None:
            return

        mode = self.probe_mode.get()
        base = self._hash_index(k, n, d)

        if mode in ["lineal", "cuadratica", "doble_hash"]:
            for idx in self._probe_indices(k, n, d):
                if self._table[idx] is None:
                    break
                self._highlight_index = idx
                self._draw()
                self.update_idletasks()
                self.after(400)
                if self._table[idx] == k:
                    self.status.configure(text=f"Encontrado {k} en dirección {idx}")
                    return

        elif mode == "arreglo_anidado":
            self._highlight_index = base
            self._draw()
            self.update_idletasks()
            self.after(400)

            if self._table[base] == k:
                self.status.configure(text=f"Encontrado {k} en dirección {base} (principal)")
                return

            if k in self._table_anidado[base]:
                pos = self._table_anidado[base].index(k)
                self.status.configure(
                    text=f"Encontrado {k} en dirección {base}, colisión #{pos + 1} (arreglo anidado)"
                )
                return

        else:  # lista_enlazada
            self._highlight_index = base
            self._draw()
            self.update_idletasks()
            self.after(400)

            if k in self._table_enlazada[base]:
                pos = self._table_enlazada[base].index(k)
                self.status.configure(text=f"Encontrado {k} en dirección {base}, nodo {pos}")
                return

        self._highlight_index = None
        self._draw()
        self.status.configure(text="No encontrado")
        messagebox.showinfo("Búsqueda", "Valor no encontrado")

    def _on_delete(self) -> None:
        if not self._ensure_structure():
            return

        n, d = self._read_params()
        key_str = self.entry_key.get().strip()
        k = self._validate_key(key_str, d)
        if k is None:
            return

        mode = self.probe_mode.get()
        base = self._hash_index(k, n, d)

        if mode in ["lineal", "cuadratica", "doble_hash"]:
            for idx in self._probe_indices(k, n, d):
                if self._table[idx] is None:
                    break
                self._highlight_index = idx
                self._draw()
                self.update_idletasks()
                self.after(400)
                if self._table[idx] == k:
                    self._table[idx] = None
                    self._highlight_index = None
                    self.status.configure(text=f"Eliminado {k}")
                    self._draw()
                    return

        elif mode == "arreglo_anidado":
            self._highlight_index = base
            self._draw()
            self.update_idletasks()
            self.after(400)

            # 1️⃣ Si la clave está en la tabla principal
            if self._table[base] == k:
                # Si hay colisiones, el primer elemento del arreglo anidado
                # sube a la tabla principal
                if self._table_anidado[base]:
                    self._table[base] = self._table_anidado[base].pop(0)
                else:
                    self._table[base] = None

                self._highlight_index = None
                self.status.configure(text=f"Eliminado {k} (principal)")
                self._draw()
                return

            # 2️⃣ Si está en la estructura de colisiones
            if k in self._table_anidado[base]:
                self._table_anidado[base].remove(k)
                self._highlight_index = None
                self.status.configure(text=f"Eliminado {k} (arreglo anidado)")
                self._draw()
                return

        else:  # lista_enlazada
            self._highlight_index = base
            self._draw()
            self.update_idletasks()
            self.after(400)

            if k in self._table_enlazada[base]:
                self._table_enlazada[base].remove(k)
                self._highlight_index = None
                self.status.configure(text=f"Eliminado {k}")
                self._draw()
                return

        self._highlight_index = None
        self._draw()
        self.status.configure(text="No encontrado")
        messagebox.showinfo("Borrado", "Valor no encontrado")

    # ------------------------------------------------------------------
    # Dibujo de bloques en el canvas (horizontal)
    # ------------------------------------------------------------------

    def _draw(self) -> None:
        self.canvas.delete("all")

        # Si la estructura no existe aún, dejar el canvas vacío
        if not self.structure_created:
            return

        n, d = self._read_params()
        mode = self.probe_mode.get()

        # Asegurar tamaños de estructuras
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

        block_count = self.b
        block_size = self.block_size

        if block_count <= 0 or block_size <= 0:
            return

        margin_x = 20
        gap_x = 12
        total_gap = gap_x * max(0, block_count - 1)
        block_width = (width - 2 * margin_x - total_gap) / max(1, block_count)
        block_width = max(140, min(240, block_width))

        header_height = 32
        cell_height = 24
        band_gap_y = 30
        start_y = 40

        # -------------------------------------------------
        # CASO ESPECIAL: ARREGLO ANIDADO → DOS BANDAS
        #   1) Banda superior: tabla principal (_table)
        #   2) Banda inferior: colisiones (_table_anidado)
        # -------------------------------------------------
        if mode == "arreglo_anidado":
            # --- Banda superior: tabla principal ---
            max_bottom_top = start_y
            for block_idx in range(block_count):
                block_x = margin_x + block_idx * (block_width + gap_x)
                block_y = start_y

                start_index = block_idx * block_size
                if start_index >= n:
                    continue
                end_index = start_index + block_size - 1
                real_end = min(end_index, n - 1)

                highlight_block = (
                    self._highlight_index is not None
                    and start_index <= self._highlight_index <= real_end
                )

                header_fill = "#4da3ff" if highlight_block else "#e0e0e0"
                header_outline = "#255eaa" if highlight_block else "#808080"

                self.canvas.create_rectangle(
                    block_x,
                    block_y,
                    block_x + block_width,
                    block_y + header_height,
                    fill=header_fill,
                    outline=header_outline,
                    width=2,
                )

                header_text = f"Bloque {block_idx + 1} (tabla)\n[{start_index}..{real_end}]"
                self.canvas.create_text(
                    block_x + block_width / 2,
                    block_y + header_height / 2,
                    text=header_text,
                    fill="#000000",
                    font=("MS Sans Serif", 9, "bold"),
                )

                cell_y = block_y + header_height + 4
                for offset in range(block_size):
                    idx = start_index + offset

                    if idx >= n:
                        # Celda fuera de rango real
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
                            block_x + block_width / 2,
                            cell_y + cell_height / 2,
                            text="-",
                            fill="#bbbbbb",
                            font=("MS Sans Serif", 8),
                        )
                        cell_y += cell_height + 2
                        continue

                    val = self._table[idx]
                    is_highlight_cell = (self._highlight_index == idx)
                    cell_fill = "#ff6666" if is_highlight_cell else "#ffffff"
                    text_color = "#ffffff" if is_highlight_cell else "#000000"

                    self.canvas.create_rectangle(
                        block_x,
                        cell_y,
                        block_x + block_width,
                        cell_y + cell_height,
                        fill=cell_fill,
                        outline="#808080",
                        width=1,
                    )

                    if val is None:
                        text = "-"
                        text_color = "#888888" if not is_highlight_cell else "#ffffff"
                    else:
                        text = str(val).zfill(d)

                    self.canvas.create_text(
                        block_x + block_width / 2,
                        cell_y + cell_height / 2,
                        text=text,
                        fill=text_color,
                        font=("MS Sans Serif", 8),
                    )

                    cell_y += cell_height + 2

                max_bottom_top = max(max_bottom_top, cell_y)

            # --- Banda inferior: estructura de colisiones (arreglo anidado) ---
            start_y_bottom = max_bottom_top + band_gap_y
            max_bottom = start_y_bottom

            for block_idx in range(block_count):
                block_x = margin_x + block_idx * (block_width + gap_x)
                block_y = start_y_bottom

                start_index = block_idx * block_size
                if start_index >= n:
                    continue
                end_index = start_index + block_size - 1
                real_end = min(end_index, n - 1)

                highlight_block = (
                    self._highlight_index is not None
                    and start_index <= self._highlight_index <= real_end
                )

                header_fill = "#ffcc66" if highlight_block else "#f0e0c0"
                header_outline = "#c09030" if highlight_block else "#a08040"

                self.canvas.create_rectangle(
                    block_x,
                    block_y,
                    block_x + block_width,
                    block_y + header_height,
                    fill=header_fill,
                    outline=header_outline,
                    width=2,
                )

                header_text = f"Colisiones bloque {block_idx + 1}\n[{start_index}..{real_end}]"
                self.canvas.create_text(
                    block_x + block_width / 2,
                    block_y + header_height / 2,
                    text=header_text,
                    fill="#000000",
                    font=("MS Sans Serif", 9, "bold"),
                )

                cell_y = block_y + header_height + 4
                for offset in range(block_size):
                    idx = start_index + offset

                    if idx >= n:
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
                            block_x + block_width / 2,
                            cell_y + cell_height / 2,
                            text="-",
                            fill="#bbbbbb",
                            font=("MS Sans Serif", 8),
                        )
                        cell_y += cell_height + 2
                        continue

                    chain = self._table_anidado[idx]
                    is_highlight_cell = (self._highlight_index == idx)
                    cell_fill = "#ff9966" if is_highlight_cell else "#ffffff"
                    text_color = "#ffffff" if is_highlight_cell else "#000000"

                    self.canvas.create_rectangle(
                        block_x,
                        cell_y,
                        block_x + block_width,
                        cell_y + cell_height,
                        fill=cell_fill,
                        outline="#808080",
                        width=1,
                    )

                    if not chain:
                        text = "-"
                        text_color = "#888888" if not is_highlight_cell else "#ffffff"
                    else:
                        text = ", ".join(str(v).zfill(d) for v in chain)

                    self.canvas.create_text(
                        block_x + block_width / 2,
                        cell_y + cell_height / 2,
                        text=text,
                        fill=text_color,
                        font=("MS Sans Serif", 8),
                    )

                    cell_y += cell_height + 2

                max_bottom = max(max_bottom, cell_y)

            info = (
                f"n={self.n}, bloques={self.b}, regs/bloque={self.block_size}, "
                f"hash={self.hash_mode.get()}, colisión={self.probe_mode.get()}"
            )
            self.canvas.create_text(
                width / 2,
                max_bottom + 10,
                text=info,
                fill="#666666",
                font=("MS Sans Serif", 9),
            )

            self.canvas.configure(scrollregion=(0, 0, width, max(height, max_bottom + 40)))
            return

        # -------------------------------------------------
        # RESTO DE MODOS (lineal, cuadrática, doble hash,
        # lista enlazada): UNA SOLA BANDA
        # -------------------------------------------------
        max_bottom = start_y

        for block_idx in range(block_count):
            block_x = margin_x + block_idx * (block_width + gap_x)
            block_y = start_y

            start_index = block_idx * block_size
            if start_index >= n:
                continue
            end_index = start_index + block_size - 1
            real_end = min(end_index, n - 1)

            highlight_block = (
                self._highlight_index is not None
                and start_index <= self._highlight_index <= real_end
            )

            header_fill = "#4da3ff" if highlight_block else "#e0e0e0"
            header_outline = "#255eaa" if highlight_block else "#808080"

            self.canvas.create_rectangle(
                block_x,
                block_y,
                block_x + block_width,
                block_y + header_height,
                fill=header_fill,
                outline=header_outline,
                width=2,
            )

            header_text = f"Bloque {block_idx + 1}\n[{start_index}..{real_end}]"
            self.canvas.create_text(
                block_x + block_width / 2,
                block_y + header_height / 2,
                text=header_text,
                fill="#000000",
                font=("MS Sans Serif", 9, "bold"),
            )

            cell_y = block_y + header_height + 4

            for offset in range(block_size):
                idx = start_index + offset

                if idx >= n:
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
                        block_x + block_width / 2,
                        cell_y + cell_height / 2,
                        text="-",
                        fill="#bbbbbb",
                        font=("MS Sans Serif", 8),
                    )
                    cell_y += cell_height + 2
                    continue

                if mode in ["lineal", "cuadratica", "doble_hash"]:
                    val = self._table[idx]
                    chain = [val] if val is not None else []
                else:  # lista_enlazada
                    chain = list(self._table_enlazada[idx])

                is_highlight_cell = (self._highlight_index == idx)
                cell_fill = "#ff6666" if is_highlight_cell else "#ffffff"
                text_color = "#ffffff" if is_highlight_cell else "#000000"

                self.canvas.create_rectangle(
                    block_x,
                    cell_y,
                    block_x + block_width,
                    cell_y + cell_height,
                    fill=cell_fill,
                    outline="#808080",
                    width=1,
                )

                if not chain:
                    text = "-"
                    text_color = "#888888" if not is_highlight_cell else "#ffffff"
                else:
                    if len(chain) == 1:
                        text = str(chain[0]).zfill(d)
                    else:
                        text = ", ".join(str(v).zfill(d) for v in chain)

                self.canvas.create_text(
                    block_x + block_width / 2,
                    cell_y + cell_height / 2,
                    text=text,
                    fill=text_color,
                    font=("MS Sans Serif", 8),
                )

                cell_y += cell_height + 2

            max_bottom = max(max_bottom, cell_y)

        info = (
            f"n={self.n}, bloques={self.b}, regs/bloque={self.block_size}, "
            f"hash={self.hash_mode.get()}, colisión={self.probe_mode.get()}"
        )
        self.canvas.create_text(
            width / 2,
            max_bottom + 10,
            text=info,
            fill="#666666",
            font=("MS Sans Serif", 9),
        )

        self.canvas.configure(scrollregion=(0, 0, width, max(height, max_bottom + 40)))


    # ------------------------------------------------------------------
    # Guardar / cargar
    # ------------------------------------------------------------------

    def _serialize(self) -> str:
        n, d = self._read_params()
        mode = self.probe_mode.get()
        base_b = self._read_base()

        lines = [
            f"n:{n}",
            f"d:{d}",
            f"hash:{self.hash_mode.get()}",
            f"probe:{mode}",
            f"base:{base_b}",
        ]

        if mode in ["lineal", "cuadratica", "doble_hash"]:
            vals = ["" if v is None else str(v) for v in self._table[:n]]
            lines.append("table:" + ",".join(vals))
        elif mode == "arreglo_anidado":
            vals = ["" if v is None else str(v) for v in self._table[:n]]
            lines.append("table:" + ",".join(vals))
            for i, arr in enumerate(self._table_anidado[:n]):
                if arr:
                    lines.append(f"anidado_{i}:" + ",".join(str(x) for x in arr))
        else:  # lista_enlazada
            for i, cadena in enumerate(self._table_enlazada[:n]):
                if cadena:
                    lines.append(f"lista_{i}:" + ",".join(str(x) for x in cadena))

        return "\n".join(lines) + "\n"

    def _parse(self, content: str):
        lines = [ln.strip() for ln in content.splitlines() if ln.strip()]

        n = d = base_b = None
        hash_mode = "modulo"
        probe_mode = "lineal"
        table: List[Optional[int]] = []
        anidados: Dict[int, List[int]] = {}
        listas: Dict[int, List[int]] = {}

        for ln in lines:
            lower = ln.lower()
            if lower.startswith("n:"):
                n = int(ln.split(":", 1)[1])
            elif lower.startswith("d:"):
                d = int(ln.split(":", 1)[1])
            elif lower.startswith("hash:"):
                hash_mode = ln.split(":", 1)[1].strip()
            elif lower.startswith("probe:"):
                probe_mode = ln.split(":", 1)[1].strip()
            elif lower.startswith("base:"):
                base_b = int(ln.split(":", 1)[1])
            elif lower.startswith("table:"):
                parts = ln.split(":", 1)[1].split(",")
                table = [int(p) if p.strip() else None for p in parts]
            elif lower.startswith("anidado_"):
                idx = int(ln.split("_")[1].split(":")[0])
                vals = [int(x) for x in ln.split(":", 1)[1].split(",") if x.strip()]
                anidados[idx] = vals
            elif lower.startswith("lista_"):
                idx = int(ln.split("_")[1].split(":")[0])
                vals = [int(x) for x in ln.split(":", 1)[1].split(",") if x.strip()]
                listas[idx] = vals

        if n is None or d is None:
            return None
        return n, d, hash_mode, probe_mode, base_b, table, anidados, listas

    def _on_save(self) -> None:
        if not self.structure_created:
            messagebox.showerror("Error", "No hay estructura para guardar.")
            return

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
        if not self.structure_created:
            messagebox.showerror("Error", "No hay estructura para guardar.")
            return

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
            self.app.navigate("externas")
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

        n, d, hash_mode, probe_mode, base_b, table, anidados, listas = parsed

        # Restaurar parámetros en UI
        self.entry_n.delete(0, tk.END)
        self.entry_n.insert(0, str(n))

        self.entry_digits.delete(0, tk.END)
        self.entry_digits.insert(0, str(d))

        if base_b is not None:
            self.entry_base.delete(0, tk.END)
            self.entry_base.insert(0, str(base_b))

        self.hash_mode.set(
            hash_mode
            if hash_mode in ("modulo", "cuadrado", "plegamiento", "truncamiento", "conversion_bases")
            else "modulo"
        )
        self.probe_mode.set(
            probe_mode
            if probe_mode in ("lineal", "cuadratica", "doble_hash", "arreglo_anidado", "lista_enlazada")
            else "lineal"
        )

        # Recalcular n, bloques, block_size
        self._read_params()
        mode = self.probe_mode.get()

        if mode in ["lineal", "cuadratica", "doble_hash"]:
            self._table = table + [None] * (self.n - len(table))
            self._table_anidado = []
            self._table_enlazada = []
        elif mode == "arreglo_anidado":
            self._table = table + [None] * (self.n - len(table))
            self._table_anidado = [anidados.get(i, []) for i in range(self.n)]
            self._table_enlazada = []
        else:  # lista_enlazada
            self._table = []
            self._table_anidado = []
            self._table_enlazada = [listas.get(i, []) for i in range(self.n)]

        self.structure_created = True
        self._highlight_index = None
        self.status.configure(
            text=f"Tabla cargada: n={self.n}, bloques={self.b}, registros por bloque={self.block_size}"
        )
        self._draw()
