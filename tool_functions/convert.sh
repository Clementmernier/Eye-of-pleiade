#!/bin/bash
pyinstaller --onefile --windowed   --add-data "LogoCNES200.jpg:."   --add-data "LogoCNES75.jpg:."   --name oeil_de_pleiadesCNES oeil_de_pleiadeCNES.py
pyinstaller --onefile --windowed   --add-data "logoPS200.png:."   --add-data "logoPS75.png:."   --name oeil_de_pleiadesPSO oeil_de_pleiadePSO.py

wine python.exe -m PyInstaller --onefile --windowed   --add-data "LogoCNES200.jpg:."   --add-data "LogoCNES75.jpg:."   --name oeil_de_pleiadesCNES oeil_de_pleiadeCNES.py
