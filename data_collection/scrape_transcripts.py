import json
import os
import time
import urllib.request
from tqdm import tqdm

def retrieve(transcript_link, file_path):
    max_retries = 3
    retry_delay = 1

    retry_count = 0

    while retry_count < max_retries:
        try:
            urllib.request.urlretrieve(transcript_link, file_path)
            return 0
        except urllib.error.HTTPError as e:
            if e.code == 400:
                print("Bad Request: The server could not understand the request.")
            else:
                print(f"HTTP Error {e.code}: {e.reason}")
            # Increment the retry count
            retry_count += 1
            if retry_count < max_retries:
                print("Retrying...")
                time.sleep(retry_delay)  # Delay before retrying
    
    return -1


def download(type, congress_year, path):
    # type is house | senate | joint
    if congress_year[type]:
        for committee in tqdm(congress_year[type], desc=f"{congress_year['congress_year']} - {type}"):
            for hearing in committee['hearings']:
                govinfo_id = hearing['govinfo_id']
                transcript_link = hearing['transcript']
                file_path = f"{path}{govinfo_id}.txt"
                if not os.path.exists(file_path):
                    if retrieve(transcript_link, file_path) == -1:
                        print(f"Couldn't download {transcript_link}")

def count_files_in_folder(folder_path):
    count = 0
    for _, _, files in os.walk(folder_path):
        count += len(files)
    return count

def main():
    metadata_file = '../data/hearing_data/hearing_metadata.json'
    transcripts_path = '../data/hearing_data/transcripts/'
    # Create the transcripts folder if not exist
    folder_path = os.path.dirname(transcripts_path)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    with open(metadata_file, 'r') as json_file:
        metadata = json.load(json_file)

    isExist = os.path.exists(transcripts_path)
    if not isExist:
        os.makedirs(transcripts_path)
    
    for congress_year in metadata:
        download('house', congress_year, transcripts_path)
        download('joint', congress_year, transcripts_path)
        download('senate', congress_year, transcripts_path)

    num_files = count_files_in_folder(transcripts_path)
    print(f'Number of transcripts downloaded: {num_files}')

if __name__ == "__main__":
    main()