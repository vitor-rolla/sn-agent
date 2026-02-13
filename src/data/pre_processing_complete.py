import json
import os
import glob
from collections import defaultdict

def compound_text(json_file):
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    if 'segments' in data:
        # Extrai o terceiro elemento (índice 2) de cada segmento
        return [data["segments"][key][2] for key in data["segments"]]
    return []

if __name__ == "__main__":
    # 1. Mapeamos os arquivos por pasta
    path_pattern = os.path.join(os.getcwd(), 'data/Dataset_complete/**', '*.json')
    json_files = glob.glob(path_pattern, recursive=True)
    
    files_by_folder = defaultdict(list)
    for f in json_files:
        files_by_folder[os.path.dirname(f)].append(f)

    # 2. Processamos cada pasta individualmente
    for folder, files in files_by_folder.items():
        all_narratives = []
        print(f"Processando pasta: {folder} ({len(files)} arquivos)")

        for json_file in files:
            narrative = compound_text(json_file)
            if narrative:
                all_narratives.extend(narrative)

        # 3. Se houver conteúdo, salvamos um único arquivo na pasta
        if all_narratives:
            # Define o nome do arquivo final baseado no nome da pasta
            folder_name = os.path.basename(folder)
            output_path = os.path.join(folder, "n_consolidated.txt")
            
            with open(output_path, "w", encoding="utf-8") as arquivo:
                arquivo.write(" ".join(all_narratives))
            print(f"Salvo: {output_path}")