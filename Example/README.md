# BioMetaDB Example

## About

This README file will provide a simple walk-through example that outlines key features and functionality within BioMetaDB.

In this example, users will create a simple database of `Quast` output for various reference genomes.

The following files are available for this example:

<pre><code>Example/
    plants/
    prokaryotes/
    plants.tsv
    prokaryotes.tsv
    prokaryotes_update.tsv
    columns_to_delete.list
    records_to_delete.list
</code></pre> 

The `.tsv` files contain output related to each genome.
The `.list` files are used in the end of this example. 
The sequences gathered for this example are all NCBI RefSeq assemblies.

**Note**: All fasta files are gzipped, and the provided `.tsv` files use extensions `.fna`. 
Be sure to gunzip all fasta files prior to use.

In this example, users will:

1. Create a database for tracking features in model organisms.
    1. Create a table in database for prokaryotes.
    2. Populate database tables with output from `Quast`.
2. Update the database with a new table.
    1. Create a table for plants and populate with output from `diamond`.
3. Write a simple script that queries the database and updates values.
4. Update table with additional data.
5. Remove extraneous columns and records.
6. Delete plant table.

## Create database and initial file system using prokaryote data

1. Ensure that `BioMetaDB` is installed.
2. Navigate to a directory where you would like to initialize this project's directory.
3. Run the following command:
    1. `dbdm INIT -w DB -n ModelOrganisms -d /path/to/Example/prokaryotes/ -t Prokaryotes -a pro -f /path/to/Example/prokaryotes.tsv`
    2. This will generate a new project structure, titled `DB`, in your current directory. This project will contain the
    database named `ModelOrganisms` and will have the table `Prokaryotes`, accessible using the alias `pro`. The table
    schema will use information from `prokaryotes.tsv` to generate table columns.
<pre><code>DB
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
    1. `dbdm CREATE -c /path/to/Example/DB -d /path/to/Example/plants/ -t Plants -a plants -f /path/to/Example/plants.tsv`
    2. This will add a new table to the database `ModelOrganisms` within the project structure `DB`. This project will
    now have the table `Plants`, accessible with `plants`, and populated using `plants.tsv`.
<pre><code>DB
├── classes
│   ├── Plants.json
│   └── Prokaryotes.json
├── config
│   └── ModelOrganisms.ini
├── db
│   ├── ModelOrganisms
│   ├── ModelOrganisms.db
│   ├── Plants
│   │   ├── Arabidopsis_thaliana.fna
│   │   ├── Brachypodium_distachyon.fna
│   │   ├── Selaginella_moellendorffii.fna
│   │   └── Solanum_lycopersicum.fna
│   └── Prokaryotes
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

## Simple scripting: Get assemblies with an n50 value that is less than its length

The below script will allow users to user a database query to identify genome assemblies that may still need a little work.

<pre><code>#!/usr/bin/env python3.5

from BioMetaDB import get_table

# Generate database session and get a reference to the database table
# Can also access through table_name instead of alias
sess, Table = get_table("/path/to/DB", alias="pro")

# Query the database for records whose n50 is less than their total length
matching_genomes = sess.query(Table).filter(Table.n50 < Table.total_length).all()

# View query results
for match in matching_genomes:
    print(match)
</code></pre>

The power of the SQLAlchemy package becomes apparent here - using the `filter` function, users can easily create fast and
powerful SQL queries that are based on the fields provided in the `.tsv` file!

## Update an existing table with additional data

After completing additional tests, for example BLAST or diamond searches, use `.tsv` output to update the database. In this
example, `diamond` was used to search for Nitrogen Fixation genes within the model organisms' genomes. A `.tsv` summary file
was generated, and this will be used to update the database schema. In this example, no additional genomes are saved.

1. Run the following command:
    1. `dbdm UPDATE -c /path/to/DB -f /path/to/Example/prokaryotes_update.tsv -a pro`
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
    1. `dbdm REMOVECOL -c /path/to/DB -a pro -l /path/to/Example/columns_to_delete.list`
    2. This command will remove all columns in `columns_to_delete.list` from the database. This will also remove 
    associated data
    
#### Deleting records

For the file called `records_to_delete.list` that contains a list of files:
<pre><code>Bacillus_subtilis.fna
</code></pre>
1. Run the following command to delete these records from the database:
    1. `dbdm DELETE -c /path/to/DB -a pro -l /path/to/Example/records_to_delete.list`
    2. This command will remove all records in `records_to_delete.list` from the project `DB`. 

## Remove table from database

Users may choose to remove a table from the project entirely. This action will remove all records and files associated with
the provided table.

1. Run the following command to remove a table from the project structure:
    1. `dbdm REMOVE -c /path/to/DB -a plants`
    2. This command will remove the `plants` table from the project.
<pre><code>DB
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
