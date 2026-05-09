import time
from orchestrator import run_pipeline

UPDATE_EVERY_HOURS = 6

if __name__ == "__main__":
    while True:
        run_pipeline()
        print(f"Sleeping for {UPDATE_EVERY_HOURS} hours...")
        time.sleep(UPDATE_EVERY_HOURS * 60 * 60)