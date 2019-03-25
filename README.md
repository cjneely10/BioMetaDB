# BioMetaDB

## Installation
Clone this repository and add the project-level directory *BioMetaDB* to your path. Create an alias to access dbdm.
<pre><code>cd /path/to/BioMetaDB
python3 setup.py build_ext --inplace
export PYTHONPATH=/path/to/BioMetaDB:$PYTHONPATH
alias dbdm="python3.5 /path/to/BioMetaDB/dbdm.py"</code></pre>
Adding the last two lines of code to a user's `.bashrc` file will maintain these settings on next log-in.

### Dependencies

- Python3.5
- Python packages
    - SQLAlchemy
    - BioPython
    - ConfigParser
    - ArgParse

Such dependencies are best maintained within a separate Python virtual environment.

## About

**BioMetaDB** is a data-management package that automatically generates database schemas, minimizing the amount
of temporary files used and handling migrations and updates smoothly. This SQLAlchemy-based wrapper package allows
researchers and data engineers to quickly generate Python classes and objects for fast data-searching, abstracting 
searches to a SQL-based API and allowing end-users to focus on query building for analysis. Finally, this schema is 
specifically useful for tsv-based output, such as output from annotation suites, and will allow users to assign output 
from these files to existing data records and files quickly and efficiently.

Database projects are organized into file-systems:

<pre><code>DB/
    classes/
        db_table_1.json
        db_table_2.json
    config/
        database.ini
    db/
        db_table_1/
            data_file_1.faa
            data_file_2.fna
            data_file_3.fasta
        db_table_2/
            data_file_1.fastq
            data_file_2.fq
    migrations/
        ########.migrations.mgt
</code></pre>

File systems created by **BioMetaDB** are accessible in Python scripts:

<pre><code>from BioMetaDB import get_table

table = get_table("/path/to/DB", table_name="db_table_1")
# Alternatively, 
# table = get_table("/path/to/DB", alias="table_1")

table.query()  # Returns all values
table.query("n50 >= 100000")  # Simple filter query
table.query("n50 >= 100000 AND n75 <= 1000000")  # More complex filter query
# Additional SQLAlchemy operations...
</code></pre>

**BioMetaDB** returns objects that directly inherit from SQLAlchemy data types, meaning that (most, if not all) 
functions that are available to SQLAlchemy objects are available here.

### Why bother?

#### Data retention

Data is commonly output as .tsv or .csv files, and gathering data from multiple .tsv files (e.g. determining the most
statistically likely annotation, combining output from multiple software suites, etc) can be a tedious process that 
frequently can require the creation of multiple temporary files. This software suite minimizes this problem by using 
the column names from .tsv files as the column names in the database table.

<pre><code># For a .tsv file formatted as:
File_name   Column.1    column_2
data_file_1.faa 25  4.7
data_file_2.fna 100 12.5

# dbdm would generate database objects with attributes accessible as:
db_objects = table.query()
db_objects[0]._id  # Returns data_file_1.faa  
db_objects[0].column_1  # Returns 25
db_objects[1].column_2  # Returns 12.5
getattr(db_objects[1], "_id")  # Returns data_file_2.fna
</code></pre>

Notice that column names are automatically adjusted to match typical SQL requirements. This system translates column 
output from .tsv files into an SQL schema, saving data files to a project-level directory and automatically handling 
data storage, which allows for more centralized data tracking.

#### Additional functionality 

- All database records generated using the values returned by `get_table` have functions available for common database 
operations
    - `__repr__()`: Prints all database table data for record in a three-column format
    - `full_path()`: Returns the complete path to the record's associated file in the project 
    - `print()`: Prints the entire contents of the file to screen
    - `write()`: Writes the contents of the file to a temporary file, with this location stored in the 
    `self.temp_filename` attribute
    - `clear()`: Deletes the temporary file created with `write()`
    - `get()`: Returns entire file contents
    - `get_records()`: Returns data file contents as a list of `BioPython` objects

## Usage Best Practices

#### SQLAlchemy

- **BioMetaDB** uses this powerful library to generate and use databases, in this case SQLite3.
- SQLAlchemy is a powerful Python package that makes working with SQL easy and fairly uniform between relational 
database management systems (RDBMSs).
- Read more about SQLAlchemy, its functionality, and its limitations:
<https://docs.sqlalchemy.org/en/latest/orm/tutorial.html>

#### Data file integrity

- **BioMetaDB** uses .tsv files to generate names and data types of columns in the RDBMS tables.
- Before running this software, ensure that data file column names are adequately formatted, with no trailing `\n` 
or `\t` in the file.
    - Columns named `Column.1` and `column_1` will both override to `column_1`.
- Data types are automatically predicted based on a randomly selected value within the column.
    - Ensure that all values in a given column store the same kind of data (e.g. Integer, Float, VARCHAR, etc).
