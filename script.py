import os
from dotenv import load_dotenv 
import google.generativeai as genai
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

load_dotenv()
api_key = os.getenv('API_KEY')
genai.configure(api_key=api_key)

CHUNK_SIZE = 5000
CONTEXT_SIZE = 40

def read_file(file_path):
    """Lê o conteúdo de um arquivo de texto e retorna como uma string."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def split_text(text, chunk_size=CHUNK_SIZE):
    """Divide o texto em blocos com no máximo chunk_size caracteres."""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        
        # Ajusta o corte para evitar cortar palavras ao meio
        if end < len(text):
            while end > start and text[end] not in (' ', '.', ',', '\n', '!', '?'):
                end -= 1
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end
    
    return chunks

def save_chunks(chunks, output_dir):
    """Salva os blocos de texto em arquivos .txt na pasta especificada."""
    os.makedirs(output_dir, exist_ok=True)
    for i, chunk in enumerate(chunks):
        chunk_file = os.path.join(output_dir, f'chunk_{i + 1}.txt')
        with open(chunk_file, 'w', encoding='utf-8') as file:
            file.write(chunk)

def save_translated_text(text, output_dir, title):
    """Salva o texto traduzido em um arquivo na pasta especificada."""
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f'{title}.txt')
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(text)

def translate_text(text):
    """Traduz o texto usando a API Gemini."""
    prompt = f"Apenas Traduza o seguinte texto do inglês para o português, sem resumos, só o texto traduzido, sem topicos, so texto o traduzido:  {text}"
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Erro ao traduzir o texto: {e}")
        return ""

def process_text(file_path, chunk_size=CHUNK_SIZE, context_size=CONTEXT_SIZE, chunks_output_dir='cortes', translated_output_dir='Cortes_traduzidos', title='translated_text'):
    """Processa o texto do arquivo, dividindo-o em blocos, traduzindo cada bloco e mantendo o contexto."""
    text = read_file(file_path)
    chunks = split_text(text, chunk_size)
    save_chunks(chunks, chunks_output_dir)
    
    translated_text = ""
    context = ""
    
    for i, chunk in enumerate(chunks):
        if context:
            chunk = context + chunk
        
        translated_chunk = translate_text(chunk)
        
        translated_text += translated_chunk + "\n\n\n"
        
        context = chunk[-context_size:]
    
    save_translated_text(translated_text, translated_output_dir, title)

def browse_file():
    """Abre um diálogo para selecionar um arquivo .txt."""
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)

def browse_folder():
    """Abre um diálogo para selecionar uma pasta."""
    folder_path = filedialog.askdirectory()
    if folder_path:
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, folder_path)

def process():
    """Inicia o processamento do texto com os parâmetros fornecidos na interface."""
    file_path = file_entry.get()
    output_dir = folder_entry.get()
    title = simpledialog.askstring("Título do arquivo", "Digite o título do arquivo final:")
    
    if not file_path or not output_dir or not title:
        messagebox.showwarning("Aviso", "Por favor, preencha todos os campos.")
        return
    
    chunks_output_dir = os.path.join(output_dir, 'cortes')
    translated_output_dir = os.path.join(output_dir, 'Cortes_traduzidos')
    
    process_text(file_path, chunks_output_dir=chunks_output_dir, translated_output_dir=translated_output_dir, title=title)
    messagebox.showinfo("Concluído", "Processamento concluído!")

# Configura a interface gráfica
root = tk.Tk()
root.title("Tradutor de Textos Grandes")

# Configura o layout
tk.Label(root, text="Arquivo .txt:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
file_entry = tk.Entry(root, width=50)
file_entry.grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Procurar", command=browse_file).grid(row=0, column=2, padx=5, pady=5)

tk.Label(root, text="Pasta de saída:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
folder_entry = tk.Entry(root, width=50)
folder_entry.grid(row=1, column=1, padx=5, pady=5)
tk.Button(root, text="Procurar", command=browse_folder).grid(row=1, column=2, padx=5, pady=5)

tk.Button(root, text="Processar", command=process).grid(row=2, column=1, padx=5, pady=10)

root.mainloop()
