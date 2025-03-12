import tkinter as tk
from tkinter import ttk, messagebox
import re
import threading
from datetime import datetime
import webview  # PyWebView
from connect_email import connect_to_gmail, fetch_uber_receipts_by_month
from get_env import get_env
from email.utils import parsedate_to_datetime

emails_data = []
loader = None

# =========== EXEMPLOS DE PARSE =========== #
def parse_driver(content):
    match = re.search(r"Você viajou com\s+(.+?)(?=<|\n|$)", content, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return "Desconhecido"

def parse_address_lines(content):
    pattern = r"(\d{2}:\d{2})\s+([^<\n]+)"
    lines = re.findall(pattern, content)
    if len(lines) >= 2:
        embarque = lines[0][1].strip()
        destino = lines[1][1].strip()
        return embarque, destino
    return ("", "")

def parse_embarque(content):
    embarque, _ = parse_address_lines(content)
    return embarque

def parse_destino(content):
    _, destino = parse_address_lines(content)
    return destino

# =========== DEMAIS FUNÇÕES =========== #
def fix_html_colors(html):
    """Converte cores rgb(...) em hex no HTML, para evitar erros no tkhtmlview ou webview."""
    html = html.replace("##", "#")
    def rgb_to_hex(match):
        r = int(match.group(1))
        g = int(match.group(2))
        b = int(match.group(3))
        return f"#{r:02x}{g:02x}{b:02x}"
    return re.sub(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", rgb_to_hex, html)

def extract_trip_details(content):
    """
    Extrai o valor total e gorjeta de uma viagem, a partir de algo como:
      "Total: R$ 20,50"
      "Gorjeta: R$ 2,00"
    """
    total = 0.0
    tip = 0.0
    total_match = re.search(r"Total.*?R\$\s*([\d.,]+)", content, re.IGNORECASE)
    if total_match:
        amount_str = total_match.group(1).replace(".", "").replace(",", ".")
        try:
            total = float(amount_str)
        except ValueError:
            pass
    tip_match = re.search(r"(gorjeta|tip).*?R\$\s*([\d.,]+)", content, re.IGNORECASE)
    if tip_match:
        amount_str = tip_match.group(2).replace(".", "").replace(",", ".")
        try:
            tip = float(amount_str)
        except ValueError:
            pass
    return total, tip

def extract_recarga_amount(content):
    """
    Extrai valor de recarga de algo como:
      "Você adicionou R$ 50,00"
    """
    match = re.search(r"adicionou.*?R\$\s*([\d.,]+)", content, re.IGNORECASE)
    if match:
        amount_str = match.group(1).replace(".", "").replace(",", ".")
        try:
            return float(amount_str)
        except ValueError:
            return 0.0
    return 0.0

# Mapeia dias da semana
weekdays_pt = {
    0: "Segunda",
    1: "Terça",
    2: "Quarta",
    3: "Quinta",
    4: "Sexta",
    5: "Sábado",
    6: "Domingo"
}

def process_emails():
    """Converte data em dia/hora e classifica emails em 'viagem' ou 'recarga'."""
    global emails_data
    for item in emails_data:
        # Converte data
        try:
            dt = parsedate_to_datetime(item['date'])
            dia = f"{dt.strftime('%d')} - {weekdays_pt[dt.weekday()]}"
            hora = dt.strftime("%H:%M:%S")
            item['dia'] = dia
            item['hora'] = hora
        except Exception:
            item['dia'] = item['date']
            item['hora'] = ""

        # Verifica se é recarga ou viagem
        subject_lower = item['subject'].lower()
        content_lower = item['content'].lower()
        if "uber cash" in subject_lower or "uber cash" in content_lower:
            item['type'] = "recarga"
            recarga_val = extract_recarga_amount(item['content'])
            item['recarga'] = recarga_val
            item['driver'] = ""
            item['embarque'] = ""
            item['destino'] = ""
        else:
            # Trata como viagem
            item['type'] = "viagem"
            total, tip = extract_trip_details(item['content'])
            item['total'] = total
            item['tip'] = tip
            item['driver'] = parse_driver(item['content'])
            item['embarque'] = parse_embarque(item['content'])
            item['destino'] = parse_destino(item['content'])

def show_loader():
    """Exibe uma janela de carregamento centrada na tela."""
    global loader
    loader = tk.Toplevel(root)
    loader.title("Carregando")
    loader.geometry("200x100")

    # Centraliza o loader
    loader.update_idletasks()
    w = loader.winfo_width()
    h = loader.winfo_height()
    x = (loader.winfo_screenwidth() // 2) - (w // 2)
    y = (loader.winfo_screenheight() // 2) - (h // 2)
    loader.geometry(f"{w}x{h}+{x}+{y}")

    loader.transient(root)
    loader.grab_set()

    label = ttk.Label(loader, text="Carregando...", anchor="center", style="Dark.TLabel")
    label.pack(expand=True, fill="both", padx=10, pady=10)

    pb = ttk.Progressbar(loader, mode="indeterminate", style="Modern.Horizontal.TProgressbar")
    pb.pack(expand=True, fill="x", padx=10, pady=10)
    pb.start()

def hide_loader():
    """Fecha a janela de carregamento."""
    global loader
    if loader is not None:
        loader.destroy()
        loader = None

def update_dashboard():
    """
    Calcula e exibe o resumo no painel à direita:
      - Viagens e soma total
      - Gorjetas
      - Recargas
      - Total sem descontos
    """
    total_trip = 0.0
    total_tip = 0.0
    total_recarga = 0.0
    num_trips = 0
    num_recargas = 0

    # 'total_no_discounts' simula um valor sem descontos.
    # Para este exemplo, vamos somar (total + tip) para viagem,
    # pois assumimos que 'total' já possa ser um valor com desconto
    # e tip é a gorjeta.
    total_no_discounts = 0.0

    for item in emails_data:
        if item.get('type') == "viagem":
            t = item.get('total', 0.0)
            tip = item.get('tip', 0.0)
            total_trip += t
            total_tip += tip
            num_trips += 1
            # Para o "sem descontos", consideramos total + gorjeta
            total_no_discounts += (t + tip)
        elif item.get('type') == "recarga":
            r = item.get('recarga', 0.0)
            total_recarga += r
            num_recargas += 1
            # recarga não tem desconto, então soma normal
            total_no_discounts += r

    lbl_recargas.config(text=f"Recargas: R$ {total_recarga:.2f}")
    lbl_trips.config(text=f"Total: R$ {total_trip:.2f}")
    lbl_no_discounts.config(text=f"Total sem descontos: R$ {total_no_discounts:.2f}")

def load_emails():
    """Faz a busca dos emails, processa e atualiza a Treeview e o dashboard."""
    global emails_data
    try:
        my_email = get_env("MY_EMAIL")
        my_password = get_env("IMAP_KEY")
        mail = connect_to_gmail(my_email, my_password)
        
        month = int(month_entry.get())
        year = int(year_entry.get())
        
        emails_data = fetch_uber_receipts_by_month(mail, month, year)
        mail.logout()
        
        process_emails()
        
        # Limpa a Treeview
        tree.delete(*tree.get_children())
        
        if not emails_data:
            messagebox.showinfo("Info", "Nenhum email encontrado.")
        else:
            # Insere cada email na tabela
            for item in emails_data:
                classificacao = item['type'].capitalize()
                if item['type'] == "viagem":
                    valor = item.get('total', 0.0)
                    motorista = item.get('driver', "")
                    # Para viagens, valor com sinal negativo (simulando débito)
                    valor_str = f"-{valor:.2f}"
                    tag = "viagem"
                else:
                    valor = item.get('recarga', 0.0)
                    motorista = ""
                    # Para recargas, valor com sinal positivo
                    valor_str = f"+{valor:.2f}"
                    tag = "recarga"

                tree.insert("", "end", values=(
                    item['dia'],
                    item['hora'],
                    motorista,
                    valor_str,
                    classificacao
                ), tags=(tag,))
            # Atualiza o dashboard (painel à direita) com os dados
            update_dashboard()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao buscar emails: {e}")
    finally:
        search_button.config(state=tk.NORMAL)
        root.after(0, hide_loader)

def search_emails():
    """Inicia a busca dos emails em uma thread, mostrando loader."""
    search_button.config(state=tk.DISABLED)
    show_loader()
    threading.Thread(target=load_emails).start()

def open_email_preview(content):
    """Abre o email em uma janela webview."""
    if "<html" not in content.lower():
        content = f"<html><body>{content}</body></html>"
    content = fix_html_colors(content)
    window = webview.create_window("Email Preview", html=content, width=800, height=600)
    webview.start()

def on_tree_select(event):
    """Duplo clique na Treeview: exibe o email completo em WebView."""
    selection = tree.selection()
    if selection:
        item_id = selection[0]
        row_index = tree.index(item_id)
        email_item = emails_data[row_index]
        content = email_item["content"]
        open_email_preview(content)

col_titles = {
    "dia": "Dia",
    "hora": "Hora",
    "motorista": "Motorista",
    "valor": "Valor (R$)",
    "classificacao": "Classificação"
}

sort_state = {
    "col": None,
    "reverse": False
}

# 1) Função de ordenação
def sort_column(tree, col):
    # Se clicou na mesma coluna, inverte a ordem; senão começa ascendente
    if sort_state["col"] == col:
        reverse = not sort_state["reverse"]
    else:
        reverse = False

    # Extrai (valor_da_célula, item_id) para cada linha
    data = [(tree.set(item_id, col), item_id) for item_id in tree.get_children('')]

    # Tenta converter valor_da_célula para float para ordenar numericamente
    # se falhar, mantém string (ordem alfanumérica)
    try:
        data = [(float(x[0]), x[1]) for x in data]
    except ValueError:
        pass

    # Ordena e reposiciona
    data.sort(reverse=reverse)
    for index, (_, item_id) in enumerate(data):
        tree.move(item_id, '', index)

    # Atualiza o estado global
    sort_state["col"] = col
    sort_state["reverse"] = reverse

    # Remove setas de todos os cabeçalhos
    for c in col_titles:
        tree.heading(c, text=col_titles[c], command=lambda c=c: sort_column(tree, c))

    # Adiciona seta na coluna atual
    arrow = "▼" if reverse else "▲"
    new_heading = f"{col_titles[col]} {arrow}"
    tree.heading(col, text=new_heading, command=lambda c=col: sort_column(tree, c))

# =========== INÍCIO DA INTERFACE =========== #
root = tk.Tk()
root.withdraw()  # Oculta a janela até definirmos a posição
root.title("Visualizador de Emails - Recebidos da Uber")

# Tamanho padrão
w_main, h_main = 900, 600
root.geometry(f"{w_main}x{h_main}")

# Centraliza a janela principal
root.update_idletasks()
x_main = (root.winfo_screenwidth() // 2) - (w_main // 2)
y_main = (root.winfo_screenheight() // 2) - (h_main // 2)
root.geometry(f"{w_main}x{h_main}+{x_main}+{y_main}")
root.deiconify()

# --------- Estilo Geral --------- #
style = ttk.Style(root)
root.configure(bg="#f8f9fa")
style.configure(".", background="#f8f9fa", foreground="#212529", font=("Segoe UI", 10))

# Top bar (frame) com fundo escuro e texto branco
style.configure("Top.TFrame", background="#000")
style.configure("Top.TLabel", background="#000", foreground="#ffffff", font=("Segoe UI", 10, "bold"))
style.configure("Top.TButton", background="#000", foreground="#ffffff", font=("Segoe UI", 10, "bold"))

# Botões “comuns”
style.configure("Modern.TButton",
    background="#000000",
    foreground="#000000",
    font=("Segoe UI", 10, "bold"),
    borderwidth=0,
    focusthickness=3,
)

# Ajuste do Treeview
style.configure("Modern.Treeview",
                background="#ffffff",
                foreground="#212529",
                rowheight=30,
                fieldbackground="#ffffff")
style.map("Modern.Treeview",
          background=[("selected", "#000")],
          foreground=[("selected", "#ffffff")])

# Barra de progresso do loader
style.configure("Modern.Horizontal.TProgressbar", troughcolor="#f8f9fa", background="#000")

# Label escura no loader
style.configure("Dark.TLabel", background="#000", foreground="#fff")

# FRAME SUPERIOR (Top Bar)
top_frame = ttk.Frame(root, style="Top.TFrame", padding="10")
top_frame.pack(side=tk.TOP, fill=tk.X)

label_month = ttk.Label(top_frame, text="Mês (número):", style="Top.TLabel")
label_month.pack(side=tk.LEFT, padx=5)
month_entry = ttk.Entry(top_frame, width=5)
month_entry.pack(side=tk.LEFT, padx=5)

label_year = ttk.Label(top_frame, text="Ano:", style="Top.TLabel")
label_year.pack(side=tk.LEFT, padx=5)
year_entry = ttk.Entry(top_frame, width=5)
year_entry.pack(side=tk.LEFT, padx=5)

now = datetime.now()
month_entry.insert(0, str(now.month))
year_entry.insert(0, str(now.year))

search_button = ttk.Button(top_frame, text="Buscar Emails", command=search_emails, style="Modern.TButton")
search_button.pack(side=tk.LEFT, padx=10)

# FRAME PRINCIPAL: Divide em dois painéis (Tabela à esquerda, Dashboard à direita)
main_pane = ttk.Panedwindow(root, orient=tk.HORIZONTAL)
main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

left_frame = ttk.Frame(main_pane, style="TFrame")
right_frame = ttk.Frame(main_pane, style="TFrame", padding="10")

main_pane.add(left_frame, weight=3)
main_pane.add(right_frame, weight=1)

# ========== TREEVIEW (ESQUERDA) ==============================
columns = ("dia", "hora", "motorista", "valor", "classificacao")
tree = ttk.Treeview(left_frame, columns=columns, show="headings", style="Modern.Treeview")
tree.pack(fill=tk.BOTH, expand=True)

# Define o heading de cada coluna
tree.heading("dia", text="Dia", command=lambda: sort_column(tree, "dia"))
tree.heading("hora", text="Hora", command=lambda: sort_column(tree, "hora"))
tree.heading("motorista", text="Motorista", command=lambda: sort_column(tree, "motorista"))
tree.heading("valor", text="Valor (R$)", command=lambda: sort_column(tree, "valor"))
tree.heading("classificacao", text="Classificação", command=lambda: sort_column(tree, "classificacao"))

# Define a largura e alinhamento das colunas (exemplo)
tree.column("dia", width=100)
tree.column("hora", width=80)
tree.column("motorista", width=120)
tree.column("valor", width=80, anchor="e")
tree.column("classificacao", width=120)

# Configura as tags para diferenciar as cores
tree.tag_configure("viagem", foreground="red")
tree.tag_configure("recarga", foreground="green")

tree.bind("<Double-Button-1>", on_tree_select)

# ========== DASHBOARD (DIREITA) ==========
dashboard_title = ttk.Label(right_frame, text="Dashboard - Receitas Uber", font=("Segoe UI", 12, "bold"))
dashboard_title.pack(anchor="w", pady=(0,10))

lbl_recargas = ttk.Label(right_frame, text="Recargas:", font=("Segoe UI", 10))
lbl_recargas.pack(anchor="w", pady=5)

lbl_trips = ttk.Label(right_frame, text="Gasto:", font=("Segoe UI", 10))
lbl_trips.pack(anchor="w", pady=5)

# Novo label para “Total sem descontos”
lbl_no_discounts = ttk.Label(right_frame, text="Gasto sem descontos: R$ 0.00", font=("Segoe UI", 10))
lbl_no_discounts.pack(anchor="w", pady=5)


root.mainloop()
