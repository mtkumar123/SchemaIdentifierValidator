## SchemaIdentifierValidator

### Project Goals
- Allow users to upload csv files of upto 100 mb in size.
  - In case csv files do not have explicit headers the tool infers the header names. More details can be read here.
- Allow users to define schemas (mapping of column names to data types) and store them in the tool to be reused.
- Allow users to associate a schema with an uploaded file.
- Allow users to view a schema associated with a file.
  - In case a file did not have an user defined schema associated with the tool infers the schema to be used.
- Allow users to perform validation of the file contents against an user provided schema or an inferred schema.

### Setting Up The Project
- Make sure you have docker installed and running.
```
# Run the following commands from the root directory of the project.
docker compose build
docker compose up
```
- Tests can be run by attaching into the container
```
docker exec -it <container-id> bash
# Make sure you are in the code directory
pytest tests/
```
- Swagger docs can be viewed at http://127.0.0.1:8000/docs#/

### Additional Details
#### Inferences
**Schema Inference**  
The schema is inferenced by pandas when reading the csv. Unfortunately a lot of the times pandas results to object dtype for a lot of columns which are clearly float or int. Pandas to_datetime and to_numeric were used to check if object dtypes could be constrained to a more specific type during the schema inference process.  

**Column Inference**  
Some of the csv files might not have headers and therefore had to be inferenced. In order to do this the tool first checks to see if there is a schema that the user has uploaded that matches the current schema of the csv file - in that case the columns of the matched schema are applied to the current one. However in case no matching schema was found - the tool defaults to using Column0...ColumnN as headers.

#### Validation
Validation of a file is done with the help of Pydantic. If a file has an associated schema that is used, otherwise we default to the inferred schema. The schema is then used to create a dynamic pydantic model which validates each row of the Dataframe.

### Limitations
- Right now schema dtypes that are supported are int, float, datetime, and str. In case a dtype is not supported we default to using str.

### Improvements
- For column inference check uploaded files as well to see if they have the same dtype structure.
- Adding linting, and mypy to the repo.
- Separate out the BaseSchemaRequest model a bit more - right now the columns and dtypes are optional and populated through the model validator - but from the openapi spec perspective they seem like mandatory fields. Overall I think the pydantic basemodel hiearchy in the project could be cleaned up a bit more.