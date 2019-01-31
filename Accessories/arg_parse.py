#!/usr/bin/env python3

import argparse
from argparse import RawTextHelpFormatter


class ArgParse:

    def __init__(self, arguments_list, description, *args, **kwargs):
        """ Class for handling parsing of arguments and error handling

        Example:

        args_list = [
            [["required_argument"],
                {"help": "Help string for argument"}],
            [["-o", "--optional"],
                {"help": "Optional argument", "default": "None"}],
            [["-r", "--required"],
                {"help": "Required argument", "require": "True"}]
        ]

        ap = ArgParse(args_list, description="Sample:\tSample program")

        ## Now you can access as ap.args.required_argument, ap.args.optional, and ap.args.required
        ## Note that you CANNOT use '-' in the names of arguments!
        ## Note that any other constructor argument that argparse.ArgumentParser() takes will also be used

        Ensure that the final value in the inner list does not have '-' characters
        Include "require": True in inner dictionary to treat arg as required

        :param arguments_list: List[List[List[str], Dict[str, str]]]
        """
        self.arguments_list = arguments_list
        self.args = []
        self.required_options = {}
        # Instantiate ArgumentParser
        self.parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter, description=description,
                                              *args, **kwargs)
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
            # Be default names argument by last value passed in inner list
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

    @staticmethod
    def description_builder(header_line, help_dict, flag_dict):
        assert set(help_dict.keys()) == set(flag_dict.keys()), "Program names do not match in key/help dictionaries"
        to_return = header_line + "\n\nAvailable Programs:\n\n"
        programs = sorted(flag_dict.keys())
        for program in programs:
            to_return += program + ": " + help_dict[program] + "\n\t" + \
                         "\t(Req: {})".format(" --" + " --".join(flag_dict[program])) + "\n"
        to_return += "\n"
        return to_return


if __name__ == '__main__':
    args_list = [
        [["required_argument"], {"help": "Help string for argument"}],
        [["-o", "--optional"], {"help": "Optional argument"}],
        [["-r", "--required"], {"help": "Required argument", "require": "True"}]
    ]
    ap = ArgParse(args_list, description="Sample ArgParse program!")
