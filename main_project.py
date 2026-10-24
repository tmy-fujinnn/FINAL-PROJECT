import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# colors set
Theme = {
    "BG_LIGHT": "#ecf1f7", "BG_PANEL": "#2c4872", "BG_CARD": "#252a30", 
    "BG_CARD2": "#243348", "BG_BLACK": "#000000",
    "C_BLUE": "#003399", "C_ORANGE": "#e87a2a", "C_GREEN": "#27ae60", 
    "C_RED": "#c0392b", "C_YELLOW": "#f1c40f",
    "TXT": "#e8f0fe", "TXT_SUB": "#8fa8c8", "TXT_MUTED": "#ffffff",
    "SIDEBAR_W": 250
}
# set font
Font = "Segoe UI"

# loading and data cleaning

def loadCleanDataset(filepath):
    df_originalData = pd.read_csv(filepath) # gets the original dataset
    df_cleanedCopy  = df_originalData.copy() # gets a copy of the dataset used for cleaning purposes
    log_lines = []

    def log(msg):
        log_lines.append(msg) # returns error fixes message

    # Fix capitalization and whitespace
    fix_cols = ['City', 'Road_Name', 'Vehicle_Type', 'Accident_Type',
                'Weather_Condition', 'Road_Condition', 'Cause', 'Severity', 'Driver_Gender']
    for col in fix_cols:
        df_cleanedCopy[col] = df_cleanedCopy[col].str.strip().str.title()
    log("Capitalization & Whitespaces - [FIXED]")

    # Fix ñ encoding errors
    df_cleanedCopy['City'] = df_cleanedCopy['City'].replace({
        'Para?Aque': 'Parañaque', 'ParaÃ±Aque': 'Parañaque',
        'Las Pi?As': 'Las Piñas', 'Las PiÃ±As': 'Las Piñas',
    })
    df_cleanedCopy['Road_Name'] = df_cleanedCopy['Road_Name'].replace({
        'Espa?A Blvd': 'España Blvd', 'EspaÃ±A Blvd': 'España Blvd',
    })
    log("Name errors (ñ) - [FIXED]")

    # Convert Date & Time
    df_cleanedCopy['Date'] = pd.to_datetime(df_cleanedCopy['Date'], errors='coerce')
    df_cleanedCopy['Time'] = pd.to_datetime(df_cleanedCopy['Time'], format='%H:%M:%S', errors='coerce')
    df_cleanedCopy['Month'] = df_cleanedCopy['Date'].dt.month
    df_cleanedCopy['Month_Name'] = df_cleanedCopy['Date'].dt.strftime('%b')
    df_cleanedCopy['Hour'] = df_cleanedCopy['Time'].dt.hour
    df_cleanedCopy['Day_Name'] = df_cleanedCopy['Date'].dt.strftime('%A')
    log("Converted Date/Time - [FIXED]")

    # Fill categorical nulls
    for col in ['Severity', 'Road_Condition', 'Cause']:
        df_cleanedCopy[col] = df_cleanedCopy[col].fillna('Unknown')
    log("Fill in null of Categorical Values - [FIXED]")

    # Fill numeric nulls with mean
    m_injury = round(df_cleanedCopy['Injury_Count'].mean(), 2)
    m_age = round(df_cleanedCopy['Driver_Age'].mean(), 2)
    m_dmg = round(df_cleanedCopy['Damage_Cost_PHP'].mean(), 2)
    df_cleanedCopy['Injury_Count'] = df_cleanedCopy['Injury_Count'].fillna(m_injury).astype(int)
    df_cleanedCopy['Driver_Age'] = df_cleanedCopy['Driver_Age'].fillna(m_age).astype(int)
    df_cleanedCopy['Damage_Cost_PHP'] = df_cleanedCopy['Damage_Cost_PHP'].fillna(m_dmg)
    log("Fill in null of Numerical Values (MEAN) - [FIXED]")

    # Remove invalid/negative values
    df_cleanedCopy = df_cleanedCopy[df_cleanedCopy['Damage_Cost_PHP'] >= 0]
    df_cleanedCopy = df_cleanedCopy[df_cleanedCopy['Injury_Count'] >= 0]
    df_cleanedCopy = df_cleanedCopy[
        (df_cleanedCopy['Driver_Age'] >= 16) & (df_cleanedCopy['Driver_Age'] <= 100)
    ]
    log("Removed negative entries and Age Group Parameters - [FIXED]")

    # Remove Duplicates
    df_cleanedCopy = df_cleanedCopy.drop_duplicates().reset_index(drop=True)
    log("Removed duplicated entries - [FIXED]")

    # returns message of what was done
    log(f"\n{'-'*48}")
    log(f"ORIGINAL ROWS : {len(df_originalData)}")
    log(f"CLEANED ROWS  : {len(df_cleanedCopy)}")
    log(f"ROWS REMOVED  : {len(df_originalData) - len(df_cleanedCopy)}")
    log(f"NULLS BEFORE  : {df_originalData.isnull().sum().sum()}")
    log(f"NULLS AFTER   : {df_cleanedCopy.isnull().sum().sum()}")

    return df_originalData, df_cleanedCopy, "\n".join(log_lines) # returns original dataset, cleaned, and errors fixed

