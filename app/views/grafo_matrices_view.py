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
		
		ttk.Label(left_panel, text="Tipo de grafo:").grid(row=1, column=0, sticky="w", pady=2)
		self.tipo_grafo = tk.StringVar(value="Dirigido")
		tipo_combo = ttk.Combobox(
			left_panel,
			textvariable=self.tipo_grafo,
			values=("Dirigido", "No dirigido"),
			state="readonly",
			width=12
		)
		tipo_combo.grid(row=1, column=1, sticky="ew", pady=2)
		tipo_combo.bind("<<ComboboxSelected>>", self._on_cambiar_tipo)
		
		ttk.Label(left_panel, text="Vértice:").grid(row=2, column=0, sticky="w", pady=2)
		self.entry_vertice = ttk.Entry(left_panel, width=12)
		self.entry_vertice.grid(row=2, column=1, pady=2)
		
		btn_add_vertice = ttk.Button(left_panel, text="Agregar vértice", command=self._on_agregar_vertice, style="Retro.TButton")
		btn_add_vertice.grid(row=3, column=0, columnspan=2, pady=2, sticky="ew")
		
		ttk.Label(left_panel, text="Arista (u→v):").grid(row=4, column=0, sticky="w", pady=2)
		frame_arista = ttk.Frame(left_panel)
		frame_arista.grid(row=4, column=1, pady=2)
		self.entry_u = ttk.Entry(frame_arista, width=5)
		self.entry_u.pack(side=tk.LEFT)
		self.arrow_label = ttk.Label(frame_arista, text="→")
		self.arrow_label.pack(side=tk.LEFT, padx=2)
		self.entry_v = ttk.Entry(frame_arista, width=5)
		self.entry_v.pack(side=tk.LEFT)
		
		btn_add_arista = ttk.Button(left_panel, text="Agregar arista", command=self._on_agregar_arista, style="Retro.TButton")
		btn_add_arista.grid(row=5, column=0, columnspan=2, pady=2, sticky="ew")
		
		btn_limpiar = ttk.Button(left_panel, text="Limpiar grafo", command=self._on_limpiar)
		btn_limpiar.grid(row=6, column=0, columnspan=2, pady=(5, 2), sticky="ew")
		
		# Canvas para visualizar el grafo
		self.canvas = tk.Canvas(left_panel, background="#ffffff", width=300, height=250)
		self.canvas.grid(row=7, column=0, columnspan=2, pady=(10, 0))
		
		# Botón calcular matrices
		btn_calcular = ttk.Button(left_panel, text="Calcular Matrices", command=self._on_calcular_matrices, style="Retro.TButton")
		btn_calcular.grid(row=8, column=0, columnspan=2, pady=(10, 0), sticky="ew")
		
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
		self.es_dirigido = True
	
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
	
	def _on_cambiar_tipo(self, *_args) -> None:
		"""Actualiza la configuración cuando cambia el tipo de grafo"""
		self.es_dirigido = self.tipo_grafo.get() == "Dirigido"
		self.arrow_label.configure(text="→" if self.es_dirigido else "—")
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
		
		# Agrupar aristas por par de vértices (sin dirección) y detectar lazos
		aristas_por_par_no_dir: Dict[Tuple[str, str], List[Tuple[str, str, str]]] = {}
		loops_por_vertice: Dict[str, List[str]] = {}
		
		for arista_id, (u, v) in self.aristas.items():
			if u == v:
				loops_por_vertice.setdefault(u, []).append(arista_id)
				continue
			
			par_no_dir = tuple(sorted([u, v]))
			aristas_por_par_no_dir.setdefault(par_no_dir, []).append((arista_id, u, v))
		
		if self.es_dirigido:
			self._draw_dirs(aristas_por_par_no_dir)
		else:
			self._draw_undir(aristas_por_par_no_dir)
		
		# Dibujar lazos (loops) al final para que queden encima
		for vertice, aristas_loop in loops_por_vertice.items():
			if vertice not in self.posiciones:
				continue
			x, y = self.posiciones[vertice]
			self._draw_loops(x, y, len(aristas_loop), self.es_dirigido)
		
		# Dibujar vértices
		radius = 15
		for vertice, (x, y) in self.posiciones.items():
			self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill="#4da3ff", outline="#255eaa", width=2)
			self.canvas.create_text(x, y, text=str(vertice), fill="#ffffff", font=("MS Sans Serif", 10, "bold"))
	
	def _draw_dirs(self, aristas_por_par_no_dir: Dict[Tuple[str, str], List[Tuple[str, str, str]]]) -> None:
		"""Dibuja las aristas para el caso dirigido"""
		for par_no_dir, aristas_grupo in aristas_por_par_no_dir.items():
			u, v = par_no_dir
			if u not in self.posiciones or v not in self.posiciones:
				continue
			
			x1, y1 = self.posiciones[u]
			x2, y2 = self.posiciones[v]
			
			aristas_u_v = [aid for aid, u_orig, v_orig in aristas_grupo if u_orig == u and v_orig == v]
			aristas_v_u = [aid for aid, u_orig, v_orig in aristas_grupo if u_orig == v and v_orig == u]
			
			total_aristas = len(aristas_u_v) + len(aristas_v_u)
			distancia = max(math.sqrt((x2 - x1)**2 + (y2 - y1)**2), 1)
			curvatura_base = max(50, distancia * 0.3)
			incremento = max(25, distancia * 0.2)
			
			def _curvaturas(total: int, lado: int) -> List[float]:
				if total == 0:
					return []
				if total == 1 and total_aristas == 1:
					return [0]
				if total == 1:
					return [lado * curvatura_base]
				offsets = []
				for idx in range(total):
					offset = (idx - (total - 1) / 2) * incremento
					offsets.append(lado * (curvatura_base + offset))
				return offsets
			
			curvas_u_v = _curvaturas(len(aristas_u_v), 1)
			curvas_v_u = _curvaturas(len(aristas_v_u), -1)
			
			for curvatura in curvas_u_v:
				if curvatura == 0:
					self._draw_arrow(x1, y1, x2, y2)
				else:
					self._draw_curved_arrow(x1, y1, x2, y2, curvatura)
			
			for curvatura in curvas_v_u:
				if curvatura == 0:
					self._draw_arrow(x2, y2, x1, y1)
				else:
					self._draw_curved_arrow(x2, y2, x1, y1, curvatura)
	
	def _draw_undir(self, aristas_por_par_no_dir: Dict[Tuple[str, str], List[Tuple[str, str, str]]]) -> None:
		"""Dibuja las aristas para el caso no dirigido"""
		for par_no_dir, aristas_grupo in aristas_por_par_no_dir.items():
			u, v = par_no_dir
			if u not in self.posiciones or v not in self.posiciones:
				continue
			
			x1, y1 = self.posiciones[u]
			x2, y2 = self.posiciones[v]
			
			total = len(aristas_grupo)
			distancia = max(math.sqrt((x2 - x1)**2 + (y2 - y1)**2), 1)
			curvatura_base = max(35, distancia * 0.25)
			incremento = max(20, distancia * 0.15)
			curvaturas = self._curvaturas_simetricas(total, curvatura_base, incremento)
			
			for (arista_id, _u, _v), curvatura in zip(aristas_grupo, curvaturas):
				if curvatura == 0:
					self._draw_undirected_line(x1, y1, x2, y2)
				else:
					self._draw_curved_undirected_line(x1, y1, x2, y2, curvatura)
	
	def _curvaturas_simetricas(self, total: int, base: float, incremento: float) -> List[float]:
		"""Genera curvaturas simétricas alrededor de cero para aristas no dirigidas"""
		if total <= 0:
			return []
		if total == 1:
			return [0]
		
		curvaturas: List[float] = []
		if total % 2 == 1:
			curvaturas.append(0)
		
		paso = 0
		while len(curvaturas) < total:
			curv = base + paso * incremento
			curvaturas.insert(0, -curv)
			if len(curvaturas) < total:
				curvaturas.append(curv)
			paso += 1
		
		return curvaturas
	
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
	
	def _draw_undirected_line(self, x1: float, y1: float, x2: float, y2: float) -> None:
		"""Dibuja una arista no dirigida recta"""
		radius = 15
		dx = x2 - x1
		dy = y2 - y1
		length = math.sqrt(dx**2 + dy**2)
		if length == 0:
			return
		
		start_x = x1 + (dx / length) * radius
		start_y = y1 + (dy / length) * radius
		end_x = x2 - (dx / length) * radius
		end_y = y2 - (dy / length) * radius
		
		self.canvas.create_line(start_x, start_y, end_x, end_y, fill="#000000", width=2)
	
	def _draw_curved_undirected_line(self, x1: float, y1: float, x2: float, y2: float, curvatura: float) -> None:
		"""Dibuja una arista no dirigida curva"""
		radius = 15
		dx = x2 - x1
		dy = y2 - y1
		length = math.sqrt(dx**2 + dy**2)
		if length == 0:
			return
		
		mid_x = (x1 + x2) / 2
		mid_y = (y1 + y2) / 2
		perp_x = -dy / length
		perp_y = dx / length
		control_x = mid_x + perp_x * curvatura
		control_y = mid_y + perp_y * curvatura
		
		dx_start = control_x - x1
		dy_start = control_y - y1
		len_start = math.sqrt(dx_start**2 + dy_start**2)
		if len_start > 0:
			start_x = x1 + (dx_start / len_start) * radius
			start_y = y1 + (dy_start / len_start) * radius
		else:
			start_x = x1
			start_y = y1
		
		dx_end = x2 - control_x
		dy_end = y2 - control_y
		len_end = math.sqrt(dx_end**2 + dy_end**2)
		if len_end > 0:
			end_x = x2 - (dx_end / len_end) * radius
			end_y = y2 - (dy_end / len_end) * radius
		else:
			end_x = x2
			end_y = y2
		
		num_points = 15
		points = []
		for i in range(num_points + 1):
			t = i / num_points
			px = (1-t)**2 * start_x + 2*(1-t)*t * control_x + t**2 * end_x
			py = (1-t)**2 * start_y + 2*(1-t)*t * control_y + t**2 * end_y
			points.extend([px, py])
		
		self.canvas.create_line(*points, fill="#000000", width=2, smooth=True, splinesteps=100)
	
	def _draw_loops(self, x: float, y: float, total: int, dirigido: bool) -> None:
		"""Dibuja uno o varios lazos en un vértice sin superposición"""
		if total <= 0:
			return
		
		base_radius = 28
		separacion = 16
		altura = 35  # cuánto se desplaza el lazo sobre el vértice
		
		for idx in range(total):
			offset = (idx - (total - 1) / 2) * separacion
			radius = base_radius + abs(offset)
			
			bbox = (
				x - radius - offset,
				y - radius - altura - abs(offset),
				x + radius - offset,
				y + radius - altura - abs(offset)
			)
			
			self.canvas.create_arc(
				bbox,
				start=210,
				extent=300,
				style=tk.ARC,
				width=2,
				outline="#000000"
			)
			
			if dirigido:
				# Pequeña flecha para indicar la dirección del lazo
				angle = math.radians(-30)
				arrow_x1 = x + (radius - 5) * math.cos(angle) - offset
				arrow_y1 = y - altura + (radius - 5) * math.sin(angle) - abs(offset)
				arrow_x2 = arrow_x1 + 12 * math.cos(angle)
				arrow_y2 = arrow_y1 + 12 * math.sin(angle)
				self.canvas.create_line(
					arrow_x1,
					arrow_y1,
					arrow_x2,
					arrow_y2,
					fill="#000000",
					width=2,
					arrow=tk.LAST,
					arrowshape=(10, 12, 3)
				)
	
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
				if self.es_dirigido:
					if v == u:
						fila.append("+1")
					elif v == w:
						fila.append("-1")
					else:
						fila.append("0")
				else:
					if u == w == v:
						fila.append("2")
					elif v == u or v == w:
						fila.append("1")
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
		for _, (u, v) in self.aristas.items():
			if self.es_dirigido:
				if u in adj_matrix and v in adj_matrix[u]:
					adj_matrix[u][v] += 1
			else:
				if u in adj_matrix and v in adj_matrix[u]:
					adj_matrix[u][v] += 1
				if u != v and v in adj_matrix and u in adj_matrix[v]:
					adj_matrix[v][u] += 1
		
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
		
		if self.es_dirigido:
			# Llenar matriz: a1 -> a2 si el vértice final de a1 es el inicial de a2
			for a1 in aristas_list:
				_, v1_final = self.aristas[a1]
				for a2 in aristas_list:
					if a1 != a2:
						u2_inicial, _ = self.aristas[a2]
						if v1_final == u2_inicial:
							adj_matrix[a1][a2] = 1
		else:
			# En grafos no dirigidos, las aristas son adyacentes si comparten al menos un vértice
			for a1 in aristas_list:
				u1, v1 = self.aristas[a1]
				conjunto1 = {u1, v1}
				for a2 in aristas_list:
					if a1 == a2:
						continue
					u2, v2 = self.aristas[a2]
					if conjunto1.intersection({u2, v2}):
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
		"""Encuentra todos los circuitos (ciclos) en el grafo"""
		if self.es_dirigido:
			return self._encontrar_circuitos_dirigidos()
		return self._encontrar_circuitos_no_dirigidos()
	
	def _encontrar_circuitos_dirigidos(self) -> List[List[str]]:
		circuitos = []
		circuitos_set = set()
		adyacencia = {v: [] for v in self.vertices}
		for arista_id, (u, v) in self.aristas.items():
			adyacencia[u].append((v, arista_id))
		
		def dfs(vertice_actual: str, camino_aristas: List[str], vertices_camino: List[str]) -> None:
			for vecino, arista_id in adyacencia.get(vertice_actual, []):
				if vecino in vertices_camino:
					idx_inicio = vertices_camino.index(vecino)
					ciclo_aristas = camino_aristas[idx_inicio:] + [arista_id]
					ciclo_tupla = tuple(sorted(ciclo_aristas))
					if ciclo_tupla not in circuitos_set:
						circuitos_set.add(ciclo_tupla)
						circuitos.append(ciclo_aristas)
				else:
					dfs(vecino, camino_aristas + [arista_id], vertices_camino + [vecino])
		
		for vertice_inicial in self.vertices:
			dfs(vertice_inicial, [], [vertice_inicial])
		
		return circuitos
	
	def _encontrar_circuitos_no_dirigidos(self) -> List[List[str]]:
		circuitos = []
		circuitos_set = set()
		adyacencia = {v: [] for v in self.vertices}
		for arista_id, (u, v) in self.aristas.items():
			adyacencia[u].append((v, arista_id))
			if u != v:
				adyacencia[v].append((u, arista_id))
		
		def dfs(vertice_actual: str, camino_aristas: List[str], vertices_camino: List[str]) -> None:
			for vecino, arista_id in adyacencia.get(vertice_actual, []):
				if arista_id in camino_aristas:
					continue
				if vecino in vertices_camino:
					idx_inicio = vertices_camino.index(vecino)
					ciclo_aristas = camino_aristas[idx_inicio:] + [arista_id]
					ciclo_tupla = tuple(sorted(ciclo_aristas))
					if ciclo_tupla not in circuitos_set:
						circuitos_set.add(ciclo_tupla)
						circuitos.append(ciclo_aristas)
				else:
					dfs(vecino, camino_aristas + [arista_id], vertices_camino + [vecino])
		
		for vertice_inicial in self.vertices:
			dfs(vertice_inicial, [], [vertice_inicial])
		
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
			if self.es_dirigido:
				camino = self._encontrar_camino_en_arbol(arbol, v, u)
			else:
				camino = self._encontrar_camino_en_arbol(arbol, u, v)
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
		
		arbol: List[str] = []
		visitados: Set[str] = set()
		aristas_usadas: Set[str] = set()
		
		adyacencia = {v: [] for v in self.vertices}
		for arista_id, (u, v) in self.aristas.items():
			adyacencia[u].append((v, arista_id))
			if not self.es_dirigido and u != v:
				adyacencia[v].append((u, arista_id))
		
		def dfs_arbol(vertice: str) -> None:
			visitados.add(vertice)
			for vecino, arista_id in adyacencia.get(vertice, []):
				if vecino not in visitados:
					if arista_id not in aristas_usadas:
						aristas_usadas.add(arista_id)
						arbol.append(arista_id)
					dfs_arbol(vecino)
		
		for vertice in self.vertices:
			if vertice not in visitados:
				dfs_arbol(vertice)
		
		return arbol
	
	def _encontrar_camino_en_arbol(self, arbol: List[str], inicio: str, fin: str) -> List[str]:
		"""Encuentra un camino en el árbol (respetando el tipo de grafo) de inicio a fin"""
		if self.es_dirigido:
			grafo_arbol: Dict[str, List[Tuple[str, str]]] = {}
			for arista_id in arbol:
				u, v = self.aristas[arista_id]
				grafo_arbol.setdefault(u, []).append((v, arista_id))
			
			def dfs_dir(vertice_actual: str, camino_actual: List[str], visitados: Set[str]) -> Optional[List[str]]:
				if vertice_actual == fin:
					return camino_actual
				for vecino, arista_id in grafo_arbol.get(vertice_actual, []):
					if vecino not in visitados:
						visitados.add(vecino)
						resultado = dfs_dir(vecino, camino_actual + [arista_id], visitados)
						if resultado:
							return resultado
						visitados.remove(vecino)
				return None
			
			resultado = dfs_dir(inicio, [], {inicio})
			return resultado if resultado else []
		
		# Caso no dirigido: se permite recorrer aristas en ambos sentidos pero sin repetirlas
		grafo_arbol: Dict[str, List[Tuple[str, str]]] = {}
		for arista_id in arbol:
			u, v = self.aristas[arista_id]
			grafo_arbol.setdefault(u, []).append((v, arista_id))
			if u != v:
				grafo_arbol.setdefault(v, []).append((u, arista_id))
		
		def dfs_undir(vertice_actual: str, camino_actual: List[str], usadas: Set[str]) -> Optional[List[str]]:
			if vertice_actual == fin:
				return camino_actual
			for vecino, arista_id in grafo_arbol.get(vertice_actual, []):
				if arista_id in usadas:
					continue
				usadas.add(arista_id)
				resultado = dfs_undir(vecino, camino_actual + [arista_id], usadas)
				if resultado:
					return resultado
				usadas.remove(arista_id)
			return None
		
		resultado = dfs_undir(inicio, [], set())
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
		"""Encuentra el componente conexo sin una arista específica"""
		componente: Set[str] = set()
		visitados: Set[str] = set()
		
		grafo_arbol: Dict[str, List[str]] = {}
		for arista_id in arbol:
			if arista_id == arista_excluida:
				continue
			u, v = self.aristas[arista_id]
			grafo_arbol.setdefault(u, []).append(v)
			if not self.es_dirigido and u != v:
				grafo_arbol.setdefault(v, []).append(u)
		
		def dfs_componente(vertice: str) -> None:
			visitados.add(vertice)
			componente.add(vertice)
			for vecino in grafo_arbol.get(vertice, []):
				if vecino not in visitados:
					dfs_componente(vecino)
		
		dfs_componente(vertice_inicial)
		return componente

