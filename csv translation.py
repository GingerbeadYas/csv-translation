import csv
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import openai
import math
import time

# Get your openai api key

openai.api_key = "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"

def split_text_into_segments(text, max_tokens):
    if not text or len(text) == 0:
        return []

    segments = []
    num_segments = math.ceil(len(text) / max_tokens)
    segment_size = math.ceil(len(text) / num_segments)

    for i in range(0, len(text), segment_size):
        segment = text[i:i + segment_size]
        segments.append(segment)

    return segments

def translate_segment(segment, target_language):
    response = None
    while not response:
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=f"Translate the following text to {target_language}: {segment}",
                max_tokens=100,
                temperature=0.7,
                n=1,
                stop=None
            )
        except openai.error.APIError as e:
            if "model currently overloaded" in str(e):
                print("Model is currently overloaded. Retrying after a delay...")
                time.sleep(5)  # Wait for 5 seconds before retrying
            else:
                raise e

    translated_text = response.choices[0].text.strip()
    return translated_text

def translate_text(text, target_language):
    segments = split_text_into_segments(text, 4096)
    translated_segments = []

    for segment in segments:
        translated_segment = translate_segment(segment, target_language)
        translated_segments.append(translated_segment)

    translated_text = "".join(translated_segments)
    return translated_text

def translate_csv_file(input_file_path, target_language):
    output_folder_path = Path.home() / "Downloads"
    output_file_path = output_folder_path / f"translated_{input_file_path.name}"

    with open(input_file_path, "r", encoding="utf-8") as input_file:
        reader = csv.reader(input_file)
        headers = next(reader)

        translated_rows = [headers]

        for row in reader:
            translated_row = [translate_text(cell, target_language) for cell in row]
            translated_rows.append(translated_row)

    with open(output_file_path, "w", encoding="utf-8", newline="") as output_file:
        writer = csv.writer(output_file)
        writer.writerows(translated_rows)

    return output_file_path

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    entry_file_path.delete(0, tk.END)
    entry_file_path.insert(tk.END, file_path)

def translate_file():
    input_file_path = entry_file_path.get()
    target_language = entry_target_language.get()

    if not input_file_path:
        label_status.config(text="Please select a file")
        return

    try:
        input_file_path = Path(input_file_path)
        translated_file_path = translate_csv_file(input_file_path, target_language)
        label_status.config(text=f"Translation complete. Saved as {translated_file_path}")
    except Exception as e:
        label_status.config(text=f"An error occurred: {str(e)}")

# Create the GUI window
window = tk.Tk()
window.title("CSV Translator")

# Create the file selection entry and button
label_file_path = tk.Label(window, text="Select CSV File:")
label_file_path.pack()
entry_file_path = tk.Entry(window, width=50)
entry_file_path.pack()
button_browse = tk.Button(window, text="Browse", command=browse_file)
button_browse.pack()

# Create the target language entry
label_target_language = tk.Label(window, text="Target Language:")
label_target_language.pack()
entry_target_language = tk.Entry(window, width=50)
entry_target_language.pack()

# Create the Translate button
button_translate = tk.Button(window, text="Translate", command=translate_file)
button_translate.pack()

# Create the status label
label_status = tk.Label(window, text="")
label_status.pack()

# Run the GUI main loop
window.mainloop()