- **BioMetaDB** matches names of data files (e.g. file_1.fasta) to record ids in the .tsv files, so make sure that
they match.

#### Modifiying project structure or source code

- **BioMetaDB** relies on the integrity of this file system that it creates when `dbdm INIT` is first called. It is 
ill-advised to manually delete files or records from the database or project, respectively. Updating records using 
`sess.commit()` is still supported (and recommended), but removing files from the project should be done using `dbdm 
DELETE`.
- Certain portions of the source code can be modified to better fit a user's needs.
    - `BioMetaDB/Models/functions.py` holds the class `DBUserClass`, which is the parent class of all database objects 
    generated using `get_table()`. Any additional functions added to this class will be available to your records.

## dbdm

**dbdm** is the primary method for making large-scale changes to the database schema or data files. Use this program 
when first creating your database or when making large updates, such as when adding/removing tables or updating/removing
values or columns.

<pre><code>usage: dbdm.py [-h] [-n DB_NAME] [-t TABLE_NAME] [-d DIRECTORY_NAME]
               [-f DATA_FILE] [-l LIST_FILE] [-c CONFIG_FILE] [-a ALIAS] [-s]
               [-v] [-q QUERY]
               program

dbdm:   Manage BioMetaDB project

Available Programs:

CREATE: Create a new table in an existing database, optionally populate using data files
                (Req:  --config_file --table_name --directory_name --data_file --alias --silent)
DELETE: Delete list of ids from database tables, remove associated files
                (Req:  --config_file --table_name --list_file --alias --silent)
FIX: Repairs errors in DB structure using .fix file
                (Req:  --data_file --silent)
INIT: Initialize database with starting table, fasta directory, and/or data files
                (Req:  --db_name --table_name --directory_name --data_file --alias --silent)
INTEGRITY: Queries project database and structure to generate .fix file for possible issues
                (Req:  --config_file --table_name --alias)
REMOVE: Remove table and all associated data from database
                (Req:  --config_file --table_name --alias --silent)
REMOVECOL: Remove column list (including data) from table
                (Req:  --config_file --table_name --list_file --alias --silent)
SUMMARIZE: Quick summary of project
                (Req:  --config_file --view --query --table_name --alias)
UPDATE: Update values in existing table or add new sequences
                (Req:  --config_file --table_name --directory_name --data_file --alias --silent)

positional arguments:
  program               Program to run

optional arguments:
  -h, --help            show this help message and exit
  -n DB_NAME, --db_name DB_NAME
                        Name of database
  -t TABLE_NAME, --table_name TABLE_NAME
                        Name of database table
  -d DIRECTORY_NAME, --directory_name DIRECTORY_NAME
                        Directory path with bio data (fasta or fastq)
  -f DATA_FILE, --data_file DATA_FILE
                        .tsv or .csv file to add, or .fix file to integrate
  -l LIST_FILE, --list_file LIST_FILE
                        File with list of items, typically ids or column names
  -c CONFIG_FILE, --config_file CONFIG_FILE
                        Config file for loading database schema
  -a ALIAS, --alias ALIAS
                        Provide alias for locating and creating table class
  -s, --silent          Silence all standard output (Standard error still displays to screen)
  -v, --view            Display column names only with SUMMARIZE
  -q QUERY, --query QUERY
                        Query to pass to SUMMARIZE</code></pre>

The typical workflow for initializing **BioMetaDB** is straightforward. Many options exist for updating, adding to, 
and removing from the existing project structure. You may also choose to assign an alternate name to a table within a
database in the form of an alias. Depending on the number of entries involved, these commands can result in voluminous
output, which can either be silenced by passing `-s y` as parameters in your command, or by redirecting standard output
to a text file. 


### INIT

**INIT** is used to create a new database project for the first time. This will create the project-level directory and
all subdirectories, will copy data files to the new project system, and will commit all information from a provided .tsv
file as the database table class schema. Notice that original file permission are maintained for any files copied to this
project.

- Required flags
    - --db_name (-n): Name to assign database (for example, Metagenomes)
    - --table_name (-t): Name to give table in database (for example, Genomic)
- Optional flags
    - --directory_name (-d): Path to directory with files to add to the database.
    - --data_file (-f): Path to .tsv file to use to generate DB table schema
    - --alias (-a): Alias (short name) for table in database
    - --silent (-s): Silence standard output
- Example
    - `dbdm INIT -n database -t db_table_1 -d /path/to/data/directory/ -f /path/to/data_file.tsv -a table_1`
    - This command will generate the following project structure and assign an alias name to the table:
<pre><code>database/
    classes/
        db_table_1.json  # Generated from data_file.tsv
    config/
        database.ini
    db/
        db_table_1/
            # Files from /path/to/data/directory/
    migrations/
</code></pre>
- Possible exceptions:
    - AssertionError: The prefix provided for the working directory already exists 

At this point, the project is available to use in scripts in the manner mentioned in the **About** section.

### UPDATE

