import pandas as pd
import time
import random
from datetime import datetime
import os

def generate_dummy_data():
    """Generate random CO level and helmet status."""
    co_level = random.randint(0, 1000)  # Random CO level between 0 and 1000
    helmet_status = random.choice([1, 0])  # Random helmet-worn status (1 or 0)
    return co_level, helmet_status

def append_to_excel(new_data, file_name):
    """Append a single row of data to the Excel file."""
    if os.path.exists(file_name):
        # Load existing data and append the new row
        existing_df = pd.read_excel(file_name)
        updated_df = pd.concat([existing_df, new_data], ignore_index=True)
    else:
        # If the file does not exist, start with the new row
        updated_df = new_data

    # Write the updated data back to the Excel file
    updated_df.to_excel(file_name, index=False)
    print(f"Data appended to {file_name}")

# File to save the data
output_file = "data/helmet_data.xlsx"

try:
    while True:  # Run indefinitely until stopped
        # Generate a new timestamp and dummy data
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Current timestamp
        co_level, helmet_status = generate_dummy_data()

        # Create a single-row DataFrame for the new data
        new_data = pd.DataFrame({
            'timestamps': [timestamp],
            'co_levels': [co_level],
            'helmet_worn': [helmet_status]
        })

        # Save the new data to the Excel file
        append_to_excel(new_data, output_file)

        # Wait for 5 seconds before generating the next data point
        time.sleep(5)

except KeyboardInterrupt:
    print("Data generation stopped.")
