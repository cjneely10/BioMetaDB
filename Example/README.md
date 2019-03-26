# BioMetaDB Example

## About

This README file will provide a simple walk-through example that outlines key features and functionality within BioMetaDB.

In this example, users will create a simple database of `Quast` and `diamond` outputs for various reference genomes.

The following files are available for this example:

<pre><code>Example/
    plants/
    prokaryotes/
    plants.tsv
    prokaryotes.tsv
    prokaryotes_update.tsv
    columns_to_delete.list
    records_to_delete.list</code></pre> 

The `.tsv` files contain output related to each genome.
The `.list` files are used in the end of this example. 
The sequences gathered for this example are all NCBI RefSeq assemblies.

**Note**: All fasta files are gzipped, and the provided `.tsv` files use extensions `.fna`. 
Be sure to gunzip all fasta files prior to use.

### In this example, users will:

1. Create a database for tracking features in model organisms.
    1. Create a table in database for prokaryotes.
    2. Populate database tables with output from `Quast`.
2. Update the database with a new table.
    1. Create a table for plants and populate with output from `diamond`.
3. View a summary of the database in its current state
5. Write a simple script that queries the database and updates values.
6. Update table with additional data.
7. Remove extraneous columns and records.
8. Delete plant table.
9. Ensure the table is appropriately integrated.

## Create database and initial file system using prokaryote data

1. Ensure that `BioMetaDB` is installed.
2. Navigate to a directory where you would like to initialize this project's directory.
3. Run the following command:
    1. `dbdm INIT -n ModelOrganisms -d /path/to/Example/prokaryotes/ -t Prokaryotes -a pro 
    -f /path/to/Example/prokaryotes.tsv`
    2. This will generate a new project structure, titled `ModelOrganisms`, in your current directory. This project will 
    contain the database named `ModelOrganisms` and will have the table `Prokaryotes`, accessible using the alias `pro`. 
    The table schema will use information from `prokaryotes.tsv` to generate table columns.
<pre><code>ModelOrganisms
├── classes
│   └── prokaryotes.json
├── config
│   └── ModelOrganisms.ini
├── db
│   ├── ModelOrganisms.db
│   └── prokaryotes
│       ├── Aliivibrio_fischeri.fna
│       ├── Azotobacter_vinelandii.fna
│       ├── Bacillus_subtilis.fna
│       ├── Caulobacter_crescentus.fna
│       ├── Escherichia_coli.fna
│       ├── Mycoplasma_genitalium.fna
│       ├── Pseudomonas_fluorescens.fna
│       └── Streptomyces_coelicolor.fna
└── migrations
    └── ########.migrations.mgt
</code></pre>

## Update the database with a new table for plants

1. Run the following command:
    1. `dbdm CREATE -c /path/to/Example/ModelOrganisms -d /path/to/Example/plants/ 
    -t plants -a plants -f /path/to/Example/plants.tsv`
    2. This will add a new table to the project `ModelOrganisms`. This project will now have the table `plants`, 
    accessible with `plants`, and populated using `plants.tsv`.
<pre><code>ModelOrganisms
├── classes
│   ├── plants.json
│   └── Prokaryotes.json
├── config
│   └── ModelOrganisms.ini
├── db
│   ├── ModelOrganisms
│   ├── ModelOrganisms.db
│   ├── plants
│   │   ├── Arabidopsis_thaliana.fna
│   │   ├── Brachypodium_distachyon.fna
│   │   ├── Selaginella_moellendorffii.fna
│   │   └── Solanum_lycopersicum.fna
│   └── prokaryotes
│       ├── Aliivibrio_fischeri.fna
│       ├── Azotobacter_vinelandii.fna
│       ├── Bacillus_subtilis.fna
│       ├── Caulobacter_crescentus.fna
│       ├── Escherichia_coli.fna
│       ├── Mycoplasma_genitalium.fna
│       ├── Pseudomonas_fluorescens.fna
│       └── Streptomyces_coelicolor.fna
└── migrations
    └── ########.migrations.mgt
</code></pre>

## View a summary of the database

Often, one may wish to view a summary of the information stored in a database or table. This is helpful for getting a 
quick glance at a particular table or database, as well as to test queries on the command line.

1. Run the following command to retrieve a summary of all tables in the project:
    1. `dbdm SUMMARIZE -c /path/to/ModelOrganisms`
    2. This command will display a simple summary of all records in all tables in the project. Averages and standard
    deviations are automatically calculated for valid fields.
    3. Other flags:
        1. `-v/--view`  View only column names
        2. `-t/--table_name`    View only for given table
        3. `-a/--alias`     View only for given alias
        4. `-q/--query`     Attach SQL query to summarize select records only. Must be combined with `-t` or `-a` flags
