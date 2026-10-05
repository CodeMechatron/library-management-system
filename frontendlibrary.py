import json
import customtkinter as ctk
from tkinter import ttk

file = r"books.json"


def load_books():
    try:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_books():
    with open(file, "w", encoding="utf-8") as f:
        json.dump(books, f, indent=2)


books = load_books()


# =====================================================================
#  THEME
# =====================================================================
BG = "#12141f"
SIDEBAR = "#181b2a"
CARD = "#1e2233"
CARD_HOVER = "#262b42"
ACCENT = "#5b7cfa"
ACCENT_HOVER = "#4a69e0"
GREEN = "#4ade80"
ORANGE = "#fb923c"
RED = "#f87171"
TEXT = "#e6e9f5"
MUTED = "#8b91ab"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Library Management System")
root.geometry("1100x680")
root.minsize(980, 620)
root.configure(fg_color=BG)

toast_job = None


# =====================================================================
#  UI HELPERS (these replace input() and print())
# =====================================================================
def show_message(text, kind="info"):
    """Replaces print(): shows a coloured message bar that fades away."""
    global toast_job
    colors = {"info": ACCENT, "success": GREEN, "warning": ORANGE, "error": RED}
    icons = {"info": "ℹ", "success": "✔", "warning": "⚠", "error": "✖"}
    toast.configure(text=f"  {icons[kind]}  {text}", text_color=colors[kind])
    if toast_job is not None:
        root.after_cancel(toast_job)
    toast_job = root.after(4000, lambda: toast.configure(text=""))


def ask_fields(title, fields, subtitle=""):
    """
    Replaces input(): opens a popup form.
    fields = [(key, label, kind, default), ...]  kind is "int" or "str"
    Returns a dict of answers, or None if cancelled.
    """
    result = {}
    height = 190 + 82 * len(fields)

    dlg = ctk.CTkToplevel(root)
    dlg.title(title)
    dlg.configure(fg_color=CARD)
    dlg.resizable(False, False)
    dlg.transient(root)

    x = root.winfo_x() + (root.winfo_width() - 400) // 2
    y = root.winfo_y() + (root.winfo_height() - height) // 2
    dlg.geometry(f"400x{height}+{x}+{y}")

    ctk.CTkLabel(dlg, text=title, font=("Segoe UI", 20, "bold"),
                 text_color=TEXT).pack(anchor="w", padx=30, pady=(24, 0))
    if subtitle:
        ctk.CTkLabel(dlg, text=subtitle, font=("Segoe UI", 12),
                     text_color=MUTED).pack(anchor="w", padx=30)

    entries = {}
    for key, label, kind, default in fields:
        ctk.CTkLabel(dlg, text=label, font=("Segoe UI", 12),
                     text_color=MUTED).pack(anchor="w", padx=30, pady=(12, 2))
        entry = ctk.CTkEntry(dlg, height=38, corner_radius=10,
                             fg_color=BG, border_color="#2f3550")
        entry.pack(fill="x", padx=30)
        if default != "":
            entry.insert(0, str(default))
        entries[key] = entry

    error_label = ctk.CTkLabel(dlg, text="", text_color=RED, font=("Segoe UI", 12))
    error_label.pack(pady=(10, 0))

    def submit(event=None):
        out = {}
        for key, label, kind, default in fields:
            value = entries[key].get().strip()
            if value == "":
                error_label.configure(text=f"{label} is required.")
                return
            if kind == "int":
                try:
                    value = int(value)
                except ValueError:
                    error_label.configure(text=f"{label} must be a number.")
                    return
            out[key] = value
        result.update(out)
        dlg.destroy()

    btn_row = ctk.CTkFrame(dlg, fg_color="transparent")
    btn_row.pack(fill="x", padx=30, pady=(8, 20))
    ctk.CTkButton(btn_row, text="Cancel", height=38, corner_radius=10,
                  fg_color="#2f3550", hover_color="#3a4163",
                  command=dlg.destroy).pack(side="left", expand=True, fill="x", padx=(0, 6))
    ctk.CTkButton(btn_row, text="Confirm", height=38, corner_radius=10,
                  fg_color=ACCENT, hover_color=ACCENT_HOVER,
                  command=submit).pack(side="left", expand=True, fill="x", padx=(6, 0))

    dlg.bind("<Return>", submit)
    dlg.bind("<Escape>", lambda e: dlg.destroy())
    first = entries[fields[0][0]]
    dlg.after(150, lambda: (dlg.grab_set(), first.focus_set()))

    root.wait_window(dlg)
    return result if result else None


def refresh_table():
    """Redraws the table and the stat cards from the books list."""
    query = search_box.get().strip().lower()

    for row in table.get_children():
        table.delete(row)

    for book in books:
        haystack = f'{book["id"]} {book["title"]} {book["author"]}'.lower()
        if query and query not in haystack:
            continue
        if book["available"]:
            status, tag = "●  Available", "available"
        else:
            status, tag = "●  Borrowed", "borrowed"
        table.insert("", "end", tags=(tag,),
                     values=(book["id"], book["title"], book["author"], status))

    total = len(books)
    free = sum(1 for b in books if b["available"])
    stat_total.configure(text=str(total))
    stat_available.configure(text=str(free))
    stat_borrowed.configure(text=str(total - free))


