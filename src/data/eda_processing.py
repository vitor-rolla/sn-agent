import os
import glob
import tiktoken  # Biblioteca padrão para contagem rápida de tokens

def count_tokens_in_text(text, model_name="gpt-4o"):
    """Calcula o total de tokens em uma string de texto."""
    try:
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    
    return len(encoding.encode(text))

if __name__ == "__main__":
    # Ajustado para buscar arquivos .txt recursivamente
    path_pattern = os.path.join(os.getcwd(), 'data/Dataset_complete/**', '*.txt')
    txt_files = glob.glob(path_pattern, recursive=True)
 
    print(f"{'Arquivo':<50} | {'Tokens':<10}")
    print("-" * 65)

    total_tokens_dataset = 0

    for txt_file in txt_files:
        try:
            with open(txt_file, 'r', encoding='utf-8') as file:
                content = file.read()
                
                if content.strip():  # Verifica se o arquivo não está vazio
                    num_tokens = count_tokens_in_text(content)
                    total_tokens_dataset += num_tokens
                    
                    file_name = os.path.basename(txt_file)
                    print(f"{file_name:<50} | {num_tokens:<10}")
                else:
                    print(f"Aviso: Arquivo vazio ignorado: {os.path.basename(txt_file)}")
                    
        except Exception as e:
            print(f"Erro ao processar {txt_file}: {e}")

    print("-" * 65)
    print(f"{'TOTAL DO DATASET':<50} | {total_tokens_dataset:<10}")