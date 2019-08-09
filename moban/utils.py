import os
import sys
import errno
import logging

import fs
from moban import constants, exceptions, file_system

LOG = logging.getLogger(__name__)
PY2 = sys.version_info[0] == 2


def merge(left, right):
    """
    deep merge dictionary on the left with the one
    on the right.

    Fill in left dictionary with right one where
    the value of the key from the right one in
    the left one is missing or None.
    """
    if isinstance(left, dict) and isinstance(right, dict):
        for key, value in right.items():
            if key not in left:
                left[key] = value
            elif left[key] is None:
                left[key] = value
            else:
                left[key] = merge(left[key], value)
    return left


def search_file(base_dir, file_name):
    the_file = file_name
    if not file_system.exists(the_file):
        if base_dir:
            file_under_base_dir = file_system.url_join(base_dir, the_file)
            if file_system.exists(file_under_base_dir):
                the_file = file_system.fs_url(file_under_base_dir)
            else:
                raise IOError(
                    constants.ERROR_DATA_FILE_NOT_FOUND % (file_name, the_file)
                )
        else:
            raise IOError(constants.ERROR_DATA_FILE_ABSENT % the_file)
    return the_file


def file_permissions_copy(source, dest):
    source_permissions = file_permissions(source)
    dest_permissions = file_permissions(dest)

    if source_permissions != dest_permissions:
        os.chmod(dest, source_permissions)


def file_permissions(afile):
    if not file_system.exists(afile):
        raise exceptions.FileNotFound(afile)
    return file_system.file_permissions(afile)


def write_file_out(filename, content):
    if PY2 and content.__class__.__name__ == "unicode":
        content = content.encode("utf-8")

    if not file_system.is_zip_alike_url(filename):
        # fix me
        dest_folder = os.path.dirname(filename)
        if dest_folder:
            mkdir_p(dest_folder)

    file_system.write_bytes(filename, content)


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def pip_install(packages):
    import subprocess

    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", " ".join(packages)]
    )


def get_template_path(template_dirs, template):
    for a_dir in template_dirs:
        try:
            template_under_dir = file_system.url_join(a_dir, template)
            template_file_exists = file_system.exists(
                template_under_dir
            ) and file_system.is_file(template_under_dir)

            if template_file_exists:
                return file_system.fs_url(template_under_dir)
        except fs.errors.CreateFailed:
            continue
    raise exceptions.FileNotFound


def verify_the_existence_of_directories(dirs):
    LOG.debug("Verifying the existence: %s", dirs)
    if not isinstance(dirs, list):
        dirs = [dirs]

    results = []

    for directory in dirs:

        if file_system.exists(directory):
            results.append(directory)
            continue
        should_I_ignore = (
            constants.DEFAULT_CONFIGURATION_DIRNAME in directory
            or constants.DEFAULT_TEMPLATE_DIRNAME in directory
        )
        if should_I_ignore:
            # ignore
            pass
        else:
            raise exceptions.DirectoryNotFound(
                constants.MESSAGE_DIR_NOT_EXIST % directory
            )
    return results


def find_file_in_template_dirs(src, template_dirs):
    LOG.debug(template_dirs)
    for folder in template_dirs:
        path = file_system.url_join(folder, src)
        if file_system.exists(path):
            return path
    else:
        return None
