
# ui/widgets.py (professional kit)
from tkinter import ttk

def card(parent, padding=(18,16), style="Card.TFrame", columns=1):
    f = ttk.Frame(parent, style=style)
    f.grid_propagate(False)
    inner = ttk.Frame(f, style="Panel.TFrame")
    inner.grid(row=0, column=0, sticky="nsew", padx=padding[0], pady=padding[1])
    f.inner = inner
    for i in range(columns):
        inner.grid_columnconfigure(i, weight=1)
    return f

def kpi_card(parent, icon, title, value="–"):
    k = card(parent, padding=(18,16), style="KPI.TFrame", columns=2)
    ic = ttk.Frame(k.inner, width=52, height=52, style="Pill.TFrame")
    ic.grid(row=0, column=0, rowspan=2, sticky="nw", padx=(2, 14), pady=(2, 2))
    ic.grid_propagate(False)
    ttk.Label(ic, text=icon, style="Pill.TLabel").pack(expand=True)
    ttk.Label(k.inner, text=title, style="Subdued.TLabel").grid(row=0, column=1, sticky="w")
    val = ttk.Label(k.inner, text=value, style="H2.TLabel")
    val.grid(row=1, column=1, sticky="w", pady=(2,0))
    return k, val

def pill_row(parent, text, col=0, row=0, icon="🚘"):
    p = ttk.Frame(parent, style="Pill.TFrame")
    p.grid(row=row, column=col, sticky="ew", pady=6)
    p.grid_columnconfigure(1, weight=1)
    ttk.Label(p, text=icon, style="Pill.TLabel").grid(row=0, column=0, padx=(12, 10), pady=10)
    ttk.Label(p, text=text, style="Pill.TLabel").grid(row=0, column=1, sticky="w")
    return p
