<!-- <div align="center">  
  <h1>  Contextual Privacy Toolkit </h1>

</div> -->

# Contextual Privacy Toolkit

The Contextual Privacy Toolkit provides a foundation for implementing contextual privacy in AI systems, with a focus on minimizing unnecessary data exposure while maintaining helpful and personalized interactions.

This toolkit is part of a broader effort to support **privacy-aware agentic workflows** — where decisions about what information to share are guided by the context and purpose of a task, not just static rules about sensitive data.

Our first implementation addresses a common issue at the user-to-agent boundary: overdisclosure, where users unknowingly share private details that may not be necessary to accomplish their goal. The toolkit introduces a lightweight privacy layer that analyzes user input, detects contextually unnecessary details, and reformulates prompts to preserve intent while minimizing disclosure.

---

<!-- ## Method Implemented -->



<!-- <div align="center">  
  <h2>Protecting Users From Themselves: Safeguarding Contextual Privacy in Interactions with Conversational Agents</h2>

📘[Read Paper](https://arxiv.org/pdf/2502.18509)   |   ✏️[Colab Quickstart](https://colab.research.google.com/drive/1wiRkvZcPk4w9XuPcr6jxQ5rGqR6zJitb?usp=sharing)   |   💼 [PyPI Package](https://pypi.org/project/contextual-privacy-llm/) -->


<!-- </div> -->

## Overview of the Method

####  Protecting Users From Themselves: Safeguarding Contextual Privacy in Interactions with Conversational Agents
[![Read Paper](https://img.shields.io/badge/Read%20Paper-PDF-yellow)](https://aclanthology.org/2025.findings-acl.1343.pdf) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1wiRkvZcPk4w9XuPcr6jxQ5rGqR6zJitb?usp=sharing) [![PyPI - Version](https://img.shields.io/pypi/v/contextual-privacy-llm)](https://pypi.org/project/contextual-privacy-llm/)

As conversational agents (e.g., LLMs) become more embedded in our daily lives, users increasingly reveal sensitive personal details—often unknowingly. Once shared, this information is vulnerable to memorization, misuse, third-party exposure, and incorporation into future model training. To mitigate this, we introduce a locally-deployable privacy guard that operates between users and LLMs. It identifies out-of-context private information and guides the user in reformulating prompts that maintain their goals while reducing unnecessary disclosure.

Inspired by the theory of Contextual Integrity, our framework goes beyond standard PII redaction by evaluating whether the shared information is contextually appropriate and necessary for achieving the user’s intent.

<p align="center">
  <img src="img/framework_overview.png" width="400"/>
</p>

---

## This Toolkit

This package allows you to:
    •   **Understand Context:** Detect the intent and task behind each user query to establish the privacy-relevant context.
    •   **Identify Sensitive Info:** Highlight details in the prompt that may be essential (relevant) or non-essential (unnecessary) for the intended goal.
    •   **Reformulate Prompts:** Remove or rephrase out-of-context information while preserving user intent.

All steps run locally, using small models that make real-time use feasible on the user side.

---

### Multiple Modes

We support two complementary modes of analysis:
    •  `dynamic` – the model adaptively decides what is essential based on how details are used in the prompt.
    •  `static` – a pre-defined list of sensitive attributes guides what should be protected, offering customizable control.


### Supported Prompt Templates

The system currently supports the following prompt templates:
    • `llama`  – for LLaMA models
    • `deepseek` – for DeepSeek models
    • `mixtral` – for Mistral models

If you use a model without a matching template, the system will automatically fall back to the `llama` prompt style. You don’t need to change anything — this helps ensure compatibility with a wide range of open-source LLMs.

---

## Quickstart

### Installation
We recommend using uv — a fast, modern package manager that handles both environment creation and dependency installation.

If you haven't installed it yet:

```bash
# Install uv (recommended)
curl -Ls https://astral.sh/uv/install.sh | sh

# or using Homebrew
brew install astral-sh/uv/uv
```
Then, install the toolkit:

```bash
# Create and activate a virtual environment
uv venv
source .venv/bin/activate  # On Linux/macOS
# .venv\Scripts\activate    # On Windows
```

Install the package:

```bash
# From PyPI
uv pip install contextual_privacy_llm
```
Or install from source:
```bash
git clone https://github.com/IBM/contextual-privacy-LLM.git
cd contextual_privacy_llm
uv pip install -e .
```
Requires Python 3.8+. You may optionally install Ollama or vLLM depending on the backend used.

### Start Ollama Serve
Before running the analysis, you should manually start the Ollama server and pull a compatible model:
```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.com/install.sh | sh

# Start ollama in the background (e.g on another terminal)
ollama serve
```
Then keep the server running in the background.

```bash
# Pull a model (example: LLaMA 3)
ollama pull llama3.2:3b-instruct-fp16

# (Optional) Test the model
ollama run llama3.2:3b-instruct-fp16 "Say hello"
```

### CLI

```bash
contextual-privacy-llm --query "I’m Jane, 35, a single mom with diabetes. Can I get treatment in France?"
# → "Can I get treatment in France as someone who has diabetes?"

```

### Python API

```python
from contextual_privacy_llm import PrivacyAnalyzer, run_single_query

analyzer = PrivacyAnalyzer(
    model="llama3.2:3b-instruct-fp16",
    prompt_template="llama",
    experiment="dynamic"
)

result = run_single_query(
    query_text="My child has autism and I’m in Paris. What support exists for moms like me?",
    query_id="001",
    model="llama3.2:3b-instruct-fp16",
    prompt_template="llama",
    experiment="dynamic"
)

print(result['reformulated_text'])
# → "What autism support exists for parents in Paris?"

print(result)

# → {
# →   "query_id": "001",
# →   "original_text": "My child has autism and I’m in Paris. What support exists for moms like me?",
# →   "intent": "support_seeking",
# →   "task": "resource_lookup",
# →   "related_context": ["autism", "Paris"],
# →   "not_related_context": ["moms like me", "my child"],
# →   "reformulated_text": "What autism support exists in Paris?"
# → }
```

---
## Colab Demos
Run lightweight examples in Google Colab:

* [Ollama backend (Llama 3)](https://colab.research.google.com/drive/1wiRkvZcPk4w9XuPcr6jxQ5rGqR6zJitb?usp=sharing)
<!-- * [vLLM backend (DeepSeek)](https://colab.research.google.com/vllm) -->

---
## Models Tested
The system has been tested with the following model configurations:
### In Colab Notebooks:
- llama3.2:3b-instruct-fp16
- llama3.2:3b
- LoTUs5494/mistral-small-3.1:24b
- mistral:7b-instruct-q4_0
  
### In Our Paper:
- mixtral:8x7b-instruct-v0.1-fp16
- llama3.1:8b-instruct-fp16
- deepseek-r1:8b

Note: Prompt templates (llama, deepseek, mixtral) may require tuning for other model variants.

---
## Project Structure

```
├── contextual_privacy_llm/         # Core module: analyzer, rules, reformulation logic
│   ├── analyzer.py                   # Main logic for contextual privacy classification
│   ├── runner.py                     # CLI runner
│   ├── patterns/                     # Task and intent pattern matchers
│   │   ├── intent_patterns.py
│   │   ├── task_patterns.py
│   ├── prompts/                      # Prompt templates for different models
│   │   ├── llama/
│   │   ├── deepseek/
│   │   └── mixtral/
│   └── __init__.py
|
├── requirements.txt                  # Required Python packages
├── setup.py                          # Installation script
├── MANIFEST.in                       # Package data manifest
├── LICENSE
└── README.md                         # You're here!
```

---

## Citation

If you use this work in your research, please cite:

```
@inproceedings{ngong-etal-2025-protecting,
    title = {Protecting Users From Themselves: Safeguarding Contextual Privacy in Interactions with Conversational Agents},
    author = {Ngong, Ivoline C.  and
      Kadhe, Swanand Ravindra  and
      Wang, Hao  and
      Murugesan, Keerthiram  and
      Weisz, Justin D.  and
      Dhurandhar, Amit  and
      Natesan Ramamurthy, Karthikeyan},
    booktitle = {Findings of the Association for Computational Linguistics: ACL 2025},
    month = jul,
    year = "2025",
    address = {Vienna, Austria},
    publisher = {Association for Computational Linguistics},
    url = {https://aclanthology.org/2025.findings-acl.1343/},
    pages = {26196--26220},
}
```

## License

This project is licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).
