import json
import re
from difflib import SequenceMatcher

model_name = "gemini-3-flash-preview"
prompt_name = "complex"


def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def normalize_name(name):
    if not name: return ""
    return re.sub(r'[^\w\s]', '', name).lower().strip()

def similarity(a, b):
    return SequenceMatcher(None, normalize_name(a), normalize_name(b)).ratio()

def analyze_performance(gt_data, pred_data):
    results = {
        "matches_found": 0,
        "perfect_matches": 0,
        "total_gt_goals": 0,
        "total_pred_goals": 0,
        "correct_goals": 0,
        "wrong_player": 0,
        "wrong_team": 0,
        "wrong_minute": 0
    }
    gt_map = {item['data']: item for item in gt_data}
    for pred_key, pred_goals in pred_data.items():
        if pred_key in gt_map:
            results["matches_found"] += 1
            gt_goals = gt_map[pred_key]['gols']
            results["total_gt_goals"] += len(gt_goals)
            results["total_pred_goals"] += len(pred_goals)
            # Comparar gols (abordagem simplificada por proximidade)
            matched_gt_indices = set()
            correct_goals_in_this_match = 0
            for p_gol in pred_goals:
                best_match = None
                best_score = 0
                for i, g_gol in enumerate(gt_goals):
                    if i in matched_gt_indices: continue
                    player_score = similarity(p_gol['player'], g_gol['jogador'])
                    team_score = similarity(p_gol['club'], g_gol['time'])
                    # player_score = similarity(p_gol.get('player', ''), g_gol.get('jogador', ''))
                    # team_score = similarity(p_gol.get('team', ''), g_gol.get('time', ''))
                    combined_score = (player_score * team_score)
                    # print(p_gol['player'], g_gol['jogador'])
                    if combined_score > best_score:
                        best_score = combined_score
                        best_match = i
                if best_score > 0.7:  # Threshold de aceitação
                    matched_gt_indices.add(best_match)
                    correct_goals_in_this_match += 1
                    results["correct_goals"] += 1
                else:
                    # Opcional: Logar se o erro foi especificamente no time ou jogador
                    pass
            # --- VALIDAÇÃO DE JOGO PERFEITO ---
            # 1. O número de gols deve ser igual ao do gabarito
            # 2. Todos os gols previstos devem ter sido validados
            if len(gt_goals) == len(pred_goals) == correct_goals_in_this_match:
                results["perfect_matches"] += 1
    # Cálculos Finais
    tp = results["correct_goals"]
    fp = results["total_pred_goals"] - tp
    fn = results["total_gt_goals"] - tp
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    return {
        "metrics": {"precision": precision, "recall": recall, "f1_score": f1},
        "counts": results
    }

gt = load_json('data/ground_truth.json')
pred = load_json(f'data/results/{model_name}/{prompt_name}/final_results.json')
report = analyze_performance(gt, pred)
print("### RELATÓRIO DE MÉTRICAS ###")
print(f"F1-Score Geral: {report['metrics']['f1_score']:.2%}")
print(f"Precisão (Gols corretos / Gols previstos): {report['metrics']['precision']:.2%}")
print(f"Recall (Gols encontrados / Gols reais): {report['metrics']['recall']:.2%}")
print("-" * 30)
print(f"Gols no Gabarito: {report['counts']['total_gt_goals']}")
print(f"Gols Extraídos: {report['counts']['total_pred_goals']}")
print(f"Gols validados (TP): {report['counts']['correct_goals']}")
print("-" * 30)
print(f"F1-Score Geral: {report['metrics']['f1_score']:.2%}")
print(f"Jogos com Placar Exato (100% acerto): {report['counts']['perfect_matches']}")
print(f"Total de jogos analisados: {report['counts']['matches_found']}")
emr = (report['counts']['perfect_matches'] / report['counts']['matches_found']) if report['counts']['matches_found'] > 0 else 0
print(f"Exact Match Rate (Jogos 100% corretos): {emr:.2%}")
