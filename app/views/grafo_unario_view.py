import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Set, Tuple
import math
import random


class GrafoUnarioView(ttk.Frame):
	def __init__(self, parent: tk.Misc, app) -> None:
		super().__init__(parent)
		
		title = ttk.Label(self, text="Operaciones con un Grafo (No Dirigido)", style="Title.TLabel")
		title.pack(pady=(20, 5))
		
		# Panel principal con dos columnas
		main_panel = ttk.Frame(self, padding=6)
		main_panel.pack(fill=tk.BOTH, expand=True)
		
		# Panel izquierdo: controles
		left_panel = ttk.Frame(main_panel, style="Panel.TFrame", padding=10)
		left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))
		
		# Sección: Agregar elementos
		lbl_add = ttk.Label(left_panel, text="Agregar Elementos", font=("MS Sans Serif", 10, "bold"))
		lbl_add.grid(row=0, column=0, columnspan=2, pady=(0, 5), sticky="w")
		
		ttk.Label(left_panel, text="Vértice:").grid(row=1, column=0, sticky="w", pady=2)
		self.entry_vertice = ttk.Entry(left_panel, width=15)
		self.entry_vertice.grid(row=1, column=1, pady=2)
		
		btn_add_vertice = ttk.Button(left_panel, text="Agregar vértice", command=self._on_agregar_vertice, style="Retro.TButton")
		btn_add_vertice.grid(row=2, column=0, columnspan=2, pady=2, sticky="ew")
		
		ttk.Label(left_panel, text="Letra arista:").grid(row=3, column=0, sticky="w", pady=2)
		self.entry_arista_letra = ttk.Entry(left_panel, width=15)
		self.entry_arista_letra.grid(row=3, column=1, pady=2)
		
		ttk.Label(left_panel, text="Arista (u,v):").grid(row=4, column=0, sticky="w", pady=2)
		frame_arista = ttk.Frame(left_panel)
		frame_arista.grid(row=4, column=1, pady=2)
		self.entry_u = ttk.Entry(frame_arista, width=6)
		self.entry_u.pack(side=tk.LEFT)
		ttk.Label(frame_arista, text=",").pack(side=tk.LEFT, padx=2)
		self.entry_v = ttk.Entry(frame_arista, width=6)
		self.entry_v.pack(side=tk.LEFT)
		
		btn_add_arista = ttk.Button(left_panel, text="Agregar arista", command=self._on_agregar_arista, style="Retro.TButton")
		btn_add_arista.grid(row=5, column=0, columnspan=2, pady=2, sticky="ew")
		
		ttk.Separator(left_panel, orient="horizontal").grid(row=6, column=0, columnspan=2, pady=10, sticky="ew")
		
		# Sección: Operaciones
		lbl_ops = ttk.Label(left_panel, text="Operaciones", font=("MS Sans Serif", 10, "bold"))
		lbl_ops.grid(row=7, column=0, columnspan=2, pady=(0, 5), sticky="w")
		
		# Fusión de vértices
		ttk.Label(left_panel, text="Fusionar (u,v):").grid(row=8, column=0, sticky="w", pady=2)
		frame_fusion = ttk.Frame(left_panel)
		frame_fusion.grid(row=8, column=1, pady=2)
		self.entry_fusion_u = ttk.Entry(frame_fusion, width=6)
		self.entry_fusion_u.pack(side=tk.LEFT)
		ttk.Label(frame_fusion, text=",").pack(side=tk.LEFT, padx=2)
		self.entry_fusion_v = ttk.Entry(frame_fusion, width=6)
		self.entry_fusion_v.pack(side=tk.LEFT)
		
		btn_fusionar = ttk.Button(left_panel, text="Fusionar vértices", command=self._on_fusionar_vertices, style="Retro.TButton")
		btn_fusionar.grid(row=9, column=0, columnspan=2, pady=2, sticky="ew")
		
		# Contracción de arista
		ttk.Label(left_panel, text="Contraer arista:").grid(row=10, column=0, sticky="w", pady=2)
		self.entry_contraer_arista = ttk.Entry(left_panel, width=15)
		self.entry_contraer_arista.grid(row=10, column=1, pady=2)
		
		btn_contraer = ttk.Button(left_panel, text="Contraer arista", command=self._on_contraer_arista, style="Retro.TButton")
		btn_contraer.grid(row=11, column=0, columnspan=2, pady=2, sticky="ew")
		
		# Eliminar vértice
		ttk.Label(left_panel, text="Eliminar vértice:").grid(row=12, column=0, sticky="w", pady=2)
		self.entry_eliminar_v = ttk.Entry(left_panel, width=15)
		self.entry_eliminar_v.grid(row=12, column=1, pady=2)
		
		btn_eliminar_v = ttk.Button(left_panel, text="Eliminar vértice", command=self._on_eliminar_vertice, style="Retro.TButton")
		btn_eliminar_v.grid(row=13, column=0, columnspan=2, pady=2, sticky="ew")
		
		# Eliminar arista
		ttk.Label(left_panel, text="Eliminar arista:").grid(row=14, column=0, sticky="w", pady=2)
		self.entry_eliminar_arista = ttk.Entry(left_panel, width=15)
		self.entry_eliminar_arista.grid(row=14, column=1, pady=2)
		
		btn_eliminar_arista = ttk.Button(left_panel, text="Eliminar arista", command=self._on_eliminar_arista, style="Retro.TButton")
		btn_eliminar_arista.grid(row=15, column=0, columnspan=2, pady=2, sticky="ew")
		
		# Botón limpiar
		btn_limpiar = ttk.Button(left_panel, text="Limpiar grafo", command=self._on_limpiar)
		btn_limpiar.grid(row=16, column=0, columnspan=2, pady=(10, 2), sticky="ew")
		
		# Estado
		self.status = ttk.Label(left_panel, text="Agrega vértices para comenzar", wraplength=180)
		self.status.grid(row=17, column=0, columnspan=2, pady=(10, 0))
		
		# Panel derecho: visualización
		right_panel = ttk.Frame(main_panel, style="Panel.TFrame", padding=8)
		right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		
		# Canvas para dibujar el grafo
		self.canvas = tk.Canvas(right_panel, background="#ffffff", width=600, height=500)
		self.canvas.pack(fill=tk.BOTH, expand=True)
		
		# Panel de archivos
		file_panel = ttk.Frame(self, style="Panel.TFrame", padding=6)
		file_panel.pack(fill=tk.X, padx=6, pady=3)
		
		btn_save_close = ttk.Button(file_panel, text="Guardar y cerrar", command=self._on_save_and_close)
		btn_save_close.pack(side=tk.LEFT, padx=4)
		
		btn_save = ttk.Button(file_panel, text="Guardar", command=self._on_save)
		btn_save.pack(side=tk.LEFT, padx=4)
		
		btn_load = ttk.Button(file_panel, text="Cargar", command=self._on_load)
		btn_load.pack(side=tk.LEFT, padx=4)
		
		# Botón volver
		back = ttk.Button(self, text="← Volver", command=lambda: app.navigate("grafos"))
		back.pack(pady=6)
		
		self.app = app
		
		# Estructuras de datos
		# Vértices: Set de strings (números como "1", "2", "3", etc. o combinados "1,2")
		self.vertices: Set[str] = set()
		# Aristas: Dict con letra como key, valor es {'u': str, 'v': str}
		self.aristas: Dict[str, Dict[str, str]] = {}
		self.posiciones: Dict[str, Tuple[float, float]] = {}
	
	def _on_agregar_vertice(self) -> None:
		"""Agrega un vértice al grafo"""
		vertice = self.entry_vertice.get().strip()
		
		if not vertice:
			messagebox.showerror("Error", "Ingresa un número para el vértice")
			return
		
		# Validar que sea un número (no permitir nombres combinados aquí, solo números simples)
		try:
			int(vertice)  # Validar que sea convertible a número
		except ValueError:
			messagebox.showerror("Error", "El vértice debe ser un número simple")
			return
		
		if vertice in self.vertices:
			messagebox.showwarning("Advertencia", f"El vértice {vertice} ya existe")
			return
		
		self.vertices.add(vertice)
		self.status.configure(text=f"Vértice {vertice} agregado")
		self.entry_vertice.delete(0, tk.END)
		self._draw()
	
	def _on_agregar_arista(self) -> None:
		"""Agrega una arista al grafo"""
		arista_letra = self.entry_arista_letra.get().strip()
		u = self.entry_u.get().strip()
		v = self.entry_v.get().strip()
		
		if not arista_letra or not u or not v:
			messagebox.showerror("Error", "Ingresa la letra de la arista y ambos vértices")
			return
		
		# Validar que la letra sea una letra única
		if not arista_letra.isalpha():
			messagebox.showerror("Error", "La arista debe ser una o más letras")
			return
		
		# Validar que la letra no exista ya
		if arista_letra in self.aristas:
			messagebox.showwarning("Advertencia", f"La arista '{arista_letra}' ya existe")
			return
		
		# Los vértices pueden ser números simples o combinados (ej: "1,2")
		# No validamos el formato, solo que existan
		if u not in self.vertices or v not in self.vertices:
			messagebox.showerror("Error", "Ambos vértices deben existir en el grafo")
			return
		
		# Agregar arista (siempre no dirigida)
		self.aristas[arista_letra] = {'u': u, 'v': v}
		
		self.status.configure(text=f"Arista '{arista_letra}' agregada: {u} - {v}")
		self.entry_arista_letra.delete(0, tk.END)
		self.entry_u.delete(0, tk.END)
		self.entry_v.delete(0, tk.END)
		self._draw()
	
	def _on_fusionar_vertices(self) -> None:
		"""Fusiona dos vértices en uno nuevo con nombre combinado"""
		u = self.entry_fusion_u.get().strip()
		v = self.entry_fusion_v.get().strip()
		
		if not u or not v:
			messagebox.showerror("Error", "Ingresa ambos vértices a fusionar")
			return
		
		# Los vértices pueden ser números simples o combinados
		if u not in self.vertices or v not in self.vertices:
			messagebox.showerror("Error", "Ambos vértices deben existir")
			return
		
		if u == v:
			messagebox.showerror("Error", "No se puede fusionar un vértice consigo mismo")
			return
		
		# Crear nuevo vértice con nombre combinado "u,v"
		nuevo = f"{u},{v}"
		
		# Verificar que el nuevo nombre no exista ya
		if nuevo in self.vertices:
			messagebox.showerror("Error", f"El vértice '{nuevo}' ya existe")
			return
		
		# Agregar el nuevo vértice
		self.vertices.add(nuevo)
		
		# Redirigir todas las aristas de u y v hacia el nuevo vértice
		# Las aristas que estaban entre u y v se convierten en bucles
		for arista_id, datos in self.aristas.items():
			if datos['u'] == u or datos['u'] == v:
				datos['u'] = nuevo
			if datos['v'] == u or datos['v'] == v:
				datos['v'] = nuevo
		
		# Eliminar los vértices originales
		self.vertices.remove(u)
		self.vertices.remove(v)
		if u in self.posiciones:
			del self.posiciones[u]
		if v in self.posiciones:
			del self.posiciones[v]
		
		self.status.configure(text=f"Vértices {u} y {v} fusionados en '{nuevo}'")
		self.entry_fusion_u.delete(0, tk.END)
		self.entry_fusion_v.delete(0, tk.END)
		self._draw()
	
	def _on_contraer_arista(self) -> None:
		"""Contrae una arista: fusiona los vértices en los extremos y elimina la arista"""
		arista_id = self.entry_contraer_arista.get().strip()
		
		if not arista_id:
			messagebox.showerror("Error", "Ingresa el ID de la arista a contraer")
			return
		
		if arista_id not in self.aristas:
			messagebox.showerror("Error", f"La arista '{arista_id}' no existe")
			return
		
		# Obtener vértices de la arista a contraer
		arista = self.aristas[arista_id]
		u = arista['u']
		v = arista['v']
		
		if u == v:
			messagebox.showerror("Error", "No se puede contraer un bucle (arista de un vértice a sí mismo)")
			return
		
		# Crear nuevo vértice con nombre combinado "u,v"
		nuevo = f"{u},{v}"
		
		# Verificar que el nuevo nombre no exista ya
		if nuevo in self.vertices:
			messagebox.showerror("Error", f"El vértice '{nuevo}' ya existe")
			return
		
		# Eliminar la arista contraída
		del self.aristas[arista_id]
		
		# Agregar el nuevo vértice
		self.vertices.add(nuevo)
		
		# Redirigir todas las demás aristas de u y v hacia el nuevo vértice
		for aid, datos in self.aristas.items():
			if datos['u'] == u or datos['u'] == v:
				datos['u'] = nuevo
			if datos['v'] == u or datos['v'] == v:
				datos['v'] = nuevo
		
		# Eliminar los vértices originales
		self.vertices.remove(u)
		self.vertices.remove(v)
		if u in self.posiciones:
			del self.posiciones[u]
		if v in self.posiciones:
			del self.posiciones[v]
		
		self.status.configure(text=f"Arista '{arista_id}' contraída: vértices {u},{v} → '{nuevo}'")
		self.entry_contraer_arista.delete(0, tk.END)
		self._draw()
	
	def _on_eliminar_vertice(self) -> None:
		"""Elimina un vértice y todas sus aristas incidentes"""
		vertice = self.entry_eliminar_v.get().strip()
		
		if not vertice:
			messagebox.showerror("Error", "Ingresa un vértice")
			return
		
		if vertice not in self.vertices:
			messagebox.showerror("Error", f"El vértice '{vertice}' no existe")
			return
		
		# Eliminar todas las aristas que incluyen este vértice
		aristas_a_eliminar = [aid for aid, datos in self.aristas.items() 
							  if datos['u'] == vertice or datos['v'] == vertice]
		
		for aid in aristas_a_eliminar:
			del self.aristas[aid]
		
		# Eliminar el vértice
		self.vertices.remove(vertice)
		if vertice in self.posiciones:
			del self.posiciones[vertice]
		
		self.status.configure(text=f"Vértice {vertice} eliminado (y {len(aristas_a_eliminar)} arista(s))")
		self.entry_eliminar_v.delete(0, tk.END)
		self._draw()
	
	def _on_eliminar_arista(self) -> None:
		"""Elimina una arista del grafo"""
		arista_id = self.entry_eliminar_arista.get().strip()
		
		if not arista_id:
			messagebox.showerror("Error", "Ingresa el ID de la arista")
			return
		
		if arista_id not in self.aristas:
			messagebox.showerror("Error", f"La arista '{arista_id}' no existe")
			return
		
		arista = self.aristas[arista_id]
		del self.aristas[arista_id]
		
		self.status.configure(text=f"Arista '{arista_id}' ({arista['u']}-{arista['v']}) eliminada")
		self.entry_eliminar_arista.delete(0, tk.END)
		self._draw()
	
	def _on_limpiar(self) -> None:
		"""Limpia el grafo"""
		self.vertices = set()
		self.aristas = {}
		self.posiciones = {}
		self.status.configure(text="Grafo limpiado")
		self._draw()
	
	def _calcular_posiciones(self) -> None:
		"""Calcula posiciones usando algoritmo force-directed (Fruchterman-Reingold)"""
		n = len(self.vertices)
		if n == 0:
			return
		
		# Calcular tamaño del canvas
		self.canvas.update_idletasks()
		width = max(self.canvas.winfo_width(), 600)
		height = max(self.canvas.winfo_height(), 500)
		
		center_x = width / 2
		center_y = height / 2
		
		# Inicializar posiciones aleatorias para vértices nuevos
		vertices_list = list(self.vertices)
		for vertice in vertices_list:
			if vertice not in self.posiciones:
				# Posición aleatoria alrededor del centro
				angle = random.uniform(0, 2 * math.pi)
				radius = random.uniform(50, min(width, height) / 4)
				self.posiciones[vertice] = (
					center_x + radius * math.cos(angle),
					center_y + radius * math.sin(angle)
				)
		
		# Parámetros del algoritmo
		area = width * height
		k = math.sqrt(area / max(n, 1))  # Distancia ideal entre nodos
		temperature = min(width, height) / 10
		iterations = 50
		
		# Crear estructura de adyacencia para optimizar
		adyacentes = {v: set() for v in vertices_list}
		for arista_id, datos in self.aristas.items():
			u, v = datos['u'], datos['v']
			if u != v:  # Ignorar bucles para el layout
				adyacentes[u].add(v)
				adyacentes[v].add(u)
		
		# Iteraciones del algoritmo force-directed
		for iteration in range(iterations):
			# Calcular fuerzas de repulsión y atracción
			fuerzas = {v: [0.0, 0.0] for v in vertices_list}
			
			# Fuerza de repulsión entre todos los pares de vértices
			for i, v1 in enumerate(vertices_list):
				for v2 in vertices_list[i + 1:]:
					x1, y1 = self.posiciones[v1]
					x2, y2 = self.posiciones[v2]
					
					dx = x2 - x1
					dy = y2 - y1
					distancia = math.sqrt(dx**2 + dy**2)
					
					if distancia > 0:
						# Fuerza de repulsión (inversamente proporcional a la distancia)
						fuerza_repulsion = k**2 / distancia
						fx = (dx / distancia) * fuerza_repulsion
						fy = (dy / distancia) * fuerza_repulsion
						
						fuerzas[v1][0] -= fx
						fuerzas[v1][1] -= fy
						fuerzas[v2][0] += fx
						fuerzas[v2][1] += fy
			
			# Fuerza de atracción entre vértices conectados
			for v1 in vertices_list:
				for v2 in adyacentes[v1]:
					if v1 < v2:  # Evitar contar dos veces
						x1, y1 = self.posiciones[v1]
						x2, y2 = self.posiciones[v2]
						
						dx = x2 - x1
						dy = y2 - y1
						distancia = math.sqrt(dx**2 + dy**2)
						
						if distancia > 0:
							# Fuerza de atracción (proporcional a la distancia)
							fuerza_atraccion = distancia**2 / k
							fx = (dx / distancia) * fuerza_atraccion
							fy = (dy / distancia) * fuerza_atraccion
							
							fuerzas[v1][0] += fx
							fuerzas[v1][1] += fy
							fuerzas[v2][0] -= fx
							fuerzas[v2][1] -= fy
			
			# Aplicar fuerzas con temperatura decreciente
			temp_actual = temperature * (1 - iteration / iterations)
			for vertice in vertices_list:
				fx, fy = fuerzas[vertice]
				fuerza_magnitud = math.sqrt(fx**2 + fy**2)
				
				if fuerza_magnitud > 0:
					# Limitar el movimiento por la temperatura
					desplazamiento = min(fuerza_magnitud, temp_actual)
					dx = (fx / fuerza_magnitud) * desplazamiento
					dy = (fy / fuerza_magnitud) * desplazamiento
					
					x, y = self.posiciones[vertice]
					nueva_x = x + dx
					nueva_y = y + dy
					
					# Mantener dentro del canvas con márgen
					margin = 50
					nueva_x = max(margin, min(width - margin, nueva_x))
					nueva_y = max(margin, min(height - margin, nueva_y))
					
					self.posiciones[vertice] = (nueva_x, nueva_y)
	
	def _draw(self) -> None:
		"""Dibuja el grafo en el canvas"""
		self.canvas.delete("all")
		
		if not self.vertices:
			# Mostrar mensaje cuando no hay vértices
			self.canvas.update_idletasks()
			width = max(self.canvas.winfo_width(), 600)
			height = max(self.canvas.winfo_height(), 500)
			self.canvas.create_text(
				width // 2, height // 2,
				text="Agrega vértices al grafo",
				fill="#666666", font=("MS Sans Serif", 12)
			)
			return
		
		self._calcular_posiciones()
		
		# Agrupar aristas por pares de vértices para curvarlas
		aristas_por_par = {}
		for arista_id, datos in self.aristas.items():
			u, v = datos['u'], datos['v']
			# Normalizar el par (siempre ordenado)
			par = tuple(sorted([u, v]))
			if par not in aristas_por_par:
				aristas_por_par[par] = []
			aristas_por_par[par].append((arista_id, datos))
		
		# Dibujar aristas
		for par, aristas_grupo in aristas_por_par.items():
			total_aristas = len(aristas_grupo)
			
			for idx, (arista_id, datos) in enumerate(aristas_grupo):
				u, v = datos['u'], datos['v']
				
				if u not in self.posiciones or v not in self.posiciones:
					continue
				
				x1, y1 = self.posiciones[u]
				x2, y2 = self.posiciones[v]
				
				# Caso especial: bucle (arista de un vértice a sí mismo)
				if u == v:
					# Dibujar bucles en diferentes ángulos si hay múltiples
					self._draw_loop(x1, y1, arista_id, idx, total_aristas)
				elif total_aristas > 1:
					# Múltiples aristas entre los mismos vértices: curvarlas
					curvatura = (idx - (total_aristas - 1) / 2) * 30
					self._draw_curved_line(x1, y1, x2, y2, arista_id, curvatura)
				else:
					# Arista simple
					self._draw_straight_line(x1, y1, x2, y2, arista_id)
		
		# Dibujar vértices (encima de las aristas)
		radius = 20
		for vertice, (x, y) in self.posiciones.items():
			# Círculo
			self.canvas.create_oval(
				x - radius, y - radius, x + radius, y + radius,
				fill="#4da3ff", outline="#255eaa", width=2
			)
			# Etiqueta del vértice
			self.canvas.create_text(
				x, y,
				text=str(vertice), fill="#ffffff",
				font=("MS Sans Serif", 12, "bold")
			)
	
	def _draw_straight_line(self, x1: float, y1: float, x2: float, y2: float, arista_id: str) -> None:
		"""Dibuja una línea recta para una arista simple"""
		# Dibujar línea
		self.canvas.create_line(x1, y1, x2, y2, fill="#000000", width=2)
		
		# Dibujar etiqueta con ID en el medio
		mid_x = (x1 + x2) / 2
		mid_y = (y1 + y2) / 2
		
		# Fondo blanco para la etiqueta
		self.canvas.create_rectangle(
			mid_x - 15, mid_y - 12,
			mid_x + 15, mid_y + 12,
			fill="#ffffff", outline=""
		)
		# Texto: solo ID
		self.canvas.create_text(
			mid_x, mid_y,
			text=arista_id, fill="#000000",
			font=("MS Sans Serif", 10, "bold")
		)
	
	def _draw_curved_line(self, x1: float, y1: float, x2: float, y2: float, arista_id: str, curvatura: float) -> None:
		"""Dibuja una línea curva para aristas múltiples"""
		# Calcular punto medio
		mid_x = (x1 + x2) / 2
		mid_y = (y1 + y2) / 2
		
		# Calcular vector perpendicular para la curvatura
		dx = x2 - x1
		dy = y2 - y1
		length = math.sqrt(dx**2 + dy**2)
		if length == 0:
			return
		
		# Vector perpendicular normalizado
		perp_x = -dy / length
		perp_y = dx / length
		
		# Punto de control para la curva
		control_x = mid_x + perp_x * curvatura
		control_y = mid_y + perp_y * curvatura
		
		# Dibujar curva usando create_line con smooth
		self.canvas.create_line(
			x1, y1, control_x, control_y, x2, y2,
			fill="#000000", width=2, smooth=True
		)
		
		# Dibujar etiqueta en el punto de control
		self.canvas.create_rectangle(
			control_x - 15, control_y - 12,
			control_x + 15, control_y + 12,
			fill="#ffffff", outline=""
		)
		self.canvas.create_text(
			control_x, control_y,
			text=arista_id, fill="#000000",
			font=("MS Sans Serif", 10, "bold")
		)
	
	def _draw_loop(self, x: float, y: float, arista_id: str, idx: int, total: int) -> None:
		"""Dibuja un bucle (arista de un vértice a sí mismo)"""
		radius = 20
		loop_radius = 25
		
		# Si hay múltiples bucles, distribuirlos en diferentes ángulos
		if total > 1:
			# Calcular ángulo base para este bucle
			# Distribuir uniformemente alrededor del vértice
			angle_offset = (idx - (total - 1) / 2) * (360 / (total + 2))
			angle_rad = math.radians(angle_offset - 90)  # -90 para que el primero esté arriba
		else:
			# Un solo bucle, ponerlo arriba
			angle_rad = math.radians(-90)
		
		# Calcular posición del centro del bucle
		distance = radius + loop_radius
		loop_x = x + distance * math.cos(angle_rad)
		loop_y = y + distance * math.sin(angle_rad)
		
		# Bucle no dirigido (sin flecha)
		self.canvas.create_oval(
			loop_x - loop_radius, loop_y - loop_radius,
			loop_x + loop_radius, loop_y + loop_radius,
			outline="#000000", width=2, fill=""
		)
		
		# Dibujar etiqueta (más alejada del centro del bucle)
		label_distance = loop_radius + 15
		label_x = loop_x + label_distance * math.cos(angle_rad)
		label_y = loop_y + label_distance * math.sin(angle_rad)
		
		self.canvas.create_rectangle(
			label_x - 15, label_y - 10,
			label_x + 15, label_y + 10,
			fill="#ffffff", outline=""
		)
		self.canvas.create_text(
			label_x, label_y,
			text=arista_id, fill="#000000",
			font=("MS Sans Serif", 10, "bold")
		)
	
	# ==================== GUARDAR / CARGAR ====================
	
	def _serialize(self) -> str:
		"""Serializa el grafo a texto"""
		lines = ["# Grafo Unario"]
		lines.append(f"vertices:{','.join(self.vertices)}")
		
		for letra, datos in self.aristas.items():
			u, v = datos['u'], datos['v']
			lines.append(f"arista:{letra},{u},{v}")
		
		return "\n".join(lines) + "\n"
	
	def _parse(self, content: str) -> bool:
		"""Parsea el contenido de un archivo"""
		self.vertices = set()
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
						self.vertices = set(v.strip() for v in verts.split(",") if v.strip())
				
				elif line.startswith("arista:"):
					parts = line.split(":", 1)[1].split(",")
					if len(parts) >= 3:
						letra = parts[0].strip()
						u = parts[1].strip()
						v = parts[2].strip()
						self.aristas[letra] = {'u': u, 'v': v}
			
			return True
		except Exception:
			return False
	
	def _on_save(self) -> None:
		"""Guarda el grafo"""
		path = filedialog.asksaveasfilename(
			title="Guardar grafo",
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
			title="Guardar grafo",
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
			title="Cargar grafo",
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
		
		self._draw()
		self.status.configure(text=f"Cargado: {len(self.vertices)} vértices, {len(self.aristas)} aristas")
