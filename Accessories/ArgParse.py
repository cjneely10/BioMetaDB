import argparse
from argparse import RawTextHelpFormatter


class ArgParse:

    def __init__(self, arguments_list, *args, **kwargs):
        """ Class for handling parsing of arguments and error handling

		Example arguments_list:
		[
			[["required_argument"],
				{"help": "Help string for argument"}],
			[["-o", "--optional"],
				{"help": "Optional argument"}],
			[["-r", "--required"],
				{"help": "Required argument", "require": "True"}]
		]

		Ensure that the final value in the inner list does not have '-' characters
Include "require": True in inner dictionary to treat arg as required


		:param arguments_list: List[List[List[str], Dict[str, str]]]
		"""
        self.arguments_list = arguments_list
        self.args = []
        self.required_options = {}
        # Instantiate ArgumentParser
        self.parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter, *args, **kwargs)
        # Add all arguments stored in self.arguments_list
        self._parse_arguments()
        # Parse arguments
        try:
            self.args = self.parser.parse_args()
            self._require_optional()
        except:
            exit(1)

    def _parse_arguments(self):
        """ Protected method for adding all arguments stored in self.arguments_list
		Checks value of "require" and sets accordingly

		"""
        for args in self.arguments_list:
            # Store requirement for option by popping from args dictionary
            # Be default names argument by last value passed in innter list
            self.required_options[args[0][-1]] = bool(args[1].pop('require', False))
            self.parser.add_argument(*args[0], **args[1])

    def _require_optional(self):
        """ Protected member for validating "require" arguments

		"""
        passed = True
        for args in self.arguments_list:
            # If argument is in "required" list and has not been set
            # raise exception
            _arg = args[0][-1]
            if self.required_options[_arg] and not getattr(self.args, _arg.strip("--")):
                print("Argument required: {}".format(_arg))
                passed = False
        if not passed:
            raise Exception


if __name__ == '__main__':
    args_list = [
        [["required_argument"], {"help": "Help string for argument"}],
        [["-o", "--optional"], {"help": "Optional argument"}],
        [["-r", "--required"], {"help": "Required argument", "require": "True"}]
    ]
    ap = ArgParse(args_list)
