# expendo

<img src="images/dumb_diagram.png" alt="drawing" width="400"/>

Automation tool to track my expenses.  

Parses credit card transaction history file, automatically infers expenditure categories based on the transaction metadata, and uses the Google API Client to update my expenses spreadsheet. 

## Usage

```shell
cd python
conda create -n expendo python=3.11 -y
pip install -r requirements.txt
```

Upload transaction history as CSV.  
Run `main.ipynb`.
