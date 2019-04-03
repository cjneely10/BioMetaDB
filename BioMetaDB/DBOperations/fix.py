import os
from BioMetaDB.Config.config_manager import ConfigManager, ConfigKeys
from BioMetaDB.Exceptions.fix_exceptions import FixAssertString
from BioMetaDB.DBManagers.integrity_manager import IntegrityManager
from BioMetaDB.DBOperations.integrity_check import integrity_check


def _fix_display_message_prelude(db_name, working_directory, fixfile_prefix):
    """ Display initial message summarizing operation on files

    :param db_name:
    :param working_directory:
    :param fixfile_prefix:
    :return:
    """
    print("FIX:\tUse .fix file to repair project issues")
    print(" Project root directory:\t%s" % working_directory)
    print(" Name of database:\t\t%s" % db_name)
    print(" Fix file to use:\t\t%s\n" % fixfile_prefix)


def _fix_display_message_epilogue():
    print("\nProject fix complete! Re-run INTEGRITY to confirm!", "\n")


def fix(config_file, data_file, silent, integrity_cancel):
    """ Function called from dbdm that commits all fixes listed in .fix file to project

    :param config_file:
    :param data_file:
    :param silent:
    :return:
    """
    _cfg, _sil = config_file, silent
    config, config_file = ConfigManager.confirm_config_set(config_file)
    assert os.path.exists(data_file) and os.path.splitext(data_file)[1] == ".fix", FixAssertString.FIX_NOT_FOUND
    if not silent:
        _fix_display_message_prelude(
            config[ConfigKeys.DATABASES][ConfigKeys.db_name],
            config[ConfigKeys.DATABASES][ConfigKeys.working_dir],
            data_file
        )

    im = IntegrityManager(config, data_file)
    im.parse_and_fix(silent)
    if not silent:
        _fix_display_message_epilogue()
    if not integrity_cancel:
        integrity_check(_cfg, "None", "None", _sil)
