import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import math
import pytz
import threading
import time as time_module
import os

# ─── Cross-platform beep ───────────────────────────────────────────────────────
import os

def beep_alarm():
    """Play macOS alarm sound."""
    try:
        for _ in range(3):
            os.system("afplay /System/Library/Sounds/Glass.aiff")
            time_module.sleep(0.2)
    except Exception:
        print("\a")


# ─── All Timezones ─────────────────────────────────────────────────────────────
ALL_TIMEZONES = sorted(pytz.all_timezones)

# ─── Theme Definitions ─────────────────────────────────────────────────────────
THEMES = {
    "dark": {
        "bg":           "#0d0d0d",
        "panel":        "#1a1a1a",
        "border":       "#2e2e2e",
        "text":         "#ffffff",
        "subtext":      "#aaaaaa",
        "accent":       "#00e5ff",
        "accent2":      "#ff4c4c",
        "digital_time": "#00ff88",
        "hand_hour":    "#ffffff",
        "hand_min":     "#cccccc",
        "hand_sec":     "#ff4c4c",
        "tick":         "#444444",
        "tick_hour":    "#888888",
        "number":       "#cccccc",
        "clock_face":   "#111111",
        "clock_border": "#00e5ff",
        "center_dot":   "#ff4c4c",
        "btn_bg":       "#1f1f1f",
        "btn_fg":       "#ffffff",
        "btn_active":   "#00e5ff",
        "entry_bg":     "#1f1f1f",
        "entry_fg":     "#ffffff",
        "listbox_bg":   "#141414",
        "listbox_fg":   "#cccccc",
        "listbox_sel":  "#00e5ff",
        "alarm_active": "#00ff88",
        "alarm_off":    "#555555",
    },
    "light": {
        "bg":           "#f0f0f0",
        "panel":        "#ffffff",
        "border":       "#dddddd",
        "text":         "#111111",
        "subtext":      "#555555",
        "accent":       "#0077cc",
        "accent2":      "#cc2200",
        "digital_time": "#007744",
        "hand_hour":    "#111111",
        "hand_min":     "#333333",
        "hand_sec":     "#cc2200",
        "tick":         "#cccccc",
        "tick_hour":    "#888888",
        "number":       "#333333",
        "clock_face":   "#ffffff",
        "clock_border": "#0077cc",
        "center_dot":   "#cc2200",
        "btn_bg":       "#e8e8e8",
        "btn_fg":       "#111111",
        "btn_active":   "#0077cc",
        "entry_bg":     "#ffffff",
        "entry_fg":     "#111111",
        "listbox_bg":   "#f8f8f8",
        "listbox_fg":   "#333333",
        "listbox_sel":  "#0077cc",
        "alarm_active": "#007744",
        "alarm_off":    "#aaaaaa",
    }
}

current_theme = "dark"


def T():
    return THEMES[current_theme]


# ─── State ─────────────────────────────────────────────────────────────────────
alarms = []          # list of {"time": "HH:MM", "enabled": BooleanVar}
alarm_triggered = set()   # tracks already-fired alarms this minute


