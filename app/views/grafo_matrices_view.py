import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Dict, Set, List, Tuple, Optional
import math
import random


class GrafoMatricesView(ttk.Frame):
	def __init__(self, parent: tk.Misc, app) -> None:
		super().__init__(parent)
		
		title = ttk.Label(self, text="Matrices de Grafo Dirigido", style="Title.TLabel")
		title.pack(pady=(20, 5))
		
		# Panel principal
		main_panel = ttk.Frame(self, padding=6)
		main_panel.pack(fill=tk.BOTH, expand=True)
		
		# Panel izquierdo: controles y grafo
		left_panel = ttk.Frame(main_panel, style="Panel.TFrame", padding=10)
		left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 6))
		
		# Sección: Agregar elementos
		lbl_add = ttk.Label(left_panel, text="Grafo Dirigido", font=("MS Sans Serif", 10, "bold"))
		lbl_add.grid(row=0, column=0, columnspan=2, pady=(0, 5), sticky="w")
		
		ttk.Label(left_panel, text="Vértice:").grid(row=1, column=0, sticky="w", pady=2)
		self.entry_vertice = ttk.Entry(left_panel, width=12)
		self.entry_vertice.grid(row=1, column=1, pady=2)
		
		btn_add_vertice = ttk.Button(left_panel, text="Agregar vértice", command=self._on_agregar_vertice, style="Retro.TButton")
		btn_add_vertice.grid(row=2, column=0, columnspan=2, pady=2, sticky="ew")
		
		ttk.Label(left_panel, text="Arista (u→v):").grid(row=3, column=0, sticky="w", pady=2)
		frame_arista = ttk.Frame(left_panel)
		frame_arista.grid(row=3, column=1, pady=2)
		self.entry_u = ttk.Entry(frame_arista, width=5)
		self.entry_u.pack(side=tk.LEFT)
		ttk.Label(frame_arista, text="→").pack(side=tk.LEFT, padx=2)
		self.entry_v = ttk.Entry(frame_arista, width=5)
		self.entry_v.pack(side=tk.LEFT)
		
		btn_add_arista = ttk.Button(left_panel, text="Agregar arista", command=self._on_agregar_arista, style="Retro.TButton")
		btn_add_arista.grid(row=4, column=0, columnspan=2, pady=2, sticky="ew")
		
		btn_limpiar = ttk.Button(left_panel, text="Limpiar grafo", command=self._on_limpiar)
		btn_limpiar.grid(row=5, column=0, columnspan=2, pady=(5, 2), sticky="ew")
		
		# Canvas para visualizar el grafo
		self.canvas = tk.Canvas(left_panel, background="#ffffff", width=300, height=250)
		self.canvas.grid(row=6, column=0, columnspan=2, pady=(10, 0))
		
		# Botón calcular matrices
		btn_calcular = ttk.Button(left_panel, text="Calcular Matrices", command=self._on_calcular_matrices, style="Retro.TButton")
		btn_calcular.grid(row=7, column=0, columnspan=2, pady=(10, 0), sticky="ew")
		
		# Panel derecho: matrices
		right_panel = ttk.Frame(main_panel, style="Panel.TFrame", padding=10)
		right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		
		# Canvas con scroll para mostrar todas las matrices
		canvas_frame = ttk.Frame(right_panel)
		canvas_frame.pack(fill=tk.BOTH, expand=True)
		
		# Canvas y scrollbar
		self.matrices_canvas = tk.Canvas(canvas_frame, bg="#ffffff")
		scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.matrices_canvas.yview)
		self.scrollable_frame = ttk.Frame(self.matrices_canvas)
		
		self.scrollable_frame.bind(
			"<Configure>",
			lambda e: self.matrices_canvas.configure(scrollregion=self.matrices_canvas.bbox("all"))
		)
		
		self.matrices_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
		self.matrices_canvas.configure(yscrollcommand=scrollbar.set)
		
		self.matrices_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
		
		# Bind mousewheel
		def _on_mousewheel(event):
			self.matrices_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
		self.matrices_canvas.bind_all("<MouseWheel>", _on_mousewheel)
		
		# Diccionario para almacenar los frames de cada matriz
		self.matrices_frames = {}
		self.matrices_grid_row = 0
		self.matrices_grid_col = 0
		
		# Botón volver
		back = ttk.Button(self, text="← Volver", command=lambda: app.navigate("grafos"))
		back.pack(pady=6)
		
		self.app = app
		
		# Estructuras de datos
		self.vertices: Set[str] = set()
		self.aristas: Dict[str, Tuple[str, str]] = {}  # {arista_id: (u, v)}
		self.posiciones: Dict[str, Tuple[float, float]] = {}
		self.arista_counter = 0
	
	def _on_agregar_vertice(self) -> None:
		"""Agrega un vértice al grafo"""
		vertice = self.entry_vertice.get().strip()
		
		if not vertice:
			messagebox.showerror("Error", "Ingresa un vértice")
			return
		
		if vertice in self.vertices:
			messagebox.showwarning("Advertencia", f"El vértice {vertice} ya existe")
			return
		
		self.vertices.add(vertice)
		self.entry_vertice.delete(0, tk.END)
		self._draw()
	
	def _on_agregar_arista(self) -> None:
		"""Agrega una arista dirigida al grafo"""
		u = self.entry_u.get().strip()
		v = self.entry_v.get().strip()
		
		if not u or not v:
			messagebox.showerror("Error", "Ingresa ambos vértices")
			return
		
		if u not in self.vertices or v not in self.vertices:
			messagebox.showerror("Error", "Ambos vértices deben existir")
			return
		
		arista_id = f"e{self.arista_counter}"
		self.arista_counter += 1
		self.aristas[arista_id] = (u, v)
		
		self.entry_u.delete(0, tk.END)
		self.entry_v.delete(0, tk.END)
		self._draw()
	
	def _on_limpiar(self) -> None:
		"""Limpia el grafo"""
		self.vertices = set()
		self.aristas = {}
		self.posiciones = {}
		self.arista_counter = 0
		# Limpiar todas las matrices
		for widget in self.scrollable_frame.winfo_children():
			widget.destroy()
		self.matrices_frames = {}
		# Resetear posiciones del grid
		self.matrices_grid_row = 0
		self.matrices_grid_col = 0
		self._draw()
	
	def _calcular_posiciones(self) -> None:
		"""Calcula posiciones para el grafo"""
		n = len(self.vertices)
		if n == 0:
			return
		
		vertices_list = list(self.vertices)
		
		# Layout circular
		center_x, center_y = 150, 125
		radius = min(100, 80)
		
		for i, vertice in enumerate(vertices_list):
			angle = 2 * math.pi * i / n - math.pi / 2
			self.posiciones[vertice] = (
				center_x + radius * math.cos(angle),
				center_y + radius * math.sin(angle)
			)
	
	def _draw(self) -> None:
		"""Dibuja el grafo dirigido"""
		self.canvas.delete("all")
		
		if not self.vertices:
			self.canvas.create_text(150, 125, text="Grafo vacío", fill="#999999", font=("MS Sans Serif", 10))
			return
		
		self._calcular_posiciones()
		
		# Agrupar aristas por par de vértices (sin dirección) para detectar bidireccionales
		aristas_por_par_no_dir = {}
		aristas_por_par_dir = {}
		
		for arista_id, (u, v) in self.aristas.items():
			# Par sin dirección (para detectar bidireccionales)
			par_no_dir = tuple(sorted([u, v]))
			if par_no_dir not in aristas_por_par_no_dir:
				aristas_por_par_no_dir[par_no_dir] = []
			aristas_por_par_no_dir[par_no_dir].append((arista_id, u, v))
			
			# Par con dirección (para paralelas en misma dirección)
			par_dir = (u, v)
			if par_dir not in aristas_por_par_dir:
				aristas_por_par_dir[par_dir] = []
			aristas_por_par_dir[par_dir].append(arista_id)
		
		# Dibujar aristas (flechas)
		aristas_dibujadas = set()
		
		for par_no_dir, aristas_grupo in aristas_por_par_no_dir.items():
			u, v = par_no_dir
			if u not in self.posiciones or v not in self.posiciones:
				continue
			
			x1, y1 = self.posiciones[u]
			x2, y2 = self.posiciones[v]
			
			# Separar aristas por dirección
			aristas_u_v = [(aid, u_orig, v_orig) for aid, u_orig, v_orig in aristas_grupo if u_orig == u and v_orig == v]
			aristas_v_u = [(aid, u_orig, v_orig) for aid, u_orig, v_orig in aristas_grupo if u_orig == v and v_orig == u]
			
			total_aristas = len(aristas_u_v) + len(aristas_v_u)
			
			# SIEMPRE curvar si hay más de una arista entre estos vértices (en cualquier dirección)
			if total_aristas > 1:
				# Hay múltiples aristas, curvar todas con mayor separación
				# Calcular distancia entre vértices
				distancia = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
				
				# Curvatura base y incremento ajustados según distancia
				# Para distancias cortas, usar valores más pequeños pero aún visibles
				# Para distancias largas, usar valores más grandes
				if distancia < 80:
					curvatura_base = 40
					incremento = 35
				elif distancia < 150:
					curvatura_base = 60
					incremento = 50
				else:
					curvatura_base = 80
					incremento = 70
				
				# Dibujar aristas u->v (curvatura positiva)
				total_u_v = len(aristas_u_v)
				for idx, (arista_id, _, _) in enumerate(aristas_u_v):
					# Distribuir uniformemente alrededor del centro
					if total_u_v == 1:
						# Si solo hay una en esta dirección pero hay otra en dirección opuesta
						curvatura = curvatura_base
					else:
						# Distribuir: para 2 aristas: -incremento/2, +incremento/2
						# Para 3: -incremento, 0, +incremento
						offset = (idx - (total_u_v - 1) / 2) * incremento
						curvatura = curvatura_base + offset
					self._draw_curved_arrow(x1, y1, x2, y2, curvatura)
					aristas_dibujadas.add(arista_id)
				
				# Dibujar aristas v->u (curvatura negativa, lado opuesto)
				total_v_u = len(aristas_v_u)
				for idx, (arista_id, _, _) in enumerate(aristas_v_u):
					# Distribuir en el lado opuesto con la misma lógica
					if total_v_u == 1:
						curvatura = -curvatura_base
					else:
						offset = (idx - (total_v_u - 1) / 2) * incremento
						curvatura = -(curvatura_base + offset)
					self._draw_curved_arrow(x2, y2, x1, y1, curvatura)
					aristas_dibujadas.add(arista_id)
			else:
				# Solo una arista, dibujar recta
				if aristas_u_v:
					arista_id, _, _ = aristas_u_v[0]
					self._draw_arrow(x1, y1, x2, y2)
					aristas_dibujadas.add(arista_id)
				elif aristas_v_u:
					arista_id, _, _ = aristas_v_u[0]
					self._draw_arrow(x2, y2, x1, y1)
					aristas_dibujadas.add(arista_id)
		
		# Dibujar vértices
		radius = 15
		for vertice, (x, y) in self.posiciones.items():
			self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill="#4da3ff", outline="#255eaa", width=2)
			self.canvas.create_text(x, y, text=str(vertice), fill="#ffffff", font=("MS Sans Serif", 10, "bold"))
	
	def _draw_arrow(self, x1: float, y1: float, x2: float, y2: float) -> None:
		"""Dibuja una flecha dirigida recta"""
		radius = 15
		# Calcular punto en el borde del círculo destino
		dx = x2 - x1
		dy = y2 - y1
		length = math.sqrt(dx**2 + dy**2)
		if length == 0:
			return
		
		# Punto de inicio ajustado al borde del círculo origen
		start_x = x1 + (dx / length) * radius
		start_y = y1 + (dy / length) * radius
		
		# Punto final ajustado al borde del círculo destino
		end_x = x2 - (dx / length) * radius
		end_y = y2 - (dy / length) * radius
		
		# Dibujar línea
		self.canvas.create_line(start_x, start_y, end_x, end_y, fill="#000000", width=2, arrow=tk.LAST, arrowshape=(10, 12, 3))
	
	def _draw_curved_arrow(self, x1: float, y1: float, x2: float, y2: float, curvatura: float) -> None:
		"""Dibuja una flecha dirigida curva con mayor separación visual"""
		radius = 15
		dx = x2 - x1
		dy = y2 - y1
		length = math.sqrt(dx**2 + dy**2)
		if length == 0:
			return
		
		# Calcular punto medio
		mid_x = (x1 + x2) / 2
		mid_y = (y1 + y2) / 2
		
		# Vector perpendicular normalizado (perpendicular a la línea)
		perp_x = -dy / length
		perp_y = dx / length
		
		# Usar la curvatura directamente (ya viene ajustada desde arriba)
		# Punto de control para la curva bezier cuadrática
		control_x = mid_x + perp_x * curvatura
		control_y = mid_y + perp_y * curvatura
		
		# Ajustar puntos de inicio y fin al borde de los círculos
		# Vector desde inicio hacia control
		dx_start = control_x - x1
		dy_start = control_y - y1
		len_start = math.sqrt(dx_start**2 + dy_start**2)
		if len_start > 0:
			start_x = x1 + (dx_start / len_start) * radius
			start_y = y1 + (dy_start / len_start) * radius
		else:
			start_x = x1
			start_y = y1
		
		# Vector desde control hacia fin
		dx_end = x2 - control_x
		dy_end = y2 - control_y
		len_end = math.sqrt(dx_end**2 + dy_end**2)
		if len_end > 0:
			end_x = x2 - (dx_end / len_end) * radius
			end_y = y2 - (dy_end / len_end) * radius
		else:
			end_x = x2
			end_y = y2
		
		# Crear múltiples puntos para una curva bezier suave y visible
		# Usar más puntos para curvas más suaves
		num_points = 15
		points = []
		
		for i in range(num_points + 1):
			t = i / num_points
			# Curva cuadrática bezier: (1-t)²P0 + 2(1-t)tP1 + t²P2
			px = (1-t)**2 * start_x + 2*(1-t)*t * control_x + t**2 * end_x
			py = (1-t)**2 * start_y + 2*(1-t)*t * control_y + t**2 * end_y
			points.extend([px, py])
		
		# Dibujar la curva con smooth=True para una curva suave y visible
		self.canvas.create_line(*points, fill="#000000", width=2, smooth=True, 
							   arrow=tk.LAST, arrowshape=(10, 12, 3), splinesteps=100)
	
	def _crear_tabla_matriz(self, titulo: str, headers: List[str], datos: List[List[str]]) -> None:
		"""Crea una tabla bonita para mostrar una matriz"""
		# Frame principal para esta matriz con borde
		matriz_frame = tk.Frame(self.scrollable_frame, bg="#e0e0e0", relief=tk.RAISED, bd=2)
		# Usar grid en lugar de pack para permitir múltiples columnas
		matriz_frame.grid(row=self.matrices_grid_row, column=self.matrices_grid_col, 
						  sticky="nsew", pady=5, padx=5)
		
		# Configurar pesos del grid para que se expandan
		self.scrollable_frame.columnconfigure(self.matrices_grid_col, weight=1)
		self.scrollable_frame.rowconfigure(self.matrices_grid_row, weight=0)
		
		# Frame interno con padding
		inner_frame = ttk.Frame(matriz_frame, padding=8)
		inner_frame.pack(fill=tk.BOTH, expand=True)
		
		# Título
		titulo_label = tk.Label(inner_frame, text=titulo, font=("MS Sans Serif", 13, "bold"),
								bg="#e0e0e0", fg="#255eaa")
		titulo_label.pack(pady=(0, 8))
		
		if not datos:
			ttk.Label(inner_frame, text="No hay datos para mostrar", font=("MS Sans Serif", 10)).pack()
			# Avanzar posición en el grid incluso si no hay datos
			if self.matrices_grid_col == 0:
				self.matrices_grid_col = 1
			else:
				self.matrices_grid_col = 0
				self.matrices_grid_row += 1
			return
		
		# Frame para la tabla con scroll horizontal si es necesario
		tabla_container = tk.Frame(inner_frame, bg="#ffffff")
		tabla_container.pack(fill=tk.BOTH, expand=True)
		
		# Canvas para scroll horizontal si la tabla es muy ancha
		canvas_tabla = tk.Canvas(tabla_container, bg="#ffffff", highlightthickness=0)
		scrollbar_h = ttk.Scrollbar(tabla_container, orient="horizontal", command=canvas_tabla.xview)
		scrollbar_v = ttk.Scrollbar(tabla_container, orient="vertical", command=canvas_tabla.yview)
		
		tabla_frame = tk.Frame(canvas_tabla, bg="#ffffff")
		
		tabla_frame.bind(
			"<Configure>",
			lambda e: canvas_tabla.configure(scrollregion=canvas_tabla.bbox("all"))
		)
		
		canvas_tabla.create_window((0, 0), window=tabla_frame, anchor="nw")
		canvas_tabla.configure(xscrollcommand=scrollbar_h.set, yscrollcommand=scrollbar_v.set)
		
		# Crear encabezados
		for col_idx, header in enumerate(headers):
			header_label = tk.Label(tabla_frame, text=str(header), font=("MS Sans Serif", 9, "bold"),
									 bg="#4da3ff", fg="#ffffff", relief=tk.RAISED, padx=6, pady=4,
									 width=12, anchor=tk.CENTER)
			header_label.grid(row=0, column=col_idx, sticky="nsew", padx=1, pady=1)
		
		# Crear filas de datos
		for row_idx, fila in enumerate(datos, start=1):
			for col_idx, valor in enumerate(fila):
				# Alternar colores de fondo
				bg_color = "#f0f0f0" if row_idx % 2 == 0 else "#ffffff"
				fg_color = "#000000"
				cell_label = tk.Label(tabla_frame, text=str(valor), font=("Courier", 8),
									  bg=bg_color, fg=fg_color, relief=tk.SUNKEN, padx=6, pady=4,
									  width=12, anchor=tk.CENTER)
				cell_label.grid(row=row_idx, column=col_idx, sticky="nsew", padx=1, pady=1)
		
		# Configurar pesos de columnas para que se expandan uniformemente
		for col_idx in range(len(headers)):
			tabla_frame.columnconfigure(col_idx, weight=1, minsize=80)
		
		# Pack scrollbars y canvas
		canvas_tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
		scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)
		
		# Bind mousewheel para scroll vertical
		def _on_mousewheel_tabla(event):
			canvas_tabla.yview_scroll(int(-1*(event.delta/120)), "units")
		canvas_tabla.bind_all("<MouseWheel>", _on_mousewheel_tabla)
		
		self.matrices_frames[titulo] = matriz_frame
		
		# Avanzar posición en el grid (2 columnas)
		if self.matrices_grid_col == 0:
			# Pasar a la segunda columna
			self.matrices_grid_col = 1
		else:
			# Pasar a la siguiente fila, primera columna
			self.matrices_grid_col = 0
			self.matrices_grid_row += 1
	
	def _on_calcular_matrices(self) -> None:
		"""Calcula todas las matrices"""
		if not self.vertices:
			messagebox.showwarning("Advertencia", "El grafo debe tener al menos un vértice")
			return
		
		# Limpiar todas las matrices anteriores
		for widget in self.scrollable_frame.winfo_children():
			widget.destroy()
		self.matrices_frames = {}
		
		# Resetear posiciones del grid (2 columnas)
		self.matrices_grid_row = 0
		self.matrices_grid_col = 0
		
		# Configurar 2 columnas en el scrollable_frame
		self.scrollable_frame.columnconfigure(0, weight=1)
		self.scrollable_frame.columnconfigure(1, weight=1)
		
		# Calcular y mostrar cada matriz
		self._mostrar_matriz_incidencia()
		self._mostrar_matriz_adyacencia_vertices()
		self._mostrar_matriz_adyacencia_aristas()
		self._mostrar_matriz_circuitos()
		self._mostrar_matriz_circuitos_fundamentales()
		self._mostrar_matriz_conjuntos_cortes()
		self._mostrar_matriz_cortes_fundamentales()
		
		# Actualizar scroll region
		self.matrices_canvas.update_idletasks()
		self.matrices_canvas.configure(scrollregion=self.matrices_canvas.bbox("all"))
	
	def _mostrar_matriz_incidencia(self) -> None:
		"""Calcula y muestra la matriz de incidencia"""
		vertices_list = sorted(list(self.vertices))
		aristas_list = sorted(list(self.aristas.keys()))
		
		if not aristas_list:
			self._crear_tabla_matriz("Matriz de Incidencia", ["Vértice"], [["No hay aristas en el grafo"]])
			return
		
		# Encabezados
		headers = ["Vértice"] + aristas_list
		
		# Filas
		datos = []
		for v in vertices_list:
			fila = [v]
			for a in aristas_list:
				u, w = self.aristas[a]
				if v == u:
					fila.append("+1")
				elif v == w:
					fila.append("-1")
				else:
					fila.append("0")
			datos.append(fila)
		
		self._crear_tabla_matriz("Matriz de Incidencia", headers, datos)
	
	def _mostrar_matriz_adyacencia_vertices(self) -> None:
		"""Calcula y muestra la matriz de adyacencia de vértices"""
		vertices_list = sorted(list(self.vertices))
		
		# Encabezados
		headers = ["Vértice"] + vertices_list
		
		# Crear matriz de adyacencia
		adj_matrix = {}
		for u in vertices_list:
			adj_matrix[u] = {}
			for v in vertices_list:
				adj_matrix[u][v] = 0
		
		# Llenar matriz
		for arista_id, (u, v) in self.aristas.items():
			if u in adj_matrix and v in adj_matrix[u]:
				adj_matrix[u][v] = 1
		
		# Preparar datos
		datos = []
		for u in vertices_list:
			fila = [u]
			for v in vertices_list:
				fila.append(str(adj_matrix[u][v]))
			datos.append(fila)
		
		self._crear_tabla_matriz("Matriz de Adyacencia de Vértices", headers, datos)
	
	def _mostrar_matriz_adyacencia_aristas(self) -> None:
		"""Calcula y muestra la matriz de adyacencia de aristas"""
		aristas_list = sorted(list(self.aristas.keys()))
		
		if not aristas_list:
			self._crear_tabla_matriz("Matriz de Adyacencia de Aristas", ["Arista"], [["No hay aristas en el grafo"]])
			return
		
		# Encabezados
		headers = ["Arista"] + aristas_list
		
		# Crear matriz de adyacencia de aristas
		adj_matrix = {}
		for a1 in aristas_list:
			adj_matrix[a1] = {}
			for a2 in aristas_list:
				adj_matrix[a1][a2] = 0
		
		# Llenar matriz: a1 -> a2 si el vértice final de a1 es el inicial de a2
		for a1 in aristas_list:
			_, v1_final = self.aristas[a1]
			for a2 in aristas_list:
				if a1 != a2:
					u2_inicial, _ = self.aristas[a2]
					if v1_final == u2_inicial:
						adj_matrix[a1][a2] = 1
		
		# Preparar datos
		datos = []
		for a1 in aristas_list:
			fila = [a1]
			for a2 in aristas_list:
				fila.append(str(adj_matrix[a1][a2]))
			datos.append(fila)
		
		self._crear_tabla_matriz("Matriz de Adyacencia de Aristas", headers, datos)
	
	def _mostrar_matriz_circuitos(self) -> None:
		"""Calcula y muestra la matriz de circuitos (todos los ciclos)"""
		circuitos = self._encontrar_circuitos()
		
		if not circuitos:
			self._crear_tabla_matriz("Matriz de Circuitos", ["Circuito"], [["No se encontraron circuitos en el grafo"]])
			return
		
		aristas_list = sorted(list(self.aristas.keys()))
		
		# Encabezados
		headers = ["Circuito"] + aristas_list
		
		# Preparar datos
		datos = []
		for idx, circuito in enumerate(circuitos):
			fila = [f"C{idx+1}"]
			for a in aristas_list:
				count = circuito.count(a)
				fila.append(str(count))
			datos.append(fila)
		
		self._crear_tabla_matriz("Matriz de Circuitos", headers, datos)
	
	def _mostrar_matriz_circuitos_fundamentales(self) -> None:
		"""Calcula y muestra la matriz de circuitos fundamentales"""
		circuitos_fund = self._encontrar_circuitos_fundamentales()
		
		if not circuitos_fund:
			self._crear_tabla_matriz("Matriz de Circuitos Fundamentales", ["Circuito"], [["No se encontraron circuitos fundamentales"]])
			return
		
		aristas_list = sorted(list(self.aristas.keys()))
		
		# Encabezados
		headers = ["Circuito Fund."] + aristas_list
		
		# Preparar datos
		datos = []
		for idx, circuito in enumerate(circuitos_fund):
			fila = [f"CF{idx+1}"]
			for a in aristas_list:
				count = circuito.count(a)
				fila.append(str(count))
			datos.append(fila)
		
		self._crear_tabla_matriz("Matriz de Circuitos Fundamentales", headers, datos)
	
	def _mostrar_matriz_conjuntos_cortes(self) -> None:
		"""Calcula y muestra la matriz de conjuntos de cortes"""
		cortes = self._encontrar_conjuntos_cortes()
		
		if not cortes:
			self._crear_tabla_matriz("Matriz de Conjuntos de Cortes", ["Corte"], [["No se encontraron conjuntos de cortes"]])
			return
		
		aristas_list = sorted(list(self.aristas.keys()))
		
		# Encabezados
		headers = ["Corte"] + aristas_list
		
		# Preparar datos
		datos = []
		for idx, corte in enumerate(cortes):
			fila = [f"K{idx+1}"]
			for a in aristas_list:
				fila.append("1" if a in corte else "0")
			datos.append(fila)
		
		self._crear_tabla_matriz("Matriz de Conjuntos de Cortes", headers, datos)
	
	def _mostrar_matriz_cortes_fundamentales(self) -> None:
		"""Calcula y muestra la matriz de cortes fundamentales"""
		cortes_fund = self._encontrar_cortes_fundamentales()
		
		if not cortes_fund:
			self._crear_tabla_matriz("Matriz de Cortes Fundamentales", ["Corte"], [["No se encontraron cortes fundamentales"]])
			return
		
		aristas_list = sorted(list(self.aristas.keys()))
		
		# Encabezados
		headers = ["Corte Fund."] + aristas_list
		
		# Preparar datos
		datos = []
		for idx, corte in enumerate(cortes_fund):
			fila = [f"KF{idx+1}"]
			for a in aristas_list:
				fila.append("1" if a in corte else "0")
			datos.append(fila)
		
		self._crear_tabla_matriz("Matriz de Cortes Fundamentales", headers, datos)
	
	# ========== ALGORITMOS PARA ENCONTRAR CIRCUITOS Y CORTES ==========
	
	def _encontrar_circuitos(self) -> List[List[str]]:
		"""Encuentra todos los circuitos (ciclos) en el grafo dirigido"""
		circuitos = []
		circuitos_set = set()  # Para evitar duplicados
		
		# Construir lista de adyacencia
		adyacencia = {v: [] for v in self.vertices}
		for arista_id, (u, v) in self.aristas.items():
			adyacencia[u].append((v, arista_id))
		
		def dfs_circuito(vertice_actual: str, camino_aristas: List[str], vertices_camino: List[str]) -> None:
			# Buscar aristas salientes
			for vecino, arista_id in adyacencia.get(vertice_actual, []):
				if vecino in vertices_camino:
					# Encontramos un ciclo
					idx_inicio = vertices_camino.index(vecino)
					ciclo_aristas = camino_aristas[idx_inicio:] + [arista_id]
					# Normalizar: ordenar y convertir a tupla para comparar
					ciclo_tupla = tuple(sorted(ciclo_aristas))
					if ciclo_tupla not in circuitos_set:
						circuitos_set.add(ciclo_tupla)
						circuitos.append(ciclo_aristas)
				else:
					# Continuar DFS
					dfs_circuito(vecino, camino_aristas + [arista_id], vertices_camino + [vecino])
		
		# Intentar desde cada vértice
		for vertice_inicial in self.vertices:
			dfs_circuito(vertice_inicial, [], [vertice_inicial])
		
		return circuitos
	
	def _encontrar_circuitos_fundamentales(self) -> List[List[str]]:
		"""Encuentra circuitos fundamentales basados en un árbol generador"""
		# Encontrar un árbol generador dirigido (spanning tree)
		arbol = self._encontrar_arbol_generador()
		
		if not arbol or len(arbol) == 0:
			return []
		
		aristas_arbol = set(arbol)
		aristas_coarbol = set(self.aristas.keys()) - aristas_arbol
		
		if not aristas_coarbol:
			return []
		
		circuitos_fund = []
		
		# Para cada arista del coárbol, encontrar el circuito fundamental
		for arista_coarbol in aristas_coarbol:
			u, v = self.aristas[arista_coarbol]
			# Encontrar camino en el árbol de v a u (si existe)
			camino = self._encontrar_camino_en_arbol(arbol, v, u)
			if camino:
				# El circuito fundamental es: camino de v a u + arista del coárbol (u -> v)
				circuito = camino + [arista_coarbol]
				circuitos_fund.append(circuito)
			else:
				# Si no hay camino, el circuito fundamental es solo la arista (si forma ciclo)
				# Verificar si u y v están conectados de alguna manera
				if self._estan_conectados_en_arbol(arbol, u, v):
					circuito = [arista_coarbol]
					circuitos_fund.append(circuito)
		
		return circuitos_fund
	
	def _encontrar_arbol_generador(self) -> List[str]:
		"""Encuentra un árbol generador usando DFS"""
		if not self.vertices:
			return []
		
		arbol = []
		visitados = set()
		
		def dfs_arbol(vertice: str) -> None:
			visitados.add(vertice)
			for arista_id, (u, v) in self.aristas.items():
				if u == vertice and v not in visitados:
					arbol.append(arista_id)
					dfs_arbol(v)
		
		# Empezar desde el primer vértice
		vertice_inicial = list(self.vertices)[0]
		dfs_arbol(vertice_inicial)
		
		# Si hay vértices no conectados, intentar conectarlos
		for vertice in self.vertices:
			if vertice not in visitados:
				dfs_arbol(vertice)
		
		return arbol
	
	def _encontrar_camino_en_arbol(self, arbol: List[str], inicio: str, fin: str) -> List[str]:
		"""Encuentra un camino en el árbol dirigido de inicio a fin"""
		# Construir grafo del árbol (dirigido)
		grafo_arbol = {}
		for arista_id in arbol:
			u, v = self.aristas[arista_id]
			if u not in grafo_arbol:
				grafo_arbol[u] = []
			grafo_arbol[u].append((v, arista_id))
		
		# DFS para encontrar camino
		def dfs_camino(vertice_actual: str, camino_actual: List[str], visitados: Set[str]) -> Optional[List[str]]:
			if vertice_actual == fin:
				return camino_actual
			
			if vertice_actual in grafo_arbol:
				for vecino, arista_id in grafo_arbol[vertice_actual]:
					if vecino not in visitados:
						visitados.add(vecino)
						resultado = dfs_camino(vecino, camino_actual + [arista_id], visitados)
						if resultado:
							return resultado
						visitados.remove(vecino)
			return None
		
		resultado = dfs_camino(inicio, [], {inicio})
		return resultado if resultado else []
	
	def _estan_conectados_en_arbol(self, arbol: List[str], u: str, v: str) -> bool:
		"""Verifica si dos vértices están conectados en el árbol"""
		camino = self._encontrar_camino_en_arbol(arbol, u, v)
		return len(camino) > 0
	
	def _encontrar_conjuntos_cortes(self) -> List[Set[str]]:
		"""Encuentra conjuntos de cortes (edge cuts)"""
		cortes = []
		
		# Un corte es un conjunto de aristas que al eliminarlas desconecta el grafo
		# Para cada partición de vértices (S, V-S), encontrar aristas entre ellos
		
		vertices_list = list(self.vertices)
		n = len(vertices_list)
		
		# Generar todas las particiones no triviales
		for i in range(1, 2**(n-1)):  # Evitar partición vacía y completa
			S = set()
			for j in range(n):
				if (i >> j) & 1:
					S.add(vertices_list[j])
			
			if not S or S == set(vertices_list):
				continue
			
			# Encontrar aristas entre S y V-S
			corte = set()
			for arista_id, (u, v) in self.aristas.items():
				if (u in S and v not in S) or (u not in S and v in S):
					corte.add(arista_id)
			
			if corte and corte not in cortes:
				cortes.append(corte)
		
		return cortes
	
	def _encontrar_cortes_fundamentales(self) -> List[Set[str]]:
		"""Encuentra cortes fundamentales basados en un árbol generador"""
		arbol = self._encontrar_arbol_generador()
		
		if not arbol:
			return []
		
		aristas_arbol = set(arbol)
		cortes_fund = []
		
		# Para cada arista del árbol, encontrar el corte fundamental
		for arista_arbol in aristas_arbol:
			u, v = self.aristas[arista_arbol]
			# El corte fundamental contiene la arista del árbol
			# y todas las aristas del coárbol que conectan los dos componentes
			corte = {arista_arbol}
			
			# Encontrar componente de u sin la arista del árbol
			componente_u = self._encontrar_componente_sin_arista(arbol, arista_arbol, u)
			
			# Agregar aristas del coárbol que conectan componente_u con el resto
			aristas_coarbol = set(self.aristas.keys()) - aristas_arbol
			for arista_coarbol in aristas_coarbol:
				u_a, v_a = self.aristas[arista_coarbol]
				if (u_a in componente_u and v_a not in componente_u) or (u_a not in componente_u and v_a in componente_u):
					corte.add(arista_coarbol)
			
			if corte:
				cortes_fund.append(corte)
		
		return cortes_fund
	
	def _encontrar_componente_sin_arista(self, arbol: List[str], arista_excluida: str, vertice_inicial: str) -> Set[str]:
		"""Encuentra el componente conexo dirigido sin una arista específica"""
		componente = set()
		visitados = set()
		
		# Construir grafo del árbol sin la arista excluida
		grafo_arbol = {}
		for arista_id in arbol:
			if arista_id == arista_excluida:
				continue
			u, v = self.aristas[arista_id]
			if u not in grafo_arbol:
				grafo_arbol[u] = []
			grafo_arbol[u].append(v)
		
		def dfs_componente(vertice: str) -> None:
			visitados.add(vertice)
			componente.add(vertice)
			if vertice in grafo_arbol:
				for vecino in grafo_arbol[vertice]:
					if vecino not in visitados:
						dfs_componente(vecino)
		
		dfs_componente(vertice_inicial)
		return componente

