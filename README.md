# Codes to convert .pdf -report summaries to Excel sheets.
## Install (for Mac)
1. Install (latest) Python 3.x with homebrew (http://brew.sh) if not available
```console
brew install python
```
2. Install git for version control
```console
brew install git
```
3. Clone these codes from git
```console
git clone http://github.com/karnivor/pdf_report_parser.git
```
4. Install required tools for to run the code 
```console
pip3 install -r requirements.txt
```
5. Install required tools for to run the code 
```console
python3 run_parser.py /path/to/raw/pdfs/ /where/to/write/results_table.xlsx
```

## Install (for Windows)

Currently I have no access to a Windows machine, so I cannot test or determine what is the optimal way of running Python in windows. Popular options probably include Anaconda https://www.anaconda.com/ or running Windows Subsystem For Linux 2 (WSL2) https://docs.microsoft.com/en-us/windows/wsl/install-win10 with Ubuntu (or other) Linux.

For installing Python3 (and pip) to Linux you can use follow a tutorial like (https://linuxize.com/post/how-to-install-python-3-9-on-ubuntu-20-04/)

## Notes
- The run_parser.py command reads the list of texts in settings.py to search for similar texts in reports. You may edit settings.py for more texts to be searched. It uses two lists. Some reports have mention "When compared with ECG of XX-AAA-XXXX". The first list is used to compare terms pre-mention and the second list post-mention. By default these are the same. The Excel header texts of post-mention are added with "_v" for the Finnish word "vertailu".
