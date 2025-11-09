import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Optional, List, Tuple


class ResiduoNode:
	def __init__(self) -> None:
		self.children: Dict[str, 'ResiduoNode'] = {}
		self.is_end: bool = False
		self.value: Optional[str] = None


class ResiduosMultiplesView(ttk.Frame):
	def __init__(self, parent: tk.Misc, app) -> None:
		super().__init__(parent)

		title = ttk.Label(self, text="Árbol de residuos múltiples", style="Title.TLabel")
		title.pack(pady=(20, 5))

		# Panel paralelo
		panel = ttk.Frame(self, padding=6)
		panel.pack(fill=tk.BOTH, expand=True)

		ops = ttk.Frame(panel, style="Panel.TFrame", padding=10)
		ops.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))

		lbl_key = ttk.Label(ops, text="Letra (A-Z):")
		lbl_key.grid(row=0, column=0, sticky="w")
		self.entry_key = ttk.Entry(ops, width=8)
		self.entry_key.grid(row=1, column=0, pady=(0, 10))

		lbl_m = ttk.Label(ops, text="m (bits por residuo):")
		lbl_m.grid(row=2, column=0, sticky="w")
		self.entry_m = ttk.Entry(ops, width=8)
		self.entry_m.insert(0, "2")
		self.entry_m.grid(row=3, column=0, pady=(0, 10))
		self.entry_m.bind("<Return>", lambda e: self._on_rebuild())
		self.entry_m.bind("<FocusOut>", lambda e: self._on_rebuild())

		btn_insert = ttk.Button(ops, text="Insertar", style="Retro.TButton", command=self._on_insert)
		btn_insert.grid(row=4, column=0, pady=4, sticky="ew")

		btn_delete = ttk.Button(ops, text="Eliminar", style="Retro.TButton", command=self._on_delete)
		btn_delete.grid(row=5, column=0, pady=4, sticky="ew")

		btn_search = ttk.Button(ops, text="Buscar", style="Retro.TButton", command=self._on_search)
		btn_search.grid(row=6, column=0, pady=4, sticky="ew")

		btn_reset_struct = ttk.Button(ops, text="Reiniciar estructura", command=self._on_reset)
		btn_reset_struct.grid(row=7, column=0, pady=6, sticky="ew")

		# Animation controls
		anim_lbl = ttk.Label(ops, text="Controles de animación")
		anim_lbl.grid(row=8, column=0, sticky="w", pady=(8, 2))
		row_base = 9
		btn_play = ttk.Button(ops, text="▶ Reproducir", command=self._on_play)
		btn_play.grid(row=row_base, column=0, pady=2, sticky="ew")
		btn_pause = ttk.Button(ops, text="⏸ Pausa", command=self._on_pause)
		btn_pause.grid(row=row_base + 1, column=0, pady=2, sticky="ew")
		btn_next = ttk.Button(ops, text="Paso", command=self._on_next)
		btn_next.grid(row=row_base + 2, column=0, pady=2, sticky="ew")
		btn_reset_anim = ttk.Button(ops, text="Reiniciar animación", command=self._on_reset_anim)
		btn_reset_anim.grid(row=row_base + 3, column=0, pady=2, sticky="ew")

		self.status = ttk.Label(ops, text="Estado: listo")
		self.status.grid(row=row_base + 4, column=0, pady=(12, 0), sticky="w")

		viz = ttk.Frame(panel, style="Panel.TFrame", padding=8)
		viz.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

		self.canvas = tk.Canvas(viz, background="#ffffff", height=460)
		self.canvas.pack(fill=tk.BOTH, expand=True)
		self.canvas.bind("<Configure>", lambda e: self._draw())

		# Save/load panel
		file_panel = ttk.Frame(self, style="Panel.TFrame", padding=8)
		file_panel.pack(fill=tk.X, padx=4, pady=6)

		btn_save = ttk.Button(file_panel, text="Guardar (.txt)", command=self._on_save)
		btn_save.grid(row=0, column=0, padx=4, pady=2)

		btn_load = ttk.Button(file_panel, text="Cargar (.txt)", command=self._on_load)
		btn_load.grid(row=0, column=1, padx=4, pady=2)

		back = ttk.Button(self, text="← Volver", command=lambda: app.navigate("internas"))
		back.pack(pady=6)

		self.root = ResiduoNode()
		self._insert_order: List[str] = []
		self._path_highlight: List[Tuple[int, str]] = []  # (depth, chunk_label)
		self._delete_highlight: Optional[Tuple[int, str]] = None
		self._anim_steps: List[Tuple[int, str]] = []
		self._anim_index: int = 0
		self._anim_running: bool = False
		self._anim_delete: bool = False
		# Build full skeleton for current m (default 2) and 5 bits
		self._build_skeleton()
		self._draw()

	def _read_digits(self) -> int:
		# Fijo en 5 dígitos (posición en alfabeto)
		return 5

	def _read_m(self) -> int:
		try:
			m = int(self.entry_m.get().strip())
		except Exception:
			m = 2
		return max(1, min(4, m))

	def _chunk_plan(self, digits: int, m: int) -> List[int]:
		plan: List[int] = []
		remain = digits
		while remain > 0:
			c = m if remain >= m else remain
			plan.append(c)
			remain -= c
		return plan

	def _bits_of_len(self, length: int) -> List[str]:
		if length <= 0:
			return [""]
		count = 1 << length
		return [format(i, f"0{length}b") for i in range(count)]

	def _build_skeleton(self) -> None:
		# Preconstruir el árbol completo para claves de 5 bits con chunks de m bits
		d = self._read_digits()
		m = self._read_m()
		plan = self._chunk_plan(d, m)  # [2, 2, 1] para m=2 y 5 bits
		self.root = ResiduoNode()
		
		def build_level(node: ResiduoNode, level: int) -> None:
			if level >= len(plan):
				return
			# Para cada nivel, crear solo los chunks de ese tamaño
			chunk_size = plan[level]
			possible_chunks = self._bits_of_len(chunk_size)
			
			for chunk in possible_chunks:
				child = ResiduoNode()
				node.children[chunk] = child
				build_level(child, level + 1)
		
		build_level(self.root, 0)
		self._path_highlight = []
		self._delete_highlight = None
		self.status.configure(text=f"Árbol construido: niveles {plan} (m={m})")

	def _letter_to_bits(self, ch: str, digits: int) -> Optional[str]:
		if not ch or len(ch) != 1 or not ch.isalpha():
			messagebox.showerror("Error", "Ingrese una letra A-Z")
			return None
		idx = ord(ch.upper()) - ord('A') + 1
		if idx < 1 or idx > 26:
			messagebox.showerror("Error", "Letra fuera de rango A-Z")
			return None
		return format(idx, f"0{digits}b")

	def _bits_to_letter(self, bits: str) -> Optional[str]:
		try:
			val = int(bits, 2)
		except Exception:
			return None
		if 1 <= val <= 26:
			return chr(ord('A') + val - 1)
		return None

	def _chunk_bits(self, bits: str, m: int) -> List[str]:
		chunks: List[str] = []
		pos = 0
		while pos + m <= len(bits):
			chunks.append(bits[pos:pos + m])
			pos += m
		if pos < len(bits):
			chunks.append(bits[pos:])
		return chunks

	def _on_reset(self) -> None:
		self._insert_order = []
		self._build_skeleton()
		self.status.configure(text="Árbol reiniciado")
		self._draw()

	def _on_rebuild(self) -> None:
		# Rebuild skeleton when m changes
		self._insert_order = []
		self._build_skeleton()
		self._draw()

	def _on_insert(self) -> None:
		d = self._read_digits()
		m = self._read_m()
		ch = self.entry_key.get().strip()
		bits = self._letter_to_bits(ch, d)
		if bits is None:
			return

		# Ruta como aristas reales
		edges, nodes_path = self._build_path_edges_from_bits(bits, m)
		if not edges and len(bits) > 0:
			self.status.configure(text="Error en la navegación del árbol")
			return

		# Nodo final de la ruta
		end_node = nodes_path[-1] if nodes_path else self.root

		# Insertar letra si no está ocupada
		if not end_node.is_end or end_node.value is None:
			end_node.is_end = True
			end_node.value = ch.upper()
			self._insert_order.append(ch.upper())
			self.status.configure(text=f"Insertado {ch.upper()} - chunks: {self._chunk_bits(bits, m)}")
		else:
			self.status.configure(text=f"Posición ocupada por {end_node.value}")

		# Preparar animación con aristas exactas (no es delete)
		self._prepare_animation_from_edges(edges, delete=False)
		self._draw()


	def _on_search(self) -> None:
		d = self._read_digits()
		m = self._read_m()
		ch = self.entry_key.get().strip()
		bits = self._letter_to_bits(ch, d)
		if bits is None:
			return

		edges, nodes_path = self._build_path_edges_from_bits(bits, m)
		if not edges:
			self.status.configure(text="No encontrado")
			messagebox.showinfo("Búsqueda", "Valor no encontrado")
			self._prepare_animation_from_edges([], delete=False)
			return

		end_node = nodes_path[-1]
		if end_node.is_end and (end_node.value or "").upper() == ch.upper():
			self.status.configure(text=f"Encontrado en profundidad {len(edges)}")
			messagebox.showinfo("Búsqueda", f"Clave '{ch.upper()}' encontrada ✅")
			self._prepare_animation_from_edges(edges, delete=False)
		else:
			self.status.configure(text="No encontrado")
			messagebox.showinfo("Búsqueda", f"Clave '{ch.upper()}' no encontrada ❌")
			self._prepare_animation_from_edges(edges, delete=False)


	def _on_delete(self) -> None:
		d = self._read_digits()
		m = self._read_m()
		ch = self.entry_key.get().strip()
		bits = self._letter_to_bits(ch, d)
		if bits is None:
			return

		# Caso raíz (por completitud; normalmente no habrá letra en root)
		if self.root.is_end and (self.root.value or "").upper() == ch.upper():
			try:
				self._insert_order.remove(ch.upper())
			except ValueError:
				pass
			self._rebuild_from_order()
			self.status.configure(text="Eliminado de raíz y reordenado")
			self._prepare_animation_from_edges([], delete=True)
			return

		edges, nodes_path = self._build_path_edges_from_bits(bits, m)
		if not edges:
			self.status.configure(text="No encontrado")
			messagebox.showinfo("Búsqueda", "Valor no encontrado")
			self._prepare_animation_from_edges([], delete=False)
			return

		end_node = nodes_path[-1]
		if end_node.is_end and (end_node.value or "").upper() == ch.upper():
			# Quitar de orden e iniciar reconstrucción
			try:
				self._insert_order.remove(ch.upper())
			except ValueError:
				pass
			# Reconstruir esqueleto + reinsertar todo lo demás
			self._rebuild_from_order()
			self.status.configure(text=f"Eliminado en profundidad {len(edges)} y reordenado")
			# Animación de la ruta usada para llegar
			self._prepare_animation_from_edges(edges, delete=True)
		else:
			self.status.configure(text="No encontrado")
			messagebox.showinfo("Búsqueda", "Valor no encontrado")
			self._prepare_animation_from_edges(edges, delete=False)


	def _insert_value_internal(self, ch: str) -> None:
		# Inserta sin efectos de UI - navega hasta el nodo final y lo marca
		d = self._read_digits()
		m = self._read_m()
		bits = self._letter_to_bits(ch, d)
		if bits is None:
			return
		chunks = self._chunk_bits(bits, m)
		node = self.root
		# Navegar hasta el nodo final siguiendo los chunks
		for chunk in chunks:
			if chunk in node.children:
				node = node.children[chunk]
			else:
				# Si no existe el camino, el esqueleto no está completo
				return
		# Marcar el nodo final con la letra
		node.is_end = True
		node.value = ch.upper()

	def _rebuild_from_order(self) -> None:
		current = list(self._insert_order)
		self._build_skeleton()  # Reconstruir el esqueleto completo
		for letter in current:
			self._insert_value_internal(letter)
		self._path_highlight = []
		self._delete_highlight = None
		self._draw()

	def _serialize(self) -> str:
		# Guardar dígitos (5), m y valores explícitos (camino de bits y letra)
		vals: List[Tuple[str, str]] = []
		def dfs(node: ResiduoNode, bits_path: str) -> None:
			if node.is_end and node.value:
				vals.append((bits_path, node.value))
			# Orden estable por etiqueta de arista
			for chunk in sorted(node.children.keys()):
				dfs(node.children[chunk], bits_path + chunk)
		dfs(self.root, "")
		vals.sort(key=lambda x: (len(x[0]), x[0], x[1]))
		lines = [f"VAL:{path}:{val}" for path, val in vals]
		return f"digits:{self._read_digits()}\nm:{self._read_m()}\n" + "\n".join(lines) + "\n"

	def _parse(self, content: str) -> Optional[Tuple[int, int, List[Tuple[str, str]]]]:
		lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
		d = 5
		m = 2
		vals: List[Tuple[str, str]] = []
		for ln in lines:
			if ln.lower().startswith("digits:"):
				try:
					d = int(ln.split(":", 1)[1])
				except Exception:
					return None
			elif ln.lower().startswith("m:"):
				try:
					m = int(ln.split(":", 1)[1])
				except Exception:
					return None
			elif ln.startswith("VAL:"):
				parts = ln.split(":", 2)
				if len(parts) == 3:
					path, letter = parts[1], (parts[2] or "").strip().upper()
					if letter:
						vals.append((path, letter))
		return d, m, vals

	def _on_save(self) -> None:
		path = filedialog.asksaveasfilename(title="Guardar árbol RM", defaultextension=".txt", filetypes=[("Texto", "*.txt")])
		if not path:
			return
		try:
			with open(path, "w", encoding="utf-8") as f:
				f.write(self._serialize())
		except Exception as e:
			messagebox.showerror("Error", f"No se pudo guardar: {e}")

	def _on_load(self) -> None:
		path = filedialog.askopenfilename(title="Cargar árbol RM", filetypes=[("Texto", "*.txt")])
		if not path:
			return
		try:
			with open(path, "r", encoding="utf-8") as f:
				content = f.read()
		except Exception as e:
			messagebox.showerror("Error", f"No se pudo leer: {e}")
			return
		parsed = self._parse(content)
		if not parsed:
			messagebox.showerror("Error", "Formato inválido")
			return
		d, m, vals = parsed
		# Set m
		self.entry_m.delete(0, tk.END)
		self.entry_m.insert(0, str(max(1, min(4, m))))
		# Rebuild from ordered letters
		# Rebuild skeleton for loaded m and then insert in order
		self._insert_order = [letter for _, letter in vals]
		self._build_skeleton()
		for _, letter in vals:
			self._insert_value_internal(letter)
		self._path_highlight = []
		self._delete_highlight = None
		self.status.configure(text="Árbol cargado")
		self._draw()

	def _prepare_animation(self, delete: bool = False) -> None:
		self._anim_steps = list(self._path_highlight)
		self._anim_index = 0
		self._anim_delete = delete
		self._anim_running = False
		self._draw()
		self.status.configure(text=f"Animación lista: {len(self._anim_steps)} pasos")

	def _anim_step(self) -> None:
		if self._anim_index >= len(self._anim_steps):
			self._anim_running = False
			return
		parent, child = self._anim_steps[self._anim_index]
		self._draw(edge_hint=(parent, child), delete=self._anim_delete)
		self._anim_index += 1
		if self._anim_running and self._anim_index < len(self._anim_steps):
			self.after(700, self._anim_step)


	def _on_play(self) -> None:
		if not self._anim_steps:
			return
		if self._anim_index >= len(self._anim_steps):
			self._anim_index = 0
		self._anim_running = True
		self._anim_step()

	def _on_pause(self) -> None:
		self._anim_running = False

	def _on_next(self) -> None:
		self._anim_running = False
		self._anim_step()

	def _on_reset_anim(self) -> None:
		self._anim_running = False
		self._anim_index = 0
		self._draw()

	def _draw(self, edge_hint: Optional[Tuple['ResiduoNode', 'ResiduoNode']] = None, delete: bool = False) -> None:
		self.canvas.delete("all")

		# --- parámetros de layout ---
		node_radius = 16
		min_sep_px = 3 * node_radius        # separación mínima entre centros de nodos hermanos
		margin_x = 32 + node_radius
		margin_y = 32 + node_radius
		level_gap_min = 80                   # separación mínima vertical entre niveles

		# Recolectar stats del árbol (profundidad máxima) y calcular spans (ancho en unidades)
		spans: Dict[ResiduoNode, int] = {}
		depths: Dict[ResiduoNode, int] = {}

		def dfs_depth(node: ResiduoNode, depth: int) -> int:
			depths[node] = depth
			if not node.children:
				return depth
			return max(dfs_depth(ch, depth + 1) for ch in node.children.values())

		max_depth = dfs_depth(self.root, 0)

		def dfs_span(node: ResiduoNode) -> int:
			# ancho en "unidades" = 1 si es hoja; si no, suma de spans de hijos
			if not node.children:
				spans[node] = 1
				return 1
			s = 0
			for k in sorted(node.children.keys()):
				s += dfs_span(node.children[k])
			spans[node] = max(1, s)
			return spans[node]

		dfs_span(self.root)

		# Convertir "unidades" a píxeles con escalado para que quepa en el canvas
		width = max(self.canvas.winfo_width(), self.canvas.winfo_reqwidth())
		height = max(self.canvas.winfo_height(), self.canvas.winfo_reqheight())

		total_units = spans[self.root]
		# espacio horizontal disponible
		avail_w = max(1, width - 2 * margin_x)
		# px por unidad, respetando separación mínima entre nodos
		unit_px = max(min_sep_px, avail_w / max(1, total_units))
		# recalcular separación vertical para que quepa en altura
		levels = max_depth + 1
		avail_h = max(1, height - 2 * margin_y)
		depth_gap = max(level_gap_min, avail_h / max(1, levels - 1)) if levels > 1 else 0

		# Segunda pasada: asignar X centrando cada subárbol en su intervalo
		positions: Dict[ResiduoNode, Tuple[int, int, int]] = {}
		edges: List[Tuple[ResiduoNode, ResiduoNode, str, int, int]] = []  # + child idx para etiquetas

		def assign_x(node: ResiduoNode, left_unit: float) -> float:
			"""
			Asigna X al centro del intervalo [left_unit, left_unit + spans[node])
			Devuelve el left_unit final tras distribuir a los hijos.
			"""
			span_u = spans[node]
			# centro del nodo en unidades:
			center_u = left_unit + span_u / 2.0
			x_px = int(margin_x + center_u * unit_px)
			y_px = int(margin_y + depths[node] * depth_gap)
			positions[node] = (x_px, y_px, depths[node])

			# distribuir hijos, uno tras otro en sus intervalos consecutivos
			cur_left = left_unit
			if node.children:
				for idx, k in enumerate(sorted(node.children.keys())):
					child = node.children[k]
					child_span = spans[child]
					# intervalo del hijo
					child_left = cur_left
					cur_left += child_span
					# asignar al hijo en su intervalo
					assign_x(child, child_left)
					edges.append((node, child, k, depths[node], idx))
			return left_unit + span_u

		assign_x(self.root, 0.0)

		# --- Dibujo de aristas ---
		for parent, child, chunk, depth, idx in edges:
			px, py, _ = positions[parent]
			cx, cy, _ = positions[child]

			color = "#808080"
			if edge_hint is not None:
				if parent is edge_hint[0] and child is edge_hint[1]:
					color = "#ff6666" if delete else "#4da3ff"

			# línea suavizada (curva sutil)
			midx = (px + cx) // 2
			c1y = py + int(0.35 * (cy - py))
			c2y = py + int(0.65 * (cy - py))
			self.canvas.create_line(px, py, midx, c1y, cx, cy, fill=color, width=2, smooth=True)

			# Etiqueta del chunk: alternar pequeño offset vertical para evitar colisiones
			label_offset = -12 if (idx % 2 == 0) else -24
			self.canvas.create_text(midx, c1y + label_offset, text=chunk,
									fill="#000000", font=("MS Sans Serif", 9, "bold"))

			# --- Dibujo de nodos ---
			for node, (x, y, depth) in positions.items():
				fill = "#bdbdbd"
				outline = "#808080"

				# Si estamos animando una arista, resalta solo el nodo destino (child)
				if edge_hint is not None and node is edge_hint[1]:
					fill = "#ff6666" if delete else "#4da3ff"
					outline = "#255eaa"

				self.canvas.create_oval(
					x - node_radius, y - node_radius,
					x + node_radius, y + node_radius,
					fill=fill, outline=outline, width=2
				)

				if node.is_end:
					text = node.value if node.value else "*"
					self.canvas.create_text(
						x, y, text=text, fill="#000000",
						font=("MS Sans Serif", 10, "bold")
					)


	def _build_path_edges_from_bits(self, bits: str, m: int) -> Tuple[List[Tuple[ResiduoNode, ResiduoNode, str, int]], List[ResiduoNode]]:
		"""
		Devuelve:
		- edges: lista de aristas (parent, child, chunk, depth) para cada chunk recorrido
		- nodes: nodos visitados en orden (incluye root y cada child sucesivo)
		Si algún chunk no existe en el esqueleto, retorna listas vacías.
		"""
		edges: List[Tuple[ResiduoNode, ResiduoNode, str, int]] = []
		nodes: List[ResiduoNode] = []

		node = self.root
		nodes.append(node)
		for depth, chunk in enumerate(self._chunk_bits(bits, m), start=1):
			child = node.children.get(chunk)
			if not child:
				return [], []
			edges.append((node, child, chunk, depth))
			nodes.append(child)
			node = child
		return edges, nodes
	
	def _prepare_animation_from_edges(self, edges: List[Tuple['ResiduoNode', 'ResiduoNode', str, int]], delete: bool = False) -> None:
		# Guardamos solo (parent, child) para el draw
		self._anim_steps = [(p, c) for (p, c, _chunk, _depth) in edges]
		self._anim_index = 0
		self._anim_delete = delete
		self._anim_running = False
		self._draw()
		self.status.configure(text=f"Animación lista: {len(self._anim_steps)} pasos")
