#!/bin/bash

echo "--- Installing required system packages and Python libraries ---"
sudo apt-get update
sudo apt-get install -y python3-pip speedtest-cli
sudo python3 -m pip install -U psutil

echo "--- Prerequisites setup complete! ---"
