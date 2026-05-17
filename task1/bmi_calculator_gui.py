import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

# ── Data storage ──────────────────────────────────────────────────────────────
DATA_FILE = "bmi_history.json"

def load_history():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ── BMI Logic ─────────────────────────────────────────────────────────────────
def calculate_bmi(weight, height):
    return weight / (height ** 2)

def classify_bmi(bmi):
    if bmi < 18.5:
        return "Underweight", "#4a9bd4"
    elif bmi < 25.0:
        return "Normal weight", "#3bb36b"
    elif bmi < 30.0:
        return "Overweight", "#f0a228"
    else:
        return "Obese", "#e05050"

def get_advice(category):
    advice = {
        "Underweight":   "Consider a nutrient-rich diet and consult a nutritionist.",
        "Normal weight": "Great! Maintain your healthy lifestyle.",
        "Overweight":    "A balanced diet and regular exercise can help.",
        "Obese":         "Please consult a healthcare provider for guidance.",
    }
    return advice.get(category, "")

# ── Main App ──────────────────────────────────────────────────────────────────
class BMIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BMI Calculator")
        self.geometry("520x680")
        self.resizable(False, False)
        self.configure(bg="#f5f4f0")

        self.history = load_history()
        self._build_ui()

    # ── UI Construction ────────────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg="#1a1a2e", height=70)
        header.pack(fill="x")
        tk.Label(header, text="BMI Calculator", font=("Georgia", 20, "bold"),
                 fg="#e8e4d0", bg="#1a1a2e").pack(pady=18)

        # Notebook / tabs
        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("TNotebook", background="#f5f4f0", borderwidth=0)
        style.configure("TNotebook.Tab", font=("Helvetica", 11),
                        padding=[20, 8], background="#ddd9ce", foreground="#555")
        style.map("TNotebook.Tab",
                  background=[("selected", "#ffffff")],
                  foreground=[("selected", "#1a1a2e")])

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=0, pady=0)

        self.calc_frame = tk.Frame(nb, bg="#f5f4f0")
        self.hist_frame = tk.Frame(nb, bg="#f5f4f0")
        nb.add(self.calc_frame, text="  Calculate  ")
        nb.add(self.hist_frame, text="  History  ")

        self._build_calc_tab()
        self._build_history_tab()

    def _build_calc_tab(self):
        pad = {"padx": 30, "pady": 8}

        # Name
        tk.Label(self.calc_frame, text="Name (optional)", font=("Helvetica", 10),
                 fg="#888", bg="#f5f4f0").pack(anchor="w", padx=30, pady=(24, 0))
        self.name_var = tk.StringVar()
        tk.Entry(self.calc_frame, textvariable=self.name_var, font=("Helvetica", 13),
                 relief="flat", bg="#ffffff", fg="#1a1a2e",
                 highlightthickness=1, highlightbackground="#ddd",
                 highlightcolor="#1a1a2e").pack(fill="x", **pad, ipady=7)

        # Weight
        tk.Label(self.calc_frame, text="Weight (kg)", font=("Helvetica", 10),
                 fg="#888", bg="#f5f4f0").pack(anchor="w", padx=30, pady=(8, 0))
        self.weight_var = tk.StringVar()
        tk.Entry(self.calc_frame, textvariable=self.weight_var, font=("Helvetica", 13),
                 relief="flat", bg="#ffffff", fg="#1a1a2e",
                 highlightthickness=1, highlightbackground="#ddd",
                 highlightcolor="#1a1a2e").pack(fill="x", **pad, ipady=7)

        # Height
        tk.Label(self.calc_frame, text="Height (m)", font=("Helvetica", 10),
                 fg="#888", bg="#f5f4f0").pack(anchor="w", padx=30, pady=(8, 0))
        self.height_var = tk.StringVar()
        tk.Entry(self.calc_frame, textvariable=self.height_var, font=("Helvetica", 13),
                 relief="flat", bg="#ffffff", fg="#1a1a2e",
                 highlightthickness=1, highlightbackground="#ddd",
                 highlightcolor="#1a1a2e").pack(fill="x", **pad, ipady=7)

        # Button
        tk.Button(self.calc_frame, text="Calculate BMI", command=self._on_calculate,
                  font=("Helvetica", 13, "bold"), bg="#1a1a2e", fg="#e8e4d0",
                  relief="flat", cursor="hand2", activebackground="#2d2d4e",
                  activeforeground="#e8e4d0").pack(fill="x", padx=30, pady=(16, 0), ipady=10)

        # Result card
        self.result_frame = tk.Frame(self.calc_frame, bg="#f5f4f0")
        self.result_frame.pack(fill="x", padx=30, pady=(20, 0))

        # BMI scale bar (canvas)
        tk.Label(self.calc_frame, text="BMI Scale", font=("Helvetica", 10),
                 fg="#888", bg="#f5f4f0").pack(anchor="w", padx=30, pady=(16, 4))
        self.scale_canvas = tk.Canvas(self.calc_frame, height=46,
                                      bg="#f5f4f0", highlightthickness=0)
        self.scale_canvas.pack(fill="x", padx=30)
        self.scale_canvas.bind("<Configure>", lambda e: self._draw_scale())
        self._draw_scale()

    def _draw_scale(self, bmi=None):
        c = self.scale_canvas
        c.delete("all")
        w = c.winfo_width() or 460
        segments = [
            ("Underweight", "#4a9bd4", 0.0, 0.25),
            ("Normal",      "#3bb36b", 0.25, 0.575),
            ("Overweight",  "#f0a228", 0.575, 0.825),
            ("Obese",       "#e05050", 0.825, 1.0),
        ]
        bar_h = 22
        for label, color, s, e in segments:
            x0, x1 = int(w * s), int(w * e)
            c.create_rectangle(x0, 0, x1, bar_h, fill=color, outline="")
            cx = (x0 + x1) // 2
            c.create_text(cx, bar_h // 2, text=label, fill="white",
                          font=("Helvetica", 8, "bold"))

        # Tick labels
        ticks = [(18.5, 0.25), (25, 0.575), (30, 0.825)]
        for val, pos in ticks:
            x = int(w * pos)
            c.create_line(x, bar_h, x, bar_h + 6, fill="#888")
            c.create_text(x, bar_h + 14, text=str(val),
                          font=("Helvetica", 8), fill="#666")

        # Pointer arrow
        if bmi is not None:
            clamped = max(10, min(bmi, 40))
            ranges = [
                (10, 18.5, 0.0, 0.25), (18.5, 25, 0.25, 0.575),
                (25, 30, 0.575, 0.825), (30, 40, 0.825, 1.0)
            ]
            px = 0
            for lo, hi, ps, pe in ranges:
                if lo <= clamped <= hi:
                    t = (clamped - lo) / (hi - lo)
                    px = int(w * (ps + t * (pe - ps)))
                    break
            c.create_polygon(px - 7, bar_h + 22, px + 7, bar_h + 22,
                             px, bar_h + 8, fill="#1a1a2e", outline="")

    def _on_calculate(self):
        # Validate
        try:
            w = float(self.weight_var.get())
            h = float(self.height_var.get())
            assert 20 <= w <= 300, "Weight must be 20–300 kg"
            assert 0.5 <= h <= 2.5, "Height must be 0.5–2.5 m"
        except (ValueError, AssertionError) as e:
            messagebox.showerror("Invalid Input",
                str(e) if isinstance(e, AssertionError)
                else "Please enter valid numbers for weight and height.")
            return

        bmi = calculate_bmi(w, h)
        category, color = classify_bmi(bmi)
        advice = get_advice(category)
        name = self.name_var.get().strip() or "You"

        # Clear previous result
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        card = tk.Frame(self.result_frame, bg=color, bd=0)
        card.pack(fill="x")

        tk.Label(card, text=f"{bmi:.1f}", font=("Georgia", 36, "bold"),
                 fg="white", bg=color).pack(side="left", padx=(16, 0), pady=12)

        info = tk.Frame(card, bg=color)
        info.pack(side="left", padx=16, pady=12)
        tk.Label(info, text=category, font=("Helvetica", 14, "bold"),
                 fg="white", bg=color).pack(anchor="w")
        tk.Label(info, text=advice, font=("Helvetica", 9),
                 fg="white", bg=color, wraplength=280, justify="left").pack(anchor="w")

        # Update scale pointer
        self._draw_scale(bmi)

        # Save to history
        entry = {
            "name": name, "weight": w, "height": h,
            "bmi": round(bmi, 1), "category": category,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self.history.insert(0, entry)
        if len(self.history) > 50:
            self.history.pop()
        save_history(self.history)
        self._refresh_history()

    # ── History Tab ───────────────────────────────────────────────────────────
    def _build_history_tab(self):
        # Trend chart area
        tk.Label(self.hist_frame, text="BMI Trend", font=("Helvetica", 10),
                 fg="#888", bg="#f5f4f0").pack(anchor="w", padx=20, pady=(16, 4))
        self.chart_canvas = tk.Canvas(self.hist_frame, height=160,
                                      bg="#ffffff", highlightthickness=1,
                                      highlightbackground="#ddd")
        self.chart_canvas.pack(fill="x", padx=20)
        self.chart_canvas.bind("<Configure>", lambda e: self._draw_chart())

        tk.Label(self.hist_frame, text="Recent entries", font=("Helvetica", 10),
                 fg="#888", bg="#f5f4f0").pack(anchor="w", padx=20, pady=(16, 4))

        # Scrollable list
        list_outer = tk.Frame(self.hist_frame, bg="#f5f4f0")
        list_outer.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        sb = tk.Scrollbar(list_outer)
        sb.pack(side="right", fill="y")

        self.hist_listbox = tk.Listbox(list_outer, yscrollcommand=sb.set,
                                        font=("Courier", 11), bg="#ffffff",
                                        fg="#1a1a2e", selectbackground="#1a1a2e",
                                        relief="flat", highlightthickness=1,
                                        highlightbackground="#ddd", bd=0)
        self.hist_listbox.pack(fill="both", expand=True)
        sb.config(command=self.hist_listbox.yview)

        btn_row = tk.Frame(self.hist_frame, bg="#f5f4f0")
        btn_row.pack(fill="x", padx=20, pady=(0, 16))
        tk.Button(btn_row, text="Clear History", command=self._clear_history,
                  font=("Helvetica", 10), bg="#e05050", fg="white",
                  relief="flat", cursor="hand2", activebackground="#c04040",
                  activeforeground="white").pack(side="right", ipady=6, ipadx=12)

        self._refresh_history()

    def _refresh_history(self):
        self.hist_listbox.delete(0, tk.END)
        for e in self.history[:20]:
            line = f"  {e['date'][:10]}  {e['name']:<12}  BMI {e['bmi']:<6}  {e['category']}"
            self.hist_listbox.insert(tk.END, line)
        self._draw_chart()

    def _draw_chart(self):
        c = self.chart_canvas
        c.delete("all")
        w = c.winfo_width() or 460
        h = 160
        pad = 30

        recent = list(reversed(self.history[:10]))
        if len(recent) < 2:
            c.create_text(w // 2, h // 2, text="Add 2+ entries to see trend",
                          fill="#aaa", font=("Helvetica", 10))
            return

        bmis = [e["bmi"] for e in recent]
        lo, hi = min(bmis) - 2, max(bmis) + 2
        lo = min(lo, 17); hi = max(hi, 31)

        def to_x(i):
            return pad + i * (w - 2 * pad) // (len(recent) - 1)

        def to_y(v):
            return pad + (1 - (v - lo) / (hi - lo)) * (h - 2 * pad)

        # Zone bands
        zones = [(lo, 18.5, "#e6f1fb"), (18.5, 25, "#eaf3de"),
                 (25, 30, "#faeeda"), (30, hi, "#fce8e8")]
        for z_lo, z_hi, zcol in zones:
            y0 = to_y(min(z_hi, hi)); y1 = to_y(max(z_lo, lo))
            if y0 < y1:
                c.create_rectangle(pad, y0, w - pad, y1, fill=zcol, outline="")

        # Grid lines
        for v in [18.5, 25, 30]:
            if lo < v < hi:
                y = to_y(v)
                c.create_line(pad, y, w - pad, y, fill="#ccc", dash=(4, 3))
                c.create_text(pad - 4, y, text=str(v), anchor="e",
                              font=("Helvetica", 7), fill="#999")

        # Line
        pts = [(to_x(i), to_y(b)) for i, b in enumerate(bmis)]
        for i in range(len(pts) - 1):
            c.create_line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1],
                          fill="#1a1a2e", width=2)

        # Dots + labels
        for i, (x, y) in enumerate(pts):
            _, col = classify_bmi(bmis[i])
            c.create_oval(x - 5, y - 5, x + 5, y + 5, fill=col, outline="white", width=1.5)
            c.create_text(x, y - 13, text=str(bmis[i]),
                          font=("Helvetica", 8, "bold"), fill="#1a1a2e")

    def _clear_history(self):
        if messagebox.askyesno("Clear History", "Delete all history?"):
            self.history = []
            save_history(self.history)
            self._refresh_history()
            for widget in self.result_frame.winfo_children():
                widget.destroy()
            self._draw_scale()


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = BMIApp()
    app.mainloop()