# =====================================================================
#  YOUR ORIGINAL LOGIC (same code, now triggered by buttons)
# =====================================================================

# ---------- 1. Add Book ----------
def add_book():
    data = ask_fields("Add Book", [
        ("id", "Book ID", "int", ""),
        ("title", "Book title", "str", ""),
        ("author", "Author", "str", ""),
    ], "Enter the details of the new book")
    if data is None:
        return
    id = data["id"]
    title = data["title"]
    author = data["author"]

    book = {
        "id": id,
        "title": title,
        "author": author,
        "available": True
    }

    books.append(book)
    save_books()
    refresh_table()

    show_message("Book added successfully.", "success")


# ---------- 2. View Books ----------
def view_books():
    search_box.delete(0, "end")
    refresh_table()
    if books == []:
        show_message("There are no books.", "warning")
    else:
        show_message(f"Showing all {len(books)} book(s).", "info")


# ---------- 3. Search Book ----------
def search_book():
    data = ask_fields("Search Book", [("id", "Book ID", "int", "")])
    if data is None:
        return
    id = data["id"]
    found = False

    for book in books:
        if book["id"] == id:
            search_box.delete(0, "end")
            refresh_table()
            for item in table.get_children():
                if str(table.item(item, "values")[0]) == str(id):
                    table.selection_set(item)
                    table.see(item)
            show_message(str(book), "info")
            found = True

    if found == False:
        show_message("Book not found.", "error")


# ---------- 4. Borrow Book ----------
def borrow_book():
    data = ask_fields("Borrow Book", [("id", "Book ID", "int", "")])
    if data is None:
        return
    id = data["id"]
    found = False

    for book in books:
        if book["id"] == id:
            found = True

            if book["available"] == False:
                show_message("The book has already been borrowed.", "warning")
            else:
                book["available"] = False
                save_books()
                refresh_table()
                show_message("Book borrowed successfully.", "success")

    if found == False:
        show_message("Book not found.", "error")


# ---------- 5. Return Book ----------
def return_book():
    data = ask_fields("Return Book", [("id", "Book ID", "int", "")])
    if data is None:
        return
    id = data["id"]
    found = False

    for book in books:
        if book["id"] == id:
            found = True

            if book["available"] == True:
                show_message("The book is already available.", "warning")
            else:
                book["available"] = True
                save_books()
                refresh_table()
                show_message("Book returned successfully.", "success")

    if found == False:
        show_message("Book not found.", "error")


# ---------- 6. Update Book ----------
def update_book():
    data = ask_fields("Update Book", [("id", "Book ID", "int", "")])
    if data is None:
        return
    id = data["id"]
    found = False

    for book in books:
        if book["id"] == id:
            found = True

            new = ask_fields("Update Book", [
                ("title", "New book title", "str", book["title"]),
                ("author", "New author", "str", book["author"]),
            ], f"Editing book ID {id}")
            if new is None:
                return

            book["title"] = new["title"]
            book["author"] = new["author"]

            save_books()
            refresh_table()
            show_message("Book updated successfully.", "success")

    if found == False:
        show_message("Book not found.", "error")


# ---------- 7. Delete Book ----------
def delete_book():
    data = ask_fields("Delete Book", [("id", "Book ID", "int", "")])
    if data is None:
        return
    id = data["id"]
    found = False

    for book in books:
        if book["id"] == id:
            found = True

            books.remove(book)
            save_books()
            refresh_table()

            show_message("Book deleted successfully.", "success")

    if found == False:
        show_message("Book not found.", "error")


# ---------- 8. Exit ----------
def exit_program():
    root.destroy()


# =====================================================================
#  LAYOUT
# =====================================================================
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)

# ---------- Sidebar ----------
sidebar = ctk.CTkFrame(root, width=240, corner_radius=0, fg_color=SIDEBAR)
sidebar.grid(row=0, column=0, sticky="nsew")
sidebar.grid_propagate(False)

ctk.CTkLabel(sidebar, text="📚", font=("Segoe UI Emoji", 38)).pack(pady=(30, 0))
ctk.CTkLabel(sidebar, text="LIBRARY", font=("Segoe UI", 22, "bold"),
             text_color=TEXT).pack()
ctk.CTkLabel(sidebar, text="Management System", font=("Segoe UI", 12),
             text_color=MUTED).pack(pady=(0, 24))

