# SN-Agent: Soccer Narratives Agent

<p align="center">
    <a href=""><img src="https://github.com/vitor-rolla/sn-agent/blob/main/src/app/intro-fig.png" width="80%"></a>
</p>

## Project Overview

SN-Agent benchmarks multiple LLMs from OpenAI and Google Gemini to parse natural language soccer commentary into structured data. The system includes data preprocessing, model querying, evaluation metrics, and an interactive Streamlit application for real-time analysis.

- Demo video:<a href="https://youtu.be/RlaRQrty4bs"> https://youtu.be/RlaRQrty4bs</a>
- Online App:<a href="https://sn-narratives.streamlit.app"> https://sn-narratives.streamlit.app</a>
- Repo:<a href="https://github.com/vitor-rolla/sn-agent"> https://github.com/vitor-rolla/sn-agent</a>

---

## 📁 Project Structure


### 📊 `data/`

Contains the dataset, ground truth data, prompts, and results.

#### Files:
- **`games.csv`**: CSV file containing game metadata (dates, teams, scores).
- **`ground_truth.json`**: Ground truth annotations for evaluation, containing verified goal events and match data.

#### Subdirectories:

##### `data/dataset/`
Subset of two soccer match data for short evaluation purposes. Each subdirectory contains files with extracted subtitles/narratives.

##### `data/dataset_complete/`
Complete dataset with 49 season games from 2016-2017. Each folder is named by date and match (e.g., "2016-08-14 - Arsenal 3 - 4 Liverpool") and contains files with subtitle segments.

##### `data/prompts/`
Contains prompt templates for different extraction strategies:
- **`default.txt`**: Standard extraction approach
- **`literal.txt`**: Literal extraction approach
- **`complex.txt`**: Complex extraction approach

##### `data/results/`
Stores output files and results from model queries and evaluations.

---

### 💻 `src/`

Source code directory containing all Python modules.

#### `src/app/`

Application layer with the user interface.

- **`sn-app.py`**: Streamlit web application for interactive YouTube video analysis.

#### `src/data/`

Data processing and transformation scripts.

- **`pre_processing_complete.py`**: Processes complete dataset JSON files by extracting narrative segments from multiple files in each game folder and compounding them into unified text representations.

- **`pre_processing_half_time.py`**: Similar to complete preprocessing but focuses on half-time analysis, processing game data by half periods.

- **`post_processing.py`**: Handles post-processing of model outputs for metrics evaluation agains the ground truth.

- **`eda_processing.py`**: Exploratory Data Analysis (EDA) script for analyzing dataset characteristics, distributions, and statistics.

#### `src/model/`

LLM modules for different providers.

- **`gemini_query.py`**: Google Gemini query.

- **`openai_query.py`**: OpenAI GPT query.

- **`ollama_query.py`**: Local LLM query.

#### `src/evaluation/`

Evaluation and metrics computation.

- **`metrics_gols.py`**: Computes performance metrics for goal extraction for relaxed and strict evaluation.

#### `src/results/`

Result analysis and visualization scripts.

- **`final_game_score.py`**: Generates comparison visualizations of model performance across different prompts. 

---

#### API Keys

Configure your API keys in `~/.streamlit/secrets.toml`:

OPENAI_API_KEY = "your-openai-key"

GOOGLE_API_KEY = "your-gemini-key"

