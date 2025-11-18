import math
import tkinter as tk
from tkinter import ttk, messagebox


class IndicesView(ttk.Frame):
    def __init__(self, parent: tk.Misc, app) -> None:  # app: RetroApp
        super().__init__(parent)

        title = ttk.Label(self, text="Búsquedas por Índices", style="Title.TLabel")
        title.pack(pady=(20, 5))

        # Panel paralelo
        panel = ttk.Frame(self, padding=6)
        panel.pack(fill=tk.BOTH, expand=True)

        # ---------------------------------------------------------------------
        # Panel izquierdo: parámetros y resultados
        # ---------------------------------------------------------------------
        ops = ttk.Frame(panel, style="Panel.TFrame", padding=10)
        ops.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))

        row = 0
        lbl_params = ttk.Label(ops, text="Parámetros del fichero de datos", style="Subtitle.TLabel")
        lbl_params.grid(row=row, column=0, columnspan=2, sticky="w", pady=(0, 6))

        # r = número de registros
        row += 1
        ttk.Label(ops, text="r (nº registros):").grid(row=row, column=0, sticky="w", pady=2)
        self.entry_r = ttk.Entry(ops, width=10)
        self.entry_r.grid(row=row, column=1, sticky="w", pady=2)

        # B = número de bytes del bloque
        row += 1
        ttk.Label(ops, text="B (bytes por bloque):").grid(row=row, column=0, sticky="w", pady=2)
        self.entry_B = ttk.Entry(ops, width=10)
        self.entry_B.grid(row=row, column=1, sticky="w", pady=2)

        # R = tamaño fijo del registro
        row += 1
        ttk.Label(ops, text="R (tamaño registro):").grid(row=row, column=0, sticky="w", pady=2)
        self.entry_R = ttk.Entry(ops, width=10)
        self.entry_R.grid(row=row, column=1, sticky="w", pady=2)

        # Tipo de índice: primario / secundario
        row += 1
        ttk.Label(ops, text="Tipo de índice:").grid(row=row, column=0, sticky="w", pady=(8, 2))
        self.index_type = tk.StringVar(value="primary")
        rb_primary = ttk.Radiobutton(ops, text="Primario (no denso)", value="primary", variable=self.index_type)
        rb_secondary = ttk.Radiobutton(ops, text="Secundario (denso)", value="secondary", variable=self.index_type)
        rb_primary.grid(row=row, column=1, sticky="w", pady=(8, 0))
        row += 1
        rb_secondary.grid(row=row, column=1, sticky="w", pady=2)

        # Check: índice multinivel
        row += 1
        self.is_multilevel = tk.BooleanVar(value=False)
        chk_multilevel = ttk.Checkbutton(ops, text="Índice multinivel", variable=self.is_multilevel)
        chk_multilevel.grid(row=row, column=1, sticky="w", pady=(4,4), padx=(0,0))

        # Parámetros del índice (v, p)
        row += 1
        lbl_idx_params = ttk.Label(ops, text="Parámetros del índice", style="Subtitle.TLabel")
        lbl_idx_params.grid(row=row, column=0, columnspan=2, sticky="w", pady=(10, 4))

        # v = longitud campo clave de ordenación
        row += 1
        ttk.Label(ops, text="v (bytes clave):").grid(row=row, column=0, sticky="w", pady=2)
        self.entry_v = ttk.Entry(ops, width=10)
        self.entry_v.insert(0, "9")  # ejemplo por defecto
        self.entry_v.grid(row=row, column=1, sticky="w", pady=2)

        # p = longitud puntero
        row += 1
        ttk.Label(ops, text="p (bytes puntero):").grid(row=row, column=0, sticky="w", pady=2)
        self.entry_p = ttk.Entry(ops, width=10)
        self.entry_p.insert(0, "6")  # ejemplo por defecto
        self.entry_p.grid(row=row, column=1, sticky="w", pady=2)

        # Botón de cálculo
        row += 1
        btn_calc = ttk.Button(ops, text="Calcular", command=self._on_calculate)
        btn_calc.grid(row=row, column=0, columnspan=2, pady=(8, 8))

        # ---------------------------------------------------------------------
        # Resultados
        # ---------------------------------------------------------------------
        row += 1
        lbl_results = ttk.Label(ops, text="Resultados", style="Subtitle.TLabel")
        lbl_results.grid(row=row, column=0, columnspan=2, sticky="w", pady=(8, 4))

        def make_result_row(texto, var_attr_name):
            nonlocal row
            row += 1
            setattr(self, var_attr_name, tk.StringVar(value="-"))
            ttk.Label(ops, text=texto).grid(row=row, column=0, sticky="w", pady=1)
            ttk.Label(ops, textvariable=getattr(self, var_attr_name)).grid(row=row, column=1, sticky="w", pady=1)

        make_result_row("bfr (B/R):", "var_bfr")
        make_result_row("b (nº bloques datos):", "var_b")
        make_result_row("Ri (p + v):", "var_Ri")
        make_result_row("bfri (B/Ri):", "var_bfri")
        make_result_row("ri (entradas índice):", "var_ri")
        make_result_row("bi (bloques índice):", "var_bi")
        make_result_row("Niveles índice:", "var_levels")
        make_result_row("Accesos a memoria:", "var_accesses")

        # ---------------------------------------------------------------------
        # Panel derecho: visualización en el Canvas
        # ---------------------------------------------------------------------
        viz = ttk.Frame(panel, style="Panel.TFrame", padding=8)
        viz.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(viz, background="#ffffff", height=460)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.create_text(
            10, 10,
            anchor="nw",
            text="Introduce los parámetros y pulsa 'Calcular' para ver cómo se relacionan\n"
                 "las tablas de ÍNDICE (izquierda) con los BLOQUES de datos (derecha).",
            fill="#444444",
            font=("Arial", 10),
        )

        # Para guardar últimos cálculos (para la visualización)
        self._last_calc = None

        # ---------------------------------------------------------------------
        # Panel inferior: guardar / cargar
        # ---------------------------------------------------------------------
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

    # -------------------------------------------------------------------------
    # Cálculos principales (ahora con opción de multinivel)
    # -------------------------------------------------------------------------
    def _on_calculate(self) -> None:
        try:
            r = int(self.entry_r.get())
            B = float(self.entry_B.get())
            R = float(self.entry_R.get())
            v = float(self.entry_v.get())
            p = float(self.entry_p.get())
        except ValueError:
            messagebox.showerror("Error", "Verifica que todos los campos numéricos sean válidos.")
            return

        if r <= 0 or B <= 0 or R <= 0 or v <= 0 or p <= 0:
            messagebox.showerror("Error", "Todos los valores deben ser positivos.")
            return

        # bfr = Factor de bloqueo = B / R (aproximando hacia abajo)
        bfr = int(B // R)
        if bfr <= 0:
            messagebox.showerror(
                "Error",
                "El factor de bloqueo bfr = B/R es 0.\nAsegúrate de que B sea mayor que R."
            )
            return

        # b = número de bloques = r / bfr (aproximando hacia arriba)
        b = int(math.ceil(r / bfr))

        # Ri = tamaño entrada de índice = p + v
        Ri = p + v

        # bfri = factor de bloqueo índice = B / Ri (aprox. hacia abajo)
        bfri = int(B // Ri)
        if bfri <= 0:
            messagebox.showerror(
                "Error",
                "El factor de bloqueo del índice bfri = B/Ri es 0.\n"
                "Ajusta B, p o v para que al menos quepa una entrada por bloque."
            )
            return

        # ri = nº total de entradas del índice
        if self.index_type.get() == "primary":
            # Índice primario (no denso): una entrada por bloque de datos
            ri = b
        else:
            # Índice secundario (denso): una entrada por registro
            ri = r

        # bi = número de bloques de índice (primer nivel) = ri / bfri (aprox. hacia arriba)
        bi = int(math.ceil(ri / bfri)) if ri > 0 else 0

        # ¿Multinivel activado?
        multilevel_blocks = []
        if bi <= 0:
            niveles = 0
            accesos = 0
        else:
            if self.is_multilevel.get():
                # -------------------- MULTINIVEL explícito --------------------
                # f0 = bfri (entradas por bloque de índice)
                # b1 = bi  (bloques del índice de primer nivel)
                # b2 = ceil(b1 / f0), b3 = ceil(b2 / f0), ...
                current = bi
                while True:
                    multilevel_blocks.append(current)
                    if current <= 1:
                        break
                    current = math.ceil(current / bfri)

                niveles = len(multilevel_blocks)        # niveles reales (b1, b2, ..., bn)
                accesos = niveles + 1                   # niveles + 1 acceso a datos
            else:
                # -------------------- SIN multinivel (aprox. log2) ---------
                # niveles ≈ ceil(log2(bi)), accesos = niveles + 1
                levels_approx = int(math.ceil(math.log2(bi))) if bi > 1 else 1
                if levels_approx < 1:
                    levels_approx = 1
                niveles = levels_approx
                accesos = niveles + 1
                multilevel_blocks = []  # no mostramos niveles explícitos

        # Actualizamos resultados
        self.var_bfr.set(str(bfr))
        self.var_b.set(str(b))
        self.var_Ri.set(str(Ri))
        self.var_bfri.set(str(bfri))
        self.var_ri.set(str(ri))
        self.var_bi.set(str(bi))
        self.var_levels.set(str(niveles))
        self.var_accesses.set(str(accesos))

        # Guardamos parámetros y niveles para la visualización
        self._last_calc = {
            "r": r,
            "B": B,
            "R": R,
            "v": v,
            "p": p,
            "bfr": bfr,
            "b": b,
            "Ri": Ri,
            "bfri": bfri,
            "ri": ri,
            "bi": bi,
            "index_type": self.index_type.get(),
            "multilevel_blocks": multilevel_blocks,      # [b1, b2, b3, ...]
            "is_multilevel": self.is_multilevel.get(),
        }

        # Dibujar visualización
        self._draw_visualization()

    # -------------------------------------------------------------------------
    # Visualización en Canvas (índice izquierda, bloques derecha)
    # -------------------------------------------------------------------------
    def _draw_visualization(self) -> None:
        self.canvas.delete("all")

        if not self._last_calc:
            self.canvas.create_text(
                10, 10,
                anchor="nw",
                text="Introduce los parámetros y pulsa 'Calcular' para ver la visualización.",
                fill="#444444",
                font=("Arial", 10),
            )
            return

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 1 or h <= 1:
            w, h = 600, 460

        # Recuperar cálculos
        r = self._last_calc["r"]
        bfr = self._last_calc["bfr"]
        b = self._last_calc["b"]
        bfri = self._last_calc["bfri"]
        bi = self._last_calc["bi"]
        index_type = self._last_calc["index_type"]
        ri = self._last_calc["ri"]
        multilevel_blocks = self._last_calc.get("multilevel_blocks", [])
        is_multilevel = self._last_calc.get("is_multilevel", False)

        # Layout general
        margin_y = 60
        block_w = 140
        block_h = 80
        v_spacing = 18

        # Columnas:
        #   - Niveles multinivel (≥2) a la izquierda
        #   - Índice primario/secundario (nivel 1) en el centro-izquierda
        #   - Bloques de datos a la derecha
        idx_center_x = w * 0.40
        data_center_x = w * 0.78

        # ---------------------------------------------------------------------
        # 1) Generación de datos de ejemplo (respetando capacidades reales)
        # ---------------------------------------------------------------------
        max_sample_records = min(10, r, b * bfr) if bfr > 0 and b > 0 else 0
        max_sample_index_entries = min(5, ri, bi * bfri) if bfri > 0 and bi > 0 else 0

        names_pool = ["Juan", "Carlos", "Ana", "María", "Luis",
                      "Sofía", "Pedro", "Lucía", "David", "Steven", "Diana", "José"]

        example_records = []
        for i in range(max_sample_records):
            rec_id = 100 + i  # 100, 101, 102, ...
            name = names_pool[i % len(names_pool)]
            example_records.append((rec_id, name))

        # Distribuir registros en bloques de datos según bfr
        data_blocks = [[] for _ in range(b)]  # lista de bloques, cada uno lista de (id, nombre)
        for i, (rec_id, name) in enumerate(example_records):
            if bfr <= 0:
                break
            block_idx = i // bfr
            if block_idx >= b:
                break
            data_blocks[block_idx].append((rec_id, name))

        # Entradas de índice según tipo
        index_entries = []  # lista de (indexacion, puntero)
        if index_type == "primary":
            # Índice primario: Indexación = id del primer registro de cada bloque, Puntero = Bk
            for block_idx, rows in enumerate(data_blocks):
                if not rows:
                    continue
                clave = rows[0][0]
                puntero = f"B{block_idx}"
                index_entries.append((str(clave), puntero))
                if len(index_entries) >= max_sample_index_entries:
                    break
        else:
            # Índice secundario: Indexación = nombre, Puntero = id
            for rec_id, name in example_records:
                index_entries.append((name, str(rec_id)))
                if len(index_entries) >= max_sample_index_entries:
                    break

        # Distribuir entradas de índice en bloques de índice según bfri
        index_blocks = [[] for _ in range(bi)]
        for i, entry in enumerate(index_entries):
            if bfri <= 0:
                break
            block_idx = i // bfri
            if block_idx >= bi:
                break
            index_blocks[block_idx].append(entry)

        # ---------------------------------------------------------------------
        # 2) Encabezados de columnas
        # ---------------------------------------------------------------------
        idx_type_text = "Primario (no denso)" if index_type == "primary" else "Secundario (denso)"
        idx_color = "#c7e9ff" if index_type == "primary" else "#c7ffd9"

        # Encabezado índice de primer nivel
        self.canvas.create_text(
            idx_center_x,
            margin_y - 30,
            anchor="s",
            text=f"ÍNDICE (nivel 1: {idx_type_text})  bi = {bi}",
            font=("Arial", 10, "bold"),
            fill="#333333",
        )

        # Encabezado bloques de datos
        self.canvas.create_text(
            data_center_x,
            margin_y - 30,
            anchor="s",
            text=f"BLOQUES DE DATOS  b = {b}",
            font=("Arial", 10, "bold"),
            fill="#333333",
        )

        start_y = margin_y

        max_blocks_draw_idx = min(3, bi)   # menos bloques para que se vea limpio
        max_blocks_draw_data = min(3, b)

        header_h = 20
        row_h = 14
        max_rows_per_block = 4  # filas visibles por bloque

        # ---------------------------------------------------------------------
        # 3) Bloques de NIVELES MULTINIVEL (>=2), a la izquierda en "cadena"
        # ---------------------------------------------------------------------
        # No mostramos el nivel 1 aquí porque es el índice base (I0, I1, ...)
        if is_multilevel and len(multilevel_blocks) > 1:
            # Niveles a mostrar: del 2 en adelante
            # multilevel_blocks = [b1, b2, b3, ...]
            levels_to_show = multilevel_blocks[1:]  # quitamos b1
            # No saturar: como máximo 3 niveles extra visibles
            levels_to_show = levels_to_show[:3]

            # Cada nivel ocupa una columna hacia la izquierda del índice base
            horizontal_gap = 20
            lvl_block_w = 130
            lvl_block_h = 70

            # x_center del nivel 2: a la izquierda del índice base
            # x_center del nivel 3: más a la izquierda, etc.
            level_centers = []
            for i in range(len(levels_to_show)):
                offset = (i + 1)  # nivel 2 -> 1, nivel 3 -> 2...
                x_center = idx_center_x - offset * (lvl_block_w + horizontal_gap)
                level_centers.append(x_center)

            lvl_y = start_y

            for idx_level, blocks_in_level in enumerate(levels_to_show):
                level_num = idx_level + 2  # porque empezamos en nivel 2
                x_center = level_centers[idx_level]

                x1 = x_center - lvl_block_w / 2
                y1 = lvl_y
                x2 = x_center + lvl_block_w / 2
                y2 = y1 + lvl_block_h

                # Marco del bloque
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill="#f5f5f5",
                    outline="#555555"
                )

                # Línea vertical para columnas
                mid_x = (x1 + x2) / 2
                self.canvas.create_line(mid_x, y1, mid_x, y2, fill="#555555")

                # Encabezados de columnas
                self.canvas.create_text(
                    (x1 + mid_x) / 2,
                    y1 + header_h / 2,
                    text="Indexación",
                    font=("Arial", 8, "bold"),
                )
                self.canvas.create_text(
                    (mid_x + x2) / 2,
                    y1 + header_h / 2,
                    text="Puntero",
                    font=("Arial", 8, "bold"),
                )

                # Línea bajo encabezado
                header_bottom = y1 + header_h
                self.canvas.create_line(x1, header_bottom, x2, header_bottom, fill="#555555")

                # Líneas horizontales de filas (solo 2 filas de ejemplo)
                for r_line in range(2):
                    y_line = header_bottom + (r_line + 1) * row_h
                    if y_line < y2:
                        self.canvas.create_line(x1, y_line, x2, y_line, fill="#bbbbbb")

                # Contenido de ejemplo (primer bloque del nivel)
                # Notación: L{level_num}_B0, L{level_num}_B1 ...
                example_rows = [
                    (f"K{level_num}1", f"L{level_num}_B0"),
                    (f"K{level_num}2", f"L{level_num}_B1" if blocks_in_level > 1 else f"L{level_num}_B0"),
                ]
                for r_idx, (idx_val, ptr_val) in enumerate(example_rows):
                    row_y = header_bottom + row_h * r_idx + row_h / 2
                    self.canvas.create_text(
                        (x1 + mid_x) / 2,
                        row_y,
                        text=idx_val,
                        font=("Arial", 8),
                    )
                    self.canvas.create_text(
                        (mid_x + x2) / 2,
                        row_y,
                        text=ptr_val,
                        font=("Arial", 8),
                    )

                # Etiqueta del bloque arriba con info de # de bloques del nivel
                self.canvas.create_text(
                    x_center,
                    y1 - 10,
                    text=f"Nivel {level_num}  (b{level_num} = {blocks_in_level} bloques)",
                    font=("Arial", 8, "bold"),
                    fill="#333333",
                )

        # ---------------------------------------------------------------------
        # 4) Bloques de ÍNDICE de primer nivel (centro-izquierda)
        # ---------------------------------------------------------------------
        if bi <= 0:
            self.canvas.create_text(
                idx_center_x,
                start_y,
                anchor="n",
                text="(No hay bloques de índice)",
                font=("Arial", 9),
                fill="#888888",
            )
        else:
            y = start_y
            first_idx_block_pos = None

            for b_idx in range(max_blocks_draw_idx):
                x1 = idx_center_x - block_w / 2
                y1 = y
                x2 = idx_center_x + block_w / 2
                y2 = y1 + block_h

                if first_idx_block_pos is None:
                    first_idx_block_pos = (x2, (y1 + y2) / 2)

                # Marco del bloque
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=idx_color,
                    outline="#555555"
                )

                # Línea vertical para dividir columnas
                mid_x = (x1 + x2) / 2
                self.canvas.create_line(mid_x, y1, mid_x, y2, fill="#555555")

                # Encabezados de columnas
                self.canvas.create_text(
                    (x1 + mid_x) / 2,
                    y1 + header_h / 2,
                    text="Indexación",
                    font=("Arial", 8, "bold"),
                )
                self.canvas.create_text(
                    (mid_x + x2) / 2,
                    y1 + header_h / 2,
                    text="Puntero",
                    font=("Arial", 8, "bold"),
                )

                # Línea bajo encabezado
                header_bottom = y1 + header_h
                self.canvas.create_line(x1, header_bottom, x2, header_bottom, fill="#555555")

                # Líneas horizontales para filas
                for r_line in range(max_rows_per_block):
                    y_line = header_bottom + (r_line + 1) * row_h
                    if y_line < y2:
                        self.canvas.create_line(x1, y_line, x2, y_line, fill="#bbbbbb")

                # Datos de este bloque de índice
                entries = index_blocks[b_idx] if b_idx < len(index_blocks) else []
                for row_idx, (idx_val, ptr_val) in enumerate(entries[:max_rows_per_block]):
                    row_y = header_bottom + row_h * row_idx + row_h / 2
                    self.canvas.create_text(
                        (x1 + mid_x) / 2,
                        row_y,
                        text=str(idx_val),
                        font=("Arial", 8),
                    )
                    self.canvas.create_text(
                        (mid_x + x2) / 2,
                        row_y,
                        text=str(ptr_val),
                        font=("Arial", 8),
                    )

                # Etiqueta del bloque arriba
                self.canvas.create_text(
                    idx_center_x,
                    y1 - 10,
                    text=f"I{b_idx}",
                    font=("Arial", 8, "bold"),
                    fill="#333333",
                )

                y = y2 + v_spacing

            if bi > max_blocks_draw_idx:
                self.canvas.create_text(
                    idx_center_x,
                    y,
                    anchor="n",
                    text=f"... (total {bi} bloques de índice)",
                    font=("Arial", 8),
                    fill="#666666",
                )

            # Capacidad del bloque índice junto al primer bloque
            if first_idx_block_pos and bfri > 0:
                cap_x, cap_y = first_idx_block_pos
                self.canvas.create_text(
                    cap_x + 10,
                    cap_y,
                    anchor="w",
                    text=f"Capacidad: {bfri} entradas/bloque",
                    font=("Arial", 8, "italic"),
                    fill="#333333",
                )

        # ---------------------------------------------------------------------
        # 5) Bloques de DATOS (derecha)
        # ---------------------------------------------------------------------
        if b <= 0:
            self.canvas.create_text(
                data_center_x,
                start_y,
                anchor="n",
                text="(No hay bloques de datos)",
                font=("Arial", 9),
                fill="#888888",
            )
        else:
            y = start_y
            first_data_block_pos = None

            for b_idx in range(max_blocks_draw_data):
                x1 = data_center_x - block_w / 2
                y1 = y
                x2 = data_center_x + block_w / 2
                y2 = y1 + block_h

                if first_data_block_pos is None:
                    first_data_block_pos = (x1, (y1 + y2) / 2)

                # Marco del bloque
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill="#e0e0e0",
                    outline="#555555"
                )

                # Línea vertical para dividir columnas
                mid_x = (x1 + x2) / 2
                self.canvas.create_line(mid_x, y1, mid_x, y2, fill="#555555")

                # Encabezados de columnas
                self.canvas.create_text(
                    (x1 + mid_x) / 2,
                    y1 + header_h / 2,
                    text="id",
                    font=("Arial", 8, "bold"),
                )
                self.canvas.create_text(
                    (mid_x + x2) / 2,
                    y1 + header_h / 2,
                    text="nombre",
                    font=("Arial", 8, "bold"),
                )

                # Línea bajo encabezado
                header_bottom = y1 + header_h
                self.canvas.create_line(x1, header_bottom, x2, header_bottom, fill="#555555")

                # Líneas horizontales para filas
                for r_line in range(max_rows_per_block):
                    y_line = header_bottom + (r_line + 1) * row_h
                    if y_line < y2:
                        self.canvas.create_line(x1, y_line, x2, y_line, fill="#bbbbbb")

                # Registros de este bloque de datos
                rows = data_blocks[b_idx] if b_idx < len(data_blocks) else []
                for row_idx, (rec_id, name) in enumerate(rows[:max_rows_per_block]):
                    row_y = header_bottom + row_h * row_idx + row_h / 2
                    self.canvas.create_text(
                        (x1 + mid_x) / 2,
                        row_y,
                        text=str(rec_id),
                        font=("Arial", 8),
                    )
                    self.canvas.create_text(
                        (mid_x + x2) / 2,
                        row_y,
                        text=str(name),
                        font=("Arial", 8),
                    )

                # Etiqueta del bloque arriba
                self.canvas.create_text(
                    data_center_x,
                    y1 - 10,
                    text=f"B{b_idx}",
                    font=("Arial", 8, "bold"),
                    fill="#333333",
                )

                y = y2 + v_spacing

            if b > max_blocks_draw_data:
                self.canvas.create_text(
                    data_center_x,
                    y,
                    anchor="n",
                    text=f"... (total {b} bloques de datos)",
                    font=("Arial", 8),
                    fill="#666666",
                )

            # Capacidad del bloque de datos junto al primer bloque
            if first_data_block_pos and bfr > 0:
                cap_x, cap_y = first_data_block_pos
                self.canvas.create_text(
                    cap_x - 10,
                    cap_y,
                    anchor="e",
                    text=f"Capacidad: {bfr} registros/bloque",
                    font=("Arial", 8, "italic"),
                    fill="#333333",
                )

        # ---------------------------------------------------------------------
        # 6) Leyenda final (incluyendo multinivel)
        # ---------------------------------------------------------------------
        if is_multilevel and multilevel_blocks:
            niveles_str = " → ".join(
                f"b{idx+1}={val}" for idx, val in enumerate(multilevel_blocks)
            )
            multinivel_line = (
                f"  • Niveles de índice (multinivel): {niveles_str} con f0 = bfri = {bfri}.\n"
                "  • Accesos a memoria = nº niveles (b1..bn) + 1 (bloque de datos)."
            )
        else:
            multinivel_line = (
                "  • Índice simple: accesos a memoria ≈ ceil(log₂(bi)) + 1.\n"
                "  • Activa 'Índice multinivel' para ver los niveles b1, b2, ..."
            )

        legend_text = (
            "Ejemplo visual:\n"
            "  • ÍNDICE primario: Indexación = id clave de bloque, Puntero = Bk.\n"
            "  • ÍNDICE secundario: Indexación = nombre, Puntero = id.\n"
            "  • Los datos (id, nombre) son de ejemplo, pero b, bi, bfr y bfri\n"
            "    provienen de los cálculos reales.\n"
            f"{multinivel_line}"
        )
        self.canvas.create_text(
            w / 2,
            h - 8,
            anchor="s",
            text=legend_text,
            font=("Arial", 9),
            fill="#444444",
        )

    # -------------------------------------------------------------------------
    # Guardar / cargar (placeholders)
    # -------------------------------------------------------------------------
    def _on_save(self) -> None:
        # Placeholder para funcionalidad futura
        pass

    def _on_save_and_close(self) -> None:
        # Placeholder para funcionalidad futura
        self.app.navigate("externas")

    def _on_load(self) -> None:
        # Placeholder para funcionalidad futura
        pass
