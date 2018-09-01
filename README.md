# Siol bandwidth meter

Simple script for measuring bandwidth of LAN ports on Siol's innbox v45 (might work on other Siol's routers). 
Requires no dependencies beyond Python 3.6.

# Usage
```
python bandwidth_meter.py [-h] [-i IP] [-u USER] [-p PASSWORD] [-d DELAY]
```
optional arguments:

  **-h**, **--help**   show help message and exit
  
  **-i** :        router's ip (default: 192.168.1.1)
  
  **-u** :      username for router's control center (default: user)
  
  **-p** :  password for router's control center (default: user)
  
  **-d** :     delay (in s) between each update (default: 5)

# Windows executable
Windows executable made with PyInstaller is also available [here](http://s000.tinyupload.com/index.php?file_id=58276614944645026960).
