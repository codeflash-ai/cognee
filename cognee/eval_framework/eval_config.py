from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional


class EvalConfig(BaseSettings):
    # Corpus builder params
    building_corpus_from_scratch: bool = True
    number_of_samples_in_corpus: int = 1
    benchmark: str = "Dummy"  # Options: 'HotPotQA', 'Dummy', 'TwoWikiMultiHop'
    task_getter_type: str = (
        "Default"  # Options: 'Default', 'CascadeGraph', 'NoSummaries', 'JustChunks'
    )

    # Question answering params
    answering_questions: bool = True
    qa_engine: str = "cognee_completion"  # Options: 'cognee_completion' or 'cognee_graph_completion' or 'cognee_graph_completion_cot' or 'cognee_graph_completion_context_extension'

    # Evaluation params
    evaluating_answers: bool = True
    evaluating_contexts: bool = True
    evaluation_engine: str = "DeepEval"  # Options: 'DeepEval' (uses deepeval_model), 'DirectLLM' (uses default llm from .env)
    evaluation_metrics: List[str] = [
        "correctness",
        "EM",
        "f1",
    ]  # Use only 'correctness' for DirectLLM
    deepeval_model: str = "gpt-5-mini"

    # Metrics params
    calculate_metrics: bool = True

    # Visualization
    dashboard: bool = True

    # file paths
    questions_path: str = "questions_output.json"
    answers_path: str = "answers_output.json"
    metrics_path: str = "metrics_output.json"
    aggregate_metrics_path: str = "aggregate_metrics.json"
    dashboard_path: str = "dashboard.html"
    direct_llm_system_prompt: str = "direct_llm_eval_system.txt"
    direct_llm_eval_prompt: str = "direct_llm_eval_prompt.txt"
    instance_filter: Optional[List[str]] = None

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    def to_dict(self) -> dict:
        # Use self.__dict__ directly for faster access and less attribute lookup overhead.
        # Only include attribute keys required by the original mapping to preserve ordering and selection.
        fields = [
            "building_corpus_from_scratch",
            "number_of_samples_in_corpus",
            "benchmark",
            "answering_questions",
            "qa_engine",
            "evaluating_answers",
            "evaluating_contexts",
            "evaluation_engine",
            "evaluation_metrics",
            "calculate_metrics",
            "dashboard",
            "questions_path",
            "answers_path",
            "metrics_path",
            "aggregate_metrics_path",
            "dashboard_path",
            "deepeval_model",
            "task_getter_type",
            "direct_llm_system_prompt",
            "direct_llm_eval_prompt",
            "instance_filter",
        ]
        dct = self.__dict__
        return {field: dct[field] for field in fields}


@lru_cache
def get_llm_config():
    return EvalConfig()
