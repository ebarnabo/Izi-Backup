import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import threading
import platform
import getpass
from concurrent import futures


class BackupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Backup App")
        self.target_paths = []
        self.selected_indices = []
        # Définir la fenêtre au premier plan
        self.root.attributes('-topmost', True)

        # Configuration du thème sombre
        root.config(bg="#2b2b2b")
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", background="#2b2b2b", foreground="white", font=('Arial', 10))
        style.configure("TButton", background="#333", foreground="white", font=('Arial', 10))
        style.configure("TEntry", background="white", foreground="black", font=('Arial', 10))
        style.configure("Custom.TButton", background=["#780000"], foreground=["#FFFFFF"], relief="flat",
                        margin=(0, 0, 0, 10))
        style.configure("Add.TButton", background="grey", foreground="white", relief="flat", margin=(0, 0, 0, 10))
        style.configure("Start.TButton", background="#003049", foreground="white", relief="flat", margin=(0, 0, 0, 10))
        style.configure("TProgressbar", troughcolor="#333", background="#11C23D")

        style.map("Custom.TButton",
                  foreground=[('hover', "#FFFFFF")],  # Remplacez par la couleur du texte souhaitée lors du survol
                  background=[('hover', "#C1121F")],  # Remplacez par la couleur de fond souhaitée lors du survol
                  )
        style.map("Add.TButton",
                  foreground=[('hover', "white")],  # Remplacez par la couleur du texte souhaitée lors du survol
                  background=[('hover', "darkgrey")],  # Remplacez par la couleur de fond souhaitée lors du survol
                  )
        style.map("Start.TButton",
                  foreground=[('hover', "#FFFFFF")],  # Remplacez par la couleur du texte souhaitée lors du survol
                  background=[('hover', "#669BBC")],  # Remplacez par la couleur de fond souhaitée lors du survol
                  )

        # Positionner la fenêtre au centre de l'écran
        window_width = 500
        window_height = 500
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

        self.target_label = ttk.Label(root, text="Déposer les fichiers ou dossiers cibles :", font=('Arial', 12, 'bold'),
                                      anchor='w')
        self.target_label.pack(fill='x', padx=10, pady=10)

        self.target_frame = tk.Frame(root, bg="#2b2b2b")
        self.target_frame.pack(fill='both', expand=True, padx=10)

        # Permettre le glisser-déposer de fichiers et dossiers
        self.target_frame.drop_target_register(DND_FILES)
        self.target_frame.dnd_bind('<<Drop>>', self.drop)

        self.target_scrollbar = ttk.Scrollbar(self.target_frame, orient='vertical')
        self.target_scrollbar.pack(side='right', fill='y')

        self.target_listbox = tk.Listbox(self.target_frame, selectbackground="#003049", selectforeground="white",
                                         font=('Arial', 10), bg="#2b2b2b", fg="white", yscrollcommand=self.target_scrollbar.set,
                                         selectmode=tk.MULTIPLE)
        self.target_listbox.pack(side='left', fill='both', expand=True)

        self.target_scrollbar.config(command=self.target_listbox.yview)

        self.target_button_folder = ttk.Button(root, text="+ Ajouter un dossier cible",
                                       command=self.add_target_folder, compound='left', style="Add.TButton")
        self.target_button_folder.pack(fill='x', padx=10, pady=5)

        self.remove_button = ttk.Button(root, text="Supprimer sélection", command=self.remove_selected_paths,
                                        style="Custom.TButton")
        self.remove_button.pack(fill='x', padx=10, pady=5)

        self.clear_button = ttk.Button(root, text="Vider la liste", command=self.clear_target_paths,
                                       style="Custom.TButton")
        self.clear_button.pack(fill='x', padx=10, pady=5)

        self.backup_label = ttk.Label(root, text="Dossier de sauvegarde :", font=('Arial', 12, 'bold'), anchor='w')
        self.backup_label.pack(fill='x', padx=10, pady=10)

        self.backup_entry = ttk.Entry(root, font=('Arial', 10))
        self.backup_entry.pack(fill='x', padx=10)

        self.backup_button = ttk.Button(root, text="Choisir le dossier de sauvegarde", command=self.choose_backup_folder , style="Add.TButton")
        self.backup_button.pack(fill='x', padx=10, pady=5)

        self.start_button = ttk.Button(root, text="Commencer la sauvegarde", command=self.start_backup , style="Start.TButton")
        self.start_button.pack(fill='x', padx=10, pady=10)

        self.progress = ttk.Progressbar(root, orient='horizontal', length=200, mode='determinate')
        self.progress.pack(fill='x', padx=10, pady=10)

        self.progress_label = ttk.Label(root, text="0%", font=('Arial', 10), anchor='w')
        self.progress_label.pack(fill='x', padx=10)

    def drop(self, event):
        paths = self.root.tk.splitlist(event.data)
        for p in paths:
            if os.path.isfile(p) or os.path.isdir(p):
                self.add_target_path(p)

    def add_target_files(self):
        paths = filedialog.askopenfilenames()  # For files
        for p in paths:
            self.add_target_path(p)

    def add_target_folder(self):
        path = filedialog.askdirectory()  # For folder
        self.add_target_path(path)

    def add_target_path(self, path):
        if path and path not in self.target_paths:
            self.target_paths.append(path)
            self.target_listbox.insert(tk.END, path)

    def remove_selected_paths(self):
        selected_indices = self.target_listbox.curselection()
        for index in reversed(selected_indices):
            path = self.target_paths[index]
            self.target_listbox.delete(index)
            self.target_paths.remove(path)

    def clear_target_paths(self):
        self.target_listbox.delete(0, tk.END)
        self.target_paths.clear()

    def choose_backup_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.backup_entry.delete(0, tk.END)
            self.backup_entry.insert(0, folder_path)

    def count_files(self, path):
        if os.path.isfile(path):
            return 1
        else:
            return sum([len(files) for root, dirs, files in os.walk(path)])

    def start_backup(self):
        backup_folder = self.backup_entry.get()
        if not backup_folder:
            messagebox.showwarning("Erreur", "Veuillez choisir un dossier de sauvegarde.")
            return

        total_files = sum(self.count_files(target_path) for target_path in self.target_paths)
        self.progress['maximum'] = total_files

        def copy_file(target_path):
            target_path_name = os.path.basename(target_path)
            backup_path = os.path.join(backup_folder, f"Backup_{platform.node()}_{getpass.getuser()}", target_path_name)

            if os.path.isfile(target_path):
                backup_dir = os.path.dirname(backup_path)
                os.makedirs(backup_dir, exist_ok=True)
                shutil.copy2(target_path, backup_path)
                return 1
            else:
                backup_dir = os.path.dirname(backup_path)
                os.makedirs(backup_dir, exist_ok=True)
                shutil.copytree(target_path, backup_path)
                return self.count_files(target_path)

        with futures.ThreadPoolExecutor() as executor:
            # Liste des tâches à exécuter en parallèle
            tasks = [executor.submit(copy_file, target_path) for target_path in self.target_paths]

            copied_files = 0
            for future in futures.as_completed(tasks):
                copied_files += future.result()
                self.progress['value'] = copied_files
                self.progress_label['text'] = f"{int(copied_files / total_files * 100)}%"
                self.progress.update()
                self.root.update_idletasks()

        messagebox.showinfo("Succès", "Sauvegarde terminée avec succès.")
        self.progress['value'] = 0
        self.progress_label['text'] = "0%"


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = BackupApp(root)

    root.mainloop()