# main application and interface

class TrafficApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Metro Manila Traffic Accident Report")
        self.geometry("1160x580")
        self.minsize(1024, 540)
        self.configure(bg=Theme["BG_LIGHT"])
        self.df_originalData = None
        self.df_cleanedCopy = None
        self.clean_log = ""
        self.buildLayout()
        self.navigate("home")

    # main layout

    def buildLayout(self):
        hdr = tk.Frame(self, bg=Theme["C_BLUE"], height=50)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr,
                 text="🚨  Metro Manila Traffic Incident 2025  -  Data Analysis",
                 bg=Theme["C_BLUE"], fg="white",
                 font=(Font, 12, "bold")).pack(side="left", padx=20, pady=14)

        body = tk.Frame(self, bg=Theme["BG_LIGHT"])
        body.pack(fill="both", expand=True)

        self.sidebar = tk.Frame(body, bg=Theme["BG_PANEL"], width=Theme["SIDEBAR_W"])
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self.build_sidebar()

        self.content = tk.Frame(body, bg=Theme["BG_LIGHT"])
        self.content.pack(side="left", fill="both", expand=True)

    # sidebar for navigation
    def build_sidebar(self):
        tk.Label(self.sidebar, text="NAVIGATION",
                 bg=Theme["BG_PANEL"], fg=Theme["TXT_MUTED"],
                 font=(Font, 8, "bold")).pack(anchor="w", padx=18, pady=(20, 6))

        self.side_btns = {}
        pages = [
            ("home", "🏠  HOME"),
            ("load", "🔃  LOAD DATA"),
            ("clean", "🧹  CLEAN DATA"),
            ("cleaned", "✅  CLEANED DATA"),
            ("stats", "📊  STATISTICS & DATA"),
            ("charts", "📈  VISUALIZATION"),
            ("insights", "🚦  INSIGHTS"),
        ]
        for key, label in pages:
            btn = tk.Button(
                self.sidebar, text=label, anchor="w",
                bg=Theme["BG_PANEL"], fg=Theme["TXT"],
                activebackground=Theme["BG_CARD2"], activeforeground=Theme["TXT"],
                relief="flat", bd=0, padx=18, pady=9,
                font=(Font, 12, "bold"), cursor="hand2",
                command=lambda k=key: self.navigate(k)
            )
            btn.pack(fill="x")
            self.side_btns[key] = btn

        # displays no dataset has been uploaded upon starting 
        self.status_display = tk.StringVar(value="No dataset has been loaded.")
        tk.Label(self.sidebar, textvariable=self.status_display,
                 bg=Theme["BG_PANEL"], fg=Theme["TXT_MUTED"],
                 font=(Font, 8), wraplength=180,
                 justify="left").pack(side="bottom", padx=16, pady=14, anchor="w")

    # redirects to specific panels when clicked
    def navigate(self, key):
        for k, btn in self.side_btns.items():
            btn.configure(bg=Theme["BG_CARD2"] if k == key else Theme["BG_PANEL"])
        pages = {
            "home": self.display_home,
            "load": self.load_file,
            "clean": self.display_cleaning,
            "cleaned": self.display_cleanedTable,
            "stats": self.show_stats,
            "charts": self.show_visual,
            "insights": self.show_insights,
        }
        pages[key]()

    def clear(self):
        for w in self.content.winfo_children():
            w.destroy()

    # header
    def header(self, title, subtitle=""):
        tk.Label(self.content, text=title,
                 bg=Theme["BG_LIGHT"], fg=Theme["BG_BLACK"],
                 font=(Font, 14, "bold")).pack(anchor="w", padx=28, pady=(22, 2))
        if subtitle:
            tk.Label(self.content, text=subtitle,
                     bg=Theme["BG_LIGHT"], fg=Theme["BG_PANEL"],
                     font=(Font, 9)).pack(anchor="w", padx=28, pady=(0, 14))

    # displays when the dataset has not been loaded
    def need_data(self):
        if self.df_cleanedCopy is None:
            messagebox.showwarning("Dataset Unknown",
                "🔽 Please load the dataset before proceeding.")
            return True
        return False

    def card(self, parent, **kw):
        return tk.Frame(parent, bg=Theme["BG_CARD"], **kw)

    # scroll feature
    def scrollable(self, parent):
        outer = tk.Frame(parent, bg=Theme["BG_LIGHT"])
        outer.pack(fill="both", expand=True)
        canvas = tk.Canvas(outer, bg=Theme["BG_LIGHT"], highlightthickness=0)
        sb = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=Theme["BG_LIGHT"])
        inner.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.bind("<MouseWheel>",
            lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        return outer, inner

    # Home Page

    def display_home(self):
        self.clear()
        f = tk.Frame(self.content, bg=Theme["BG_LIGHT"])
        f.pack(fill="both", expand=True)
        tk.Label(f, text="🚘", bg=Theme["BG_LIGHT"],
                 font=(Font, 52)).pack(pady=(50, 6))
        tk.Label(f, text="Metro Manila Traffic Incidents 2025",
                 bg=Theme["BG_LIGHT"], fg=Theme["BG_BLACK"],
                 font=(Font, 17, "bold")).pack()
        tk.Label(f, text="A Data Analytics System on Uncleaned Incident Reports",
                 bg=Theme["BG_LIGHT"], fg=Theme["TXT_SUB"],
                 font=(Font, 9)).pack(pady=(4, 28))
        tk.Button(f, text="📂  Load the Dataset",
                  bg=Theme["C_BLUE"], fg="white",
                  font=(Font, 11, "bold"), relief="flat",
                  padx=28, pady=10, cursor="hand2",
                  command=lambda: self.navigate("load")).pack(pady=32)

    # load the dataset

    def load_file(self):
        path = r"FINAL PROJECT\Metro_Manila_Traffic_Incidents_2025.csv"
        try:
            self.df_originalData, self.df_cleanedCopy, self.clean_log = loadCleanDataset(path)
            self.status_display.set(
                f"✅ Loaded\n{len(self.df_cleanedCopy)} rows : {len(self.df_cleanedCopy.columns)} cols"
            )
            messagebox.showinfo("Dataset Loaded",
                f"Dataset loaded and cleaned!\n\n"
                f"Original rows : {len(self.df_originalData)}\n"
                f"Cleaned rows  : {len(self.df_cleanedCopy)}\n"
                f"Columns       : {len(self.df_cleanedCopy.columns)}")
            self.navigate("clean")
        except FileNotFoundError:
            messagebox.showerror("File Not Found",
                "File not found.\nMake sure the CSV is in the FINAL PROJECT folder.")
        except Exception as e:
            messagebox.showerror("Load Error", f"Could not load file:\n{e}")

    # data cleaning process

    def display_cleaning(self):
        self.clear()
        if self.need_data(): return
        self.header("🧹  Data Cleaning Report",
                    "Problems found in the dataset and methods applied")

        # Save button pinned to bottom BEFORE scrollable
        btn_bar = tk.Frame(self.content, bg=Theme["BG_LIGHT"])
        btn_bar.pack(side="bottom", fill="x", padx=28, pady=10)

        def save_csv():
            save_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                initialfile="Metro_Manila_Traffic_Cleaned_2025.csv",
                filetypes=[("CSV files", "*.csv")]
            )
            if save_path:
                self.df_cleanedCopy.to_csv(save_path, index=False, encoding='utf-8-sig')
                messagebox.showinfo("Saved", f"Cleaned dataset saved to:\n{save_path}")

        tk.Button(btn_bar, text="💾   Save Cleaned Dataset as CSV",
                  bg=Theme["C_GREEN"], fg="white",
                  font=(Font, 10, "bold"), relief="flat",
                  padx=20, pady=8, cursor="hand2",
                  command=save_csv).pack(anchor="w")

        # Scrollable content
        _, inner = self.scrollable(self.content)
        outer = tk.Frame(inner, bg=Theme["BG_LIGHT"])
        outer.pack(fill="both", expand=True, padx=28, pady=4)

        # NULL BEFORE
        before_card = self.card(outer)
        before_card.pack(fill="x", pady=(0, 10))
        tk.Label(before_card, text="NULL Values - BEFORE Cleaning",
                 bg=Theme["BG_CARD"], fg="white",
                 font=(Font, 10, "bold")).pack(anchor="w", padx=16, pady=(12, 6))
        null_grid = tk.Frame(before_card, bg=Theme["BG_CARD"])
        null_grid.pack(fill="x", padx=16, pady=(0, 12))
        for i, (col, cnt) in enumerate(self.df_originalData.isnull().sum().items()):
            color  = Theme["C_ORANGE"] if cnt > 0 else Theme["C_GREEN"]
            status = f"{cnt}  ← fix" if cnt > 0 else "0  ✓"
            row_f  = tk.Frame(null_grid, bg=Theme["BG_CARD"])
            row_f.grid(row=i//2, column=i%2, padx=6, pady=1, sticky="ew")
            null_grid.columnconfigure(i%2, weight=1)
            tk.Label(row_f, text=f"{col:<25} {status}",
                     bg=Theme["BG_CARD"], fg=color,
                     font=("Courier New", 9)).pack(anchor="w")

        # ISSUE CARDS
        issue_row = tk.Frame(outer, bg=Theme["BG_LIGHT"])
        issue_row.pack(fill="x", pady=8)
        issues = [
            (Theme["C_ORANGE"], "405", "Severity nulls",       " fillna('Unknown')"),
            (Theme["C_ORANGE"], "396", "Road Condition nulls",  " fillna('Unknown')"),
            (Theme["C_ORANGE"], "264", "Cause nulls",           " fillna('Unknown')"),
            (Theme["C_BLUE"],   "165", "Injury Count nulls",    " fillna(mean)"),
            (Theme["C_BLUE"],    "14", "Driver Age nulls",      " fillna(mean)"),
            (Theme["C_BLUE"],     "8", "Damage Cost nulls",     " fillna(mean)"),
            (Theme["C_RED"],      "3", "Negative Damage Cost",  " row removed"),
            (Theme["C_RED"],     "10", "Duplicate rows",        " drop_duplicates()"),
        ]
        for i, (color, num, lbl, fix) in enumerate(issues):
            c = tk.Frame(issue_row, bg=Theme["BG_CARD"], padx=14, pady=12)
            c.grid(row=i//4, column=i%4, padx=5, pady=5, sticky="ew")
            issue_row.columnconfigure(i%4, weight=1)
            tk.Label(c, text=num,  bg=Theme["BG_CARD"], fg=color,
                     font=(Font, 20, "bold")).pack(anchor="w")
            tk.Label(c, text=lbl,  bg=Theme["BG_CARD"], fg="white",
                     font=(Font, 8, "bold")).pack(anchor="w")
            tk.Label(c, text=fix,  bg=Theme["BG_CARD"], fg=Theme["TXT_SUB"],
                     font=(Font, 8)).pack(anchor="w")

        # CLEANING LOG
        log_card = self.card(outer)
        log_card.pack(fill="x", pady=8)
        tk.Label(log_card, text="Cleaning Log",
                 bg=Theme["BG_CARD"], fg="white",
                 font=(Font, 10, "bold")).pack(anchor="w", padx=16, pady=(12, 4))
        tk.Label(log_card, text=self.clean_log,
                 bg=Theme["BG_CARD"], fg="white",
                 font=("Courier New", 8),
                 justify="left").pack(anchor="w", padx=16, pady=(0, 12))

        # NULL AFTER
        after_card = self.card(outer)
        after_card.pack(fill="x", pady=(0, 20))
        tk.Label(after_card, text="Missing Values - AFTER Cleaning",
                 bg=Theme["BG_CARD"], fg=Theme["C_GREEN"],
                 font=(Font, 10, "bold")).pack(anchor="w", padx=16, pady=(12, 6))
        after_grid = tk.Frame(after_card, bg=Theme["BG_CARD"])
        after_grid.pack(fill="x", padx=16, pady=(0, 12))
        for i, (col, cnt) in enumerate(self.df_cleanedCopy.isnull().sum().items()):
            row_f = tk.Frame(after_grid, bg=Theme["BG_CARD"])
            row_f.grid(row=i//2, column=i%2, padx=6, pady=1, sticky="ew")
            after_grid.columnconfigure(i%2, weight=1)
            tk.Label(row_f,
                     text=f"{col:<25} {cnt}  {'✓' if cnt == 0 else '← still missing!'}",
                     bg=Theme["BG_CARD"],
                     fg=Theme["C_GREEN"] if cnt == 0 else Theme["C_RED"],
                     font=("Courier New", 9)).pack(anchor="w")

    # display clean data

    def display_cleanedTable(self):
        self.clear()
        if self.need_data(): return
        self.header("📋  Cleaned Dataset",
                    f"First 200 rows of {len(self.df_cleanedCopy)} total records · {len(self.df_cleanedCopy.columns)} columns")

        frame = tk.Frame(self.content, bg=Theme["BG_LIGHT"])
        frame.pack(fill="both", expand=True, padx=28, pady=4)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background=Theme["BG_CARD"], foreground=Theme["TXT"],
                        fieldbackground=Theme["BG_CARD"], rowheight=24,
                        font=(Font, 8))
        style.configure("Treeview.Heading",
                        background=Theme["BG_CARD2"], foreground=Theme["C_BLUE"],
                        font=(Font, 8, "bold"), relief="flat")
        style.map("Treeview",
                  background=[("selected", Theme["C_BLUE"])],
                  foreground=[("selected", "white")])

        cols = ['Incident_ID', 'Date', 'City', 'Road_Name', 'Vehicle_Type',
                'Accident_Type', 'Severity', 'Weather_Condition',
                'Road_Condition', 'Cause', 'Driver_Age',
                'Driver_Gender', 'Injury_Count', 'Damage_Cost_PHP']

        col_widths = {
            'Incident_ID': 110, 'Date': 90, 'City': 100, 'Road_Name': 110,
            'Vehicle_Type': 90, 'Accident_Type': 100, 'Severity': 70,
            'Weather_Condition': 110, 'Road_Condition': 100, 'Cause': 130,
            'Driver_Age': 80, 'Driver_Gender': 90,
            'Injury_Count': 90, 'Damage_Cost_PHP': 120,
        }

        tree = ttk.Treeview(frame, columns=cols, show="headings")
        for col in cols:
            tree.heading(col, text=col.replace("_", " "))
            tree.column(col, width=col_widths.get(col, 100), anchor="w")

        for _, row in self.df_cleanedCopy[cols].head(200).iterrows():
            vals = []
            for v in row:
                if isinstance(v, float): vals.append(f"{v:,.2f}")
                elif hasattr(v, 'date'): vals.append(str(v.date()))
                else: vals.append(str(v))
            tree.insert("", "end", values=vals)

        vsb = ttk.Scrollbar(frame, orient="vertical",   command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right",  fill="y")
        hsb.pack(side="bottom", fill="x")
        tree.pack(fill="both", expand=True)

    # statistics and computations

    def show_stats(self):
        self.clear()
        if self.need_data(): return
        self.header("📊  Statistical Analysis",
                    "Numerical computations across key columns")

        _, inner = self.scrollable(self.content)
        outer = tk.Frame(inner, bg=Theme["BG_LIGHT"])
        outer.pack(fill="both", expand=True, padx=28, pady=4)

        # Numeric stats cards
        num_cols = {
            "Driver Age (years)" : self.df_cleanedCopy['Driver_Age'],
            "Injury Count"       : self.df_cleanedCopy['Injury_Count'],
            "Damage Cost (PHP)"  : self.df_cleanedCopy['Damage_Cost_PHP'],
        }
        for label, series in num_cols.items():
            card = self.card(outer)
            card.pack(fill="x", pady=5)
            tk.Label(card, text=label,
                     bg=Theme["BG_CARD"], fg=Theme["C_BLUE"],
                     font=(Font, 10, "bold")).pack(anchor="w", padx=16, pady=(12, 8))

            stat_row = tk.Frame(card, bg=Theme["BG_CARD"])
            stat_row.pack(fill="x", padx=16, pady=(0, 12))

            stats = [
                ("Mean", f"{np.mean(series):,.2f}"),
                ("Median", f"{np.median(series):,.2f}"),
                ("Mode", f"{series.mode()[0]:,.2f}"),
                ("Std Dev", f"{np.std(series):,.2f}"),
                ("Min", f"{np.min(series):,.2f}"),
                ("Max", f"{np.max(series):,.2f}"),
            ]

            for i, (lbl, val) in enumerate(stats):
                cell = tk.Frame(stat_row, bg=Theme["BG_CARD2"], padx=10, pady=10)
                cell.grid(row=0, column=i, padx=3, sticky="ew")
                stat_row.columnconfigure(i, weight=1)
                tk.Label(cell, text=val,
                         bg=Theme["BG_CARD2"], fg=Theme["TXT"],
                         font=(Font, 10, "bold")).pack()
                tk.Label(cell, text=lbl,
                         bg=Theme["BG_CARD2"], fg=Theme["TXT_SUB"],
                         font=(Font, 8)).pack()

        # Frequency Distribution
        tk.Label(outer, text="Frequency Distribution",
                 bg=Theme["BG_LIGHT"], fg=Theme["BG_PANEL"],
                 font=(Font, 9, "bold")).pack(anchor="w", pady=(10, 4))

        # Horizontal scroll wrapper
        freq_container = tk.Frame(outer, bg=Theme["BG_LIGHT"])
        freq_container.pack(fill="x", pady=4)

        freq_hsb = ttk.Scrollbar(freq_container, orient="horizontal")
        freq_hsb.pack(side="bottom", fill="x")             

        freq_canvas = tk.Canvas(freq_container,
                                bg=Theme["BG_LIGHT"],
                                highlightthickness=0,
                                height=260)
        freq_canvas.pack(side="top", fill="x", expand=True)
        freq_canvas.configure(xscrollcommand=freq_hsb.set)
        freq_hsb.configure(command=freq_canvas.xview)

        freq_row = tk.Frame(freq_canvas, bg=Theme["BG_LIGHT"])  # ← ONE freq_row only
        freq_canvas.create_window((0, 0), window=freq_row, anchor="nw")
        freq_row.bind(
            "<Configure>",
            lambda e: freq_canvas.configure(
                scrollregion=freq_canvas.bbox("all")
            )
        )

        for col, title in [
            ('Severity', 'Severity'),
            ('Accident_Type', 'Accident Type'),
            ('Cause', 'Top Causes'),
            ('Weather_Condition', 'Weather'),
            ('Vehicle_Type', 'Vehicle Type'),
        ]:
            card = self.card(freq_row, padx=14, pady=12)
            card.pack(side="left", fill="y", padx=4)       

            tk.Label(card, text=title,
                     bg=Theme["BG_CARD"], fg=Theme["C_BLUE"],
                     font=(Font, 9, "bold")).pack(anchor="w", pady=(0, 8))

            freq = self.df_cleanedCopy[col].value_counts().head(7)
            total = len(self.df_cleanedCopy)

            for val, cnt in freq.items():
                pct = cnt / total * 100
                row_f = tk.Frame(card, bg=Theme["BG_CARD"])
                row_f.pack(fill="x", pady=1)
                tk.Label(row_f, text=str(val)[:20],
                         bg=Theme["BG_CARD"], fg=Theme["TXT"],
                         font=(Font, 8), width=20, anchor="w").pack(side="left")
                tk.Label(row_f, text=f"{cnt}  ({pct:.1f}%)",
                         bg=Theme["BG_CARD"], fg=Theme["TXT_SUB"],
                         font=(Font, 8)).pack(side="right")

        # Correlation matrix
        corr_card = self.card(outer)
        corr_card.pack(fill="x", pady=(10, 4))
        tk.Label(corr_card,
                 text="Correlation Matrix  (Driver_Age, Injury_Count, Damage_Cost_PHP)",
                 bg=Theme["BG_CARD"], fg=Theme["C_BLUE"],
                 font=(Font, 10, "bold")).pack(anchor="w", padx=16, pady=(12, 4))
        corr = self.df_cleanedCopy[
            ['Driver_Age', 'Injury_Count', 'Damage_Cost_PHP']
        ].corr().round(4)
        tk.Label(corr_card, text=corr.to_string(),
                 bg=Theme["BG_CARD"], fg=Theme["TXT"],
                 font=("Courier New", 9),
                 justify="left").pack(anchor="w", padx=16, pady=(0, 12))

        # City ranking
        rank_card = self.card(outer)
        rank_card.pack(fill="x", pady=(4, 20))
        tk.Label(rank_card, text="Incidents per City (Ranked)",
                 bg=Theme["BG_CARD"], fg=Theme["C_BLUE"],
                 font=(Font, 10, "bold")).pack(anchor="w", padx=16, pady=(12, 6))
        city_counts = (self.df_cleanedCopy
                       .groupby('City')['Incident_ID']
                       .count()
                       .sort_values(ascending=False))
        for rank, (city, cnt) in enumerate(city_counts.items(), 1):
            avg_dmg = (self.df_cleanedCopy[self.df_cleanedCopy['City'] == city]
                       ['Damage_Cost_PHP'].mean())
            row_f = tk.Frame(rank_card, bg=Theme["BG_CARD"])
            row_f.pack(fill="x", padx=16, pady=2)
            tk.Label(row_f,
                     text=f"{rank:>2}. {city:<18}  {cnt:>4} incidents   avg damage PHP {avg_dmg:>10,.2f}",
                     bg=Theme["BG_CARD"], fg=Theme["TXT"],
                     font=("Courier New", 9)).pack(anchor="w")
        tk.Frame(rank_card, bg=Theme["BG_CARD"], height=10).pack()

    # visualization

    def show_visual(self):
        self.clear()
        if self.need_data(): return
        self.header("📈  Visualization", "Select a Chart Option.")

        btn_bar = tk.Frame(self.content, bg=Theme["BG_LIGHT"])
        btn_bar.pack(padx=28, pady=(0, 8), anchor="w")

        self.chart_frame = tk.Frame(self.content, bg=Theme["BG_LIGHT"])
        self.chart_frame.pack(fill="both", expand=True, padx=28, pady=4)

        self.chart_btns = {}
        charts = [
            ("bar", "Bar — Incidents per City"),
            ("line", "Line — Monthly Trend"),
            ("pie", "Pie — Accident Types"),
            ("histogram", "Histogram — Driver Age"),
            ("scatter", "Scatter — Injury vs Damage"),
        ]
        for key, label in charts:
            b = tk.Button(btn_bar, text=label,
                          bg=Theme["BG_CARD2"], fg=Theme["TXT"],
                          font=(Font, 8), relief="flat",
                          padx=10, pady=6, cursor="hand2",
                          activebackground=Theme["C_BLUE"],
                          activeforeground="white",
                          command=lambda k=key: self.draw_chart(k))
            b.pack(side="left", padx=3)
            self.chart_btns[key] = b

        self.draw_chart("bar")

    def draw_chart(self, key):
        for k, b in self.chart_btns.items():
            b.configure(bg=Theme["C_BLUE"] if k == key else Theme["BG_CARD2"])
        for w in self.chart_frame.winfo_children():
            w.destroy()
        fig = self.make_figure(key)
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

    def make_figure(self, key):
        df  = self.df_cleanedCopy
        BG  = Theme["BG_CARD"]
        BG2 = Theme["BG_CARD2"]
        CB  = Theme["C_BLUE"]
        CO  = Theme["C_ORANGE"]
        CG  = Theme["C_GREEN"]
        CR  = Theme["C_RED"]
        TXTCOLOR   = Theme["TXT"]
        TS  = Theme["TXT_SUB"]

        fig, ax = plt.subplots(figsize=(11, 5), facecolor=BG)
        ax.set_facecolor(BG)

        def style_ax(title, xlabel, ylabel):
            ax.set_title(title, color=TXTCOLOR, fontsize=12, fontweight="bold", pad=10)
            ax.set_xlabel(xlabel, color=TS, fontsize=9)
            ax.set_ylabel(ylabel, color=TS, fontsize=9)
            ax.tick_params(colors=TS, labelsize=8)
            ax.spines[['top', 'right', 'left', 'bottom']].set_color(BG2)
            ax.yaxis.grid(True, linestyle="--", alpha=0.25, color="#4a6380")
            ax.set_axisbelow(True)

        # display bar graph
        if key == "bar":
            city_c = (df.groupby('City')['Incident_ID']
                      .count().sort_values(ascending=False))
            colors = [CO if i == 0 else CB for i in range(len(city_c))]
            bars = ax.bar(city_c.index, city_c.values,
                          color=colors, edgecolor=BG, linewidth=0.8)
            for b in bars:
                ax.text(b.get_x() + b.get_width() / 2,
                        b.get_height() + 0.4,
                        str(int(b.get_height())),
                        ha="center", va="bottom", fontsize=7.5, color=TS)
            ax.tick_params(axis='x', rotation=40)
            style_ax("Traffic Incidents Per City", "City", "Number of Incidents")

        # display line graph
        elif key == "line":
            mo = ['Jan','Feb','Mar','Apr','May','Jun',
                  'Jul','Aug','Sep','Oct','Nov','Dec']
            monthly = (df.groupby('Month_Name')['Incident_ID']
                       .count().reindex(mo, fill_value=0))
            ax.plot(monthly.index, monthly.values,
                    color=CB, linewidth=2.5, marker='o',
                    markersize=7, markerfacecolor=CO,
                    markeredgecolor=BG, markeredgewidth=1.5)
            ax.fill_between(monthly.index, monthly.values, alpha=0.10, color=CB)
            for x, y in zip(monthly.index, monthly.values):
                ax.annotate(str(y), (x, y), xytext=(0, 9),
                            textcoords='offset points',
                            ha='center', fontsize=7.5, color=TS)
            ax.tick_params(axis='x', rotation=30)
            ax.xaxis.grid(True, linestyle="--", alpha=0.15, color="#4a6380")
            style_ax("Monthly Incident Trend (2025)", "Month", "Number of Incidents")

        # display pie chart
        elif key == "pie":
            acc = df['Accident_Type'].value_counts()
            pie_colors = [CB, '#2e9ad4', CO, CR, CG]
            wedges, texts, autos = ax.pie(
                acc.values, labels=acc.index,
                colors=pie_colors[:len(acc)],
                autopct='%1.1f%%', startangle=140, pctdistance=0.82,
                wedgeprops={'edgecolor': BG, 'linewidth': 2}
            )
            for t in texts:
                t.set_color(TXTCOLOR); t.set_fontsize(9)
            for a in autos:
                a.set_color("white"); a.set_fontsize(8); a.set_fontweight("bold")
            ax.set_title("Accident Type Breakdown",
                         color=TXTCOLOR, fontsize=12, fontweight="bold")

        # display histogram
        elif key == "histogram":
            ages = df['Driver_Age'].dropna()
            n, _, patches = ax.hist(ages, bins=15, color=CB,
                                    edgecolor=BG, linewidth=0.8, alpha=0.85)
            patches[int(np.argmax(n))].set_facecolor(CO)
            mean_age = np.mean(ages)
            ax.axvline(mean_age, color=CR, linestyle='--', linewidth=2,
                       label=f"Mean Age: {mean_age:.1f}")
            ax.legend(fontsize=9, facecolor=BG2, edgecolor='none', labelcolor=TXTCOLOR)
            style_ax("Driver Age Distribution", "Driver Age (years)", "Frequency")

        # display scatter plot
        elif key == "scatter":
            sev_c = {'Minor': CG, 'Major': CO, 'Fatal': CR, 'Unknown': "#4a6380"}
            for sev, grp in df.groupby('Severity'):
                ax.scatter(grp['Injury_Count'], grp['Damage_Cost_PHP'],
                           c=sev_c.get(sev, '#888'), label=sev,
                           alpha=0.5, s=28, edgecolors=BG, linewidths=0.3)
            z  = np.polyfit(df['Injury_Count'], df['Damage_Cost_PHP'], 1)
            xl = np.linspace(df['Injury_Count'].min(), df['Injury_Count'].max(), 100)
            ax.plot(xl, np.poly1d(z)(xl), color=TXTCOLOR, linewidth=1.8,
                    linestyle='--', label='Trend Line')
            ax.legend(fontsize=8, facecolor=BG2, edgecolor='none')
            ax.xaxis.grid(True, linestyle="--", alpha=0.2, color="#4a6380")
            style_ax("Injury Count vs. Damage Cost (PHP)\nColored by Severity",
                     "Injury Count", "Damage Cost (PHP)")

        fig.tight_layout()
        return fig

    # INSIGHTS

    def show_insights(self):
        self.clear()
        if self.need_data(): return
        self.header("🚦  Insights & Recommendations",
                    "Key findings derived from the data analysis")

        _, inner = self.scrollable(self.content)
        outer = tk.Frame(inner, bg=Theme["BG_LIGHT"])
        outer.pack(fill="both", expand=True, padx=28, pady=4)

        df = self.df_cleanedCopy

        # top records idetified 
        top_city = df.groupby('City')['Incident_ID'].count().idxmax()
        top_cause = (df[df['Cause'] != 'Unknown']['Cause']
                       .value_counts().idxmax())
        avg_dmg = df['Damage_Cost_PHP'].mean()
        fatal_pct = (df['Severity'] == 'Fatal').sum() / len(df) * 100
        rain_pct = df['Weather_Condition'].isin(['Rain','Storm']).sum() / len(df) * 100
        peak_hr = int(df['Hour'].mode()[0])
        peak_lbl = ("morning rush"  if 6  <= peak_hr <= 9  else
                       "evening rush"  if 17 <= peak_hr <= 20 else
                       "off-peak hour")
        top_vehicle = df['Vehicle_Type'].value_counts().idxmax()
        top_road = df['Road_Name'].value_counts().idxmax()

        # display insights and top findings
        findings = [
            (Theme["C_RED"], "🏙️ Hotspot City",
             f"{top_city} recorded the highest number of traffic incidents in Metro Manila for 2025. "
             f"LGUs and MMDA should prioritize road safety enforcement and infrastructure investment here."),

            (Theme["C_ORANGE"], "⚠️  Leading Cause",
             f"'{top_cause}' is the most frequently recorded cause of accidents. "
             f"Stricter enforcement, public awareness campaigns, and driver education are urgently needed."),

            (Theme["C_BLUE"],   "💸  Financial Impact",
             f"The average damage cost per incident is PHP {avg_dmg:,.2f}. "
             f"This represents a significant economic burden — prevention programs are financially justified."),

            (Theme["C_RED"],    "💀  Fatal Incidents",
             f"{fatal_pct:.1f}% of all incidents were classified as Fatal. "
             f"Better emergency response, road design, and enforcement can directly reduce this rate."),

            (Theme["C_BLUE"],   "🌧️  Weather Factor",
             f"{rain_pct:.1f}% of incidents occurred during rainy or stormy weather. "
             f"DPWH and MMDA should improve drainage and deploy weather-adaptive traffic management."),

            (Theme["C_GREEN"],  f"🕐  Peak Hour — {peak_hr}:00 ({peak_lbl})",
             f"The highest concentration of incidents occurs at {peak_hr}:00. "
             f"Deploying additional enforcers and speed limits during this window could reduce incidents."),

            (Theme["C_YELLOW"], "🚗  Most Involved Vehicle",
             f"'{top_vehicle}' is the most common vehicle type in incidents. "
             f"Targeted roadworthiness checks for this vehicle type may help reduce accidents."),

            (Theme["C_ORANGE"], "🛣️  Most Incident-Prone Road",
             f"'{top_road}' has the highest number of recorded incidents. "
             f"Better lighting, markings, and signage are recommended for this road."),
        ]

        for color, title, body_text in findings:
            card = tk.Frame(outer, bg=Theme["BG_CARD"], padx=18, pady=14)
            card.pack(fill="x", pady=4)
            bar = tk.Frame(card, bg=color, width=4)
            bar.pack(side="left", fill="y", padx=(0, 12))
            txt_f = tk.Frame(card, bg=Theme["BG_CARD"])
            txt_f.pack(side="left", fill="both", expand=True)
            tk.Label(txt_f, text=title,
                     bg=Theme["BG_CARD"], fg=color,
                     font=(Font, 10, "bold")).pack(anchor="w")
            tk.Label(txt_f, text=body_text,
                     bg=Theme["BG_CARD"], fg=Theme["TXT"],
                     font=(Font, 9), wraplength=800,
                     justify="left").pack(anchor="w", pady=(3, 0))

        # Recommendations
        rec = tk.Frame(outer, bg=Theme["BG_CARD2"], padx=18, pady=14)
        rec.pack(fill="x", pady=(10, 24))
        tk.Label(rec, text="📌  Recommendations",
                 bg=Theme["BG_CARD2"], fg=Theme["C_GREEN"],
                 font=(Font, 10, "bold")).pack(anchor="w", pady=(0, 8))
        recs = [
            f"Launch anti-{top_cause.lower()} campaigns, especially in {top_city}.",
            "Improve road drainage and signage on flood-prone routes.",
            f"Increase MMDA enforcer deployment at {peak_hr}:00 ({peak_lbl}).",
            "Install speed cameras on high-risk roads.",
            "Strengthen sobriety checkpoints to deter drunk driving.",
            f"Implement stricter roadworthiness checks for {top_vehicle.lower()}s.",
            f"Prioritize infrastructure upgrades on {top_road}.",

            "MMDA: Mandate digital incident reporting with controlled dropdowns for Severity, Cause, and Road Condition to eliminate the 40.2% Unknown classification gap.",
            "LTO: Shift enforcement from age-based targeting to behavioral profiling — enforce mandatory refresher courses and data-sharing protocols with MMDA across all license categories.",
            f"LGUs: Allocate road safety budgets based on both incident frequency and average damage cost — high-frequency cities like {top_city} need enforcement saturation while lower-frequency cities need road engineering audits.",
            "MMDA & DPWH: Launch pre-emptive drainage inspections, road maintenance, and heightened enforcement from June to September to address the July incident peak during the wet season.",
            "PNP-HPG: Expand CCTV coverage on high-incident corridors and establish a streamlined Hit and Run reporting pipeline with MMDA, backed by stricter legal penalties and public awareness campaigns.",
            "Future studies should incorporate real MMDA-sourced data and variables such as vehicle speed, seatbelt use, alcohol involvement, and road surface type to produce findings with stronger policy applicability.",
        ]

        # display recommendations
        for r in recs:
            row_r = tk.Frame(rec, bg=Theme["BG_CARD2"])
            row_r.pack(fill="x", pady=2)
            tk.Label(row_r, text="•",
                     bg=Theme["BG_CARD2"], fg=Theme["C_GREEN"],
                     font=(Font, 10, "bold")).pack(side="left", padx=(0, 8))
            tk.Label(row_r, text=r,
                     bg=Theme["BG_CARD2"], fg=Theme["TXT"],
                     font=(Font, 9), wraplength=800,
                     justify="left").pack(side="left")

# main entry point 
if __name__ == "__main__":
    app = TrafficApp()
    app.mainloop()