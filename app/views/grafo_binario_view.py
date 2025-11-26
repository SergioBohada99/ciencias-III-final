import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Set, Tuple, Optional
import math
import random


class GrafoBinarioView(ttk.Frame):
	def __init__(self, parent: tk.Misc, app) -> None:
		super().__init__(parent)
		
		title = ttk.Label(self, text="Operaciones con Dos Grafos (No Dirigidos)", style="Title.TLabel")
		title.pack(pady=(20, 5))
		
		# Panel principal con tres columnas: G1, G2, Resultado
		main_panel = ttk.Frame(self, padding=6)
		main_panel.pack(fill=tk.BOTH, expand=True)
		
		# Panel izquierdo: Grafo 1
		left_panel = ttk.Frame(main_panel, style="Panel.TFrame", padding=10)
		left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 3))
		
		lbl_g1 = ttk.Label(left_panel, text="Grafo G₁", font=("MS Sans Serif", 11, "bold"))
		lbl_g1.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="w")
		
		# Sección: Agregar elementos G1
		lbl_add = ttk.Label(left_panel, text="Agregar Elementos", font=("MS Sans Serif", 9, "bold"))
		lbl_add.grid(row=1, column=0, columnspan=2, pady=(0, 5), sticky="w")
		
		ttk.Label(left_panel, text="Vértice:").grid(row=2, column=0, sticky="w", pady=2)
		self.entry_vertice_g1 = ttk.Entry(left_panel, width=12)
		self.entry_vertice_g1.grid(row=2, column=1, pady=2)
		
		btn_add_vertice_g1 = ttk.Button(left_panel, text="Agregar vértice", command=lambda: self._on_agregar_vertice(1), style="Retro.TButton")
		btn_add_vertice_g1.grid(row=3, column=0, columnspan=2, pady=2, sticky="ew")
		
		ttk.Label(left_panel, text="Letra arista:").grid(row=4, column=0, sticky="w", pady=2)
		self.entry_arista_letra_g1 = ttk.Entry(left_panel, width=12)
		self.entry_arista_letra_g1.grid(row=4, column=1, pady=2)
		
		ttk.Label(left_panel, text="Arista (u,v):").grid(row=5, column=0, sticky="w", pady=2)
		frame_arista_g1 = ttk.Frame(left_panel)
		frame_arista_g1.grid(row=5, column=1, pady=2)
		self.entry_u_g1 = ttk.Entry(frame_arista_g1, width=5)
		self.entry_u_g1.pack(side=tk.LEFT)
		ttk.Label(frame_arista_g1, text=",").pack(side=tk.LEFT, padx=1)
		self.entry_v_g1 = ttk.Entry(frame_arista_g1, width=5)
		self.entry_v_g1.pack(side=tk.LEFT)
		
		btn_add_arista_g1 = ttk.Button(left_panel, text="Agregar arista", command=lambda: self._on_agregar_arista(1), style="Retro.TButton")
		btn_add_arista_g1.grid(row=6, column=0, columnspan=2, pady=2, sticky="ew")
		
		btn_limpiar_g1 = ttk.Button(left_panel, text="Limpiar G₁", command=lambda: self._on_limpiar(1))
		btn_limpiar_g1.grid(row=7, column=0, columnspan=2, pady=(5, 2), sticky="ew")
		
		# Canvas pequeño para G1
		self.canvas_g1 = tk.Canvas(left_panel, background="#ffffff", width=200, height=150)
		self.canvas_g1.grid(row=8, column=0, columnspan=2, pady=(5, 0))
		
		# Panel central: Grafo 2
		center_panel = ttk.Frame(main_panel, style="Panel.TFrame", padding=10)
		center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=3)
		
		lbl_g2 = ttk.Label(center_panel, text="Grafo G₂", font=("MS Sans Serif", 11, "bold"))
		lbl_g2.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="w")
		
		# Sección: Agregar elementos G2
		lbl_add_g2 = ttk.Label(center_panel, text="Agregar Elementos", font=("MS Sans Serif", 9, "bold"))
		lbl_add_g2.grid(row=1, column=0, columnspan=2, pady=(0, 5), sticky="w")
		
		ttk.Label(center_panel, text="Vértice:").grid(row=2, column=0, sticky="w", pady=2)
		self.entry_vertice_g2 = ttk.Entry(center_panel, width=12)
		self.entry_vertice_g2.grid(row=2, column=1, pady=2)
		
		btn_add_vertice_g2 = ttk.Button(center_panel, text="Agregar vértice", command=lambda: self._on_agregar_vertice(2), style="Retro.TButton")
		btn_add_vertice_g2.grid(row=3, column=0, columnspan=2, pady=2, sticky="ew")
		
		ttk.Label(center_panel, text="Letra arista:").grid(row=4, column=0, sticky="w", pady=2)
		self.entry_arista_letra_g2 = ttk.Entry(center_panel, width=12)
		self.entry_arista_letra_g2.grid(row=4, column=1, pady=2)
		
		ttk.Label(center_panel, text="Arista (u,v):").grid(row=5, column=0, sticky="w", pady=2)
		frame_arista_g2 = ttk.Frame(center_panel)
		frame_arista_g2.grid(row=5, column=1, pady=2)
		self.entry_u_g2 = ttk.Entry(frame_arista_g2, width=5)
		self.entry_u_g2.pack(side=tk.LEFT)
		ttk.Label(frame_arista_g2, text=",").pack(side=tk.LEFT, padx=1)
		self.entry_v_g2 = ttk.Entry(frame_arista_g2, width=5)
		self.entry_v_g2.pack(side=tk.LEFT)
		
		btn_add_arista_g2 = ttk.Button(center_panel, text="Agregar arista", command=lambda: self._on_agregar_arista(2), style="Retro.TButton")
		btn_add_arista_g2.grid(row=6, column=0, columnspan=2, pady=2, sticky="ew")
		
		btn_limpiar_g2 = ttk.Button(center_panel, text="Limpiar G₂", command=lambda: self._on_limpiar(2))
		btn_limpiar_g2.grid(row=7, column=0, columnspan=2, pady=(5, 2), sticky="ew")
		
		# Canvas pequeño para G2
		self.canvas_g2 = tk.Canvas(center_panel, background="#ffffff", width=200, height=150)
		self.canvas_g2.grid(row=8, column=0, columnspan=2, pady=(5, 0))
		
		# Panel derecho: Operaciones y Resultado
		right_panel = ttk.Frame(main_panel, style="Panel.TFrame", padding=10)
		right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(3, 0))
		
		lbl_ops = ttk.Label(right_panel, text="Operaciones", font=("MS Sans Serif", 11, "bold"))
		lbl_ops.grid(row=0, column=0, pady=(0, 10), sticky="w")
		
		# Botones de operaciones
		btn_union = ttk.Button(right_panel, text="Unión (G₁ ∪ G₂)", command=self._on_union, style="Retro.TButton")
		btn_union.grid(row=1, column=0, pady=2, sticky="ew")
		
		btn_interseccion = ttk.Button(right_panel, text="Intersección (G₁ ∩ G₂)", command=self._on_interseccion, style="Retro.TButton")
		btn_interseccion.grid(row=2, column=0, pady=2, sticky="ew")
		
		btn_suma_anillo = ttk.Button(right_panel, text="Suma Anillo (G₁ ⊕ G₂)", command=self._on_suma_anillo, style="Retro.TButton")
		btn_suma_anillo.grid(row=3, column=0, pady=2, sticky="ew")
		
		ttk.Separator(right_panel, orient="horizontal").grid(row=4, column=0, pady=10, sticky="ew")
		
		btn_cartesiano = ttk.Button(right_panel, text="Producto Cartesiano (G₁ × G₂)", command=self._on_cartesiano, style="Retro.TButton")
		btn_cartesiano.grid(row=5, column=0, pady=2, sticky="ew")
		
		btn_tensorial = ttk.Button(right_panel, text="Producto Tensorial (G₁ ⊗ G₂)", command=self._on_tensorial, style="Retro.TButton")
		btn_tensorial.grid(row=6, column=0, pady=2, sticky="ew")
		
		btn_composicion = ttk.Button(right_panel, text="Composición (G₁[G₂])", command=self._on_composicion, style="Retro.TButton")
		btn_composicion.grid(row=7, column=0, pady=2, sticky="ew")
		
		# Estado
		self.status = ttk.Label(right_panel, text="Define G₁ y G₂", wraplength=200)
		self.status.grid(row=8, column=0, pady=(10, 0))
		
		# Canvas para resultado
		lbl_resultado = ttk.Label(right_panel, text="Resultado", font=("MS Sans Serif", 10, "bold"))
		lbl_resultado.grid(row=9, column=0, pady=(10, 5), sticky="w")
		
		self.canvas_resultado = tk.Canvas(right_panel, background="#ffffff", width=300, height=300)
		self.canvas_resultado.grid(row=10, column=0, pady=(0, 0))
		
		# Botón volver
		back = ttk.Button(self, text="← Volver", command=lambda: app.navigate("grafos"))
		back.pack(pady=6)
		
		self.app = app
		
		# Estructuras de datos para G1 y G2
		self.vertices_g1: Set[str] = set()
		self.aristas_g1: Dict[str, Dict[str, str]] = {}
		self.posiciones_g1: Dict[str, Tuple[float, float]] = {}
		
		self.vertices_g2: Set[str] = set()
		self.aristas_g2: Dict[str, Dict[str, str]] = {}
		self.posiciones_g2: Dict[str, Tuple[float, float]] = {}
		
		# Grafo resultado
		self.vertices_resultado: Set[str] = set()
		self.aristas_resultado: Dict[str, Dict[str, str]] = {}
		self.posiciones_resultado: Dict[str, Tuple[float, float]] = {}
		self.operacion_actual: Optional[str] = None
	
	def _on_agregar_vertice(self, grafo: int) -> None:
		"""Agrega un vértice al grafo especificado (1 o 2)"""
		if grafo == 1:
			vertice = self.entry_vertice_g1.get().strip()
			entry = self.entry_vertice_g1
			vertices = self.vertices_g1
		else:
			vertice = self.entry_vertice_g2.get().strip()
			entry = self.entry_vertice_g2
			vertices = self.vertices_g2
		
		if not vertice:
			messagebox.showerror("Error", "Ingresa un número para el vértice")
			return
		
		try:
			int(vertice)
		except ValueError:
			messagebox.showerror("Error", "El vértice debe ser un número simple")
			return
		
		if vertice in vertices:
			messagebox.showwarning("Advertencia", f"El vértice {vertice} ya existe en G{grafo}")
			return
		
		vertices.add(vertice)
		entry.delete(0, tk.END)
		self._draw_grafo(grafo)
	
	def _on_agregar_arista(self, grafo: int) -> None:
		"""Agrega una arista al grafo especificado (1 o 2)"""
		if grafo == 1:
			arista_letra = self.entry_arista_letra_g1.get().strip()
			u = self.entry_u_g1.get().strip()
			v = self.entry_v_g1.get().strip()
			entry_letra = self.entry_arista_letra_g1
			entry_u = self.entry_u_g1
			entry_v = self.entry_v_g1
			vertices = self.vertices_g1
			aristas = self.aristas_g1
		else:
			arista_letra = self.entry_arista_letra_g2.get().strip()
			u = self.entry_u_g2.get().strip()
			v = self.entry_v_g2.get().strip()
			entry_letra = self.entry_arista_letra_g2
			entry_u = self.entry_u_g2
			entry_v = self.entry_v_g2
			vertices = self.vertices_g2
			aristas = self.aristas_g2
		
		if not arista_letra or not u or not v:
			messagebox.showerror("Error", "Ingresa la letra de la arista y ambos vértices")
			return
		
		if not arista_letra.isalpha():
			messagebox.showerror("Error", "La arista debe ser una o más letras")
			return
		
		# Validar que la letra no exista ya en el grafo correspondiente
		if arista_letra in aristas:
			messagebox.showwarning("Advertencia", f"La arista '{arista_letra}' ya existe en G{grafo}")
			return
		
		if u not in vertices or v not in vertices:
			messagebox.showerror("Error", f"Ambos vértices deben existir en G{grafo}")
			return
		
		aristas[arista_letra] = {'u': u, 'v': v}
		
		entry_letra.delete(0, tk.END)
		entry_u.delete(0, tk.END)
		entry_v.delete(0, tk.END)
		self._draw_grafo(grafo)
	
	def _on_limpiar(self, grafo: int) -> None:
		"""Limpia el grafo especificado"""
		if grafo == 1:
			self.vertices_g1 = set()
			self.aristas_g1 = {}
			self.posiciones_g1 = {}
			self._draw_grafo(1)
		else:
			self.vertices_g2 = set()
			self.aristas_g2 = {}
			self.posiciones_g2 = {}
			self._draw_grafo(2)
	
	def _draw_grafo(self, grafo: int) -> None:
		"""Dibuja el grafo especificado en su canvas correspondiente"""
		if grafo == 1:
			canvas = self.canvas_g1
			vertices = self.vertices_g1
			aristas = self.aristas_g1
			posiciones = self.posiciones_g1
		else:
			canvas = self.canvas_g2
			vertices = self.vertices_g2
			aristas = self.aristas_g2
			posiciones = self.posiciones_g2
		
		canvas.delete("all")
		
		if not vertices:
			canvas.create_text(
				100, 75,
				text=f"G{grafo} vacío",
				fill="#999999", font=("MS Sans Serif", 10)
			)
			return
		
		self._calcular_posiciones_pequeno(vertices, posiciones, canvas)
		
		# Dibujar aristas
		for arista_id, datos in aristas.items():
			u, v = datos['u'], datos['v']
			if u not in posiciones or v not in posiciones:
				continue
			
			x1, y1 = posiciones[u]
			x2, y2 = posiciones[v]
			
			if u == v:
				# Bucle
				self._draw_loop_pequeno(canvas, x1, y1, arista_id)
			else:
				# Línea recta
				canvas.create_line(x1, y1, x2, y2, fill="#000000", width=1.5)
				mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
				canvas.create_rectangle(mid_x - 8, mid_y - 8, mid_x + 8, mid_y + 8, fill="#ffffff", outline="")
				canvas.create_text(mid_x, mid_y, text=arista_id, fill="#000000", font=("MS Sans Serif", 8))
		
		# Dibujar vértices
		radius = 12
		for vertice, (x, y) in posiciones.items():
			canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill="#4da3ff", outline="#255eaa", width=1.5)
			canvas.create_text(x, y, text=str(vertice), fill="#ffffff", font=("MS Sans Serif", 9, "bold"))
	
	def _calcular_posiciones_pequeno(self, vertices: Set[str], posiciones: Dict[str, Tuple[float, float]], canvas: tk.Canvas) -> None:
		"""Calcula posiciones para grafos pequeños"""
		canvas.update_idletasks()
		width = max(canvas.winfo_width(), 200)
		height = max(canvas.winfo_height(), 150)
		
		vertices_list = list(vertices)
		n = len(vertices_list)
		
		# Inicializar posiciones si no existen
		for vertice in vertices_list:
			if vertice not in posiciones:
				angle = random.uniform(0, 2 * math.pi)
				radius = min(width, height) / 4
				posiciones[vertice] = (
					width / 2 + radius * math.cos(angle),
					height / 2 + radius * math.sin(angle)
				)
		
		# Layout circular simple
		if n > 0:
			center_x, center_y = width / 2, height / 2
			radius = min(width, height) / 3
			for i, vertice in enumerate(vertices_list):
				angle = 2 * math.pi * i / n - math.pi / 2
				posiciones[vertice] = (
					center_x + radius * math.cos(angle),
					center_y + radius * math.sin(angle)
				)
	
	def _draw_loop_pequeno(self, canvas: tk.Canvas, x: float, y: float, arista_id: str) -> None:
		"""Dibuja un bucle pequeño"""
		radius = 12
		loop_radius = 15
		loop_x = x
		loop_y = y - radius - loop_radius
		canvas.create_oval(loop_x - loop_radius, loop_y - loop_radius, loop_x + loop_radius, loop_y + loop_radius, outline="#000000", width=1.5, fill="")
		canvas.create_rectangle(loop_x - 8, loop_y - loop_radius - 12, loop_x + 8, loop_y - loop_radius - 4, fill="#ffffff", outline="")
		canvas.create_text(loop_x, loop_y - loop_radius - 8, text=arista_id, fill="#000000", font=("MS Sans Serif", 8))
	
	# ========== OPERACIONES DE GRAFOS ==========
	
	def _on_union(self) -> None:
		"""Unión: G1 ∪ G2 - une vértices y aristas de ambos grafos"""
		if not self.vertices_g1 and not self.vertices_g2:
			messagebox.showwarning("Advertencia", "Al menos uno de los grafos debe tener vértices")
			return
		
		self.vertices_resultado = self.vertices_g1 | self.vertices_g2
		self.aristas_resultado = {}
		self.posiciones_resultado = {}  # Limpiar posiciones anteriores
		
		# Agregar aristas de G1 con prefijo
		for arista_id, datos in self.aristas_g1.items():
			self.aristas_resultado[f"G1_{arista_id}"] = datos.copy()
		
		# Agregar aristas de G2 con prefijo
		for arista_id, datos in self.aristas_g2.items():
			self.aristas_resultado[f"G2_{arista_id}"] = datos.copy()
		
		self.operacion_actual = "Unión (G₁ ∪ G₂)"
		self.status.configure(text=self.operacion_actual)
		self._draw_resultado()
	
	def _on_interseccion(self) -> None:
		"""Intersección: G1 ∩ G2 - solo vértices y aristas comunes"""
		if not self.vertices_g1 or not self.vertices_g2:
			messagebox.showwarning("Advertencia", "Ambos grafos deben tener vértices")
			return
		
		self.vertices_resultado = self.vertices_g1 & self.vertices_g2
		self.aristas_resultado = {}
		self.posiciones_resultado = {}  # Limpiar posiciones anteriores
		
		# Solo aristas que existen en ambos grafos (mismos vértices)
		aristas_g1_set = set()
		for datos in self.aristas_g1.values():
			par = tuple(sorted([datos['u'], datos['v']]))
			aristas_g1_set.add(par)
		
		aristas_g2_set = set()
		for datos in self.aristas_g2.values():
			par = tuple(sorted([datos['u'], datos['v']]))
			aristas_g2_set.add(par)
		
		aristas_comunes = aristas_g1_set & aristas_g2_set
		
		# Agregar aristas comunes (usar las de G1)
		for arista_id, datos in self.aristas_g1.items():
			par = tuple(sorted([datos['u'], datos['v']]))
			if par in aristas_comunes:
				self.aristas_resultado[arista_id] = datos.copy()
		
		self.operacion_actual = "Intersección (G₁ ∩ G₂)"
		self.status.configure(text=self.operacion_actual)
		self._draw_resultado()
	
	def _on_suma_anillo(self) -> None:
		"""Suma anillo: G1 ⊕ G2 - unión menos intersección (solo elementos únicos)"""
		if not self.vertices_g1 and not self.vertices_g2:
			messagebox.showwarning("Advertencia", "Al menos uno de los grafos debe tener vértices")
			return
		
		self.vertices_resultado = self.vertices_g1 ^ self.vertices_g2  # XOR: solo en uno u otro
		self.aristas_resultado = {}
		self.posiciones_resultado = {}  # Limpiar posiciones anteriores
		
		# Aristas de G1 que no están en G2
		aristas_g2_set = set()
		for datos in self.aristas_g2.values():
			par = tuple(sorted([datos['u'], datos['v']]))
			aristas_g2_set.add(par)
		
		for arista_id, datos in self.aristas_g1.items():
			par = tuple(sorted([datos['u'], datos['v']]))
			if par not in aristas_g2_set:
				self.aristas_resultado[f"G1_{arista_id}"] = datos.copy()
		
		# Aristas de G2 que no están en G1
		aristas_g1_set = set()
		for datos in self.aristas_g1.values():
			par = tuple(sorted([datos['u'], datos['v']]))
			aristas_g1_set.add(par)
		
		for arista_id, datos in self.aristas_g2.items():
			par = tuple(sorted([datos['u'], datos['v']]))
			if par not in aristas_g1_set:
				self.aristas_resultado[f"G2_{arista_id}"] = datos.copy()
		
		self.operacion_actual = "Suma Anillo (G₁ ⊕ G₂)"
		self.status.configure(text=self.operacion_actual)
		self._draw_resultado()
	
	def _on_cartesiano(self) -> None:
		"""Producto cartesiano: G1 × G2"""
		if not self.vertices_g1 or not self.vertices_g2:
			messagebox.showwarning("Advertencia", "Ambos grafos deben tener vértices")
			return
		
		# Vértices: todos los pares (u1, u2) donde u1 ∈ G1 y u2 ∈ G2
		self.vertices_resultado = set()
		for u1 in self.vertices_g1:
			for u2 in self.vertices_g2:
				self.vertices_resultado.add(f"({u1},{u2})")
		
		self.aristas_resultado = {}
		self.posiciones_resultado = {}  # Limpiar posiciones anteriores
		arista_counter = 0
		
		# Aristas: (u1, u2) - (v1, v2) existe si:
		# 1. u1 = v1 y (u2, v2) es arista en G2, O
		# 2. u2 = v2 y (u1, v1) es arista en G1
		
		# Caso 1: u1 = v1, (u2, v2) en G2
		for u1 in self.vertices_g1:
			for arista_id, datos in self.aristas_g2.items():
				u2, v2 = datos['u'], datos['v']
				v1 = f"({u1},{u2})"
				v2_new = f"({u1},{v2})"
				if v1 in self.vertices_resultado and v2_new in self.vertices_resultado:
					self.aristas_resultado[f"c{arista_counter}"] = {'u': v1, 'v': v2_new}
					arista_counter += 1
		
		# Caso 2: u2 = v2, (u1, v1) en G1
		for u2 in self.vertices_g2:
			for arista_id, datos in self.aristas_g1.items():
				u1, v1 = datos['u'], datos['v']
				v1_new = f"({u1},{u2})"
				v2_new = f"({v1},{u2})"
				if v1_new in self.vertices_resultado and v2_new in self.vertices_resultado:
					self.aristas_resultado[f"c{arista_counter}"] = {'u': v1_new, 'v': v2_new}
					arista_counter += 1
		
		self.operacion_actual = "Producto Cartesiano (G₁ × G₂)"
		self.status.configure(text=self.operacion_actual)
		self._draw_resultado()
	
	def _on_tensorial(self) -> None:
		"""Producto tensorial: G1 ⊗ G2"""
		if not self.vertices_g1 or not self.vertices_g2:
			messagebox.showwarning("Advertencia", "Ambos grafos deben tener vértices")
			return
		
		# Vértices: todos los pares (u1, u2) donde u1 ∈ G1 y u2 ∈ G2
		self.vertices_resultado = set()
		for u1 in self.vertices_g1:
			for u2 in self.vertices_g2:
				self.vertices_resultado.add(f"({u1},{u2})")
		
		self.aristas_resultado = {}
		self.posiciones_resultado = {}  # Limpiar posiciones anteriores
		arista_counter = 0
		
		# Aristas: (u1, u2) - (v1, v2) existe si:
		# (u1, v1) es arista en G1 Y (u2, v2) es arista en G2
		for arista_g1_id, datos_g1 in self.aristas_g1.items():
			u1, v1 = datos_g1['u'], datos_g1['v']
			for arista_g2_id, datos_g2 in self.aristas_g2.items():
				u2, v2 = datos_g2['u'], datos_g2['v']
				
				v1_new = f"({u1},{u2})"
				v2_new = f"({v1},{v2})"
				if v1_new in self.vertices_resultado and v2_new in self.vertices_resultado:
					self.aristas_resultado[f"t{arista_counter}"] = {'u': v1_new, 'v': v2_new}
					arista_counter += 1
		
		self.operacion_actual = "Producto Tensorial (G₁ ⊗ G₂)"
		self.status.configure(text=self.operacion_actual)
		self._draw_resultado()
	
	def _on_composicion(self) -> None:
		"""Composición: G1[G2]"""
		if not self.vertices_g1 or not self.vertices_g2:
			messagebox.showwarning("Advertencia", "Ambos grafos deben tener vértices")
			return
		
		# Vértices: todos los pares (u1, u2) donde u1 ∈ G1 y u2 ∈ G2
		self.vertices_resultado = set()
		for u1 in self.vertices_g1:
			for u2 in self.vertices_g2:
				self.vertices_resultado.add(f"({u1},{u2})")
		
		self.aristas_resultado = {}
		self.posiciones_resultado = {}  # Limpiar posiciones anteriores
		arista_counter = 0
		
		# Aristas: (u1, u2) - (v1, v2) existe si:
		# 1. (u1, v1) es arista en G1, O
		# 2. u1 = v1 y (u2, v2) es arista en G2
		
		# Caso 1: (u1, v1) en G1
		for arista_id, datos in self.aristas_g1.items():
			u1, v1 = datos['u'], datos['v']
			for u2 in self.vertices_g2:
				for v2 in self.vertices_g2:
					v1_new = f"({u1},{u2})"
					v2_new = f"({v1},{v2})"
					if v1_new in self.vertices_resultado and v2_new in self.vertices_resultado:
						self.aristas_resultado[f"comp{arista_counter}"] = {'u': v1_new, 'v': v2_new}
						arista_counter += 1
		
		# Caso 2: u1 = v1 y (u2, v2) en G2
		for u1 in self.vertices_g1:
			for arista_id, datos in self.aristas_g2.items():
				u2, v2 = datos['u'], datos['v']
				v1_new = f"({u1},{u2})"
				v2_new = f"({u1},{v2})"
				if v1_new in self.vertices_resultado and v2_new in self.vertices_resultado:
					self.aristas_resultado[f"comp{arista_counter}"] = {'u': v1_new, 'v': v2_new}
					arista_counter += 1
		
		self.operacion_actual = "Composición (G₁[G₂])"
		self.status.configure(text=self.operacion_actual)
		self._draw_resultado()
	
	def _draw_resultado(self) -> None:
		"""Dibuja el grafo resultado en el canvas de resultado"""
		self.canvas_resultado.delete("all")
		
		if not self.vertices_resultado:
			self.canvas_resultado.create_text(
				150, 150,
				text="Resultado vacío",
				fill="#999999", font=("MS Sans Serif", 12)
			)
			return
		
		# Calcular posiciones usando algoritmo force-directed
		self._calcular_posiciones_resultado()
		
		# Agrupar aristas por pares para curvarlas
		aristas_por_par = {}
		for arista_id, datos in self.aristas_resultado.items():
			u, v = datos['u'], datos['v']
			par = tuple(sorted([u, v]))
			if par not in aristas_por_par:
				aristas_por_par[par] = []
			aristas_por_par[par].append((arista_id, datos))
		
		# Dibujar aristas
		for par, aristas_grupo in aristas_por_par.items():
			total_aristas = len(aristas_grupo)
			for idx, (arista_id, datos) in enumerate(aristas_grupo):
				u, v = datos['u'], datos['v']
				# Verificar que ambos vértices estén en el resultado y tengan posición
				if u not in self.vertices_resultado or v not in self.vertices_resultado:
					continue
				if u not in self.posiciones_resultado or v not in self.posiciones_resultado:
					continue
				
				x1, y1 = self.posiciones_resultado[u]
				x2, y2 = self.posiciones_resultado[v]
				
				if u == v:
					self._draw_loop_resultado(x1, y1, arista_id, idx, total_aristas)
				elif total_aristas > 1:
					curvatura = (idx - (total_aristas - 1) / 2) * 25
					self._draw_curved_line_resultado(x1, y1, x2, y2, arista_id, curvatura)
				else:
					self._draw_straight_line_resultado(x1, y1, x2, y2, arista_id)
		
		# Dibujar vértices (solo los que están en vertices_resultado)
		radius = 15
		for vertice in self.vertices_resultado:
			if vertice not in self.posiciones_resultado:
				continue
			x, y = self.posiciones_resultado[vertice]
			self.canvas_resultado.create_oval(
				x - radius, y - radius, x + radius, y + radius,
				fill="#4da3ff", outline="#255eaa", width=2
			)
			# Texto más pequeño para vértices con paréntesis
			font_size = 9 if len(str(vertice)) > 5 else 11
			self.canvas_resultado.create_text(
				x, y,
				text=str(vertice), fill="#ffffff",
				font=("MS Sans Serif", font_size, "bold")
			)
	
	def _calcular_posiciones_resultado(self) -> None:
		"""Calcula posiciones para el grafo resultado usando force-directed"""
		n = len(self.vertices_resultado)
		if n == 0:
			self.posiciones_resultado = {}  # Limpiar si no hay vértices
			return
		
		# Eliminar posiciones de vértices que ya no están en el resultado
		vertices_a_eliminar = [v for v in self.posiciones_resultado.keys() if v not in self.vertices_resultado]
		for v in vertices_a_eliminar:
			del self.posiciones_resultado[v]
		
		self.canvas_resultado.update_idletasks()
		width = max(self.canvas_resultado.winfo_width(), 300)
		height = max(self.canvas_resultado.winfo_height(), 300)
		
		center_x = width / 2
		center_y = height / 2
		
		vertices_list = list(self.vertices_resultado)
		
		# Inicializar posiciones solo para vértices que no tienen posición
		for vertice in vertices_list:
			if vertice not in self.posiciones_resultado:
				angle = random.uniform(0, 2 * math.pi)
				radius = random.uniform(50, min(width, height) / 3)
				self.posiciones_resultado[vertice] = (
					center_x + radius * math.cos(angle),
					center_y + radius * math.sin(angle)
				)
		
		# Algoritmo force-directed simplificado
		area = width * height
		k = math.sqrt(area / max(n, 1))
		temperature = min(width, height) / 10
		iterations = 30
		
		adyacentes = {v: set() for v in vertices_list}
		for arista_id, datos in self.aristas_resultado.items():
			u, v = datos['u'], datos['v']
			if u != v:
				adyacentes[u].add(v)
				adyacentes[v].add(u)
		
		for iteration in range(iterations):
			fuerzas = {v: [0.0, 0.0] for v in vertices_list}
			
			# Repulsión
			for i, v1 in enumerate(vertices_list):
				for v2 in vertices_list[i + 1:]:
					x1, y1 = self.posiciones_resultado[v1]
					x2, y2 = self.posiciones_resultado[v2]
					dx = x2 - x1
					dy = y2 - y1
					distancia = math.sqrt(dx**2 + dy**2)
					if distancia > 0:
						fuerza_repulsion = k**2 / distancia
						fx = (dx / distancia) * fuerza_repulsion
						fy = (dy / distancia) * fuerza_repulsion
						fuerzas[v1][0] -= fx
						fuerzas[v1][1] -= fy
						fuerzas[v2][0] += fx
						fuerzas[v2][1] += fy
			
			# Atracción
			for v1 in vertices_list:
				for v2 in adyacentes[v1]:
					if v1 < v2:
						x1, y1 = self.posiciones_resultado[v1]
						x2, y2 = self.posiciones_resultado[v2]
						dx = x2 - x1
						dy = y2 - y1
						distancia = math.sqrt(dx**2 + dy**2)
						if distancia > 0:
							fuerza_atraccion = distancia**2 / k
							fx = (dx / distancia) * fuerza_atraccion
							fy = (dy / distancia) * fuerza_atraccion
							fuerzas[v1][0] += fx
							fuerzas[v1][1] += fy
							fuerzas[v2][0] -= fx
							fuerzas[v2][1] -= fy
			
			# Aplicar fuerzas
			temp_actual = temperature * (1 - iteration / iterations)
			for vertice in vertices_list:
				fx, fy = fuerzas[vertice]
				fuerza_magnitud = math.sqrt(fx**2 + fy**2)
				if fuerza_magnitud > 0:
					desplazamiento = min(fuerza_magnitud, temp_actual)
					dx = (fx / fuerza_magnitud) * desplazamiento
					dy = (fy / fuerza_magnitud) * desplazamiento
					x, y = self.posiciones_resultado[vertice]
					nueva_x = x + dx
					nueva_y = y + dy
					margin = 40
					nueva_x = max(margin, min(width - margin, nueva_x))
					nueva_y = max(margin, min(height - margin, nueva_y))
					self.posiciones_resultado[vertice] = (nueva_x, nueva_y)
	
	def _draw_straight_line_resultado(self, x1: float, y1: float, x2: float, y2: float, arista_id: str) -> None:
		"""Dibuja línea recta en resultado"""
		self.canvas_resultado.create_line(x1, y1, x2, y2, fill="#000000", width=2)
		mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
		self.canvas_resultado.create_rectangle(mid_x - 12, mid_y - 10, mid_x + 12, mid_y + 10, fill="#ffffff", outline="")
		self.canvas_resultado.create_text(mid_x, mid_y, text=arista_id, fill="#000000", font=("MS Sans Serif", 9, "bold"))
	
	def _draw_curved_line_resultado(self, x1: float, y1: float, x2: float, y2: float, arista_id: str, curvatura: float) -> None:
		"""Dibuja línea curva en resultado"""
		mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
		dx = x2 - x1
		dy = y2 - y1
		length = math.sqrt(dx**2 + dy**2)
		if length == 0:
			return
		perp_x = -dy / length
		perp_y = dx / length
		control_x = mid_x + perp_x * curvatura
		control_y = mid_y + perp_y * curvatura
		self.canvas_resultado.create_line(x1, y1, control_x, control_y, x2, y2, fill="#000000", width=2, smooth=True)
		self.canvas_resultado.create_rectangle(control_x - 12, control_y - 10, control_x + 12, control_y + 10, fill="#ffffff", outline="")
		self.canvas_resultado.create_text(control_x, control_y, text=arista_id, fill="#000000", font=("MS Sans Serif", 9, "bold"))
	
	def _draw_loop_resultado(self, x: float, y: float, arista_id: str, idx: int, total: int) -> None:
		"""Dibuja bucle en resultado"""
		radius = 15
		loop_radius = 20
		if total > 1:
			angle_offset = (idx - (total - 1) / 2) * (360 / (total + 2))
			angle_rad = math.radians(angle_offset - 90)
		else:
			angle_rad = math.radians(-90)
		distance = radius + loop_radius
		loop_x = x + distance * math.cos(angle_rad)
		loop_y = y + distance * math.sin(angle_rad)
		self.canvas_resultado.create_oval(loop_x - loop_radius, loop_y - loop_radius, loop_x + loop_radius, loop_y + loop_radius, outline="#000000", width=2, fill="")
		label_distance = loop_radius + 12
		label_x = loop_x + label_distance * math.cos(angle_rad)
		label_y = loop_y + label_distance * math.sin(angle_rad)
		self.canvas_resultado.create_rectangle(label_x - 12, label_y - 10, label_x + 12, label_y + 10, fill="#ffffff", outline="")
		self.canvas_resultado.create_text(label_x, label_y, text=arista_id, fill="#000000", font=("MS Sans Serif", 9, "bold"))
