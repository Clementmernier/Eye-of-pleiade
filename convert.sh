#!/bin/bash
pyinstaller --onefile --windowed   --add-data "LogoCNES200.jpg:."   --add-data "LogoCNES75.jpg:."   --name oeil_de_pleiadesCNES.exe oeil_de_pleiadeCNES.py
pyinstaller --onefile --windowed   --add-data "logoPS200.png:."   --add-data "logoPS75.png:."   --name oeil_de_pleiadesPSO.exe oeil_de_pleiadePSO.py
