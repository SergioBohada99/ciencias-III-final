import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Set, List, Tuple, Optional
import math


class GrafoMatricesView(ttk.Frame):
	def __init__(self, parent: tk.Misc, app) -> None:
		super().__init__(parent)
		self.app = app
		
		# Estructuras de datos del grafo
		self.vertices: List[str] = []
		self.aristas: Dict[str, Tuple[str, str, float]] = {}  # {nombre_peso: (u, v, peso)}
		self.posiciones: Dict[str, Tuple[float, float]] = {}
		
		# Contador de pesos para nombres únicos
		self.conteo_pesos: Dict[str, int] = {}  # {"5": 2} significa que hay 5 y 5'
		
		# Árbol generador para circuitos y cortes fundamentales
		self.arbol_generador: List[str] = []
		self.cuerdas: Set[str] = set()
		
		self._build_ui()
	
	def _build_ui(self) -> None:
		"""Construye la interfaz de usuario"""
		title = ttk.Label(self, text="Matrices de Grafos", style="Title.TLabel")
		title.pack(pady=(10, 3))
		
		desc = ttk.Label(self, text="Genera las matrices asociadas a un grafo conexo ponderado no dirigido")
		desc.pack(pady=2)
		
		# Panel principal
		main_container = ttk.Frame(self)
		main_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=3)
		
		# Panel superior
		top_panel = ttk.Frame(main_container)
		top_panel.pack(fill=tk.BOTH, expand=True, pady=3)
		
		# Panel izquierdo: controles de entrada
		left_panel = ttk.Frame(top_panel, style="Panel.TFrame", padding=8)
		left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 4))
		
		# Sección: Agregar vértices (solo con Enter)
		lbl_vertices = ttk.Label(left_panel, text="Agregar Vértice", font=("MS Sans Serif", 9, "bold"))
		lbl_vertices.grid(row=0, column=0, columnspan=3, pady=(0, 3), sticky="w")
		
		ttk.Label(left_panel, text="Vértice:").grid(row=1, column=0, sticky="w", pady=1)
		self.entry_vertice = ttk.Entry(left_panel, width=8)
		self.entry_vertice.grid(row=1, column=1, columnspan=2, pady=1, sticky="w")
		self.entry_vertice.bind("<Return>", lambda e: self._on_agregar_vertice())
		
		ttk.Label(left_panel, text="(Enter para agregar)", font=("MS Sans Serif", 7)).grid(row=2, column=0, columnspan=3, sticky="w")
		
		ttk.Separator(left_panel, orient="horizontal").grid(row=3, column=0, columnspan=3, pady=6, sticky="ew")
		
		# Sección: Agregar aristas ponderadas
		lbl_aristas = ttk.Label(left_panel, text="Agregar Arista", font=("MS Sans Serif", 9, "bold"))
		lbl_aristas.grid(row=4, column=0, columnspan=3, pady=(0, 3), sticky="w")
		
		# Fila de arista: u [] - v []
		frame_arista = ttk.Frame(left_panel)
		frame_arista.grid(row=5, column=0, columnspan=3, pady=2, sticky="w")
		
		self.entry_u = ttk.Entry(frame_arista, width=5)
		self.entry_u.pack(side=tk.LEFT)
		ttk.Label(frame_arista, text=" — ").pack(side=tk.LEFT)
		self.entry_v = ttk.Entry(frame_arista, width=5)
		self.entry_v.pack(side=tk.LEFT)
		
		# Peso
		frame_peso = ttk.Frame(left_panel)
		frame_peso.grid(row=6, column=0, columnspan=3, pady=2, sticky="w")
		
		ttk.Label(frame_peso, text="Peso:").pack(side=tk.LEFT)
		self.entry_peso = ttk.Entry(frame_peso, width=8)
		self.entry_peso.pack(side=tk.LEFT, padx=(5, 0))
		self.entry_peso.bind("<Return>", lambda e: self._on_agregar_arista())
		
		ttk.Label(left_panel, text="(Enter en peso para agregar)", font=("MS Sans Serif", 7)).grid(row=7, column=0, columnspan=3, sticky="w")
		
		ttk.Separator(left_panel, orient="horizontal").grid(row=8, column=0, columnspan=3, pady=6, sticky="ew")
		
		# Botones de acción
		btn_ejecutar = ttk.Button(left_panel, text="▶ Generar Matrices", command=self._on_calcular_matrices, style="Retro.TButton")
		btn_ejecutar.grid(row=9, column=0, columnspan=3, pady=2, sticky="ew")
		
		btn_limpiar = ttk.Button(left_panel, text="Limpiar", command=self._on_limpiar)
		btn_limpiar.grid(row=10, column=0, columnspan=3, pady=2, sticky="ew")
		
		# Estado
		self.status = ttk.Label(left_panel, text="Agrega vértices y aristas", wraplength=130, font=("MS Sans Serif", 8))
		self.status.grid(row=11, column=0, columnspan=3, pady=(8, 0))
		
		# Panel central: Canvas para visualizar el grafo
		center_panel = ttk.Frame(top_panel, style="Panel.TFrame", padding=5)
		center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)
		
		lbl_grafo = ttk.Label(center_panel, text="Visualización del Grafo", font=("MS Sans Serif", 9, "bold"))
		lbl_grafo.pack(anchor="w")
		
		self.canvas = tk.Canvas(center_panel, background="#ffffff", width=350, height=280)
		self.canvas.pack(fill=tk.BOTH, expand=True)
		
		# Panel inferior: matrices con scroll
		bottom_panel = ttk.Frame(main_container, style="Panel.TFrame", padding=8)
		bottom_panel.pack(fill=tk.BOTH, expand=True, pady=3)
		
		lbl_matrices = ttk.Label(bottom_panel, text="Matrices", font=("MS Sans Serif", 9, "bold"))
		lbl_matrices.pack(anchor="w")
		
		# Canvas con scroll para las matrices
		matrices_container = ttk.Frame(bottom_panel)
		matrices_container.pack(fill=tk.BOTH, expand=True)
		
		self.matrices_canvas = tk.Canvas(matrices_container, bg="#f5f5f5")
		scroll_v = ttk.Scrollbar(matrices_container, orient="vertical", command=self.matrices_canvas.yview)
		scroll_h = ttk.Scrollbar(matrices_container, orient="horizontal", command=self.matrices_canvas.xview)
		
		self.scrollable_frame = ttk.Frame(self.matrices_canvas)
		self.scrollable_frame.bind("<Configure>", lambda e: self.matrices_canvas.configure(scrollregion=self.matrices_canvas.bbox("all")))
		
		self.matrices_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
		self.matrices_canvas.configure(yscrollcommand=scroll_v.set, xscrollcommand=scroll_h.set)
		
		scroll_v.pack(side=tk.RIGHT, fill=tk.Y)
		scroll_h.pack(side=tk.BOTTOM, fill=tk.X)
		self.matrices_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		
		# Grid para las matrices
		self.matrices_grid_row = 0
		self.matrices_grid_col = 0
		
		# Panel de archivos
		file_panel = ttk.Frame(self, style="Panel.TFrame", padding=6)
		file_panel.pack(fill=tk.X, padx=8, pady=3)
		
		btn_save_close = ttk.Button(file_panel, text="Guardar y cerrar", command=self._on_save_and_close)
		btn_save_close.pack(side=tk.LEFT, padx=4)
		
		btn_save = ttk.Button(file_panel, text="Guardar", command=self._on_save)
		btn_save.pack(side=tk.LEFT, padx=4)
		
		btn_load = ttk.Button(file_panel, text="Cargar", command=self._on_load)
		btn_load.pack(side=tk.LEFT, padx=4)
		
		# Botón volver
		back = ttk.Button(self, text="← Volver", command=lambda: self.app.navigate("arboles_menu"))
		back.pack(pady=5)
		
		self._draw_grafo()
	
	# ==================== ENTRADA DE DATOS ====================
	
	def _on_agregar_vertice(self) -> None:
		"""Agrega un vértice al grafo"""
		vertice = self.entry_vertice.get().strip()
		
		if not vertice:
			return
		
		if not vertice.isalnum():
			messagebox.showerror("Error", "El vértice debe ser solo letras o números")
			return
		
		if vertice in self.vertices:
			messagebox.showwarning("Advertencia", f"El vértice '{vertice}' ya existe")
			return
		
		self.vertices.append(vertice)
		self.status.configure(text=f"Vértice '{vertice}' agregado")
		self.entry_vertice.delete(0, tk.END)
		self._draw_grafo()
	
	def _generar_nombre_arista(self, peso: float) -> str:
		"""Genera el nombre de la arista basado en su peso con primas para repetidos"""
		# Formatear peso
		if peso == int(peso):
			peso_base = str(int(peso))
		else:
			peso_base = f"{peso:.1f}"
		
		# Contar cuántas veces ya existe este peso
		if peso_base not in self.conteo_pesos:
			self.conteo_pesos[peso_base] = 0
			return peso_base
		else:
			# Agregar primas
			count = self.conteo_pesos[peso_base]
			self.conteo_pesos[peso_base] += 1
			primas = "'" * (count + 1)
			return f"{peso_base}{primas}"
	
	def _on_agregar_arista(self) -> None:
		"""Agrega una arista ponderada al grafo"""
		u = self.entry_u.get().strip()
		v = self.entry_v.get().strip()
		peso_str = self.entry_peso.get().strip()
		
		if not u or not v or not peso_str:
			messagebox.showerror("Error", "Completa origen, destino y peso")
			return
		
		if u not in self.vertices or v not in self.vertices:
			messagebox.showerror("Error", "Ambos vértices deben existir en el grafo")
			return
		
		try:
			peso = float(peso_str)
			if peso < 0:
				messagebox.showerror("Error", "El peso debe ser positivo")
				return
		except ValueError:
			messagebox.showerror("Error", "El peso debe ser un número válido")
			return
		
		# Verificar si ya existe arista entre u y v
		for datos in self.aristas.values():
			if (datos[0] == u and datos[1] == v) or (datos[0] == v and datos[1] == u):
				messagebox.showwarning("Advertencia", f"Ya existe una arista entre {u} y {v}")
				return
		
		nombre = self._generar_nombre_arista(peso)
		self.aristas[nombre] = (u, v, peso)
		self.status.configure(text=f"Arista '{nombre}': {u}—{v}")
		
		self.entry_u.delete(0, tk.END)
		self.entry_v.delete(0, tk.END)
		self.entry_peso.delete(0, tk.END)
		self.entry_u.focus()
		
		self._draw_grafo()
	
	def _on_limpiar(self) -> None:
		"""Limpia todo el grafo"""
		self.vertices = []
		self.aristas = {}
		self.posiciones = {}
		self.conteo_pesos = {}
		self.arbol_generador = []
		self.cuerdas = set()
		
		# Limpiar matrices
		for widget in self.scrollable_frame.winfo_children():
			widget.destroy()
		self.matrices_grid_row = 0
		self.matrices_grid_col = 0
		
		self._draw_grafo()
		self.status.configure(text="Grafo limpiado")
	
	def _es_conexo(self) -> bool:
		"""Verifica si el grafo es conexo"""
		if len(self.vertices) <= 1:
			return True
		
		if not self.aristas:
			return False
		
		adj: Dict[str, Set[str]] = {v: set() for v in self.vertices}
		for u, v, _ in self.aristas.values():
			adj[u].add(v)
			adj[v].add(u)
		
		visitados = set()
		cola = [self.vertices[0]]
		visitados.add(self.vertices[0])
		
		while cola:
			actual = cola.pop(0)
			for vecino in adj[actual]:
				if vecino not in visitados:
					visitados.add(vecino)
					cola.append(vecino)
		
		return len(visitados) == len(self.vertices)
	
	# ==================== VISUALIZACIÓN ====================
	
	def _calcular_posiciones(self) -> None:
		"""Calcula posiciones usando layout circular"""
		n = len(self.vertices)
		if n == 0:
			return
		
		self.canvas.update_idletasks()
		width = max(self.canvas.winfo_width(), 350)
		height = max(self.canvas.winfo_height(), 280)
		
		center_x = width / 2
		center_y = height / 2
		radius = min(width, height) / 2.8
		
		for i, vertice in enumerate(self.vertices):
			angle = 2 * math.pi * i / n - math.pi / 2
			self.posiciones[vertice] = (
				center_x + radius * math.cos(angle),
				center_y + radius * math.sin(angle)
			)
	
	def _draw_grafo(self) -> None:
		"""Dibuja el grafo"""
		self.canvas.delete("all")
		
		if not self.vertices:
			self.canvas.update_idletasks()
			width = max(self.canvas.winfo_width(), 350)
			height = max(self.canvas.winfo_height(), 280)
			self.canvas.create_text(width // 2, height // 2, text="Agrega vértices al grafo", fill="#666666", font=("MS Sans Serif", 11))
			return
		
		self._calcular_posiciones()
		
		# Dibujar aristas
		for nombre_arista, (u, v, peso) in self.aristas.items():
			if u not in self.posiciones or v not in self.posiciones:
				continue
			
			x1, y1 = self.posiciones[u]
			x2, y2 = self.posiciones[v]
			
			# Color según si es rama o cuerda
			if self.arbol_generador:
				if nombre_arista in self.arbol_generador:
					color = "#00aa00"
					width = 3
				else:
					color = "#ff6600"
					width = 2
			else:
				color = "#333333"
				width = 2
			
			self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width)
			
			# Etiqueta de la arista (nombre basado en peso)
			mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
			
			# Calcular ancho del texto
			text_width = len(nombre_arista) * 6 + 8
			half_w = max(text_width // 2, 10)
			
			self.canvas.create_rectangle(mid_x - half_w, mid_y - 10, mid_x + half_w, mid_y + 10, fill="#ffffff", outline=color)
			self.canvas.create_text(mid_x, mid_y, text=nombre_arista, fill=color, font=("MS Sans Serif", 9, "bold"))
		
		# Dibujar vértices
		radius = 16
		for vertice in self.vertices:
			if vertice not in self.posiciones:
				continue
			x, y = self.posiciones[vertice]
			
			self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill="#4da3ff", outline="#255eaa", width=2)
			self.canvas.create_text(x, y, text=str(vertice), fill="#ffffff", font=("MS Sans Serif", 10, "bold"))
	
	# ==================== CÁLCULO DE MATRICES ====================
	
	def _on_calcular_matrices(self) -> None:
		"""Calcula y muestra todas las matrices"""
		if len(self.vertices) < 2:
			messagebox.showerror("Error", "Se necesitan al menos 2 vértices")
			return
		
		if not self.aristas:
			messagebox.showerror("Error", "Se necesita al menos una arista")
			return
		
		if not self._es_conexo():
			messagebox.showerror("Error", "El grafo debe ser conexo")
			return
		
		# Calcular árbol generador
		self._calcular_arbol_generador()
		
		# Limpiar matrices anteriores
		for widget in self.scrollable_frame.winfo_children():
			widget.destroy()
		self.matrices_grid_row = 0
		self.matrices_grid_col = 0
		
		# Configurar columnas
		self.scrollable_frame.columnconfigure(0, weight=1)
		self.scrollable_frame.columnconfigure(1, weight=1)
		
		# Generar todas las matrices
		self._mostrar_matriz_adyacencia_vertices()
		self._mostrar_matriz_adyacencia_aristas()
		self._mostrar_matriz_incidencia()
		self._mostrar_matriz_circuitos()
		self._mostrar_matriz_circuitos_fundamentales()
		self._mostrar_matriz_conjuntos_corte()
		self._mostrar_matriz_cortes_fundamentales()
		
		# Actualizar scroll
		self.matrices_canvas.update_idletasks()
		self.matrices_canvas.configure(scrollregion=self.matrices_canvas.bbox("all"))
		
		# Redibujar grafo con colores
		self._draw_grafo()
		
		self.status.configure(text="Matrices generadas ✓")
	
	def _calcular_arbol_generador(self) -> None:
		"""Calcula un árbol generador usando DFS"""
		self.arbol_generador = []
		self.cuerdas = set()
		
		if not self.vertices:
			return
		
		visitados: Set[str] = set()
		
		# Construir adyacencia con nombres de aristas
		adj: Dict[str, List[Tuple[str, str]]] = {v: [] for v in self.vertices}
		for nombre_arista, (u, v, _) in self.aristas.items():
			adj[u].append((v, nombre_arista))
			adj[v].append((u, nombre_arista))
		
		def dfs(vertice: str) -> None:
			visitados.add(vertice)
			for vecino, nombre_arista in adj[vertice]:
				if vecino not in visitados:
					self.arbol_generador.append(nombre_arista)
					dfs(vecino)
		
		dfs(self.vertices[0])
		
		# Cuerdas = aristas que no están en el árbol
		self.cuerdas = set(self.aristas.keys()) - set(self.arbol_generador)
	
	def _crear_tabla_matriz(self, titulo: str, headers: List[str], datos: List[List[str]]) -> None:
		"""Crea una tabla para mostrar una matriz"""
		frame = tk.Frame(self.scrollable_frame, bg="#e0e0e0", relief=tk.RAISED, bd=2)
		frame.grid(row=self.matrices_grid_row, column=self.matrices_grid_col, sticky="nsew", pady=4, padx=4)
		
		inner = ttk.Frame(frame, padding=6)
		inner.pack(fill=tk.BOTH, expand=True)
		
		# Título
		lbl_titulo = tk.Label(inner, text=titulo, font=("MS Sans Serif", 10, "bold"), bg="#e0e0e0", fg="#255eaa")
		lbl_titulo.pack(pady=(0, 6))
		
		if not datos:
			ttk.Label(inner, text="Sin datos").pack()
			self._avanzar_grid()
			return
		
		# Tabla
		tabla = tk.Frame(inner, bg="#ffffff")
		tabla.pack(fill=tk.BOTH, expand=True)
		
		# Encabezados
		for col, header in enumerate(headers):
			lbl = tk.Label(tabla, text=str(header), font=("Consolas", 8, "bold"), bg="#4da3ff", fg="#ffffff", relief=tk.RAISED, padx=4, pady=2, width=6)
			lbl.grid(row=0, column=col, sticky="nsew", padx=1, pady=1)
		
		# Filas
		for row, fila in enumerate(datos, start=1):
			for col, valor in enumerate(fila):
				bg = "#f0f0f0" if row % 2 == 0 else "#ffffff"
				lbl = tk.Label(tabla, text=str(valor), font=("Consolas", 8), bg=bg, relief=tk.SUNKEN, padx=4, pady=2, width=6)
				lbl.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)
		
		self._avanzar_grid()
	
	def _avanzar_grid(self) -> None:
		"""Avanza la posición del grid"""
		if self.matrices_grid_col == 0:
			self.matrices_grid_col = 1
		else:
			self.matrices_grid_col = 0
			self.matrices_grid_row += 1
	
	def _subindice(self, num: int) -> str:
		"""Convierte un número a subíndice Unicode"""
		subindices = {'0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
					  '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉'}
		return ''.join(subindices.get(c, c) for c in str(num))
	
	# ==================== MATRICES ====================
	
	def _mostrar_matriz_adyacencia_vertices(self) -> None:
		"""Matriz de adyacencia de vértices"""
		vertices_ord = sorted(self.vertices)
		
		headers = [""] + vertices_ord
		datos = []
		
		for v1 in vertices_ord:
			fila = [v1]
			for v2 in vertices_ord:
				# Contar aristas entre v1 y v2
				count = 0
				for u, w, _ in self.aristas.values():
					if (u == v1 and w == v2) or (u == v2 and w == v1):
						count += 1
				fila.append(str(count))
			datos.append(fila)
		
		self._crear_tabla_matriz("Adyacencia de Vértices", headers, datos)
	
	def _mostrar_matriz_adyacencia_aristas(self) -> None:
		"""Matriz de adyacencia de aristas"""
		aristas_ord = sorted(self.aristas.keys())
		
		if not aristas_ord:
			self._crear_tabla_matriz("Adyacencia de Aristas", [], [])
			return
		
		headers = [""] + aristas_ord
		datos = []
		
		for a1 in aristas_ord:
			fila = [a1]
			u1, v1, _ = self.aristas[a1]
			vertices_a1 = {u1, v1}
			
			for a2 in aristas_ord:
				if a1 == a2:
					fila.append("0")
				else:
					u2, v2, _ = self.aristas[a2]
					# Aristas adyacentes si comparten un vértice
					if vertices_a1.intersection({u2, v2}):
						fila.append("1")
					else:
						fila.append("0")
			datos.append(fila)
		
		self._crear_tabla_matriz("Adyacencia de Aristas", headers, datos)
	
	def _mostrar_matriz_incidencia(self) -> None:
		"""Matriz de incidencia vértice-arista"""
		vertices_ord = sorted(self.vertices)
		aristas_ord = sorted(self.aristas.keys())
		
		if not aristas_ord:
			self._crear_tabla_matriz("Incidencia Vértice-Arista", [], [])
			return
		
		headers = [""] + aristas_ord
		datos = []
		
		for v in vertices_ord:
			fila = [v]
			for a in aristas_ord:
				u, w, _ = self.aristas[a]
				if u == v and w == v:
					fila.append("2")  # Bucle
				elif u == v or w == v:
					fila.append("1")
				else:
					fila.append("0")
			datos.append(fila)
		
		self._crear_tabla_matriz("Incidencia Vértice-Arista", headers, datos)
	
	def _mostrar_matriz_circuitos(self) -> None:
		"""Matriz de todos los circuitos"""
		circuitos = self._encontrar_circuitos()
		aristas_ord = sorted(self.aristas.keys())
		
		if not circuitos:
			self._crear_tabla_matriz("Matriz de Circuitos", [""], [["Sin circuitos"]])
			return
		
		headers = [""] + aristas_ord
		datos = []
		
		for idx, circuito in enumerate(circuitos):
			# Usar C₁, C₂, etc.
			nombre = f"C{self._subindice(idx + 1)}"
			fila = [nombre]
			for a in aristas_ord:
				fila.append("1" if a in circuito else "0")
			datos.append(fila)
		
		self._crear_tabla_matriz("Matriz de Circuitos", headers, datos)
	
	def _mostrar_matriz_circuitos_fundamentales(self) -> None:
		"""Matriz de circuitos fundamentales"""
		circuitos_fund = self._encontrar_circuitos_fundamentales()
		aristas_ord = sorted(self.aristas.keys())
		
		if not circuitos_fund:
			self._crear_tabla_matriz("Circuitos Fundamentales", [""], [["Sin circ. fund."]])
			return
		
		headers = [""] + aristas_ord
		datos = []
		
		for idx, circuito in enumerate(circuitos_fund):
			# Usar C₁, C₂, etc.
			nombre = f"C{self._subindice(idx + 1)}"
			fila = [nombre]
			for a in aristas_ord:
				fila.append("1" if a in circuito else "0")
			datos.append(fila)
		
		self._crear_tabla_matriz("Circuitos Fundamentales", headers, datos)
	
	def _mostrar_matriz_conjuntos_corte(self) -> None:
		"""Matriz de conjuntos de corte"""
		cortes = self._encontrar_conjuntos_corte()
		aristas_ord = sorted(self.aristas.keys())
		
		if not cortes:
			self._crear_tabla_matriz("Conjuntos de Corte", [""], [["Sin cortes"]])
			return
		
		headers = [""] + aristas_ord
		datos = []
		
		for idx, corte in enumerate(cortes):
			# Usar Cc₁, Cc₂, etc.
			nombre = f"Cc{self._subindice(idx + 1)}"
			fila = [nombre]
			for a in aristas_ord:
				fila.append("1" if a in corte else "0")
			datos.append(fila)
		
		self._crear_tabla_matriz("Conjuntos de Corte", headers, datos)
	
	def _mostrar_matriz_cortes_fundamentales(self) -> None:
		"""Matriz de cortes fundamentales"""
		cortes_fund = self._encontrar_cortes_fundamentales()
		aristas_ord = sorted(self.aristas.keys())
		
		if not cortes_fund:
			self._crear_tabla_matriz("Cortes Fundamentales", [""], [["Sin cortes fund."]])
			return
		
		headers = [""] + aristas_ord
		datos = []
		
		for idx, corte in enumerate(cortes_fund):
			# Usar Cc₁, Cc₂, etc.
			nombre = f"Cc{self._subindice(idx + 1)}"
			fila = [nombre]
			for a in aristas_ord:
				fila.append("1" if a in corte else "0")
			datos.append(fila)
		
		self._crear_tabla_matriz("Cortes Fundamentales", headers, datos)
	
	# ==================== ALGORITMOS ====================
	
	def _encontrar_circuitos(self) -> List[Set[str]]:
		"""Encuentra todos los circuitos del grafo"""
		circuitos: List[Set[str]] = []
		circuitos_set: Set[frozenset] = set()
		
		# Construir adyacencia
		adj: Dict[str, List[Tuple[str, str]]] = {v: [] for v in self.vertices}
		for nombre_arista, (u, v, _) in self.aristas.items():
			adj[u].append((v, nombre_arista))
			adj[v].append((u, nombre_arista))
		
		def dfs(actual: str, camino: List[str], aristas_usadas: Set[str], inicio: str) -> None:
			for vecino, nombre_arista in adj[actual]:
				if nombre_arista in aristas_usadas:
					continue
				
				if vecino == inicio and len(aristas_usadas) >= 2:
					# Encontramos un circuito
					circuito = aristas_usadas | {nombre_arista}
					circuito_frozen = frozenset(circuito)
					if circuito_frozen not in circuitos_set:
						circuitos_set.add(circuito_frozen)
						circuitos.append(circuito)
				elif vecino not in camino:
					dfs(vecino, camino + [vecino], aristas_usadas | {nombre_arista}, inicio)
		
		for v in self.vertices:
			dfs(v, [v], set(), v)
		
		return circuitos
	
	def _encontrar_circuitos_fundamentales(self) -> List[Set[str]]:
		"""Encuentra circuitos fundamentales (uno por cada cuerda)"""
		if not self.arbol_generador or not self.cuerdas:
			return []
		
		circuitos_fund: List[Set[str]] = []
		
		# Construir grafo del árbol
		adj_arbol: Dict[str, List[Tuple[str, str]]] = {v: [] for v in self.vertices}
		for nombre_arista in self.arbol_generador:
			u, v, _ = self.aristas[nombre_arista]
			adj_arbol[u].append((v, nombre_arista))
			adj_arbol[v].append((u, nombre_arista))
		
		def encontrar_camino(inicio: str, fin: str) -> Optional[Set[str]]:
			"""Encuentra el camino en el árbol entre dos vértices"""
			if inicio == fin:
				return set()
			
			visitados: Set[str] = set()
			cola: List[Tuple[str, Set[str]]] = [(inicio, set())]
			
			while cola:
				actual, camino = cola.pop(0)
				if actual in visitados:
					continue
				visitados.add(actual)
				
				for vecino, nombre_arista in adj_arbol[actual]:
					if vecino == fin:
						return camino | {nombre_arista}
					if vecino not in visitados:
						cola.append((vecino, camino | {nombre_arista}))
			
			return None
		
		# Para cada cuerda, encontrar el circuito fundamental
		for cuerda in sorted(self.cuerdas):
			u, v, _ = self.aristas[cuerda]
			camino = encontrar_camino(u, v)
			if camino is not None:
				circuito = camino | {cuerda}
				circuitos_fund.append(circuito)
		
		return circuitos_fund
	
	def _encontrar_conjuntos_corte(self) -> List[Set[str]]:
		"""Encuentra todos los conjuntos de corte"""
		cortes: List[Set[str]] = []
		cortes_set: Set[frozenset] = set()
		
		vertices_list = self.vertices
		n = len(vertices_list)
		
		# Generar todas las particiones
		for mask in range(1, 2**(n-1)):
			S = {vertices_list[i] for i in range(n) if (mask >> i) & 1}
			
			if not S or S == set(vertices_list):
				continue
			
			# Encontrar aristas entre S y V-S
			corte: Set[str] = set()
			for nombre_arista, (u, v, _) in self.aristas.items():
				if (u in S and v not in S) or (u not in S and v in S):
					corte.add(nombre_arista)
			
			if corte:
				corte_frozen = frozenset(corte)
				if corte_frozen not in cortes_set:
					cortes_set.add(corte_frozen)
					cortes.append(corte)
		
		return cortes
	
	def _encontrar_cortes_fundamentales(self) -> List[Set[str]]:
		"""Encuentra cortes fundamentales (uno por cada rama del árbol)"""
		if not self.arbol_generador:
			return []
		
		cortes_fund: List[Set[str]] = []
		
		for rama in self.arbol_generador:
			u_rama, v_rama, _ = self.aristas[rama]
			
			# Encontrar componente de u sin la rama
			componente = self._componente_sin_arista(rama, u_rama)
			
			# Corte = rama + cuerdas que cruzan la partición
			corte: Set[str] = {rama}
			for nombre_arista, (u, v, _) in self.aristas.items():
				if nombre_arista == rama:
					continue
				if (u in componente and v not in componente) or (u not in componente and v in componente):
					corte.add(nombre_arista)
			
			cortes_fund.append(corte)
		
		return cortes_fund
	
	def _componente_sin_arista(self, arista_excluida: str, inicio: str) -> Set[str]:
		"""Encuentra el componente conexo sin una arista específica"""
		componente: Set[str] = set()
		
		# Construir grafo sin la arista
		adj: Dict[str, List[str]] = {v: [] for v in self.vertices}
		for nombre_arista, (u, v, _) in self.aristas.items():
			if nombre_arista == arista_excluida:
				continue
			adj[u].append(v)
			adj[v].append(u)
		
		# BFS
		cola = [inicio]
		componente.add(inicio)
		
		while cola:
			actual = cola.pop(0)
			for vecino in adj[actual]:
				if vecino not in componente:
					componente.add(vecino)
					cola.append(vecino)
		
		return componente
	
	# ==================== GUARDAR / CARGAR ====================
	
	def _serialize(self) -> str:
		"""Serializa el grafo a texto"""
		lines = ["# Grafo Matrices"]
		lines.append(f"vertices:{','.join(self.vertices)}")
		
		for nombre, (u, v, peso) in self.aristas.items():
			lines.append(f"arista:{nombre},{u},{v},{peso}")
		
		return "\n".join(lines) + "\n"
	
	def _parse(self, content: str) -> bool:
		"""Parsea el contenido de un archivo"""
		self.vertices = []
		self.aristas = {}
		self.posiciones = {}
		self.conteo_pesos = {}
		
		try:
			for line in content.splitlines():
				line = line.strip()
				if not line or line.startswith("#"):
					continue
				
				if line.startswith("vertices:"):
					verts = line.split(":", 1)[1]
					if verts:
						self.vertices = [v.strip() for v in verts.split(",") if v.strip()]
				
				elif line.startswith("arista:"):
					parts = line.split(":", 1)[1].split(",")
					if len(parts) >= 4:
						nombre = parts[0].strip()
						u = parts[1].strip()
						v = parts[2].strip()
						peso = float(parts[3].strip())
						self.aristas[nombre] = (u, v, peso)
			
			return True
		except Exception:
			return False
	
	def _on_save(self) -> None:
		"""Guarda el grafo"""
		path = filedialog.asksaveasfilename(
			title="Guardar grafo Matrices",
			defaultextension=".txt",
			filetypes=[("Texto", "*.txt"), ("Todos", "*.*")]
		)
		if not path:
			return
		try:
			with open(path, "w", encoding="utf-8") as f:
				f.write(self._serialize())
			messagebox.showinfo("Éxito", "Grafo guardado correctamente")
		except Exception as e:
			messagebox.showerror("Error", f"No se pudo guardar: {e}")
	
	def _on_save_and_close(self) -> None:
		"""Guarda y cierra"""
		path = filedialog.asksaveasfilename(
			title="Guardar grafo Matrices",
			defaultextension=".txt",
			filetypes=[("Texto", "*.txt"), ("Todos", "*.*")]
		)
		if not path:
			return
		try:
			with open(path, "w", encoding="utf-8") as f:
				f.write(self._serialize())
			messagebox.showinfo("Éxito", "Grafo guardado correctamente")
			self.app.navigate("arboles_menu")
		except Exception as e:
			messagebox.showerror("Error", f"No se pudo guardar: {e}")
	
	def _on_load(self) -> None:
		"""Carga un grafo"""
		path = filedialog.askopenfilename(
			title="Cargar grafo Matrices",
			filetypes=[("Texto", "*.txt"), ("Todos", "*.*")]
		)
		if not path:
			return
		try:
			with open(path, "r", encoding="utf-8") as f:
				content = f.read()
		except Exception as e:
			messagebox.showerror("Error", f"No se pudo leer: {e}")
			return
		
		if not self._parse(content):
			messagebox.showerror("Error", "Formato de archivo inválido")
			return
		
		# Limpiar matrices anteriores
		self.arbol_generador = []
		self.cuerdas = set()
		for widget in self.scrollable_frame.winfo_children():
			widget.destroy()
		
		self._draw_grafo()
		self.status.configure(text=f"Cargado: {len(self.vertices)} vértices, {len(self.aristas)} aristas")
