import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Set, Tuple, Optional, List
import math
import random


class GrafoBinarioView(ttk.Frame):
	def __init__(self, parent: tk.Misc, app) -> None:
		super().__init__(parent)
		self.app = app
		
		# Lista de grafos: cada grafo es un diccionario con vertices, aristas, posiciones
		self.grafos: List[Dict] = []
		self.grafo_seleccionado: int = -1  # Índice del grafo actualmente seleccionado para editar
		self.grafos_para_operar: List[int] = []  # Índices de grafos seleccionados para operación
		
		# Grafo resultado
		self.vertices_resultado: Set[str] = set()
		self.aristas_resultado: Dict[str, Dict[str, str]] = {}
		self.posiciones_resultado: Dict[str, Tuple[float, float]] = {}
		self.operacion_actual: Optional[str] = None
		
		self._build_ui()
	
	def _build_ui(self) -> None:
		"""Construye la interfaz de usuario"""
		title = ttk.Label(self, text="Operaciones entre Grafos", style="Title.TLabel")
		title.pack(pady=(5, 3))
		
		# Container principal horizontal
		main_container = ttk.Frame(self)
		main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
		
		# ===== PANEL IZQUIERDO: Controles =====
		left_panel = ttk.Frame(main_container, style="Panel.TFrame", padding=5)
		left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 3))
		
		# Gestión de Grafos
		ttk.Label(left_panel, text="Gestión", font=("MS Sans Serif", 8, "bold")).grid(row=0, column=0, columnspan=2, sticky="w")
		
		btn_nuevo = ttk.Button(left_panel, text="+ Nuevo", command=self._on_nuevo_grafo, style="Retro.TButton", width=10)
		btn_nuevo.grid(row=1, column=0, columnspan=2, pady=1, sticky="ew")
		
		btn_eliminar = ttk.Button(left_panel, text="- Eliminar", command=self._on_eliminar_grafo, width=10)
		btn_eliminar.grid(row=2, column=0, columnspan=2, pady=1, sticky="ew")
		
		ttk.Separator(left_panel, orient="horizontal").grid(row=3, column=0, columnspan=2, pady=4, sticky="ew")
		
		# Editar
		ttk.Label(left_panel, text="Editar", font=("MS Sans Serif", 8, "bold")).grid(row=4, column=0, columnspan=2, sticky="w")
		self.lbl_grafo_actual = ttk.Label(left_panel, text="Click en grafo", font=("MS Sans Serif", 7))
		self.lbl_grafo_actual.grid(row=5, column=0, columnspan=2, sticky="w")
		
		ttk.Label(left_panel, text="V:", font=("MS Sans Serif", 8)).grid(row=6, column=0, sticky="w")
		self.entry_vertice = ttk.Entry(left_panel, width=6)
		self.entry_vertice.grid(row=6, column=1, pady=1)
		self.entry_vertice.bind("<Return>", lambda e: self._on_agregar_vertice())
		
		ttk.Label(left_panel, text="A:", font=("MS Sans Serif", 8)).grid(row=7, column=0, sticky="w")
		frame_arista = ttk.Frame(left_panel)
		frame_arista.grid(row=7, column=1, pady=1)
		self.entry_u = ttk.Entry(frame_arista, width=2)
		self.entry_u.pack(side=tk.LEFT)
		ttk.Label(frame_arista, text="-").pack(side=tk.LEFT)
		self.entry_v = ttk.Entry(frame_arista, width=2)
		self.entry_v.pack(side=tk.LEFT)
		self.entry_v.bind("<Return>", lambda e: self._on_agregar_arista())
		
		btn_limpiar = ttk.Button(left_panel, text="Limpiar", command=self._on_limpiar_grafo, width=10)
		btn_limpiar.grid(row=8, column=0, columnspan=2, pady=2, sticky="ew")
		
		ttk.Separator(left_panel, orient="horizontal").grid(row=9, column=0, columnspan=2, pady=4, sticky="ew")
		
		# Operaciones
		ttk.Label(left_panel, text="Operaciones", font=("MS Sans Serif", 8, "bold")).grid(row=10, column=0, columnspan=2, sticky="w")
		self.lbl_seleccion = ttk.Label(left_panel, text="☑ para operar", font=("MS Sans Serif", 7))
		self.lbl_seleccion.grid(row=11, column=0, columnspan=2, sticky="w")
		
		btn_union = ttk.Button(left_panel, text="∪ Unión", command=self._on_union, style="Retro.TButton", width=10)
		btn_union.grid(row=12, column=0, columnspan=2, pady=1, sticky="ew")
		
		btn_inter = ttk.Button(left_panel, text="∩ Intersec.", command=self._on_interseccion, style="Retro.TButton", width=10)
		btn_inter.grid(row=13, column=0, columnspan=2, pady=1, sticky="ew")
		
		btn_xor = ttk.Button(left_panel, text="⊕ Anillo", command=self._on_suma_anillo, style="Retro.TButton", width=10)
		btn_xor.grid(row=14, column=0, columnspan=2, pady=1, sticky="ew")
		
		btn_cart = ttk.Button(left_panel, text="× Cartes.", command=self._on_cartesiano, style="Retro.TButton", width=10)
		btn_cart.grid(row=15, column=0, columnspan=2, pady=1, sticky="ew")
		
		btn_tens = ttk.Button(left_panel, text="⊗ Tensor.", command=self._on_tensorial, style="Retro.TButton", width=10)
		btn_tens.grid(row=16, column=0, columnspan=2, pady=1, sticky="ew")
		
		btn_comp = ttk.Button(left_panel, text="[ ] Compos.", command=self._on_composicion, style="Retro.TButton", width=10)
		btn_comp.grid(row=17, column=0, columnspan=2, pady=1, sticky="ew")
		
		btn_suma = ttk.Button(left_panel, text="+ Suma", command=self._on_suma, style="Retro.TButton", width=10)
		btn_suma.grid(row=18, column=0, columnspan=2, pady=1, sticky="ew")
		
		btn_limpiar_sel = ttk.Button(left_panel, text="Limpiar Sel.", command=self._on_limpiar_seleccion, width=10)
		btn_limpiar_sel.grid(row=19, column=0, columnspan=2, pady=2, sticky="ew")
		
		self.status = ttk.Label(left_panel, text="", wraplength=90, font=("MS Sans Serif", 7))
		self.status.grid(row=20, column=0, columnspan=2, pady=(3, 0))
		
		# ===== PANEL CENTRAL: Grafos de entrada =====
		center_panel = ttk.Frame(main_container, style="Panel.TFrame", padding=4)
		center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 3))
		
		lbl_grafos = ttk.Label(center_panel, text="Grafos (click = editar, ☑ = operar)", font=("MS Sans Serif", 8, "bold"))
		lbl_grafos.pack(anchor="w")
		
		# Canvas con scroll para grafos
		grafos_container = ttk.Frame(center_panel)
		grafos_container.pack(fill=tk.BOTH, expand=True)
		
		self.grafos_canvas = tk.Canvas(grafos_container, bg="#e8e8e8")
		scroll_v = ttk.Scrollbar(grafos_container, orient="vertical", command=self.grafos_canvas.yview)
		scroll_h = ttk.Scrollbar(grafos_container, orient="horizontal", command=self.grafos_canvas.xview)
		
		self.grafos_frame = ttk.Frame(self.grafos_canvas)
		self.grafos_frame.bind("<Configure>", lambda e: self.grafos_canvas.configure(scrollregion=self.grafos_canvas.bbox("all")))
		
		self.grafos_canvas.create_window((0, 0), window=self.grafos_frame, anchor="nw")
		self.grafos_canvas.configure(yscrollcommand=scroll_v.set, xscrollcommand=scroll_h.set)
		
		scroll_v.pack(side=tk.RIGHT, fill=tk.Y)
		scroll_h.pack(side=tk.BOTTOM, fill=tk.X)
		self.grafos_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		
		# ===== PANEL DERECHO: Resultado =====
		right_panel = ttk.Frame(main_container, style="Panel.TFrame", padding=4)
		right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		
		lbl_resultado = ttk.Label(right_panel, text="Resultado", font=("MS Sans Serif", 8, "bold"))
		lbl_resultado.pack(anchor="w")
		
		self.canvas_resultado = tk.Canvas(right_panel, background="#ffffff")
		self.canvas_resultado.pack(fill=tk.BOTH, expand=True)
		
		# Botón volver
		back = ttk.Button(self, text="← Volver", command=lambda: self.app.navigate("grafos"))
		back.pack(pady=3)
		
		# Crear 2 grafos vacíos inicialmente
		self._on_nuevo_grafo()
		self._on_nuevo_grafo()
	
	# ==================== GESTIÓN DE GRAFOS ====================
	
	def _on_nuevo_grafo(self) -> None:
		"""Crea un nuevo grafo vacío"""
		nuevo_grafo = {
			'vertices': set(),
			'aristas': {},
			'posiciones': {},
			'nombre': f"G{len(self.grafos) + 1}"
		}
		self.grafos.append(nuevo_grafo)
		self._actualizar_grid_grafos()
		self.status.configure(text=f"Grafo {nuevo_grafo['nombre']} creado")
	
	def _on_eliminar_grafo(self) -> None:
		"""Elimina el grafo seleccionado"""
		if self.grafo_seleccionado < 0 or self.grafo_seleccionado >= len(self.grafos):
			messagebox.showwarning("Advertencia", "Selecciona un grafo para eliminar (click en el grafo)")
			return
		
		if len(self.grafos) <= 1:
			messagebox.showwarning("Advertencia", "Debe haber al menos un grafo")
			return
		
		nombre = self.grafos[self.grafo_seleccionado]['nombre']
		del self.grafos[self.grafo_seleccionado]
		
		# Limpiar selección
		self.grafos_para_operar = [i for i in self.grafos_para_operar if i != self.grafo_seleccionado]
		self.grafos_para_operar = [i if i < self.grafo_seleccionado else i - 1 for i in self.grafos_para_operar]
		self.grafo_seleccionado = -1
		
		# Renumerar grafos
		for i, grafo in enumerate(self.grafos):
			grafo['nombre'] = f"G{i + 1}"
		
		self._actualizar_grid_grafos()
		self.lbl_grafo_actual.configure(text="Selecciona un grafo")
		self.status.configure(text=f"Grafo {nombre} eliminado")
	
	def _on_limpiar_grafo(self) -> None:
		"""Limpia el grafo seleccionado"""
		if self.grafo_seleccionado < 0 or self.grafo_seleccionado >= len(self.grafos):
			messagebox.showwarning("Advertencia", "Selecciona un grafo para limpiar")
			return
		
		grafo = self.grafos[self.grafo_seleccionado]
		grafo['vertices'] = set()
		grafo['aristas'] = {}
		grafo['posiciones'] = {}
		self._actualizar_grid_grafos()
		self.status.configure(text=f"{grafo['nombre']} limpiado")
	
	def _on_limpiar_seleccion(self) -> None:
		"""Limpia la selección de grafos para operar"""
		self.grafos_para_operar = []
		self._actualizar_grid_grafos()
		self.status.configure(text="Selección limpiada")
	
	# ==================== EDICIÓN DE GRAFOS ====================
	
	def _seleccionar_para_editar(self, idx: int) -> None:
		"""Selecciona un grafo para editar (click normal)"""
		if idx < 0 or idx >= len(self.grafos):
			return
		self.grafo_seleccionado = idx
		self.lbl_grafo_actual.configure(text=f"Editando: {self.grafos[idx]['nombre']}")
		self._actualizar_grid_grafos()
	
	def _toggle_seleccion_operar(self, idx: int) -> None:
		"""Toggle selección de grafo para operar (click izquierdo)"""
		if idx < 0 or idx >= len(self.grafos):
			return
		
		if idx in self.grafos_para_operar:
			self.grafos_para_operar.remove(idx)
		else:
			self.grafos_para_operar.append(idx)
		
		self._actualizar_grid_grafos()
		nombres = [self.grafos[i]['nombre'] for i in self.grafos_para_operar]
		self.status.configure(text=f"Operar: {' → '.join(nombres) if nombres else 'Ninguno'}")
	
	def _on_agregar_vertice(self) -> None:
		"""Agrega un vértice al grafo seleccionado"""
		if self.grafo_seleccionado < 0:
			messagebox.showwarning("Advertencia", "Selecciona un grafo (click en el grafo)")
			return
		
		vertice = self.entry_vertice.get().strip()
		if not vertice:
			return
		
		if not vertice.isalnum():
			messagebox.showerror("Error", "El vértice debe ser alfanumérico")
			return
		
		grafo = self.grafos[self.grafo_seleccionado]
		if vertice in grafo['vertices']:
			messagebox.showwarning("Advertencia", f"El vértice {vertice} ya existe")
			return
		
		grafo['vertices'].add(vertice)
		self.entry_vertice.delete(0, tk.END)
		self._actualizar_grid_grafos()
	
	def _on_agregar_arista(self) -> None:
		"""Agrega una arista al grafo seleccionado"""
		if self.grafo_seleccionado < 0:
			messagebox.showwarning("Advertencia", "Selecciona un grafo (click en el grafo)")
			return
		
		u = self.entry_u.get().strip()
		v = self.entry_v.get().strip()
		
		if not u or not v:
			return
		
		grafo = self.grafos[self.grafo_seleccionado]
		
		if u not in grafo['vertices'] or v not in grafo['vertices']:
			messagebox.showerror("Error", "Ambos vértices deben existir")
			return
		
		# Verificar arista duplicada
		for datos in grafo['aristas'].values():
			if (datos['u'] == u and datos['v'] == v) or (datos['u'] == v and datos['v'] == u):
				messagebox.showwarning("Advertencia", "La arista ya existe")
				return
		
		# Generar letra de arista
		letra = self._generar_letra_arista(grafo)
		grafo['aristas'][letra] = {'u': u, 'v': v}
		
		self.entry_u.delete(0, tk.END)
		self.entry_v.delete(0, tk.END)
		self.entry_u.focus()
		self._actualizar_grid_grafos()
	
	def _generar_letra_arista(self, grafo: Dict) -> str:
		"""Genera la siguiente letra disponible para arista"""
		letras_usadas = set(grafo['aristas'].keys())
		for i in range(26):
			letra = chr(ord('a') + i)
			if letra not in letras_usadas:
				return letra
		# Si se agotan las letras simples
		for i in range(26):
			for j in range(26):
				letra = chr(ord('a') + i) + chr(ord('a') + j)
				if letra not in letras_usadas:
					return letra
		return f"e{len(letras_usadas)}"
	
	# ==================== VISUALIZACIÓN GRID ====================
	
	def _actualizar_grid_grafos(self) -> None:
		"""Actualiza el grid de grafos"""
		# Limpiar grid anterior
		for widget in self.grafos_frame.winfo_children():
			widget.destroy()
		
		if not self.grafos:
			return
		
		# Calcular dimensiones del grid (máximo 3 columnas)
		n = len(self.grafos)
		cols = min(3, n)
		
		# Crear canvas para cada grafo
		for idx, grafo in enumerate(self.grafos):
			row = idx // cols
			col = idx % cols
			
			# Frame contenedor
			frame = tk.Frame(self.grafos_frame, relief=tk.RAISED, bd=2)
			
			# Determinar color del borde según selección
			if idx == self.grafo_seleccionado:
				frame.configure(bg="#4da3ff")  # Azul = editando
			elif idx in self.grafos_para_operar:
				frame.configure(bg="#00aa00")  # Verde = seleccionado para operar
			else:
				frame.configure(bg="#cccccc")
			
			frame.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")
			
			# Barra superior con título y checkbox
			top_bar = tk.Frame(frame, bg=frame.cget("bg"))
			top_bar.pack(fill=tk.X, padx=2, pady=2)
			
			# Checkbox para seleccionar para operar
			is_selected = idx in self.grafos_para_operar
			orden_text = ""
			if is_selected:
				orden = self.grafos_para_operar.index(idx) + 1
				orden_text = f" #{orden}"
			
			# Botón checkbox visual
			checkbox_text = "☑" if is_selected else "☐"
			btn_check = tk.Button(
				top_bar, 
				text=checkbox_text + orden_text,
				font=("MS Sans Serif", 10, "bold"),
				bg="#00aa00" if is_selected else "#ffffff",
				fg="#ffffff" if is_selected else "#666666",
				relief=tk.FLAT,
				width=4,
				cursor="hand2",
				command=lambda i=idx: self._toggle_seleccion_operar(i)
			)
			btn_check.pack(side=tk.LEFT, padx=2)
			
			# Título del grafo
			fg_color = "#ffffff" if idx == self.grafo_seleccionado or idx in self.grafos_para_operar else "#333333"
			lbl_titulo = tk.Label(
				top_bar, 
				text=grafo['nombre'], 
				font=("MS Sans Serif", 9, "bold"), 
				bg=frame.cget("bg"), 
				fg=fg_color
			)
			lbl_titulo.pack(side=tk.LEFT, padx=4)
			
			# Canvas del grafo
			canvas = tk.Canvas(frame, bg="#ffffff", width=240, height=200)
			canvas.pack(padx=3, pady=(0, 3))
			
			# Click en canvas o título = editar
			canvas.bind("<Button-1>", lambda e, i=idx: self._seleccionar_para_editar(i))
			lbl_titulo.bind("<Button-1>", lambda e, i=idx: self._seleccionar_para_editar(i))
			
			# Dibujar grafo
			self._dibujar_grafo_mini(canvas, grafo)
		
		# Configurar columnas para que se expandan
		for col in range(cols):
			self.grafos_frame.columnconfigure(col, weight=1)
	
	def _dibujar_grafo_mini(self, canvas: tk.Canvas, grafo: Dict) -> None:
		"""Dibuja un grafo en un canvas pequeño"""
		vertices = grafo['vertices']
		aristas = grafo['aristas']
		posiciones = grafo['posiciones']
		
		if not vertices:
			canvas.create_text(120, 100, text="Vacío", fill="#999999", font=("MS Sans Serif", 10))
			return
		
		# Calcular posiciones si no existen
		self._calcular_posiciones_mini(canvas, list(vertices), posiciones)
		
		# Dibujar aristas
		for arista_id, datos in aristas.items():
			u, v = datos['u'], datos['v']
			if u not in posiciones or v not in posiciones:
				continue
			
			x1, y1 = posiciones[u]
			x2, y2 = posiciones[v]
			
			if u == v:
				# Bucle
				radius = 14
				loop_radius = 16
				canvas.create_oval(x1 - loop_radius, y1 - radius - loop_radius * 2, x1 + loop_radius, y1 - radius, outline="#333333", width=2)
			else:
				canvas.create_line(x1, y1, x2, y2, fill="#333333", width=2)
		
		# Dibujar vértices
		radius = 14
		for vertice in vertices:
			if vertice not in posiciones:
				continue
			x, y = posiciones[vertice]
			canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill="#4da3ff", outline="#255eaa", width=2)
			canvas.create_text(x, y, text=str(vertice), fill="#ffffff", font=("MS Sans Serif", 9, "bold"))
	
	def _calcular_posiciones_mini(self, canvas: tk.Canvas, vertices: List[str], posiciones: Dict) -> None:
		"""Calcula posiciones circulares para un grafo mini"""
		canvas.update_idletasks()
		width = canvas.winfo_width()
		height = canvas.winfo_height()
		
		# Usar valores por defecto si el canvas aún no tiene tamaño
		if width < 50:
			width = 240
		if height < 50:
			height = 200
		
		n = len(vertices)
		if n == 0:
			return
		
		# Siempre recalcular posiciones para que quepan en el canvas
		margin = 25  # Margen desde el borde
		center_x = width / 2
		center_y = height / 2
		radius = min(width - margin * 2, height - margin * 2) / 2.2
		
		for i, vertice in enumerate(vertices):
			angle = 2 * math.pi * i / n - math.pi / 2
			posiciones[vertice] = (
				center_x + radius * math.cos(angle),
				center_y + radius * math.sin(angle)
			)
	
	# ==================== OPERACIONES ====================
	
	def _obtener_grafos_seleccionados(self) -> List[Dict]:
		"""Obtiene los grafos seleccionados para operar en orden"""
		if len(self.grafos_para_operar) < 2:
			messagebox.showwarning("Advertencia", "Selecciona al menos 2 grafos para operar (click izquierdo)")
			return []
		return [self.grafos[i] for i in self.grafos_para_operar]
	
	def _on_union(self) -> None:
		"""Unión de N grafos"""
		grafos = self._obtener_grafos_seleccionados()
		if not grafos:
			return
		
		self.vertices_resultado = set()
		self.aristas_resultado = {}
		self.posiciones_resultado = {}
		
		for idx, grafo in enumerate(grafos):
			nombre = grafo['nombre']
			self.vertices_resultado |= grafo['vertices']
			
			for arista_id, datos in grafo['aristas'].items():
				nueva_arista = datos.copy()
				nueva_arista['regla'] = 0
				self.aristas_resultado[f"{nombre}_{arista_id}"] = nueva_arista
		
		nombres = [g['nombre'] for g in grafos]
		self.operacion_actual = f"Unión ({' ∪ '.join(nombres)})"
		self.status.configure(text="Unión calculada")
		self._draw_resultado()
	
	def _on_interseccion(self) -> None:
		"""Intersección de N grafos"""
		grafos = self._obtener_grafos_seleccionados()
		if not grafos:
			return
		
		# Vértices comunes a todos
		self.vertices_resultado = grafos[0]['vertices'].copy()
		for grafo in grafos[1:]:
			self.vertices_resultado &= grafo['vertices']
		
		# Aristas comunes (mismo par de vértices en todos)
		aristas_por_par: Dict[tuple, List] = {}
		for grafo in grafos:
			for arista_id, datos in grafo['aristas'].items():
				par = tuple(sorted([datos['u'], datos['v']]))
				if par not in aristas_por_par:
					aristas_por_par[par] = []
				aristas_por_par[par].append((grafo['nombre'], arista_id, datos))
		
		self.aristas_resultado = {}
		self.posiciones_resultado = {}
		
		for par, lista in aristas_por_par.items():
			if len(lista) == len(grafos):  # Existe en todos
				nombre, arista_id, datos = lista[0]
				nueva_arista = datos.copy()
				nueva_arista['regla'] = 0
				self.aristas_resultado[arista_id] = nueva_arista
		
		nombres = [g['nombre'] for g in grafos]
		self.operacion_actual = f"Intersección ({' ∩ '.join(nombres)})"
		self.status.configure(text="Intersección calculada")
		self._draw_resultado()
	
	def _on_suma_anillo(self) -> None:
		"""Suma anillo (XOR) de N grafos"""
		grafos = self._obtener_grafos_seleccionados()
		if not grafos:
			return
		
		# Vértices que aparecen en número impar de grafos
		conteo_vertices: Dict[str, int] = {}
		for grafo in grafos:
			for v in grafo['vertices']:
				conteo_vertices[v] = conteo_vertices.get(v, 0) + 1
		
		self.vertices_resultado = {v for v, count in conteo_vertices.items() if count % 2 == 1}
		
		# Aristas que aparecen en número impar de grafos
		conteo_aristas: Dict[tuple, List] = {}
		for grafo in grafos:
			for arista_id, datos in grafo['aristas'].items():
				par = tuple(sorted([datos['u'], datos['v']]))
				if par not in conteo_aristas:
					conteo_aristas[par] = []
				conteo_aristas[par].append((grafo['nombre'], arista_id, datos))
		
		self.aristas_resultado = {}
		self.posiciones_resultado = {}
		
		contador = 0
		for par, lista in conteo_aristas.items():
			if len(lista) % 2 == 1:  # Número impar
				nombre, arista_id, datos = lista[0]
				nueva_arista = datos.copy()
				nueva_arista['regla'] = 0
				self.aristas_resultado[f"x{contador}"] = nueva_arista
				contador += 1
		
		nombres = [g['nombre'] for g in grafos]
		self.operacion_actual = f"Suma Anillo ({' ⊕ '.join(nombres)})"
		self.status.configure(text="Suma anillo calculada")
		self._draw_resultado()
	
	def _on_cartesiano(self) -> None:
		"""Producto cartesiano de N grafos (secuencial)"""
		grafos = self._obtener_grafos_seleccionados()
		if not grafos:
			return
		
		# Empezar con el primer grafo
		vertices_actual = {v for v in grafos[0]['vertices']}
		aristas_actual = {k: v.copy() for k, v in grafos[0]['aristas'].items()}
		
		# Aplicar producto cartesiano secuencialmente
		for grafo in grafos[1:]:
			nuevos_vertices = set()
			nuevas_aristas = {}
			contador = 0
			
			# Nuevos vértices: pares (u1, u2)
			for v1 in vertices_actual:
				for v2 in grafo['vertices']:
					nuevos_vertices.add(f"({v1},{v2})")
			
			# Regla 1: u1 = v1, arista en G2
			for v1 in vertices_actual:
				for arista_id, datos in grafo['aristas'].items():
					u2, w2 = datos['u'], datos['v']
					vert1 = f"({v1},{u2})"
					vert2 = f"({v1},{w2})"
					if vert1 in nuevos_vertices and vert2 in nuevos_vertices:
						nuevas_aristas[f"c{contador}"] = {'u': vert1, 'v': vert2, 'regla': 1}
						contador += 1
			
			# Regla 2: u2 = v2, arista en G1 actual
			for v2 in grafo['vertices']:
				for arista_id, datos in aristas_actual.items():
					u1, w1 = datos['u'], datos['v']
					vert1 = f"({u1},{v2})"
					vert2 = f"({w1},{v2})"
					if vert1 in nuevos_vertices and vert2 in nuevos_vertices:
						nuevas_aristas[f"c{contador}"] = {'u': vert1, 'v': vert2, 'regla': 2}
						contador += 1
			
			vertices_actual = nuevos_vertices
			aristas_actual = nuevas_aristas
		
		self.vertices_resultado = vertices_actual
		self.aristas_resultado = aristas_actual
		self.posiciones_resultado = {}
		
		nombres = [g['nombre'] for g in grafos]
		self.operacion_actual = f"Cartesiano ({' × '.join(nombres)})"
		self.status.configure(text="Producto cartesiano calculado")
		self._draw_resultado()
	
	def _on_tensorial(self) -> None:
		"""Producto tensorial de N grafos"""
		grafos = self._obtener_grafos_seleccionados()
		if not grafos:
			return
		
		# Similar al cartesiano pero con regla diferente
		vertices_actual = {v for v in grafos[0]['vertices']}
		aristas_actual = {k: v.copy() for k, v in grafos[0]['aristas'].items()}
		
		for grafo in grafos[1:]:
			nuevos_vertices = set()
			nuevas_aristas = {}
			contador = 0
			aristas_agregadas = set()
			
			for v1 in vertices_actual:
				for v2 in grafo['vertices']:
					nuevos_vertices.add(f"({v1},{v2})")
			
			# Aristas: ambas aristas deben existir
			for arista1_id, datos1 in aristas_actual.items():
				u1, w1 = datos1['u'], datos1['v']
				for arista2_id, datos2 in grafo['aristas'].items():
					u2, w2 = datos2['u'], datos2['v']
					
					# (u1,u2) - (w1,w2)
					vert1 = f"({u1},{u2})"
					vert2 = f"({w1},{w2})"
					par = tuple(sorted([vert1, vert2]))
					if vert1 in nuevos_vertices and vert2 in nuevos_vertices and par not in aristas_agregadas:
						nuevas_aristas[f"t{contador}"] = {'u': vert1, 'v': vert2, 'regla': 0}
						aristas_agregadas.add(par)
						contador += 1
					
					# Cruzada: (u1,w2) - (w1,u2)
					if u1 != w1 and u2 != w2:
						vert1_c = f"({u1},{w2})"
						vert2_c = f"({w1},{u2})"
						par_c = tuple(sorted([vert1_c, vert2_c]))
						if vert1_c in nuevos_vertices and vert2_c in nuevos_vertices and par_c not in aristas_agregadas:
							nuevas_aristas[f"t{contador}"] = {'u': vert1_c, 'v': vert2_c, 'regla': 0}
							aristas_agregadas.add(par_c)
							contador += 1
			
			vertices_actual = nuevos_vertices
			aristas_actual = nuevas_aristas
		
		self.vertices_resultado = vertices_actual
		self.aristas_resultado = aristas_actual
		self.posiciones_resultado = {}
		
		nombres = [g['nombre'] for g in grafos]
		self.operacion_actual = f"Tensorial ({' ⊗ '.join(nombres)})"
		self.status.configure(text="Producto tensorial calculado")
		self._draw_resultado()
	
	def _on_composicion(self) -> None:
		"""Composición de N grafos (siempre en orden G1, G2, G3...)"""
		if len(self.grafos_para_operar) < 2:
			from tkinter import messagebox
			messagebox.showwarning("Advertencia", "Selecciona al menos 2 grafos para operar")
			return
		
		# Ordenar por índice para que siempre sea G1[G2[G3...]]
		indices_ordenados = sorted(self.grafos_para_operar)
		grafos = [self.grafos[i] for i in indices_ordenados]
		
		vertices_actual = {v for v in grafos[0]['vertices']}
		aristas_actual = {k: v.copy() for k, v in grafos[0]['aristas'].items()}
		
		for grafo in grafos[1:]:
			nuevos_vertices = set()
			nuevas_aristas = {}
			contador = 0
			
			for v1 in vertices_actual:
				for v2 in grafo['vertices']:
					nuevos_vertices.add(f"({v1},{v2})")
			
			# Regla 1: arista en G1 actual (todas las combinaciones de G2)
			for arista_id, datos in aristas_actual.items():
				u1, w1 = datos['u'], datos['v']
				for v2_a in grafo['vertices']:
					for v2_b in grafo['vertices']:
						vert1 = f"({u1},{v2_a})"
						vert2 = f"({w1},{v2_b})"
						if vert1 in nuevos_vertices and vert2 in nuevos_vertices:
							nuevas_aristas[f"comp{contador}"] = {'u': vert1, 'v': vert2, 'regla': 1}
							contador += 1
			
			# Regla 2: u1 = v1 y arista en G2
			for v1 in vertices_actual:
				for arista_id, datos in grafo['aristas'].items():
					u2, w2 = datos['u'], datos['v']
					vert1 = f"({v1},{u2})"
					vert2 = f"({v1},{w2})"
					if vert1 in nuevos_vertices and vert2 in nuevos_vertices:
						nuevas_aristas[f"comp{contador}"] = {'u': vert1, 'v': vert2, 'regla': 2}
						contador += 1
			
			vertices_actual = nuevos_vertices
			aristas_actual = nuevas_aristas
		
		self.vertices_resultado = vertices_actual
		self.aristas_resultado = aristas_actual
		self.posiciones_resultado = {}
		
		nombres = [g['nombre'] for g in grafos]
		if len(nombres) == 2:
			self.operacion_actual = f"Composición ({nombres[0]}[{nombres[1]}])"
		else:
			self.operacion_actual = f"Composición ({nombres[0]}[{'['.join(nombres[1:])}]{']' * (len(nombres) - 1)})"
		self.status.configure(text="Composición calculada")
		self._draw_resultado()
	
	def _on_suma(self) -> None:
		"""Suma de grafos: une vértices de diferentes grafos con aristas"""
		grafos = self._obtener_grafos_seleccionados()
		if not grafos:
			return
		
		self.vertices_resultado = set()
		self.aristas_resultado = {}
		self.posiciones_resultado = {}
		contador = 0
		
		# Recopilar todos los vértices y aristas originales
		vertices_por_grafo = []
		for grafo in grafos:
			vertices_por_grafo.append(set(grafo['vertices']))
			self.vertices_resultado |= grafo['vertices']
			
			# Agregar aristas originales
			for arista_id, datos in grafo['aristas'].items():
				self.aristas_resultado[f"orig{contador}"] = {'u': datos['u'], 'v': datos['v'], 'regla': 0}
				contador += 1
		
		# Agregar aristas entre vértices de diferentes grafos
		for i in range(len(vertices_por_grafo)):
			for j in range(i + 1, len(vertices_por_grafo)):
				for v1 in vertices_por_grafo[i]:
					for v2 in vertices_por_grafo[j]:
						self.aristas_resultado[f"suma{contador}"] = {'u': v1, 'v': v2, 'regla': 1}
						contador += 1
		
		nombres = [g['nombre'] for g in grafos]
		self.operacion_actual = f"Suma ({' + '.join(nombres)})"
		self.status.configure(text="Suma calculada")
		self._draw_resultado()
	
	# ==================== VISUALIZACIÓN RESULTADO ====================
	
	def _draw_resultado(self) -> None:
		"""Dibuja el grafo resultado"""
		self.canvas_resultado.delete("all")
		
		if not self.vertices_resultado:
			self.canvas_resultado.update_idletasks()
			w = max(self.canvas_resultado.winfo_width(), 300)
			h = max(self.canvas_resultado.winfo_height(), 300)
			self.canvas_resultado.create_text(w / 2, h / 2, text="Resultado vacío", fill="#999999", font=("MS Sans Serif", 12))
			return
		
		self._calcular_posiciones_resultado()
		
		# Agrupar aristas
		aristas_por_par = {}
		for arista_id, datos in self.aristas_resultado.items():
			u, v = datos['u'], datos['v']
			par = tuple(sorted([u, v]))
			if par not in aristas_por_par:
				aristas_por_par[par] = []
			aristas_por_par[par].append((arista_id, datos))
		
		# Dibujar aristas (primero negras, luego rojas para que se vean encima)
		for color_order in [1, 2]:  # 1=negro primero, 2=rojo después
			for par, aristas_grupo in aristas_por_par.items():
				total = len(aristas_grupo)
				for idx, (arista_id, datos) in enumerate(aristas_grupo):
					regla = datos.get('regla', 0)
					
					# Solo dibujar las del color actual
					if color_order == 1 and regla == 2:
						continue
					if color_order == 2 and regla != 2:
						continue
					
					u, v = datos['u'], datos['v']
					
					if u not in self.posiciones_resultado or v not in self.posiciones_resultado:
						continue
					
					x1, y1 = self.posiciones_resultado[u]
					x2, y2 = self.posiciones_resultado[v]
					
					color = "#cc0000" if regla == 2 else "#333333"
					width = 2.5 if regla == 2 else 2  # Rojas más gruesas
					
					if u == v:
						self._draw_loop(x1, y1, color)
					elif total > 1:
						curvatura = (idx - (total - 1) / 2) * 30
						self._draw_curved_line(x1, y1, x2, y2, curvatura, color)
					else:
						self.canvas_resultado.create_line(x1, y1, x2, y2, fill=color, width=width)
		
		# Dibujar vértices
		radius = 16
		for vertice in self.vertices_resultado:
			if vertice not in self.posiciones_resultado:
				continue
			x, y = self.posiciones_resultado[vertice]
			self.canvas_resultado.create_oval(x - radius, y - radius, x + radius, y + radius, fill="#4da3ff", outline="#255eaa", width=2)
			font_size = 8 if len(str(vertice)) > 6 else 9
			self.canvas_resultado.create_text(x, y, text=str(vertice), fill="#ffffff", font=("MS Sans Serif", font_size, "bold"))
		
	
	def _calcular_posiciones_resultado(self) -> None:
		"""Calcula posiciones en formato grid/cuadrícula"""
		n = len(self.vertices_resultado)
		if n == 0:
			return
		
		self.canvas_resultado.update_idletasks()
		width = max(self.canvas_resultado.winfo_width(), 300)
		height = max(self.canvas_resultado.winfo_height(), 300)
		
		vertices_list = list(self.vertices_resultado)
		self.posiciones_resultado = {}  # Limpiar posiciones anteriores
		
		# Intentar detectar si son vértices compuestos "(x,y)"
		# y organizarlos en grid
		componentes_fila = set()  # Primer componente (filas)
		componentes_col = set()   # Segundo componente (columnas)
		es_compuesto = True
		
		for v in vertices_list:
			if v.startswith("(") and v.endswith(")") and "," in v:
				# Extraer componentes
				inner = v[1:-1]
				parts = inner.rsplit(",", 1)  # Dividir por la última coma
				if len(parts) == 2:
					componentes_fila.add(parts[0])
					componentes_col.add(parts[1])
				else:
					es_compuesto = False
					break
			else:
				es_compuesto = False
				break
		
		margin_x = 50
		margin_y = 30
		
		if es_compuesto and componentes_fila and componentes_col:
			# Organizar en grid
			filas = sorted(componentes_fila)
			cols = sorted(componentes_col)
			
			num_filas = len(filas)
			num_cols = len(cols)
			
			# Calcular espaciado
			espacio_x = (width - 2 * margin_x) / max(num_cols - 1, 1) if num_cols > 1 else 0
			espacio_y = (height - 2 * margin_y) / max(num_filas - 1, 1) if num_filas > 1 else 0
			
			# Centrar si hay pocos elementos
			start_x = margin_x if num_cols > 1 else width / 2
			start_y = margin_y if num_filas > 1 else height / 2
			
			for v in vertices_list:
				inner = v[1:-1]
				parts = inner.rsplit(",", 1)
				fila_idx = filas.index(parts[0])
				col_idx = cols.index(parts[1])
				
				x = start_x + col_idx * espacio_x
				y = start_y + fila_idx * espacio_y
				self.posiciones_resultado[v] = (x, y)
		else:
			# Layout circular para vértices simples
			center_x = width / 2
			center_y = height / 2
			radius = min(width - 2 * margin_x, height - 2 * margin_y) / 2.5
			
			for i, v in enumerate(sorted(vertices_list)):
				angle = 2 * math.pi * i / n - math.pi / 2
				x = center_x + radius * math.cos(angle)
				y = center_y + radius * math.sin(angle)
				self.posiciones_resultado[v] = (x, y)
	
	def _draw_loop(self, x: float, y: float, color: str) -> None:
		"""Dibuja un bucle"""
		loop_r = 14
		self.canvas_resultado.create_oval(x - loop_r, y - 12 - loop_r * 2, x + loop_r, y - 12, outline=color, width=2)
	
	def _draw_curved_line(self, x1: float, y1: float, x2: float, y2: float, curv: float, color: str) -> None:
		"""Dibuja línea curva"""
		mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
		dx, dy = x2 - x1, y2 - y1
		length = math.sqrt(dx**2 + dy**2) + 0.01
		px, py = -dy / length, dx / length
		cx, cy = mid_x + px * curv, mid_y + py * curv
		self.canvas_resultado.create_line(x1, y1, cx, cy, x2, y2, fill=color, width=2, smooth=True)
