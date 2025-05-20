import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import collections
import re
import csv

default_stoplist = os.path.join(os.getcwd(), "stoplist.txt")

def CreateIndex(Dir, StopList, progress_callback=None):
    with open(StopList, 'r', encoding='utf-8') as f:
        stop_words = set(word.strip().lower() for word in f.readlines())

    doc_table = []
    term_table = collections.defaultdict(lambda: collections.defaultdict(int))

    files = [f for f in os.listdir(Dir) if os.path.isfile(os.path.join(Dir, f)) and f != os.path.basename(StopList)]
    total_files = len(files)

    for i, filename in enumerate(files):
        filepath = os.path.join(Dir, filename)
        doc_table.append(filename)
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
        words = re.findall(r'\b\w+\b', content, flags=re.UNICODE)
        for w in words:
            w_lower = w.lower()
            if w_lower not in stop_words:
                term_table[w_lower][filename] += 1

        if progress_callback:
            progress_callback(i + 1, total_files)

    return doc_table, term_table

def save_doc_table_csv(doc_table, filepath="doc_table.csv"):
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Document'])
        for doc in doc_table:
            writer.writerow([doc])

def save_term_table_csv(term_table, filepath="term_table.csv"):
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Term', 'Document', 'Frequency'])
        for term, postings in term_table.items():
            for doc, freq in postings.items():
                writer.writerow([term, doc, freq])

def update_progress(current, total):
    percent = int(current / total * 100)
    progress['value'] = percent
    status_label.config(text=f"Creating inverted index... {percent}%")
    root.update_idletasks()

def hide_progress_widgets():
    progress.pack_forget()
    status_label.pack_forget()
    progress['value'] = 0

def create_index_thread():
    selected_dir = dir_path.get()
    stoplist_selected = default_stoplist
    if not selected_dir or not os.path.isfile(stoplist_selected):
        messagebox.showwarning("Warning", "Please select a document folder and ensure stoplist.txt is in the project folder.")
        hide_progress_widgets()
        status_label.config(text="Ready")
        return
    try:
        global docs, terms
        docs, terms = CreateIndex(selected_dir, stoplist_selected, progress_callback=update_progress)
        save_doc_table_csv(docs)
        save_term_table_csv(terms)
        status_label.config(text="Index creation completed.")
        root.after(1000, hide_progress_widgets)
    except Exception as e:
        messagebox.showerror("Error", f"Error when creating index:\n{e}")
        status_label.config(text="Error occurred during index creation.")
        hide_progress_widgets()

def show_progress_widgets():
    status_label.pack(fill="x", padx=20, pady=(5, 0))
    progress.pack(fill="x", padx=20, pady=(2, 10))

def create_index():
    show_progress_widgets()
    progress['value'] = 0
    status_label.config(text="Starting index creation...")
    threading.Thread(target=create_index_thread, daemon=True).start()

def open_index_window():
    if not docs or not terms:
        messagebox.showwarning("Warning", "You need to create the index before viewing.")
        return

    index_win = tk.Toplevel(root)
    index_win.title("Inverted Indexes")
    index_win.geometry("900x700")

    # DocTable
    tk.Label(index_win, text="DocTable").pack()
    frame_doc = tk.Frame(index_win)
    frame_doc.pack(fill="both", expand=True, padx=5, pady=5)

    tree_docs_win = ttk.Treeview(frame_doc, columns=("Document",), show='headings', height=10)
    tree_docs_win.heading("Document", text="Document")
    tree_docs_win.column("Document", width=600)
    tree_docs_win.pack(side=tk.LEFT, fill="both", expand=True)

    scrollbar_doc = ttk.Scrollbar(frame_doc, orient="vertical", command=tree_docs_win.yview)
    scrollbar_doc.pack(side=tk.RIGHT, fill="y")
    tree_docs_win.configure(yscrollcommand=scrollbar_doc.set)

    for doc in docs:
        tree_docs_win.insert("", "end", values=(doc,))

    # TermTable 
    tk.Label(index_win, text="TermTable").pack()
    frame_term_win = tk.Frame(index_win)
    frame_term_win.pack(fill="both", expand=True, padx=5, pady=5)

    tree_terms_win = ttk.Treeview(frame_term_win, columns=("Term", "Document", "Frequency"),
                                  show='headings', height=15)
    tree_terms_win.heading("Term", text="Term")
    tree_terms_win.heading("Document", text="Document")
    tree_terms_win.heading("Frequency", text="Frequency")
    tree_terms_win.column("Term", width=300)
    tree_terms_win.column("Document", width=350)
    tree_terms_win.column("Frequency", width=150)
    tree_terms_win.pack(side=tk.LEFT, fill="both", expand=True)

    scrollbar_term = ttk.Scrollbar(frame_term_win, orient="vertical", command=tree_terms_win.yview)
    scrollbar_term.pack(side=tk.RIGHT, fill="y")
    tree_terms_win.configure(yscrollcommand=scrollbar_term.set)

    for term, postings in terms.items():
        for doc, freq in postings.items():
            tree_terms_win.insert("", "end", values=(term, doc, freq))

    btn_back = tk.Button(index_win, text="Back", width=30, command=index_win.destroy)
    btn_back.pack(pady=10)

