# BioMetaDB v0.1.2

## Installation
Clone this repository and add the project-level directory *BioMetaDB* to your path. Create an alias to access `dbdm`.
<pre><code>cd /path/to/BioMetaDB
pip3 install -r requirements.txt
python3 setup.py build_ext --inplace
alias dbdm="python3 /path/to/BioMetaDB/dbdm.py"</code></pre>
Adding the last line of the above code to a user's `.bashrc` file will maintain these settings on next log-in.

### Dependencies

- Python &ge; 3.5
- Cython 0.29.2
- Python packages
    - SQLAlchemy 1.3.2
    - BioPython 1.73
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

<pre><code>database/
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

table = get_table("/path/to/database", table_name="db_table_1")
# Alternatively, 
# table = get_table("/path/to/database", alias="table_1")

table.query()  # Returns all values
table.query("n50 >= 100000")  # Simple filter query
table.query("n50 >= 100000 AND n75 <= 1000000")  # More complex filter query
table.query("_id LIKE '%genome%'") # Has genome in name of record
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
table.query()
table[0]._id  # Returns data_file_1.faa  
table[0].column_1  # Returns 25
table[1].column_2  # Returns 12.5
getattr(table[1], "_id")  # Returns data_file_2.fna
</code></pre>

Notice that column names are automatically adjusted to match typical SQL requirements. This system translates column 
output from .tsv files into an SQL schema, saving data files to a project-level directory and automatically handling 
data storage, which allows for more centralized data tracking.

#### Additional functionality 

For a complete summary of the functionality afforded by using the classes Record and RecordList, see the complete
documentation to come.

- `Record` - all objects generated by the database.
    - `__repr()__`:         returns a "pretty-print" summary of the record
    - `full_path()`:        returns full path to data file
    - `write_temp()`:            writes entire contents of data file to current directory as temp file
    - `clear_temp()`:            erases temporary data file
    - `records()`:      calls SeqIO.parse() from the Bio package (optimized for larger files)
    
- `RecordList` - returned by `get_table()`, a quasi list/dict data type for multiple records.
    - `__repr()__`:         returns a "pretty-print" summary of the table
    - `query("query string")`:   runs query through SQL database
    - `columns()`:          returns a dict of column names for the database table
    - `columns_summary()`:  returns a "pretty-print" summary of all of the column names in the database table
    - `summarize()`:        returns a "pretty-print" summary (averages and std. devs) of the items in the list
    - `find_column("search string")`:     returns list of columns that are "like" the passed search_str
    - `save()`:             updates database with newly set values
    - `write_records("out.fna")`: save all sequences in db view (e.g. result of `query()`) to file
    - `write_tsv("out.tsv")`: save all data for current db view (e.g. result of `query()`) to file
    - "quasi list/dict data type"
        - Can iterate over a `RecordList` object
        - Can get `len()` of `RecordList` - e.g. how many records were returned by `query()`
        - Can return `keys()`, `values()`, and `items()`
        - Can return records by index or by id
    - `update(self, data=None, directory_name="None", silent=False, integrity_cancel=False)`
        - Creates new database table schema and updates current values in database by referencing a an `UpdateData` data object

