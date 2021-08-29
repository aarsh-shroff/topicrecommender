#!/bin/bash
sudo apt install python3-venv -y
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r topicrecommender/requirements.txt