<pre><code>SUMMARIZE:      View summary of all tables in database
 Project root directory:        ModelOrganisms
 Name of database:              ModelOrganisms.db

**********************************************************************
                 Table Name:    prokaryotes
          Number of Records:    8

                 Column Name    Average         Std Dev

                          gc    53.751          14.849
    (...)
                         n50    4653940.750     2440726.993
                         n75    4458040.375     2655302.860
    (...)
                total_length    4874381.000     2438681.143
    (...)
        total_length_gt_1000    4874381.000     2438681.143
----------------------------------------------------------------------

**********************************************************************
                 Table Name:    plants
          Number of Records:    3

                 Column Name    Average         Std Dev

                          gc    42.560          5.660
    (...)
                         n50    28113428.000    28972021.833
                         n75    23065659.000    24023210.450
    (...)
                total_length    201093640.333   76435013.348
    (...)
        total_length_gt_1000    201090333.333   76434285.411
----------------------------------------------------------------------</code></pre>

## Simple scripting: Get assemblies with an n50 value that is less than its length

The below script will allow users to use a database query to identify genome assemblies that may still need a little work.

<pre><code>#!/usr/bin/env python3.5

from BioMetaDB import get_table

# Generate database session and get a reference to the database table
# Can also access through table_name instead of alias
table = get_table("/path/to/DB", alias="pro")

# Query the database for records whose n50 is less than their total length
table.query("n50 < total_length")
print(len(table))  # Prints 2
print(table.columns())  # Prints all columns as dict_keys

# View query results
for match in table:
    print(match)  # 'pretty-print' viewing of record

# Change value of first record retrieved in query
table[0].n75 = 0
print(table[0].n75)  # Prints 0 to screen
table.save()  # Saves data to database

# Search for field names, 
table.find_column("totallength")  # Returns list ['total_length', 'total_length_gt_0', ...]
table.find_column("totallength$")  # Returns ['total_length']

</code></pre>

The power of the SQLAlchemy package becomes apparent here - users can easily create fast and powerful SQL queries that 
are based on the fields provided in the `.tsv` file!

## Update an existing table with additional data

After completing additional tests, for example BLAST or diamond searches, use `.tsv` output to update the database. In this
example, `diamond` was used to search for Nitrogen Fixation genes within the model organisms' genomes. A `.tsv` summary file
was generated, and this will be used to update the database schema. In this example, no additional genomes are saved.

1. Run the following command:
    1. `dbdm UPDATE -c /path/to/ModelOrganisms -f /path/to/Example/prokaryotes_update.tsv -a pro`
    2. This command will update the table associated with the alias `pro` in the project `DB` to include additional columns 
    and column data from `prokaryotes_update.tsv`.
    
Running the same script above will now display additional values related to nitrogen fixation.

## Remove unnecessary columns and records

Occasionally, users may wish to remove certain columns from being tracked. Users may also wish to remove a large number 
of records and files from the project at a given time.

#### Removing columns

For the file called `columns_to_delete.list` that contains a list of column names:
<pre><code>nifd
nifh
</code></pre>
1. Run the following command to remove items in this file:
    1. `dbdm REMOVECOL -c /path/to/ModelOrganisms -a pro -l /path/to/Example/columns_to_delete.list`
    2. This command will remove all columns in `columns_to_delete.list` from the database. This will also remove 
    associated data
    
#### Deleting records

For the file called `records_to_delete.list` that contains a list of files:
<pre><code>Bacillus_subtilis.fna
</code></pre>
1. Run the following command to delete these records from the database:
    1. `dbdm DELETE -c /path/to/ModelOrganisms -a pro -l /path/to/Example/records_to_delete.list`
    2. This command will remove all records in `records_to_delete.list` from the project `DB`.

## Remove table from database

Users may choose to remove a table from the project entirely. This action will remove all records and files associated with
the provided table.

1. Run the following command to remove a table from the project structure:
    1. `dbdm REMOVE -c /path/to/ModelOrganisms -a plants`
    2. This command will remove the `plants` table from the project.
<pre><code>ModelOrganisms
├── classes
│   └── Prokaryotes.json
├── config
│   └── ModelOrganisms.ini
├── db
│   ├── ModelOrganisms
│   ├── ModelOrganisms.db
│   └── Prokaryotes
│       ├── Aliivibrio_fischeri.fna
│       ├── Azotobacter_vinelandii.fna
│       ├── Caulobacter_crescentus.fna
│       ├── Escherichia_coli.fna
│       ├── Mycoplasma_genitalium.fna
│       ├── Pseudomonas_fluorescens.fna
│       └── Streptomyces_coelicolor.fna
└── migrations
    └── ########.migrations.mgt
</code></pre>
