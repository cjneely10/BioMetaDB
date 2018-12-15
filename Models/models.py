import os
from fastbio import BioParse
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

""" Typical usage:

First time:
	from models import *
	BaseData.create_all()

Querying and performing operations:
	from models import *
	sess = BaseData.get_session(DBNames.Genomic)
	
	sess.query(Sequence).all()	# Get all values
	sess.query(Sequence).filter(Sequence.location == Sequence.FileLocations.GEN).all()	# Get genome folder values
	sess.query(Sequence).filter(Sequence.data_type == Sequence.DataTypes.AA).all()	# Get all amino acids

	record = sess.query(Sequence).first()	# Query first value in database
	record_as_bio_record = record.get_records()	# Return file contents as SeqRecord objects

"""
class DBNames:
	""" Class for holding names of databases and locations of specific project-related info

	"""
	Planctomycetes = "Planctomycetes.db"

class BaseData:
	""" Class for storing database config values, initial creation, and creating session
	
	"""

	# Base directory for entire database cluster
	basedir = "/media/imperator/cneely"
	Base = declarative_base()

	@staticmethod
	def _get_uri(db_name):
		"""

		:param db_name: (str)	Name of database, preferably from child class DBNames
		"""
		return os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(BaseData.basedir, db_name)

	@staticmethod
	def create(db_name):
		""" Creates all tables in engine

		:param db_name: (str) Name of database to create. Should reference from child class DBNames
		"""
		SQLALCHEMY_DATABASE_URI = BaseData._get_uri(db_name)
		engine = create_engine(SQLALCHEMY_DATABASE_URI)
		# Creates all tables in database
		BaseData.Base.metadata.create_all(engine)

	@staticmethod
	def get_session(db_name):
		""" Returns session variable

		:param db_name: (str) Name of database for which to create session
		:return Object:
		"""
		SQLALCHEMY_DATABASE_URI = BaseData._get_uri(db_name)
		engine = create_engine(SQLALCHEMY_DATABASE_URI)
		# Returns session for CRUD operations on database
		return sessionmaker(bind=engine)()


""" Database schema requirements:

Each class representing a table in a database must have:
	a db_name class attribute set
	a __tablename__ class attribute set
	a genome_id attribute
	a data_type attribute
	a location attribute
	an id attribute as Column(Integer, primary_key=True)
	a child class for DataTypes
	a child class for FileLocations
	It is advisable to have getter/setter methods prepared for each class


"""
class Planctomycetes(BaseData.Base):
	""" Class for retrieving genomic data by storing metadata in database

	"""
	db_name = DBNames.Planctomycetes
	__tablename__ = 'planctomycetes'

	id = Column(Integer, primary_key=True)
	genome_id = Column(String, unique=True, index=True)
	data_type = Column(String, index=True)
	location = Column(String, index=True)
	completeness = Column(Float, index=True, default=0.0)
	contamination = Column(Float, index=True, default=0.0)
	heterogeneity = Column(Float, index=True, default=0.0)
	is_contaminated = Column(Boolean, index=True, default=False)
	is_complete = Column(Boolean, index=True, default=False)
	needs_refining = Column(Boolean, index=True, default=False)
	is_non_redundant = Column(Boolean, index=True, default=False)

	def __repr__(self):
		return "".join(['{',
			'"genome_id": "', str(self.genome_id), '", ',
			'"data_type": "', str(self.data_type), '", ',
			'"location": "', str(self.location), '", ',
			'"completeness": "', str(self.completeness), '", ',
			'"contamination": "', str(self.contamination), '", ',
			'"heterogeneity": "', str(self.heterogeneity), '", ',
			'"is_contaminated": "', str(self.is_contaminated), '", ',
			'"is_complete": "', str(self.is_complete), '", ',
			'"needs_refining": "', str(self.needs_refining), '", ',
			'"is_non_redundant": "', str(self.is_non_redundant), '", ',
			'"id": "', str(self.id), '"}'
			])

	def get(self):
		""" Method for retrieving file contents
		
		:return str:
		"""
		file_contents = ""
		with open(self.full_path(), "r") as R:
			file_contents += R.read()
		return file_contents

	def print(self):
		""" Method for printing file contents to screen

		"""
		with open(self.full_path(), "r") as R:
			print(R.read())

	def full_path(self):
		""" Method returns full path
		
		:return str:
		"""
		return self.location + "/" + self.genome_id + "." + self.data_type

	def write(self):
		""" Method writes file contents to temporary file and stores file name in object

		"""
		filename = self.genome_id + ".tmp." + self.data_type
		W = open(filename, "w")
		with open(self.full_path(), "r") as R:
			W.write(R.read())
		W.close()
		self.temp_filename = filename

	def clear(self):
		""" Method for deleting temporary file

		"""
		if self.temp_filename:
			os.remove(self.temp_filename)
			self.temp_filename = None

	def get_records(self):
		""" Method returns contents of record's file as a list of SeqRecord objects
		
		:return List[SeqRecord]
		"""
		data_type = "fasta"
		if self.data_type == "fq":
			data_type = "fastq"
		return list(BioParse.parse(self.full_path()))

	def set_flags(self):
		if (self.completeness > 90 and self.contamination < 10) or \
			(self.completeness >= 80 and self.contamination <= 10) or \
			(self.completeness > 50 and self.contamination <= 5):
			self.is_complete = True
		elif self.completeness >= 50 and self.contamination >= 5:
			self.needs_refining = True
		else:
			self.is_contaminated = True

	class DataTypes:
		""" Class for enumerating possible file types

		"""
		AA = "faa"
		DNA = "fna"
		FQ = "fq"


	class FileLocations:
		""" Class for holding directory locations that will be maintained by database

		"""
		AA = BaseData.basedir + "/aa_complete"
		CDS = BaseData.basedir + "/cds_complete"
		GEN = BaseData.basedir + "/genomes_complete"
	