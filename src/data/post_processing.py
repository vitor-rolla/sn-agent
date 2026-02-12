import json
import os

model_name = "gpt-4o-mini"

data = json.load(open(f'data/results/{model_name}/raw_results.json')) 

consolidated = {}

for path, content in data.items():
    # Extrai o nome da pasta (o nome do jogo)
    game_name = os.path.basename(os.path.dirname(path))
    
    if game_name not in consolidated:
        consolidated[game_name] = []
    
    # Adiciona os gols à lista do jogo correspondente
    consolidated[game_name].extend(content['gols'])

with open(f'data/results/{model_name}/final_results.json', 'w', encoding='utf-8') as f:
    json.dump(consolidated, f, indent=4, ensure_ascii=False)