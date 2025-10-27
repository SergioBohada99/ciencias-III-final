import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Dict, List, Tuple, Any
from enum import Enum


class NodeType(Enum):
	LINK = "enlace"
	COLLISION = "colision"
	LEAF = "hoja"


class ResidNode:
	def __init__(self, node_type: NodeType = NodeType.LINK) -> None:
		self.node_type: NodeType = node_type
		self.symbol: Optional[str] = None
		self.value: Optional[int] = None
		self.bits: Optional[str] = None  # bits MSB->LSB (por ejemplo "10010")
		self.left: Optional['ResidNode'] = None
		self.right: Optional['ResidNode'] = None


class ResiduosTreeView(ttk.Frame):
	def __init__(self, parent: tk.Misc, app) -> None:
		super().__init__(parent)

		title = ttk.Label(self, text="Árbol por residuos (MSB→LSB)", style="Title.TLabel")
		title.pack(pady=(20, 5))

		panel = ttk.Frame(self, padding=6)
		panel.pack(fill=tk.BOTH, expand=True)

		ops = ttk.Frame(panel, style="Panel.TFrame", padding=10)
		ops.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))

		lbl = ttk.Label(ops, text="Letra (A-Z, sin Ñ):")
		lbl.grid(row=0, column=0, sticky="w")
		self.entry = ttk.Entry(ops, width=10)
		self.entry.grid(row=1, column=0, pady=(0, 10))

		btn_insert = ttk.Button(ops, text="Insertar", style="Retro.TButton", command=self._on_insert)
		btn_insert.grid(row=2, column=0, pady=4, sticky="ew")

		btn_delete = ttk.Button(ops, text="Eliminar", style="Retro.TButton", command=self._on_delete)
		btn_delete.grid(row=3, column=0, pady=4, sticky="ew")

		btn_search = ttk.Button(ops, text="Buscar", style="Retro.TButton", command=self._on_search)
		btn_search.grid(row=4, column=0, pady=4, sticky="ew")

		btn_reset = ttk.Button(ops, text="Reiniciar", command=self._on_reset)
		btn_reset.grid(row=5, column=0, pady=6, sticky="ew")

		anim_lbl = ttk.Label(ops, text="Controles de animación")
		anim_lbl.grid(row=6, column=0, sticky="w", pady=(8, 2))
		btn_play = ttk.Button(ops, text="▶ Reproducir", command=self._on_play)
		btn_play.grid(row=7, column=0, pady=2, sticky="ew")
		btn_pause = ttk.Button(ops, text="⏸ Pausa", command=self._on_pause)
		btn_pause.grid(row=8, column=0, pady=2, sticky="ew")
		btn_next = ttk.Button(ops, text="Paso", command=self._on_next)
		btn_next.grid(row=9, column=0, pady=2, sticky="ew")
		btn_reset_anim = ttk.Button(ops, text="Reiniciar animación", command=self._on_reset_anim)
		btn_reset_anim.grid(row=10, column=0, pady=2, sticky="ew")

		btn_undo = ttk.Button(ops, text="↶ Deshacer (Ctrl+Z)", command=self._on_undo)
		btn_undo.grid(row=11, column=0, pady=2, sticky="ew")

		self.status = ttk.Label(ops, text="Estado: listo")
		self.status.grid(row=12, column=0, pady=(10, 0), sticky="w")

		viz = ttk.Frame(panel, style="Panel.TFrame", padding=8)
		viz.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

		self.canvas = tk.Canvas(viz, background="#ffffff", height=460)
		self.canvas.pack(fill=tk.BOTH, expand=True)
		self.canvas.bind("<Configure>", lambda e: self._draw())

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

		# Estructura
		self.root: ResidNode = ResidNode(NodeType.LINK)
		self.symbols: Dict[str, int] = {}

		# Animación
		self._anim_steps: List[Dict[str, Any]] = []
		self._anim_index: int = 0
		self._anim_running: bool = False
		self._highlight_nodes: List[ResidNode] = []

		# Undo
		self._history: List[Dict[str, Any]] = []
		self._max_history = 20
		self.bind_all("<Control-z>", self._on_undo)

		self._draw()
		

	def _save_state(self) -> None:
		self._history.append({
			"symbols": dict(self.symbols),
			"tree": self._serialize_tree(self.root),
		})
		if len(self._history) > self._max_history:
			self._history.pop(0)

	def _serialize_tree(self, node: Optional[ResidNode]) -> Optional[Dict[str, Any]]:
		if node is None:
			return None
		return {
			"type": node.node_type.value,
			"symbol": node.symbol,
			"value": node.value,
			"bits": node.bits,
			"left": self._serialize_tree(node.left),
			"right": self._serialize_tree(node.right),
		}

	def _deserialize_tree(self, data: Optional[Dict[str, Any]]) -> Optional[ResidNode]:
		if data is None:
			return None
		node = ResidNode(NodeType(data["type"]))
		node.symbol = data["symbol"]
		node.value = data["value"]
		node.bits = data["bits"]
		node.left = self._deserialize_tree(data.get("left"))
		node.right = self._deserialize_tree(data.get("right"))
		return node

	def _char_to_value(self, ch: str) -> int:
		ch = ch.upper()
		if not ('A' <= ch <= 'Z') or ch == 'Ñ':
			raise ValueError("Letra inválida")
		return ord(ch) - ord('A') + 1  # ✅ A=1 ... Z=26

	def _value_to_bits_msb(self, value: int) -> str:
		return format(value, '05b')  # ✅ SIEMPRE 5 bits, MSB primero

	def _validate_char(self, s: str) -> Optional[str]:
		if not s or len(s) != 1 or not s.isalpha() or s.upper() == 'Ñ':
			messagebox.showerror("Error", "Ingrese una letra A-Z (sin Ñ)")
			return None
		return s.upper()

	def _insert_symbol(self, symbol: str, animate: bool) -> None:
		if symbol in self.symbols:
			messagebox.showwarning("Advertencia", f"'{symbol}' ya existe")
			return
		value = self._char_to_value(symbol)
		bits = self._value_to_bits_msb(value)
		self.symbols[symbol] = value
		if animate:
			self._anim_steps = [{
				"type": "start", "message": f"Insertando {symbol} = {value} = {bits}₂"
			}]
		self._insert_recursive(self.root, symbol, value, bits, depth=0, animate=animate)
		if animate:
			self._anim_steps.append({"type": "done", "message": f"Inserción de {symbol} completada"})

	def _insert_recursive(self, node: ResidNode, symbol: str, value: int, bits: str, depth: int, animate: bool) -> None:
		"""
		Insercion que:
		- nunca convierte la raiz en hoja (root debe ser LINK)
		- rechaza duplicados exactos (sin animacion)
		- avanza por el prefijo comun y bifurca en el primer bit distinto
		- mantiene pasos de animacion en puntos relevantes
		"""
		# Aseguramos que, si estamos en depth 0, el nodo sea LINK (raiz siempre LINK)
		if depth == 0 and node.node_type != NodeType.LINK:
			node.node_type = NodeType.LINK
			node.symbol = None
			node.value = None
			node.bits = None

		# --- Caso: Nodo hoja (posible colision o duplicado) ---
		if node.node_type == NodeType.LEAF:
			# Duplicado exacto -> rechazar (sin animacion)
			if node.bits == bits:
				messagebox.showwarning("Duplicado", f"{symbol} ya existe, no se inserta")
				return

			# Colision: encontramos el primer bit distinto (AHORA desde 'depth')
			existing_symbol = node.symbol or ""
			existing_value = node.value or 0
			existing_bits = node.bits or ""

			if animate:
				self._anim_steps.append({"type": "collision", "message": f"Colisión: {existing_symbol} vs {symbol} — buscando bit distinto"})

			max_len = max(len(existing_bits), len(bits))

			# <<< CORRECCIÓN: empezar la búsqueda en 'depth', no en 0 >>>
			diff_index = depth
			while diff_index < max_len:
				b_exist = existing_bits[diff_index] if diff_index < len(existing_bits) else '0'
				b_new = bits[diff_index] if diff_index < len(bits) else '0'
				if b_exist != b_new:
					break
				diff_index += 1

			# Convertir este nodo en LINK (vaciar datos)
			node.node_type = NodeType.LINK
			node.symbol = None
			node.value = None
			node.bits = None

			# Si no encontramos diferencia (muy raro) -> asignacion deterministica
			if diff_index >= max_len:
				if animate:
					self._anim_steps.append({"type": "split", "message": "Bits iguales hasta el final: asignando determinísticamente izq/der"})
				# existing -> left, new -> right
				node.left = ResidNode(NodeType.LEAF)
				node.left.symbol = existing_symbol
				node.left.value = existing_value
				node.left.bits = existing_bits

				node.right = ResidNode(NodeType.LEAF)
				node.right.symbol = symbol
				node.right.value = value
				node.right.bits = bits
				return

			# Construir la ruta de prefijo común desde 'node' hasta diff_index-1
			cur = node
			for i in range(depth, diff_index):
				# bit comun (si uno se acaba usamos el que exista, por convención '0')
				b_common = (existing_bits[i] if i < len(existing_bits) else ('0' if i >= len(bits) else bits[i]))
				# crear enlace si hace falta
				if b_common == '0':
					if cur.left is None:
						cur.left = ResidNode(NodeType.LINK)
					cur = cur.left
				else:
					if cur.right is None:
						cur.right = ResidNode(NodeType.LINK)
					cur = cur.right
				if animate:
					# mostramos el bit absoluto (i+1)
					self._anim_steps.append({"type": "traverse", "message": f"Prefijo, bit {i+1} = {b_common} → {'izq' if b_common == '0' else 'der'}"})

			# En diff_index los bits difieren (usar '0' por defecto si alguno se acaba)
			b_exist = existing_bits[diff_index] if diff_index < len(existing_bits) else '0'
			b_new = bits[diff_index] if diff_index < len(bits) else '0'

			# Crear hojas en los lados correspondientes
			if b_exist == '0':
				cur.left = ResidNode(NodeType.LEAF)
				cur.left.symbol = existing_symbol
				cur.left.value = existing_value
				cur.left.bits = existing_bits
			else:
				cur.right = ResidNode(NodeType.LEAF)
				cur.right.symbol = existing_symbol
				cur.right.value = existing_value
				cur.right.bits = existing_bits

			if b_new == '0':
				# si hay colision en la misma posicion (raro), sobreescribimos/garantizamos hoja
				cur.left = cur.left or ResidNode(NodeType.LEAF)
				cur.left.node_type = NodeType.LEAF
				cur.left.symbol = symbol
				cur.left.value = value
				cur.left.bits = bits
			else:
				cur.right = cur.right or ResidNode(NodeType.LEAF)
				cur.right.node_type = NodeType.LEAF
				cur.right.symbol = symbol
				cur.right.value = value
				cur.right.bits = bits

			if animate:
				self._anim_steps.append({"type": "split", "message": f"Separando en bit {diff_index + 1}: {b_exist} vs {b_new}"})
			return

		# --- Caso: Nodo enlace (LINK) ---
		# Si ya superamos la longitud de bits (poco probable si usas 5 bits fijos),
		# colocamos la hoja de forma determinista en la izquierda si está libre, si no en la derecha.
		if depth >= len(bits):
			if node.left is None:
				node.left = ResidNode(NodeType.LEAF)
				node.left.symbol = symbol
				node.left.value = value
				node.left.bits = bits
				if animate:
					self._anim_steps.append({"type": "leaf", "message": f"Insertar {symbol} en left (depth final)"})
				return
			elif node.right is None:
				node.right = ResidNode(NodeType.LEAF)
				node.right.symbol = symbol
				node.right.value = value
				node.right.bits = bits
				if animate:
					self._anim_steps.append({"type": "leaf", "message": f"Insertar {symbol} en right (depth final)"})
				return
			else:
				# Ambos ocupados: continuar por la izquierda de forma determinista
				if node.left is not None:
					self._insert_recursive(node.left, symbol, value, bits, depth + 1, animate)
				return

		# Normal: tomamos el bit actual y descendemos/insertamos
		bit = bits[depth]
		if animate:
			self._anim_steps.append({"type": "traverse", "message": f"Bit {depth + 1} = {bit} → {'derecha' if bit == '1' else 'izquierda'}"})

		if bit == '0':
			if node.left is None:
				# insertar hoja directamente en esa posicion
				node.left = ResidNode(NodeType.LEAF)
				node.left.symbol = symbol
				node.left.value = value
				node.left.bits = bits
				if animate:
					self._anim_steps.append({"type": "leaf", "message": f"Insertar {symbol} en izq (bit {depth+1})"})
				return
			else:
				self._insert_recursive(node.left, symbol, value, bits, depth + 1, animate)
		else:
			if node.right is None:
				node.right = ResidNode(NodeType.LEAF)
				node.right.symbol = symbol
				node.right.value = value
				node.right.bits = bits
				if animate:
					self._anim_steps.append({"type": "leaf", "message": f"Insertar {symbol} en der (bit {depth+1})"})
				return
			else:
				self._insert_recursive(node.right, symbol, value, bits, depth + 1, animate)

	def _promote_to_collision(self, node: ResidNode, animate: bool) -> None:
		if animate:
			self._anim_steps.append({"type": "collision", "message": "¡Colisión! Promover a nodo de colisión"})
		# Convertir hoja/enlace a colisión conservando temporalmente datos para reinsertar
		# (El que llama se encarga de reinsertar el/los símbolos)
		node.node_type = NodeType.COLLISION
		# Eliminar datos de hoja, se reinsertan
		node.symbol = None
		node.value = None
		node.bits = None

	def _reinsert_from(self, node: ResidNode, symbol: str, value: int, bits: str, depth: int, animate: bool) -> None:
		# Reinsertar a partir del mismo depth (siguiente decisión por el bit en depth)
		if depth >= len(bits):
			# Si ya no hay más bits, caerá aquí: ocupar como hoja en subrama libre
			# Buscar lado libre de forma determinista (izq primero)
			if node.left is None:
				node.left = ResidNode(NodeType.LEAF)
				node.left.symbol = symbol
				node.left.value = value
				node.left.bits = bits
			elif node.right is None:
				node.right = ResidNode(NodeType.LEAF)
				node.right.symbol = symbol
				node.right.value = value
				node.right.bits = bits
			else:
				# Si ambas ocupadas, continuar descendiendo por la izquierda
				self._reinsert_from(node.left, symbol, value, bits, depth, animate)
			return
		bit = bits[depth]
		if bit == '0':
			if node.left is None:
				node.left = ResidNode(NodeType.LINK)
			self._insert_recursive(node.left, symbol, value, bits, depth + 1, animate)
		else:
			if node.right is None:
				node.right = ResidNode(NodeType.LINK)
			self._insert_recursive(node.right, symbol, value, bits, depth + 1, animate)

	def _search_symbol(self, symbol: str, animate: bool) -> Optional[ResidNode]:
		if symbol not in self.symbols:
			return None
		value = self.symbols[symbol]
		bits = self._value_to_bits_msb(value)
		if animate:
			self._anim_steps = [{"type": "start", "message": f"Buscando {symbol} = {value} = {bits}₂"}]
		return self._search_recursive(self.root, symbol, bits, 0, animate)

	def _search_recursive(self, node: Optional[ResidNode], symbol: str, bits: str, depth: int, animate: bool) -> Optional[ResidNode]:
		if node is None:
			return None
		if node.node_type == NodeType.LEAF:
			return node if node.symbol == symbol else None
		if depth >= len(bits):
			return None
		bit = bits[depth]
		if animate:
			self._anim_steps.append({"type": "traverse", "message": f"Bit {depth + 1} = {bit} → {'der' if bit == '1' else 'izq'}"})
		if bit == '0':
			return self._search_recursive(node.left, symbol, bits, depth + 1, animate)
		else:
			return self._search_recursive(node.right, symbol, bits, depth + 1, animate)

	def _remove_symbol(self, symbol: str) -> bool:
		if symbol not in self.symbols:
			return False
		# Reconstruir sin el símbolo
		remaining = [s for s in self.symbols.keys() if s != symbol]
		self.root = ResidNode(NodeType.LINK)
		self.symbols = {}
		for s in remaining:
			self._insert_symbol(s, animate=False)
		return True

	def _on_insert(self) -> None:
		ch = self._validate_char(self.entry.get().strip())
		if not ch:
			return
		self._save_state()
		self._insert_symbol(ch, animate=True)
		self._prepare_animation()
		if self._anim_steps:
			self._anim_index = 0
			self._anim_running = True
			self._anim_step()
		self.entry.delete(0, tk.END)
		print(self._serialize_tree(self.root))
		self._draw()

	def _on_delete(self) -> None:
		ch = self._validate_char(self.entry.get().strip())
		if not ch:
			return
		self._save_state()
		if not self._remove_symbol(ch):
			messagebox.showinfo("Eliminar", "Letra no encontrada")
		else:
			self.status.configure(text=f"Eliminada '{ch}'")
		self.entry.delete(0, tk.END)
		self._draw()

	def _on_search(self) -> None:
		ch = self._validate_char(self.entry.get().strip())
		if not ch:
			return
		res = self._search_symbol(ch, animate=True)
		self._prepare_animation()
		if self._anim_steps:
			self._anim_index = 0
			self._anim_running = True
			self._anim_step()
		if res is None:
			# El message de no encontrado se muestra al final de la animación
			pass
		self.entry.delete(0, tk.END)

	def _on_reset(self) -> None:
		self._save_state()
		self.root = ResidNode(NodeType.LINK)
		self.symbols = {}
		self._anim_steps = []
		self._anim_index = 0
		self._anim_running = False
		self.status.configure(text="Estructura reiniciada")
		self._draw()

	def _on_undo(self, event=None) -> None:
		if not self._history:
			messagebox.showinfo("Deshacer", "No hay operaciones para deshacer")
			return
		state = self._history.pop()
		self.symbols = state["symbols"]
		self.root = self._deserialize_tree(state["tree"]) or ResidNode(NodeType.LINK)
		self.status.configure(text=f"Operación deshecha. Estados: {len(self._history)}")
		self._draw()

	def _prepare_animation(self) -> None:
		self._anim_index = 0
		self._anim_running = False
		self._highlight_nodes = []
		self.status.configure(text=f"Animación lista: {len(self._anim_steps)} pasos")

	def _anim_step(self) -> None:
		if self._anim_index >= len(self._anim_steps):
			self._anim_running = False
			self.status.configure(text="Animación terminada")
			if self._anim_steps and self._anim_steps[-1].get("type") == "not_found":
				messagebox.showinfo("Búsqueda", "Letra no encontrada")
			return
		step = self._anim_steps[self._anim_index]
		self.status.configure(text=step.get("message", ""))
		self._draw()
		self._anim_index += 1
		if self._anim_running and self._anim_index < len(self._anim_steps):
			self.after(1200, self._anim_step)

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

	def _serialize(self) -> str:
		out = []
		for s, v in self.symbols.items():
			out.append(f"symbol:{s}:{v}")
		return "\n".join(out) + ("\n" if out else "")

	def _parse(self, content: str) -> bool:
		lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
		syms: Dict[str, int] = {}
		for ln in lines:
			if ln.startswith("symbol:"):
				parts = ln[7:].split(":", 1)
				if len(parts) == 2 and parts[0] and parts[1].isdigit():
					syms[parts[0]] = int(parts[1])
		self.root = ResidNode(NodeType.LINK)
		self.symbols = {}
		for s in syms.keys():
			self._insert_symbol(s, animate=False)
		return True

	def _on_save(self) -> None:
		path = filedialog.asksaveasfilename(title="Guardar árbol por residuos", defaultextension=".txt", filetypes=[("Texto", "*.txt")])
		if not path:
			return
		try:
			with open(path, "w", encoding="utf-8") as f:
				f.write(self._serialize())
			messagebox.showinfo("Éxito", "Árbol guardado correctamente")
		except Exception as e:
			messagebox.showerror("Error", f"No se pudo guardar: {e}")

	def _on_save_and_close(self) -> None:
		path = filedialog.asksaveasfilename(title="Guardar árbol por residuos", defaultextension=".txt", filetypes=[("Texto", "*.txt")])
		if not path:
			return
		try:
			with open(path, "w", encoding="utf-8") as f:
				f.write(self._serialize())
			messagebox.showinfo("Éxito", "Árbol guardado correctamente")
			self.app.navigate("internas")
		except Exception as e:
			messagebox.showerror("Error", f"No se pudo guardar: {e}")

	def _on_load(self) -> None:
		self._save_state()
		path = filedialog.askopenfilename(title="Cargar árbol por residuos", filetypes=[("Texto", "*.txt")])
		if not path:
			if self._history:
				self._history.pop()
			return
		try:
			with open(path, "r", encoding="utf-8") as f:
				content = f.read()
		except Exception as e:
			messagebox.showerror("Error", f"No se pudo leer: {e}")
			if self._history:
				self._history.pop()
			return
		if not self._parse(content):
			messagebox.showerror("Error", "Formato inválido")
			if self._history:
				self._history.pop()
			return
		self.status.configure(text="Árbol cargado")
		self._draw()

	def _draw(self) -> None:
		self.canvas.delete("all")
		self.canvas.update_idletasks()
		width = max(self.canvas.winfo_width(), 600)
		height = max(self.canvas.winfo_height(), 420)
		# Árbol vacío
		if self.root.node_type == NodeType.LINK and self.root.left is None and self.root.right is None and self.root.symbol is None:
			self.canvas.create_text(width // 2, height // 2, text="Inserte letras para construir el árbol", fill="#666666", font=("MS Sans Serif", 12))
			return
		# Calcular posiciones
		positions: Dict[ResidNode, Tuple[int, int]] = {}
		self._layout(self.root, width // 2, 40, width // 4, positions)
		# Dibujar aristas
		self._draw_edges(self.root, positions)
		# Dibujar nodos
		self._draw_nodes(positions)

	def _layout(self, node: Optional[ResidNode], x: int, y: int, dx: int, positions: Dict[ResidNode, Tuple[int, int]]) -> None:
		if node is None:
			return
		positions[node] = (x, y)
		if node.left or node.right:
			child_y = y + 80
			child_dx = max(30, dx // 2)
			self._layout(node.left, x - dx, child_y, child_dx, positions)
			self._layout(node.right, x + dx, child_y, child_dx, positions)

	def _draw_edges(self, node: Optional[ResidNode], positions: Dict[ResidNode, Tuple[int, int]]) -> None:
		if node is None:
			return
		if node.left:
			x, y = positions[node]
			xl, yl = positions[node.left]
			color = "#808080"
			self.canvas.create_line(x, y, xl, yl, fill=color, width=2)
			mx, my = (x + xl) // 2, (y + yl) // 2
			self.canvas.create_text(mx - 10, my, text="0", fill="#000000", font=("MS Sans Serif", 9, "bold"))
			self._draw_edges(node.left, positions)
		if node.right:
			x, y = positions[node]
			xr, yr = positions[node.right]
			color = "#808080"
			self.canvas.create_line(x, y, xr, yr, fill=color, width=2)
			mx, my = (x + xr) // 2, (y + yr) // 2
			self.canvas.create_text(mx + 10, my, text="1", fill="#000000", font=("MS Sans Serif", 9, "bold"))
			self._draw_edges(node.right, positions)

	def _draw_nodes(self, positions: Dict[ResidNode, Tuple[int, int]]) -> None:
		r = 18
		for node, (x, y) in positions.items():
			if node.node_type == NodeType.LINK:
				fill = "#e0e0e0"
				outline = "#808080"
				text = "ENL"
			elif node.node_type == NodeType.COLLISION:
				fill = "#ffcccc"
				outline = "#ff6666"
				text = "COL"
			else:
				fill = "#ccffcc"
				outline = "#66aa66"
				text = f"{node.symbol}\n{node.value}"
			self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=fill, outline=outline, width=2)
			self.canvas.create_text(x, y, text=text, fill="#000000", font=("MS Sans Serif", 9, "bold"))

	def _split_node(self,
					node: ResidNode,
					existing_symbol: str, existing_value: int, existing_bits: str,
					new_symbol: str, new_value: int, new_bits: str,
					depth: int, animate: bool) -> None:
		"""
		Construye, a partir del `node` (que debe ser convertido a LINK antes),
		la bifurcacion necesaria encontrando el primer bit distinto desde `depth`.
		Inserta las dos hojas en los lados correspondientes.
		"""

		# Encuentra la primer posicion donde difieren (o donde uno se acaba)
		max_len = max(len(existing_bits), len(new_bits))
		split_pos = depth
		while split_pos < max_len:
			# Obtener bit en posicion i para cada cadena; si no existe, usamos None
			b_exist = existing_bits[split_pos] if split_pos < len(existing_bits) else None
			b_new = new_bits[split_pos] if split_pos < len(new_bits) else None

			# Si son distintos (incluyendo el caso en que uno es None) => punto de bifurcacion
			if b_exist != b_new:
				break
			split_pos += 1

		# Si nunca difieren (caso raro: mismos bits), para evitar loop colocamos existing a la izquierda y new a la derecha
		if split_pos >= max_len:
			# crear una estructura simple con dos hojas deterministicas
			node.left = ResidNode(NodeType.LEAF)
			node.left.symbol = existing_symbol
			node.left.value = existing_value
			node.left.bits = existing_bits

			node.right = ResidNode(NodeType.LEAF)
			node.right.symbol = new_symbol
			node.right.value = new_value
			node.right.bits = new_bits
			if animate:
				self._anim_steps.append({"type": "collision", "message": "Colisión sin diferencia de bits, asignando deterministicamente izq/der"})
			return

		# Ahora en split_pos los bits son diferentes (o uno es None)
		# Construimos la ruta desde 'depth' hasta 'split_pos' creando nodos LINK intermedios si hace falta
		cur = node
		for i in range(depth, split_pos):
			# crear nodo intermedio (LINK) en la direccion correspondiente al bit común
			# los bits en este rango son iguales para ambos, podemos tomar uno de ellos (preferimos existing si existe)
			b = existing_bits[i] if i < len(existing_bits) else (new_bits[i] if i < len(new_bits) else '0')
			if b == '0':
				if cur.left is None:
					cur.left = ResidNode(NodeType.LINK)
				cur = cur.left
			else:
				if cur.right is None:
					cur.right = ResidNode(NodeType.LINK)
				cur = cur.right

		# En split_pos los bits determinan lado para cada simbolo
		b_exist = existing_bits[split_pos] if split_pos < len(existing_bits) else '0'
		b_new = new_bits[split_pos] if split_pos < len(new_bits) else '0'

		# Crear hojas en los lados respectivos; si ya hay nodo, sobreescribimos solo si es None
		if b_exist == '0':
			if cur.left is None:
				cur.left = ResidNode(NodeType.LEAF)
			cur.left.node_type = NodeType.LEAF
			cur.left.symbol = existing_symbol
			cur.left.value = existing_value
			cur.left.bits = existing_bits
		else:
			if cur.right is None:
				cur.right = ResidNode(NodeType.LEAF)
			cur.right.node_type = NodeType.LEAF
			cur.right.symbol = existing_symbol
			cur.right.value = existing_value
			cur.right.bits = existing_bits

		if b_new == '0':
			if cur.left is None:
				cur.left = ResidNode(NodeType.LEAF)
			else:
				# Si ya ocupa la izquierda, crea un nivel extra deterministico hacia la izquierda
				if cur.left.node_type != NodeType.LEAF:
					pass
			cur.left.node_type = NodeType.LEAF
			cur.left.symbol = new_symbol
			cur.left.value = new_value
			cur.left.bits = new_bits
		else:
			if cur.right is None:
				cur.right = ResidNode(NodeType.LEAF)
			cur.right.node_type = NodeType.LEAF
			cur.right.symbol = new_symbol
			cur.right.value = new_value
			cur.right.bits = new_bits

		if animate:
			self._anim_steps.append({"type": "split", "message": f"Separando en bit {split_pos+1}: {b_exist} vs {b_new}"})
