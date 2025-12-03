import math
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json


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

        # Selección de tipo de índice mediante ComboBox
        row += 1
        ttk.Label(ops, text="Tipo de índice:").grid(row=row, column=0, sticky="w", pady=(8, 2))

        # Variable interna: siempre "primary" o "secondary"
        self.index_type = tk.StringVar(value="primary")

        # ComboBox solo para visual (Primario/Secundario)
        self.cmb_index_type = ttk.Combobox(
            ops,
            state="readonly",
            values=["Primario", "Secundario"],
        )
        self.cmb_index_type.grid(row=row, column=1, sticky="w", pady=(8, 2))
        self.cmb_index_type.current(0)  # Mostrar "Primario" por defecto

        def _update_index_type(event=None):
            selected = self.cmb_index_type.get()
            if selected == "Primario":
                self.index_type.set("primary")
            else:
                self.index_type.set("secondary")

        # Sincronizar al inicio
        _update_index_type()
        self.cmb_index_type.bind("<<ComboboxSelected>>", _update_index_type)

        # Check: índice multinivel
        row += 1
        self.is_multilevel = tk.BooleanVar(value=False)
        chk_multilevel = ttk.Checkbutton(ops, text="Índice multinivel", variable=self.is_multilevel)
        chk_multilevel.grid(row=row, column=1, sticky="w", pady=(4, 4), padx=(0, 0))

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
        # Panel inferior: guardar / cargar / limpiar
        # ---------------------------------------------------------------------
        file_panel = ttk.Frame(self, style="Panel.TFrame", padding=8)
        file_panel.pack(fill=tk.X, padx=4, pady=6)

        btn_save_close = ttk.Button(file_panel, text="Guardar y cerrar", command=self._on_save_and_close)
        btn_save_close.grid(row=0, column=0, padx=4, pady=2)

        btn_save = ttk.Button(file_panel, text="Guardar", command=self._on_save)
        btn_save.grid(row=0, column=1, padx=4, pady=2)

        btn_load = ttk.Button(file_panel, text="Cargar", command=self._on_load)
        btn_load.grid(row=0, column=2, padx=4, pady=2)

        btn_clear = ttk.Button(file_panel, text="Limpiar pantalla", command=self._on_clear)
        btn_clear.grid(row=0, column=3, padx=4, pady=2)

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
    # Visualización en Canvas
    # -------------------------------------------------------------------------
    def _draw_visualization(self) -> None:
        self.canvas.delete("all")

        if not hasattr(self, "_last_calc") or not self._last_calc:
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
            w, h = 900, 460

        # ------------------------------------------------------------------
        # Recuperar cálculos
        # ------------------------------------------------------------------
        r = self._last_calc["r"]
        bfr = self._last_calc["bfr"]
        b = self._last_calc["b"]
        bfri = self._last_calc["bfri"]
        bi = self._last_calc["bi"]
        index_type = self._last_calc["index_type"]
        ri = self._last_calc["ri"]
        multilevel_blocks = self._last_calc.get("multilevel_blocks", [])
        is_multilevel = self._last_calc.get("is_multilevel", False)

        # ------------------------------------------------------------------
        # Layout general
        # ------------------------------------------------------------------
        margin_y = 70
        header_h = 20
        row_h = 14

        # Más filas visibles por bloque para rellenar mejor
        max_rows_per_block = 6

        section_h = max_rows_per_block * row_h
        content_h = 3 * section_h
        struct_h = header_h + content_h + 10

        idx_center_x = w * 0.45
        data_center_x = w * 0.80

        # Para flechas índice → datos
        idx_block_centers: dict[str, float] = {}
        data_block_centers: dict[str, float] = {}
        idx_struct_right: float | None = None
        data_struct_left: float | None = None

        # ------------------------------------------------------------------
        # Helpers
        # ------------------------------------------------------------------
        def pick_three_indices(total_blocks: int):
            """Devuelve índices representativos: [bloque1, intermedio, final]."""
            if total_blocks <= 0:
                return []
            if total_blocks == 1:
                return [0]
            if total_blocks == 2:
                return [0, 1]
            first = 0
            mid = total_blocks // 2
            last = total_blocks - 1
            return [first, mid, last]

        def draw_bracket(x_ref: float, y_top: float, y_bottom: float, side: str = "left"):
            """Dibuja una llave lateral para marcar inicio y fin de un bloque."""
            offset = 8
            if side == "left":
                x1 = x_ref - offset
                x2 = x_ref
            else:
                x1 = x_ref
                x2 = x_ref + offset

            self.canvas.create_line(x1, y_top, x1, y_bottom, fill="#444444")
            self.canvas.create_line(x1, y_top, x2, y_top, fill="#444444")
            self.canvas.create_line(x1, y_bottom, x2, y_bottom, fill="#444444")

        # ------------------------------------------------------------------
        # 1) Datos de ejemplo respetando capacidades (LLENOS)
        # ------------------------------------------------------------------
        # Generamos tantos registros como permite el fichero: min(r, b*bfr)
        max_sample_records = min(r, b * bfr) if bfr > 0 and b > 0 else 0
        # Generamos tantas entradas de índice como quepan: min(ri, bi*bfri)
        max_sample_index_entries = min(ri, bi * bfri) if bfri > 0 and bi > 0 else 0

        names_pool = [
            "Juan", "Carlos", "Ana", "María", "Luis", "Sofía",
            "Pedro", "Lucía", "David", "Steven", "Diana", "José",
            "Elena", "Andrés", "Paula", "Camila", "Mateo", "Sara",
        ]

        example_records: list[tuple[int, str]] = []
        for i in range(max_sample_records):
            rec_id = 100 + i
            name = names_pool[i % len(names_pool)]
            example_records.append((rec_id, name))

        # Bloques de datos
        data_blocks: list[list[tuple[int, str]]] = [[] for _ in range(b)]
        for i, (rec_id, name) in enumerate(example_records):
            if bfr <= 0:
                break
            block_idx = i // bfr
            if block_idx >= b:
                break
            data_blocks[block_idx].append((rec_id, name))

        # Entradas de índice
        index_entries: list[tuple[str, str]] = []
        if index_type == "primary":
            # Primario: indexación = id del primer registro en el bloque, puntero = Bk
            for block_idx, rows in enumerate(data_blocks):
                if not rows:
                    continue
                clave = rows[0][0]
                puntero = f"B{block_idx}"
                index_entries.append((str(clave), puntero))
                if len(index_entries) >= max_sample_index_entries:
                    break
        else:
            # Secundario: indexación = nombre, puntero = id, ORDENADO alfabéticamente
            temp_entries = [(name, str(rec_id)) for rec_id, name in example_records]
            temp_entries.sort(key=lambda x: x[0].lower())
            index_entries.extend(temp_entries[:max_sample_index_entries])

        # Distribuir entradas en bloques de índice
        index_blocks: list[list[tuple[str, str]]] = [[] for _ in range(bi)]
        for i, entry in enumerate(index_entries):
            if bfri <= 0:
                break
            block_idx = i // bfri
            if block_idx >= bi:
                break
            index_blocks[block_idx].append(entry)

        # ------------------------------------------------------------------
        # 2) Índices multinivel (niveles ≥ 2) como estructuras únicas
        # ------------------------------------------------------------------
        if is_multilevel and len(multilevel_blocks) > 1:
            levels_to_show = multilevel_blocks[1:][:2]  # b2, b3 (máx 2)
            struct_w_lvl = 170
            struct_h_lvl = struct_h
            base_center_x = idx_center_x - struct_w_lvl - 80
            y1_struct_lvl = margin_y
            y2_struct_lvl = y1_struct_lvl + struct_h_lvl

            for idx_level, blocks_in_level in enumerate(levels_to_show):
                level_num = idx_level + 2  # nivel 2, 3, ...
                x_center = base_center_x - idx_level * (struct_w_lvl + 50)

                x1_struct = x_center - struct_w_lvl / 2
                x2_struct = x_center + struct_w_lvl / 2

                self.canvas.create_rectangle(
                    x1_struct, y1_struct_lvl, x2_struct, y2_struct_lvl,
                    outline="#444444",
                    fill="#f5f5f5"
                )

                inner_x1 = x1_struct + 5
                inner_x2 = x2_struct - 5
                mid_x = (inner_x1 + inner_x2) / 2

                # Encabezados
                self.canvas.create_text(
                    (inner_x1 + mid_x) / 2,
                    y1_struct_lvl + header_h / 2,
                    text="Indexación",
                    font=("Arial", 8, "bold"),
                )
                self.canvas.create_text(
                    (mid_x + inner_x2) / 2,
                    y1_struct_lvl + header_h / 2,
                    text="Puntero",
                    font=("Arial", 8, "bold"),
                )

                header_bottom = y1_struct_lvl + header_h
                self.canvas.create_line(inner_x1, header_bottom, inner_x2, header_bottom, fill="#555555")
                self.canvas.create_line(mid_x, y1_struct_lvl, mid_x, y2_struct_lvl, fill="#555555")

                # Grid continuo
                content_y1 = header_bottom
                total_rows = 3 * max_rows_per_block
                for r_line in range(total_rows):
                    y_line = content_y1 + (r_line + 1) * row_h
                    if y_line < y2_struct_lvl:
                        self.canvas.create_line(inner_x1, y_line, inner_x2, y_line, fill="#bbbbbb")

                # Selección de bloques representativos para este nivel
                block_indices_lvl = pick_three_indices(blocks_in_level)
                total_blocks_lvl = blocks_in_level

                if total_blocks_lvl == 1:
                    sections_to_draw = [("Bloque 1", block_indices_lvl[0])]
                elif total_blocks_lvl == 2:
                    sections_to_draw = [
                        ("Bloque 1", block_indices_lvl[0]),
                        ("Bloque final", block_indices_lvl[1]),
                    ]
                else:
                    sections_to_draw = [
                        ("Bloque 1", block_indices_lvl[0]),
                        ("Bloque i", block_indices_lvl[1]),
                        ("Bloque final", block_indices_lvl[2]),
                    ]

                current_y = content_y1

                for label_text, block_idx in sections_to_draw:
                    sec_y1 = current_y
                    sec_y2 = sec_y1 + section_h

                    # Llave a la izquierda
                    draw_bracket(x1_struct, sec_y1, sec_y2, side="left")

                    final_label = label_text
                    if block_idx is not None:
                        if label_text == "Bloque 1":
                            final_label += f" (L{level_num}_B0)"
                        elif label_text == "Bloque final":
                            final_label += f" (L{level_num}_B{block_idx})"
                        else:
                            final_label += f" (L{level_num}_B{block_idx})"

                    self.canvas.create_text(
                        x1_struct - 12,
                        (sec_y1 + sec_y2) / 2,
                        anchor="e",
                        text=final_label,
                        font=("Arial", 8, "bold"),
                        fill="#333333",
                    )

                    # Filas cosméticas
                    for row_idx in range(min(4, max_rows_per_block)):
                        row_y = sec_y1 + row_h * row_idx + row_h / 2
                        idx_val = f"K{level_num}{row_idx + 1}"
                        ptr_val = f"L{level_num}_B{block_idx if block_idx is not None else 0}"
                        self.canvas.create_text(
                            (inner_x1 + mid_x) / 2,
                            row_y,
                            text=idx_val,
                            font=("Arial", 8),
                        )
                        self.canvas.create_text(
                            (mid_x + inner_x2) / 2,
                            row_y,
                            text=ptr_val,
                            font=("Arial", 8),
                        )

                    current_y = sec_y2

                # Título del nivel
                self.canvas.create_text(
                    x_center,
                    y1_struct_lvl - 12,
                    text=f"Nivel {level_num} (b{level_num} = {blocks_in_level} bloques)",
                    font=("Arial", 8, "bold"),
                    fill="#333333",
                )

        # ------------------------------------------------------------------
        # 3) Índice nivel 1 como estructura única
        # ------------------------------------------------------------------
        idx_type_text = "Primario (no denso)" if index_type == "primary" else "Secundario (denso)"
        idx_fill = "#e3f3ff" if index_type == "primary" else "#dfffea"

        self.canvas.create_text(
            idx_center_x,
            margin_y - 30,
            anchor="s",
            text=f"ÍNDICE (nivel 1: {idx_type_text})  bi = {bi}",
            font=("Arial", 10, "bold"),
            fill="#333333",
        )

        start_y = margin_y

        if bi <= 0:
            self.canvas.create_text(
                idx_center_x,
                start_y,
                anchor="n",
                text="(No hay índice construido)",
                font=("Arial", 9),
                fill="#888888",
            )
        else:
            struct_w = 200
            x1_struct = idx_center_x - struct_w / 2
            x2_struct = idx_center_x + struct_w / 2
            y1_struct = start_y
            y2_struct = y1_struct + struct_h

            # Guardar borde derecho para flechas
            idx_struct_right = x2_struct

            # Marco
            self.canvas.create_rectangle(
                x1_struct, y1_struct, x2_struct, y2_struct,
                outline="#444444",
                fill=idx_fill
            )

            inner_x1 = x1_struct + 5
            inner_x2 = x2_struct - 5
            mid_x = (inner_x1 + inner_x2) / 2

            # Encabezados
            self.canvas.create_text(
                (inner_x1 + mid_x) / 2,
                y1_struct + header_h / 2,
                text="Indexación",
                font=("Arial", 8, "bold"),
            )
            self.canvas.create_text(
                (mid_x + inner_x2) / 2,
                y1_struct + header_h / 2,
                text="Puntero",
                font=("Arial", 8, "bold"),
            )

            header_bottom = y1_struct + header_h
            self.canvas.create_line(inner_x1, header_bottom, inner_x2, header_bottom, fill="#555555")
            self.canvas.create_line(mid_x, y1_struct, mid_x, y2_struct, fill="#555555")

            content_y1 = header_bottom
            total_rows = 3 * max_rows_per_block
            for r_line in range(total_rows):
                y_line = content_y1 + (r_line + 1) * row_h
                if y_line < y2_struct:
                    self.canvas.create_line(inner_x1, y_line, inner_x2, y_line, fill="#bbbbbb")

            # Capacidad
            if bfri > 0:
                self.canvas.create_text(
                    idx_center_x,
                    y2_struct + 12,
                    anchor="n",
                    text=f"Capacidad: {bfri} entradas/bloque",
                    font=("Arial", 8, "italic"),
                    fill="#333333",
                )

            total_blocks_idx = bi
            block_indices_idx = pick_three_indices(total_blocks_idx)

            if total_blocks_idx == 1:
                sections_to_draw = [("Bloque 1", block_indices_idx[0])]
            elif total_blocks_idx == 2:
                sections_to_draw = [
                    ("Bloque 1", block_indices_idx[0]),
                    ("Bloque final", block_indices_idx[1]),
                ]
            else:
                sections_to_draw = [
                    ("Bloque 1", block_indices_idx[0]),
                    ("Bloque i", block_indices_idx[1]),
                    ("Bloque final", block_indices_idx[2]),
                ]

            struct_edge_x = x2_struct
            label_x = x2_struct + 12
            label_anchor = "w"
            current_y = content_y1

            for label_text, block_idx in sections_to_draw:
                sec_y1 = current_y
                sec_y2 = sec_y1 + section_h
                center_y = (sec_y1 + sec_y2) / 2

                draw_bracket(struct_edge_x, sec_y1, sec_y2, side="right")

                final_label = label_text
                if block_idx is not None:
                    final_label += f" (I{block_idx})"

                self.canvas.create_text(
                    label_x,
                    center_y,
                    anchor=label_anchor,
                    text=final_label,
                    font=("Arial", 8, "bold"),
                    fill="#333333",
                )

                # Guardar centros para flechas
                if label_text.startswith("Bloque 1"):
                    idx_block_centers["first"] = center_y
                elif label_text.startswith("Bloque i"):
                    idx_block_centers["middle"] = center_y
                elif label_text.startswith("Bloque final"):
                    idx_block_centers["last"] = center_y

                if block_idx is not None and block_idx < len(index_blocks):
                    rows = index_blocks[block_idx]
                    for row_idx in range(min(max_rows_per_block, len(rows))):
                        row_y = sec_y1 + row_h * row_idx + row_h / 2
                        idx_val, ptr_val = rows[row_idx]
                        self.canvas.create_text(
                            (inner_x1 + mid_x) / 2,
                            row_y,
                            text=str(idx_val),
                            font=("Arial", 8),
                        )
                        self.canvas.create_text(
                            (mid_x + inner_x2) / 2,
                            row_y,
                            text=str(ptr_val),
                            font=("Arial", 8),
                        )

                current_y = sec_y2

        # ------------------------------------------------------------------
        # 4) Bloques de datos como estructura única
        # ------------------------------------------------------------------
        self.canvas.create_text(
            data_center_x,
            margin_y - 30,
            anchor="s",
            text=f"BLOQUES DE DATOS  b = {b}",
            font=("Arial", 10, "bold"),
            fill="#333333",
        )

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
            struct_w = 200
            x1_struct = data_center_x - struct_w / 2
            x2_struct = data_center_x + struct_w / 2
            y1_struct = start_y
            y2_struct = y1_struct + struct_h

            # Guardar borde izquierdo para flechas
            data_struct_left = x1_struct

            self.canvas.create_rectangle(
                x1_struct, y1_struct, x2_struct, y2_struct,
                outline="#444444",
                fill="#f0f0f0"
            )

            inner_x1 = x1_struct + 5
            inner_x2 = x2_struct - 5
            mid_x = (inner_x1 + inner_x2) / 2

            self.canvas.create_text(
                (inner_x1 + mid_x) / 2,
                y1_struct + header_h / 2,
                text="id",
                font=("Arial", 8, "bold"),
            )
            self.canvas.create_text(
                (mid_x + inner_x2) / 2,
                y1_struct + header_h / 2,
                text="nombre",
                font=("Arial", 8, "bold"),
            )

            header_bottom = y1_struct + header_h
            self.canvas.create_line(inner_x1, header_bottom, inner_x2, header_bottom, fill="#555555")
            self.canvas.create_line(mid_x, y1_struct, mid_x, y2_struct, fill="#555555")

            content_y1 = header_bottom
            total_rows = 3 * max_rows_per_block
            for r_line in range(total_rows):
                y_line = content_y1 + (r_line + 1) * row_h
                if y_line < y2_struct:
                    self.canvas.create_line(inner_x1, y_line, inner_x2, y_line, fill="#bbbbbb")

            if bfr > 0:
                self.canvas.create_text(
                    data_center_x,
                    y2_struct + 12,
                    anchor="n",
                    text=f"Capacidad: {bfr} registros/bloque",
                    font=("Arial", 8, "italic"),
                    fill="#333333",
                )

            total_blocks_data = b
            block_indices_data = pick_three_indices(total_blocks_data)

            if total_blocks_data == 1:
                sections_to_draw = [("Bloque 1", block_indices_data[0])]
            elif total_blocks_data == 2:
                sections_to_draw = [
                    ("Bloque 1", block_indices_data[0]),
                    ("Bloque final", block_indices_data[1]),
                ]
            else:
                sections_to_draw = [
                    ("Bloque 1", block_indices_data[0]),
                    ("Bloque j", block_indices_data[1]),
                    ("Bloque final", block_indices_data[2]),
                ]

            struct_edge_x = x2_struct
            label_x = x2_struct + 12
            label_anchor = "w"
            current_y = content_y1

            for label_text, block_idx in sections_to_draw:
                sec_y1 = current_y
                sec_y2 = sec_y1 + section_h
                center_y = (sec_y1 + sec_y2) / 2

                draw_bracket(struct_edge_x, sec_y1, sec_y2, side="right")

                final_label = label_text
                if block_idx is not None:
                    final_label += f" (B{block_idx})"

                self.canvas.create_text(
                    label_x,
                    center_y,
                    anchor=label_anchor,
                    text=final_label,
                    font=("Arial", 8, "bold"),
                    fill="#333333",
                )

                # Guardar centros para flechas
                if label_text.startswith("Bloque 1"):
                    data_block_centers["first"] = center_y
                elif label_text.startswith("Bloque j"):
                    data_block_centers["middle"] = center_y
                elif label_text.startswith("Bloque final"):
                    data_block_centers["last"] = center_y

                if block_idx is not None and block_idx < len(data_blocks):
                    rows = data_blocks[block_idx]
                    for row_idx, (rec_id, name) in enumerate(rows[:max_rows_per_block]):
                        row_y = sec_y1 + row_h * row_idx + row_h / 2
                        self.canvas.create_text(
                            (inner_x1 + mid_x) / 2,
                            row_y,
                            text=str(rec_id),
                            font=("Arial", 8),
                        )
                        self.canvas.create_text(
                            (mid_x + inner_x2) / 2,
                            row_y,
                            text=str(name),
                            font=("Arial", 8),
                        )

                current_y = sec_y2

        # ------------------------------------------------------------------
        # 5) Flechas índice → datos
        # ------------------------------------------------------------------
        if idx_struct_right is not None and data_struct_left is not None:
            pairs: list[tuple[str, float, float]] = []

            if "first" in idx_block_centers and "first" in data_block_centers:
                pairs.append(("first", idx_block_centers["first"], data_block_centers["first"]))
            if "middle" in idx_block_centers and "middle" in data_block_centers:
                pairs.append(("middle", idx_block_centers["middle"], data_block_centers["middle"]))
            if "last" in idx_block_centers and "last" in data_block_centers:
                pairs.append(("last", idx_block_centers["last"], data_block_centers["last"]))

            for kind, y_idx, y_data in pairs:
                offset = 0
                if kind == "middle":
                    offset = 4
                elif kind == "last":
                    offset = 8

                self.canvas.create_line(
                    idx_struct_right,
                    y_idx + offset,
                    data_struct_left,
                    y_data + offset,
                    arrow=tk.LAST,
                    smooth=True,
                    fill="#444444",
                )

        # ------------------------------------------------------------------
        # 6) Leyenda
        # ------------------------------------------------------------------
        if is_multilevel and multilevel_blocks:
            niveles_str = " → ".join(
                f"b{idx+1}={val}" for idx, val in enumerate(multilevel_blocks)
            )
            multinivel_line = (
                f"  • Niveles de índice (multinivel): {niveles_str} con f0 = bfri = {bfri}.\n"
                "  • Accesos a memoria (multinivel) ≈ nº niveles (b1..bn) + 1 (bloque de datos)."
            )
        else:
            multinivel_line = (
                "  • Índice simple: accesos a memoria ≈ ceil(log₂(bi)) + 1.\n"
                "  • Activa \"Índice multinivel\" para ver los niveles superiores (b2, b3, ...)."
            )

        legend_text = (
            "Ejemplo visual:\n"
            "  • El ÍNDICE (nivel 1) y los BLOQUES DE DATOS se muestran como estructuras únicas divididas en bloques.\n"
            "  • Las llaves indican Bloque 1, Bloque i/j y Bloque final (solo si hay suficientes bloques).\n"
            "  • Las flechas conectan los bloques lógicos del índice con los bloques físicos de datos.\n"
            "  • Los datos (id, nombre) e índices son de ejemplo, pero r, b, bi, bfr y bfri provienen de los cálculos reales.\n"
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
    # Guardar configuración y resultados en un archivo JSON
    # -------------------------------------------------------------------------
    def _on_save(self) -> None:
        if not hasattr(self, "_last_calc") or not self._last_calc:
            messagebox.showinfo("Guardar", "No hay cálculos para guardar todavía.")
            return

        file_path = filedialog.asksaveasfilename(
            parent=self,
            title="Guardar configuración de índices",
            defaultextension=".json",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
        )
        if not file_path:
            return  # Usuario canceló

        # Construimos el payload a guardar
        data_to_save = {
            "params": {},
            "calc": self._last_calc,
        }

        # Intentamos guardar también los campos de entrada si existen
        def safe_get_entry(name: str) -> str | None:
            widget = getattr(self, name, None)
            try:
                return widget.get().strip() if widget is not None else None
            except Exception:
                return None

        data_to_save["params"] = {
            "r": safe_get_entry("entry_r"),
            "B": safe_get_entry("entry_B"),
            "R": safe_get_entry("entry_R"),
            "v": safe_get_entry("entry_v"),
            "p": safe_get_entry("entry_p"),
            "index_type": self.index_type.get() if hasattr(self, "index_type") else None,
            "is_multilevel": self.is_multilevel.get() if hasattr(self, "is_multilevel") else None,
        }

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Guardar", "Configuración guardada correctamente.")
        except Exception as e:
            messagebox.showerror("Error al guardar", f"No se pudo guardar el archivo:\n{e}")

    # -------------------------------------------------------------------------
    # Guardar y cerrar la vista
    # -------------------------------------------------------------------------
    def _on_save_and_close(self) -> None:
        if not hasattr(self, "app") or self.app is None:
            # Por si acaso, si no hay app, solo intenta guardar
            self._on_save()
            return

        if not hasattr(self, "_last_calc") or not self._last_calc:
            # Si no hay nada calculado, solo navegar
            self.app.navigate("externas")
            return

        file_path = filedialog.asksaveasfilename(
            parent=self,
            title="Guardar configuración de índices antes de salir",
            defaultextension=".json",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            data_to_save = {
                "params": {},
                "calc": self._last_calc,
            }

            def safe_get_entry(name: str) -> str | None:
                widget = getattr(self, name, None)
                try:
                    return widget.get().strip() if widget is not None else None
                except Exception:
                    return None

            data_to_save["params"] = {
                "r": safe_get_entry("entry_r"),
                "B": safe_get_entry("entry_B"),
                "R": safe_get_entry("entry_R"),
                "v": safe_get_entry("entry_v"),
                "p": safe_get_entry("entry_p"),
                "index_type": self.index_type.get() if hasattr(self, "index_type") else None,
                "is_multilevel": self.is_multilevel.get() if hasattr(self, "is_multilevel") else None,
            }

            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data_to_save, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("Guardar", "Configuración guardada correctamente.")
            except Exception as e:
                messagebox.showerror("Error al guardar", f"No se pudo guardar el archivo:\n{e}")
                return

        # Navegamos de vuelta al menú anterior
        self.app.navigate("externas")

    # -------------------------------------------------------------------------
    # Cargar configuración y resultados desde un archivo JSON
    # -------------------------------------------------------------------------
    def _on_load(self) -> None:
        file_path = filedialog.askopenfilename(
            parent=self,
            title="Cargar configuración de índices",
            defaultextension=".json",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
        )
        if not file_path:
            return  # Usuario canceló

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data_loaded = json.load(f)
        except Exception as e:
            messagebox.showerror("Error al cargar", f"No se pudo leer el archivo:\n{e}")
            return

        # Restaurar cálculos
        calc = data_loaded.get("calc")
        if calc:
            self._last_calc = calc
        else:
            messagebox.showwarning("Cargar", "El archivo no contiene información de cálculos.")
            return

        # Restaurar parámetros de entrada si los widgets existen
        params = data_loaded.get("params", {})

        def safe_set_entry(name: str, value: str | None):
            widget = getattr(self, name, None)
            if widget is not None and value is not None:
                try:
                    widget.delete(0, tk.END)
                    widget.insert(0, str(value))
                except Exception:
                    pass

        safe_set_entry("entry_r", params.get("r"))
        safe_set_entry("entry_B", params.get("B"))
        safe_set_entry("entry_R", params.get("R"))
        safe_set_entry("entry_v", params.get("v"))
        safe_set_entry("entry_p", params.get("p"))

        # Tipo de índice (primario/secundario)
        if hasattr(self, "index_type") and params.get("index_type"):
            self.index_type.set(params["index_type"])
            if hasattr(self, "cmb_index_type"):
                if params["index_type"] == "primary":
                    self.cmb_index_type.set("Primario")
                else:
                    self.cmb_index_type.set("Secundario")

        # Índice multinivel (checkbutton)
        if hasattr(self, "is_multilevel") and params.get("is_multilevel") is not None:
            try:
                self.is_multilevel.set(params["is_multilevel"])
            except Exception:
                pass

        # Redibujar visualización con los datos cargados
        self._draw_visualization()
        messagebox.showinfo("Cargar", "Configuración cargada correctamente.")

    def _on_clear(self) -> None:
        """Limpia todo el canvas y elimina resultados anteriores."""
        self.canvas.delete("all")
        self._last_calc = None

        self.canvas.create_text(
            10, 10,
            anchor="nw",
            text="Pantalla limpiada. Introduce valores y pulsa 'Calcular'.",
            fill="#777777",
            font=("Arial", 10, "italic"),
        )
