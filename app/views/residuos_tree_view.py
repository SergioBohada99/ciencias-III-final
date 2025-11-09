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
		
		#Edges
		self._edge_hint: Optional[Tuple[ResidNode, ResidNode]] = None

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
		Inserta (symbol, value, bits MSB→LSB) en el árbol:
		- La raíz siempre permanece como LINK.
		- Rechaza duplicados exactos.
		- En colisión, busca el primer bit distinto a partir de `depth`,
		crea el prefijo común y bifurca en ese punto.
		- Emite pasos de animación con la arista exacta (parent -> child) en cada avance.
		"""
		# Asegurar que la raíz (depth==0) sea LINK
		if depth == 0 and node.node_type != NodeType.LINK:
			node.node_type = NodeType.LINK
			node.symbol = None
			node.value = None
			node.bits = None

		# ========== CASO: NODO HOJA ==========
		if node.node_type == NodeType.LEAF:
			# Duplicado exacto -> no insertar
			if node.bits == bits:
				messagebox.showwarning("Duplicado", f"{symbol} ya existe, no se inserta")
				return

			existing_symbol = node.symbol or ""
			existing_value = node.value or 0
			existing_bits = node.bits or ""

			if animate:
				self._anim_steps.append({"type": "collision", "message": f"Colisión: {existing_symbol} vs {symbol} — buscando primer bit distinto"})

			# Buscar primer índice distinto desde 'depth'
			max_len = max(len(existing_bits), len(bits))
			diff_index = depth
			while diff_index < max_len:
				b_exist = existing_bits[diff_index] if diff_index < len(existing_bits) else '0'
				b_new   = bits[diff_index]           if diff_index < len(bits)           else '0'
				if b_exist != b_new:
					break
				diff_index += 1

			# Convertir este nodo en LINK (se reinsertan como hojas abajo)
			node.node_type = NodeType.LINK
			node.symbol = None
			node.value = None
			node.bits = None

			# Caso extremo: no se encontró diferencia (misma secuencia efectiva de bits)
			if diff_index >= max_len:
				# Determinista: existing->left, new->right
				node.left = ResidNode(NodeType.LEAF)
				node.left.symbol = existing_symbol
				node.left.value = existing_value
				node.left.bits = existing_bits

				node.right = ResidNode(NodeType.LEAF)
				node.right.symbol = symbol
				node.right.value = value
				node.right.bits = bits

				if animate:
					self._anim_steps.append({"type": "split", "message": "Bits iguales hasta el final: asignando izq/der determinísticamente"})
					self._add_edge_step(node, node.left,  f"Colocar {existing_symbol} a la IZQ", "leaf")
					self._add_edge_step(node, node.right, f"Colocar {symbol} a la DER", "leaf")
				return

			# Construir prefijo común desde 'depth' hasta 'diff_index - 1'
			cur = node
			for i in range(depth, diff_index):
				# Bit común (si alguno no alcanza, usamos el que exista; por convención '0')
				b_common = existing_bits[i] if i < len(existing_bits) else (bits[i] if i < len(bits) else '0')

				# Crear/usar el enlace correspondiente y registrar paso de arista
				if b_common == '0':
					if cur.left is None:
						cur.left = ResidNode(NodeType.LINK)
					if animate:
						self._add_edge_step(cur, cur.left, f"Prefijo, bit {i+1} = 0 → IZQ", "traverse")
					cur = cur.left
				else:
					if cur.right is None:
						cur.right = ResidNode(NodeType.LINK)
					if animate:
						self._add_edge_step(cur, cur.right, f"Prefijo, bit {i+1} = 1 → DER", "traverse")
					cur = cur.right

			# En diff_index hay diferencia (o uno terminó)
			b_exist = existing_bits[diff_index] if diff_index < len(existing_bits) else '0'
			b_new   = bits[diff_index]           if diff_index < len(bits)           else '0'

			# Colocar existing
			if b_exist == '0':
				cur.left = ResidNode(NodeType.LEAF)
				cur.left.symbol = existing_symbol
				cur.left.value = existing_value
				cur.left.bits = existing_bits
				if animate:
					self._add_edge_step(cur, cur.left, f"Separación en bit {diff_index+1}: existing → IZQ (0)", "leaf")
			else:
				cur.right = ResidNode(NodeType.LEAF)
				cur.right.symbol = existing_symbol
				cur.right.value = existing_value
				cur.right.bits = existing_bits
				if animate:
					self._add_edge_step(cur, cur.right, f"Separación en bit {diff_index+1}: existing → DER (1)", "leaf")

			# Colocar new
			if b_new == '0':
				# Si coincide con existing y ya ocupó, garantizamos hoja (sobrescribe seguro porque acabamos de crear el otro lado)
				cur.left = cur.left or ResidNode(NodeType.LEAF)
				cur.left.node_type = NodeType.LEAF
				cur.left.symbol = symbol
				cur.left.value = value
				cur.left.bits = bits
				if animate:
					self._add_edge_step(cur, cur.left, f"Separación en bit {diff_index+1}: {symbol} → IZQ (0)", "leaf")
			else:
				cur.right = cur.right or ResidNode(NodeType.LEAF)
				cur.right.node_type = NodeType.LEAF
				cur.right.symbol = symbol
				cur.right.value = value
				cur.right.bits = bits
				if animate:
					self._add_edge_step(cur, cur.right, f"Separación en bit {diff_index+1}: {symbol} → DER (1)", "leaf")
			return

		# ========== CASO: NODO ENLACE (LINK) ==========
		# Si ya no quedan bits (muy raro con 5 bits fijos), ubicamos determinísticamente
		if depth >= len(bits):
			if node.left is None:
				node.left = ResidNode(NodeType.LEAF)
				node.left.symbol = symbol
				node.left.value = value
				node.left.bits = bits
				if animate:
					self._add_edge_step(node, node.left, f"Sin más bits: colocar {symbol} a la IZQ", "leaf")
				return
			elif node.right is None:
				node.right = ResidNode(NodeType.LEAF)
				node.right.symbol = symbol
				node.right.value = value
				node.right.bits = bits
				if animate:
					self._add_edge_step(node, node.right, f"Sin más bits: colocar {symbol} a la DER", "leaf")
				return
			else:
				# Ambos ocupados: bajar por la izquierda de forma determinista
				if animate and node.left is not None:
					self._add_edge_step(node, node.left, "Descender determinísticamente por la IZQ", "traverse")
				if node.left is not None:
					self._insert_recursive(node.left, symbol, value, bits, depth, animate)
				return

		# Bit actual y descenso normal
		bit = bits[depth]
		if bit == '0':
			if node.left is None:
				node.left = ResidNode(NodeType.LEAF)
				node.left.symbol = symbol
				node.left.value = value
				node.left.bits = bits
				if animate:
					self._add_edge_step(node, node.left, f"Bit {depth+1} = 0 → insertar {symbol} en IZQ", "leaf")
				return
			else:
				if animate:
					self._add_edge_step(node, node.left, f"Bit {depth+1} = 0 → IZQ", "traverse")
				self._insert_recursive(node.left, symbol, value, bits, depth + 1, animate)
		else:
			if node.right is None:
				node.right = ResidNode(NodeType.LEAF)
				node.right.symbol = symbol
				node.right.value = value
				node.right.bits = bits
				if animate:
					self._add_edge_step(node, node.right, f"Bit {depth+1} = 1 → insertar {symbol} en DER", "leaf")
				return
			else:
				if animate:
					self._add_edge_step(node, node.right, f"Bit {depth+1} = 1 → DER", "traverse")
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
			if animate:
				self._anim_steps.append({"type": "not_found", "message": f"No hay nodo en profundidad {depth}"})
			return None

		if node.node_type == NodeType.LEAF:
			if node.symbol == symbol:
				if animate:
					self._anim_steps.append({"type": "found", "message": f"Encontrado '{symbol}' en hoja"})
				return node
			else:
				if animate:
					self._anim_steps.append({"type": "not_found", "message": f"Hoja distinta ({node.symbol}), no coincide"})
				return None

		if depth >= len(bits):
			if animate:
				self._anim_steps.append({"type": "not_found", "message": "Se agotaron los bits sin hallar la letra"})
			return None

		bit = bits[depth]
		# Decidir rama y empujar paso de arista si existe
		if bit == '0':
			if node.left is not None and animate:
				self._add_edge_step(node, node.left, f"Bit {depth + 1} = 0 → izq", "traverse")
			return self._search_recursive(node.left, symbol, bits, depth + 1, animate)
		else:
			if node.right is not None and animate:
				self._add_edge_step(node, node.right, f"Bit {depth + 1} = 1 → der", "traverse")
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

	def _delete_symbol(self, symbol: str, animate: bool) -> bool:
		"""
		Elimina la hoja que contiene `symbol` sin reconfigurar el árbol.
		Genera pasos de animación con aristas reales (parent->child).
		Devuelve True si se eliminó, False si no se encontró.
		"""
		# Si no existe en el índice, animamos 'no encontrado'
		if symbol not in self.symbols:
			if animate:
				self._anim_steps = [
					{"type": "start", "message": f"Eliminar {symbol}: no existe en el índice"},
					{"type": "not_found", "message": "Letra no encontrada"},
				]
			return False

		value = self.symbols[symbol]
		bits = self._value_to_bits_msb(value)

		if animate:
			self._anim_steps = [{"type": "start", "message": f"Eliminando {symbol} = {value} = {bits}₂"}]

		# Buscar y eliminar exactamente la hoja
		deleted = self._delete_recursive(self.root, parent=None, side=None,
										symbol=symbol, bits=bits, depth=0, animate=animate)

		if deleted:
			# Actualiza índice de símbolos
			try:
				del self.symbols[symbol]
			except KeyError:
				pass
			if animate:
				self._anim_steps.append({"type": "deleted", "message": f"Eliminada '{symbol}'"})
			return True
		else:
			if animate:
				self._anim_steps.append({"type": "not_found", "message": "Letra no encontrada"})
			return False
		
	def _delete_recursive(self,
						node: Optional[ResidNode],
						parent: Optional[ResidNode],
						side: Optional[str],  # 'left' | 'right' | None (para la raíz)
						symbol: str,
						bits: str,
						depth: int,
						animate: bool) -> bool:
		"""
		Recorre siguiendo `bits` y elimina la hoja con `symbol` cuando la encuentra.
		No reconfigura/comprime el árbol: solo quita el puntero a la hoja.
		"""
		# No hay nodo en este punto del camino
		if node is None:
			return False

		# Caso hoja: compara símbolo
		if node.node_type == NodeType.LEAF:
			if node.symbol == symbol:
				# Desenganchar del padre (o resetear raíz si fuera el único nodo)
				if parent is None:
					# Caso raro: raíz hoja; se deja la raíz como LINK vacío
					self.root = ResidNode(NodeType.LINK)
				else:
					if side == 'left':
						parent.left = None
					elif side == 'right':
						parent.right = None
				return True
			return False

		# Si es LINK y se agotaron los bits (muy raro con 5 bits fijos), no hay hoja aquí
		if depth >= len(bits):
			return False

		# Decidir rama por el bit actual y animar la arista si existe
		bit = bits[depth]
		if bit == '0':
			if node.left is not None and animate:
				self._add_edge_step(node, node.left, f"Bit {depth + 1} = 0 → izq", "traverse")
			return self._delete_recursive(node.left, node, 'left', symbol, bits, depth + 1, animate)
		else:
			if node.right is not None and animate:
				self._add_edge_step(node, node.right, f"Bit {depth + 1} = 1 → der", "traverse")
			return self._delete_recursive(node.right, node, 'right', symbol, bits, depth + 1, animate)


	def _on_insert(self) -> None:
		ch = self._validate_char(self.entry.get().strip())
		if not ch:
			return
		self._save_state()
		self._insert_symbol(ch, animate=True)
		self._prepare_animation()

		self.entry.delete(0, tk.END)
		self._draw()

	def _on_delete(self) -> None:
		ch = self._validate_char(self.entry.get().strip())
		if not ch:
			return

		self._save_state()

		# Construye pasos de animación y elimina solo la hoja (sin reconfigurar el árbol)
		ok = self._delete_symbol(ch, animate=True)

		# Preparar y lanzar animación
		self._prepare_animation()

		# Estado / UI inmediata (también habrá feedback al final de la animación)
		if ok:
			self.status.configure(text=f"Eliminada '{ch}'")
		else:
			self.status.configure(text="Letra no encontrada")

		self.entry.delete(0, tk.END)
		self._draw()

	def _on_search(self) -> None:
		ch = self._validate_char(self.entry.get().strip())
		if not ch:
			return
		# Construir los pasos de animación, pero NO ejecutar todavía
		result_node = self._search_symbol(ch, animate=True)
		self._prepare_animation()
		# Mostrar mensaje según resultado
		if result_node is not None:
			messagebox.showinfo("Búsqueda", f"Clave '{ch}' encontrada ✅")
			self.status.configure(text=f"Clave '{ch}' encontrada. Animación lista (usa ▶ Reproducir o Paso).")
		else:
			messagebox.showinfo("Búsqueda", f"Clave '{ch}' no encontrada ❌")
			self.status.configure(text=f"Clave '{ch}' no encontrada. Animación lista (usa ▶ Reproducir o Paso).")
		self.entry.delete(0, tk.END)
		self._draw()

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
		self._edge_hint = None
		self.status.configure(text=f"Animación lista: {len(self._anim_steps)} pasos")

	def _add_edge_step(self, parent: ResidNode, child: Optional[ResidNode], message: str, step_type: str = "traverse") -> None:
		"""
		Registra un paso de animación para una arista concreta (parent->child).
		Si child es None, no agrega el edge (pero sí el mensaje).
		"""
		if child is not None:
			self._anim_steps.append({"type": step_type, "edge": (parent, child), "message": message})
		else:
			self._anim_steps.append({"type": step_type, "message": message})

	def _anim_step(self) -> None:
		if self._anim_index >= len(self._anim_steps):
			self._anim_running = False
			self.status.configure(text="Animación terminada")
			# Mensajería final
			if self._anim_steps:
				last = self._anim_steps[-1]
				if last.get("type") == "found":
					messagebox.showinfo("Búsqueda", "Clave encontrada")
				elif last.get("type") == "not_found":
					messagebox.showinfo("Búsqueda", "Letra no encontrada")
			return

		step = self._anim_steps[self._anim_index]
		self.status.configure(text=step.get("message", ""))

		# Arista actual a resaltar (solo una por frame)
		edge = step.get("edge")
		self._edge_hint = edge if edge else None

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
		# Evita fallar si el canvas aún no está listo
		if not hasattr(self, "canvas"):
			return

		self.canvas.delete("all")
		self.canvas.update_idletasks()

		width = max(self.canvas.winfo_width(), 600)
		height = max(self.canvas.winfo_height(), 420)

		# Árbol vacío
		if (self.root.node_type == NodeType.LINK and
			self.root.left is None and self.root.right is None and
			self.root.symbol is None):
			self.canvas.create_text(
				width // 2, height // 2,
				text="Inserte letras para construir el árbol",
				fill="#666666", font=("MS Sans Serif", 12)
			)
			return

		# Calcular posiciones y dibujar
		positions: Dict[ResidNode, Tuple[int, int]] = {}
		self._layout(self.root, width // 2, 40, width // 4, positions)
		self._draw_edges(self.root, positions)
		self._draw_nodes(positions)

	def _draw_edges(self, node: Optional[ResidNode], positions: Dict[ResidNode, Tuple[int, int]]) -> None:
		if node is None:
			return

		if node.left:
			x, y = positions[node]
			xl, yl = positions[node.left]
			# Color por arista activa:
			color = "#4da3ff" if (self._edge_hint and self._edge_hint[0] is node and self._edge_hint[1] is node.left) else "#808080"
			self.canvas.create_line(x, y, xl, yl, fill=color, width=2)
			mx, my = (x + xl) // 2, (y + yl) // 2
			self.canvas.create_text(mx - 10, my, text="0", fill="#000000", font=("MS Sans Serif", 9, "bold"))
			self._draw_edges(node.left, positions)

		if node.right:
			x, y = positions[node]
			xr, yr = positions[node.right]
			color = "#4da3ff" if (self._edge_hint and self._edge_hint[0] is node and self._edge_hint[1] is node.right) else "#808080"
			self.canvas.create_line(x, y, xr, yr, fill=color, width=2)
			mx, my = (x + xr) // 2, (y + yr) // 2
			self.canvas.create_text(mx + 10, my, text="1", fill="#000000", font=("MS Sans Serif", 9, "bold"))
			self._draw_edges(node.right, positions)

	def _layout(self, node: Optional[ResidNode], x: int, y: int, dx: int, positions: Dict[ResidNode, Tuple[int, int]]) -> None:
		if node is None:
			return
		positions[node] = (x, y)
		if node.left or node.right:
			child_y = y + 80
			child_dx = max(30, dx // 2)
			self._layout(node.left, x - dx, child_y, child_dx, positions)
			self._layout(node.right, x + dx, child_y, child_dx, positions)

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
