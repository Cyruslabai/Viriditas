"""Business logic orchestration services.

This package provides high-level service classes that coordinate inference,
training, and evaluation. Services are designed to be called by notebooks,
CLI tools, FastAPI endpoints, and LLM orchestration.

Future Services:
    - InferenceService: Wraps Predictor with error handling and logging
    - TrainingService: Wraps Trainer with progress tracking
    - EvaluationService: Wraps Analyzer with result aggregation
    - DataPipeline: Orchestrate Index → Train → Evaluate
    - ProductionPipeline: Orchestrate Load Model → Predict → Explain → Recommend
"""

# Services will be imported as they are implemented in future phases
