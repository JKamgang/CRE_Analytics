from src.widgets.pipeline_runner import DataArteryPipeline
import json

def main():
    pipeline = DataArteryPipeline()
    result = pipeline.run_pipeline()

    print("\n--- Pipeline Execution Complete ---")
    print("\nVisualizer Ready Output:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
