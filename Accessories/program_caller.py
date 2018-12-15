"""
Script handles program calls and minimizes the amount of code that needs to be written

"""


class ProgramCaller:
    def __init__(self, programs, flags, errors, _help, classes={None: None}):
        """ ProgramCaller is used for when a script has multiple possible sub-programs available.
		Wrapper functionality is available to ensure database or file system integrity

		Example:
			from models import *
			from ArgParse import ArgParse
			from program_caller import ProgramCaller, db_validate

			@db_validate
			def add_file(file, data_type):
				...

			classes = { 	"Plancto":		Planctomycetes}
			programs = {	"ADD":			add_file}
			flags = {		"ADD":			("file", "data_type")}
			errors = {		"INCORRECT_DB_TYPE":		"Incorrect database called"}
			_help = {	"ADD":		"Program for adding files to database"}

			args_list = [
				[["-f", "--file"],
				{"help": "File to pass"}],
				[["-d", "--data_type"],
				{"help": "Type of data (fasta or fastq)"}],
			]

			ap = ArgParse(args_list, description="Program to add file to database by type")
			pc = ProgramCaller(classes=classes, programs=programs, flags=flags, errors=errors, _help=_help)

			pc.run(ap.args)
			

		:param classes: (Dict[str, class])		Class mappings
		:param programs: (Dict[str, callable])	Program name: function mapping
		:param flags: (Dict[str, tuple])		Flag mapping program_name: (needed flags,)
		:param errors: (Dict[str, str])			Error string to print by error type
		"""
        self.classes = classes
        self.programs = programs
        self.flags = flags
        self.errors = errors
        self.errors["INCORRECT_FLAGS"] = "Pass all necessary flags:"
        self._help = _help

    def error(self, error_type, program):
        """ Function called to handle error

		:param error_type: (str)	Key for type of error
		:param program: (str)	Name of program that was called
		"""
        if type(error_type) == str:
            if "flags" in error_type or "FLAGS" in error_type:
                print()
                print(" ERROR " + self.errors["INCORRECT_FLAGS"], "--" + " --".join(self.flags[program]))
        else:
            print()
            print(" ERROR " + self.errors[error_type])
        if program in self._help.keys():
            print()
            print(" " + program + ": " + self._help[program])
        print()
        exit(1)

    def mapper(self, program):
        """ Function maps the name of a program with its given function and returns function call
		Catches errors that may arise and returns user-defined response

		:param program: (str)	Name of program to use in programs dict to call function
		:return function:
		"""
        try:
            return self.programs[program](**self.flags_dict)
        except Exception as e:
            try:
                print(self.error(type(e), program))
            except KeyError:
                print("An untracked exception has occurred\n Class: {}\n {}".format(type(e), e))

    def flag_check(self, program, ap_args_object):
        """ Function checks if required flags were set for a given program

		:param program: (str)	Name of program
		:param flags_dict: (Dict[str])	Dictionary with key: progname and value: needed flags
		:return bool:
		"""
        try:
            self.flags_dict = {flag: vars(ap_args_object)[flag] for flag in self.flags[program]}
        except KeyError as e:
            print(" ERROR: Invalid program name", str(e))
            exit(1)
        for flag in self.flags[program]:
            if not self.flags_dict[flag] or self.flags_dict[flag] == "":
                return False
        return True

    def run(self, args):
        """ Primary function to call ProgramCaller and to run the script

		:param args: (ArgParse.args)	ArgParse.args object
		"""
        program = args.program
        if self.flag_check(program, args):
            self.mapper(program)
        else:
            self.error("INCORRECT_FLAGS", program)


def db_validate(func):
    def wrapped(*args, **kwargs):
        func(*args, **kwargs)

    return func
