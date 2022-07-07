# property-pricer
A quick web app to show distributions of property prices based on property types and postcodes. 



## Quickstart
Clone the environment within the `requirements.txt` file.

To run the data preprocessing, run the script `clean_preprocess_data.py`, but in order to do so, insert property sales CSVs so that the data directory is structured as such:
data
├── raw_data 
    ├── Average-price-seasonally=adjusted.csv  # UK housing index fund information
    ├── Postcode districts.csv  # General UK postcode information
    ├── pp-20XX.csv # Historical property sales file - any number of these files can be added here
    ├── pp-20xx.csv # Configuration for the production workflow. 
├── cleaned_data 
     ├── (optional) joined_imputed_data.csv # Optional file to speed up run time, contains imputed postcodes


Navigating to the root of the repo and running the bash command `python clean_preprocess_data.py` will then invoke the preprocessing script (if imputed postcodes are needed, uncomment the 
appropriate lines in the clean_preprocess file), and the json file needed will be generated and stored in the `data/cleaned_data/` directory.
 
## Tests
TBD


## Repo Structure
```bash
├── data  # Stores files associated with the repo
├── property-pricer  # Logs produced during processing
    ├── __init__.py  # Unit test files
    ├── ingest.py # Execution and logic for the quarterly pipeline
    ├── preprocessing.py # Configuration for the production workflow.
    ├── transform.py # Configurations for development work.
    └── utils.py  # Used to simplify command line execution
├── README.md # Documentation
└── clean_preprocess_data.py  # Source code for the application
```
