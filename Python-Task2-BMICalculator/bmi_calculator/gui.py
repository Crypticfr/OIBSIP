# -*- coding: utf-8 -*-
"""
Advanced Graphical User Interface (GUI) for BMI Calculator.
Features:
- Demo Video Splash Screen (OIBSIP requirement)
- Multi-user support: save & filter records for named users
- Metric (kg, m / cm) & Imperial (lbs, ft & in) unit toggling
- Dynamic color-coded BMI gauge and category advice
- SQLite data persistence with comprehensive read/write error handling
- Embedded Matplotlib trend chart with user filtering & health zones
"""
import os
import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from typing import Optional

from .calculator import (
    calculate_bmi,
    classify_bmi,
    validate_positive_number,
    lbs_to_kg,
    feet_inches_to_meters
)
from .database import BMIDatabase, DatabaseError

INTERN_NAME = os.environ.get("OIBSIP_NAME", "Subhajit Samajpati")
INTERN_TRACK = "Python Development"
TASK_TITLE = "BMI Calculator (Task 2)"

class BMICalculatorGUI:
    def __init__(self, root: tk.Tk, show_splash: bool = True, splash_duration: int = 2800, db_path: Optional[str] = None):
        self.root = root
        self.root.title("BMI Calculator - OIBSIP")
        self.root.geometry("880x760")
        self.root.minsize(800, 700)
        self.root.configure(bg="#1e1e2e")

        try:
            self.db = BMIDatabase(db_path=db_path)
        except DatabaseError as e:
            messagebox.showerror("Database Error", f"Failed to initialize database: {e}")
            self.db = None

        self.unit_mode = tk.StringVar(value="metric")  # "metric" or "imperial"
        self.active_user = tk.StringVar(value=INTERN_NAME)
        self.filter_user = tk.StringVar(value="All Users")

        self.splash_frame = None
        self._splash_after_id = None

        if show_splash:
            self._show_splash_screen(duration_ms=splash_duration)
        else:
            self._build_ui()

    def _show_splash_screen(self, duration_ms: int = 2800):
        self.splash_frame = tk.Frame(self.root, bg="#11111b")
        self.splash_frame.pack(fill=tk.BOTH, expand=True)

        card = tk.Frame(
            self.splash_frame,
            bg="#181825",
            padx=32,
            pady=36,
            highlightbackground="#89b4fa",
            highlightthickness=1
        )
        card.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.82)

        badge = tk.Label(
            card,
            text="OASIS INFOBYTE (OIBSIP)",
            font=("Segoe UI", 12, "bold"),
            fg="#89b4fa",
            bg="#181825"
        )
        badge.pack(pady=(0, 4))

        subtitle = tk.Label(
            card,
            text="TASK 2 - PROJECT DEMO WALKTHROUGH",
            font=("Segoe UI", 9, "bold"),
            fg="#6c7086",
            bg="#181825"
        )
        subtitle.pack(pady=(0, 20))

        divider = tk.Frame(card, height=1, bg="#313244")
        divider.pack(fill=tk.X, pady=(0, 18))

        fields = [
            ("Full Name", INTERN_NAME, "#cdd6f4"),
            ("Assigned Track", INTERN_TRACK, "#a6e3a1"),
            ("Task Title", TASK_TITLE, "#f9e2af"),
        ]

        for label_text, value_text, color in fields:
            row = tk.Frame(card, bg="#181825")
            row.pack(fill=tk.X, pady=6)

            lbl = tk.Label(
                row,
                text=f"{label_text}:",
                font=("Segoe UI", 10, "bold"),
                fg="#a6adc8",
                bg="#181825",
                width=16,
                anchor="w"
            )
            lbl.pack(side=tk.LEFT)

            val = tk.Label(
                row,
                text=value_text,
                font=("Segoe UI", 12, "bold"),
                fg=color,
                bg="#181825",
                anchor="w"
            )
            val.pack(side=tk.LEFT, fill=tk.X, expand=True)

        divider2 = tk.Frame(card, height=1, bg="#313244")
        divider2.pack(fill=tk.X, pady=(18, 14))

        self.splash_timer_lbl = tk.Label(
            card,
            text="Launching BMI Calculator in 3s... (click to skip)",
            font=("Segoe UI", 9, "italic"),
            fg="#585b70",
            bg="#181825"
        )
        self.splash_timer_lbl.pack()

        self.splash_frame.bind("<Button-1>", lambda e: self._dismiss_splash())
        card.bind("<Button-1>", lambda e: self._dismiss_splash())
        self._splash_after_id = self.root.after(duration_ms, self._dismiss_splash)

    def _dismiss_splash(self):
        if self._splash_after_id:
            try:
                self.root.after_cancel(self._splash_after_id)
            except Exception:
                pass
            self._splash_after_id = None

        if self.splash_frame:
            self.splash_frame.destroy()
            self.splash_frame = None
            self._build_ui()

    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#181825", padx=20, pady=12)
        header.pack(fill=tk.X, side=tk.TOP)

        title = tk.Label(
            header,
            text="📊 BMI Calculator & Health Tracker",
            font=("Segoe UI", 16, "bold"),
            fg="#cdd6f4",
            bg="#181825"
        )
        title.pack(side=tk.LEFT)

        subtitle = tk.Label(
            header,
            text="OIBSIP Python Development - Task 2",
            font=("Segoe UI", 9),
            fg="#a6adc8",
            bg="#181825"
        )
        subtitle.pack(side=tk.RIGHT, pady=(6, 0))

        # Notebook
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background="#1e1e2e", borderwidth=0)
        style.configure("TNotebook.Tab", background="#313244", foreground="#cdd6f4", padding=[16, 6], font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#89b4fa")], foreground=[("selected", "#11111b")])
        style.configure("TCombobox", fieldbackground="#313244", background="#45475a", foreground="#cdd6f4")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=14, pady=12)

        self.tab_calc = tk.Frame(self.notebook, bg="#1e1e2e")
        self.tab_trends = tk.Frame(self.notebook, bg="#1e1e2e")

        self.notebook.add(self.tab_calc, text="Calculator & Results")
        self.notebook.add(self.tab_trends, text="Multi-User Trends & History")

        self._build_calc_tab()
        self._build_trends_tab()

    def _build_calc_tab(self):
        left_frame = tk.Frame(self.tab_calc, bg="#181825", padx=20, pady=16)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8), pady=4)

        right_frame = tk.Frame(self.tab_calc, bg="#181825", padx=20, pady=16)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0), pady=4)

        # 1. Multi-User Profile Selector
        user_frame = tk.Frame(left_frame, bg="#181825")
        user_frame.pack(fill=tk.X, pady=(0, 14))

        tk.Label(
            user_frame,
            text="User Profile (Multi-User Support):",
            font=("Segoe UI", 10, "bold"),
            fg="#cdd6f4",
            bg="#181825"
        ).pack(anchor="w", pady=(0, 4))

        existing_users = self._get_user_list()
        self.user_combo = ttk.Combobox(
            user_frame,
            textvariable=self.active_user,
            values=existing_users,
            font=("Segoe UI", 10)
        )
        self.user_combo.pack(fill=tk.X, ipady=3)
        tk.Label(
            user_frame,
            text="Select an existing user or type a new name to save records separately.",
            font=("Segoe UI", 8, "italic"),
            fg="#6c7086",
            bg="#181825"
        ).pack(anchor="w", pady=(2, 0))

        # 2. Unit System Selector
        unit_lbl = tk.Label(left_frame, text="Unit System:", font=("Segoe UI", 10, "bold"), fg="#cdd6f4", bg="#181825")
        unit_lbl.pack(anchor="w", pady=(10, 4))

        unit_btn_frame = tk.Frame(left_frame, bg="#181825")
        unit_btn_frame.pack(fill=tk.X, pady=(0, 14))

        self.btn_metric = tk.Radiobutton(
            unit_btn_frame,
            text="Metric (kg, m / cm)",
            variable=self.unit_mode,
            value="metric",
            command=self._on_unit_change,
            font=("Segoe UI", 9, "bold"),
            bg="#181825",
            fg="#cdd6f4",
            selectcolor="#313244",
            activebackground="#181825",
            activeforeground="#89b4fa"
        )
        self.btn_metric.pack(side=tk.LEFT, padx=(0, 12))

        self.btn_imperial = tk.Radiobutton(
            unit_btn_frame,
            text="Imperial (lbs, ft & in)",
            variable=self.unit_mode,
            value="imperial",
            command=self._on_unit_change,
            font=("Segoe UI", 9, "bold"),
            bg="#181825",
            fg="#cdd6f4",
            selectcolor="#313244",
            activebackground="#181825",
            activeforeground="#89b4fa"
        )
        self.btn_imperial.pack(side=tk.LEFT)

        # 3. Dynamic Input Fields
        self.input_container = tk.Frame(left_frame, bg="#181825")
        self.input_container.pack(fill=tk.X, pady=(0, 10))
        self._render_inputs()

        # 4. Calculate Button
        self.calc_btn = tk.Button(
            left_frame,
            text="Calculate BMI",
            font=("Segoe UI", 12, "bold"),
            bg="#89b4fa",
            fg="#11111b",
            activebackground="#b4befe",
            activeforeground="#11111b",
            bd=0,
            relief=tk.FLAT,
            pady=10,
            cursor="hand2",
            command=self.perform_calculation
        )
        self.calc_btn.pack(fill=tk.X, pady=(8, 8))

        # 5. WHO Standard Categories Card
        cat_card = tk.LabelFrame(
            left_frame,
            text="WHO Standard BMI Categories",
            font=("Segoe UI", 9, "bold"),
            bg="#181825",
            fg="#a6adc8",
            padx=12,
            pady=8
        )
        cat_card.pack(fill=tk.X, pady=(8, 0))

        cats = [
            ("Underweight", "< 18.5", "#89b4fa"),
            ("Normal weight", "18.5 – 24.9", "#a6e3a1"),
            ("Overweight", "25.0 – 29.9", "#fab387"),
            ("Obese", "≥ 30.0", "#f38ba8"),
        ]
        for name, rng, col in cats:
            r = tk.Frame(cat_card, bg="#181825")
            r.pack(fill=tk.X, pady=2)
            tk.Label(r, text=f"● {name}", font=("Segoe UI", 9), fg=col, bg="#181825", anchor="w").pack(side=tk.LEFT)
            tk.Label(r, text=rng, font=("Segoe UI", 9, "bold"), fg="#cdd6f4", bg="#181825", anchor="e").pack(side=tk.RIGHT)

        # Right: Result Display Card
        res_header = tk.Label(right_frame, text="BMI Assessment Result", font=("Segoe UI", 12, "bold"), fg="#cdd6f4", bg="#181825")
        res_header.pack(anchor="w", pady=(0, 8))

        self.user_display_lbl = tk.Label(
            right_frame,
            text=f"User: {self.active_user.get()}",
            font=("Segoe UI", 10, "italic"),
            fg="#89b4fa",
            bg="#181825"
        )
        self.user_display_lbl.pack(anchor="w", pady=(0, 6))

        self.bmi_display_lbl = tk.Label(
            right_frame,
            text="--.--",
            font=("Segoe UI", 36, "bold"),
            fg="#6c7086",
            bg="#181825"
        )
        self.bmi_display_lbl.pack(pady=(4, 4))

        self.category_badge = tk.Label(
            right_frame,
            text="Awaiting Input",
            font=("Segoe UI", 11, "bold"),
            fg="#11111b",
            bg="#45475a",
            padx=14,
            pady=4,
            relief=tk.FLAT
        )
        self.category_badge.pack(pady=(0, 14))

        # Colored spectrum canvas gauge
        self.gauge_canvas = tk.Canvas(right_frame, height=22, bg="#181825", highlightthickness=0)
        self.gauge_canvas.pack(fill=tk.X, pady=(0, 16))
        self._draw_gauge(current_bmi=None)

        # Health Advice Box
        advice_lbl = tk.Label(right_frame, text="Health Feedback & Advice:", font=("Segoe UI", 9, "bold"), fg="#a6adc8", bg="#181825")
        advice_lbl.pack(anchor="w", pady=(0, 4))

        self.advice_text = tk.Label(
            right_frame,
            text="Enter weight and height measurements, select your user name, then click 'Calculate BMI' to see your personalized health report.",
            font=("Segoe UI", 9),
            fg="#cdd6f4",
            bg="#313244",
            wraplength=320,
            justify=tk.LEFT,
            padx=12,
            pady=12,
            relief=tk.FLAT
        )
        self.advice_text.pack(fill=tk.BOTH, expand=True)

    def _render_inputs(self):
        for widget in self.input_container.winfo_children():
            widget.destroy()

        if self.unit_mode.get() == "metric":
            # Weight (kg)
            tk.Label(self.input_container, text="Weight (kg):", font=("Segoe UI", 9, "bold"), fg="#a6adc8", bg="#181825").pack(anchor="w", pady=(0, 2))
            self.entry_weight = tk.Entry(self.input_container, font=("Segoe UI", 11), bg="#313244", fg="#cdd6f4", insertbackground="#cdd6f4", bd=0, relief=tk.FLAT)
            self.entry_weight.pack(fill=tk.X, ipady=6, pady=(0, 10))

            # Height (m)
            tk.Label(self.input_container, text="Height (meters, e.g. 1.75):", font=("Segoe UI", 9, "bold"), fg="#a6adc8", bg="#181825").pack(anchor="w", pady=(0, 2))
            self.entry_height = tk.Entry(self.input_container, font=("Segoe UI", 11), bg="#313244", fg="#cdd6f4", insertbackground="#cdd6f4", bd=0, relief=tk.FLAT)
            self.entry_height.pack(fill=tk.X, ipady=6, pady=(0, 2))

            hint = tk.Label(self.input_container, text="Tip: 175 cm = 1.75 meters", font=("Segoe UI", 8, "italic"), fg="#6c7086", bg="#181825")
            hint.pack(anchor="w")

        else:
            # Imperial: Weight (lbs)
            tk.Label(self.input_container, text="Weight (lbs):", font=("Segoe UI", 9, "bold"), fg="#a6adc8", bg="#181825").pack(anchor="w", pady=(0, 2))
            self.entry_weight = tk.Entry(self.input_container, font=("Segoe UI", 11), bg="#313244", fg="#cdd6f4", insertbackground="#cdd6f4", bd=0, relief=tk.FLAT)
            self.entry_weight.pack(fill=tk.X, ipady=6, pady=(0, 10))

            # Height: Feet and Inches
            tk.Label(self.input_container, text="Height:", font=("Segoe UI", 9, "bold"), fg="#a6adc8", bg="#181825").pack(anchor="w", pady=(0, 2))
            ft_in_frame = tk.Frame(self.input_container, bg="#181825")
            ft_in_frame.pack(fill=tk.X, pady=(0, 2))

            tk.Label(ft_in_frame, text="Feet:", font=("Segoe UI", 9), fg="#a6adc8", bg="#181825").pack(side=tk.LEFT, padx=(0, 4))
            self.entry_ft = tk.Entry(ft_in_frame, font=("Segoe UI", 11), bg="#313244", fg="#cdd6f4", insertbackground="#cdd6f4", bd=0, relief=tk.FLAT, width=6)
            self.entry_ft.pack(side=tk.LEFT, ipady=6, padx=(0, 12))

            tk.Label(ft_in_frame, text="Inches:", font=("Segoe UI", 9), fg="#a6adc8", bg="#181825").pack(side=tk.LEFT, padx=(0, 4))
            self.entry_in = tk.Entry(ft_in_frame, font=("Segoe UI", 11), bg="#313244", fg="#cdd6f4", insertbackground="#cdd6f4", bd=0, relief=tk.FLAT, width=6)
            self.entry_in.pack(side=tk.LEFT, ipady=6)

    def _on_unit_change(self):
        self._render_inputs()

    def _get_user_list(self):
        users = [INTERN_NAME]
        if self.db:
            try:
                db_users = self.db.get_users()
                for u in db_users:
                    if u not in users:
                        users.append(u)
            except DatabaseError:
                pass
        return sorted(users)

    def _draw_gauge(self, current_bmi: Optional[float] = None):
        self.gauge_canvas.delete("all")
        width = self.gauge_canvas.winfo_width()
        if width <= 1:
            width = 320

        height = 18
        min_bmi, max_bmi = 15.0, 40.0
        
        def bmi_to_x(val):
            ratio = (val - min_bmi) / (max_bmi - min_bmi)
            ratio = max(0.0, min(1.0, ratio))
            return ratio * width

        x_under = bmi_to_x(18.5)
        x_norm = bmi_to_x(25.0)
        x_over = bmi_to_x(30.0)

        self.gauge_canvas.create_rectangle(0, 0, x_under, height, fill="#89b4fa", outline="")
        self.gauge_canvas.create_rectangle(x_under, 0, x_norm, height, fill="#a6e3a1", outline="")
        self.gauge_canvas.create_rectangle(x_norm, 0, x_over, height, fill="#fab387", outline="")
        self.gauge_canvas.create_rectangle(x_over, 0, width, height, fill="#f38ba8", outline="")

        if current_bmi is not None:
            px = bmi_to_x(current_bmi)
            self.gauge_canvas.create_polygon(px - 6, height + 4, px + 6, height + 4, px, 2, fill="#f8f8f2", outline="#11111b")

    def perform_calculation(self):
        user_name = self.active_user.get().strip() or "Default User"
        try:
            if self.unit_mode.get() == "metric":
                w_str = self.entry_weight.get()
                h_str = self.entry_height.get()
                weight_kg = validate_positive_number(w_str, "Weight (kg)")
                height_m = validate_positive_number(h_str, "Height (m)")
                
                if height_m > 3.0:
                    if messagebox.askyesno("Height Unit Check", f"You entered {height_m} meters. Did you mean {height_m / 100:.2f} meters ({height_m:.0f} cm)?"):
                        height_m = height_m / 100.0
                        self.entry_height.delete(0, tk.END)
                        self.entry_height.insert(0, f"{height_m:.2f}")

            else:
                w_str = self.entry_weight.get()
                ft_str = self.entry_ft.get()
                in_str = self.entry_in.get() or "0"
                
                weight_lbs = validate_positive_number(w_str, "Weight (lbs)")
                feet = validate_positive_number(ft_str, "Height (Feet)")
                try:
                    inches = float(in_str.strip())
                    if inches < 0:
                        raise ValueError()
                except ValueError:
                    raise ValueError("Inches must be a non-negative number.")

                weight_kg = lbs_to_kg(weight_lbs)
                height_m = feet_inches_to_meters(feet, inches)

            bmi = calculate_bmi(weight_kg, height_m)
            category, advice, color = classify_bmi(bmi)

            # Update results UI
            self.user_display_lbl.config(text=f"User: {user_name}")
            self.bmi_display_lbl.config(text=f"{bmi:.2f}", fg=color)
            self.category_badge.config(text=category, bg=color, fg="#11111b")
            self.advice_text.config(text=advice)
            self._draw_gauge(current_bmi=bmi)

            # Save to SQLite with error handling
            if self.db:
                try:
                    self.db.add_record(weight_kg, height_m, bmi, category, user_name=user_name)
                except DatabaseError as dberr:
                    messagebox.showerror("Database Write Error", f"Failed to save record: {dberr}")

            # Refresh dropdowns and tables
            self._update_user_dropdowns()
            self._refresh_history()
            self._plot_trend_chart()

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
        except Exception as e:
            messagebox.showerror("Calculation Error", f"An unexpected error occurred: {e}")

    def _build_trends_tab(self):
        # Top chart frame, bottom history table
        self.chart_frame = tk.Frame(self.tab_trends, bg="#181825", padx=12, pady=10)
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=(4, 6))

        self.table_frame = tk.Frame(self.tab_trends, bg="#181825", padx=12, pady=8)
        self.table_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=(4, 4))

        # Table controls: Filter by User + Clear
        tbl_ctrl = tk.Frame(self.table_frame, bg="#181825")
        tbl_ctrl.pack(fill=tk.X, pady=(0, 6))

        tk.Label(tbl_ctrl, text="Filter by User:", font=("Segoe UI", 9, "bold"), fg="#a6adc8", bg="#181825").pack(side=tk.LEFT, padx=(0, 6))

        filter_options = ["All Users"] + self._get_user_list()
        self.filter_combo = ttk.Combobox(
            tbl_ctrl,
            textvariable=self.filter_user,
            values=filter_options,
            state="readonly",
            width=18,
            font=("Segoe UI", 9)
        )
        self.filter_combo.pack(side=tk.LEFT, padx=(0, 16))
        self.filter_combo.bind("<<ComboboxSelected>>", lambda e: self._on_filter_changed())

        btn_clear = tk.Button(
            tbl_ctrl,
            text="Clear Filtered Records",
            font=("Segoe UI", 8, "bold"),
            bg="#f38ba8",
            fg="#11111b",
            bd=0,
            padx=8,
            pady=2,
            relief=tk.FLAT,
            cursor="hand2",
            command=self._clear_selected_records
        )
        btn_clear.pack(side=tk.RIGHT)

        # Treeview table
        columns = ("id", "user", "timestamp", "weight", "height", "bmi", "category")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", height=5)
        self.tree.heading("id", text="#")
        self.tree.heading("user", text="User")
        self.tree.heading("timestamp", text="Date & Time")
        self.tree.heading("weight", text="Weight (kg)")
        self.tree.heading("height", text="Height (m)")
        self.tree.heading("bmi", text="BMI")
        self.tree.heading("category", text="Category")

        self.tree.column("id", width=35, anchor=tk.CENTER)
        self.tree.column("user", width=120, anchor=tk.W)
        self.tree.column("timestamp", width=135, anchor=tk.CENTER)
        self.tree.column("weight", width=85, anchor=tk.CENTER)
        self.tree.column("height", width=85, anchor=tk.CENTER)
        self.tree.column("bmi", width=75, anchor=tk.CENTER)
        self.tree.column("category", width=110, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self._refresh_history()
        self._plot_trend_chart()

    def _on_filter_changed(self):
        self._refresh_history()
        self._plot_trend_chart()

    def _update_user_dropdowns(self):
        users = self._get_user_list()
        if hasattr(self, "user_combo"):
            self.user_combo["values"] = users
        if hasattr(self, "filter_combo"):
            self.filter_combo["values"] = ["All Users"] + users

    def _refresh_history(self):
        if not hasattr(self, "tree") or not self.db:
            return
        for row in self.tree.get_children():
            self.tree.delete(row)

        target_user = self.filter_user.get()
        try:
            records = self.db.get_all_records(user_name=target_user, limit=100)
            for r in records:
                self.tree.insert("", tk.END, values=(
                    r["id"],
                    r.get("user_name", "Default User"),
                    r["timestamp"],
                    f"{r['weight_kg']:.1f}",
                    f"{r['height_m']:.2f}",
                    f"{r['bmi']:.2f}",
                    r["category"]
                ))
        except DatabaseError as e:
            messagebox.showerror("Database Read Error", f"Failed to load records: {e}")

    def _plot_trend_chart(self):
        """Renders an embedded Matplotlib trend line chart filtered by user."""
        if not hasattr(self, "chart_frame") or not self.db:
            return

        for w in self.chart_frame.winfo_children():
            w.destroy()

        target_user = self.filter_user.get()
        try:
            records = self.db.get_chronological_records(user_name=target_user, limit=30)
        except DatabaseError as e:
            tk.Label(self.chart_frame, text=f"Failed to read database records: {e}", fg="#f38ba8", bg="#181825").pack()
            return
        
        try:
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

            fig = Figure(figsize=(6.5, 2.8), dpi=90, facecolor="#181825")
            ax = fig.add_subplot(111)
            ax.set_facecolor("#1e1e2e")

            # Reference bands
            ax.axhspan(10, 18.5, color="#89b4fa", alpha=0.15, label="Underweight (<18.5)")
            ax.axhspan(18.5, 25.0, color="#a6e3a1", alpha=0.20, label="Normal (18.5-24.9)")
            ax.axhspan(25.0, 30.0, color="#fab387", alpha=0.15, label="Overweight (25-29.9)")
            ax.axhspan(30.0, 50.0, color="#f38ba8", alpha=0.15, label="Obese (≥30)")

            user_label = target_user if target_user != "All Users" else "All Users"
            if len(records) > 0:
                indices = list(range(1, len(records) + 1))
                bmis = [r["bmi"] for r in records]
                ax.plot(indices, bmis, marker="o", color="#cdd6f4", linewidth=2.2, markersize=5, label=f"{user_label} BMI")
                ax.set_xticks(indices)
                ax.set_xlabel("Measurement Entry #", color="#a6adc8", fontsize=8)
            else:
                ax.text(0.5, 0.5, f"No measurements recorded for '{user_label}'.\nCalculate a BMI to begin viewing trends!", color="#6c7086", ha="center", va="center", transform=ax.transAxes, fontsize=10)

            ax.set_title(f"BMI Progression Trend ({user_label})", color="#cdd6f4", fontsize=9, fontweight="bold")
            ax.set_ylabel("BMI Value", color="#a6adc8", fontsize=8)
            ax.set_ylim(14, 38)
            ax.tick_params(colors="#a6adc8", labelsize=8)
            for spine in ax.spines.values():
                spine.set_color("#313244")

            ax.legend(loc="upper right", facecolor="#181825", edgecolor="#313244", labelcolor="#cdd6f4", fontsize=7)
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        except Exception as err:
            tk.Label(self.chart_frame, text=f"Trend Chart Preview Unavailable: {err}", fg="#a6adc8", bg="#181825").pack()

    def _clear_selected_records(self):
        target = self.filter_user.get()
        prompt = f"Are you sure you want to clear records for '{target}'?" if target != "All Users" else "Are you sure you want to clear ALL historical records for all users?"
        if messagebox.askyesno("Confirm Clear", prompt):
            try:
                self.db.clear_history(user_name=target)
                self._update_user_dropdowns()
                self._refresh_history()
                self._plot_trend_chart()
            except DatabaseError as e:
                messagebox.showerror("Database Error", f"Failed to clear records: {e}")

def launch_gui(show_splash: bool = True, db_path: Optional[str] = None):
    root = tk.Tk()
    app = BMICalculatorGUI(root, show_splash=show_splash, db_path=db_path)
    root.mainloop()

if __name__ == "__main__":
    launch_gui()