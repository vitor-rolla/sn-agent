import json
import os
from typing import List, Literal
from pydantic import BaseModel, Field, ValidationError
import requests
import glob

model_name = "gemma3:27b"  # Change this to your Ollama model name
ollama_api_url = "http://10.105.158.17:11434"  # Ollama server URL

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


def gerar_resposta_llm(narrativa, previous_output=None, error_msg=None):
    # Endpoint de CHAT é mais organizado que o de GENERATE
    url = f"{ollama_api_url}/api/chat"
    
    system_content = (
        "Extract soccer goals into JSON. Rules:\n"
        "- 'minute': int (0-100)\n"
        "- 'type': MUST be 'Finalization', 'Header', 'Penalty', 'Free kick', 'Own goal', or 'Bicycle'\n"
        "- If no goals: {\"gols\": []}\n"
        "Return ONLY valid JSON."
    )

    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": f"Narrative: {narrativa}"}
    ]

    # Se for uma tentativa de correção, adicionamos o histórico do erro
    if previous_output and error_msg:
        messages.append({"role": "assistant", "content": previous_output})
        messages.append({
            "role": "user", 
            "content": f"Your previous JSON is invalid. Error: {error_msg}. Please fix it and return ONLY the valid JSON."
        })

    payload = {
        "model": model_name,
        "messages": messages,
        "stream": False,
        "format": "json", # ISSO GARANTE QUE O OLLAMA TENTE ENTREGAR JSON
        "options": {
            "temperature": 0.1 # Temperatura baixa para extração de dados (mais determinístico)
        }
    }

    response = requests.post(url, json=payload)
    response.raise_for_status()
    
    # No endpoint de chat, a resposta vem em message -> content
    result = response.json()
    return result.get("message", {}).get("content", "")

def processar_narrativas(lista_arquivos: List[str], max_retries=3):
    resultados_globais = {}

    for caminho_arquivo in lista_arquivos:

        if not os.path.exists(caminho_arquivo):
            print(f"⚠️ No file found: {caminho_arquivo}")
            continue

        print(f"Searching: {caminho_arquivo}...")

        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            narrativa = f.read()

        previous_output = None

        for tentativa in range(1, max_retries + 1):

            try:

                if tentativa == 1:
                    # primeira geração
                    raw_output = gerar_resposta_llm(narrativa)
                else:
                    # correção baseada no erro anterior
                    raw_output = gerar_resposta_llm(
                        narrativa,
                        previous_output=previous_output,
                        error_msg=error_msg
                    )

                dados_extraidos = ListaGols.model_validate_json(raw_output)

                resultados_globais[caminho_arquivo] = dados_extraidos.model_dump()
                break  # sucesso

            except ValidationError as e:

                error_msg = str(e)
                previous_output = raw_output

                print(f"⚠️ Attempt {tentativa} failed.")
                print(error_msg)

                if tentativa == max_retries:
                    print(f"❌ Failed after {max_retries} attempts.")
                    resultados_globais[caminho_arquivo] = {"gols": []}

    return resultados_globais

narrative_files = glob.glob(os.path.join(os.getcwd(), 'data/Dataset_complete/**', '*.txt'), recursive=True)

dicionario_final = processar_narrativas(narrative_files)

with open(f'data/results/{model_name}/raw_results.json', 'w', encoding='utf-8') as f:
    json.dump(dicionario_final, f, indent=4, ensure_ascii=False)