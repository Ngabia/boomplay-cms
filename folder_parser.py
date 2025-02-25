import os
import shutil
import datetime
import pandas as pd
from pathlib import Path
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen import File

# Define allowed file types
AUDIO_EXTENSIONS = {'.mp3', '.flac', '.wav'}
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png'}

# Function to extract metadata from audio files
def get_audio_metadata(file_path):
    try:
        ext = Path(file_path).suffix.lower()
        audio = File(file_path, easy=True)
        if audio is None:
            return None, None, None
        
        title = audio.get("title", [Path(file_path).stem])[0]
        artist = audio.get("artist", ["Unknown Artist"])[0]
        album = audio.get("album", ["Unknown Album"])[0]
        return title, artist, album
    except Exception as e:
        print(f"Error reading metadata for {file_path}: {e}")
        return None, None, None

# Function to recursively parse folder and collect files
def parse_folder(input_folder):
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    output_folder = f"Processed_{Path(input_folder).stem}_{today}"
    tracks_folder = os.path.join(output_folder, "Tracks")
    covers_folder = os.path.join(output_folder, "Covers")
    os.makedirs(tracks_folder, exist_ok=True)
    os.makedirs(covers_folder, exist_ok=True)
    
    metadata = []  # Store file info for CSV/Excel
    ignored_files = []  # Store ignored files for logging
    track_counter = 1  # Numbering for tracks
    
    # Walk through the entire directory tree
    for root, dirs, files in os.walk(input_folder, topdown=False):
        for file in files:
            file_path = os.path.join(root, file)
            ext = Path(file).suffix.lower()
            
            if ext in AUDIO_EXTENSIONS:
                title, artist, album = get_audio_metadata(file_path)
                title = title if title else Path(file).stem
                artist = artist if artist else Path(input_folder).stem
                new_filename = f"{str(track_counter).zfill(2)}_{artist}_{title}{ext}"
                shutil.copy(file_path, os.path.join(tracks_folder, new_filename))
                metadata.append([new_filename, artist, "", "", "Pending", ""])
                track_counter += 1
            
            elif ext in IMAGE_EXTENSIONS:
                shutil.copy(file_path, os.path.join(covers_folder, file))
            else:
                ignored_files.append(file)
        
        # Remove empty directories
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if not os.listdir(dir_path):
                os.rmdir(dir_path)
    
    # Generate CSV & Excel files
    csv_path = os.path.join(output_folder, "metadata.csv")
    excel_path = os.path.join(output_folder, "metadata.xlsx")
    columns = ["Track Name", "Artist Name", "UPC", "ISRC", "Upload Status", "Upload Timestamp"]
    df = pd.DataFrame(metadata, columns=columns)
    df.to_csv(csv_path, index=False)
    df.to_excel(excel_path, index=False)
    
    print(f"Processing complete! Organized files saved in: {output_folder}")
    
# Example usage
if __name__ == "__main__":
    input_folder = input("Enter the path of the messy artist folder: ")
    parse_folder(input_folder)
