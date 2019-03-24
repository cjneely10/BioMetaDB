"""
Script holds functionality for handling data types associated with database records
Based on verbosity, will calculate standard deviation and averages of numerical values
And will provide info about most frequently occurring characters/words in character values

"""


class RecordList(list):
    def __init__(self, *args, **kwargs):
        # initialize superclass
        super().__init__(*args, **kwargs)