- `UpdateData` - build a dataset with simple variable/attribute assignments
    - See the [blog post](https://cjneely10.github.io/posts/2019/10/MetaSanity-Adding-Additional-Analyses/) for more info

## Usage Best Practices

#### SQLAlchemy

- **BioMetaDB** uses this powerful library to generate and use databases, in this case SQLite3.
- SQLAlchemy is a powerful Python package that makes working with SQL easy and fairly uniform between relational 
database management systems (RdatabaseMSs).
- Read more about SQLAlchemy, its functionality, and its limitations:
<https://docs.sqlalchemy.org/en/latest/orm/tutorial.html>

#### Data file integrity

- **BioMetaDB** uses .tsv files to generate names and data types of columns in the RdatabaseMS tables.
- Before running this software, ensure that data file column names are adequately formatted, with no trailing `\n` 
or `\t` in the file.
    - Columns named `Column.1` and `column_1` will both override to `column_1`.
- Data types are automatically predicted based on a randomly selected value within the column.
    - Ensure that all values in a given column store the same kind of data (e.g. Integer, Float, VARCHAR, etc).
- **BioMetaDB** matches names of data files (e.g. file_1.fasta) to record ids in the .tsv files, so make sure that
they match.

#### Modifying project structure or source code

- **BioMetaDB** relies on the integrity of this file system that it creates when `dbdm INIT` is first called. It is 
ill-advised to manually delete files or records from the database or project, respectively. Updating records using 
`table.save()` is the preferred method for updating database table values within code, but records themselves should
only be removed using `dbdm DELETE`
- Certain portions of the source code can be modified to better fit a user's needs.
    - `BioMetaDB/Models/functions.py` holds the class `Record`, which is the parent class of all database objects 
    generated using `get_table()`. Any additional functions added to this class will be available to your records.
    - `BioMetaDB/DataStructures/record_list.pyx` holds the class `RecordList`, which is a simple container class for 
    handling database records. Currently, this class functions as a quasi-dictionary-and-list data structure.
    - `BioMetaDB/Accessories/update_data.py` provides a dynamic data structure for storing information as object attributes and writing the result to file.

## dbdm

**dbdm** is the primary method for making large-scale changes to the database schema or data files. Use this program 
when first creating your database or when making large updates, such as when adding/removing tables or updating/removing
values or columns.

<pre><code>usage: dbdm.py [-h] [-n DB_NAME] [-t TABLE_NAME] [-d DIRECTORY_NAME]
               [-f DATA_FILE] [-l LIST_FILE] [-c CONFIG_FILE] [-a ALIAS] [-s]
               [-v VIEW] [-q QUERY] [-u UNIQUE] [-i] [-w WRITE] [-x WRITE_TSV]
               [-p PATH]
               program

dbdm:	Manage BioMetaDB project

Available Programs:

CREATE: Create a new table in an existing database, optionally populate using data files
		(Req:  --config_file --table_name --directory_name --data_file --alias --silent --integrity_cancel)
DELETE: Delete list of ids from database tables, remove associated files
		(Req:  --config_file --table_name --list_file --alias --silent --integrity_cancel)
FIX: Repairs errors in DB structure using .fix file
		(Req:  --config_file --data_file --silent --integrity_cancel)
INIT: Initialize database with starting table, fasta directory, and/or data files
		(Req:  --db_name --table_name --directory_name --data_file --alias --silent --integrity_cancel)
INTEGRITY: Queries project database and structure to generate .fix file for possible issues
		(Req:  --config_file --table_name --alias --silent)
MOVE: Move project to new location
		(Req:  --config_file --path --integrity_cancel --silent)
REMOVE: Remove table and all associated data from database
		(Req:  --config_file --table_name --alias --silent --integrity_cancel)
REMOVECOL: Remove column list (including data) from table
		(Req:  --config_file --table_name --list_file --alias --silent --integrity_cancel)
SUMMARIZE: Summarize project and query data. Write records or metadata to file
		(Req:  --config_file --view --query --table_name --alias --write --write_tsv --unique)
UPDATE: Update values in existing table or add new sequences
		(Req:  --config_file --table_name --directory_name --data_file --alias --silent --integrity_cancel)

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
                        /path/to/BioMetaDB-project-directory - Can omit if no other BioMetaDB project present
  -a ALIAS, --alias ALIAS
                        Provide alias for locating and creating table class
  -s, --silent          Silence all standard output (Standard error still displays to screen)
  -v VIEW, --view VIEW  View (c)olumns or (t)ables with SUMMARIZE
  -q QUERY, --query QUERY
                        evaluation ~> genome; function -> gen; eval >> fxn; eval ~> fxn -> gen;
  -u UNIQUE, --unique UNIQUE
                        View unique values of column using SUMMARIZE
  -i, --integrity_cancel
                        Cancel integrity check
  -w WRITE, --write WRITE
                        Write fastx records from SUMMARIZE to outfile
  -x WRITE_TSV, --write_tsv WRITE_TSV
                        Write table record metadata from SUMMARIZE to outfile
  -p PATH, --path PATH  New path for moving project in MOVE command</code></pre>

The typical workflow for initializing **BioMetaDB** is straightforward. Many options exist for updating, adding to, 
and removing from the existing project structure. You may also choose to assign an alternate name to a table within a
database in the form of an alias. Depending on the number of entries involved, these commands can result in voluminous
output, which can either be silenced by passing `-s` as parameters in your command, or by redirecting standard output
to a text file.

After every major change to the project, `dbdm` will run an integrity check. This default can be cancelled by passing `-i`
with each command. However, integrity checks are optimized and useful, so users are advised not to cancel standard checks.

Currently, the following issues are identified in a tab-delimited `.fix` file with each integrity check:

- PROJECT INVALID_PATH:   working_dir path stored in config file is invalid
- RECORD  BAD_TYPE:       data type for record could not be determined
- RECORD  BAD_LOCATION:       stored file path for record does not exist
- FILE    BAD_RECORD:       file exists in project directory with no assigned database id

More information on using this `.fix` file to repair issues can be found in the generated `.fix` file, in the `Accessory 
Scripts` section in this README, and in the provided `Example/` directory.

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
    - --data_file (-f): Path to .tsv file to use to generate database table schema
    - --alias (-a): Alias (short name) for table in database
    - --silent (-s): Silence standard output
    - --integrity_cancel (-i): Cancel integrity check
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
    - --data_file (-f): Path to .tsv file to use to generate database table schema
    - --alias (-a): Alias (short name) for table in database
    - --silent (-s): Silence standard output
    - --integrity_cancel (-i): Cancel integrity check
- Example
    - `dbdm UPDATE -c /path/to/database -t db_table_1 -f /path/to/data_file.tsv -d /path/to/data_dir/`
    - This command will update the table named `db_table_1`, which is part of the database in the project `database`. This 
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
    - --integrity_cancel (-i): Cancel integrity check
- Example
    - `dbdm REMOVECOL -c /path/to/database -t db_table_1 -l /path/to/list_to_remove.list`
    - This command will remove all columns provided in the newline-separated file `list_to_remove.list` from 
    `db_table_1` within the project `database`.
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
    - --integrity_cancel (-i): Cancel integrity check
- Example
    - `dbdm REMOVECOL -c /path/to/database -t db_table_1 -l /path/to/list_to_remove.list`
    - This command will remove all record ids provided in the newline-separated file `list_to_remove.list` from 
    `db_table_1` within the project `database`.
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
    - --data_file (-f): Path to .tsv file to use to generate database table schema
    - --alias (-a): Alias (short name) for table in database
    - --silent (-s): Silence standard output
    - --integrity_cancel (-i): Cancel integrity check
- Example
    - `dbdm CREATE -c /path/to/database -t db_table_2 -d /path/to/data/directory/ 
    -f /path/to/data_file.tsv -a table_2`
    - This command will update the project structure `database` to include the new table:
<pre><code>database/
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
    - --integrity_cancel (-i): Cancel integrity check
- Example
    - `dbdm REMOVE -c /path/to/database -t db_table_2`
    - This command will remove the table `db_table_2` from the project `database`.
    
### MOVE

**MOVE** is used to move an entire project to a different location on the user's filesystem.

- Required flags
    - --config_file (-c): Path to project directory
    - --path (-p): New project path (must exist)
- Optional flags
    - --silent (-s): Silence standard output
    - --integrity_cancel (-i): Cancel integrity check
    
### SUMMARIZE

**SUMMARIZE** is used to display information about the project or a table within the project. This command can also run 
queries to the database and display summary data on only these selected records. See [this blog](https://cjneely10.github.io/posts/2019/10/MetaSanity-Demo-BioMetaDB/) for more info on query statements.

- Required flags
    - --config_file (-c): Path to project directory 
- Optional flags
    - --table_name (-t): Name of table to summarize
    - --alias (-a): Alias (short name) for table in database
    - --view (-v): View (c)olumns or (t)ables
    - --truncate (-r): Return only ID of annotation and not the complete description, excluding Prokka
    - --query (-q): Attach SQL query to summarize select records only. Must be combined with `-t` or `-a` flags
    - --write (-w): Write records in SQL query, or entire table, to directory. Must pass with `-t` or `-a` flags
    - --write_tsv (-x): Write metadata for record in table to file. Must pass with `-t` or `-a` flags
- Examples
    - `dbdm SUMMARIZE -c /path/to/database`
    - This command will summarize all tables in the database. Per table, this command displays the number of records as 
    well as averages and standard deviations for each column.
    - `dbdm SUMMARIZE -t table_name -w output` or `dbdm SUMMARIZE -t table_name -x out.tsv`
    - The first command writes all records in the table `table_name` to `output/`, whereas the second command writes record metadata
    from `table_name` to `out.tsv`.
    - `dbdm SUMMARIZE -t table_name -v c` or `dbdm SUMMARIZE -v t`
    - These commands display the columns in `table_name` and the names of all tables in the project, respectively.
    - See `Examples/README.md` for using the query option.
    - See the [blog post](https://cjneely10.github.io/posts/2019/10/MetaSanity-Demo-BioMetaDB/) for more information.
    
### INTEGRITY

**INTEGRITY** checks the project structure and individual records for missing data files, improperly determined data types,
and errors in the project structure. **INTEGRITY** generates a `.fix` file that lists all issues with default settings to
either do nothing or delete the record that caused the issue. Users can manually edit the file, or use 
`BioMetaDB/AccessoryScripts/edit_fix_file.py` to quickly set values for many records. See the header in a generated `.fix`
file for instructions on setting values.

- Required flags
    - --config_file (-c): Path to project directory
- Example
    - `dbdm INTEGRITY -c /path/to/database`
    - This command will identify all integrity issues in the project `database` and will generate a `########.###.fix` file.
    
### FIX

**FIX** uses the output `.fix` file generated in **INTEGRITY** to repair database issues. See the header in a generated `.fix`
file for instructions on setting values.

- Required flags
    - --config_file (-c): Path to project directory
    - --data_file (-f): Path to `.fix` file generated by `dbdm INTEGRITY`.
- Optional flags
    - --silent (-s): Silence standard output
    - --integrity_cancel (-i): Cancel integrity check
- Example
    - `dbdm FIX -c /path/to/database -f /path/to/########.###.fix`
    - This command will use `########.###.fix` to change values in records in `database`.

## Other Information

### Accessory scripts 

- `BioMetaBD/AccessoryScripts/edit_fix_file.py`
    - Allows users to make multiple changes to a `.fix` file with a single command.
    - This script will look for issues that match all user-passed filtering criteria and will replace the default fix value
    with the user-passed value. Users can reference other fields in ISSUE (see the header in a generated `.fix`
    file).
    - Issues are written as:
    <pre><code>  ISSUE
    DATA_TYPE:    ID[:  LOCATION]
    ISSUE_TYPE  FIX_TYPE[   FIX_DATA]
    ---</code></pre>
    - Required flags
        - --match (-m): Comma-separated list of strings that must be found in issue to make edit
        - --replace (-r): Comma-separated list of strings with FIX_TYPE and value to use 
        - --fix_file (-f): `.fix` file output by `dbdm INTEGRITY`
    - Example
        - `edit_fix_file.py -m RECORD,BAD_TYPE,table_name -r SET,fasta -f /path/to/########.###.fix`
        - This command will replace the default fix value for issues with descriptions matching `RECORD`, `BAD_TYPE`, and
         `table_name`. This fix value will be replaced with `SET    fasta`.
    - Another (more complex) example
        - `edit_fix_file.py -m RECORD,BAD_LOCATION,genomic -r "FILE,/path/to/<ID>.fna" -f /path/to/########.###.fix`
        -  This command will replace the file locations for records with issues in the genomic table. It will replace
        the default fix value with a file location whose value is created using the ID field of that particular issue.
        Notice that the argument passed with `-r` is surrounded by double-quotes.

### Other scripts

#### ArgParse

- `BioMetaBD/Accessories/arg_parse.py`
- **ArgParse** is a simple wrapper script for the Python module `argparse` that reduces the amount of if/then checking.

#### ProgramCaller

- `BioMetaBD/Accessories/program_caller.py`
- **ProgramCaller** is a script made for handling flags and errors in a moderately complex program (such as this one), 
and is highly useful for fast script-making.

### Contact

This project was designed and written by Christopher Neely. Email me anytime at `christopher.neely1200@gmail.com`.
