# Skypath

## Backend Notes
* Flake8 is used for enforcing style and consistency
* There is a typo in "JFK" for flight SP995, I have decided to rename this to the corrected version instead of throwing a warning and not logging this.We may want to throw a warning instead, but I currently prefer just making the change since this is a small dataset and having one more available flight may affect test cases.


### Data loader decisions and assumptions
Assumptions
1. Data cleanliness - I have unit tests to check that the data provided is reasonably accurate to the json file provided. This loader will not work if, for example, the airport codes are in lower case. While I have added guards for scenarios around missing/malformed required fields, invalid/unparseable dates, impossible flights (going back in time), and empty datasets, I believe that having valid cases and data will be more interesting instead of having pedantic verification/tests.  

1. Data in the flights.json file are well-formed

Data loader test
* In the happy case unit tests, we load the full dataset directly from the json file. This is a decision made right now to ensure tests are hermetic and isolated. This is at the cost of time to load/parse the json files, but because the dataset file is small, this is not be a concern right now. If datasets get bigger, then we will revisit this based on what the requirements of the unit tests are.
* In the edge case unit tests, instead of loading in the entire json file, we create temporary json fixtures with the invalid/custom flight and ensure that the data loader skips the exceptions without crashing. 
* I have added a test case/restraint for uniqueness on the "flightNumber" key. Any two flights should not have the same flight number, in the event of a duplicate, only the first flight is loaded, the rest are logged as warning during json loading.