# SN-Agent: Soccer Narratives Agent

<p align="center">
    <a href=""><img src="https://github.com/vitor-rolla/sn-agent/blob/main/src/app/logo.jpg" width="50%"></a>
    <a href=""><img src="https://github.com/vitor-rolla/sn-agent/blob/main/src/app/intro-fig.png" width="50%"></a>
</p>

<div style="display: flex; justify-content: center; gap: 10px;">
    <img src="https://github.com/vitor-rolla/sn-agent/blob/main/src/app/logo.jpg" width="50%">
    <img src="https://github.com/vitor-rolla/sn-agent/blob/main/src/app/intro-fig.png" width="50%">
</div>

## Project Overview

SN-Echoes leverages multiple LLM providers (OpenAI GPT, Google Gemini, and Ollama) to parse natural language soccer commentary into structured data. The system includes data preprocessing, model querying, evaluation metrics, and an interactive Streamlit application for real-time analysis.

---

## 📁 Project Structure

### Root Directory

- **`pyproject.toml`**: Project configuration file defining dependencies, project metadata, and Python version requirements. Includes packages like `openai`, `google-generativeai`, `ollama`, `streamlit`, and `haystack-ai`.
- **`packages.txt`**: System-level package dependencies (if any).
- **`README.md`**: This documentation file.

---

### 📊 `data/`

Contains all datasets, ground truth data, prompts, and results.

#### Files:
- **`games.csv`**: CSV file containing game metadata (dates, teams, scores).
- **`ground_truth.json`**: Ground truth annotations for evaluation, containing verified goal events and match data.

#### Subdirectories:

##### `data/Dataset/`
Subset of soccer match data with limited games (e.g., "2016-08-20 - Leicester 0 - 0 Arsenal"). Each subdirectory contains JSON files with extracted subtitles/narratives from YouTube videos.

##### `data/Dataset_complete/`
Complete dataset with full season games from 2016-2017 (Arsenal, Liverpool, Chelsea, Leicester, Manchester United, etc.). Each folder is named by date and match (e.g., "2016-08-14 - Arsenal 3 - 4 Liverpool") and contains JSON files with subtitle segments.

##### `data/prompts/`
Contains prompt templates for different extraction strategies:
- **`default.txt`**: Standard extraction prompt focusing on deduplication and validation
- **`literal.txt`**: Literal extraction approach with minimal interpretation
- **`complex.txt`**: Advanced prompt for complex goal event extraction

##### `data/results/`
Stores output files and results from model queries and evaluations.

---

### 💻 `src/`

Source code directory containing all Python modules.

#### `src/app/`

Application layer with the user interface.

- **`sn-app.py`**: Streamlit web application for interactive YouTube video analysis. Features include:
  - YouTube subtitle extraction using yt-dlp
  - Multi-model support (OpenAI GPT-4, Gemini)
  - Prompt selection interface
  - Real-time goal event extraction
  - Visual results display

- **`logo.jpg`**: Application logo displayed in the sidebar

#### `src/data/`

Data processing and transformation scripts.

- **`pre_processing_complete.py`**: Processes complete dataset JSON files by extracting narrative segments from multiple files in each game folder and compounding them into unified text representations.

- **`pre_processing_half_time.py`**: Similar to complete preprocessing but focuses on half-time analysis, processing game data by half periods.

- **`post_processing.py`**: Handles post-processing of model outputs, likely cleaning and structuring extracted goal data for evaluation.

- **`eda_processing.py`**: Exploratory Data Analysis (EDA) script for analyzing dataset characteristics, distributions, and statistics.

#### `src/model/`

LLM integration modules for different AI providers.

- **`gemini_query.py`**: Google Gemini API integration. Uses Pydantic schemas to define structured output for goal events (minute, player, club, type). Supports models like `gemini-2.5-pro` and `gemini-3-flash-preview`.

- **`openai_query.py`**: OpenAI GPT API integration (GPT-4o, GPT-4o-mini). Implements structured extraction using OpenAI's function calling or structured outputs.

