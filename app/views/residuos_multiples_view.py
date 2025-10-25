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
		
		# Debug: mostrar la conversión
		print(f"Letra {ch.upper()} -> bits: {bits}")
		
		# Navegar hasta el nodo final del esqueleto preconstruido
		self._path_highlight = []
		chunks = self._chunk_bits(bits, m)
		print(f"Chunks: {chunks}")
		
		node = self.root
		path_valid = True
		
		# Construir el path highlight para la animación
		for depth, chunk in enumerate(chunks, start=1):
			self._path_highlight.append((depth, chunk))
			if chunk in node.children:
				node = node.children[chunk]
				print(f"Navegando a nivel {depth} con chunk '{chunk}' - OK")
			else:
				print(f"ERROR: No existe chunk '{chunk}' en nivel {depth}")
				path_valid = False
				break
		
		if not path_valid:
			self.status.configure(text="Error en la navegación del árbol")
			return
		
		# Verificar si el nodo final ya tiene una letra
		if not node.is_end or node.value is None:
			node.is_end = True
			node.value = ch.upper()
			self._insert_order.append(ch.upper())
			self.status.configure(text=f"Insertado {ch.upper()} - chunks: {chunks}")
			print(f"Letra {ch.upper()} insertada correctamente")
		else:
			self.status.configure(text=f"Posición ocupada por {node.value}")
		
		self._prepare_animation(delete=False)
		self._draw()

	def _on_search(self) -> None:
		d = self._read_digits()
		m = self._read_m()
		ch = self.entry_key.get().strip()
		bits = self._letter_to_bits(ch, d)
		if bits is None:
			return
		# Check root
		if self.root.is_end and (self.root.value or "").upper() == ch.upper():
			self._path_highlight = [(0, '')]
			self.status.configure(text="Encontrado en raíz")
			self._prepare_animation(delete=False)
			return
		node = self.root
		self._path_highlight = []
		for depth, chunk in enumerate(self._chunk_bits(bits, m), start=1):
			self._path_highlight.append((depth, chunk))
			next_node = node.children.get(chunk)
			if not next_node:
				self.status.configure(text="No encontrado")
				messagebox.showinfo("Búsqueda", "Valor no encontrado")
				self._prepare_animation(delete=False)
				return
			node = next_node
			if node.is_end and (node.value or "").upper() == ch.upper():
				self.status.configure(text=f"Encontrado en profundidad {depth}")
				self._prepare_animation(delete=False)
				return
		self.status.configure(text="No encontrado")
		messagebox.showinfo("Búsqueda", "Valor no encontrado")
		self._prepare_animation(delete=False)

	def _on_delete(self) -> None:
		d = self._read_digits()
		m = self._read_m()
		ch = self.entry_key.get().strip()
		bits = self._letter_to_bits(ch, d)
		if bits is None:
			return
		# Root case
		if self.root.is_end and (self.root.value or "").upper() == ch.upper():
			self._path_highlight = [(0, '')]
			self._delete_highlight = self._path_highlight[-1]
			try:
				self._insert_order.remove(ch.upper())
			except ValueError:
				pass
			self._rebuild_from_order()
			self.status.configure(text="Eliminado de raíz y reordenado")
			self._prepare_animation(delete=True)
			return
		node = self.root
		self._path_highlight = []
		path_nodes: List[Tuple[ResiduoNode, str]] = []
		for depth, chunk in enumerate(self._chunk_bits(bits, m), start=1):
			self._path_highlight.append((depth, chunk))
			next_node = node.children.get(chunk)
			if not next_node:
				self.status.configure(text="No encontrado")
				messagebox.showinfo("Búsqueda", "Valor no encontrado")
				self._prepare_animation(delete=False)
				return
			path_nodes.append((node, chunk))
			node = next_node
			if node.is_end and (node.value or "").upper() == ch.upper():
				self._delete_highlight = self._path_highlight[-1]
				try:
					self._insert_order.remove(ch.upper())
				except ValueError:
					pass
				self._rebuild_from_order()
				self.status.configure(text=f"Eliminado en profundidad {depth} y reordenado")
				self._prepare_animation(delete=True)
				return
		self.status.configure(text="No encontrado")
		messagebox.showinfo("Búsqueda", "Valor no encontrado")
		self._prepare_animation(delete=False)

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
		item = self._anim_steps[self._anim_index]
		is_delete_step = self._anim_delete and item == (self._delete_highlight or ())
		self._draw(path_hint=item, delete=is_delete_step)
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

	def _draw(self, path_hint: Optional[Tuple[int, str]] = None, delete: bool = False) -> None:
		self.canvas.delete("all")
		depth_gap = 80
		node_radius = 16
		width = self.canvas.winfo_width() or self.canvas.winfo_reqwidth()
		# Position map for nodes
		positions: Dict[ResiduoNode, Tuple[int, int, int]] = {}
		edges: List[Tuple[ResiduoNode, ResiduoNode, str, int]] = []

		def layout(node: ResiduoNode, depth: int, x: int) -> None:
			y = 40 + depth * depth_gap
			positions[node] = (x, y, depth)
			children_keys = sorted(node.children.keys())
			if not children_keys:
				return
			# spacing adapts to number of children
			base = max(60, width // 4)
			dx = max(40, base // max(1, len(children_keys)))
			start_x = x - dx * (len(children_keys) - 1) // 2
			for idx, chunk in enumerate(children_keys):
				child = node.children[chunk]
				cx = start_x + idx * dx
				edges.append((node, child, chunk, depth))
				layout(child, depth + 1, cx)

		# Root centered
		layout(self.root, 0, (width // 2))

		# Draw edges with chunk labels
		for parent, child, chunk, depth in edges:
			px, py, _ = positions[parent]
			cx, cy, _ = positions[child]
			color = "#808080"
			if path_hint and path_hint[0] == depth + 1 and path_hint[1] == chunk:
				color = "#ff6666" if delete else "#4da3ff"
			self.canvas.create_line(px, py, cx, cy, fill=color, width=2)
			mx = (px + cx) // 2
			my = (py + cy) // 2
			self.canvas.create_text(mx, my - 10, text=chunk, fill="#000000", font=("MS Sans Serif", 9, "bold"))

		# Draw nodes
		for node, (x, y, depth) in positions.items():
			fill = "#bdbdbd"
			outline = "#808080"
			if path_hint and path_hint[0] == depth:
				fill = "#ff6666" if delete else "#4da3ff"
				outline = "#255eaa"
			self.canvas.create_oval(x - node_radius, y - node_radius, x + node_radius, y + node_radius, fill=fill, outline=outline, width=2)
			if node.is_end:
				text = node.value if node.value else "*"
				self.canvas.create_text(x, y, text=text, fill="#000000", font=("MS Sans Serif", 10, "bold"))


