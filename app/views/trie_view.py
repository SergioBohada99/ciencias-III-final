import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Optional, List, Tuple


class TrieNode:
	def __init__(self) -> None:
		self.children: Dict[str, 'TrieNode'] = {}
		self.is_end: bool = False
		self.value: Optional[str] = None


class TrieView(ttk.Frame):
	def __init__(self, parent: tk.Misc, app) -> None:
		super().__init__(parent)

		title = ttk.Label(self, text="Árbol digital", style="Title.TLabel")
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

		btn_insert = ttk.Button(ops, text="Insertar", style="Retro.TButton", command=self._on_insert)
		btn_insert.grid(row=2, column=0, pady=4, sticky="ew")

		btn_delete = ttk.Button(ops, text="Eliminar", style="Retro.TButton", command=self._on_delete)
		btn_delete.grid(row=3, column=0, pady=4, sticky="ew")

		btn_search = ttk.Button(ops, text="Buscar", style="Retro.TButton", command=self._on_search)
		btn_search.grid(row=4, column=0, pady=4, sticky="ew")

		btn_reset_struct = ttk.Button(ops, text="Reiniciar estructura", command=self._on_reset)
		btn_reset_struct.grid(row=5, column=0, pady=6, sticky="ew")

		# Animation controls
		anim_lbl = ttk.Label(ops, text="Controles de animación")
		anim_lbl.grid(row=6, column=0, sticky="w", pady=(8, 2))
		row_base = 7
		btn_play = ttk.Button(ops, text="▶ Reproducir", command=self._on_play)
		btn_play.grid(row=row_base, column=0, pady=2, sticky="ew")
		btn_pause = ttk.Button(ops, text="⏸ Pausa", command=self._on_pause)
		btn_pause.grid(row=row_base + 1, column=0, pady=2, sticky="ew")
		btn_next = ttk.Button(ops, text="Paso", command=self._on_next)
		btn_next.grid(row=row_base + 2, column=0, pady=2, sticky="ew")
		btn_reset_anim = ttk.Button(ops, text="Reiniciar animación", command=self._on_reset_anim)
		btn_reset_anim.grid(row=row_base + 3, column=0, pady=2, sticky="ew")
		
		# Botón de deshacer
		btn_undo = ttk.Button(ops, text="↶ Deshacer (Ctrl+Z)", command=self._on_undo)
		btn_undo.grid(row=row_base + 4, column=0, pady=2, sticky="ew")

		self.status = ttk.Label(ops, text="Estado: listo")
		self.status.grid(row=row_base + 5, column=0, pady=(12, 0), sticky="w")

		viz = ttk.Frame(panel, style="Panel.TFrame", padding=8)
		viz.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

		self.canvas = tk.Canvas(viz, background="#ffffff", height=460)
		self.canvas.pack(fill=tk.BOTH, expand=True)
		# Redraw on resize so the root stays centered after initial load
		self.canvas.bind("<Configure>", lambda e: self._draw())

		# Save/load panel
		file_panel = ttk.Frame(self, style="Panel.TFrame", padding=8)
		file_panel.pack(fill=tk.X, padx=4, pady=6)

		btn_save_close = ttk.Button(file_panel, text="Guardar y cerrar", command=self._on_save_and_close)
		btn_save_close.grid(row=0, column=0, padx=4, pady=2)

		btn_save = ttk.Button(file_panel, text="Guardar", command=self._on_save)
		btn_save.grid(row=0, column=1, padx=4, pady=2)

		btn_load = ttk.Button(file_panel, text="Cargar", command=self._on_load)
		btn_load.grid(row=0, column=2, padx=4, pady=2)

		back = ttk.Button(self, text="← Volver", command=lambda: app.navigate("internas"))
		back.pack(pady=6)

		self.app = app

		self.root = TrieNode()
		self._insert_order: List[str] = []
		self._path_highlight: List[Tuple[int, int, str]] = []
		self._delete_highlight: Optional[Tuple[int, int, str]] = None
		self._anim_steps: List[Tuple[int, int, str]] = []
		self._anim_index: int = 0
		self._anim_running: bool = False
		self._anim_delete: bool = False
		
		# Undo mechanism
		self._history: List[List[str]] = []
		self._max_history = 20  # Máximo 20 estados en el historial
		
		# Bind Ctrl+Z
		self.bind_all("<Control-z>", self._on_undo)
		
		self._draw()

	def _save_state(self) -> None:
		"""Guarda el estado actual en el historial para poder deshacerlo"""
		current_state = list(self._insert_order)  # Copia de la lista
		self._history.append(current_state)
		
		# Mantener solo los últimos N estados
		if len(self._history) > self._max_history:
			self._history.pop(0)

	def _on_reset(self) -> None:
		self._save_state()  # Guardar estado antes de reiniciar
		self.root = TrieNode()
		self._path_highlight = []
		self._delete_highlight = None
		self._insert_order = []
		self.status.configure(text="Trie reiniciado")
		self._draw()

	def _read_digits(self) -> int:
		return 5

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

	def _on_insert(self) -> None:
		d = self._read_digits()
		ch = self.entry_key.get().strip()
		bits = self._letter_to_bits(ch, d)
		if bits is None:
			return
		
		# Guardar estado antes de insertar
		self._save_state()
		
		# If completely empty, place at root
		if not self.root.is_end and (self.root.value is None) and not self.root.children:
			self._path_highlight = [(0, 0, '')]
			self.root.is_end = True
			self.root.value = ch.upper()
			self._insert_order.append(ch.upper())
			self.status.configure(text=f"Insertado {ch} en raíz")
			self._prepare_animation(delete=False)
			return
		# Traverse bits; place at the first available node along the path
		node = self.root
		self._path_highlight = []
		for depth, b in enumerate(bits):
			self._path_highlight.append((depth, 0 if b == '0' else 1, b))
			child = node.children.get(b)
			if child is None:
				child = TrieNode()
				node.children[b] = child
				child.is_end = True
				child.value = ch.upper()
				self._insert_order.append(ch.upper())
				self.status.configure(text=f"Insertado {ch} en profundidad {depth + 1}")
				self._prepare_animation(delete=False)
				return
			# If child exists but is free of value, occupy it
			if not child.is_end and child.value is None:
				child.is_end = True
				child.value = ch.upper()
				self._insert_order.append(ch.upper())
				self.status.configure(text=f"Insertado {ch} en profundidad {depth + 1}")
				self._prepare_animation(delete=False)
				return
			node = child
		# If all path nodes already had values, keep last and overwrite? No: report ocupado
		self.status.configure(text="Ruta completa ocupada, no insertado")
		self._prepare_animation(delete=False)

	def _on_search(self) -> None:
		d = self._read_digits()
		ch = self.entry_key.get().strip()
		bits = self._letter_to_bits(ch, d)
		if bits is None:
			return
		# Check root
		if self.root.is_end and (self.root.value or "").upper() == ch.upper():
			self._path_highlight = [(0, 0, '')]
			self.status.configure(text="Encontrado en raíz")
			self._prepare_animation(delete=False)
			return
		# Traverse; match as soon as the node along the path holds the value
		node = self.root
		self._path_highlight = []
		for depth, b in enumerate(bits):
			self._path_highlight.append((depth, 0 if b == '0' else 1, b))
			next_node = node.children.get(b)
			if not next_node:
				self.status.configure(text="No encontrado")
				messagebox.showinfo("Búsqueda", "Valor no encontrado")
				self._prepare_animation(delete=False)
				return
			node = next_node
			if node.is_end and (node.value or "").upper() == ch.upper():
				self.status.configure(text=f"Encontrado en profundidad {depth + 1}")
				self._prepare_animation(delete=False)
				return
		self.status.configure(text="No encontrado")
		messagebox.showinfo("Búsqueda", "Valor no encontrado")
		self._prepare_animation(delete=False)

	def _on_delete(self) -> None:
		d = self._read_digits()
		ch = self.entry_key.get().strip()
		bits = self._letter_to_bits(ch, d)
		if bits is None:
			return
		
		# Guardar estado antes de eliminar
		self._save_state()
		
		# Check root
		if self.root.is_end and (self.root.value or "").upper() == ch.upper():
			self._path_highlight = [(0, 0, '')]
			self._delete_highlight = self._path_highlight[-1]
			# update order and rebuild
			try:
				self._insert_order.remove(ch.upper())
			except ValueError:
				pass
			self._rebuild_from_order()
			self.status.configure(text="Eliminado de raíz y reordenado")
			self._prepare_animation(delete=True)
			return
		# Traverse and collect path for pruning; delete as soon as we meet the node with the value
		node = self.root
		self._path_highlight = []
		path_nodes: List[Tuple[TrieNode, str]] = []
		for depth, b in enumerate(bits):
			self._path_highlight.append((depth, 0 if b == '0' else 1, b))
			next_node = node.children.get(b)
			if not next_node:
				self.status.configure(text="No encontrado")
				messagebox.showinfo("Búsqueda", "Valor no encontrado")
				self._prepare_animation(delete=False)
				# Restaurar estado ya que no se eliminó nada
				if self._history:
					self._history.pop()  # Remover el estado que acabamos de guardar
				return
			path_nodes.append((node, b))
			node = next_node
			if node.is_end and (node.value or "").upper() == ch.upper():
				self._delete_highlight = self._path_highlight[-1]
				# update order and rebuild from original insertion sequence
				try:
					self._insert_order.remove(ch.upper())
				except ValueError:
					pass
				self._rebuild_from_order()
				self.status.configure(text=f"Eliminado en profundidad {depth + 1} y reordenado")
				self._prepare_animation(delete=True)
				return
		self.status.configure(text="No encontrado")
		messagebox.showinfo("Búsqueda", "Valor no encontrado")
		self._prepare_animation(delete=False)
		# Restaurar estado ya que no se eliminó nada
		if self._history:
			self._history.pop()  # Remover el estado que acabamos de guardar

	def _insert_value_internal(self, ch: str) -> None:
		# Insert without UI side-effects, respecting the same placement rules
		d = self._read_digits()
		bits = self._letter_to_bits(ch, d)
		if bits is None:
			return
		if not self.root.is_end and (self.root.value is None) and not self.root.children:
			self.root.is_end = True
			self.root.value = ch.upper()
			return
		node = self.root
		for b in bits:
			child = node.children.get(b)
			if child is None:
				child = TrieNode()
				node.children[b] = child
				child.is_end = True
				child.value = ch.upper()
				return
			if not child.is_end and child.value is None:
				child.is_end = True
				child.value = ch.upper()
				return
			node = child

	def _rebuild_from_order(self) -> None:
		# Recreate the trie using the original insertion order
		current_order = list(self._insert_order)
		self.root = TrieNode()
		for letter in current_order:
			self._insert_value_internal(letter)
		self._path_highlight = []
		self._delete_highlight = None
		self._draw()

	def _serialize(self) -> str:
		# Serialize explicit values to avoid ambiguity with partial paths
		vals: List[Tuple[str, str]] = []
		def dfs(node: TrieNode, prefix: str) -> None:
			if node.is_end and node.value:
				vals.append((prefix, node.value))
			for bit in ('0', '1'):
				child = node.children.get(bit)
				if child:
					dfs(child, prefix + bit)
		dfs(self.root, "")
		# stable order
		vals.sort(key=lambda x: (len(x[0]), x[0], x[1]))
		lines = [f"VAL:{path}:{val}" for path, val in vals]
		d = self._read_digits()
		return f"digits:{d}\n" + "\n".join(lines) + "\n"

	def _parse(self, content: str) -> Optional[int]:
		lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
		d = 5
		vals: List[Tuple[str, str]] = []
		edges: List[str] = []
		ends: List[str] = []
		for ln in lines:
			if ln.lower().startswith("digits:"):
				try:
					d = int(ln.split(":", 1)[1])
				except Exception:
					return None
			elif ln.startswith("VAL:"):
				# format VAL:<path>:<LETTER>
				parts = ln.split(":", 2)
				if len(parts) == 3:
					path, letter = parts[1], parts[2]
					letter = (letter or "").strip().upper()
					if letter:
						vals.append((path, letter))
			elif ln.startswith("EDGE:"):
				edges.append(ln[5:])
			elif ln.startswith("END:"):
				ends.append(ln[4:])
		self.root = TrieNode()
		if vals:
			# preserve input order as insertion order for future rebuilds
			self._insert_order = [letter for _, letter in vals]
			for path, letter in vals:
				node = self.root
				for b in path:
					if b not in node.children:
						node.children[b] = TrieNode()
					node = node.children[b]
				node.is_end = True
				node.value = letter
			return d
		# Fallback legacy format
		for path in edges:
			node = self.root
			for b in path:
				if b not in node.children:
					node.children[b] = TrieNode()
				node = node.children[b]
		for path in ends:
			node = self.root
			for b in path:
				node = node.children.get(b, TrieNode())
			node.is_end = True
			letter = self._bits_to_letter(path)
			node.value = letter.upper() if letter else None
		return d

	def _on_save(self) -> None:
		path = filedialog.asksaveasfilename(title="Guardar trie", defaultextension=".txt", filetypes=[("Texto", "*.txt")])
		if not path:
			return
		try:
			with open(path, "w", encoding="utf-8") as f:
				f.write(self._serialize())
			messagebox.showinfo("Éxito", "Trie guardado correctamente")
		except Exception as e:
			messagebox.showerror("Error", f"No se pudo guardar: {e}")

	def _on_save_and_close(self) -> None:
		path = filedialog.asksaveasfilename(title="Guardar trie", defaultextension=".txt", filetypes=[("Texto", "*.txt")])
		if not path:
			return
		try:
			with open(path, "w", encoding="utf-8") as f:
				f.write(self._serialize())
			messagebox.showinfo("Éxito", "Trie guardado correctamente")
			self.app.navigate("internas")
		except Exception as e:
			messagebox.showerror("Error", f"No se pudo guardar: {e}")

	def _on_undo(self, event=None) -> None:
		"""Deshace la última operación realizada"""
		if not self._history:
			self.status.configure(text="No hay operaciones para deshacer")
			messagebox.showinfo("Deshacer", "No hay operaciones para deshacer")
			return
		
		# Restaurar el último estado guardado
		last_state = self._history.pop()
		self._insert_order = list(last_state)  # Copia de la lista
		
		# Reconstruir el trie desde el estado restaurado
		self._rebuild_from_order()
		self.status.configure(text=f"Operación deshecha. Estados restantes: {len(self._history)}")
		self._draw()

	def _on_load(self) -> None:
		# Guardar estado antes de cargar
		self._save_state()
		
		path = filedialog.askopenfilename(title="Cargar trie", filetypes=[("Texto", "*.txt")])
		if not path:
			# Restaurar estado ya que no se cargó nada
			if self._history:
				self._history.pop()
			return
		try:
			with open(path, "r", encoding="utf-8") as f:
				content = f.read()
		except Exception as e:
			messagebox.showerror("Error", f"No se pudo leer: {e}")
			# Restaurar estado ya que no se cargó nada
			if self._history:
				self._history.pop()
			return
		d = self._parse(content)
		if d is None:
			messagebox.showerror("Error", "Formato inválido")
			# Restaurar estado ya que no se cargó nada
			if self._history:
				self._history.pop()
			return
		# Parámetro de dígitos fijo en 5; ignoramos lo cargado
		self._path_highlight = []
		self._delete_highlight = None
		self.status.configure(text="Trie cargado")
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

	def _draw(self, path_hint: Optional[Tuple[int, int, str]] = None, delete: bool = False) -> None:
		self.canvas.delete("all")
		# Always layout so that bit '0' goes to the left and bit '1' to the right
		depth_gap = 80
		node_radius = 16
		width = self.canvas.winfo_width() or self.canvas.winfo_reqwidth()
		height = self.canvas.winfo_height() or self.canvas.winfo_reqheight()

		# Position map for nodes
		positions: Dict[TrieNode, Tuple[int, int, str, int]] = {}
		edges: List[Tuple[TrieNode, TrieNode, str, int]] = []

		def layout(node: TrieNode, depth: int, x: int, label: str) -> None:
			y = 40 + depth * depth_gap
			positions[node] = (x, y, label, depth)
			# spacing shrinks with depth to keep children near their parent
			base = max(60, width // 4)
			dx = max(40, base // (2 ** max(1, depth)))
			# Ensure deterministic order: left '0' then right '1'
			for bit in ('0', '1'):
				child = node.children.get(bit)
				if not child:
					continue
				cx = x - dx if bit == '0' else x + dx
				edges.append((node, child, bit, depth))
				layout(child, depth + 1, cx, bit)

		# Start from root at center
		layout(self.root, 0, (width // 2), "")

		# Draw edges first and place bit labels on edges
		for parent, child, bit, depth in edges:
			px, py, _, pdepth = positions[parent]
			cx, cy, _, cdepth = positions[child]
			color = "#808080"
			if path_hint and path_hint[0] == depth and path_hint[2] == bit:
				color = "#ff6666" if delete else "#4da3ff"
			self.canvas.create_line(px, py, cx, cy, fill=color, width=2)
			# Edge label (0/1) near the midpoint of the edge
			mx = (px + cx) // 2
			my = (py + cy) // 2
			self.canvas.create_text(mx, my - 10, text=bit, fill="#000000", font=("MS Sans Serif", 9, "bold"))

		# Draw nodes (without 0/1 labels; labels are on edges)
		for node, (x, y, label, depth) in positions.items():
			fill = "#bdbdbd"
			outline = "#808080"
			if path_hint and path_hint[0] == depth:
				fill = "#ff6666" if delete else "#4da3ff"
				outline = "#255eaa"
			self.canvas.create_oval(x - node_radius, y - node_radius, x + node_radius, y + node_radius, fill=fill, outline=outline, width=2)
			if node.is_end:
				text = node.value if node.value else "*"
				self.canvas.create_text(x, y, text=text, fill="#000000", font=("MS Sans Serif", 10, "bold"))


