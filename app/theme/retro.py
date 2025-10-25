import tkinter as tk
from tkinter import ttk


PALETTE = {
	"win_bg": "#c0c0c0",
	"panel": "#bdbdbd",
	"light": "#ffffff",
	"dark": "#808080",
	"shadow": "#000000",
	"text": "#000000",
	"text_muted": "#1f1f1f",
}


def apply_retro_style(root: tk.Misc) -> None:
	root.configure(bg=PALETTE["win_bg"]) 

	style = ttk.Style(root)
	for theme in ("winnative", "clam", "classic", "alt"):
		try:
			style.theme_use(theme)
			break
		except tk.TclError:
			continue

	base_font = ("MS Sans Serif", 10)
	title_font = ("MS Sans Serif", 18, "bold")

	style.configure("TFrame", background=PALETTE["win_bg"]) 
	style.configure(
		"Panel.TFrame",
		background=PALETTE["panel"],
		borderwidth=2,
		relief="groove",
	)
	style.configure(
		"Title.TLabel",
		background=PALETTE["win_bg"],
		foreground=PALETTE["text"],
		font=title_font,
	)
	style.configure(
		"TLabel",
		background=PALETTE["win_bg"],
		foreground=PALETTE["text"],
		font=base_font,
	)
	style.configure(
		"TButton",
		font=base_font,
		padding=6,
	)
	style.configure(
		"Retro.TButton",
		font=base_font,
		foreground=PALETTE["text"],
		background=PALETTE["panel"],
		borderwidth=2,
		relief="raised",
	)
	style.map(
		"Retro.TButton",
		background=[("active", PALETTE["light"])],
		relief=[("pressed", "sunken")],
	)

	style.configure(
		"TEntry",
		fieldbackground="#ffffff",
		foreground=PALETTE["text"],
		padding=4,
	)