# ══════════════════════════════════════════════════════════════════════════════
#  CLOCK DRAWING
# ══════════════════════════════════════════════════════════════════════════════
def draw_clock(canvas, now, size=280):
    canvas.delete("all")
    cx = cy = size // 2
    r = size // 2 - 10
    th = T()

    # Clock face
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                       fill=th["clock_face"], outline=th["clock_border"], width=3)

    # Tick marks
    for i in range(60):
        angle = math.radians(i * 6)
        if i % 5 == 0:
            r1, r2, w, color = r - 18, r - 4, 2, th["tick_hour"]
        else:
            r1, r2, w, color = r - 8, r - 4, 1, th["tick"]
        x1 = cx + math.sin(angle) * r1
        y1 = cy - math.cos(angle) * r1
        x2 = cx + math.sin(angle) * r2
        y2 = cy - math.cos(angle) * r2
        canvas.create_line(x1, y1, x2, y2, fill=color, width=w)

    # Hour numbers
    for i in range(1, 13):
        angle = math.radians(i * 30)
        x = cx + math.sin(angle) * (r - 28)
        y = cy - math.cos(angle) * (r - 28)
        canvas.create_text(x, y, text=str(i), fill=th["number"],
                           font=("Courier", 10, "bold"))

    sec    = now.second
    minute = now.minute
    hour   = now.hour % 12

    sec_angle  = math.radians(sec * 6)
    min_angle  = math.radians(minute * 6 + sec * 0.1)
    hour_angle = math.radians(hour * 30 + minute * 0.5)

    # Hour hand
    canvas.create_line(cx, cy,
                       cx + math.sin(hour_angle) * (r * 0.5),
                       cy - math.cos(hour_angle) * (r * 0.5),
                       fill=th["hand_hour"], width=6, capstyle=tk.ROUND)

    # Minute hand
    canvas.create_line(cx, cy,
                       cx + math.sin(min_angle) * (r * 0.75),
                       cy - math.cos(min_angle) * (r * 0.75),
                       fill=th["hand_min"], width=4, capstyle=tk.ROUND)

    # Second hand (with tail)
    canvas.create_line(cx - math.sin(sec_angle) * 20,
                       cy + math.cos(sec_angle) * 20,
                       cx + math.sin(sec_angle) * (r * 0.88),
                       cy - math.cos(sec_angle) * (r * 0.88),
                       fill=th["hand_sec"], width=1)

    # Center dot
    canvas.create_oval(cx - 6, cy - 6, cx + 6, cy + 6,
                       fill=th["center_dot"], outline=th["hand_hour"], width=1)


