
# Install virtualenv
python3 -m venv venv

# activate it
source venv/bin/activate

# Install libraries
python -m pip install -U pyserial
# python -m pip install -U can-utils
# sudo apt-get install can-utils
python -m pip install -U net-tools
python -m pip install -U python-can
python -m pip install -U scipy
python -m pip install -U matplotlib
python -m pip install -U pandas
python -m pip install -U pyqt5
python -m pip install -U toopazo-tools

