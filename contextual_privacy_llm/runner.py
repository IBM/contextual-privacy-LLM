import json
import argparse
from contextual_privacy_llm.analyzer import PrivacyAnalyzer
from typing import Dict, Any

def run_single_query(query_text: str, 
                     query_id: str = "1", 
                     model: str = 'llama3.1:8b-instruct-fp16', 
                     prompt_template: str = 'llama',
                     experiment: str = 'dynamic') -> Dict[str, Any]:
    """
    Run a full contextual privacy analysis pipeline on a single user query.

    This includes:
    - Detecting the user's intent
    - Identifying the underlying task
    - Extracting essential vs. non-essential (sensitive) information
    - Reformulating the prompt to remove non-essential sensitive info

    Args:
        query_text (str): The original input query from the user.
        query_id (str): Unique identifier for the query.
        model (str): Model name served by Ollama (e.g., 'llama3.1:8b-instruct-fp16').
        prompt_template (str): Template folder to use (e.g., 'llama', 'deepseek').
        experiment (str): 'static' or 'dynamic' template variant.

    Returns:
        Dict[str, Any]: A dictionary containing all analysis results, including reformulated text.
    """
    
    analyzer = PrivacyAnalyzer(
        model=model,
        prompt_template=prompt_template,
        experiment=experiment,
        output_dir="outputs_single"
    )

    # Detect intent
    _, intent = analyzer.detect_intent(query_text, query_id)
    # Detect task
    _, task = analyzer.detect_task(query_text, query_id)
    # Detect sensitive information
    _, sensitive_info = analyzer.detect_sensitive_info(query_text, intent, task, query_id)
    # Reformulate if needed
    related = sensitive_info.get('related_context', [])
    not_related = sensitive_info.get('not_related_context', [])
    reformulated = query_text
    if not_related:
        _, reformulated = analyzer.reformulate_prompt(query_text, sensitive_info, intent, task, query_id)

    return {
        "query_id": query_id,
        "original_text": query_text,
        "intent": intent,
        "task": task,
        "related_context": sensitive_info.get('related_context', []),
        "not_related_context": sensitive_info.get('not_related_context', []),
        "reformulated_text": reformulated
    }

def main():
    parser = argparse.ArgumentParser(description='Contextual Privacy CLI')
    parser.add_argument('--query', required=True)
    parser.add_argument('--id', default='1')
    parser.add_argument('--model', default='llama3.1:8b-instruct-fp16')
    parser.add_argument('--prompt-template', default='llama')
    parser.add_argument('--experiment', default='dynamic')
    args = parser.parse_args()
    result = run_single_query(
        args.query, 
        args.id, 
        args.model, 
        args.prompt_template, 
        args.experiment
    )
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()