menu = [
    ("＋   Add Book", add_book, ACCENT, ACCENT_HOVER),
    ("☰   View Books", view_books, "transparent", CARD_HOVER),
    ("⌕   Search Book", search_book, "transparent", CARD_HOVER),
    ("↗   Borrow Book", borrow_book, "transparent", CARD_HOVER),
    ("↙   Return Book", return_book, "transparent", CARD_HOVER),
    ("✎   Update Book", update_book, "transparent", CARD_HOVER),
    ("🗑   Delete Book", delete_book, "transparent", CARD_HOVER),
]

for text, command, color, hover in menu:
    ctk.CTkButton(sidebar, text=text, command=command, anchor="w", height=44,
                  corner_radius=12, fg_color=color, hover_color=hover,
                  text_color=TEXT, font=("Segoe UI", 14)).pack(fill="x", padx=18, pady=4)

ctk.CTkButton(sidebar, text="⏻   Exit", command=exit_program, anchor="w", height=44,
              corner_radius=12, fg_color="#3a1f28", hover_color="#512733",
              text_color=RED, font=("Segoe UI", 14, "bold")).pack(
    side="bottom", fill="x", padx=18, pady=24)

# ---------- Main area ----------
main = ctk.CTkFrame(root, fg_color="transparent")
main.grid(row=0, column=1, sticky="nsew", padx=28, pady=24)
main.grid_columnconfigure(0, weight=1)
main.grid_rowconfigure(3, weight=1)

ctk.CTkLabel(main, text="Dashboard", font=("Segoe UI", 28, "bold"),
             text_color=TEXT).grid(row=0, column=0, sticky="w")
ctk.CTkLabel(main, text="Manage your books, borrowers and returns in one place.",
             font=("Segoe UI", 13), text_color=MUTED).grid(row=1, column=0, sticky="w", pady=(0, 16))

# ---------- Stat cards ----------
cards = ctk.CTkFrame(main, fg_color="transparent")
cards.grid(row=2, column=0, sticky="ew", pady=(0, 16))
for i in range(3):
    cards.grid_columnconfigure(i, weight=1)


def make_card(column, title, color):
    card = ctk.CTkFrame(cards, corner_radius=16, fg_color=CARD)
    card.grid(row=0, column=column, sticky="ew", padx=(0 if column == 0 else 8, 0 if column == 2 else 8))
    ctk.CTkLabel(card, text=title, font=("Segoe UI", 12), text_color=MUTED).pack(
        anchor="w", padx=20, pady=(16, 0))
    value = ctk.CTkLabel(card, text="0", font=("Segoe UI", 34, "bold"), text_color=color)
    value.pack(anchor="w", padx=20, pady=(0, 14))
    return value


stat_total = make_card(0, "TOTAL BOOKS", ACCENT)
stat_available = make_card(1, "AVAILABLE", GREEN)
stat_borrowed = make_card(2, "BORROWED", ORANGE)

# ---------- Table panel ----------
panel = ctk.CTkFrame(main, corner_radius=16, fg_color=CARD)
panel.grid(row=3, column=0, sticky="nsew")
panel.grid_columnconfigure(0, weight=1)
panel.grid_rowconfigure(1, weight=1)

search_box = ctk.CTkEntry(panel, height=40, corner_radius=12, fg_color=BG,
                          border_color="#2f3550",
                          placeholder_text="🔍  Filter by ID, title or author...")
search_box.grid(row=0, column=0, columnspan=2, sticky="ew", padx=16, pady=16)
search_box.bind("<KeyRelease>", lambda e: refresh_table())

style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", background=CARD, fieldbackground=CARD, foreground=TEXT,
                rowheight=40, borderwidth=0, font=("Segoe UI", 12))
style.configure("Treeview.Heading", background="#2a2f45", foreground="#ffffff",
                font=("Segoe UI", 12, "bold"), relief="flat", padding=10)
style.map("Treeview", background=[("selected", ACCENT)],
          foreground=[("selected", "#ffffff")])
style.map("Treeview.Heading", background=[("active", "#353b57")])

table = ttk.Treeview(panel, columns=("ID", "Title", "Author", "Status"),
                     show="headings", selectmode="browse")
for col, width, anchor in (("ID", 80, "center"), ("Title", 330, "w"),
                           ("Author", 250, "w"), ("Status", 140, "center")):
    table.heading(col, text=col)
    table.column(col, width=width, anchor=anchor)
table.tag_configure("available", foreground=TEXT)
table.tag_configure("borrowed", foreground=ORANGE)
table.grid(row=1, column=0, sticky="nsew", padx=(16, 0), pady=(0, 16))

scroll = ctk.CTkScrollbar(panel, command=table.yview)
scroll.grid(row=1, column=1, sticky="ns", padx=(4, 12), pady=(0, 16))
table.configure(yscrollcommand=scroll.set)

# ---------- Message bar ----------
toast = ctk.CTkLabel(main, text="", anchor="w", height=36, corner_radius=10,
                     fg_color=SIDEBAR, font=("Segoe UI", 13))
toast.grid(row=4, column=0, sticky="ew", pady=(14, 0))

refresh_table()
root.mainloop()