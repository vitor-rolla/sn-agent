import json
import os
from typing import List, Literal
from pydantic import BaseModel, Field, ValidationError
from openai import OpenAI
import glob
import tomllib

model_name = "gpt-5-nano"

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


def gerar_resposta_llm(narrativa):
    """
    Usa Structured Outputs (SDK v1.40+) para garantir fidelidade ao Pydantic.
    """
    try:
        # O método .parse substitui o .create quando usamos Pydantic
        completion = client.beta.chat.completions.parse(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": """Role: You are a specialized Soccer Data Analyst. Your task is to extract real-time goal events from match narratives into a structured format.
                        Extraction Logic & Constraints:
                        - Deduplication: Extract each goal ONLY ONCE. Distinguish between live action and subsequent recaps/summaries.
                        - Validation: Only include confirmed goals. Ignore disallowed goals (VAR/Offside).
                        - Minute: Use integers (0-100). For stoppage time like 90+3, use 93.
                        - Goal Type: Strictly use: "Finalization", "Header", "Penalty", "Free kick", "Own goal", "Bicycle".
                        - Own Goals: Identify carefully; the 'club' field must be the team that gained the point."""
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
        objeto_gols = gerar_resposta_llm(narrativa)
        if objeto_gols:
            # .model_dump() transforma o objeto Pydantic em dicionário Python
            resultados_globais[caminho_arquivo] = objeto_gols.model_dump()
        else:
            # Caso a API falhe por algum motivo externo
            resultados_globais[caminho_arquivo] = {"gols": []}
    return resultados_globais

narrative_files = glob.glob(os.path.join(os.getcwd(), 'data/Dataset_complete/**', 'n_consolidated.txt'), recursive=True)

dicionario_final = processar_narrativas(narrative_files)

with open(f'data/results/{model_name}/raw_results.json', 'w', encoding='utf-8') as f:
    json.dump(dicionario_final, f, indent=4, ensure_ascii=False)