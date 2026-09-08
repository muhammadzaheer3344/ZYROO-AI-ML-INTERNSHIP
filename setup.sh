#!/bin/bash
# Optional local/container setup helper; Streamlit Cloud uses packages.txt.
sudo apt-get update --allow-releaseinfo-change || true
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng || true
