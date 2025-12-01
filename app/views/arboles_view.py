import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Set, List, Tuple
import math
import random


class ArbolesView(ttk.Frame):
	def __init__(self, parent: tk.Misc, app) -> None:
		super().__init__(parent)
		self.app = app
		
		# Estructuras de datos del grafo
		self.vertices: List[str] = []
		self.aristas: Dict[str, Dict[str, any]] = {}  # {letra: {'u': str, 'v': str, 'peso': float}}
		self.posiciones: Dict[str, Tuple[float, float]] = {}
		
		# Árbol generador mínimo
		self.mst_aristas: Set[str] = set()  # IDs de aristas en el MST (ramas)
		self.cuerdas: Set[str] = set()  # IDs de aristas que no están en el MST
		
		# Ventana de visualización
		self.ventana_graficos: tk.Toplevel = None
		
		self._build_ui()
	
	def _build_ui(self) -> None:
		"""Construye la interfaz de usuario"""
		title = ttk.Label(self, text="Árbol Generador Mínimo", style="Title.TLabel")
		title.pack(pady=(10, 3))
		
		desc = ttk.Label(self, text="Genera un árbol generador mínimo usando el algoritmo de Kruskal")
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
		btn_ejecutar = ttk.Button(left_panel, text="▶ Generar Árbol", command=self._on_calcular_mst, style="Retro.TButton")
		btn_ejecutar.grid(row=9, column=0, columnspan=3, pady=2, sticky="ew")
		
		# Botón para ver gráficos
		self.btn_ver_graficos = ttk.Button(left_panel, text="📊 Ver Ramas y Cuerdas", command=self._abrir_ventana_graficos, state="disabled")
		self.btn_ver_graficos.grid(row=10, column=0, columnspan=3, pady=2, sticky="ew")
		
		btn_limpiar = ttk.Button(left_panel, text="Limpiar", command=self._on_limpiar)
		btn_limpiar.grid(row=11, column=0, columnspan=3, pady=2, sticky="ew")
		
		# Estado
		self.status = ttk.Label(left_panel, text="Agrega vértices y aristas", wraplength=130, font=("MS Sans Serif", 8))
		self.status.grid(row=12, column=0, columnspan=3, pady=(8, 0))
		
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
		
		self.txt_resultados = tk.Text(right_panel, width=30, height=18, font=("Consolas", 8))
		scroll_resultados = ttk.Scrollbar(right_panel, orient="vertical", command=self.txt_resultados.yview)
		self.txt_resultados.configure(yscrollcommand=scroll_resultados.set)
		
		scroll_resultados.pack(side=tk.RIGHT, fill=tk.Y)
		self.txt_resultados.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		self.txt_resultados.configure(state="disabled")
		
		# Botón volver
		back = ttk.Button(self, text="← Volver", command=lambda: self.app.navigate("arboles_menu"))
		back.pack(pady=5)
		
		self._draw_grafo()
		self._limpiar_resultados()
	
	# ==================== ENTRADA DE DATOS ====================
	
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
		letras_usadas = set(self.aristas.keys())
		letra_idx = 0
		while True:
			if letra_idx < 26:
				letra = chr(ord('a') + letra_idx)
			else:
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
		
		if u == v:
			messagebox.showerror("Error", "No se permiten bucles")
			return
		
		# Verificar si ya existe arista entre u y v
		for datos in self.aristas.values():
			if (datos['u'] == u and datos['v'] == v) or (datos['u'] == v and datos['v'] == u):
				messagebox.showwarning("Advertencia", f"Ya existe una arista entre {u} y {v}")
				return
		
		try:
			peso = float(peso_str)
			if peso < 0:
				messagebox.showerror("Error", "El peso debe ser positivo")
				return
		except ValueError:
			messagebox.showerror("Error", "El peso debe ser un número válido")
			return
		
		letra = self._generar_letra_arista()
		self.aristas[letra] = {'u': u, 'v': v, 'peso': peso}
		self.status.configure(text=f"Arista '{letra}': {u}↔{v} (w={peso})")
		
		# Limpiar campos
		self.entry_u.delete(0, tk.END)
		self.entry_v.delete(0, tk.END)
		self.entry_peso.delete(0, tk.END)
		self.entry_u.focus()
		
		self._draw_grafo()
	
	def _on_limpiar(self) -> None:
		"""Limpia todo el grafo y resultados"""
		self.vertices = []
		self.aristas = {}
		self.posiciones = {}
		self.mst_aristas = set()
		self.cuerdas = set()
		
		# Desactivar botón de gráficos
		self.btn_ver_graficos.configure(state="disabled")
		
		# Cerrar ventana de gráficos si está abierta
		if self.ventana_graficos and self.ventana_graficos.winfo_exists():
			self.ventana_graficos.destroy()
		
		self._draw_grafo()
		self._limpiar_resultados()
		self.status.configure(text="Grafo limpiado")
	
	def _es_conexo(self) -> bool:
		"""Verifica si el grafo es conexo"""
		if len(self.vertices) <= 1:
			return True
		
		if not self.aristas:
			return False
		
		adj: Dict[str, Set[str]] = {v: set() for v in self.vertices}
		for datos in self.aristas.values():
			u, v = datos['u'], datos['v']
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
		"""Calcula posiciones usando algoritmo force-directed"""
		n = len(self.vertices)
		if n == 0:
			return
		
		self.canvas.update_idletasks()
		width = max(self.canvas.winfo_width(), 400)
		height = max(self.canvas.winfo_height(), 280)
		
		center_x = width / 2
		center_y = height / 2
		
		for vertice in self.vertices:
			if vertice not in self.posiciones:
				angle = random.uniform(0, 2 * math.pi)
				radius = random.uniform(40, min(width, height) / 3)
				self.posiciones[vertice] = (
					center_x + radius * math.cos(angle),
					center_y + radius * math.sin(angle)
				)
		
		# Force-directed layout
		area = width * height
		k = math.sqrt(area / max(n, 1))
		temperature = min(width, height) / 10
		iterations = 50
		
		adyacentes = {v: set() for v in self.vertices}
		for datos in self.aristas.values():
			u, v = datos['u'], datos['v']
			if u != v:
				adyacentes[u].add(v)
				adyacentes[v].add(u)
		
		for iteration in range(iterations):
			fuerzas = {v: [0.0, 0.0] for v in self.vertices}
			
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
		"""Dibuja el grafo con el árbol generador resaltado"""
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
		
		# Dibujar cuerdas primero (punteadas, naranja)
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
			
			self.canvas.create_line(x1, y1, x2, y2, fill="#ff6600", width=2, dash=(6, 3))
			
			mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
			peso_txt = f"{int(peso)}" if peso == int(peso) else f"{peso:.1f}"
			self.canvas.create_rectangle(mid_x - 12, mid_y - 10, mid_x + 12, mid_y + 10, fill="#fff0e0", outline="#ff6600")
			self.canvas.create_text(mid_x, mid_y, text=peso_txt, fill="#cc4400", font=("MS Sans Serif", 9, "bold"))
		
		# Dibujar ramas del MST (verde, gruesas)
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
			
			self.canvas.create_line(x1, y1, x2, y2, fill="#00aa00", width=4)
			
			mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
			peso_txt = f"{int(peso)}" if peso == int(peso) else f"{peso:.1f}"
			self.canvas.create_rectangle(mid_x - 12, mid_y - 10, mid_x + 12, mid_y + 10, fill="#e0ffe0", outline="#00aa00", width=2)
			self.canvas.create_text(mid_x, mid_y, text=peso_txt, fill="#006600", font=("MS Sans Serif", 9, "bold"))
		
		# Si no hay MST calculado, dibujar todas las aristas normalmente
		if not self.mst_aristas and not self.cuerdas:
			for arista_id, datos in self.aristas.items():
				u, v = datos['u'], datos['v']
				peso = datos['peso']
				
				if u not in self.posiciones or v not in self.posiciones:
					continue
				
				x1, y1 = self.posiciones[u]
				x2, y2 = self.posiciones[v]
				
				self.canvas.create_line(x1, y1, x2, y2, fill="#333333", width=2)
				
				mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
				peso_txt = f"{int(peso)}" if peso == int(peso) else f"{peso:.1f}"
				self.canvas.create_rectangle(mid_x - 12, mid_y - 10, mid_x + 12, mid_y + 10, fill="#ffffcc", outline="#999999")
				self.canvas.create_text(mid_x, mid_y, text=peso_txt, fill="#000000", font=("MS Sans Serif", 9, "bold"))
		
		# Dibujar vértices
		radius = 18
		for vertice in self.vertices:
			if vertice not in self.posiciones:
				continue
			x, y = self.posiciones[vertice]
			
			self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill="#4da3ff", outline="#255eaa", width=2)
			self.canvas.create_text(x, y, text=str(vertice), fill="#ffffff", font=("MS Sans Serif", 10, "bold"))
		
		# Leyenda
		if self.mst_aristas:
			self.canvas.create_line(8, 12, 28, 12, fill="#00aa00", width=4)
			self.canvas.create_text(32, 12, text="Ramas (T)", fill="#000000", font=("MS Sans Serif", 8), anchor="w")
			
			if self.cuerdas:
				self.canvas.create_line(8, 28, 28, 28, fill="#ff6600", width=2, dash=(6, 3))
				self.canvas.create_text(32, 28, text="Cuerdas (T')", fill="#000000", font=("MS Sans Serif", 8), anchor="w")
	
	# ==================== VENTANA DE GRÁFICOS ====================
	
	def _abrir_ventana_graficos(self) -> None:
		"""Abre una nueva ventana para mostrar ramas y cuerdas gráficamente"""
		if not self.mst_aristas:
			messagebox.showwarning("Advertencia", "Primero genera el árbol")
			return
		
		# Si ya existe la ventana, traerla al frente
		if self.ventana_graficos and self.ventana_graficos.winfo_exists():
			self.ventana_graficos.lift()
			self.ventana_graficos.focus_force()
			return
		
		# Crear nueva ventana
		self.ventana_graficos = tk.Toplevel(self)
		self.ventana_graficos.title("Ramas y Cuerdas - Visualización")
		self.ventana_graficos.geometry("900x500")
		self.ventana_graficos.resizable(True, True)
		
		# Frame principal
		main_frame = ttk.Frame(self.ventana_graficos, padding=10)
		main_frame.pack(fill=tk.BOTH, expand=True)
		
		# Título
		titulo = ttk.Label(main_frame, text="Visualización de Ramas y Cuerdas", font=("MS Sans Serif", 14, "bold"))
		titulo.pack(pady=(0, 10))
		
		# Frame para los dos canvas
		canvas_frame = ttk.Frame(main_frame)
		canvas_frame.pack(fill=tk.BOTH, expand=True)
		
		# Panel izquierdo: Ramas (Árbol T)
		left_frame = ttk.LabelFrame(canvas_frame, text="Árbol Generador T (Ramas)", padding=5)
		left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
		
		self.canvas_ramas = tk.Canvas(left_frame, background="#f0fff0", width=400, height=350)
		self.canvas_ramas.pack(fill=tk.BOTH, expand=True)
		
		# Panel derecho: Cuerdas (Complemento T')
		right_frame = ttk.LabelFrame(canvas_frame, text="Complemento T' (Cuerdas)", padding=5)
		right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
		
		self.canvas_cuerdas = tk.Canvas(right_frame, background="#fff5ee", width=400, height=350)
		self.canvas_cuerdas.pack(fill=tk.BOTH, expand=True)
		
		# Info en la parte inferior
		info_frame = ttk.Frame(main_frame)
		info_frame.pack(fill=tk.X, pady=(10, 0))
		
		n = len(self.vertices)
		m = len(self.aristas)
		rango = len(self.mst_aristas)
		nulidad = len(self.cuerdas)
		
		info_text = f"Vértices: {n}  |  Aristas totales: {m}  |  Ramas: {rango}  |  Cuerdas: {nulidad}  |  Rango(ρ): {rango}  |  Nulidad(ν): {nulidad}"
		info_label = ttk.Label(info_frame, text=info_text, font=("MS Sans Serif", 9))
		info_label.pack()
		
		# Botón cerrar
		btn_cerrar = ttk.Button(main_frame, text="Cerrar", command=self.ventana_graficos.destroy)
		btn_cerrar.pack(pady=(10, 0))
		
		# Dibujar después de que la ventana esté lista
		self.ventana_graficos.after(100, self._dibujar_ramas_cuerdas)
	
	def _dibujar_ramas_cuerdas(self) -> None:
		"""Dibuja las ramas y cuerdas en sus respectivos canvas"""
		self._dibujar_ramas()
		self._dibujar_cuerdas()
	
	def _dibujar_ramas(self) -> None:
		"""Dibuja solo las ramas (árbol T) en su canvas"""
		self.canvas_ramas.delete("all")
		
		self.canvas_ramas.update_idletasks()
		width = max(self.canvas_ramas.winfo_width(), 400)
		height = max(self.canvas_ramas.winfo_height(), 350)
		
		if not self.mst_aristas:
			self.canvas_ramas.create_text(width // 2, height // 2, text="Sin ramas", fill="#666666", font=("MS Sans Serif", 12))
			return
		
		# Calcular posiciones para este canvas
		posiciones_ramas = self._calcular_posiciones_para_canvas(width, height)
		
		# Dibujar las ramas
		for arista_id in self.mst_aristas:
			if arista_id not in self.aristas:
				continue
			datos = self.aristas[arista_id]
			u, v = datos['u'], datos['v']
			peso = datos['peso']
			
			if u not in posiciones_ramas or v not in posiciones_ramas:
				continue
			
			x1, y1 = posiciones_ramas[u]
			x2, y2 = posiciones_ramas[v]
			
			# Línea verde gruesa
			self.canvas_ramas.create_line(x1, y1, x2, y2, fill="#00aa00", width=4)
			
			# Etiqueta
			mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
			peso_txt = f"{int(peso)}" if peso == int(peso) else f"{peso:.1f}"
			self.canvas_ramas.create_rectangle(mid_x - 14, mid_y - 12, mid_x + 14, mid_y + 12, fill="#e0ffe0", outline="#00aa00", width=2)
			self.canvas_ramas.create_text(mid_x, mid_y, text=peso_txt, fill="#006600", font=("MS Sans Serif", 10, "bold"))
		
		# Dibujar vértices
		radius = 20
		for vertice in self.vertices:
			if vertice not in posiciones_ramas:
				continue
			x, y = posiciones_ramas[vertice]
			
			self.canvas_ramas.create_oval(x - radius, y - radius, x + radius, y + radius, fill="#00cc00", outline="#006600", width=2)
			self.canvas_ramas.create_text(x, y, text=str(vertice), fill="#ffffff", font=("MS Sans Serif", 11, "bold"))
		
		# Peso total
		peso_total = sum(self.aristas[aid]['peso'] for aid in self.mst_aristas)
		peso_txt = f"{int(peso_total)}" if peso_total == int(peso_total) else f"{peso_total:.2f}"
		self.canvas_ramas.create_text(width // 2, height - 15, text=f"Peso total: {peso_txt}", fill="#006600", font=("MS Sans Serif", 10, "bold"))
	
	def _dibujar_cuerdas(self) -> None:
		"""Dibuja solo las cuerdas (complemento T') en su canvas"""
		self.canvas_cuerdas.delete("all")
		
		self.canvas_cuerdas.update_idletasks()
		width = max(self.canvas_cuerdas.winfo_width(), 400)
		height = max(self.canvas_cuerdas.winfo_height(), 350)
		
		if not self.cuerdas:
			self.canvas_cuerdas.create_text(width // 2, height // 2, text="T' = ∅\n(Sin cuerdas)", fill="#666666", font=("MS Sans Serif", 12), justify="center")
			# Dibujar vértices aislados
			posiciones_cuerdas = self._calcular_posiciones_para_canvas(width, height)
			radius = 20
			for vertice in self.vertices:
				if vertice not in posiciones_cuerdas:
					continue
				x, y = posiciones_cuerdas[vertice]
				self.canvas_cuerdas.create_oval(x - radius, y - radius, x + radius, y + radius, fill="#cccccc", outline="#888888", width=2)
				self.canvas_cuerdas.create_text(x, y, text=str(vertice), fill="#ffffff", font=("MS Sans Serif", 11, "bold"))
			return
		
		# Calcular posiciones para este canvas
		posiciones_cuerdas = self._calcular_posiciones_para_canvas(width, height)
		
		# Dibujar las cuerdas
		for arista_id in self.cuerdas:
			if arista_id not in self.aristas:
				continue
			datos = self.aristas[arista_id]
			u, v = datos['u'], datos['v']
			peso = datos['peso']
			
			if u not in posiciones_cuerdas or v not in posiciones_cuerdas:
				continue
			
			x1, y1 = posiciones_cuerdas[u]
			x2, y2 = posiciones_cuerdas[v]
			
			# Línea naranja
			self.canvas_cuerdas.create_line(x1, y1, x2, y2, fill="#ff6600", width=3)
			
			# Etiqueta
			mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
			peso_txt = f"{int(peso)}" if peso == int(peso) else f"{peso:.1f}"
			self.canvas_cuerdas.create_rectangle(mid_x - 14, mid_y - 12, mid_x + 14, mid_y + 12, fill="#fff0e0", outline="#ff6600", width=2)
			self.canvas_cuerdas.create_text(mid_x, mid_y, text=peso_txt, fill="#cc4400", font=("MS Sans Serif", 10, "bold"))
		
		# Dibujar vértices
		radius = 20
		for vertice in self.vertices:
			if vertice not in posiciones_cuerdas:
				continue
			x, y = posiciones_cuerdas[vertice]
			
			self.canvas_cuerdas.create_oval(x - radius, y - radius, x + radius, y + radius, fill="#ff9966", outline="#cc4400", width=2)
			self.canvas_cuerdas.create_text(x, y, text=str(vertice), fill="#ffffff", font=("MS Sans Serif", 11, "bold"))
	
	def _calcular_posiciones_para_canvas(self, width: int, height: int) -> Dict[str, Tuple[float, float]]:
		"""Calcula posiciones de vértices para un canvas específico"""
		n = len(self.vertices)
		if n == 0:
			return {}
		
		# Usar layout circular para consistencia
		center_x = width / 2
		center_y = height / 2 - 15  # Un poco más arriba para dejar espacio al texto
		radius = min(width, height) / 2.8
		
		posiciones = {}
		for i, vertice in enumerate(self.vertices):
			angle = 2 * math.pi * i / n - math.pi / 2
			posiciones[vertice] = (
				center_x + radius * math.cos(angle),
				center_y + radius * math.sin(angle)
			)
		
		return posiciones
	
	# ==================== ALGORITMO DE KRUSKAL ====================
	
	def _on_calcular_mst(self) -> None:
		"""Calcula el árbol generador mínimo usando Kruskal"""
		if len(self.vertices) < 2:
			messagebox.showerror("Error", "Se necesitan al menos 2 vértices")
			return
		
		if not self.aristas:
			messagebox.showerror("Error", "Se necesita al menos una arista")
			return
		
		if not self._es_conexo():
			messagebox.showerror("Error", "El grafo debe ser conexo para generar un árbol generador")
			return
		
		# Kruskal
		self.mst_aristas = self._kruskal_mst()
		self.cuerdas = set(self.aristas.keys()) - self.mst_aristas
		
		# Activar botón de gráficos
		self.btn_ver_graficos.configure(state="normal")
		
		# Redibujar
		self._draw_grafo()
		
		# Mostrar resultados
		self._mostrar_resultados()
		
		self.status.configure(text="Árbol generado ✓")
		
		# Abrir automáticamente la ventana de visualización
		self._abrir_ventana_graficos()
	
	def _kruskal_mst(self) -> Set[str]:
		"""Algoritmo de Kruskal para MST"""
		parent = {v: v for v in self.vertices}
		rank = {v: 0 for v in self.vertices}
		
		def find(x: str) -> str:
			if parent[x] != x:
				parent[x] = find(parent[x])
			return parent[x]
		
		def union(x: str, y: str) -> bool:
			root_x = find(x)
			root_y = find(y)
			if root_x == root_y:
				return False
			
			if rank[root_x] < rank[root_y]:
				parent[root_x] = root_y
			elif rank[root_x] > rank[root_y]:
				parent[root_y] = root_x
			else:
				parent[root_y] = root_x
				rank[root_x] += 1
			return True
		
		aristas_ordenadas = sorted(self.aristas.items(), key=lambda x: x[1]['peso'])
		
		mst = set()
		for arista_id, datos in aristas_ordenadas:
			u, v = datos['u'], datos['v']
			if find(u) != find(v):
				union(u, v)
				mst.add(arista_id)
				if len(mst) == len(self.vertices) - 1:
					break
		
		return mst
	
	# ==================== RESULTADOS ====================
	
	def _mostrar_resultados(self) -> None:
		"""Muestra los resultados del árbol generador"""
		self.txt_resultados.configure(state="normal")
		self.txt_resultados.delete("1.0", tk.END)
		
		n = len(self.vertices)
		m = len(self.aristas)
		
		# Rango y Nulidad
		rango = n - 1
		nulidad = m - rango
		
		# Peso total del MST
		peso_total = sum(self.aristas[aid]['peso'] for aid in self.mst_aristas)
		
		self.txt_resultados.insert(tk.END, "══ INFORMACIÓN ══\n")
		self.txt_resultados.insert(tk.END, f"  Vértices (n): {n}\n")
		self.txt_resultados.insert(tk.END, f"  Aristas (m): {m}\n")
		peso_txt = f"{int(peso_total)}" if peso_total == int(peso_total) else f"{peso_total:.2f}"
		self.txt_resultados.insert(tk.END, f"  Peso total T: {peso_txt}\n\n")
		
		self.txt_resultados.insert(tk.END, "══ RANGO Y NULIDAD ══\n")
		self.txt_resultados.insert(tk.END, f"  Rango (ρ) = {rango}\n")
		self.txt_resultados.insert(tk.END, f"  Nulidad (ν) = {nulidad}\n\n")
		
		self.txt_resultados.insert(tk.END, "══ RAMAS (T) ══\n")
		if self.mst_aristas:
			for arista_id in sorted(self.mst_aristas):
				datos = self.aristas[arista_id]
				u, v = datos['u'], datos['v']
				peso = datos['peso']
				peso_txt = f"{int(peso)}" if peso == int(peso) else f"{peso:.1f}"
				self.txt_resultados.insert(tk.END, f"  {arista_id}: {u}↔{v} (w={peso_txt})\n")
		
		self.txt_resultados.insert(tk.END, "\n══ CUERDAS (T') ══\n")
		if self.cuerdas:
			for arista_id in sorted(self.cuerdas):
				datos = self.aristas[arista_id]
				u, v = datos['u'], datos['v']
				peso = datos['peso']
				peso_txt = f"{int(peso)}" if peso == int(peso) else f"{peso:.1f}"
				self.txt_resultados.insert(tk.END, f"  {arista_id}: {u}↔{v} (w={peso_txt})\n")
		else:
			self.txt_resultados.insert(tk.END, "  T' = ∅\n")
		
		self.txt_resultados.insert(tk.END, "\n══ RESUMEN ══\n")
		ramas_str = ", ".join(sorted(self.mst_aristas)) if self.mst_aristas else "∅"
		cuerdas_str = ", ".join(sorted(self.cuerdas)) if self.cuerdas else "∅"
		self.txt_resultados.insert(tk.END, f"  T  = {{{ramas_str}}}\n")
		self.txt_resultados.insert(tk.END, f"  T' = {{{cuerdas_str}}}\n")
		
		self.txt_resultados.configure(state="disabled")
	
	def _limpiar_resultados(self) -> None:
		"""Limpia el panel de resultados"""
		self.txt_resultados.configure(state="normal")
		self.txt_resultados.delete("1.0", tk.END)
		self.txt_resultados.insert(tk.END, "Genera el árbol para\nver resultados.")
		self.txt_resultados.configure(state="disabled")
