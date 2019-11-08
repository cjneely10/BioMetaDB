import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, create_session
from sqlalchemy.ext.declarative import declarative_base

""" Class for handling Bsse schema requests, gathering metadata and session info, etc.



"""


class BaseData:
    """ Class for storing database config values, initial creation, and creating session

    """
    Base = declarative_base()

    @staticmethod
    def get_uri(basedir, db_name):
        """

        :param db_name: (str)	Name of database, preferably from child class DBNames
        """
        return os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, db_name)

    @staticmethod
    def create(basedir, db_name):
        """ Creates all tables in engine

        :param basedir: (str) Base directory of database folder
        :param db_name: (str) Name of database to create. Should reference from child class DBNames
        """
        SQLALCHEMY_DATABASE_URI = BaseData.get_uri(basedir, db_name)
        engine = create_engine(SQLALCHEMY_DATABASE_URI)
        # Creates all tables in database
        BaseData.Base.metadata.create_all(engine)

    @staticmethod
    def get_session(basedir, db_name):
        """ Returns session variable

        :param basedir: (str) Base directory of database folder
        :param db_name: (str) Name of database for which to create session
        :return Object:
        """
        SQLALCHEMY_DATABASE_URI = BaseData.get_uri(basedir, db_name)
        engine = create_engine(SQLALCHEMY_DATABASE_URI)
        # Returns session for CRUD operations on database
        return sessionmaker(bind=engine)()

    @staticmethod
    def get_session_from_engine(e):
        """ Returns session variable

        :param e: (Engine)  Engine object
        :return Object:
        """
        # Returns session for CRUD operations on database
        return create_session(bind=e, autocommit=False, autoflush=True)

    @staticmethod
    def get_engine(basedir, db_name):
        """ Returns session variable

        :param basedir: (str) Base directory of database folder
        :param db_name: (str) Name of database for which to create session
        :return Object:
        """
        SQLALCHEMY_DATABASE_URI = BaseData.get_uri(basedir, db_name)
        engine = create_engine(SQLALCHEMY_DATABASE_URI)
        # Returns session for CRUD operations on database
        return engine
