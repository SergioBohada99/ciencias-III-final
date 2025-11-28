import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Dict, Set, List, Tuple, Optional
import math
import random


class ArbolesView(ttk.Frame):
	def __init__(self, parent: tk.Misc, app) -> None:
		super().__init__(parent)
		
		title = ttk.Label(self, text="Árbol Generador Mínimo", style="Title.TLabel")
		title.pack(pady=(20, 5))
		
		# Panel principal
		main_panel = ttk.Frame(self, padding=6)
		main_panel.pack(fill=tk.BOTH, expand=True)
		
		# Panel izquierdo: controles y grafo
		left_panel = ttk.Frame(main_panel, style="Panel.TFrame", padding=10)
		left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 6))
		
		# Sección: Agregar elementos
		lbl_add = ttk.Label(left_panel, text="Grafo Ponderado", font=("MS Sans Serif", 10, "bold"))
		lbl_add.grid(row=0, column=0, columnspan=2, pady=(0, 5), sticky="w")
		
		ttk.Label(left_panel, text="Vértice:").grid(row=1, column=0, sticky="w", pady=2)
		self.entry_vertice = ttk.Entry(left_panel, width=12)
		self.entry_vertice.grid(row=1, column=1, pady=2)
		
		btn_add_vertice = ttk.Button(left_panel, text="Agregar vértice", command=self._on_agregar_vertice, style="Retro.TButton")
		btn_add_vertice.grid(row=2, column=0, columnspan=2, pady=2, sticky="ew")
		
		ttk.Label(left_panel, text="Arista (u,v):").grid(row=3, column=0, sticky="w", pady=2)
		frame_arista = ttk.Frame(left_panel)
		frame_arista.grid(row=3, column=1, pady=2)
		self.entry_u = ttk.Entry(frame_arista, width=5)
		self.entry_u.pack(side=tk.LEFT)
		ttk.Label(frame_arista, text=",").pack(side=tk.LEFT, padx=1)
		self.entry_v = ttk.Entry(frame_arista, width=5)
		self.entry_v.pack(side=tk.LEFT)
		
		ttk.Label(left_panel, text="Peso:").grid(row=4, column=0, sticky="w", pady=2)
		self.entry_peso = ttk.Entry(left_panel, width=12)
		self.entry_peso.grid(row=4, column=1, pady=2)
		
		btn_add_arista = ttk.Button(left_panel, text="Agregar arista", command=self._on_agregar_arista, style="Retro.TButton")
		btn_add_arista.grid(row=5, column=0, columnspan=2, pady=2, sticky="ew")
		
		btn_limpiar = ttk.Button(left_panel, text="Limpiar grafo", command=self._on_limpiar)
		btn_limpiar.grid(row=6, column=0, columnspan=2, pady=(5, 2), sticky="ew")
		
		# Canvas para visualizar el grafo
		self.canvas = tk.Canvas(left_panel, background="#ffffff", width=300, height=250)
		self.canvas.grid(row=7, column=0, columnspan=2, pady=(10, 0))
		
		# Botón calcular MST
		btn_calcular = ttk.Button(left_panel, text="Calcular Árbol Generador Mínimo", command=self._on_calcular_mst, style="Retro.TButton")
		btn_calcular.grid(row=8, column=0, columnspan=2, pady=(10, 0), sticky="ew")
		
		# Panel derecho: resultados
		right_panel = ttk.Frame(main_panel, style="Panel.TFrame", padding=10)
		right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		
		# Canvas con scroll para mostrar resultados
		canvas_frame = ttk.Frame(right_panel)
		canvas_frame.pack(fill=tk.BOTH, expand=True)
		
		self.resultados_canvas = tk.Canvas(canvas_frame, bg="#ffffff")
		scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.resultados_canvas.yview)
		self.scrollable_frame = ttk.Frame(self.resultados_canvas)
		
		self.scrollable_frame.bind(
			"<Configure>",
			lambda e: self.resultados_canvas.configure(scrollregion=self.resultados_canvas.bbox("all"))
		)
		
		self.resultados_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
		self.resultados_canvas.configure(yscrollcommand=scrollbar.set)
		
		self.resultados_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
		
		# Bind mousewheel
		def _on_mousewheel(event):
			self.resultados_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
		self.resultados_canvas.bind_all("<MouseWheel>", _on_mousewheel)
		
		# Botón volver
		back = ttk.Button(self, text="← Volver", command=lambda: app.navigate("grafos"))
		back.pack(pady=6)
		
		self.app = app
		
		# Estructuras de datos
		self.vertices: Set[str] = set()
		self.aristas: Dict[str, Dict[str, any]] = {}  # {arista_id: {'u': str, 'v': str, 'peso': float}}
		self.posiciones: Dict[str, Tuple[float, float]] = {}
		self.arista_counter = 0
		
		# Árbol generador mínimo
		self.mst_aristas: Set[str] = set()  # IDs de aristas en el MST
		self.cuerdas: Set[str] = set()  # IDs de aristas que no están en el MST
		
		# Para grid de resultados
		self.resultados_grid_row = 0
		self.resultados_grid_col = 0
	
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
		"""Agrega una arista ponderada al grafo"""
		u = self.entry_u.get().strip()
		v = self.entry_v.get().strip()
		peso_str = self.entry_peso.get().strip()
		
		if not u or not v or not peso_str:
			messagebox.showerror("Error", "Ingresa ambos vértices y el peso")
			return
		
		try:
			peso = float(peso_str)
		except ValueError:
			messagebox.showerror("Error", "El peso debe ser un número")
			return
		
		if u not in self.vertices or v not in self.vertices:
			messagebox.showerror("Error", "Ambos vértices deben existir")
			return
		
		if u == v:
			messagebox.showerror("Error", "No se permiten bucles (vértice a sí mismo)")
			return
		
		# Verificar si ya existe una arista entre estos vértices
		arista_existente = None
		for aid, datos in self.aristas.items():
			if (datos['u'] == u and datos['v'] == v) or (datos['u'] == v and datos['v'] == u):
				arista_existente = aid
				break
		
		if arista_existente:
			messagebox.showwarning("Advertencia", f"Ya existe una arista entre {u} y {v}")
			return
		
		arista_id = f"e{self.arista_counter}"
		self.arista_counter += 1
		self.aristas[arista_id] = {'u': u, 'v': v, 'peso': peso}
		
		self.entry_u.delete(0, tk.END)
		self.entry_v.delete(0, tk.END)
		self.entry_peso.delete(0, tk.END)
		self._draw()
	
	def _on_limpiar(self) -> None:
		"""Limpia el grafo"""
		self.vertices = set()
		self.aristas = {}
		self.posiciones = {}
		self.arista_counter = 0
		self.mst_aristas = set()
		self.cuerdas = set()
		# Limpiar resultados
		for widget in self.scrollable_frame.winfo_children():
			widget.destroy()
		self.resultados_grid_row = 0
		self.resultados_grid_col = 0
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
		"""Dibuja el grafo ponderado con diferenciación visual de ramas y cuerdas"""
		self.canvas.delete("all")
		
		if not self.vertices:
			self.canvas.create_text(150, 125, text="Grafo vacío", fill="#999999", font=("MS Sans Serif", 10))
			return
		
		self._calcular_posiciones()
		
		# Primero dibujar las cuerdas (aristas fuera del MST) en rojo/naranja y punteadas
		for arista_id in self.cuerdas:
			if arista_id not in self.aristas:
				continue
			datos = self.aristas[arista_id]
			u, v = datos['u'], datos['v']
			peso = datos['peso']
			
			if u not in self.posiciones or v not in self.posiciones:
				continue
			
			x1, y1 = self.posiciones[u]
			x2, y2 = self.posiciones[v]
			
			# Cuerdas en rojo/naranja y punteadas para mayor visibilidad
			self.canvas.create_line(x1, y1, x2, y2, fill="#ff6600", width=2, dash=(8, 4))
			
			# Peso de la cuerda
			mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
			self.canvas.create_rectangle(mid_x - 20, mid_y - 10, mid_x + 20, mid_y + 10, fill="#ffffff", outline="#ff6600", width=1)
			self.canvas.create_text(mid_x, mid_y, text=f"{peso:.1f}", fill="#cc4400", font=("MS Sans Serif", 9))
		
		# Luego dibujar las ramas del MST (árbol generador) en verde y más gruesas
		for arista_id in self.mst_aristas:
			if arista_id not in self.aristas:
				continue
			datos = self.aristas[arista_id]
			u, v = datos['u'], datos['v']
			peso = datos['peso']
			
			if u not in self.posiciones or v not in self.posiciones:
				continue
			
			x1, y1 = self.posiciones[u]
			x2, y2 = self.posiciones[v]
			
			# Ramas del MST en verde y gruesas
			self.canvas.create_line(x1, y1, x2, y2, fill="#00aa00", width=4)
			
			# Peso de la rama
			mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
			self.canvas.create_rectangle(mid_x - 20, mid_y - 10, mid_x + 20, mid_y + 10, fill="#ffffff", outline="#00aa00", width=2)
			self.canvas.create_text(mid_x, mid_y, text=f"{peso:.1f}", fill="#006600", font=("MS Sans Serif", 9, "bold"))
		
		# Si no se ha calculado el MST, dibujar todas las aristas normalmente
		if not self.mst_aristas and not self.cuerdas:
			for arista_id, datos in self.aristas.items():
				u, v = datos['u'], datos['v']
				peso = datos['peso']
				
				if u not in self.posiciones or v not in self.posiciones:
					continue
				
				x1, y1 = self.posiciones[u]
				x2, y2 = self.posiciones[v]
				
				# Dibujar línea normal
				self.canvas.create_line(x1, y1, x2, y2, fill="#000000", width=2)
				
				# Dibujar peso
				mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
				self.canvas.create_rectangle(mid_x - 20, mid_y - 10, mid_x + 20, mid_y + 10, fill="#ffffff", outline="#000000", width=1)
				self.canvas.create_text(mid_x, mid_y, text=f"{peso:.1f}", fill="#000000", font=("MS Sans Serif", 9))
		
		# Dibujar vértices encima de todo
		radius = 15
		for vertice, (x, y) in self.posiciones.items():
			self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill="#4da3ff", outline="#255eaa", width=2)
			self.canvas.create_text(x, y, text=str(vertice), fill="#ffffff", font=("MS Sans Serif", 10, "bold"))
		
		# Leyenda si hay MST calculado
		if self.mst_aristas:
			leyenda_y = 10
			# Leyenda para ramas
			self.canvas.create_line(10, leyenda_y, 30, leyenda_y, fill="#00aa00", width=4)
			self.canvas.create_text(35, leyenda_y, text="Ramas (MST)", fill="#000000", font=("MS Sans Serif", 8), anchor="w")
			
			# Leyenda para cuerdas
			if self.cuerdas:
				leyenda_y += 20
				self.canvas.create_line(10, leyenda_y, 30, leyenda_y, fill="#ff6600", width=2, dash=(8, 4))
				self.canvas.create_text(35, leyenda_y, text="Cuerdas", fill="#000000", font=("MS Sans Serif", 8), anchor="w")
	
	def _on_calcular_mst(self) -> None:
		"""Calcula el árbol generador mínimo usando algoritmo de Kruskal"""
		if len(self.vertices) < 2:
			messagebox.showwarning("Advertencia", "El grafo debe tener al menos 2 vértices")
			return
		
		if len(self.aristas) == 0:
			messagebox.showwarning("Advertencia", "El grafo debe tener al menos una arista")
			return
		
		# Limpiar resultados anteriores
		for widget in self.scrollable_frame.winfo_children():
			widget.destroy()
		self.resultados_grid_row = 0
		self.resultados_grid_col = 0
		self.scrollable_frame.columnconfigure(0, weight=1)
		self.scrollable_frame.columnconfigure(1, weight=1)
		
		# Calcular MST usando Kruskal
		self.mst_aristas = self._kruskal_mst()
		self.cuerdas = set(self.aristas.keys()) - self.mst_aristas
		
		# Redibujar con colores del MST
		self._draw()
		
		# Mostrar tablas con los resultados analíticos
		self._mostrar_circuitos_fundamentales()
		self._mostrar_circuitos()
		self._mostrar_conjuntos_corte()
		self._mostrar_cortes_fundamentales()
		
		# Actualizar scroll region
		self.resultados_canvas.update_idletasks()
		self.resultados_canvas.configure(scrollregion=self.resultados_canvas.bbox("all"))
	
	def _kruskal_mst(self) -> Set[str]:
		"""Algoritmo de Kruskal para encontrar el árbol generador mínimo"""
		# Estructura Union-Find para detectar ciclos
		parent = {v: v for v in self.vertices}
		rank = {v: 0 for v in self.vertices}
		
		def find(x: str) -> str:
			if parent[x] != x:
				parent[x] = find(parent[x])  # Path compression
			return parent[x]
		
		def union(x: str, y: str) -> bool:
			root_x = find(x)
			root_y = find(y)
			if root_x == root_y:
				return False  # Ya están en el mismo componente
			
			# Union by rank
			if rank[root_x] < rank[root_y]:
				parent[root_x] = root_y
			elif rank[root_x] > rank[root_y]:
				parent[root_y] = root_x
			else:
				parent[root_y] = root_x
				rank[root_x] += 1
			return True
		
		# Ordenar aristas por peso
		aristas_ordenadas = sorted(self.aristas.items(), key=lambda x: x[1]['peso'])
		
		mst = set()
		for arista_id, datos in aristas_ordenadas:
			u, v = datos['u'], datos['v']
			if find(u) != find(v):
				union(u, v)
				mst.add(arista_id)
				if len(mst) == len(self.vertices) - 1:
					break  # Ya tenemos todas las aristas necesarias
		
		return mst
	
	def _crear_tabla_resultado(self, titulo: str, headers: List[str], datos: List[List[str]]) -> None:
		"""Crea una tabla para mostrar resultados"""
		# Frame principal
		resultado_frame = tk.Frame(self.scrollable_frame, bg="#e0e0e0", relief=tk.RAISED, bd=2)
		resultado_frame.grid(row=self.resultados_grid_row, column=self.resultados_grid_col, 
							sticky="nsew", pady=5, padx=5)
		
		# Frame interno
		inner_frame = ttk.Frame(resultado_frame, padding=8)
		inner_frame.pack(fill=tk.BOTH, expand=True)
		
		# Título
		titulo_label = tk.Label(inner_frame, text=titulo, font=("MS Sans Serif", 12, "bold"),
								bg="#e0e0e0", fg="#255eaa")
		titulo_label.pack(pady=(0, 8))
		
		if not datos:
			ttk.Label(inner_frame, text="No hay datos para mostrar", font=("MS Sans Serif", 10)).pack()
			# Avanzar grid
			if self.resultados_grid_col == 0:
				self.resultados_grid_col = 1
			else:
				self.resultados_grid_col = 0
				self.resultados_grid_row += 1
			return
		
		# Frame para tabla
		tabla_frame = tk.Frame(inner_frame, bg="#ffffff")
		tabla_frame.pack(fill=tk.BOTH, expand=True)
		
		# Encabezados
		for col_idx, header in enumerate(headers):
			header_label = tk.Label(tabla_frame, text=str(header), font=("MS Sans Serif", 9, "bold"),
									 bg="#4da3ff", fg="#ffffff", relief=tk.RAISED, padx=6, pady=4)
			header_label.grid(row=0, column=col_idx, sticky="nsew", padx=1, pady=1)
		
		# Filas de datos
		for row_idx, fila in enumerate(datos, start=1):
			for col_idx, valor in enumerate(fila):
				bg_color = "#f0f0f0" if row_idx % 2 == 0 else "#ffffff"
				cell_label = tk.Label(tabla_frame, text=str(valor), font=("Courier", 8),
									  bg=bg_color, fg="#000000", relief=tk.SUNKEN, padx=6, pady=4)
				cell_label.grid(row=row_idx, column=col_idx, sticky="nsew", padx=1, pady=1)
		
		# Configurar columnas
		for col_idx in range(len(headers)):
			tabla_frame.columnconfigure(col_idx, weight=1, minsize=80)
		
		# Avanzar posición en grid
		if self.resultados_grid_col == 0:
			self.resultados_grid_col = 1
		else:
			self.resultados_grid_col = 0
			self.resultados_grid_row += 1
	
	def _mostrar_ramas(self) -> None:
		"""Muestra las ramas (aristas del MST)"""
		if not self.mst_aristas:
			self._crear_tabla_resultado("Ramas (Aristas del MST)", ["Arista", "Vértices", "Peso"], [])
			return
		
		headers = ["Arista", "Vértices", "Peso"]
		datos = []
		
		for arista_id in sorted(self.mst_aristas):
			datos_arista = self.aristas[arista_id]
			u, v = datos_arista['u'], datos_arista['v']
			peso = datos_arista['peso']
			datos.append([arista_id, f"{u}-{v}", f"{peso:.2f}"])
		
		self._crear_tabla_resultado("Ramas (Aristas del MST)", headers, datos)
	
	def _mostrar_cuerdas(self) -> None:
		"""Muestra las cuerdas (aristas que no están en el MST)"""
		if not self.cuerdas:
			self._crear_tabla_resultado("Cuerdas (Aristas fuera del MST)", ["Arista", "Vértices", "Peso"], [])
			return
		
		headers = ["Arista", "Vértices", "Peso"]
		datos = []
		
		for arista_id in sorted(self.cuerdas):
			datos_arista = self.aristas[arista_id]
			u, v = datos_arista['u'], datos_arista['v']
			peso = datos_arista['peso']
			datos.append([arista_id, f"{u}-{v}", f"{peso:.2f}"])
		
		self._crear_tabla_resultado("Cuerdas (Aristas fuera del MST)", headers, datos)
	
	def _mostrar_circuitos_fundamentales(self) -> None:
		"""Muestra los circuitos fundamentales (uno por cada cuerda)"""
		if not self.cuerdas:
			self._crear_tabla_resultado("Circuitos Fundamentales", ["Circuito", "Aristas"], [])
			return
		
		circuitos_fund = []
		
		# Construir grafo del MST para encontrar caminos
		grafo_mst = {v: [] for v in self.vertices}
		for arista_id in self.mst_aristas:
			datos = self.aristas[arista_id]
			u, v = datos['u'], datos['v']
			grafo_mst[u].append(v)
			grafo_mst[v].append(u)
		
		# Para cada cuerda, encontrar el circuito fundamental
		for cuerda_id in sorted(self.cuerdas):
			datos_cuerda = self.aristas[cuerda_id]
			u, v = datos_cuerda['u'], datos_cuerda['v']
			
			# Encontrar camino en el MST entre u y v
			camino = self._encontrar_camino_mst(grafo_mst, u, v)
			
			# El circuito fundamental es el camino + la cuerda
			circuito = camino + [cuerda_id]
			circuitos_fund.append(circuito)
		
		# Mostrar en tabla
		headers = ["Circuito"] + sorted(list(self.aristas.keys()))
		datos = []
		
		for idx, circuito in enumerate(circuitos_fund):
			fila = [f"CF{idx+1}"]
			for arista_id in sorted(self.aristas.keys()):
				count = circuito.count(arista_id)
				fila.append(str(count))
			datos.append(fila)
		
		self._crear_tabla_resultado("Circuitos Fundamentales", headers, datos)
	
	def _mostrar_circuitos(self) -> None:
		"""Muestra todos los circuitos del grafo"""
		circuitos = self._encontrar_todos_circuitos()
		
		if not circuitos:
			self._crear_tabla_resultado("Circuitos", ["Circuito", "Aristas"], [])
			return
		
		headers = ["Circuito"] + sorted(list(self.aristas.keys()))
		datos = []
		
		for idx, circuito in enumerate(circuitos):
			fila = [f"C{idx+1}"]
			for arista_id in sorted(self.aristas.keys()):
				count = circuito.count(arista_id)
				fila.append(str(count))
			datos.append(fila)
		
		self._crear_tabla_resultado("Circuitos", headers, datos)
	
	def _mostrar_conjuntos_corte(self) -> None:
		"""Muestra todos los conjuntos de corte del grafo"""
		cortes = self._encontrar_conjuntos_corte()
		
		if not cortes:
			self._crear_tabla_resultado("Conjuntos de Corte", ["Corte", "Aristas"], [])
			return
		
		headers = ["Corte"] + sorted(list(self.aristas.keys()))
		datos = []
		
		for idx, corte in enumerate(cortes):
			fila = [f"K{idx+1}"]
			for arista_id in sorted(self.aristas.keys()):
				fila.append("1" if arista_id in corte else "0")
			datos.append(fila)
		
		self._crear_tabla_resultado("Conjuntos de Corte", headers, datos)
	
	def _mostrar_cortes_fundamentales(self) -> None:
		"""Muestra los conjuntos de corte fundamentales basados en el MST"""
		if not self.mst_aristas:
			self._crear_tabla_resultado("Conjuntos de Corte Fundamentales", ["Corte", "Aristas"], [])
			return
		
		cortes_fund = self._encontrar_cortes_fundamentales()
		
		if not cortes_fund:
			self._crear_tabla_resultado("Conjuntos de Corte Fundamentales", ["Corte", "Aristas"], [])
			return
		
		headers = ["Corte Fund."] + sorted(list(self.aristas.keys()))
		datos = []
		
		for idx, corte in enumerate(cortes_fund):
			fila = [f"KF{idx+1}"]
			for arista_id in sorted(self.aristas.keys()):
				fila.append("1" if arista_id in corte else "0")
			datos.append(fila)
		
		self._crear_tabla_resultado("Conjuntos de Corte Fundamentales", headers, datos)
	
	def _encontrar_camino_mst(self, grafo_mst: Dict[str, List[str]], inicio: str, fin: str) -> List[str]:
		"""Encuentra un camino en el MST usando BFS"""
		if inicio == fin:
			return []
		
		cola = [(inicio, [])]
		visitados = {inicio}
		
		while cola:
			vertice_actual, camino_aristas = cola.pop(0)
			
			if vertice_actual == fin:
				return camino_aristas
			
			for vecino in grafo_mst[vertice_actual]:
				if vecino not in visitados:
					visitados.add(vecino)
					# Encontrar la arista entre vertice_actual y vecino
					arista_encontrada = None
					for arista_id in self.mst_aristas:
						datos = self.aristas[arista_id]
						if (datos['u'] == vertice_actual and datos['v'] == vecino) or \
						   (datos['u'] == vecino and datos['v'] == vertice_actual):
							arista_encontrada = arista_id
							break
					
					if arista_encontrada:
						cola.append((vecino, camino_aristas + [arista_encontrada]))
		
		return []
	
	def _encontrar_todos_circuitos(self) -> List[List[str]]:
		"""Encuentra todos los circuitos en el grafo no dirigido"""
		circuitos = []
		circuitos_set = set()
		
		# Construir lista de adyacencia
		adyacencia = {v: [] for v in self.vertices}
		for arista_id, datos in self.aristas.items():
			u, v = datos['u'], datos['v']
			adyacencia[u].append((v, arista_id))
			adyacencia[v].append((u, arista_id))
		
		visitados_global = set()
		
		def dfs_circuito(vertice_actual: str, camino_aristas: List[str], vertices_camino: List[str], aristas_visitadas: Set[str]) -> None:
			for vecino, arista_id in adyacencia.get(vertice_actual, []):
				# Evitar usar la misma arista dos veces en el mismo camino
				if arista_id in aristas_visitadas:
					continue
				
				if vecino in vertices_camino:
					# Encontramos un ciclo
					idx_inicio = vertices_camino.index(vecino)
					ciclo_aristas = camino_aristas[idx_inicio:] + [arista_id]
					# Normalizar: ordenar y convertir a tupla para evitar duplicados
					ciclo_tupla = tuple(sorted(ciclo_aristas))
					if ciclo_tupla not in circuitos_set and len(ciclo_aristas) >= 3:  # Al menos 3 aristas para un ciclo
						circuitos_set.add(ciclo_tupla)
						circuitos.append(ciclo_aristas)
				else:
					# Continuar DFS
					nuevo_set = aristas_visitadas | {arista_id}
					dfs_circuito(vecino, camino_aristas + [arista_id], vertices_camino + [vecino], nuevo_set)
		
		# Intentar desde cada vértice no visitado
		for vertice_inicial in self.vertices:
			if vertice_inicial not in visitados_global:
				dfs_circuito(vertice_inicial, [], [vertice_inicial], set())
				visitados_global.add(vertice_inicial)
		
		return circuitos
	
	def _encontrar_conjuntos_corte(self) -> List[Set[str]]:
		"""Encuentra todos los conjuntos de corte (edge cuts) del grafo"""
		if len(self.vertices) < 2 or not self.aristas:
			return []
		
		vertices_list = sorted(list(self.vertices))
		n = len(vertices_list)
		cortes: List[Set[str]] = []
		visitados: Set[frozenset[str]] = set()
		
		for mask in range(1, 1 << n):
			if not (mask & 1):
				continue  # asegurar particiones únicas (incluye al primer vértice)
			if mask == (1 << n) - 1:
				continue  # evitar conjunto completo
			
			S = {vertices_list[i] for i in range(n) if (mask >> i) & 1}
			corte = set()
			for arista_id, datos in self.aristas.items():
				u, v = datos['u'], datos['v']
				if (u in S and v not in S) or (v in S and u not in S):
					corte.add(arista_id)
			
			if corte:
				corte_frozen = frozenset(corte)
				if corte_frozen not in visitados:
					visitados.add(corte_frozen)
					cortes.append(corte)
		
		return cortes
	
	def _encontrar_cortes_fundamentales(self) -> List[Set[str]]:
		"""Encuentra los conjuntos de corte fundamentales basados en el MST"""
		if not self.mst_aristas:
			return []
		
		cortes_fundamentales: List[Set[str]] = []
		for arista_id in sorted(self.mst_aristas):
			datos = self.aristas[arista_id]
			u, v = datos['u'], datos['v']
			componente_u = self._componente_mst_sin_arista(arista_id, u)
			
			corte = {arista_id}
			for otra_id, datos_arista in self.aristas.items():
				if otra_id == arista_id:
					continue
				a, b = datos_arista['u'], datos_arista['v']
				if (a in componente_u and b not in componente_u) or (b in componente_u and a not in componente_u):
					corte.add(otra_id)
			
			cortes_fundamentales.append(corte)
		
		return cortes_fundamentales
	
	def _componente_mst_sin_arista(self, arista_excluida: str, vertice_inicial: str) -> Set[str]:
		"""Encuentra el componente del MST sin una arista específica"""
		grafo = {v: [] for v in self.vertices}
		for arista_id in self.mst_aristas:
			if arista_id == arista_excluida:
				continue
			datos = self.aristas[arista_id]
			u, v = datos['u'], datos['v']
			grafo[u].append(v)
			grafo[v].append(u)
		
		componente = set()
		cola = [vertice_inicial]
		while cola:
			actual = cola.pop(0)
			if actual in componente:
				continue
			componente.add(actual)
			for vecino in grafo.get(actual, []):
				if vecino not in componente:
					cola.append(vecino)
		
		return componente

