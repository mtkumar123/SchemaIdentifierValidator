### Demo

#### File Uploading
train_split_00.csv is less than 100 mb and passes upload.
people-1000000.csv is greater than 100 mb and fails upload.

#### Data with provided Columns
people-500000.csv has headers - look at schema of file
validate the file with the inferred schema and given columns

#### Data without provided columns
post schema of people-500000.csv
upload people-500000-noheader.csv
view schema and validate
remove the existing schema and upload file again - default col0...

#### Validation Error
Change the schema of people-500000.csv from str to int
somewhere and run validation.