import sqlalchemy as sa
from Models.models import Model

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


class Planctomycetes(Model):
    """ Class for retrieving genomic data by storing metadata in database

    """
    db_name = "Planctomycetes.db"
    __tablename__ = 'planctomycetes'

    completeness = sa.Column(sa.Float, index=True, default=0.0)
    contamination = sa.Column(sa.Float, index=True, default=0.0)
    heterogeneity = sa.Column(sa.Float, index=True, default=0.0)
    is_contaminated = sa.Column(sa.Boolean, index=True, default=False)
    is_complete = sa.Column(sa.Boolean, index=True, default=False)
    needs_refining = sa.Column(sa.Boolean, index=True, default=False)
    is_non_redundant = sa.Column(sa.Boolean, index=True, default=False)

    def __repr__(self):
        return "".join(['{',
                        '"genome_id": "', str(self._id), '", ',
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
        AA = Model.basedir + "/aa_complete"
        CDS = Model.basedir + "/cds_complete"
        GEN = Model.basedir + "/genomes_complete"
