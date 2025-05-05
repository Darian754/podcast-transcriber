#!/bin/bash

# Download podcasts
python3 -m src.downloader

# Transcribe downloaded files
python3 -m src.transcriber
