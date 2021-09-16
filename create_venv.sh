
# Install virtualenv
python3 -m venv venv

# activate it
source venv/bin/activate

# Install libraries
python -m pip install -U scipy
python -m pip install -U pyserial
python -m pip install -U can-utils
python -m pip install -U net-tools
python -m pip install -U python-can
python -m pip install -U toopazo-tools

