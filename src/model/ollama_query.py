import json
import os
from typing import List, Literal
from pydantic import BaseModel, Field, ValidationError
import requests
import glob

model_name = "qwen3:4b"
prompt_name = "literal"

# ollama_api_url = "http://10.105.158.17:11434"  # Ollama server URL
ollama_api_url = "http://localhost:11434"  # Ollama server URL

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


def gerar_resposta_llm(narrativa, prompt_name, previous_output=None, error_msg=None):
    url = f"{ollama_api_url}/api/chat"
    
    # 1. Carrega o prompt base
    base_system_content = carregar_prompt(prompt_name)
    
    # 2. Se houver erro anterior, injetamos o aviso NO SYSTEM PROMPT (mais autoridade)
    # Em vez de criar um diálogo longo, damos uma instrução corretiva direta.
    if error_msg:
        instrucao_correcao = (
            f"\n\nIMPORTANT: Your last attempt failed validation with error: {error_msg}.\n"
        )
        system_content = base_system_content + instrucao_correcao
    else:
        system_content = base_system_content

    # 3. Mantemos a estrutura simples (Stateless)
    # Isso evita que o modelo tente "explicar" o erro anterior dentro do JSON
    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": f"Narrative to process:\n{narrativa}"}
    ]

    payload = {
        "model": model_name,
        "messages": messages,
        "stream": False,
        "format": ListaGols.model_json_schema(), # Força o decoder-level enforcement
        "options": {
            "temperature": 0.0,       # Máximo determinismo para extração
            "num_ctx": 8192,          # Aumentado para modelos maiores (30B+)
            "num_predict": 1000,      # Espaço para listas longas de gols
            "top_k": 20,
            "top_p": 0.9
        }
    }

    try:
        # Aumentei o timeout para 300s. Modelos de 30B em infra comum podem demorar no prefill.
        response = requests.post(url, json=payload, timeout=300)
        response.raise_for_status()
        
        content = response.json().get("message", {}).get("content", "")
        
        # Limpeza extra: Às vezes o modelo coloca markdown mesmo com o format:json
        content = content.replace("```json", "").replace("```", "").strip()
        
        return content
    except requests.exceptions.Timeout:
        print(f"❌ Timeout no modelo {model_name}. Narrativa muito longa ou hardware lento.")
        return ""
    except Exception as e:
        print(f"❌ Erro na chamada ao Ollama: {e}")
        return ""

def processar_narrativas(lista_arquivos: List[str], max_retries=3):
    resultados_globais = {}

    for caminho_arquivo in lista_arquivos:
        if not os.path.exists(caminho_arquivo):
            continue

        print(f"🔍 Processing: {os.path.abspath(caminho_arquivo)}")
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            narrativa = f.read()

        raw_output = None
        error_msg = None

        for tentativa in range(1, max_retries + 1):
            raw_output = gerar_resposta_llm(narrativa, prompt_name, previous_output=raw_output, error_msg=error_msg)
            
            try:
                # Validação rigorosa com Pydantic
                dados_extraidos = ListaGols.model_validate_json(raw_output)
                resultados_globais[caminho_arquivo] = dados_extraidos.model_dump()
                print(f"✅ Success on attempt {tentativa}")
                print(resultados_globais[caminho_arquivo])
                break 
            
            except ValidationError as e:
                # Extrai apenas as mensagens de erro relevantes para economizar tokens de feedback
                error_details = e.errors()
                error_msg = "; ".join([f"Loc: {err['loc']} - {err['msg']}" for err in error_details])
                print(f"⚠️ Attempt {tentativa} failed validation: {error_msg}")

                if tentativa == max_retries:
                    print(f"❌ Abandoning file after {max_retries} failed attempts.")
                    resultados_globais[caminho_arquivo] = {"gols": []}

    return resultados_globais

narrative_files = glob.glob(os.path.join(os.getcwd(), 'data/Dataset_complete/**', 'n_consolidated.txt'), recursive=True)

dicionario_final = processar_narrativas(narrative_files)

output_path = f'data/results/{model_name}/{prompt_name}/raw_results.json'
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(dicionario_final, f, indent=4, ensure_ascii=False)

