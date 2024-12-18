import subprocess
import time

def run_background_task():
    """Run the data generation script in the background."""
    subprocess.Popen(["python", "generated_data.py"])

def main_app():
    """Main application logic."""
    print("Main app is running...")
    # Simulate the main app doing some work
    for _ in range(10):  # Simulate the main app doing work for a while
        print("Main app doing work...")
        time.sleep(2)

if __name__ == "__main__":
    # Start the background task when the app runs
    run_background_task()

    # Run the main app
    main_app()
