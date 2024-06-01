import tkinter as tk
from tkinter import ttk

def on_select(event):
    selected_item = autocomplete_entry.get()
    suggestions = [suggestion for suggestion in suggestions_list if suggestion.startswith(selected_item)]
    autocomplete_entry['values'] = suggestions
    if suggestions:
        autocomplete_entry.set(suggestions[0])
        autocomplete_entry.icursor(len(selected_item))
    else:
        autocomplete_entry.icursor(0)

# Lista de sugestões
suggestions_list = ["apple", "banana", "orange", "grape", "pineapple", "watermelon", "kiwi", "strawberry"]

# Criar a janela
root = tk.Tk()
root.title("Autocomplete")

# Criar a entrada de texto com autocompletar
autocomplete_entry = ttk.Combobox(root, values=suggestions_list)
autocomplete_entry.pack(pady=10)
autocomplete_entry.bind("<FocusIn>", on_select)

root.mainloop()
