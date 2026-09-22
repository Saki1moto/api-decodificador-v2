import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import pandas as pd
from googlenewsdecoder import gnewsdecoder

class DecodificadorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Decodificador de Links - Google News")
        self.root.geometry("650x550")
        
        style = ttk.Style()
        style.theme_use("clam")

        tk.Label(
            root, 
            text="Cole os links do Google News abaixo (um por linha):", 
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.txt_input = tk.Text(root, height=8, font=("Consolas", 9))
        self.txt_input.pack(fill="x", padx=15, pady=5)

        self.btn_decode = tk.Button(
            root, 
            text="🚀 Decodificar Links", 
            command=self.iniciar_decodificacao, 
            bg="#2b5c8f", 
            fg="white", 
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=10,
            pady=5
        )
        self.btn_decode.pack(pady=10)

        self.lbl_status = tk.Label(root, text="", font=("Segoe UI", 9, "italic"))
        self.lbl_status.pack(pady=2)

        self.tree = ttk.Treeview(root, columns=("Original", "Decodificado"), show="headings")
        self.tree.heading("Original", text="Link Original")
        self.tree.heading("Decodificado", text="Link Decodificado")
        self.tree.column("Original", width=250)
        self.tree.column("Decodificado", width=350)
        self.tree.pack(fill="both", expand=True, padx=15, pady=5)

        self.btn_export = tk.Button(
            root, 
            text="📥 Exportar para Excel / CSV", 
            command=self.exportar_arquivo, 
            state="disabled",
            bg="#2e7d32", 
            fg="white", 
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=10,
            pady=3
        )
        self.btn_export.pack(pady=10)

        self.resultados = []

    def iniciar_decodificacao(self):
        texto = self.txt_input.get("1.0", tk.END).strip()
        links = [l.strip().replace('"', '').replace("'", "") for l in texto.splitlines() if l.strip()]

        if not links:
            messagebox.showwarning("Aviso", "Por favor, cole pelo menos um link válido!")
            return

        self.btn_decode.config(state="disabled")
        self.btn_export.config(state="disabled")
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        self.resultados = []
        threading.Thread(target=self.processar_links, args=(links,), daemon=True).start()

    def processar_links(self, links):
        total = len(links)
        for i, link in enumerate(links, 1):
            self.lbl_status.config(text=f"Processando {i} de {total}...")
            
            try:
                res = gnewsdecoder(link, interval=1)
                if res and res.get("status"):
                    decodificado = res["decoded_url"]
                else:
                    msg = res.get('message') if res else 'Falha na resposta'
                    decodificado = f"Erro: {msg}"
            except Exception as e:
                decodificado = f"Erro: {str(e)}"

            self.resultados.append({"Link Original": link, "Link Decodificado": decodificado})
            self.tree.insert("", "end", values=(link, decodificado))
            time.sleep(0.5)

        self.lbl_status.config(text="✅ Processamento concluído!")
        self.btn_decode.config(state="normal")
        self.btn_export.config(state="normal")

    def exportar_arquivo(self):
        if not self.resultados:
            return
            
        caminho = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Arquivo Excel", "*.xlsx"), ("Arquivo CSV", "*.csv")]
        )
        
        if caminho:
            df = pd.DataFrame(self.resultados)
            if caminho.endswith(".csv"):
                df.to_csv(caminho, index=False)
            else:
                df.to_excel(caminho, index=False)
            messagebox.showinfo("Sucesso", "Arquivo salvo com sucesso!")

if __name__ == "__main__":
    root = tk.Tk()
    app = DecodificadorApp(root)
    root.mainloop()
