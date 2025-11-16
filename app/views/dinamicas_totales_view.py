# app/views/dinamicas_totales_view.py

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import List, Optional


class HashTableTotales:
    """
    Tabla hash basada en cubetas, con expansiones y reducciones TOTALES.

    - #cubetas iniciales
    - tamaño de cubeta
    - densidad de ocupación objetivo (ej: 0.75)

    Manejo de colisiones:
        - Si la cubeta está llena, el nuevo registro va a una lista de
          *desbordamiento (overflow)* asociada a esa cubeta.

    Expansión total:
        - Se dispara cuando densidad_actual >= densidad_objetivo
        - Duplica el número de cubetas (N -> 2N) y reubica todos los registros
        (cubetas + overflow).

    Reducción total:
        - Forzada manualmente (botón)
        - Reduce a la mitad el número de cubetas (N -> N/2), hasta un mínimo
        de num_cubetas_inicial, reubicando todos los registros.
    """

    def __init__(self, num_cubetas: int, tam_cubeta: int, densidad_objetivo: float) -> None:
        self.num_cubetas_inicial = max(1, num_cubetas)
        self.num_cubetas = max(1, num_cubetas)
        self.tam_cubeta = max(1, tam_cubeta)
        self.densidad_objetivo = densidad_objetivo  # ej: 0.75

        # buckets: lista de cubetas (área principal)
        self.buckets: list[list[int | None]] = [
            [None] * self.tam_cubeta for _ in range(self.num_cubetas)
        ]
        # overflow: lista de listas, una por cubeta
        self.overflow: list[list[int]] = [[] for _ in range(self.num_cubetas)]

        self.total_registros: int = 0  # cuenta principal + overflow
                # 🔹 Nuevo: orden en que se insertaron las claves
        self.insertion_order: list[int] = []

    # ------------------------------------------------------------
    # Propiedades
    # ------------------------------------------------------------
    @property
    def capacidad_total(self) -> int:
        # Capacidad del área principal (sin contar overflow)
        return self.num_cubetas * self.tam_cubeta

    @property
    def densidad_actual(self) -> float:
        if self.capacidad_total == 0:
            return 0.0
        # Todos los registros (incluyendo overflow) sobre la capacidad principal
        return self.total_registros / self.capacidad_total

    # ------------------------------------------------------------
    # Operaciones básicas
    # ------------------------------------------------------------
    def insertar(self, clave: int) -> str:
        """
        Inserta una clave en la tabla.

        - Calcula bucket_index = clave % num_cubetas.
        - Si hay espacio en la cubeta principal, se inserta allí.
        - Si la cubeta está llena, se inserta en la lista de overflow de esa cubeta.
        - Después de insertar, si densidad >= objetivo, realiza expansión total.
        """
        msg = self._insertar_en_cubeta_o_overflow(clave)

        # Verificar densidad para posible expansión total
        if self.densidad_actual >= self.densidad_objetivo:
            msg += (
                f" | Densidad actual {self.densidad_actual:.2f} ≥ objetivo "
                f"{self.densidad_objetivo:.2f}, se realiza expansión TOTAL (duplicar cubetas)."
            )
            self._expansion_total()
        else:
            msg += f" | Densidad actual {self.densidad_actual:.2f}, no se requiere expansión."

        return msg

    def eliminar(self, clave: int) -> str:
        bucket_idx = clave % self.num_cubetas

        # Buscar en área principal
        bucket = self.buckets[bucket_idx]
        for i, val in enumerate(bucket):
            if val == clave:
                bucket[i] = None
                self.total_registros -= 1
                self._remove_from_insertion_order(clave)  # 🔹 nuevo
                msg = (
                    f"Registro {clave} eliminado de la cubeta {bucket_idx}, posición {i}. "
                    f"Densidad actual: {self.densidad_actual:.2f}"
                )
                return self._post_delete_maybe_reduce(msg)

        # Buscar en overflow
        overflow_list = self.overflow[bucket_idx]
        if clave in overflow_list:
            overflow_list.remove(clave)
            self.total_registros -= 1
            self._remove_from_insertion_order(clave)  # 🔹 nuevo
            msg = (
                f"Registro {clave} eliminado del overflow de la cubeta {bucket_idx}. "
                f"Densidad actual: {self.densidad_actual:.2f}"
            )
            return self._post_delete_maybe_reduce(msg)

        return f"Registro {clave} no encontrado en la cubeta {bucket_idx}."

    def _post_delete_maybe_reduce(self, base_msg: str) -> str:
        """
        Tras una eliminación exitosa, verifica si la densidad
        cayó por debajo del umbral de reducción.

        Umbral de reducción: 1 - densidad_objetivo.
        Ejemplo: objetivo = 0.75 -> umbral_baja = 0.25.
        """
        # Si no hay capacidad (caso extremo), no reducimos más.
        if self.capacidad_total == 0:
            return base_msg

        umbral_baja = 1.0 - self.densidad_objetivo

        if self.densidad_actual <= umbral_baja:
            # Intentar reducción total (la función ya respeta el mínimo de cubetas)
            reduccion_msg = self.reduccion_total()
            return (
                base_msg
                + f" | Densidad actual ≤ {umbral_baja:.2f}, se intenta REDUCCIÓN TOTAL. "
                + reduccion_msg
            )

        return base_msg
    
    def _remove_from_insertion_order(self, clave: int) -> None:
        try:
            self.insertion_order.remove(clave)
        except ValueError:
            # Por si acaso no está; no queremos que explote la app docente
            pass


    # ------------------------------------------------------------
    # Internos: inserción con overflow
    # ------------------------------------------------------------
    def _insertar_en_cubeta_o_overflow(self, clave: int) -> str:
        bucket_idx = clave % self.num_cubetas
        bucket = self.buckets[bucket_idx]

        # Intentar en el área principal
        for i in range(self.tam_cubeta):
            if bucket[i] is None:
                bucket[i] = clave
                self.total_registros += 1
                # 🔹 registrar orden de inserción
                self.insertion_order.append(clave)
                return (
                    f"Registro {clave} insertado en cubeta {bucket_idx}, posición {i} "
                    f"(clave % {self.num_cubetas} = {bucket_idx})."
                )

        # Cubeta llena: insertar en overflow
        self.overflow[bucket_idx].append(clave)
        self.total_registros += 1
        # 🔹 registrar orden de inserción
        self.insertion_order.append(clave)
        return (
            f"Cubeta {bucket_idx} llena, registro {clave} insertado en OVERFLOW "
            f"de la cubeta {bucket_idx}."
        )


    # ------------------------------------------------------------
    # Expansión y reducción TOTALES
    # ------------------------------------------------------------
    def _expansion_total(self) -> None:
        """
        Expansión TOTAL:
        - Duplica el número de cubetas: N -> 2N
        - Reubica todos los registros (principal + overflow) recalculando el módulo.
        """
        nuevas_cubetas = self.num_cubetas * 2
        if nuevas_cubetas == self.num_cubetas:
            return

        valores = self._extraer_todos_los_valores()
        self.num_cubetas = nuevas_cubetas

        self.buckets = [[None] * self.tam_cubeta for _ in range(self.num_cubetas)]
        self.overflow = [[] for _ in range(self.num_cubetas)]
        self.total_registros = 0

        for v in valores:
            self._insertar_sin_expandir(v)

    def reduccion_total(self) -> str:
        """
        Reducción TOTAL (forzada):
        - num_cubetas: N -> N/2, sin bajar del número inicial.
        - Reubica todos los registros.
        """
        if self.num_cubetas <= self.num_cubetas_inicial:
            return "No se puede reducir más, ya se alcanzó el número mínimo de cubetas."

        nuevas_cubetas = max(self.num_cubetas_inicial, self.num_cubetas // 2)
        if nuevas_cubetas == self.num_cubetas:
            return "El número de cubetas ya es el mínimo permitido."

        valores = self._extraer_todos_los_valores()
        self.num_cubetas = nuevas_cubetas

        self.buckets = [[None] * self.tam_cubeta for _ in range(self.num_cubetas)]
        self.overflow = [[] for _ in range(self.num_cubetas)]
        self.total_registros = 0

        for v in valores:
            self._insertar_sin_expandir(v)

        return (
            f"Reducción TOTAL realizada: ahora hay {self.num_cubetas} cubetas. "
            f"Densidad actual: {self.densidad_actual:.2f}"
        )

    # ------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------
    def _extraer_todos_los_valores(self) -> list[int]:
        """
        Devuelve los registros en el orden EXACTO en que fueron insertados.
        Esto garantiza que en cualquier expansión/reducción los módulos
        se recalculen en ese mismo orden.
        """
        return list(self.insertion_order)


    def _insertar_sin_expandir(self, clave: int) -> None:
        """
        Inserta un valor sin disparar expansiones (se usa únicamente
        dentro de expansión/reducción).
        """
        bucket_idx = clave % self.num_cubetas
        bucket = self.buckets[bucket_idx]

        for i in range(self.tam_cubeta):
            if bucket[i] is None:
                bucket[i] = clave
                self.total_registros += 1
                return

        # Si la cubeta está llena en la reconstrucción, se va a overflow
        self.overflow[bucket_idx].append(clave)
        self.total_registros += 1



class DinamicasTotalesView(ttk.Frame):
    """
    Vista para manejar y visualizar cubetas con expansiones / reducciones TOTALES.
    """

    BUCKET_WIDTH = 70
    CELL_HEIGHT = 26
    MARGIN = 10

    def __init__(self, parent: tk.Widget, app) -> None:
        super().__init__(parent)
        self.app = app

        self.hash_table: Optional[HashTableTotales] = None

        self._build_widgets()
        self._configure_layout()

    # ------------------------------------------------------------
    # Construcción UI
    # ------------------------------------------------------------
    def _build_widgets(self) -> None:
        # Título
        self.label_title = ttk.Label(
            self,
            text="Dinámicas de Hash – Expansiones y Reducciones TOTALES",
            font=("TkDefaultFont", 14, "bold"),
        )

        # Botón volver
        self.btn_back = ttk.Button(
            self,
            text="← Volver",
            style="Retro.TButton",
            command=lambda: self.app.navigate("externas"),
        )

        # === Configuración de la tabla ===
        self.frame_config = ttk.LabelFrame(self, text="Configuración de la tabla", padding=10)

        ttk.Label(self.frame_config, text="Cubetas:").grid(
            row=0, column=0, sticky="e", padx=5, pady=5
        )
        self.entry_cubetas = ttk.Entry(self.frame_config, width=6)
        self.entry_cubetas.grid(row=0, column=1, padx=5)

        ttk.Label(self.frame_config, text="Tamaño:").grid(
            row=0, column=2, sticky="e", padx=5
        )
        self.entry_tam = ttk.Entry(self.frame_config, width=6)
        self.entry_tam.grid(row=0, column=3, padx=5)

        ttk.Label(self.frame_config, text="Densidad (%):").grid(
            row=0, column=4, sticky="e", padx=5
        )
        self.entry_dens = ttk.Entry(self.frame_config, width=6)
        self.entry_dens.grid(row=0, column=5, padx=5)

        self.btn_init = ttk.Button(
            self.frame_config,
            text="Inicializar tabla",
            command=self._on_init_table,
        )
        self.btn_init.grid(row=0, column=6, padx=10)

        # === Operaciones ===
        self.frame_ops = ttk.LabelFrame(self, text="Operaciones", padding=10)

        # Fila 0 - Insertar
        ttk.Label(self.frame_ops, text="Insertar registro:").grid(
            row=0, column=0, sticky="e", padx=5, pady=5
        )
        self.entry_insert = ttk.Entry(self.frame_ops, width=10)
        self.entry_insert.grid(row=0, column=1, padx=5)
        self.btn_insert = ttk.Button(
            self.frame_ops,
            text="Ingresar",
            command=self._on_insert,
            state="disabled",
        )
        self.btn_insert.grid(row=0, column=2, padx=5)

        # Fila 1 - Eliminar
        ttk.Label(self.frame_ops, text="Eliminar registro:").grid(
            row=1, column=0, sticky="e", padx=5
        )
        self.entry_delete = ttk.Entry(self.frame_ops, width=10)
        self.entry_delete.grid(row=1, column=1, padx=5)
        self.btn_delete = ttk.Button(
            self.frame_ops,
            text="Eliminar",
            command=self._on_delete,
            state="disabled",
        )
        self.btn_delete.grid(row=1, column=2, padx=5)

        # Fila 2 - Expansión / Reducción forzada
        self.btn_expand_total = ttk.Button(
            self.frame_ops,
            text="Expansión total",
            command=self._on_force_expand,
            state="disabled",
        )
        self.btn_expand_total.grid(row=2, column=0, padx=5, pady=10)

        self.btn_reduce_total = ttk.Button(
            self.frame_ops,
            text="Reducción total",
            command=self._on_force_reduce,
            state="disabled",
        )
        self.btn_reduce_total.grid(row=2, column=1, padx=5, pady=10)

        # Canvas
        self.canvas = tk.Canvas(
            self,
            width=800,
            height=320,
            bg="white",
            highlightthickness=1,
            highlightbackground="#cccccc",
        )
        self.canvas.bind("<Configure>", lambda e: self._draw_table())

        # Estado / log
        self.label_estado = ttk.Label(self, text="Tabla no inicializada.")
        self.label_log = ttk.Label(
            self,
            text="",
            foreground="blue",
            wraplength=780,
            justify="left",
        )


    def _configure_layout(self) -> None:
        # Título
        self.label_title.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))

        # Configuración de tabla
        self.frame_config.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        # Operaciones
        self.frame_ops.grid(row=2, column=0, sticky="ew", padx=10, pady=5)

        # Canvas
        self.canvas.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)

        # Estado y log
        self.label_estado.grid(row=4, column=0, sticky="w", padx=10, pady=(0, 5))
        self.label_log.grid(row=5, column=0, sticky="w", padx=10, pady=(0, 10))

        # Botón volver centrado abajo
        self.btn_back.grid(row=99, column=0, pady=20)

        # Expansión del canvas
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)
        # La fila 99 (botón volver) no se estira
        self.rowconfigure(99, weight=0)


    # ------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------
    def _on_init_table(self) -> None:
        try:
            num_cubetas = int(self.entry_cubetas.get())
            tam_cubeta = int(self.entry_tam.get())
            densidad_pct = float(self.entry_dens.get())
            densidad_obj = densidad_pct / 100.0
        except ValueError:
            self.label_log.config(text="Parámetros inválidos. Usa enteros para cubetas/tamaño y número para densidad.")
            return

        if num_cubetas <= 0 or tam_cubeta <= 0 or densidad_obj <= 0 or densidad_obj > 1:
            self.label_log.config(
                text="Verifica que: cubetas > 0, tamaño > 0 y 0 < densidad ≤ 100."
            )
            return

        self.hash_table = HashTableTotales(num_cubetas, tam_cubeta, densidad_obj)
        self._update_estado()
        self._draw_table()

        self.btn_insert.config(state="normal")
        self.btn_delete.config(state="normal")
        self.btn_expand_total.config(state="normal")
        self.btn_reduce_total.config(state="normal")

        self.label_log.config(text="Tabla inicializada correctamente.")

    def _on_insert(self) -> None:
        if not self.hash_table:
            return

        try:
            clave = int(self.entry_insert.get())
        except ValueError:
            self.label_log.config(text="La clave a insertar debe ser un entero.")
            return

        msg = self.hash_table.insertar(clave)
        self._update_estado()
        self._draw_table()
        self.label_log.config(text=msg)

    def _on_delete(self) -> None:
        if not self.hash_table:
            return

        try:
            clave = int(self.entry_delete.get())
        except ValueError:
            self.label_log.config(text="La clave a eliminar debe ser un entero.")
            return

        msg = self.hash_table.eliminar(clave)
        self._update_estado()
        self._draw_table()
        self.label_log.config(text=msg)

    def _on_force_expand(self) -> None:
        if not self.hash_table:
            return
        # Forzamos una expansión total manual
        self.hash_table._expansion_total()
        self._update_estado()
        self._draw_table()
        self.label_log.config(
            text=f"Expansión TOTAL forzada. Ahora hay {self.hash_table.num_cubetas} cubetas."
        )

    def _on_force_reduce(self) -> None:
        if not self.hash_table:
            return
        msg = self.hash_table.reduccion_total()
        self._update_estado()
        self._draw_table()
        self.label_log.config(text=msg)

    # ------------------------------------------------------------
    # Helpers UI
    # ------------------------------------------------------------
    def _update_estado(self) -> None:
        if not self.hash_table:
            self.label_estado.config(text="Tabla no inicializada.")
            return

        ht = self.hash_table
        self.label_estado.config(
            text=(
                f"Cubetas: {ht.num_cubetas} | "
                f"Tamaño cubeta: {ht.tam_cubeta} | "
                f"Capacidad total: {ht.capacidad_total} | "
                f"Registros: {ht.total_registros} | "
                f"Densidad actual: {ht.densidad_actual:.2f} "
                f"(objetivo: {ht.densidad_objetivo:.2f})"
            )
        )

    def _draw_table(self) -> None:
        self.canvas.delete("all")
        if not self.hash_table:
            return

        ht = self.hash_table
        num_buckets = ht.num_cubetas
        tam = ht.tam_cubeta

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width <= 0:
            width = 800
        if height <= 0:
            height = 320

        bucket_w = self.BUCKET_WIDTH
        cell_h = self.CELL_HEIGHT
        margin = self.MARGIN

        # ¿Cuántas cubetas caben por fila?
        cubetas_por_fila = max(1, (width - 2 * margin) // (bucket_w + margin))
        if cubetas_por_fila <= 0:
            cubetas_por_fila = 1

        for b_idx in range(num_buckets):
            fila = b_idx // cubetas_por_fila
            col = b_idx % cubetas_por_fila

            x0 = margin + col * (bucket_w + margin)
            y0 = margin + fila * (cell_h * (tam + 1) + 2 * margin)

            # Marco principal de la cubeta
            self.canvas.create_rectangle(
                x0,
                y0,
                x0 + bucket_w,
                y0 + cell_h * (tam + 1),
                outline="#333333",
                width=1,
            )

            # Header con índice de cubeta
            self.canvas.create_rectangle(
                x0,
                y0,
                x0 + bucket_w,
                y0 + cell_h,
                fill="#e0e0e0",
                outline="#333333",
            )
            self.canvas.create_text(
                x0 + bucket_w / 2,
                y0 + cell_h / 2,
                text=f"b{b_idx}",
                font=("TkDefaultFont", 9, "bold"),
            )

            # Celdas internas (área principal)
            bucket = ht.buckets[b_idx]
            for i in range(tam):
                cy0 = y0 + cell_h * (i + 1)
                cy1 = cy0 + cell_h

                self.canvas.create_rectangle(
                    x0,
                    cy0,
                    x0 + bucket_w,
                    cy1,
                    outline="#999999",
                )

                val = bucket[i]
                if val is not None:
                    self.canvas.create_text(
                        x0 + bucket_w / 2,
                        cy0 + cell_h / 2,
                        text=str(val),
                        font=("TkDefaultFont", 9),
                    )

            # --- Dibujar OVERFLOW debajo de la cubeta ---
            overflow_vals = ht.overflow[b_idx]
            if overflow_vals:
                base_y = y0 + cell_h * (tam + 1) + 4  # un poquito debajo de la cubeta

                # Pequeño título "overflow"
                self.canvas.create_text(
                    x0 + bucket_w / 2,
                    base_y,
                    text="overflow",
                    font=("TkDefaultFont", 7, "italic"),
                    fill="#555555",
                )

                # Cada registro del overflow como un cuadro debajo
                for j, val in enumerate(overflow_vals):
                    oy0 = base_y + 2 + j * cell_h
                    oy1 = oy0 + cell_h
                    self.canvas.create_rectangle(
                        x0,
                        oy0,
                        x0 + bucket_w,
                        oy1,
                        outline="#cc0000",
                    )
                    self.canvas.create_text(
                        x0 + bucket_w / 2,
                        (oy0 + oy1) / 2,
                        text=str(val),
                        font=("TkDefaultFont", 9),
                        fill="#cc0000",
                    )

