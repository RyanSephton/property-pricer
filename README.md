# property-pricer
A quick web app to show distributions of property prices based on property types and postcodes. 



## Quickstart
Clone the environment within the `requirements.txt` file.

To run the data preprocessing, run the script `clean_preprocess_data.py`, but in order to do so, insert property sales CSVs so that the data directory is structured as such:
```bash
data
├── raw_data 
    ├── Average-price-seasonally=adjusted.csv  # UK housing index fund information
    ├── Postcode districts.csv  # General UK postcode information
    ├── pp-20XX.csv # Historical property sales file - any number of these files can be added here
    ├── pp-20xx.csv # Configuration for the production workflow. 
├── cleaned_data 
     ├── (optional) joined_imputed_data.csv # Optional file to speed up run time, contains imputed postcodes
```

Navigating to the root of the repo and running the bash command `python clean_preprocess_data.py` will then invoke the preprocessing script (if imputed postcodes are needed, uncomment the 
appropriate lines in the clean_preprocess file), and the json file needed will be generated and stored in the `data/cleaned_data/` directory.


To run the application from the command line see `main.py` for instructions

To run the application with a basic UI in a webapp, navigate to the root of the directory on the command line and enter `streamlit run app.py`. A browser will then open with all
of the visuals. NOTE: the conda environment with the requirements.txt must be activated prior to running this.


## Tests
TBD


## Repo Structure
```bash
├── data  # Stores files associated with the repo
├── app.py  # Web app to give a simple UI to the pricing algo
├── main.py  # Main app entrypoint to allow command line use
├── main.ipynb  # Main app entrypoint giving a simple example
├── property-pricer  # Logs produced during processing
    ├── __init__.py  # init file for absolute imports
    ├── ingest.py # Reads the required data in
    ├── model.py # Specifies the KDE model to calculate crit values
    ├── determine_price.py # Runs the price determination code
    ├── preprocessing.py # Manipulates the data into usable format
    ├── transform.py # Applies feature engineering ready for modelling step
    └── utils.py  # Helper functions
├── README.md # Documentation
└── clean_preprocess_data.py  # Source code for preprocessing the data
```
