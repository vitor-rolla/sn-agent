import json
import os
from typing import List, Literal
from pydantic import BaseModel, Field, ValidationError
from openai import OpenAI
import glob
import tomllib

model_name = "o3"
prompt_name = "default"

# Load API key from ~/.streamlit/secrets.toml
secrets_path = os.path.expanduser("~/.streamlit/secrets.toml")
with open(secrets_path, "rb") as f:
    secrets = tomllib.load(f)
    openai_api_key = secrets["OPENAI_API_KEY"]

client = OpenAI(api_key=openai_api_key)

class Gol(BaseModel):
    minute: int = Field(
        description="Game minute as an integer (0-100)", 
        ge=0, 
        le=100
    )
    player: str = Field(description="Player who scored the goal")
    club: str = Field(description="Player's club")
    type: Literal["Finalization", "Header", "Penalty", "Free kick", "Own goal", "Bicycle"] = Field(
        description="Goal type. Choose strictly from the allowed list."
    )

class ListaGols(BaseModel):
    gols: List[Gol]


def carregar_prompt(prompt_name: str = "default") -> str:
    caminho_prompt = os.path.join(os.getcwd(), f"data/prompts/{prompt_name}.txt")
    
    if not os.path.exists(caminho_prompt):
        raise FileNotFoundError(f"Arquivo de prompt não encontrado: {caminho_prompt}")
    
    with open(caminho_prompt, "r", encoding="utf-8") as f:
        return f.read()


def gerar_resposta_llm(narrativa, prompt_name: str = "default"):
    """
    Usa Structured Outputs (SDK v1.40+) para garantir fidelidade ao Pydantic.
    
    Args:
        narrativa: Texto da narrativa do jogo
        prompt_name: Nome do arquivo de prompt a usar (sem extensão .txt)
    """
    try:
        # Carrega o prompt do arquivo
        prompt_content = carregar_prompt(prompt_name)
        
        # O método .parse substitui o .create quando usamos Pydantic
        completion = client.beta.chat.completions.parse(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": prompt_content
                },
                {"role": "user", "content": narrativa}
            ],
            response_format=ListaGols, # Passa a classe diretamente aqui
            #temperature=0.1, # Recomendado para extração de dados
        )
        return completion.choices[0].message.parsed
    except Exception as e:
        print(f"❌ Erro crítico na API: {e}")
        return None

def processar_narrativas(lista_arquivos: List[str]):
    resultados_globais = {}
    for caminho_arquivo in lista_arquivos:
        if not os.path.exists(caminho_arquivo):
            continue
        print(f"Processando: {os.path.basename(caminho_arquivo)}...")
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            narrativa = f.read()
        # Agora a validação acontece dentro da chamada da API
        objeto_gols = gerar_resposta_llm(narrativa, prompt_name=prompt_name)
        if objeto_gols:
            # .model_dump() transforma o objeto Pydantic em dicionário Python
            resultados_globais[caminho_arquivo] = objeto_gols.model_dump()
        else:
            # Caso a API falhe por algum motivo externo
            resultados_globais[caminho_arquivo] = {"gols": []}
    return resultados_globais

narrative_files = glob.glob(os.path.join(os.getcwd(), 'data/Dataset_complete/**', 'n_consolidated.txt'), recursive=True)

dicionario_final = processar_narrativas(narrative_files)

output_path = f'data/results/{model_name}/{prompt_name}/raw_results.json'
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(dicionario_final, f, indent=4, ensure_ascii=False)