import heapq
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Optional, List, Tuple, Any


class HuffmanNode:
	def __init__(self, char: Optional[str] = None, freq: int = 0, left: Optional['HuffmanNode'] = None, right: Optional['HuffmanNode'] = None) -> None:
		self.char = char
		self.freq = freq
		self.left = left
		self.right = right
	
	def __lt__(self, other: 'HuffmanNode') -> bool:
		return self.freq < other.freq


class HuffmanView(ttk.Frame):
	def __init__(self, parent: tk.Misc, app) -> None:
		super().__init__(parent)

		title = ttk.Label(self, text="Árboles de Huffman", style="Title.TLabel")
		title.pack(pady=(20, 5))

		# Panel paralelo
		panel = ttk.Frame(self, padding=6)
		panel.pack(fill=tk.BOTH, expand=True)

		ops = ttk.Frame(panel, style="Panel.TFrame", padding=10)
		ops.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))

		lbl_char = ttk.Label(ops, text="Letra (A-Z):")
		lbl_char.grid(row=0, column=0, sticky="w")
		self.entry_char = ttk.Entry(ops, width=8)
		self.entry_char.grid(row=1, column=0, pady=(0, 10))

		btn_add = ttk.Button(ops, text="Agregar letra", style="Retro.TButton", command=self._on_add_char)
		btn_add.grid(row=2, column=0, pady=4, sticky="ew")

		btn_remove = ttk.Button(ops, text="Eliminar letra", style="Retro.TButton", command=self._on_remove_char)
		btn_remove.grid(row=3, column=0, pady=4, sticky="ew")

		btn_build = ttk.Button(ops, text="Construir árbol", style="Retro.TButton", command=self._on_build_tree)
		btn_build.grid(row=4, column=0, pady=4, sticky="ew")

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
		# Redraw on resize so the tree stays centered after initial load
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

		self.root_node: Optional[HuffmanNode] = None
		self.huffman_codes: Dict[str, str] = {}
		self.frequencies: Dict[str, int] = {}
		self.current_text: str = ""  # Texto actual construido letra por letra
		self._highlight_nodes: List[HuffmanNode] = []
		self._anim_steps: List[Tuple[str, Any]] = []
		self._anim_index: int = 0
		self._anim_running: bool = False
		
		# Undo mechanism
		self._history: List[Dict[str, Any]] = []
		self._max_history = 20  # Máximo 20 estados en el historial
		
		# Bind Ctrl+Z
		self.bind_all("<Control-z>", self._on_undo)
		
		self._draw()

	def _save_state(self) -> None:
		"""Guarda el estado actual en el historial para poder deshacerlo"""
		current_state = {
			'text': self.current_text,
			'frequencies': dict(self.frequencies),
			'huffman_codes': dict(self.huffman_codes),
			'root_node': self._serialize_node(self.root_node) if self.root_node else None
		}
		self._history.append(current_state)
		
		# Mantener solo los últimos N estados
		if len(self._history) > self._max_history:
			self._history.pop(0)

	def _serialize_node(self, node: Optional[HuffmanNode]) -> Optional[Dict[str, Any]]:
		"""Serializa un nodo del árbol de Huffman"""
		if node is None:
			return None
		return {
			'char': node.char,
			'freq': node.freq,
			'left': self._serialize_node(node.left),
			'right': self._serialize_node(node.right)
		}

	def _deserialize_node(self, data: Optional[Dict[str, Any]]) -> Optional[HuffmanNode]:
		"""Deserializa un nodo del árbol de Huffman"""
		if data is None:
			return None
		node = HuffmanNode(
			char=data['char'],
			freq=data['freq']
		)
		node.left = self._deserialize_node(data.get('left'))
		node.right = self._deserialize_node(data.get('right'))
		return node

	def _validate_char(self, char_str: str) -> Optional[str]:
		"""Valida que la entrada sea una letra válida"""
		if not char_str or len(char_str) != 1:
			messagebox.showerror("Error", "Ingrese una sola letra")
			return None
		if not char_str.isalpha():
			messagebox.showerror("Error", "Ingrese solo letras (A-Z)")
			return None
		return char_str.upper()

	def _rebuild_tree(self) -> None:
		"""Reconstruye el árbol de Huffman con las frecuencias actuales"""
		if not self.frequencies:
			self.root_node = None
			self.huffman_codes = {}
			self._draw()
			return

		# Crear nodos hoja con prioridad estable (freq, orden, nodo)
		heap: List[Tuple[int, int, HuffmanNode]] = []
		counter = 0  # contador global de creación de nodos

		# dict mantiene el orden de inserción → orden de ingreso de la letra
		for char, freq in self.frequencies.items():
			node = HuffmanNode(char, freq)
			heapq.heappush(heap, (freq, counter, node))
			counter += 1

		# Construir el árbol
		while len(heap) > 1:
			freq1, order1, left = heapq.heappop(heap)
			freq2, order2, right = heapq.heappop(heap)

			merged = HuffmanNode(
				char=None,
				freq=freq1 + freq2,
				left=left,
				right=right,
			)

			heapq.heappush(heap, (freq1 + freq2, counter, merged))
			counter += 1

		self.root_node = heap[0][2] if heap else None

		# Generar códigos
		self.huffman_codes = {}
		if self.root_node:
			if self.root_node.char is not None:  # Solo un carácter
				self.huffman_codes[self.root_node.char] = "0"
			else:
				self._generate_codes(self.root_node, "")

		self._draw()


	def _generate_codes(self, node: HuffmanNode, code: str) -> None:
		"""Genera los códigos de Huffman recursivamente"""
		if node is None:
			return
		
		if node.char is not None:  # Nodo hoja
			self.huffman_codes[node.char] = code if code else "0"
			return
		
		self._generate_codes(node.left, code + "0")
		self._generate_codes(node.right, code + "1")

	def _on_add_char(self) -> None:
		"""Agrega una letra y reconstruye el árbol"""
		char_str = self.entry_char.get().strip()
		char = self._validate_char(char_str)
		if char is None:
			return
		
		# Guardar estado antes de agregar
		self._save_state()
		
		# Agregar la letra al texto y frecuencias
		self.current_text += char
		self.frequencies[char] = self.frequencies.get(char, 0) + 1
		
		# Reconstruir árbol automáticamente
		self._rebuild_tree()
		
		self.status.configure(text=f"Agregada '{char}'. Frecuencia: {self.frequencies[char]}")
		self.entry_char.delete(0, tk.END)

	def _on_remove_char(self) -> None:
		"""Elimina una letra y reconstruye el árbol"""
		char_str = self.entry_char.get().strip()
		char = self._validate_char(char_str)
		if char is None:
			return
		
		if char not in self.frequencies:
			messagebox.showwarning("Advertencia", f"La letra '{char}' no está en el texto")
			return
		
		# Guardar estado antes de eliminar
		self._save_state()
		
		# Eliminar una instancia de la letra
		self.frequencies[char] -= 1
		if self.frequencies[char] <= 0:
			del self.frequencies[char]
		
		# Eliminar del texto actual
		if char in self.current_text:
			idx = self.current_text.find(char)
			self.current_text = self.current_text[:idx] + self.current_text[idx+1:]
		
		# Reconstruir árbol automáticamente
		self._rebuild_tree()
		
		remaining = self.frequencies.get(char, 0)
		if remaining > 0:
			self.status.configure(text=f"Eliminada '{char}'. Frecuencia restante: {remaining}")
		else:
			self.status.configure(text=f"Eliminada '{char}' completamente del texto")
		self.entry_char.delete(0, tk.END)

	def _on_build_tree(self) -> None:
		"""Construye el árbol con el texto actual (si existe)"""
		if not self.frequencies:
			messagebox.showinfo("Información", "Agregue letras primero para construir el árbol")
			return

		# Guardar estado antes de construir
		self._save_state()

		# Preparar animación de construcción
		self._anim_steps = [("frequencies", dict(self.frequencies))]

		# Crear nodos hoja para animación con prioridad estable
		heap: List[Tuple[int, int, HuffmanNode]] = []
		counter = 0
		for char, freq in self.frequencies.items():
			node = HuffmanNode(char, freq)
			heapq.heappush(heap, (freq, counter, node))
			counter += 1

		# Simular construcción para animación
		while len(heap) > 1:
			freq1, order1, left = heapq.heappop(heap)
			freq2, order2, right = heapq.heappop(heap)

			merged = HuffmanNode(
				char=None,
				freq=freq1 + freq2,
				left=left,
				right=right,
			)

			heapq.heappush(heap, (freq1 + freq2, counter, merged))
			counter += 1

			# Guardamos los nodos reales para la animación
			self._anim_steps.append(("merge", (left, right, merged)))

		self.status.configure(text=f"Árbol construido con {len(self.frequencies)} caracteres únicos")
		self._prepare_animation()

	def _on_reset(self) -> None:
		self._save_state()  # Guardar estado antes de reiniciar
		self.root_node = None
		self.huffman_codes = {}
		self.frequencies = {}
		self.current_text = ""
		self._highlight_nodes = []
		self.status.configure(text="Estructura reiniciada")
		self._draw()

	def _on_undo(self, event=None) -> None:
		"""Deshace la última operación realizada"""
		if not self._history:
			self.status.configure(text="No hay operaciones para deshacer")
			messagebox.showinfo("Deshacer", "No hay operaciones para deshacer")
			return
		
		# Restaurar el último estado guardado
		last_state = self._history.pop()
		
		self.current_text = last_state['text']
		self.frequencies = last_state['frequencies']
		self.huffman_codes = last_state['huffman_codes']
		self.root_node = self._deserialize_node(last_state['root_node'])
		
		self.status.configure(text=f"Operación deshecha. Estados restantes: {len(self._history)}")
		self._draw()



	def _serialize(self) -> str:
		"""Serializa el estado actual para guardar"""
		result = f"text:{self.current_text}\n"
		
		for char, freq in self.frequencies.items():
			char_escaped = repr(char)
			result += f"freq:{char_escaped}:{freq}\n"
		
		for char, code in self.huffman_codes.items():
			char_escaped = repr(char)
			result += f"code:{char_escaped}:{code}\n"
		
		return result

	def _parse(self, content: str) -> bool:
		"""Parsea el contenido de un archivo guardado"""
		lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
		
		text = ""
		frequencies = {}
		codes = {}
		
		for line in lines:
			if line.startswith("text:"):
				text = line[5:]
			elif line.startswith("freq:"):
				parts = line[5:].split(":", 2)
				if len(parts) >= 2:
					char = eval(parts[0])  # Usar eval para caracteres escapados
					freq = int(parts[1])
					frequencies[char] = freq
			elif line.startswith("code:"):
				parts = line[5:].split(":", 2)
				if len(parts) >= 2:
					char = eval(parts[0])  # Usar eval para caracteres escapados
					code = parts[1]
					codes[char] = code
		
		self.current_text = text
		self.frequencies = frequencies
		self.huffman_codes = codes
		
		# Reconstruir el árbol automáticamente
		if frequencies:
			self._rebuild_tree()
		
		return True

	def _on_save(self) -> None:
		path = filedialog.asksaveasfilename(title="Guardar árbol de Huffman", defaultextension=".txt", filetypes=[("Texto", "*.txt")])
		if not path:
			return
		try:
			with open(path, "w", encoding="utf-8") as f:
				f.write(self._serialize())
			messagebox.showinfo("Éxito", "Árbol de Huffman guardado correctamente")
		except Exception as e:
			messagebox.showerror("Error", f"No se pudo guardar: {e}")

	def _on_save_and_close(self) -> None:
		path = filedialog.asksaveasfilename(title="Guardar árbol de Huffman", defaultextension=".txt", filetypes=[("Texto", "*.txt")])
		if not path:
			return
		try:
			with open(path, "w", encoding="utf-8") as f:
				f.write(self._serialize())
			messagebox.showinfo("Éxito", "Árbol de Huffman guardado correctamente")
			self.app.navigate("internas")
		except Exception as e:
			messagebox.showerror("Error", f"No se pudo guardar: {e}")

	def _on_load(self) -> None:
		# Guardar estado antes de cargar
		self._save_state()
		
		path = filedialog.askopenfilename(title="Cargar árbol de Huffman", filetypes=[("Texto", "*.txt")])
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
		
		success = self._parse(content)
		if not success:
			messagebox.showerror("Error", "Formato inválido")
			# Restaurar estado ya que no se cargó nada
			if self._history:
				self._history.pop()
			return
		
		self.status.configure(text="Árbol de Huffman cargado")
		self._draw()

	def _prepare_animation(self) -> None:
		self._anim_index = 0
		self._anim_running = False
		self._draw()
		self.status.configure(text=f"Animación lista: {len(self._anim_steps)} pasos")

	def _anim_step(self) -> None:
		if self._anim_index >= len(self._anim_steps):
			self._anim_running = False
			return
		
		step_type, data = self._anim_steps[self._anim_index]
		
		if step_type == "frequencies":
			self.status.configure(text="Calculando frecuencias...")
		elif step_type == "merge":
			left, right, merged = data
			self._highlight_nodes = [left, right, merged]
			self.status.configure(text=f"Fusionando nodos: {left.freq} + {right.freq} = {merged.freq}")
		
		self._draw()
		self._anim_index += 1
		
		if self._anim_running and self._anim_index < len(self._anim_steps):
			self.after(1000, self._anim_step)

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
		self._highlight_nodes = []
		self._draw()

	def _draw(self) -> None:
		self.canvas.delete("all")
		
		if not self.root_node:
			return
		
		width = self.canvas.winfo_width() or self.canvas.winfo_reqwidth()
		height = self.canvas.winfo_height() or self.canvas.winfo_reqheight()
		
		# Calcular posiciones de los nodos
		positions = {}
		self._calculate_positions(self.root_node, width // 2, 40, width // 4, positions)
		
		# Dibujar aristas
		self._draw_edges(self.root_node, positions)
		
		# Dibujar nodos
		self._draw_nodes(positions)

	def _calculate_positions(self, node: HuffmanNode, x: int, y: int, dx: int, positions: Dict[HuffmanNode, Tuple[int, int]]) -> None:
		"""Calcula las posiciones de todos los nodos del árbol"""
		if node is None:
			return
		
		positions[node] = (x, y)
		
		if node.left or node.right:
			child_y = y + 80
			child_dx = max(30, dx // 2)
			
			if node.left:
				self._calculate_positions(node.left, x - dx, child_y, child_dx, positions)
			if node.right:
				self._calculate_positions(node.right, x + dx, child_y, child_dx, positions)

	def _draw_edges(self, node: HuffmanNode, positions: Dict[HuffmanNode, Tuple[int, int]]) -> None:
		"""Dibuja las aristas del árbol"""
		if node is None or (node.left is None and node.right is None):
			return
		
		x, y = positions[node]
		
		if node.left:
			left_x, left_y = positions[node.left]
			color = "#ff6666" if node.left in self._highlight_nodes else "#808080"
			self.canvas.create_line(x, y, left_x, left_y, fill=color, width=2)
			# Etiqueta "0" en la arista izquierda
			mid_x, mid_y = (x + left_x) // 2, (y + left_y) // 2
			self.canvas.create_text(mid_x - 10, mid_y, text="0", fill="#000000", font=("MS Sans Serif", 9, "bold"))
			self._draw_edges(node.left, positions)
		
		if node.right:
			right_x, right_y = positions[node.right]
			color = "#ff6666" if node.right in self._highlight_nodes else "#808080"
			self.canvas.create_line(x, y, right_x, right_y, fill=color, width=2)
			# Etiqueta "1" en la arista derecha
			mid_x, mid_y = (x + right_x) // 2, (y + right_y) // 2
			self.canvas.create_text(mid_x + 10, mid_y, text="1", fill="#000000", font=("MS Sans Serif", 9, "bold"))
			self._draw_edges(node.right, positions)

	def _draw_nodes(self, positions: Dict[HuffmanNode, Tuple[int, int]]) -> None:
		"""Dibuja los nodos del árbol"""
		node_radius = 20
		
		for node, (x, y) in positions.items():
			# Color del nodo
			fill = "#4da3ff" if node in self._highlight_nodes else "#bdbdbd"
			outline = "#255eaa" if node in self._highlight_nodes else "#808080"
			
			# Dibujar círculo del nodo
			self.canvas.create_oval(
				x - node_radius, y - node_radius,
				x + node_radius, y + node_radius,
				fill=fill, outline=outline, width=2
			)
			
			# Texto del nodo
			if node.char is not None:  # Nodo hoja
				char_display = repr(node.char) if node.char in [' ', '\n', '\t'] else node.char
				text = f"{char_display}\n{node.freq}"
			else:  # Nodo interno
				text = str(node.freq)
			
			self.canvas.create_text(x, y, text=text, fill="#000000", font=("MS Sans Serif", 8, "bold"))