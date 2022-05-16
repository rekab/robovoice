https://docs.google.com/document/d/1wDfdpEdLlfDwexNORDDVtKARrnzqxjQtfFlcrvqhabM/edit

sudo apt install libportaudio2
sudo apt install libportmidi0
sudo apt install liblo-tools
sudo apt install libsndfile1

python3 -m venv voice-env
source voice-env/bin/activate
pip install -r requirements.txt
