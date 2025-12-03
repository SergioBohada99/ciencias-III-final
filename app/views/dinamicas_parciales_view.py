# app/views/dinamicas_parciales_view.py

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import List, Optional
from tkinter import messagebox, filedialog
import json



class HashTableParciales:
    """
    Tabla hash basada en cubetas, con expansiones y reducciones PARCIALES.

    Expansión parcial:
        - Se dispara cuando densidad_actual >= densidad_objetivo
        - Aumenta el número de cubetas en 1: N -> N + 1
        - Reubica todos los registros recalculando el módulo.

    Reducción parcial:
        - Forzada por botón
        - Disminuye el número de cubetas en 1: N -> N - 1
        - Nunca baja del número inicial de cubetas.
    """

    def __init__(self, num_cubetas: int, tam_cubeta: int, densidad_objetivo: float) -> None:
        self.num_cubetas_inicial = max(1, num_cubetas)
        self.num_cubetas = max(1, num_cubetas)
        self.tam_cubeta = max(1, tam_cubeta)
        self.densidad_objetivo = densidad_objetivo

        self.buckets: list[list[int | None]] = [
            [None] * self.tam_cubeta for _ in range(self.num_cubetas)
        ]
        self.overflow: list[list[int]] = [[] for _ in range(self.num_cubetas)]
        self.total_registros: int = 0

        # 🔹 Estado para el ciclo de expansiones parciales
        self._partial_cycle_base: int | None = self.num_cubetas
        self._partial_cycle_steps: int = 0
        # 🔹 Nuevo: orden en que se insertaron las claves
        self.insertion_order: list[int] = []

    # ------------------------------------------------------------
    @property
    def capacidad_total(self) -> int:
        return self.num_cubetas * self.tam_cubeta

    @property
    def densidad_actual(self) -> float:
        if self.capacidad_total == 0:
            return 0.0
        return self.total_registros / self.capacidad_total

    # ------------------------------------------------------------
    # Operaciones
    # ------------------------------------------------------------
    
    def _existe_clave(self, clave: int) -> bool:
        """Retorna True si la clave ya está en la tabla (cubeta u overflow)."""
        return clave in self.insertion_order

    def insertar(self, clave: int) -> str:
        # verificar duplicados
        if self._existe_clave(clave):
            messagebox.showwarning(
                "Clave duplicada",
                f"La clave {clave} ya se encuentra almacenada en la tabla."
            )
            return f"La clave {clave} ya se encuentra almacenada. No se permiten duplicados."

        ok, msg = self._insertar_en_cubeta_o_expandir_parcial(clave)

        if not ok:
            return msg  # caso extremo

        if self.densidad_actual >= self.densidad_objetivo:
            msg += (
                f" | Densidad actual {self.densidad_actual:.2f} ≥ objetivo "
                f"{self.densidad_objetivo:.2f}, se realiza expansión PARCIAL."
            )
            self._expansion_parcial()
        else:
            msg += f" | Densidad actual {self.densidad_actual:.2f}, no se requiere expansión."

        return msg
    
    def _remove_from_insertion_order(self, clave: int) -> None:
        try:
            self.insertion_order.remove(clave)
        except ValueError:
            # Por si acaso no está; no queremos que explote la app docente
            pass

    # ------------------------------------------------------------
    # Serialización para guardar/cargar
    # ------------------------------------------------------------
    def to_dict(self) -> dict:
        return {
            "tipo": "parciales",
            "num_cubetas_inicial": self.num_cubetas_inicial,
            "num_cubetas": self.num_cubetas,
            "tam_cubeta": self.tam_cubeta,
            "densidad_objetivo": self.densidad_objetivo,
            "buckets": self.buckets,
            "overflow": self.overflow,
            "insertion_order": self.insertion_order,
            # si usas ciclo parcial:
            "_partial_cycle_base": getattr(self, "_partial_cycle_base", None),
            "_partial_cycle_steps": getattr(self, "_partial_cycle_steps", 0),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "HashTableParciales":
        num_cubetas = data["num_cubetas"]
        tam_cubeta = data["tam_cubeta"]
        densidad_objetivo = data["densidad_objetivo"]

        obj = cls(num_cubetas=num_cubetas, tam_cubeta=tam_cubeta, densidad_objetivo=densidad_objetivo)
        obj.num_cubetas_inicial = data.get("num_cubetas_inicial", num_cubetas)
        obj.buckets = data["buckets"]
        obj.overflow = data["overflow"]
        obj.insertion_order = data.get("insertion_order", [])

        obj.total_registros = 0
        for b in range(obj.num_cubetas):
            for v in obj.buckets[b]:
                if v is not None:
                    obj.total_registros += 1
            obj.total_registros += len(obj.overflow[b])

        obj._partial_cycle_base = data.get("_partial_cycle_base", obj.num_cubetas)
        obj._partial_cycle_steps = data.get("_partial_cycle_steps", 0)

        return obj

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
        """
        if self.capacidad_total == 0:
            return base_msg

        umbral_baja = 1.0 - self.densidad_objetivo

        if self.densidad_actual <= umbral_baja:
            reduccion_msg = self.reduccion_parcial()
            return (
                base_msg
                + f" | Densidad actual ≤ {umbral_baja:.2f}, se intenta REDUCCIÓN PARCIAL. "
                + reduccion_msg
            )

        return base_msg


    # ------------------------------------------------------------
    # Internos
    # ------------------------------------------------------------
    def _insertar_en_cubeta_o_expandir_parcial(self, clave: int) -> tuple[bool, str]:
        """
        Intenta insertar la clave en la cubeta correspondiente.
        Si la cubeta está llena, la clave se coloca en el OVERFLOW de esa cubeta.
        Aquí **no** se realizan expansiones; eso se hace en `insertar` según la densidad.

        Devuelve (ok, mensaje).
        """
        bucket_idx = clave % self.num_cubetas
        bucket = self.buckets[bucket_idx]

        # 1) Intentar en área principal de la cubeta
        for i in range(self.tam_cubeta):
            if bucket[i] is None:
                bucket[i] = clave
                self.total_registros += 1
                # Registrar orden de inserción
                self.insertion_order.append(clave)
                return True, (
                    f"Registro {clave} insertado en cubeta {bucket_idx}, posición {i} "
                    f"(clave % {self.num_cubetas} = {bucket_idx})."
                )

        # 2) Cubeta llena → insertar en overflow de esa cubeta
        self.overflow[bucket_idx].append(clave)
        self.total_registros += 1
        self.insertion_order.append(clave)

        msg = (
            f"Cubeta {bucket_idx} llena al insertar {clave}, "
            f"registro colocado en OVERFLOW de la cubeta {bucket_idx}."
        )
        return True, msg


    def _expansion_parcial(self) -> None:
        """
        Expansión PARCIAL con la regla:
        - Dos expansiones parciales equivalen a una expansión total.

        Si N es el número de cubetas al inicio del ciclo:
        1ª parcial: num_cubetas = N + N//2
        2ª parcial: num_cubetas = 2 * N

        En cada expansión parcial se rehashean TODOS los registros
        usando el nuevo número de cubetas. Por eso, después de la
        segunda parcial, el estado es equivalente a haber hecho
        directamente una expansión total desde N a 2N.
        """
        # N al inicio del ciclo de parciales
        if self._partial_cycle_base is None:
            self._partial_cycle_base = self.num_cubetas

        base = self._partial_cycle_base

        if self._partial_cycle_steps == 0:
            # Primera expansión parcial del ciclo: N -> N + N//2
            incremento = max(1, base // 2)
            nuevas_cubetas = base + incremento
            self._partial_cycle_steps = 1
        else:
            # Segunda expansión parcial del ciclo: -> 2 * N
            nuevas_cubetas = max(self.num_cubetas, base * 2)
            # Ciclo completo, reseteamos
            self._partial_cycle_steps = 0
            self._partial_cycle_base = nuevas_cubetas  # nuevo N base para próximos ciclos

        # Reconstituir tabla con el nuevo número de cubetas
        valores = self._extraer_todos_los_valores()
        self.num_cubetas = nuevas_cubetas

        self.buckets = [[None] * self.tam_cubeta for _ in range(self.num_cubetas)]
        self.overflow = [[] for _ in range(self.num_cubetas)]
        self.total_registros = 0

        for v in valores:
            self._insertar_sin_expandir(v)


    def reduccion_parcial(self) -> str:
        if self.num_cubetas <= self.num_cubetas_inicial:
            return "No se puede reducir más, ya se alcanzó el número mínimo de cubetas."

        nuevas_cubetas = max(self.num_cubetas_inicial, self.num_cubetas - 1)
        if nuevas_cubetas == self.num_cubetas:
            return "El número de cubetas ya es el mínimo permitido."

        valores = self._extraer_todos_los_valores()
        self.num_cubetas = nuevas_cubetas

        self.buckets = [[None] * self.tam_cubeta for _ in range(self.num_cubetas)]
        self.overflow = [[] for _ in range(self.num_cubetas)]
        self.total_registros = 0

        for v in valores:
            self._insertar_sin_expandir(v)

        # 🔹 Reiniciamos ciclo parcial
        self._partial_cycle_base = self.num_cubetas
        self._partial_cycle_steps = 0

        return (
            f"Reducción PARCIAL realizada: ahora hay {self.num_cubetas} cubetas. "
            f"Densidad actual: {self.densidad_actual:.2f}"
        )


    def _extraer_todos_los_valores(self) -> list[int]:
        return list(self.insertion_order)

    def _insertar_sin_expandir(self, clave: int) -> None:
        bucket_idx = clave % self.num_cubetas
        bucket = self.buckets[bucket_idx]
        for i in range(self.tam_cubeta):
            if bucket[i] is None:
                bucket[i] = clave
                self.total_registros += 1
                return


class DinamicasParcialesView(ttk.Frame):
    """
    Vista para manejar y visualizar cubetas con expansiones / reducciones PARCIALES.
    """

    BUCKET_WIDTH = 70
    CELL_HEIGHT = 26
    MARGIN = 10

    def __init__(self, parent: tk.Widget, app) -> None:
        super().__init__(parent)
        self.app = app

        self.hash_table: Optional[HashTableParciales] = None

        self._build_widgets()
        self._configure_layout()

    # ------------------------------------------------------------
    def _build_widgets(self) -> None:
        # Título
        self.label_title = ttk.Label(
            self,
            text="Dinámicas de Hash – Expansiones y Reducciones Parciales",
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
        self.frame_config = ttk.LabelFrame(self, text="Configuración de la estructura", padding=10)

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
            text="Inicializar estructura",
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
            text="Expansión parcial",
            command=self._on_force_expand,
            state="disabled",
        )
        self.btn_expand_total.grid(row=2, column=0, padx=5, pady=10)

        self.btn_reduce_total = ttk.Button(
            self.frame_ops,
            text="Reducción parcial",
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

        # === BOTONES INFERIORES (Guardar / Cargar) ===
        self.frame_bottom_buttons = ttk.Frame(self, padding=10)

        self.btn_save_close = ttk.Button(
            self.frame_bottom_buttons,
            text="Guardar y cerrar",
            command=self._on_save_and_close,
            state="disabled",
        )

        self.btn_save = ttk.Button(
            self.frame_bottom_buttons,
            text="Guardar",
            command=self._on_save,
            state="disabled",
        )

        self.btn_load = ttk.Button(
            self.frame_bottom_buttons,
            text="Cargar",
            command=self._on_load,
        )


        # Estado / log
        self.label_estado = ttk.Label(self, text="Estructura no inicializada.")
        self.label_log = ttk.Label(
            self,
            text="",
            foreground="blue",
            wraplength=780,
            justify="left",
        )

        # Botones inferiores (Guardar / Cargar)
        self.frame_bottom_buttons.grid(row=6, column=0, pady=10, sticky="w")

        # Ubicar botones centrados en el frame
        self.btn_save_close.grid(row=0, column=0, padx=10)
        self.btn_save.grid(row=0, column=1, padx=10)
        self.btn_load.grid(row=0, column=2, padx=10)


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
    # Guardar / Cargar
    # ------------------------------------------------------------
    def _on_save(self) -> None:
        if not self.hash_table:
            messagebox.showwarning("Guardar tabla", "Primero inicializa la tabla para poder guardarla.")
            return

        filename = filedialog.asksaveasfilename(
            title="Guardar tabla de dinámicas parciales",
            defaultextension=".json",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")],
        )
        if not filename:
            return  # usuario canceló

        try:
            data = self.hash_table.to_dict()
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Guardar tabla", f"Tabla guardada correctamente en:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error al guardar", f"No se pudo guardar la tabla:\n{e}")

    def _on_save_and_close(self) -> None:
        """
        Guarda la tabla y luego vuelve a la vista anterior (externas).
        """
        if not self.hash_table:
            messagebox.showwarning("Guardar tabla", "Primero inicializa la tabla para poder guardarla.")
            return

        filename = filedialog.asksaveasfilename(
            title="Guardar tabla de dinámicas parciales",
            defaultextension=".json",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")],
        )
        if not filename:
            return  # usuario canceló

        try:
            data = self.hash_table.to_dict()
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Guardar tabla", f"Tabla guardada correctamente en:\n{filename}")
            # Cerrar (volver) tras guardar
            self.app.navigate("externas")
        except Exception as e:
            messagebox.showerror("Error al guardar", f"No se pudo guardar la tabla:\n{e}")

    def _on_load(self) -> None:
        """
        Carga una tabla previamente guardada desde un archivo JSON.
        """
        filename = filedialog.askopenfilename(
            title="Cargar tabla de dinámicas parciales",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")],
        )
        if not filename:
            return

        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Verificación mínima de tipo
            if data.get("tipo") not in (None, "parciales"):
                messagebox.showwarning(
                    "Cargar tabla",
                    "El archivo no parece corresponder a una tabla de dinámicas parciales.",
                )

            self.hash_table = HashTableParciales.from_dict(data)

            # Actualizar controles de configuración con los valores cargados
            self.entry_cubetas.delete(0, tk.END)
            self.entry_cubetas.insert(0, str(self.hash_table.num_cubetas))

            self.entry_tam.delete(0, tk.END)
            self.entry_tam.insert(0, str(self.hash_table.tam_cubeta))

            self.entry_dens.delete(0, tk.END)
            self.entry_dens.insert(0, str(int(self.hash_table.densidad_objetivo * 100)))

            # Habilitar botones
            self.btn_insert.config(state="normal")
            self.btn_delete.config(state="normal")
            self.btn_expand_total.config(state="normal")
            self.btn_reduce_total.config(state="normal")
            self.btn_save.config(state="normal")
            self.btn_save_close.config(state="normal")

            self._update_estado()
            self._draw_table()
            messagebox.showinfo("Cargar tabla", f"Tabla cargada correctamente desde:\n{filename}")

        except Exception as e:
            messagebox.showerror("Error al cargar", f"No se pudo cargar la tabla:\n{e}")



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

        self.hash_table = HashTableParciales(num_cubetas, tam_cubeta, densidad_obj)
        self._update_estado()
        self._draw_table()

        self.btn_insert.config(state="normal")
        self.btn_delete.config(state="normal")
        self.btn_expand_total.config(state="normal")
        self.btn_reduce_total.config(state="normal")
        # 🔹 habilitar guardar / guardar y cerrar
        self.btn_save.config(state="normal")
        self.btn_save_close.config(state="normal")

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
        self.hash_table._expansion_parcial()
        self._update_estado()
        self._draw_table()
        self.label_log.config(
            text=f"Expansión PARCIAL forzada. Ahora hay {self.hash_table.num_cubetas} cubetas."
        )

    def _on_force_reduce(self) -> None:
        if not self.hash_table:
            return
        msg = self.hash_table.reduccion_parcial()
        self._update_estado()
        self._draw_table()
        self.label_log.config(text=msg)

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

        cubetas_por_fila = max(1, (width - 2 * margin) // (bucket_w + margin))
        if cubetas_por_fila <= 0:
            cubetas_por_fila = 1

        for b_idx in range(num_buckets):
            fila = b_idx // cubetas_por_fila
            col = b_idx % cubetas_por_fila

            x0 = margin + col * (bucket_w + margin)
            # algo de espacio vertical entre filas de cubetas
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

            # Celdas principales de la cubeta
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

