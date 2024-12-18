import pandas as pd
import time
import re
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# File system event handler for monitoring Excel file updates
class ExcelFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(r'helmet_data.xlsx'):  # Replace with the correct path
            update_html_with_helmet_status()

# Function to update the HTML file with the helmet status
def update_html_with_helmet_status():
    df = pd.read_excel(r'data\helmet_data.xlsx')  # Update the path to your Excel file
    df = df[['helmet_worn']].tail(1)  # Get the last row of the helmet_worn column
    helmet_status = 'On' if df['helmet_worn'].iloc[0] == 1 else 'Off'
    color = 'green' if helmet_status == 'On' else 'red'

    # Create the line to update the HTML
    new_line = f"""<p id="helmet-status">Helmet Worn: <span style="color: {color};">{helmet_status}</span></p>"""

    # Read the existing HTML file
    with open(r'templates/helmet_detail.html', 'r') as file:  # Update the path to your HTML file
        existing_html = file.read()

    # Replace or add the status line
    if 'id="helmet-status"' in existing_html:
        updated_html = re.sub(r'<p id="helmet-status">.*?</p>', new_line, existing_html, flags=re.DOTALL)
    else:
        updated_html = existing_html.replace('</body>', f'{new_line}\n</body>')

    # Write the updated HTML back to the file
    with open(r'templates/helmet_detail.html', 'w') as file:  # Update the path to your HTML file
        file.write(updated_html)

    print(f"Helmet status updated to: {helmet_status}")

# Main function to start monitoring
def start_monitoring():
    event_handler = ExcelFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path=r'data', recursive=False)  # Update the path to your folder
    observer.start()
    print("Helmet status monitoring started.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_monitoring()