**UPDATE** is used to add columns to an existing table and to add or modify large numbers of entries in the database.
This command creates and stores a deep copy of the existing database, updates the existing columns to include new 
columns from a provided .tsv file, and adds new data files from a provided directory. The deep copy is saved in the 
project-level `migrations` folder.

- Required flags
    - --config_file (-c): Path to project directory 
    - --table_name (-t): Name of table to update
- Optional flags
    - --directory_name (-d):- Path to directory with files to add to the database.
    - --data_file (-f): Path to .tsv file to use to generate DB table schema
    - --alias (-a): Alias (short name) for table in database
    - --silent (-s): Silence standard output
- Example
    - `dbdm UPDATE -c /path/to/DB -t db_table_1 -f /path/to/data_file.tsv -d /path/to/data_dir/`
    - This command will update the table named `db_table_1`, which is part of the database in the project `DB`. This 
    command will add new column data from the file `/path/to/data_file.tsv` and will add new data files from the 
    directory `/path/to/data_dir/`. A copy of the database is stored in the project-directory `migrations`, 
    named using the date that the command was run.

### REMOVECOL

**REMOVECOL** is used to remove columns from a table within the database. All associated data is deleted, and the table
is regenerated using existing data.

- Required flags
    - --config_file (-c): Path to project directory 
    - --table_name (-t): Name of table to update
    - --list_file (-l): Path to file with list of column names to remove from database table
- Optional flags
    - --alias (-a): Alias (short name) for table in database
    - --silent (-s): Silence standard output
- Example
    - `dbdm REMOVECOL -c /path/to/DB -t db_table_1 -l /path/to/list_to_remove.list`
    - This command will remove all columns provided in the newline-separated file `list_to_remove.list` from 
    `db_table_1` within the project `DB`.
- Possible exceptions
    - ListFileNotProvidedError:   List file not provided, pass path to a list

### DELETE

**DELETE** removes records, and their associated files, from a table in the database.

- Required flags
    - --config_file (-c): Path to project directory 
    - --table_name (-t): Name of table to update
    - --list_file (-l): Path to file with list of record ids to remove from database table
- Optional flags
    - --alias (-a): Alias (short name) for table in database
    - --silent (-s): Silence standard output
- Example
    - `dbdm REMOVECOL -c /path/to/DB -t db_table_1 -l /path/to/list_to_remove.list`
    - This command will remove all record ids provided in the newline-separated file `list_to_remove.list` from 
    `db_table_1` within the project `DB`.
- Possible exceptions
    - ListFileNotProvidedError:   List file not provided, pass path to a list

### CREATE

**CREATE** is used to add a new table to an existing project structure and database. This command updates an existing
project structure.

- Required flags
    - --config_file (-c): Path to project directory 
    - --table_name (-t): Name of table to create
- Optional flags
    - --directory_name (-d): Path to directory with files to add to the database. 
    - --data_file (-f): Path to .tsv file to use to generate DB table schema
    - --alias (-a): Alias (short name) for table in database
    - --silent (-s): Silence standard output
- Example
    - `dbdm CREATE -c /path/to/DB -t db_table_2 -d /path/to/data/directory/ 
    -f /path/to/data_file.tsv -a table_2`
    - This command will update the project structure `DB` to include the new table:
<pre><code>DB/
    classes/
        db_table_1.json
        db_table_2.json  # Generated from data_file.tsv 
    config/
        database.ini
    db/
        db_table_1/
        db_table_2/
            # Files from /path/to/data/directory/
    migrations/
</code></pre>

### REMOVE

**REMOVE** is used to remove a table from an existing database, including all associated records and files. As this
command cannot be undone, you are recommended to run `UPDATE` with only the required flags to store a migration copy of
your data as a .tsv file.

- Required flags
    - --config_file (-c): Path to project directory 
    - --table_name (-t): Name of table to remove
- Optional flags
    - --alias (-a): Alias (short name) for table in database
    - --silent (-s): Silence standard output
- Example
    - `dbdm REMOVE -c /path/to/DB/config/database.ini -t db_table_2`
    - This command will remove the table `db_table_2` from the project `DB`.

## Other Information

### Useful accessory scripts

#### ArgParse

- `BioMetaBD/Accessories/arg_parse.py`
- **ArgParse** is a simple wrapper script for the Python module `argparse` that reduces the amount of if/then checking.

#### ProgramCaller

- `BioMetaBD/Accessories/program_caller.py`
- **ProgramCaller** is a script made for handling flags and errors in a moderately complex program (such as this one), 
and is highly useful for fast script-making.

### Planned updates

- `BioMetaDB/DataStructures/record_list.py`
    - `RecordList` is a simple class that inherits from *list*, but focuses on displaying averages, standard deviations,
    etc., about records in the list.

### Contact

This project was designed and written by Christopher Neely. Email me anytime at `christopher.neely1200@gmail.com`.