def Find(word, weight, N):
    word_lower = word.lower()
    if word_lower not in terms:
        return []
    postings = terms[word_lower]
    scored_docs = [(doc, freq * weight) for doc, freq in postings.items()]
    scored_docs.sort(key=lambda x: x[1], reverse=True)
    return scored_docs[:N]

def FindFromFile(wordfile, N):
    if not os.path.isfile(wordfile):
        messagebox.showerror("Error", f"File '{wordfile}' not found.")
        return []
    doc_scores = collections.defaultdict(float)

    with open(wordfile, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 2:
                continue
            word = parts[0].lower()
            try:
                weight = float(parts[1])
            except ValueError:
                continue

            if word not in terms:
                continue
            postings = terms[word]
            for doc, freq in postings.items():
                doc_scores[doc] += freq * weight
    sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_docs[:N]

def on_search():
    word = search_word_var.get().strip()
    try:
        weight = float(search_weight_var.get())
        N = int(search_N_var.get())
    except ValueError:
        messagebox.showerror("Error", "Please enter valid Weight and Top N values.")
        return
    if not word:
        messagebox.showerror("Error", "Please enter a search word.")
        return
    if not docs or not terms:
        messagebox.showwarning("Warning", "Please create the index first.")
        return

    results = Find(word, weight, N)
    if not results:
        messagebox.showinfo("No results", f"No documents found containing '{word}'.")
        search_result_tree.pack_forget()
        return

    if not search_result_tree.winfo_ismapped():
        search_result_tree.pack(padx=100, pady=(0, 20), fill="both", expand=True)

    for item in search_result_tree.get_children():
        search_result_tree.delete(item)

    for doc, score in results:
        search_result_tree.insert("", "end", values=(doc, round(score, 2)))

def on_file_search():
    wordfile = wordfile_path_var.get().strip()
    try:
        N = int(file_search_N_var.get())
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid Top N value.")
        return
    if not wordfile:
        messagebox.showerror("Error", "Please select a Word File.")
        return
    if not docs or not terms:
        messagebox.showwarning("Warning", "Please create the index first.")
        return

    results = FindFromFile(wordfile, N)
    if not results:
        messagebox.showinfo("No results", "No documents matched the query.")
        search_result_tree.pack_forget()
        return

    if not search_result_tree.winfo_ismapped():
        search_result_tree.pack(padx=100, pady=(0, 20), fill="both", expand=True)

    for item in search_result_tree.get_children():
        search_result_tree.delete(item)

    for doc, score in results:
        search_result_tree.insert("", "end", values=(doc, round(score, 2)))

root = tk.Tk()
root.geometry("900x700")
root.title("Inverted Indexes")

docs = []
terms = {}

dir_path = tk.StringVar()

frame_select = tk.Frame(root)
frame_select.pack(padx=(100, 0), pady=(30, 0), fill="x")
frame_select.pack_propagate(True)

entry_dir = tk.Entry(frame_select, textvariable=dir_path, state='readonly', width=100)
entry_dir.pack(side=tk.LEFT, fill="x", expand=True, ipady=3)

btn_browse = tk.Button(frame_select, text="Select Folder",
                       command=lambda: dir_path.set(filedialog.askdirectory()))
btn_browse.pack(side=tk.LEFT, expand=True, padx=(10, 100))

btn_create = tk.Button(root, text="Inverted Indexes", command=create_index)
btn_create.pack(pady=(5, 2), padx=150)

btn_show = tk.Button(root, text="Show Inverted Indexes", command=open_index_window)
btn_show.pack(pady=(5, 10))

frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=(5, 10), padx=150)

