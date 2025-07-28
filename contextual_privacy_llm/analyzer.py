import json
import requests
import re
import os
from typing import List, Dict, Tuple, Any, Union
from datetime import datetime
import time

import logging
logger = logging.getLogger("contextual_privacy_llm")
logger.setLevel(logging.WARNING)

from contextual_privacy_llm.patterns.intent_patterns import INTENT_PATTERNS
from contextual_privacy_llm.patterns.task_patterns import TASK_PATTERNS

def _extract_thinking_output(response: str) -> Tuple[str, str]:
    """
    Extracts the "thinking" and the output from the response.
    """
    if "<think>" in response and "</think>" in response:
        parts = response.split("</think>")
        thinking = re.sub(r'^.*?<think>', '', parts[0], flags=re.DOTALL).strip()
        output = parts[1].strip()
    elif "</think>" in response:
        idx = response.find("</think>")
        thinking = response[:idx].strip()
        output = response[idx + len("</think>"):].strip()
    elif "<think>" in response:
        idx = response.find("<think>")
        thinking = response[idx + len("<think>"):].strip()
        output = response[:idx].strip()
    else:
        thinking = ""
        output = response.strip()
    return thinking, output

class PrivacyAnalyzer:
    """
    Main analyzer class to detect intent, task, sensitive context,
    and to reformulate user prompts using LLMs.
    """
    def __init__(self, 
                 model: str = 'deepseek-r1:8b', 
                 prompt_template: str = 'deepseek',
                 experiment: str = 'dynamic',
                 output_dir: str = 'json_outputs'):
        self.model = model
        self.prompt_template = prompt_template  # Folder name: deepseek, llama, mixtral
        self.experiment = experiment            # "dynamic" or "static"

        self.host = os.getenv('OLLAMA_API_HOST', 'localhost')
        self.api_url = f"http://{self.host}:11434/api/generate"
        
        # Load patterns
        self.intent_patterns = INTENT_PATTERNS
        self.task_patterns = TASK_PATTERNS

        # Setup directories
        self.output_dir = output_dir
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.run_dir = os.path.join(output_dir, self.timestamp)
        os.makedirs(self.run_dir, exist_ok=True)

        # Precompile regex patterns
        self.compiled_intent_patterns = {
            intent: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
            for intent, patterns in INTENT_PATTERNS.items()
        }
        self.compiled_task_patterns = {
            task: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
            for task, patterns in TASK_PATTERNS.items()
        }

        # Supported prompt templates
        available_templates = {"llama", "deepseek", "mixtral"}

        # Fallback to 'llama' if the given prompt_temp              late is unknown
        if self.prompt_template not in available_templates:
            logger.warning(f"Unknown prompt template '{self.prompt_template}' for model '{self.model}'. Falling back to 'llama'.")
            self.prompt_template = "llama"  
                
        self.load_prompts()

    def load_prompts(self):
        """Load prompt files based on the prompt_template folder and experiment type."""
        self.prompts = {}
        base_prompt_dir = os.path.join(os.path.dirname(__file__), 'prompts', self.prompt_template)
        try:
            with open(os.path.join(base_prompt_dir, 'intent_detection.txt'), 'r') as f:
                self.prompts['intent'] = f.read()
            with open(os.path.join(base_prompt_dir, 'task_detection.txt'), 'r') as f:
                self.prompts['task'] = f.read()
            with open(os.path.join(base_prompt_dir, 'sensitive_info.txt'), 'r') as f:
                self.prompts['sensitive'] = f.read()
            with open(os.path.join(base_prompt_dir, 'reformulation.txt'), 'r') as f:
                self.prompts['reformulation'] = f.read()
            
            # For sensitive info related prompts, choose based on experiment type.
            if self.experiment == 'static':
                with open(os.path.join(base_prompt_dir, 'essential_info_static.txt'), 'r') as f:
                    self.prompts['sensitive_info_related'] = f.read()
                with open(os.path.join(base_prompt_dir, 'non_essential_info_static.txt'), 'r') as f:
                    self.prompts['sensitive_info_nonrelated'] = f.read()
            else:  # default to dynamic
                with open(os.path.join(base_prompt_dir, 'essential_info.txt'), 'r') as f:
                    self.prompts['sensitive_info_related'] = f.read()
                with open(os.path.join(base_prompt_dir, 'non_essential_info.txt'), 'r') as f:
                    self.prompts['sensitive_info_nonrelated'] = f.read()
        except Exception as e:
            raise Exception(f"Failed to load prompt templates: {str(e)}")

    def _call_ollama(self, prompt: str) -> Union[str, None]:
        """
        Call the Ollama API with a prompt and return the LLM response.
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 1000
            }
        }
        try:
            response = requests.post(self.api_url, json=payload, timeout=60)
            response.raise_for_status()
            response_text = response.text
            lines = [line for line in response_text.split('\n') if line.strip()]
            responses = [json.loads(line)['response'] for line in lines]
            return ''.join(responses)
        except Exception as e:
            logger.debug(f"Error calling Ollama API: {e}")
            return None

    def _retry_operation(self, operation_name: str, operation_func, *args, max_retries: int = 2) -> Tuple[Any, bool]:
        """
        Retry an operation up to `max_retries` times, with debug logging.
        """
        for attempt in range(max_retries + 1):
            try:
                result = operation_func(*args)
                if result is not None:
                    if attempt > 0:
                        logger.debug(f"Succeeded on retry {attempt} for {operation_name}")
                    return result, True
                raise Exception("Operation returned None")
            except Exception as e:
                if attempt < max_retries:
                    logger.debug(f"Attempt {attempt + 1} failed for {operation_name}. Retrying... Error: {e}")
                else:
                    logger.debug(f"All {max_retries + 1} attempts failed for {operation_name}. Skipping... Error: {e}")
                    return None, False

    def detect_intent(self, text: str, conversation_id: str) -> Tuple[str, str]:
        """
        Use LLM to detect user intent from input text.
        Fallback to pattern matching if raw prediction is ambiguous.
        """
        def _detect():
            prompt = self.prompts['intent'].format(input_text=text)
            response = self._call_ollama(prompt)
            if not response:
                return None
            thinking, raw_intent = _extract_thinking_output(response)
            # Try exact match first.
            for intent in self.intent_patterns.keys():
                if intent.lower() == raw_intent.lower():
                    return thinking, intent
            # Then substring match.
            for intent in self.intent_patterns.keys():
                if intent.lower() in raw_intent.lower():
                    return thinking, intent
            # Fallback: pattern matching.
            logger.debug("No direct intent found, using pattern matching")
            text_to_analyze = raw_intent.lower()
            intent_matches = {}
            for intent, patterns in self.intent_patterns.items():
                matches = sum(1 for pattern in patterns if re.search(pattern, text_to_analyze, re.IGNORECASE))
                if matches > 0:
                    intent_matches[intent] = matches
            if intent_matches:
                best_intent = max(intent_matches.items(), key=lambda x: x[1])[0]
                return thinking, best_intent
            logger.debug(f"Could not determine intent from response: {raw_intent}")
            return None

        result, success = self._retry_operation("intent detection", _detect)
        return result if success else (None, None)

    def detect_task(self, text: str, conversation_id: str) -> Tuple[str, str]:
        """
        Use LLM to detect user task from input text.
        Fallback to pattern matching if raw prediction is ambiguous.
        """
        def _detect():
            prompt = self.prompts['task'].format(text=text)
            response = self._call_ollama(prompt)
            if not response:
                return None
            thinking, raw_task = _extract_thinking_output(response)
            for task in self.task_patterns.keys():
                if task.lower() == raw_task.lower():
                    return thinking, task
            for task in self.task_patterns.keys():
                if task.lower() in raw_task.lower():
                    return thinking, task
            logger.debug("No direct task found, using pattern matching")
            text_to_analyze = raw_task.lower()
            task_matches = {}
            for task, patterns in self.task_patterns.items():
                matches = sum(1 for pattern in patterns if re.search(pattern, text_to_analyze, re.IGNORECASE))
                if matches > 0:
                    task_matches[task] = matches
            if task_matches:
                best_task = max(task_matches.items(), key=lambda x: x[1])[0]
                return thinking, best_task
            logger.debug(f"Could not determine task from response: {raw_task}")
            return None

        result, success = self._retry_operation("task detection", _detect)
        return result if success else (None, None)

    def detect_sensitive_info(self, text: str, intent: str, task: str, conversation_id: str) -> Tuple[str, Dict]:
        """Detect sensitive info."""
        
        def normalize_text(text: str) -> str:
            """Normalize text for comparison."""
            text = text.lower()
            text = re.sub(r'[^\w\s-]', '', text)  # Remove punctuation except dashes
            text = re.sub(r'\b(\d+)(st|nd|rd|th)\b', r'\1', text)  # Normalize ordinal numbers
            return ' '.join(text.split())

        def are_similar(item1: str, item2: str) -> bool:
            """Check if two items are similar enough to be considered duplicates."""
            norm1, norm2 = normalize_text(item1), normalize_text(item2)
            
            # Exact match
            if norm1 == norm2:
                return True
            
            # One is a substring of the other
            if norm1 in norm2 or norm2 in norm1:
                return True
                
            # Split into words and check for high word overlap
            words1 = set(norm1.split())
            words2 = set(norm2.split())
            if len(words1) > 0 and len(words2) > 0:
                overlap = len(words1.intersection(words2))
                total = len(words1.union(words2))
                if overlap / total > 0.8:  # 80% word overlap threshold
                    return True
            return False

        def clean_item(item: str) -> str:
            """Clean and normalize extracted items."""
            # Remove common meta phrases
            meta_phrases = [
                'here is', 'following are', 'these points', 
                'structured summary', 'key points', 'in summary',
                'to summarize', 'i should', 'we should', 'let me',
                'let us', 'i will', 'thinking about', 'considering',
                'analyzing', 'first', 'then', 'next', 'finally', 'Alright'
            ]
            
            item_lower = item.lower()
            if any(phrase in item_lower for phrase in meta_phrases):
                return ''
            
            # Remove markdown formatting
            item = re.sub(r'\*\*|\*|__|\^|#|`', '', item)
            
            # Remove leading/trailing punctuation and whitespace
            item = item.strip('.,;:!?-*• \t\n')
            
            return item.strip()

        def extract_thinking(response: str) -> str:
            """Extract thinking content with better stray tag handling."""
            if not response:
                return ""
            
            # Handle proper think tags
            think_match = re.search(r'<think>(.*?)</think>', response, re.DOTALL)
            if think_match:
                return think_match.group(1).strip()
            
            # Handle stray closing tag
            if '</think>' in response:
                parts = response.split('</think>')
                if len(parts) > 1:
                    return parts[0].strip()  
            return ""

        def clean_text_for_extraction(response: str) -> str:
            """Clean text for better extraction, handling lists and intros."""
            if not response:
                return ""
                
            # Remove thinking content
            thinking = extract_thinking(response)
            if thinking:
                response = response.replace(thinking, '')
                response = response.replace('<think>', '').replace('</think>', '')
            
            # Check for bullet points or numbered lists
            bullet_points = re.findall(r'(?:^|\n)[-•*]\s*([^\n]+)', response)
            numbered_points = re.findall(r'(?:^|\n)\d+\.\s*([^\n]+)', response)
            
            if bullet_points or numbered_points:
                # Only extract list items
                items = []
                items.extend(bullet_points)
                items.extend(numbered_points)
                return "\n".join(items)
            else:
                # Extract all non-empty paragraphs
                paragraphs = [p.strip() for p in response.split('\n\n') if p.strip()]
                return "\n".join(paragraphs)

        def deduplicate_lists(related: List[str], not_related: List[str]) -> Tuple[List[str], List[str]]:
            """Deduplicate with priority for non-essential context."""
            seen = set()
            unique_not_related = []
            unique_related = []

            # Process not_related first (priority)
            for item in not_related:
                cleaned_item = clean_item(item)
                if not cleaned_item or len(cleaned_item) < 3:
                    continue
                
                if not any(are_similar(cleaned_item, existing) for existing in unique_not_related):
                    unique_not_related.append(cleaned_item)
                    seen.add(normalize_text(cleaned_item))

            # Then process related, avoiding overlap
            for item in related:
                cleaned_item = clean_item(item)
                if not cleaned_item or len(cleaned_item) < 3:
                    continue
                
                if normalize_text(cleaned_item) not in seen and \
                not any(are_similar(cleaned_item, nr_item) for nr_item in unique_not_related) and \
                not any(are_similar(cleaned_item, r_item) for r_item in unique_related):
                    unique_related.append(cleaned_item)
                    seen.add(normalize_text(cleaned_item))

            return unique_related, unique_not_related

        def get_context(prompt_key: str) -> Tuple[str, List[str]]:
            """Get context with improved response handling for various formats."""
            response = self._call_ollama(self.prompts[prompt_key].format(
                intent=intent, task=task, text=text))
                
            if not response:
                return "", []
    
            # Extract thinking/reasoning first (keep this for compatibility)
            thinking = ""
            if '<think>' in response or '</think>' in response:
                thinking = extract_thinking(response)
                # Clean thinking tags from response
                response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
                response = response.replace('<think>', '').replace('</think>', '')

            # Try to extract items in order of preference:
            items = []
            
            # 1. Try extracting from list format with various headers
            list_headers = [
                r'(?:###|##|#)?\s*(?:ESSENTIAL|Essential|essential)\s*(?:INFORMATION|Information|information):\s*\[(.*?)\]',
                r'(?:###|##|#)?\s*(?:NON-ESSENTIAL|Non-Essential|non-essential)\s*(?:INFORMATION|Information|information):\s*\[(.*?)\]',
                r'(?:ESSENTIAL|Essential|essential)\s*(?:INFORMATION|Information|information):\s*\[(.*?)\]',
                r'(?:NON-ESSENTIAL|Non-Essential|non-essential)\s*(?:INFORMATION|Information|information):\s*\[(.*?)\]'
            ]

            for pattern in list_headers:
                match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
                if match:
                    try:
                        # Clean and parse items
                        items_str = match.group(1).strip()
                        # Try JSON parse first
                        try:
                            items = json.loads(f"[{items_str}]")
                            items = [str(item).strip() for item in items if item]
                            if items:
                                return thinking, items
                        except json.JSONDecodeError:
                            # If JSON fails, try comma separation
                            items = [i.strip(' "\'\t\n') for i in items_str.split(',')]
                            items = [i for i in items if i]
                            if items:
                                return thinking, items
                    except Exception as e:
                        logger.debug(f"List extraction failed: {str(e)}")
                        continue

            return thinking, []

        # Main retry loop with exponential backoff
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Get both types of content
                non_essential_thinking, not_related = get_context('sensitive_info_nonrelated')
                essential_thinking, related = get_context('sensitive_info_related')
                
                # Combine thinking from both responses
                combined_reasoning = ""
                if non_essential_thinking:
                    combined_reasoning += non_essential_thinking + "\n\n"
                if essential_thinking:
                    combined_reasoning += essential_thinking
                
                # Apply deduplication with priority
                related, not_related = deduplicate_lists(related, not_related)
                
                if related or not_related:
                    return combined_reasoning.strip() or "Analysis completed successfully", {
                        "related_context": related,
                        "not_related_context": not_related
                    }

                logger.debug(f"Attempt {attempt + 1}/{max_retries} failed to extract meaningful content")
                time.sleep(2 ** attempt)  # Exponential backoff
                
            except Exception as e:
                logger.debug(f"Error in attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)

        return "Failed to extract sensitive information", {
            "related_context": [],
            "not_related_context": []
        }


    def reformulate_prompt(self, text: str, context_info: Dict, intent: str, task: str, conversation_id: str) -> Tuple[str, str]:
        """Reformulate prompt while handling <think> tags if present."""
        def _reformulate():
            context = f"{intent} for {task}"
            prompt = self.prompts['reformulation'].format(
                text=text,
                intent=context,
                essential_info=json.dumps(context_info['related_context']),
                removable_info=json.dumps(context_info['not_related_context'])
            )
            response = self._call_ollama(prompt)
            if not response:
                return None
            thinking, reformulation = _extract_thinking_output(response)
            return thinking, reformulation
        result, success = self._retry_operation("reformulation", _reformulate)
        return result if success else (None, None)
