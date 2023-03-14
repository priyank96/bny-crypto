# bny-crypto
MSAII Capstone

## Running Streamlit Dashboard
```bash
conda create -n capstone python==3.10.4
conda activate capstone
pip install -r requirements.txt
streamlit run dashboard.py
```


## Creating the conda environment
```commandline
conda env create -f environment.yml
```
This will create a new conda environment for this project. 
The name of the environment (capstone) is specified in the [environment.yml](environment.yml) file.

## Updating the conda environemt
Please update the environment file each time a dependency is added or updated.
```commandline
conda env export --from-history > environment.yml
```
The `--from-history` flag is used to only export the packages that were installed explicitly by the user,
this helps to make the environment portable across platforms.
## Notes
To generate data for v0 experiments:
1. Aggregate binance data (binance_data_aggregator.py) - this is in UTC
2. Run generate_csv.py to add all the TAs (Optional)
3. Run SPY_data.py to add the S&P500 data

Use the sp500values.csv file!


## Quick Commands
### Kafka
#### Start the ZooKeeper service
```commandline
bin/zookeeper-server-start.sh config/zookeeper.properties
```
#### Start the Kafka broker service
```commandline
bin/kafka-server-start.sh config/server.properties
```
#### Create a topic
```commandline
bin/kafka-topics.sh --create --topic quickstart-events --bootstrap-server localhost:9092
```


### Using Pycaret
#### Adding/Using Data Sources
Add the raw/processed data files in the drive and load the data in the files in the notebook (preferably in a dataframe format). All Dataframe needs to be the merged into a single datafram prior to loading the 

#### Setup
Setup will setup the training pipeline, some key parameters:
- If testset is set (we haven't set), it would be used as a holdout test
- fold_strategy defines how to make the split, (set to timeseries makes sure the time isn't morphed)
- We have 10 folds by default

#### Adding custom Metrics
RDR can be used an example to see how to add a custom metric

#### Comparing Model
Compares all the models the pycaret library on the given data. Models can be added or excluded using parameters. Cross Validation parameters will overwrite the setup parameters.

The results can be analyzed using the interactive dashboard pycaret provides