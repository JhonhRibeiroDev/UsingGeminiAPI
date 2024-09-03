import os
from dotenv import load_dotenv 
import google.generativeai as genai

load_dotenv()
api_key = os.getenv('API_KEY')
genai.configure(api_key=api_key)
# Constantes
FILE_PATH = 'roteiro - Inglês (teste).txt'
CHUNK_SIZE = 5000
CONTEXT_SIZE = 40
CHUNKS_OUTPUT_DIR = 'cortes'
TRANSLATED_OUTPUT_DIR = 'Cortes_traduzidos'

def read_file(file_path):
    """Lê o conteúdo de um arquivo de texto e retorna como uma string."""
    print(f"Lendo o arquivo de texto: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def split_text(text, chunk_size=CHUNK_SIZE):
    """Divide o texto em blocos com no máximo chunk_size caracteres."""
    print(f"Dividindo o texto em blocos de até {chunk_size} caracteres.")
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        
        # Ajusta o corte para evitar cortar palavras ao meio
        if end < len(text):
            while end > start and text[end] not in (' ', '.', ',', '\n', '!', '?'):
                end -= 1
        
        # Adiciona o bloco somente se não estiver vazio
        chunk = text[start:end].strip()
        if chunk:  # Verifica se o bloco não está vazio
            chunks.append(chunk)
            print(f"Corte no texto: {start} a {end} caracteres. Comprimento do bloco: {len(chunk)}")
        
        start = end
    
    return chunks

def save_chunks(chunks, output_dir):
    """Salva os blocos de texto em arquivos .txt na pasta especificada."""
    os.makedirs(output_dir, exist_ok=True)
    for i, chunk in enumerate(chunks):
        chunk_file = os.path.join(output_dir, f'chunk_{i + 1}.txt')
        with open(chunk_file, 'w', encoding='utf-8') as file:
            file.write(chunk)
        print(f"Bloco {i + 1} salvo em: {chunk_file}")

def save_translated_text(text, output_dir):
    """Salva o texto traduzido em um arquivo na pasta especificada."""
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'translated_text.txt')
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(text)
    print(f"Texto traduzido salvo em: {output_file}")

def translate_text(text):
    """Traduz o texto usando a API Gemini."""
    print(f"Enviando bloco para tradução. Comprimento do texto: {len(text)} caracteres.")

    # Adiciona a instrução ao prompt
    prompt = f"Apenas Traduza o seguinte texto do inglês para o português, sem resumos, só o texto traduzido, sem topicos, so texto o traduzido:  {text}"
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        translated_text = response.text.strip()  # Recupera o texto traduzido
        print(f"Texto traduzido com sucesso. Comprimento do texto traduzido: {len(translated_text)} caracteres.")
        return translated_text
    except Exception as e:
        print(f"Erro ao traduzir o texto: {e}")
        return ""

def process_text(file_path=FILE_PATH, chunk_size=CHUNK_SIZE, context_size=CONTEXT_SIZE):
    """Processa o texto do arquivo, dividindo-o em blocos, traduzindo cada bloco e mantendo o contexto."""
    print("Iniciando processamento do texto.")
    text = read_file(file_path)
    chunks = split_text(text, chunk_size)
    save_chunks(chunks, CHUNKS_OUTPUT_DIR)
    
    translated_text = ""
    context = ""
    
    for i, chunk in enumerate(chunks):
        print(f"\nProcessando bloco {i + 1}/{len(chunks)}")
        
        # Adiciona o contexto ao início do bloco, se houver
        if context:
            chunk = context + chunk
        
        # Traduz o bloco
        translated_chunk = translate_text(chunk)
        
        # Exibe o bloco traduzido no console
        print(f"\nBloco traduzido {i + 1}:")
        print(translated_chunk)
        
        translated_text += translated_chunk + "\n\n\n"
        
        # Atualiza o contexto para o próximo bloco
        context = chunk[-context_size:]
    
    print("Processamento concluído.")
    
    # Salva o texto traduzido em um arquivo separado
    save_translated_text(translated_text, TRANSLATED_OUTPUT_DIR)

# Exemplo de uso
process_text()
