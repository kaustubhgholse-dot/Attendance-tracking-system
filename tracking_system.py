"""
Project 12: Smart Attendance Register (GUI version, Tkinter)
Concepts used: Dictionaries, Nested Loops, Datetime, File I/O, Formatted Output
Uses the same attendance_data.json file as the console version.
"""

import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date

DATA_FILE = "attendance_data.json"
THRESHOLD = 75.0
LEAVE_COUNTS_AS_PRESENT = False   # set True if approved leave counts as attended

# ---------------------------------------------------------------- Theme
BG = "#f3f5f9"          # window background
CARD = "#ffffff"        # panels / cards
NAVY = "#1f3a5f"        # header, table headings
ACCENT = "#2e86de"      # buttons, selected tab
ACCENT_DARK = "#2169b3"
TEXT = "#2d3436"
MUTED = "#7b8794"
STRIPE = "#f0f4fa"      # alternate table row
RISK_BG = "#fdecea"
RISK_FG = "#c0392b"
OK_FG = "#1e8449"
FONT = "Segoe UI"


# ---------------------------------------------------------------- File I/O
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {"students": {}, "attendance": {}}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ---------------------------------------------------------------- Logic
def attended_count(data, roll):
    count = 0
    for record in data["attendance"].values():
        status = record.get(roll)
        if status == "P" or (status == "L" and LEAVE_COUNTS_AS_PRESENT):
            count += 1
    return count


def percentage(data, roll):
    total = len(data["attendance"])
    if total == 0:
        return 0.0
    return attended_count(data, roll) / total * 100


# ---------------------------------------------------------------- Styling
def apply_theme(root):
    style = ttk.Style(root)
    style.theme_use("clam")
    root.configure(bg=BG)

    style.configure(".", background=BG, foreground=TEXT, font=(FONT, 10))
    style.configure("TFrame", background=BG)
    style.configure("Card.TFrame", background=CARD)
    style.configure("TLabel", background=BG, foreground=TEXT)
    style.configure("Card.TLabel", background=CARD, foreground=TEXT)
    style.configure("Title.TLabel", background=BG, font=(FONT, 15, "bold"), foreground=NAVY)
    style.configure("Sub.TLabel", background=BG, foreground=MUTED)
    style.configure("CardTitle.TLabel", background=CARD, foreground=MUTED, font=(FONT, 9))
    style.configure("CardValue.TLabel", background=CARD, foreground=NAVY, font=(FONT, 22, "bold"))
    style.configure("RiskValue.TLabel", background=CARD, foreground=RISK_FG, font=(FONT, 22, "bold"))
    style.configure("Head.TLabel", background=CARD, foreground=NAVY, font=(FONT, 10, "bold"))

    # Notebook tabs
    style.configure("TNotebook", background=BG, borderwidth=0, tabmargins=(0, 4, 0, 0))
    style.configure("TNotebook.Tab", padding=(18, 9), font=(FONT, 10, "bold"),
                    background="#dfe5ee", foreground=MUTED, borderwidth=0)
    style.map("TNotebook.Tab",
              background=[("selected", CARD), ("active", "#eef2f8")],
              foreground=[("selected", ACCENT)])

    # Buttons
    style.configure("Accent.TButton", background=ACCENT, foreground="white",
                    font=(FONT, 10, "bold"), padding=(14, 7), borderwidth=0, focusthickness=0)
    style.map("Accent.TButton", background=[("active", ACCENT_DARK), ("pressed", ACCENT_DARK)])
    style.configure("Soft.TButton", background="#e4eaf3", foreground=NAVY,
                    font=(FONT, 10), padding=(12, 7), borderwidth=0, focusthickness=0)
    style.map("Soft.TButton", background=[("active", "#d3dcea")])

    # Entries
    style.configure("TEntry", fieldbackground="white", bordercolor="#c9d2de",
                    lightcolor="#c9d2de", darkcolor="#c9d2de", padding=6)
    style.map("TEntry", bordercolor=[("focus", ACCENT)], lightcolor=[("focus", ACCENT)],
              darkcolor=[("focus", ACCENT)])

    # Tables
    style.configure("Treeview", background="white", fieldbackground="white", foreground=TEXT,
                    rowheight=28, borderwidth=0, font=(FONT, 10))
    style.configure("Treeview.Heading", background=NAVY, foreground="white",
                    font=(FONT, 10, "bold"), padding=(6, 7), borderwidth=0, relief="flat")
    style.map("Treeview.Heading", background=[("active", NAVY)])
    style.map("Treeview", background=[("selected", "#cfe3f8")], foreground=[("selected", TEXT)])

    # Row styles for the attendance-marking grid
    for name, color in (("RowA", CARD), ("RowB", STRIPE)):
        style.configure(f"{name}.TFrame", background=color)
        style.configure(f"{name}.TLabel", background=color, foreground=TEXT)
        style.configure(f"{name}.TRadiobutton", background=color, focuscolor=color)
    style.configure("Present.TRadiobutton", foreground=OK_FG)
    style.configure("Absent.TRadiobutton", foreground=RISK_FG)

    style.configure("Status.TLabel", background=NAVY, foreground="#c9d6ea",
                    font=(FONT, 9), padding=(12, 5))


