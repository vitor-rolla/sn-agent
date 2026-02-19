import json
import os
import glob
import tomllib
from typing import List, Literal
from pydantic import BaseModel, Field
import google.generativeai as genai

# Configurações de modelo
model_name = "gemini-2.5-flash-lite"
prompt_name = "complex"

# Load API key from ~/.streamlit/secrets.toml
secrets_path = os.path.expanduser("~/.streamlit/secrets.toml")
with open(secrets_path, "rb") as f:
    secrets = tomllib.load(f)
    # Certifique-se de que a chave no .toml seja GEMINI_API_KEY ou ajuste abaixo
    gemini_api_key = secrets.get("GEMINI_API_KEY") or secrets.get("OPENAI_API_KEY")

genai.configure(api_key=gemini_api_key)

# --- Definição dos Schemas (Pydantic) ---

class Gol(BaseModel):
    minute: int = Field(
        description="Game minute as an integer (0-100)"
    )
    player: str = Field(description="Player who scored the goal")
    club: str = Field(description="Player's club")
    type: Literal["Finalization", "Header", "Penalty", "Free kick", "Own goal", "Bicycle"] = Field(
        description="Goal type. Choose strictly from the allowed list."
    )

class ListaGols(BaseModel):
    gols: List[Gol]

# --- Funções de Apoio ---

def carregar_prompt(prompt_name: str = "default") -> str:
    caminho_prompt = os.path.join(os.getcwd(), f"data/prompts/{prompt_name}.txt")
    if not os.path.exists(caminho_prompt):
        raise FileNotFoundError(f"Arquivo de prompt não encontrado: {caminho_prompt}")
    with open(caminho_prompt, "r", encoding="utf-8") as f:
        return f.read()

def gerar_resposta_llm(narrativa, prompt_name: str = "default"):
    """
    Usa o SDK do Google Generative AI com response_mime_type 
    para garantir o retorno estruturado via Pydantic.
    """
    try:
        prompt_content = carregar_prompt(prompt_name)
        
        # Inicializa o modelo com a configuração de resposta estruturada
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=prompt_content
        )
        
        # O Gemini usa 'response_schema' para garantir a estrutura
        response = model.generate_content(
            narrativa,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=ListaGols,
                temperature=0.1
            )
        )
        
        # Converte a string JSON de resposta de volta para o objeto Pydantic
        return ListaGols.model_validate_json(response.text)
        
    except Exception as e:
        print(f"❌ Erro crítico na API Gemini: {e}")
        return None

def processar_narrativas(lista_arquivos: List[str]):
    resultados_globais = {}
    for caminho_arquivo in lista_arquivos:
        if not os.path.exists(caminho_arquivo):
            continue
            
        print(f"Processando: {os.path.basename(caminho_arquivo)}...")
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            narrativa = f.read()
            
        objeto_gols = gerar_resposta_llm(narrativa, prompt_name=prompt_name)

        if objeto_gols:
            resultados_globais[caminho_arquivo] = objeto_gols.model_dump()
        else:
            resultados_globais[caminho_arquivo] = {"gols": []}
            
    return resultados_globais


narrative_files = glob.glob(os.path.join(os.getcwd(), 'data/Dataset_complete/**', 'n_consolidated.txt'), recursive=True)

dicionario_final = processar_narrativas(narrative_files)

output_path = f'data/results/{model_name}/{prompt_name}/raw_results.json'
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(dicionario_final, f, indent=4, ensure_ascii=False)