# ══════════════════════════════════════════════════════════════════════════════
#  ALARM CHECK
# ══════════════════════════════════════════════════════════════════════════════
def check_alarms(now_str_hhmm):
    for alarm in alarms:
        if alarm["enabled"].get() and alarm["time"] == now_str_hhmm:
            key = alarm["time"]
            if key not in alarm_triggered:
                alarm_triggered.add(key)
                threading.Thread(target=beep_alarm, daemon=True).start()
                messagebox.showinfo("⏰ Alarm", f"Alarm ringing: {alarm['time']}!")
        else:
            # Reset trigger when minute passes
            alarm_triggered.discard(alarm["time"])


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN APP CLASS
# ══════════════════════════════════════════════════════════════════════════════
class ClockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Clock")
        self.root.resizable(False, False)

        self.selected_tz = tk.StringVar(value="Asia/Kolkata")
        self.search_var  = tk.StringVar()
        self.search_var.trace("w", self.filter_timezones)

        self._build_ui()
        self._apply_theme()
        self.update_clock()

    # ── UI CONSTRUCTION ────────────────────────────────────────────────────
    def _build_ui(self):
        root = self.root

        # ── Top bar ───────────────────────────────────────────────────────
        self.top_bar = tk.Frame(root, pady=6)
        self.top_bar.pack(fill="x", padx=12)

        self.title_lbl = tk.Label(self.top_bar, text="🕐  ADVANCED CLOCK",
                                  font=("Courier", 13, "bold"))
        self.title_lbl.pack(side="left")

        self.theme_btn = tk.Button(self.top_bar, text="☀  Light Mode",
                                   font=("Courier", 9), relief="flat", bd=0,
                                   padx=10, pady=4, cursor="hand2",
                                   command=self.toggle_theme)
        self.theme_btn.pack(side="right")

        # ── Main layout (left clock | right panels) ───────────────────────
        self.main = tk.Frame(root)
        self.main.pack(padx=12, pady=6)

        # Left: clock display
        self.left = tk.Frame(self.main)
        self.left.grid(row=0, column=0, padx=(0, 12))

        self.time_lbl = tk.Label(self.left, text="00:00:00 AM",
                                  font=("Courier", 36, "bold"))
        self.time_lbl.pack()

        self.day_lbl = tk.Label(self.left, text="Monday",
                                 font=("Courier", 14))
        self.day_lbl.pack()

        self.date_lbl = tk.Label(self.left, text="January 01, 2024",
                                  font=("Courier", 12))
        self.date_lbl.pack(pady=(0, 6))

        self.canvas = tk.Canvas(self.left, width=280, height=280,
                                highlightthickness=0)
        self.canvas.pack()

        self.tz_lbl = tk.Label(self.left, text="Asia/Kolkata",
                                font=("Courier", 9))
        self.tz_lbl.pack(pady=(4, 0))

        # Right: panels
        self.right = tk.Frame(self.main)
        self.right.grid(row=0, column=1, sticky="n")

        self._build_timezone_panel()
        self._build_alarm_panel()

        # ── Status bar ────────────────────────────────────────────────────
        self.status = tk.Label(root, text="Ready", font=("Courier", 8),
                               anchor="w", pady=3)
        self.status.pack(fill="x", padx=12, pady=(2, 6))

    def _build_timezone_panel(self):
        th = T()
        self.tz_panel = tk.LabelFrame(self.right, text=" 🌍 Timezone ",
                                       font=("Courier", 10, "bold"),
                                       padx=8, pady=8)
        self.tz_panel.pack(fill="x", pady=(0, 10))

        # Search box
        self.search_entry = tk.Entry(self.tz_panel, textvariable=self.search_var,
                                     font=("Courier", 10), width=26, relief="flat",
                                     bd=2)
        self.search_entry.pack(fill="x", pady=(0, 4))
        self._add_placeholder(self.search_entry, "🔍 Search timezone...")

        # Listbox + scrollbar
        lb_frame = tk.Frame(self.tz_panel)
        lb_frame.pack(fill="both")

        self.tz_listbox = tk.Listbox(lb_frame, height=7, font=("Courier", 9),
                                     relief="flat", bd=0, selectborderwidth=0,
                                     activestyle="none", width=26,
                                     exportselection=False)
        self.tz_listbox.pack(side="left", fill="both", expand=True)

        sb = tk.Scrollbar(lb_frame, command=self.tz_listbox.yview)
        sb.pack(side="right", fill="y")
        self.tz_listbox.config(yscrollcommand=sb.set)

        self._populate_listbox(ALL_TIMEZONES)

        # Select current tz
        self.tz_listbox.bind("<<ListboxSelect>>", self.on_tz_select)
        self._scroll_to_tz("Asia/Kolkata")

        # Current label
        self.current_tz_lbl = tk.Label(self.tz_panel,
                                        text="Current: Asia/Kolkata",
                                        font=("Courier", 8))
        self.current_tz_lbl.pack(anchor="w", pady=(4, 0))

    def _build_alarm_panel(self):
        self.alarm_panel = tk.LabelFrame(self.right, text=" ⏰ Alarms ",
                                          font=("Courier", 10, "bold"),
                                          padx=8, pady=8)
        self.alarm_panel.pack(fill="both", expand=True)

        # Add alarm row
        add_row = tk.Frame(self.alarm_panel)
        add_row.pack(fill="x", pady=(0, 6))

        self.alarm_hour_var = tk.StringVar(value="07")
        self.alarm_min_var  = tk.StringVar(value="00")

        tk.Label(add_row, text="HH", font=("Courier", 8)).grid(row=0, column=0)
        tk.Label(add_row, text="MM", font=("Courier", 8)).grid(row=0, column=2)

        self.h_spin = tk.Spinbox(add_row, from_=0, to=23, width=3,
                                  textvariable=self.alarm_hour_var,
                                  format="%02.0f", font=("Courier", 12),
                                  relief="flat", bd=2)
        self.h_spin.grid(row=1, column=0, padx=(0, 2))

        tk.Label(add_row, text=":", font=("Courier", 14, "bold")).grid(row=1, column=1)

        self.m_spin = tk.Spinbox(add_row, from_=0, to=59, width=3,
                                  textvariable=self.alarm_min_var,
                                  format="%02.0f", font=("Courier", 12),
                                  relief="flat", bd=2)
        self.m_spin.grid(row=1, column=2, padx=(2, 8))

        self.add_alarm_btn = tk.Button(add_row, text="+ Add",
                                        font=("Courier", 9, "bold"),
                                        relief="flat", padx=8, pady=4,
                                        cursor="hand2",
                                        command=self.add_alarm)
        self.add_alarm_btn.grid(row=1, column=3)

        # Alarm list frame (scrollable)
        self.alarm_list_frame = tk.Frame(self.alarm_panel)
        self.alarm_list_frame.pack(fill="both", expand=True)

        self.no_alarm_lbl = tk.Label(self.alarm_list_frame,
                                      text="No alarms set.",
                                      font=("Courier", 9), pady=8)
        self.no_alarm_lbl.pack()

    # ── TIMEZONE LOGIC ─────────────────────────────────────────────────────
    def filter_timezones(self, *_):
        query = self.search_var.get().strip().lower()
        if query in ("", "🔍 search timezone..."):
            filtered = ALL_TIMEZONES
        else:
            filtered = [tz for tz in ALL_TIMEZONES if query in tz.lower()]
        self._populate_listbox(filtered)

    def _populate_listbox(self, tzlist):
        self.tz_listbox.delete(0, "end")
        for tz in tzlist:
            self.tz_listbox.insert("end", tz)
        self._apply_listbox_theme()

    def on_tz_select(self, _=None):
        sel = self.tz_listbox.curselection()
        if not sel:
            return
        tz = self.tz_listbox.get(sel[0])
        self.selected_tz.set(tz)
        self.tz_lbl.config(text=tz)
        self.current_tz_lbl.config(text=f"Current: {tz}")
        self.status.config(text=f"Timezone changed to {tz}")

    def _scroll_to_tz(self, tz):
        try:
            idx = ALL_TIMEZONES.index(tz)
            self.tz_listbox.selection_clear(0, "end")
            self.tz_listbox.selection_set(idx)
            self.tz_listbox.see(idx)
        except ValueError:
            pass

    def _add_placeholder(self, entry, text):
        entry.insert(0, text)
        entry.config(fg="#888888")

        def on_focus_in(e):
            if entry.get() == text:
                entry.delete(0, "end")
                entry.config(fg=T()["entry_fg"])

        def on_focus_out(e):
            if not entry.get():
                entry.insert(0, text)
                entry.config(fg="#888888")

        entry.bind("<FocusIn>",  on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    # ── ALARM LOGIC ────────────────────────────────────────────────────────
    def add_alarm(self):
        try:
            hh = int(self.alarm_hour_var.get())
            mm = int(self.alarm_min_var.get())
            if not (0 <= hh <= 23 and 0 <= mm <= 59):
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid", "Enter a valid time (HH: 0-23, MM: 0-59)")
            return

        alarm_time = f"{hh:02d}:{mm:02d}"

        # Duplicate check
        for a in alarms:
            if a["time"] == alarm_time:
                messagebox.showinfo("Duplicate", f"Alarm {alarm_time} already exists.")
                return

        enabled_var = tk.BooleanVar(value=True)
        alarms.append({"time": alarm_time, "enabled": enabled_var})
        self._rebuild_alarm_list()
        self.status.config(text=f"Alarm set for {alarm_time}")

    def remove_alarm(self, alarm_time):
        global alarms
        alarms = [a for a in alarms if a["time"] != alarm_time]
        alarm_triggered.discard(alarm_time)
        self._rebuild_alarm_list()
        self.status.config(text=f"Alarm {alarm_time} removed")

    def _rebuild_alarm_list(self):
        for w in self.alarm_list_frame.winfo_children():
            w.destroy()

        if not alarms:
            self.no_alarm_lbl = tk.Label(self.alarm_list_frame,
                                          text="No alarms set.",
                                          font=("Courier", 9), pady=8,
                                          bg=T()["panel"], fg=T()["subtext"])
            self.no_alarm_lbl.pack()
            return

        for alarm in sorted(alarms, key=lambda x: x["time"]):
            self._build_alarm_row(alarm)

    def _build_alarm_row(self, alarm):
        th = T()
        row = tk.Frame(self.alarm_list_frame, bg=th["panel"], pady=3)
        row.pack(fill="x", pady=2)

        # Toggle switch (checkbutton styled)
        toggle = tk.Checkbutton(row, variable=alarm["enabled"],
                                 font=("Courier", 9),
                                 bg=th["panel"], fg=th["alarm_active"],
                                 selectcolor=th["panel"],
                                 activebackground=th["panel"],
                                 relief="flat", bd=0, cursor="hand2")
        toggle.pack(side="left")

        lbl_color = th["alarm_active"] if alarm["enabled"].get() else th["alarm_off"]
        time_lbl = tk.Label(row, text=f"⏰  {alarm['time']}",
                             font=("Courier", 13, "bold"),
                             bg=th["panel"], fg=lbl_color)
        time_lbl.pack(side="left", padx=6)

        del_btn = tk.Button(row, text="✕", font=("Courier", 9),
                             bg=th["panel"], fg=th["accent2"],
                             activebackground=th["panel"],
                             activeforeground="#ff0000",
                             relief="flat", bd=0, cursor="hand2",
                             command=lambda t=alarm["time"]: self.remove_alarm(t))
        del_btn.pack(side="right", padx=4)

    # ── THEME ──────────────────────────────────────────────────────────────
    def toggle_theme(self):
        global current_theme
        current_theme = "light" if current_theme == "dark" else "dark"
        self._apply_theme()
        icon = "🌙  Dark Mode" if current_theme == "light" else "☀  Light Mode"
        self.theme_btn.config(text=icon)

    def _apply_theme(self):
        th = T()
        self.root.configure(bg=th["bg"])

        def style_frame(w):
            try:    w.configure(bg=th["bg"])
            except: pass
            for child in w.winfo_children():
                style_frame(child)

        style_frame(self.root)

        # Specific overrides
        self.top_bar.config(bg=th["panel"])
        self.title_lbl.config(bg=th["panel"], fg=th["accent"])
        self.theme_btn.config(bg=th["btn_bg"], fg=th["btn_fg"],
                               activebackground=th["accent"],
                               activeforeground=th["bg"])

        self.left.config(bg=th["bg"])
        self.time_lbl.config(bg=th["bg"], fg=th["digital_time"])
        self.day_lbl.config(bg=th["bg"],  fg=th["text"])
        self.date_lbl.config(bg=th["bg"], fg=th["subtext"])
        self.tz_lbl.config(bg=th["bg"],   fg=th["subtext"])

        self.canvas.config(bg=th["bg"])

        self.right.config(bg=th["bg"])
        self.tz_panel.config(bg=th["panel"], fg=th["accent"])
        self.alarm_panel.config(bg=th["panel"], fg=th["accent"])

        self.search_entry.config(bg=th["entry_bg"], fg=th["entry_fg"],
                                  insertbackground=th["text"])
        self._apply_listbox_theme()

        self.current_tz_lbl.config(bg=th["panel"], fg=th["subtext"])

        self.alarm_list_frame.config(bg=th["panel"])

        self.h_spin.config(bg=th["entry_bg"], fg=th["text"],
                            buttonbackground=th["btn_bg"],
                            insertbackground=th["text"])
        self.m_spin.config(bg=th["entry_bg"], fg=th["text"],
                            buttonbackground=th["btn_bg"],
                            insertbackground=th["text"])

        self.add_alarm_btn.config(bg=th["accent"], fg=th["bg"],
                                   activebackground=th["btn_active"])

        self.status.config(bg=th["border"], fg=th["subtext"])

        self._rebuild_alarm_list()

        # Labels in add_row
        for w in self.root.winfo_children():
            self._deep_style(w, th)

    def _deep_style(self, widget, th):
        try:
            cls = widget.winfo_class()
            if cls == "Label":
                widget.config(bg=widget.master.cget("bg") if widget.master else th["bg"],
                               fg=th["text"])
        except Exception:
            pass
        for child in widget.winfo_children():
            self._deep_style(child, th)

    def _apply_listbox_theme(self):
        th = T()
        self.tz_listbox.config(bg=th["listbox_bg"], fg=th["listbox_fg"],
                                selectbackground=th["listbox_sel"],
                                selectforeground=th["bg"])

    # ── MAIN UPDATE LOOP ───────────────────────────────────────────────────
    def update_clock(self):
        tz_name = self.selected_tz.get()
        try:
            tz  = pytz.timezone(tz_name)
            now = datetime.now(tz)
        except Exception:
            now = datetime.now()

        self.time_lbl.config(text=now.strftime("%I:%M:%S %p"))
        self.day_lbl.config(text=now.strftime("%A"))
        self.date_lbl.config(text=now.strftime("%B %d, %Y"))

        draw_clock(self.canvas, now)
        check_alarms(now.strftime("%H:%M"))

        self.root.after(1000, self.update_clock)


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    root = tk.Tk()
    app  = ClockApp(root)
    app._apply_theme()   # initial theme pass
    root.mainloop()