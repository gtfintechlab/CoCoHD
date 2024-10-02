#!/bin/bash

# Check if an argument is provided
if [ $# -eq 0 ]; then
    echo "Error: No argument provided."
    echo "Usage: sh ./collect_congress_no.sh <argument>"
    exit 1
fi

# Call the Python script with the passed argument
python3 scrape_hearings.py --no "$1"
python3 scrape_transcripts.py
python3 scrape_details.py