# ---------------------------------------------------------------- GUI
class AttendanceApp:
    def __init__(self, root):
        self.root = root
        self.data = load_data()
        root.title("Smart Attendance Register")
        root.geometry("980x640")
        root.minsize(820, 520)
        apply_theme(root)

        self.build_header()
        self.build_status_bar()      # packed at bottom before the notebook so it stays visible

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=14, pady=(10, 8))

        self.tab_register = ttk.Frame(self.notebook, padding=18, style="Card.TFrame")
        self.tab_mark = ttk.Frame(self.notebook, padding=18, style="Card.TFrame")
        self.tab_percent = ttk.Frame(self.notebook, padding=18, style="Card.TFrame")
        self.tab_detention = ttk.Frame(self.notebook, padding=18, style="Card.TFrame")
        self.tab_monthly = ttk.Frame(self.notebook, padding=18, style="Card.TFrame")

        self.notebook.add(self.tab_register, text="  Students  ")
        self.notebook.add(self.tab_mark, text="  Mark Attendance  ")
        self.notebook.add(self.tab_percent, text="  Percentages  ")
        self.notebook.add(self.tab_detention, text="  Detention List  ")
        self.notebook.add(self.tab_monthly, text="  Monthly Report  ")

        self.build_register_tab()
        self.build_mark_tab()
        self.build_percent_tab()
        self.build_detention_tab()
        self.build_monthly_tab()

        self.notebook.bind("<<NotebookTabChanged>>", lambda e: self.refresh_all())
        self.refresh_all()
        self.set_status("Ready")

    # ---------- shared pieces
    def build_header(self):
        header = tk.Frame(self.root, bg=NAVY)
        header.pack(fill="x")
        left = tk.Frame(header, bg=NAVY)
        left.pack(side="left", padx=20, pady=14)
        tk.Label(left, text="Smart Attendance Register", bg=NAVY, fg="white",
                 font=(FONT, 18, "bold")).pack(anchor="w")
        tk.Label(left, text="Track daily attendance and spot students at risk of detention",
                 bg=NAVY, fg="#a9bad3", font=(FONT, 10)).pack(anchor="w")
        tk.Label(header, text=date.today().strftime("%A\n%d %B %Y"), bg=NAVY, fg="#dbe5f4",
                 font=(FONT, 10), justify="right").pack(side="right", padx=20)

    def build_status_bar(self):
        self.status_var = tk.StringVar()
        ttk.Label(self.root, textvariable=self.status_var, style="Status.TLabel",
                  anchor="w").pack(side="bottom", fill="x")

    def set_status(self, text):
        self.status_var.set(text)

    @staticmethod
    def page_title(parent, title, subtitle):
        ttk.Label(parent, text=title, style="Title.TLabel", background=CARD).pack(anchor="w")
        ttk.Label(parent, text=subtitle, style="Sub.TLabel", background=CARD).pack(anchor="w", pady=(0, 12))

    @staticmethod
    def make_tree(parent, columns, widths, anchors=None, horizontal=False):
        frame = ttk.Frame(parent, style="Card.TFrame")
        tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
        for i, (col, w) in enumerate(zip(columns, widths)):
            tree.heading(col, text=col)
            anchor = anchors[i] if anchors else "center"
            tree.column(col, width=w, anchor=anchor, minwidth=30, stretch=not horizontal)
        vscroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vscroll.set)
        if horizontal:
            hscroll = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
            tree.configure(xscrollcommand=hscroll.set)
            hscroll.pack(side="bottom", fill="x")
        vscroll.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)
        tree.tag_configure("even", background="white")
        tree.tag_configure("odd", background=STRIPE)
        tree.tag_configure("risk", background=RISK_BG, foreground=RISK_FG)
        return frame, tree

    @staticmethod
    def zebra(index):
        return "even" if index % 2 == 0 else "odd"

    def stat_card(self, parent, title, value_style="CardValue.TLabel"):
        card = tk.Frame(parent, bg=CARD, highlightbackground="#dbe2ec", highlightthickness=1)
        inner = ttk.Frame(card, style="Card.TFrame", padding=(16, 10))
        inner.pack(fill="both", expand=True)
        ttk.Label(inner, text=title.upper(), style="CardTitle.TLabel").pack(anchor="w")
        value = ttk.Label(inner, text="0", style=value_style)
        value.pack(anchor="w")
        return card, value

    def refresh_all(self):
        self.refresh_students()
        self.refresh_percent()
        self.refresh_detention()

    # ---------- Tab 1: students
    def build_register_tab(self):
        t = self.tab_register
        self.page_title(t, "Students", "Register each student with a roll number and name.")
        form = ttk.Frame(t, style="Card.TFrame")
        form.pack(anchor="w", pady=(0, 14))
        ttk.Label(form, text="Roll number", style="Card.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 8))
        ttk.Label(form, text="Name", style="Card.TLabel").grid(row=0, column=1, sticky="w", padx=(0, 8))
        self.roll_var = tk.StringVar()
        self.name_var = tk.StringVar()
        roll_entry = ttk.Entry(form, textvariable=self.roll_var, width=14)
        roll_entry.grid(row=1, column=0, padx=(0, 8), pady=(2, 0))
        name_entry = ttk.Entry(form, textvariable=self.name_var, width=32)
        name_entry.grid(row=1, column=1, padx=(0, 12), pady=(2, 0))
        roll_entry.bind("<Return>", lambda e: name_entry.focus_set())
        name_entry.bind("<Return>", lambda e: self.register_student())
        ttk.Button(form, text="+  Add student", style="Accent.TButton",
                   command=self.register_student).grid(row=1, column=2, pady=(2, 0))
        self.roll_entry = roll_entry

        frame, self.student_tree = self.make_tree(t, ("Roll", "Name"), (140, 520), anchors=("center", "w"))
        frame.pack(fill="both", expand=True)

    def register_student(self):
        roll = self.roll_var.get().strip()
        name = self.name_var.get().strip()
        if not roll or not name:
            messagebox.showwarning("Missing details", "Enter both roll number and name.")
            return
        if roll in self.data["students"]:
            messagebox.showerror("Duplicate", f"Roll {roll} is already registered.")
            return
        self.data["students"][roll] = name
        save_data(self.data)
        self.roll_var.set("")
        self.name_var.set("")
        self.roll_entry.focus_set()
        self.refresh_all()
        self.build_mark_rows()
        self.set_status(f"Registered {name} (Roll {roll})")

    def refresh_students(self):
        self.student_tree.delete(*self.student_tree.get_children())
        for i, roll in enumerate(sorted(self.data["students"])):
            self.student_tree.insert("", "end", tags=(self.zebra(i),),
                                     values=(roll, self.data["students"][roll]))

    # ---------- Tab 2: mark attendance
    def build_mark_tab(self):
        t = self.tab_mark
        self.page_title(t, "Mark Attendance", "Choose a status for every student, then save the day.")
        top = ttk.Frame(t, style="Card.TFrame")
        top.pack(fill="x", pady=(0, 10))
        ttk.Label(top, text="Date (YYYY-MM-DD)", style="Card.TLabel").pack(side="left", padx=(0, 8))
        self.date_var = tk.StringVar(value=date.today().isoformat())
        ttk.Entry(top, textvariable=self.date_var, width=13).pack(side="left", padx=(0, 6))
        ttk.Button(top, text="Today", style="Soft.TButton",
                   command=lambda: self.date_var.set(date.today().isoformat())).pack(side="left", padx=3)
        ttk.Button(top, text="All Present", style="Soft.TButton",
                   command=lambda: self.set_all("P")).pack(side="left", padx=3)
        ttk.Button(top, text="Save attendance", style="Accent.TButton",
                   command=self.save_attendance).pack(side="right")
        self.summary_var = tk.StringVar()
        ttk.Label(top, textvariable=self.summary_var, style="Card.TLabel",
                  foreground=MUTED).pack(side="right", padx=16)

        # Scrollable grid of students
        holder = tk.Frame(t, bg="#dbe2ec", highlightthickness=0)
        holder.pack(fill="both", expand=True)
        self.mark_canvas = tk.Canvas(holder, highlightthickness=0, bg=CARD)
        scroll = ttk.Scrollbar(holder, orient="vertical", command=self.mark_canvas.yview)
        self.mark_canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.mark_canvas.pack(side="left", fill="both", expand=True, padx=1, pady=1)
        self.mark_inner = ttk.Frame(self.mark_canvas, style="Card.TFrame")
        self.mark_window = self.mark_canvas.create_window((0, 0), window=self.mark_inner, anchor="nw")
        self.mark_inner.bind("<Configure>", lambda e: self.mark_canvas.configure(
            scrollregion=self.mark_canvas.bbox("all")))
        self.mark_canvas.bind("<Configure>", lambda e: self.mark_canvas.itemconfigure(
            self.mark_window, width=e.width))
        self.mark_canvas.bind("<Enter>", lambda e: self.mark_canvas.bind_all("<MouseWheel>", self.on_wheel))
        self.mark_canvas.bind("<Leave>", lambda e: self.mark_canvas.unbind_all("<MouseWheel>"))

        self.mark_vars = {}
        self.build_mark_rows()

    def on_wheel(self, event):
        self.mark_canvas.yview_scroll(int(-event.delta / 120), "units")

    def build_mark_rows(self):
        for child in self.mark_inner.winfo_children():
            child.destroy()
        self.mark_vars = {}
        inner = self.mark_inner
        if not self.data["students"]:
            ttk.Label(inner, text="No students registered yet. Add some in the Students tab.",
                      style="Card.TLabel", foreground=MUTED, padding=20).pack()
            self.summary_var.set("")
            return

        head = ttk.Frame(inner, style="Card.TFrame")
        head.pack(fill="x")
        for col, (text, w) in enumerate((("Roll", 10), ("Name", 28), ("Present", 10), ("Absent", 10), ("Leave", 10))):
            ttk.Label(head, text=text, style="Head.TLabel", width=w,
                      padding=(14, 8)).grid(row=0, column=col, sticky="w")

        for i, roll in enumerate(sorted(self.data["students"])):      # loop over students
            tone = "RowA" if i % 2 == 0 else "RowB"
            row = ttk.Frame(inner, style=f"{tone}.TFrame")
            row.pack(fill="x")
            var = tk.StringVar(value="P")
            var.trace_add("write", lambda *a: self.update_summary())
            self.mark_vars[roll] = var
            ttk.Label(row, text=roll, style=f"{tone}.TLabel", width=10, padding=(14, 6)).grid(row=0, column=0, sticky="w")
            ttk.Label(row, text=self.data["students"][roll], style=f"{tone}.TLabel", width=28,
                      padding=(14, 6)).grid(row=0, column=1, sticky="w")
            for c, code in enumerate(("P", "A", "L"), start=2):
                holder = ttk.Frame(row, style=f"{tone}.TFrame", width=110)
                holder.grid(row=0, column=c, sticky="w", padx=(14, 0))
                ttk.Radiobutton(holder, variable=var, value=code,
                                style=f"{tone}.TRadiobutton").pack(anchor="w", padx=(10, 40))
        self.update_summary()

    def update_summary(self):
        counts = {"P": 0, "A": 0, "L": 0}
        for var in self.mark_vars.values():
            counts[var.get()] = counts.get(var.get(), 0) + 1
        self.summary_var.set(f"Present {counts['P']}   Absent {counts['A']}   Leave {counts['L']}")

    def set_all(self, code):
        for var in self.mark_vars.values():
            var.set(code)

    def save_attendance(self):
        if not self.mark_vars:
            messagebox.showwarning("No students", "Register students first.")
            return
        try:
            d = datetime.strptime(self.date_var.get().strip(), "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Invalid date", "Use the format YYYY-MM-DD.")
            return
        if d > date.today():
            messagebox.showerror("Invalid date", "Cannot mark attendance for a future date.")
            return
        key = d.isoformat()
        if key in self.data["attendance"]:                    # duplicate guard
            messagebox.showerror("Duplicate entry", f"Attendance for {key} is already recorded.")
            return
        self.data["attendance"][key] = {roll: var.get() for roll, var in self.mark_vars.items()}
        save_data(self.data)
        self.refresh_all()
        self.set_status(f"Attendance saved for {key}")
        messagebox.showinfo("Saved", f"Attendance saved for {key}.")

    # ---------- Tab 3: percentages
    def build_percent_tab(self):
        t = self.tab_percent
        self.page_title(t, "Attendance Percentage",
                        f"Students below {THRESHOLD:.0f}% are highlighted in red.")
        cards = ttk.Frame(t, style="Card.TFrame")
        cards.pack(fill="x", pady=(0, 12))
        specs = (("Students", "CardValue.TLabel", "students_val"),
                 ("Days recorded", "CardValue.TLabel", "days_val"),
                 ("Class average", "CardValue.TLabel", "avg_val"),
                 ("At risk", "RiskValue.TLabel", "risk_val"))
        for i, (title, vstyle, attr) in enumerate(specs):
            card, value = self.stat_card(cards, title, vstyle)
            card.grid(row=0, column=i, sticky="ew", padx=(0, 10))
            cards.columnconfigure(i, weight=1)
            setattr(self, attr, value)

        frame, self.percent_tree = self.make_tree(
            t, ("Roll", "Name", "Attended", "Total Days", "Percent"), (90, 280, 110, 110, 110),
            anchors=("center", "w", "center", "center", "center"))
        frame.pack(fill="both", expand=True)

    def refresh_percent(self):
        total = len(self.data["attendance"])
        rolls = sorted(self.data["students"])
        self.percent_tree.delete(*self.percent_tree.get_children())
        pcts = []
        risk = 0
        for i, roll in enumerate(rolls):
            pct = percentage(self.data, roll)
            pcts.append(pct)
            at_risk = total > 0 and pct < THRESHOLD
            risk += at_risk
            self.percent_tree.insert("", "end", tags=("risk" if at_risk else self.zebra(i),), values=(
                roll, self.data["students"][roll], attended_count(self.data, roll), total, f"{pct:.1f}%"))
        self.students_val.config(text=str(len(rolls)))
        self.days_val.config(text=str(total))
        self.avg_val.config(text=f"{sum(pcts) / len(pcts):.0f}%" if pcts else "-")
        self.risk_val.config(text=str(risk))

    # ---------- Tab 4: detention list
    def build_detention_tab(self):
        t = self.tab_detention
        self.page_title(t, "Detention List", f"Students with attendance below {THRESHOLD:.0f}%.")
        self.detention_msg = ttk.Label(t, text="", style="Card.TLabel", foreground=MUTED)
        self.detention_msg.pack(anchor="w", pady=(0, 8))
        frame, self.detention_tree = self.make_tree(
            t, ("Roll", "Name", "Percent", "Needed to reach 75%"), (90, 280, 110, 190),
            anchors=("center", "w", "center", "center"))
        frame.pack(fill="both", expand=True)

    def refresh_detention(self):
        self.detention_tree.delete(*self.detention_tree.get_children())
        total = len(self.data["attendance"])
        if not total:
            self.detention_msg.config(text="No attendance recorded yet.", foreground=MUTED)
            return
        count = 0
        for roll in sorted(self.data["students"]):
            pct = percentage(self.data, roll)
            if pct < THRESHOLD:
                count += 1
                attended = attended_count(self.data, roll)
                # consecutive present days needed so that (attended+x)/(total+x) >= 75%
                need = 0
                while (attended + need) / (total + need) * 100 < THRESHOLD:
                    need += 1
                self.detention_tree.insert("", "end", tags=("risk",), values=(
                    roll, self.data["students"][roll], f"{pct:.1f}%", f"{need} more present day(s)"))
        if count:
            self.detention_msg.config(text=f"{count} student(s) at risk of detention.", foreground=RISK_FG)
        else:
            self.detention_msg.config(text="No students at risk. Everyone is at or above the threshold.",
                                      foreground=OK_FG)

    # ---------- Tab 5: monthly report
    def build_monthly_tab(self):
        t = self.tab_monthly
        self.page_title(t, "Monthly Report", "P = Present   A = Absent   L = Leave   - = not recorded")
        top = ttk.Frame(t, style="Card.TFrame")
        top.pack(fill="x", pady=(0, 10))
        ttk.Label(top, text="Month (YYYY-MM)", style="Card.TLabel").pack(side="left", padx=(0, 8))
        self.month_var = tk.StringVar(value=date.today().strftime("%Y-%m"))
        month_entry = ttk.Entry(top, textvariable=self.month_var, width=10)
        month_entry.pack(side="left", padx=(0, 8))
        month_entry.bind("<Return>", lambda e: self.show_monthly())
        ttk.Button(top, text="Show report", style="Accent.TButton",
                   command=self.show_monthly).pack(side="left")
        self.monthly_holder = ttk.Frame(t, style="Card.TFrame")
        self.monthly_holder.pack(fill="both", expand=True)

    def show_monthly(self):
        text = self.month_var.get().strip()
        try:
            month = datetime.strptime(text, "%Y-%m")
        except ValueError:
            messagebox.showerror("Invalid month", "Use the format YYYY-MM.")
            return
        days = sorted(k for k in self.data["attendance"] if k.startswith(text))
        for child in self.monthly_holder.winfo_children():
            child.destroy()
        if not days:
            ttk.Label(self.monthly_holder, text=f"No attendance recorded for {month.strftime('%B %Y')}.",
                      style="Card.TLabel", foreground=MUTED, padding=20).pack(anchor="w")
            return
        columns = ["Roll", "Name"] + [d[-2:] for d in days] + ["P", "A", "L", "%"]
        widths = [70, 150] + [40] * len(days) + [42, 42, 42, 74]
        anchors = ["center", "w"] + ["center"] * (len(days) + 4)
        frame, tree = self.make_tree(self.monthly_holder, columns, widths, anchors, horizontal=True)
        frame.pack(fill="both", expand=True)

        # Nested loops: students x days
        for i, roll in enumerate(sorted(self.data["students"])):
            counts = {"P": 0, "A": 0, "L": 0}
            cells = []
            for day in days:
                status = self.data["attendance"][day].get(roll, "-")
                if status in counts:
                    counts[status] += 1
                cells.append(status)
            attended = counts["P"] + (counts["L"] if LEAVE_COUNTS_AS_PRESENT else 0)
            pct = attended / len(days) * 100
            tag = "risk" if pct < THRESHOLD else self.zebra(i)
            tree.insert("", "end", tags=(tag,), values=(
                [roll, self.data["students"][roll]] + cells +
                [counts["P"], counts["A"], counts["L"], f"{pct:.1f}%"]))
        self.set_status(f"Showing {month.strftime('%B %Y')} ({len(days)} day(s) recorded)")


def main():
    root = tk.Tk()
    AttendanceApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
