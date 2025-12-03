import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, List, Tuple, Set
import math
import random


class FloydView(ttk.Frame):
	def __init__(self, parent: tk.Misc, app) -> None:
		super().__init__(parent)
		self.app = app
		
		# Estructuras de datos del grafo
		self.vertices: List[str] = []
		self.aristas: Dict[str, Dict[str, float]] = {}  # {letra: {'u': str, 'v': str, 'peso': float}}
		self.posiciones: Dict[str, Tuple[float, float]] = {}
		
		# Matrices de Floyd
		self.matriz_distancias: List[List[float]] = []
		self.matrices_intermedias: List[Tuple[int, List[List[float]]]] = []  # (k, matriz)
		
		# Resultados
		self.excentricidades: Dict[str, float] = {}
		self.radio: float = float('inf')
		self.diametro: float = 0
		self.centros: List[str] = []
		self.mediana: List[str] = []
		self.sumas_distancias: Dict[str, float] = {}
		
		self._build_ui()
	
	def _build_ui(self) -> None:
		"""Construye la interfaz de usuario"""
		title = ttk.Label(self, text="Algoritmo de Floyd", style="Title.TLabel")
		title.pack(pady=(10, 3))
		
		desc = ttk.Label(self, text="Encuentra el camino más corto entre todos los pares de vértices (Grafo Dirigido)")
		desc.pack(pady=2)
		
		# Panel principal
		main_container = ttk.Frame(self)
		main_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=3)
		
		# Panel superior: entrada + grafo + resultados
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
		
		# Fila de arista: u [] -> v []
		frame_arista = ttk.Frame(left_panel)
		frame_arista.grid(row=5, column=0, columnspan=3, pady=2, sticky="w")
		
		self.entry_u = ttk.Entry(frame_arista, width=5)
		self.entry_u.pack(side=tk.LEFT)
		ttk.Label(frame_arista, text=" → ").pack(side=tk.LEFT)
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
		btn_ejecutar = ttk.Button(left_panel, text="▶ Ejecutar Floyd", command=self._ejecutar_floyd, style="Retro.TButton")
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
		
		self.canvas = tk.Canvas(center_panel, background="#ffffff", width=400, height=280)
		self.canvas.pack(fill=tk.BOTH, expand=True)
		
		# Panel derecho: resultados
		right_panel = ttk.Frame(top_panel, style="Panel.TFrame", padding=8)
		right_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(4, 0))
		
		lbl_resultados = ttk.Label(right_panel, text="Resultados", font=("MS Sans Serif", 9, "bold"))
		lbl_resultados.pack(anchor="w")
		
		self.txt_resultados = tk.Text(right_panel, width=28, height=16, font=("Consolas", 8))
		scroll_resultados = ttk.Scrollbar(right_panel, orient="vertical", command=self.txt_resultados.yview)
		self.txt_resultados.configure(yscrollcommand=scroll_resultados.set)
		
		scroll_resultados.pack(side=tk.RIGHT, fill=tk.Y)
		self.txt_resultados.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		self.txt_resultados.configure(state="disabled")
		
		# Panel inferior: matrices
		bottom_panel = ttk.Frame(main_container, style="Panel.TFrame", padding=8)
		bottom_panel.pack(fill=tk.BOTH, expand=True, pady=3)
		
		lbl_matrices = ttk.Label(bottom_panel, text="Matrices de Floyd", font=("MS Sans Serif", 9, "bold"))
		lbl_matrices.pack(anchor="w")
		
		# Frame con scroll horizontal para las matrices
		matrices_container = ttk.Frame(bottom_panel)
		matrices_container.pack(fill=tk.BOTH, expand=True)
		
		# Canvas con scroll para las matrices
		self.canvas_matrices = tk.Canvas(matrices_container, height=160)
		scroll_h = ttk.Scrollbar(matrices_container, orient="horizontal", command=self.canvas_matrices.xview)
		scroll_v = ttk.Scrollbar(matrices_container, orient="vertical", command=self.canvas_matrices.yview)
		
		self.canvas_matrices.configure(xscrollcommand=scroll_h.set, yscrollcommand=scroll_v.set)
		
		scroll_h.pack(side=tk.BOTTOM, fill=tk.X)
		scroll_v.pack(side=tk.RIGHT, fill=tk.Y)
		self.canvas_matrices.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		
		# Frame interior para las matrices
		self.frame_matrices = ttk.Frame(self.canvas_matrices)
		self.canvas_matrices.create_window((0, 0), window=self.frame_matrices, anchor="nw")
		
		self.frame_matrices.bind("<Configure>", lambda e: self.canvas_matrices.configure(scrollregion=self.canvas_matrices.bbox("all")))
		
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
		back = ttk.Button(self, text="← Volver", command=lambda: self.app.navigate("grafos"))
		back.pack(pady=5)
		
		self._draw_grafo()
		self._limpiar_resultados()
	
	def _on_agregar_vertice(self) -> None:
		"""Agrega un vértice al grafo"""
		vertice = self.entry_vertice.get().strip()
		
		if not vertice:
			return
		
		# Validar que sea solo letras o números
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
	
	def _generar_letra_arista(self) -> str:
		"""Genera automáticamente la siguiente letra para la arista"""
		# Usar letras minúsculas: a, b, c, ..., z, aa, ab, ...
		letras_usadas = set(self.aristas.keys())
		letra_idx = 0
		while True:
			if letra_idx < 26:
				letra = chr(ord('a') + letra_idx)
			else:
				# Para más de 26 aristas: aa, ab, ac, ...
				primera = chr(ord('a') + (letra_idx // 26) - 1)
				segunda = chr(ord('a') + (letra_idx % 26))
				letra = primera + segunda
			
			if letra not in letras_usadas:
				return letra
			letra_idx += 1
	
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
		
		# Generar letra automáticamente
		letra = self._generar_letra_arista()
		
		self.aristas[letra] = {'u': u, 'v': v, 'peso': peso}
		self.status.configure(text=f"Arista '{letra}': {u}→{v} (w={peso})")
		
		# Limpiar campos
		self.entry_u.delete(0, tk.END)
		self.entry_v.delete(0, tk.END)
		self.entry_peso.delete(0, tk.END)
		
		# Poner foco en el primer campo para agregar otra
		self.entry_u.focus()
		
		self._draw_grafo()
	
	def _on_limpiar(self) -> None:
		"""Limpia todo el grafo y resultados"""
		self.vertices = []
		self.aristas = {}
		self.posiciones = {}
		self.matriz_distancias = []
		self.matrices_intermedias = []
		self.excentricidades = {}
		self.radio = float('inf')
		self.diametro = 0
		self.centros = []
		self.mediana = []
		self.sumas_distancias = {}
		
		self._draw_grafo()
		self._limpiar_resultados()
		self._limpiar_matrices()
		self.status.configure(text="Grafo limpiado")
	
	def _es_conexo(self) -> bool:
		"""Verifica si el grafo es conexo usando BFS"""
		if len(self.vertices) <= 1:
			return True
		
		if not self.aristas:
			return False
		
		# Construir lista de adyacencia (no dirigido)
		adj: Dict[str, Set[str]] = {v: set() for v in self.vertices}
		for datos in self.aristas.values():
			u, v = datos['u'], datos['v']
			adj[u].add(v)
			adj[v].add(u)
		
		# BFS desde el primer vértice
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
	
	# ==================== VISUALIZACIÓN DEL GRAFO ====================
	
	def _calcular_posiciones(self) -> None:
		"""Calcula posiciones usando algoritmo force-directed"""
		n = len(self.vertices)
		if n == 0:
			return
		
		self.canvas.update_idletasks()
		width = max(self.canvas.winfo_width(), 400)
		height = max(self.canvas.winfo_height(), 280)
		
		center_x = width / 2
		center_y = height / 2
		
		# Inicializar posiciones aleatorias para vértices nuevos
		for vertice in self.vertices:
			if vertice not in self.posiciones:
				angle = random.uniform(0, 2 * math.pi)
				radius = random.uniform(40, min(width, height) / 3)
				self.posiciones[vertice] = (
					center_x + radius * math.cos(angle),
					center_y + radius * math.sin(angle)
				)
		
		# Parámetros del algoritmo force-directed
		area = width * height
		k = math.sqrt(area / max(n, 1))
		temperature = min(width, height) / 10
		iterations = 50
		
		# Crear estructura de adyacencia
		adyacentes = {v: set() for v in self.vertices}
		for datos in self.aristas.values():
			u, v = datos['u'], datos['v']
			if u != v:
				adyacentes[u].add(v)
				adyacentes[v].add(u)
		
		# Iteraciones del algoritmo
		for iteration in range(iterations):
			fuerzas = {v: [0.0, 0.0] for v in self.vertices}
			
			# Fuerza de repulsión
			for i, v1 in enumerate(self.vertices):
				for v2 in self.vertices[i + 1:]:
					x1, y1 = self.posiciones[v1]
					x2, y2 = self.posiciones[v2]
					
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
			
			# Fuerza de atracción
			for v1 in self.vertices:
				for v2 in adyacentes[v1]:
					if v1 < v2:
						x1, y1 = self.posiciones[v1]
						x2, y2 = self.posiciones[v2]
						
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
			for vertice in self.vertices:
				fx, fy = fuerzas[vertice]
				fuerza_magnitud = math.sqrt(fx**2 + fy**2)
				
				if fuerza_magnitud > 0:
					desplazamiento = min(fuerza_magnitud, temp_actual)
					dx = (fx / fuerza_magnitud) * desplazamiento
					dy = (fy / fuerza_magnitud) * desplazamiento
					
					x, y = self.posiciones[vertice]
					nueva_x = x + dx
					nueva_y = y + dy
					
					margin = 35
					nueva_x = max(margin, min(width - margin, nueva_x))
					nueva_y = max(margin, min(height - margin, nueva_y))
					
					self.posiciones[vertice] = (nueva_x, nueva_y)
	
	def _draw_grafo(self) -> None:
		"""Dibuja el grafo en el canvas"""
		self.canvas.delete("all")
		
		if not self.vertices:
			self.canvas.update_idletasks()
			width = max(self.canvas.winfo_width(), 400)
			height = max(self.canvas.winfo_height(), 280)
			self.canvas.create_text(
				width // 2, height // 2,
				text="Agrega vértices al grafo",
				fill="#666666", font=("MS Sans Serif", 11)
			)
			return
		
		self._calcular_posiciones()
		
		# Agrupar aristas por pares ordenados (u, v) - grafo dirigido
		aristas_por_par = {}
		for arista_id, datos in self.aristas.items():
			u, v = datos['u'], datos['v']
			par = (u, v)  # No ordenar - mantener dirección
			if par not in aristas_por_par:
				aristas_por_par[par] = []
			aristas_por_par[par].append((arista_id, datos))
		
		# Dibujar aristas
		for par, aristas_grupo in aristas_por_par.items():
			u_par, v_par = par
			# Verificar si hay aristas en dirección contraria
			hay_contraria = (v_par, u_par) in aristas_por_par
			total_aristas = len(aristas_grupo)
			
			for idx, (arista_id, datos) in enumerate(aristas_grupo):
				u, v = datos['u'], datos['v']
				peso = datos['peso']
				
				if u not in self.posiciones or v not in self.posiciones:
					continue
				
				x1, y1 = self.posiciones[u]
				x2, y2 = self.posiciones[v]
				
				if u == v:
					self._draw_loop(x1, y1, arista_id, peso, idx, total_aristas)
				elif total_aristas > 1 or hay_contraria:
					# Curvar si hay múltiples o hay arista en dirección opuesta
					curvatura = 20 if total_aristas == 1 else (idx - (total_aristas - 1) / 2) * 25
					self._draw_curved_edge(x1, y1, x2, y2, arista_id, peso, curvatura)
				else:
					self._draw_straight_edge(x1, y1, x2, y2, arista_id, peso)
		
		# Dibujar vértices
		radius = 18
		for vertice in self.vertices:
			if vertice not in self.posiciones:
				continue
			x, y = self.posiciones[vertice]
			
			# Círculo del vértice
			self.canvas.create_oval(
				x - radius, y - radius, x + radius, y + radius,
				fill="#4da3ff", outline="#255eaa", width=2
			)
			# Etiqueta
			self.canvas.create_text(
				x, y,
				text=str(vertice), fill="#ffffff",
				font=("MS Sans Serif", 10, "bold")
			)
	
	def _draw_straight_edge(self, x1: float, y1: float, x2: float, y2: float, arista_id: str, peso: float) -> None:
		"""Dibuja una arista recta con peso y flecha (dirigida)"""
		# Calcular punto final ajustado (para que la flecha no quede dentro del nodo)
		dx = x2 - x1
		dy = y2 - y1
		length = math.sqrt(dx**2 + dy**2)
		if length == 0:
			return
		
		# Ajustar el punto final para que la flecha termine en el borde del nodo
		node_radius = 18
		ratio = (length - node_radius) / length
		x2_adj = x1 + dx * ratio
		y2_adj = y1 + dy * ratio
		
		# Dibujar línea con flecha
		self.canvas.create_line(x1, y1, x2_adj, y2_adj, fill="#333333", width=2, arrow=tk.LAST, arrowshape=(10, 12, 5))
		
		mid_x = (x1 + x2) / 2
		mid_y = (y1 + y2) / 2
		
		# Formatear peso
		peso_txt = f"{int(peso)}" if peso == int(peso) else f"{peso:.1f}"
		
		# Fondo para etiqueta
		self.canvas.create_rectangle(
			mid_x - 12, mid_y - 10,
			mid_x + 12, mid_y + 10,
			fill="#ffffcc", outline="#999999"
		)
		self.canvas.create_text(
			mid_x, mid_y,
			text=peso_txt, fill="#000000",
			font=("MS Sans Serif", 9, "bold")
		)
	
	def _draw_curved_edge(self, x1: float, y1: float, x2: float, y2: float, arista_id: str, peso: float, curvatura: float) -> None:
		"""Dibuja una arista curva con peso y flecha (dirigida)"""
		mid_x = (x1 + x2) / 2
		mid_y = (y1 + y2) / 2
		
		dx = x2 - x1
		dy = y2 - y1
		length = math.sqrt(dx**2 + dy**2)
		if length == 0:
			return
		
		perp_x = -dy / length
		perp_y = dx / length
		
		control_x = mid_x + perp_x * curvatura
		control_y = mid_y + perp_y * curvatura
		
		# Ajustar punto final para la flecha
		node_radius = 18
		# Calcular dirección desde el punto de control al destino
		dx_ctrl = x2 - control_x
		dy_ctrl = y2 - control_y
		len_ctrl = math.sqrt(dx_ctrl**2 + dy_ctrl**2)
		if len_ctrl > 0:
			x2_adj = x2 - (dx_ctrl / len_ctrl) * node_radius
			y2_adj = y2 - (dy_ctrl / len_ctrl) * node_radius
		else:
			x2_adj, y2_adj = x2, y2
		
		# Dibujar curva
		self.canvas.create_line(
			x1, y1, control_x, control_y, x2_adj, y2_adj,
			fill="#333333", width=2, smooth=True, arrow=tk.LAST, arrowshape=(10, 12, 5)
		)
		
		peso_txt = f"{int(peso)}" if peso == int(peso) else f"{peso:.1f}"
		
		self.canvas.create_rectangle(
			control_x - 12, control_y - 10,
			control_x + 12, control_y + 10,
			fill="#ffffcc", outline="#999999"
		)
		self.canvas.create_text(
			control_x, control_y,
			text=peso_txt, fill="#000000",
			font=("MS Sans Serif", 9, "bold")
		)
	
	def _draw_loop(self, x: float, y: float, arista_id: str, peso: float, idx: int, total: int) -> None:
		"""Dibuja un bucle con peso y flecha (dirigido)"""
		radius = 18
		loop_radius = 20
		
		if total > 1:
			angle_offset = (idx - (total - 1) / 2) * (360 / (total + 2))
			angle_rad = math.radians(angle_offset - 90)
		else:
			angle_rad = math.radians(-90)
		
		distance = radius + loop_radius
		loop_x = x + distance * math.cos(angle_rad)
		loop_y = y + distance * math.sin(angle_rad)
		
		# Dibujar bucle como arco con flecha
		self.canvas.create_oval(
			loop_x - loop_radius, loop_y - loop_radius,
			loop_x + loop_radius, loop_y + loop_radius,
			outline="#333333", width=2, fill=""
		)
		
		# Dibujar flecha pequeña para indicar dirección (en sentido horario)
		arrow_angle = angle_rad + math.pi / 2
		arrow_x = loop_x + loop_radius * math.cos(arrow_angle + 0.3)
		arrow_y = loop_y + loop_radius * math.sin(arrow_angle + 0.3)
		arrow_dx = math.cos(arrow_angle + math.pi/2) * 6
		arrow_dy = math.sin(arrow_angle + math.pi/2) * 6
		self.canvas.create_line(
			arrow_x - arrow_dx, arrow_y - arrow_dy,
			arrow_x + arrow_dx, arrow_y + arrow_dy,
			fill="#333333", width=2, arrow=tk.LAST, arrowshape=(6, 8, 4)
		)
		
		peso_txt = f"{int(peso)}" if peso == int(peso) else f"{peso:.1f}"
		
		label_distance = loop_radius + 12
		label_x = loop_x + label_distance * math.cos(angle_rad)
		label_y = loop_y + label_distance * math.sin(angle_rad)
		
		self.canvas.create_rectangle(
			label_x - 12, label_y - 8,
			label_x + 12, label_y + 8,
			fill="#ffffcc", outline="#999999"
		)
		self.canvas.create_text(
			label_x, label_y,
			text=peso_txt, fill="#000000",
			font=("MS Sans Serif", 9, "bold")
		)
	
	# ==================== ALGORITMO DE FLOYD ====================
	
	def _ejecutar_floyd(self) -> None:
		"""Ejecuta el algoritmo de Floyd"""
		if len(self.vertices) < 2:
			messagebox.showerror("Error", "Se necesitan al menos 2 vértices")
			return
		
		if not self.aristas:
			messagebox.showerror("Error", "Se necesita al menos una arista")
			return
		
		if not self._es_conexo():
			messagebox.showwarning("Advertencia", "El grafo no es conexo. Algunas distancias serán infinitas.")
		
		n = len(self.vertices)
		INF = float('inf')
		
		# Inicializar matriz de distancias
		D: List[List[float]] = [[INF] * n for _ in range(n)]
		
		# Distancia de cada vértice a sí mismo es 0
		for i in range(n):
			D[i][i] = 0
		
		# Mapeo de vértices a índices
		idx = {v: i for i, v in enumerate(self.vertices)}
		
		# Llenar con las aristas existentes (grafo dirigido)
		for datos in self.aristas.values():
			u, v, peso = datos['u'], datos['v'], datos['peso']
			i, j = idx[u], idx[v]
			D[i][j] = min(D[i][j], peso)
		
		# Guardar matriz inicial (D^0)
		self.matrices_intermedias = [(0, [row[:] for row in D])]
		
		# Algoritmo de Floyd
		for k in range(n):
			for i in range(n):
				for j in range(n):
					if D[i][k] + D[k][j] < D[i][j]:
						D[i][j] = D[i][k] + D[k][j]
			
			# Guardar matriz intermedia D^(k+1)
			self.matrices_intermedias.append((k + 1, [row[:] for row in D]))
		
		self.matriz_distancias = D
		
		# Calcular métricas
		self._calcular_metricas()
		
		# Mostrar resultados
		self._mostrar_resultados()
		self._mostrar_matrices()
		
		self.status.configure(text="Floyd ejecutado ✓")
	
	def _calcular_metricas(self) -> None:
		"""Calcula excentricidades, radio, diámetro, centros y mediana"""
		n = len(self.vertices)
		INF = float('inf')
		
		# Calcular excentricidades
		self.excentricidades = {}
		for i, v in enumerate(self.vertices):
			max_dist = 0
			for j in range(n):
				if i != j and self.matriz_distancias[i][j] != INF:
					max_dist = max(max_dist, self.matriz_distancias[i][j])
				elif i != j and self.matriz_distancias[i][j] == INF:
					max_dist = INF
					break
			self.excentricidades[v] = max_dist
		
		# Radio = mínima excentricidad
		exc_finitas = [e for e in self.excentricidades.values() if e != INF]
		self.radio = min(exc_finitas) if exc_finitas else INF
		
		# Diámetro = máxima excentricidad
		self.diametro = max(exc_finitas) if exc_finitas else INF
		
		# Centros = vértices con excentricidad igual al radio
		self.centros = [v for v, e in self.excentricidades.items() if e == self.radio]
		
		# Calcular suma de distancias para cada vértice
		self.sumas_distancias = {}
		for i, v in enumerate(self.vertices):
			suma = 0
			for j in range(n):
				if self.matriz_distancias[i][j] != INF:
					suma += self.matriz_distancias[i][j]
				else:
					suma = INF
					break
			self.sumas_distancias[v] = suma
		
		# Mediana = vértice(s) con mínima suma de distancias
		sumas_finitas = [s for s in self.sumas_distancias.values() if s != INF]
		if sumas_finitas:
			min_suma = min(sumas_finitas)
			self.mediana = [v for v, s in self.sumas_distancias.items() if s == min_suma]
		else:
			self.mediana = []
	
	def _mostrar_resultados(self) -> None:
		"""Muestra los resultados calculados"""
		self.txt_resultados.configure(state="normal")
		self.txt_resultados.delete("1.0", tk.END)
		
		INF = float('inf')
		
		def fmt(val):
			if val == INF:
				return "∞"
			return f"{val:.1f}" if isinstance(val, float) and val != int(val) else str(int(val))
		
		# Excentricidades
		self.txt_resultados.insert(tk.END, "══ EXCENTRICIDADES ══\n")
		for v in self.vertices:
			self.txt_resultados.insert(tk.END, f"  e({v}) = {fmt(self.excentricidades.get(v, INF))}\n")
		
		self.txt_resultados.insert(tk.END, "\n══ RADIO ══\n")
		self.txt_resultados.insert(tk.END, f"  r(G) = {fmt(self.radio)}\n")
		
		self.txt_resultados.insert(tk.END, "\n══ DIÁMETRO ══\n")
		self.txt_resultados.insert(tk.END, f"  d(G) = {fmt(self.diametro)}\n")
		
		self.txt_resultados.insert(tk.END, "\n══ CENTRO(S) ══\n")
		if self.centros:
			self.txt_resultados.insert(tk.END, f"  {', '.join(self.centros)}\n")
		else:
			self.txt_resultados.insert(tk.END, "  (ninguno)\n")
		
		self.txt_resultados.insert(tk.END, "\n══ DISTANCIA VÉRTICES ══\n")
		for v in self.vertices:
			self.txt_resultados.insert(tk.END, f"  σ({v}) = {fmt(self.sumas_distancias.get(v, INF))}\n")
		
		self.txt_resultados.insert(tk.END, "\n══ MEDIANA ══\n")
		if self.mediana:
			self.txt_resultados.insert(tk.END, f"  {', '.join(self.mediana)}\n")
		else:
			self.txt_resultados.insert(tk.END, "  (ninguna)\n")
		
		self.txt_resultados.configure(state="disabled")
	
	def _limpiar_resultados(self) -> None:
		"""Limpia el panel de resultados"""
		self.txt_resultados.configure(state="normal")
		self.txt_resultados.delete("1.0", tk.END)
		self.txt_resultados.insert(tk.END, "Ejecuta Floyd para\nver resultados.")
		self.txt_resultados.configure(state="disabled")
	
	def _limpiar_matrices(self) -> None:
		"""Limpia el panel de matrices"""
		for widget in self.frame_matrices.winfo_children():
			widget.destroy()
	
	def _mostrar_matrices(self) -> None:
		"""Muestra las matrices de Floyd paso a paso"""
		self._limpiar_matrices()
		
		INF = float('inf')
		n = len(self.vertices)
		
		for k, matriz in self.matrices_intermedias:
			# Frame para cada matriz
			frame = ttk.Frame(self.frame_matrices, style="Panel.TFrame", padding=4)
			frame.pack(side=tk.LEFT, padx=4, pady=3)
			
			# Título
			titulo = "D⁰ (Inicial)" if k == 0 else f"D^{k}"
			lbl_titulo = ttk.Label(frame, text=titulo, font=("MS Sans Serif", 8, "bold"))
			lbl_titulo.pack()
			
			# Frame para la tabla
			tabla = ttk.Frame(frame)
			tabla.pack()
			
			# Encabezado de columnas
			ttk.Label(tabla, text="", width=3).grid(row=0, column=0)
			for j, v in enumerate(self.vertices):
				lbl = ttk.Label(tabla, text=v, width=5, font=("Consolas", 7, "bold"))
				lbl.grid(row=0, column=j+1)
			
			# Filas
			for i, v in enumerate(self.vertices):
				lbl_row = ttk.Label(tabla, text=v, width=3, font=("Consolas", 7, "bold"))
				lbl_row.grid(row=i+1, column=0)
				
				for j in range(n):
					valor = matriz[i][j]
					if valor == INF:
						texto = "∞"
						bg = "#ffcccc"
					elif valor == 0:
						texto = "0"
						bg = "#e0e0e0"
					else:
						texto = f"{valor:.0f}" if valor == int(valor) else f"{valor:.1f}"
						bg = "#ccffcc"
					
					celda = tk.Label(tabla, text=texto, width=5, bg=bg, font=("Consolas", 7), relief="solid", borderwidth=1)
					celda.grid(row=i+1, column=j+1)
		
		# Actualizar scroll region
		self.frame_matrices.update_idletasks()
		self.canvas_matrices.configure(scrollregion=self.canvas_matrices.bbox("all"))
	
	# ==================== GUARDAR / CARGAR ====================
	
	def _serialize(self) -> str:
		"""Serializa el grafo a texto"""
		lines = ["# Grafo Floyd"]
		lines.append(f"vertices:{','.join(self.vertices)}")
		
		for letra, datos in self.aristas.items():
			u, v, peso = datos['u'], datos['v'], datos['peso']
			lines.append(f"arista:{letra},{u},{v},{peso}")
		
		return "\n".join(lines) + "\n"
	
	def _parse(self, content: str) -> bool:
		"""Parsea el contenido de un archivo"""
		self.vertices = []
		self.aristas = {}
		self.posiciones = {}
		
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
						letra = parts[0].strip()
						u = parts[1].strip()
						v = parts[2].strip()
						peso = float(parts[3].strip())
						self.aristas[letra] = {'u': u, 'v': v, 'peso': peso}
			
			return True
		except Exception:
			return False
	
	def _on_save(self) -> None:
		"""Guarda el grafo"""
		path = filedialog.asksaveasfilename(
			title="Guardar grafo Floyd",
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
			title="Guardar grafo Floyd",
			defaultextension=".txt",
			filetypes=[("Texto", "*.txt"), ("Todos", "*.*")]
		)
		if not path:
			return
		try:
			with open(path, "w", encoding="utf-8") as f:
				f.write(self._serialize())
			messagebox.showinfo("Éxito", "Grafo guardado correctamente")
			self.app.navigate("grafos")
		except Exception as e:
			messagebox.showerror("Error", f"No se pudo guardar: {e}")
	
	def _on_load(self) -> None:
		"""Carga un grafo"""
		path = filedialog.askopenfilename(
			title="Cargar grafo Floyd",
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
		
		# Limpiar resultados anteriores
		self.matriz_distancias = []
		self.matrices_intermedias = []
		self.excentricidades = {}
		self._limpiar_resultados()
		self._limpiar_matrices()
		
		self._draw_grafo()
		self.status.configure(text=f"Cargado: {len(self.vertices)} vértices, {len(self.aristas)} aristas")
