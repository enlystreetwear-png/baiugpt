from pipeline.ingest import run_ingestion
from pipeline.clean import run_cleaning
from pipeline.embed import run_embedding


def run_pipeline():
    print("\n==============================")
    print("Running BaiuGPT Data Pipeline")
    print("==============================\n")

    run_ingestion()
    run_cleaning()
    run_embedding()

    print("\nPipeline finished successfully!")


if __name__ == "__main__":
    run_pipeline()