btn_find = tk.Button(frame_buttons, text="Find", command=lambda: search_frame.pack(padx=100, pady=10, fill="x"))
btn_find.pack(side=tk.LEFT, padx=(0, 10))

def toggle_file_search_frame():
    if file_search_frame.winfo_ismapped():
        file_search_frame.pack_forget()
        search_result_tree.pack_forget()
    else:
        file_search_frame.pack(padx=100, pady=(5, 15), fill="x")

btn_wordfile_search = tk.Button(frame_buttons, text="WordFile Search", command=toggle_file_search_frame)
btn_wordfile_search.pack(side=tk.LEFT)


search_frame = tk.Frame(root)

tk.Label(search_frame, text="Word:").pack(side=tk.LEFT)
search_word_var = tk.StringVar()
entry_word = tk.Entry(search_frame, textvariable=search_word_var, width=20)
entry_word.pack(side=tk.LEFT, padx=(5, 15))

tk.Label(search_frame, text="Weight:").pack(side=tk.LEFT)
search_weight_var = tk.DoubleVar(value=1.0)
entry_weight = tk.Entry(search_frame, textvariable=search_weight_var, width=12)
entry_weight.pack(side=tk.LEFT, padx=(5, 15))

tk.Label(search_frame, text="Top N:").pack(side=tk.LEFT)
search_N_var = tk.IntVar(value=5)
entry_N = tk.Entry(search_frame, textvariable=search_N_var, width=10)
entry_N.pack(side=tk.LEFT, padx=(5, 15))

btn_search = tk.Button(search_frame, text="Find", width=10, command=on_search)
btn_search.pack(side=tk.LEFT, padx=(5, 15))

def on_cancel():
    search_frame.pack_forget()
    search_result_tree.pack_forget()

btn_cancel = tk.Button(search_frame, text="Cancel", command=on_cancel)
btn_cancel.pack(side=tk.LEFT, padx=5)

search_result_tree = ttk.Treeview(root, columns=("Document", "Score"), show='headings', height=2)
search_result_tree.heading("Document", text="Document")
search_result_tree.heading("Score", text="Score")
search_result_tree.column("Document", width=300)
search_result_tree.column("Score", width=50, anchor="center")
search_result_tree.pack_forget()

# Frame tìm từ file
file_search_frame = tk.Frame(root)
file_search_frame.pack_forget()

tk.Label(file_search_frame, text="Word File:").pack(side=tk.LEFT)
wordfile_path_var = tk.StringVar()
entry_wordfile = tk.Entry(file_search_frame, textvariable=wordfile_path_var, width=60)
entry_wordfile.pack(side=tk.LEFT, padx=(5,10))

def browse_wordfile():
    filename = filedialog.askopenfilename(title="Select Word File", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if filename:
        wordfile_path_var.set(filename)

btn_browse_wordfile = tk.Button(file_search_frame, text="Browse", command=browse_wordfile)
btn_browse_wordfile.pack(side=tk.LEFT, padx=(0,10))

tk.Label(file_search_frame, text="Top N:").pack(side=tk.LEFT)
file_search_N_var = tk.IntVar(value=5)
entry_file_search_N = tk.Entry(file_search_frame, width=6, textvariable=file_search_N_var)
entry_file_search_N.pack(side=tk.LEFT, padx=(0,10))

btn_file_search = tk.Button(file_search_frame, text="Search from File", width=30, command=on_file_search)
btn_file_search.pack(side=tk.LEFT)

status_label = tk.Label(root, text="Ready", anchor="w")
progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")

status_label.pack(side=tk.BOTTOM, fill="x", padx=20, pady=(5, 0))
progress.pack(side=tk.BOTTOM, fill="x", padx=20, pady=(2, 10))

status_label.pack_forget()
progress.pack_forget()

root.mainloop()