- **`ollama_query.py`**: Local LLM integration using Ollama (supports models like Qwen, Llama). Enables running inference locally without API costs.

#### `src/evaluation/`

Evaluation and metrics computation.

- **`metrics_gols.py`**: Computes performance metrics for goal extraction accuracy:
  - Match detection (games correctly identified)
  - Perfect matches (exact goal details)
  - Correct goals vs wrong player/team/minute
  - Name similarity matching using SequenceMatcher
  - Configurable for different models and prompts

#### `src/results/`

Result analysis and visualization scripts.

- **`final_game_score.py`**: Generates comparison visualizations of model performance across different prompts. Uses matplotlib and seaborn to create bar plots comparing accuracy across:
  - Multiple Gemini versions
  - GPT-4o variants
  - Different prompt strategies (Default, Literal, Complex)

- **`goals_name_club.py`**: Analyzes and visualizes goal extraction accuracy by player name and club.

- **`goals_name_club_time_type.py`**: Extended analysis including time and goal type dimensions (Finalization, Header, Penalty, Free kick, Own goal, Bicycle).

---

## 🚀 Getting Started

### Prerequisites

- Python >= 3.12
- API Keys for:
  - OpenAI (optional)
  - Google Gemini (optional)
  - Local Ollama installation (optional)

### Installation

1. Clone the repository:
```bash
cd /home/vitor-rolla/ml_projects/sn-agent
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -e .
```

4. Configure API keys in `~/.streamlit/secrets.toml`:
```toml
OPENAI_API_KEY = "your-openai-key"
GOOGLE_API_KEY = "your-gemini-key"
GEMINI_API_KEY = "your-gemini-key"
```

### Running the Application

```bash
streamlit run src/app/sn-app.py
```

### Running Evaluations

```bash
# Run Gemini extraction
python src/model/gemini_query.py

# Run OpenAI extraction
python src/model/openai_query.py

# Run Ollama extraction
python src/model/ollama_query.py

# Evaluate results
python src/evaluation/metrics_gols.py
```

### Generating Visualizations

```bash
python src/results/final_game_score.py
python src/results/goals_name_club_time_type.py
```

---

## 📈 Workflow

1. **Data Collection**: YouTube videos with soccer match commentary
2. **Preprocessing**: Extract and structure subtitle data (`pre_processing_*.py`)
3. **Extraction**: Query LLMs with prompts to extract goal events (`*_query.py`)
4. **Evaluation**: Compare extracted data with ground truth (`metrics_gols.py`)
5. **Visualization**: Generate performance charts (`final_game_score.py`)
6. **Interactive Use**: Use Streamlit app for real-time analysis (`sn-app.py`)

---

## 🎯 Key Features

- **Multi-Model Support**: Compare performance across GPT-4, Gemini, and local LLMs
- **Prompt Engineering**: Test different extraction strategies (default, literal, complex)
- **Structured Extraction**: Pydantic-validated outputs ensure data consistency
- **Performance Metrics**: Comprehensive evaluation of accuracy, precision, and recall
- **Interactive Interface**: User-friendly Streamlit app for YouTube video analysis
- **Visualization**: Clear charts showing model comparison results

---

## 📊 Evaluation Metrics

The system evaluates models on:
- **Match Detection Rate**: Percentage of games correctly identified
- **Perfect Match Rate**: Exact matches for all goal attributes
- **Goal Accuracy**: Correct goals extracted vs total ground truth
- **Attribute Accuracy**: Separate metrics for player names, teams, minutes, and goal types
- **Name Similarity**: Fuzzy matching for player name variations

---

## 🔬 Research Applications

This project is useful for:
- Benchmarking LLM performance on structured extraction tasks
- Studying prompt engineering effectiveness
- Comparing commercial vs open-source models
- Analyzing sports data extraction from natural language
- Building automated sports analytics pipelines

---

## 📝 License

This project is part of ML research at UFMG (Universidade Federal de Minas Gerais).

---

## 🤝 Contributing

For questions or contributions, please refer to the project documentation or contact the maintainers.
