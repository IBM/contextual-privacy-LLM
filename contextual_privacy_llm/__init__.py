import logging

logger = logging.getLogger("contextual_privacy_guard")
logger.setLevel(logging.WARNING)

# Ensure logs are shown in environments like Colab/Jupyter
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Public API
from .analyzer import PrivacyAnalyzer
from .runner import run_single_query, main
