"""
setup / install / distribute
"""
# =====================================================================================================================
# init script env -- ensure cwd = root of source dir
# =====================================================================================================================
from copy import deepcopy
from ctypes.util import find_library as ctypes_util_find_library
from inspect import (
    currentframe as inspect_currentframe,
    getfile as inspect_getfile,
)
from os import (
    listdir as os_listdir,
    remove as os_remove,
    walk as os_walk,
)
from os.path import (
    abspath as path_abspath,
    dirname as path_dirname,
    exists as path_exists,
    isfile as path_isfile,
    join as path_join,
    splitext as path_splitext,
)
from shutil import rmtree as shutil_rmtree
from sys import (
    argv as sys_argv,
    exit as sys_exit,
)

from setuptools import (
    Command as setuptools_Command,
    Extension as setuptools_Extension,
    find_packages as setuptools_find_packages,
    setup as setuptools_setup,
)


# Warning : do not import the distutils extension before setuptools It does break the cythonize function calls
# https://github.com/enthought/pyql/blob/master/setup.py
from Cython.Build import cythonize
from Cython.Compiler.Options import parse_directive_list

SCRIPT_PATH = path_dirname(path_abspath(inspect_getfile(inspect_currentframe())))
PACKAGE_NAME = 'PyLCONF'
ROOT_PACKAGE_PATH = path_join(path_dirname(SCRIPT_PATH), PACKAGE_NAME)
MAIN_PACKAGE_PATH = path_join(ROOT_PACKAGE_PATH, PACKAGE_NAME)

VERSION = __import__(PACKAGE_NAME).__version__

# check some untested options
for option_temp in {'bdist_dumb', 'bdist_rpm', 'bdist_wininst', 'bdist_egg'}:
    if option_temp in sys_argv:
        print('''

            You specified an untested option: <{}>\n\n

                This might work or might not work correctly.

            '''.format(option_temp))


# =====================================================================================================================
# helper classes, functions
# =====================================================================================================================
def read_requires(filename):
    requires = []
    with open(filename, 'r') as file_:
        for line in file_:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            requires.append(line)
    return requires


def no_cythonize(extensions):
    """ Helper: based on https://github.com/ryanvolz/radarmodel(Copyright (c) 2014, Ryan Volz)
    """
    dupextensions = deepcopy(extensions)
    for extension in dupextensions:
        sources = []
        for sfile in extension.sources:
            path, ext = path_splitext(sfile)
            if ext in ('.pyx', '.py'):
                if extension.language == 'c++':
                    ext = '.cpp'
                else:
                    ext = '.c'
                sfile = path + ext
            sources.append(sfile)
        extension.sources[:] = sources
    return dupextensions


def add_ext_cython_modules(_cython_extension_names):
    """ Adds cython modules to the extensions

    example::

        # Cython extension names
        cython_extension_name_sources = {
            'PyLCONF.utilities': ['PyLCONF/cython/utilities.pyx'],
        }

        ext_cython_modules = add_ext_cython_modules(cython_extension_name_sources)
    """
    _ext_cython_modules = []
    for _ext_cython_name, _sources in _cython_extension_names.items():
        ext_cython = setuptools_Extension(
            _ext_cython_name,
            sources=_sources,
            include_dirs=INCLUDE_DIRS,
            library_dirs=LIBRARY_DIRS,
            libraries=DEPENDING_LIB_NAMES,
            extra_compile_args=['-O3', '-ffast-math', '-fopenmp'],
            extra_link_args=['-O3', '-ffast-math', '-fopenmp'],
        )
        _ext_cython_modules.append(ext_cython)
    return _ext_cython_modules


class CleanCommand(setuptools_Command):
    """ Custom distutils command to clean
    """
    description = '''Custom clean: FILES:`.coverage, MANIFEST, *.pyc, *.pyo, *.pyd, *.o, *.orig`
                     and DIRS: `*.__pycache__`'''
    user_options = [
        ('all', None,
        '''remove also: DIRS: `build, dist, cover, *._pyxbld, *.egg-info` and
           FILES in MAIN_PACKAGE_PATH: `*.so, *.c` and cython annotate html'''
        ),
        ('excludefiles', None,
        'remove also any files in: exclude_files'
        ),
    ]

    def initialize_options(self):
        self.all = False
        self.excludefiles = False

    def finalize_options(self):
        pass

    def run(self):
        need_normal_clean = True
        exclude_files = [
           'lconf_classes.c',
           'structure_classes.c',
           'main_code.c',
           'transform.c',
           'utilities.c',
           'validator.c',
           '_version.c',
        ]
        remove_files = []
        remove_dirs = []

        # remove also: DIRS: `build, dist, cover, *._pyxbld, *.egg-info`
        # and FILES in MAIN_PACKAGE_PATH: `*.so, *.c` and cython annotate html
        if self.all:
            need_normal_clean = True
            for dir_ in {'build', 'dist', 'cover'}:
                dir_path = path_join(ROOT_PACKAGE_PATH, dir_)
                if path_exists(dir_path):
                    remove_dirs.append(dir_path)
            for root, dirs_w, files_w in os_walk(ROOT_PACKAGE_PATH):
                for dir_ in dirs_w:
                    if '_pyxbld' in dir_ or 'egg-info' in dir_:
                        remove_dirs.append(path_join(root, dir_))

            # remove FILES in MAIN_PACKAGE_PATH: `*.so, *.c` and cython annotate html
            for root, dirs_w, files_w in os_walk(MAIN_PACKAGE_PATH):
                for file_ in files_w:
                    if file_ not in exclude_files:
                        if path_splitext(file_)[-1] in {'.so', '.c'}:
                            remove_files.append(path_join(root, file_))

                        tmp_name, tmp_ext = path_splitext(file_)
                        if tmp_ext == '.pyx':
                            # Check if we have a html with the same name
                            check_html_path = path_join(root, tmp_name + '.html')
                            if path_isfile(check_html_path):
                                remove_files.append(check_html_path)

        # remove also: all files defined in exclude_files
        if self.excludefiles:
            for root, dirs_w, files_w in os_walk(MAIN_PACKAGE_PATH):
                for file_ in files_w:
                    if file_ in exclude_files:
                        remove_files.append(path_join(root, file_))

        # do the general clean
        if need_normal_clean:
            for file_ in {'.coverage', 'MANIFEST'}:
                if path_exists(file_):
                    remove_files.append(file_)

            for root, dirs_w, files_w in os_walk(ROOT_PACKAGE_PATH):
                for file_ in files_w:
                    if file_ not in exclude_files:
                        if path_splitext(file_)[-1] in {'.pyc', '.pyo', '.pyd', '.o', '.orig'}:
                            remove_files.append(path_join(root, file_))
                for dir_ in dirs_w:
                    if '__pycache__' in dir_:
                        remove_dirs.append(path_join(root, dir_))

        # REMOVE ALL SELECTED
        try:
            for file_ in remove_files:
                if path_exists(file_):
                    os_remove(file_)
            for dir_ in remove_dirs:
                if path_exists(dir_):
                    shutil_rmtree(dir_)
        except Exception:
            pass


class CreateCythonCommand(setuptools_Command):
    """ Cythonize source files: taken from https://github.com/ryanvolz/radarmodel(Copyright (c) 2014, Ryan Volz)"""

    description = 'Compile Cython code to C code'

    user_options = [
        ('timestamps', 't', 'Only compile newer source files.'),
        ('annotate',   'a', 'Show a Cython"s code analysis as html.'),
        ('directive=', 'X', 'Overrides a compiler directive.'),
    ]

    def initialize_options(self):
        self.timestamps = False
        self.annotate = False
        self.directive = ''

    def finalize_options(self):
        self.directive = parse_directive_list(self.directive)

    def run(self):
        cythonize(
            ext_cython_modules,
            include_path=cython_include_path,
            force=(not self.timestamps),
            annotate=self.annotate,
            compiler_directives=self.directive
        )


# =====================================================================================================================
# LIBRARY setup
# =====================================================================================================================

# the underlying C libraries name
DEPENDING_LIB_NAMES = [
    # e.g.: 'calg',
]

SRC_LIBS_CODE_INCLUDE = [
    # path_join(SCRIPT_PATH, 'src_libs')
]

# Put SRC_LIBS_CODE_INCLUDE first
INCLUDE_DIRS = SRC_LIBS_CODE_INCLUDE + [
    '/usr/include',
    '/usr/local/include',
    '/opt/include',
    '/opt/local/include',
]

LIBRARY_DIRS = [
    '/usr/lib',
    '/usr/local/lib',
    '/opt/lib',
    '/opt/local/lib',
]


# Check any required library
if DEPENDING_LIB_NAMES:
    for depending_lib_name in DEPENDING_LIB_NAMES:
        for lib_search_dir in LIBRARY_DIRS:
            try:
                files = os_listdir(lib_search_dir)
                if any(depending_lib_name in file_ for file_ in files):
                    break
            except OSError:
                pass
        else:
            # try find_library
            extra_info = ''
            ctypes_found_libname = ctypes_util_find_library(depending_lib_name)
            if ctypes_found_libname:
                extra_info = 'ctypes.util.find_library` found it: do a manual search and add the correct `LIBRARY_DIRS`'
            sys_exit('ERROR: Cannot find library: <{}>\n\nLIBRARY_DIRS: <{}>\n\n  ctypes_found_libname: <{}>\n    {}'.format(
                depending_lib_name,
                LIBRARY_DIRS,
                ctypes_found_libname,
                extra_info,
            ))


# some linux distros seem to require it: 'm'
DEPENDING_LIB_NAMES.extend(['m'])


# =====================================================================================================================
# extension modules
# =====================================================================================================================
# regular extension modules  !! TODO
ext_modules = []

# cython extension modules  !! TODO
cython_include_path = []  # include for cimport, different from compile include: see: CreateCythonCommand.cythonize
# Cython extension names
cython_extension_name_sources = {
    # 'PyLCONF.constants': ['PyLCONF/cython/constants.pyx'],
    # 'PyLCONF.lconf_classes': ['PyLCONF/cython/lconf_classes.pyx'],
    # 'PyLCONF.structure_classes': ['PyLCONF/cython/structure_classes.pyx'],
    # 'PyLCONF.main_code': ['PyLCONF/cython/main_code.pyx'],
    # 'PyLCONF.utilities': ['PyLCONF/cython/utilities.pyx'],
    # 'PyLCONF.validator': ['PyLCONF/cython/validator.pyx'],
    # 'PyLCONF.schema_validator': ['PyLCONF/cython/schema_validator.pyx'],
    # 'PyLCONF.lconf_section': ['PyLCONF/cython/lconf_section.pyx'],
    # 'PyLCONF.lconf_schema': ['PyLCONF/cython/lconf_schema.pyx'],
}

ext_cython_modules = add_ext_cython_modules(cython_extension_name_sources)


# =====================================================================================================================
# Do the rest of the configuration
# =====================================================================================================================

# add C-files from cython modules to extension modules
ext_modules.extend(no_cythonize(ext_cython_modules))

cmdclass = {
    # 'build': CmdBuild,
    # 'sdist': CmdSdist,
    }
cmdclass.update({
    'clean': CleanCommand,
    'cython': CreateCythonCommand,
})


# =====================================================================================================================
# setuptools_setup
# =====================================================================================================================
setuptools_setup(
    name='PyLCONF',
    version=VERSION,
    author='peter1000',
    author_email='https://github.com/peter1000',
    url='http://lconf-data-serialization-format.github.io/PyLCONF/',
    license='MIT (Expat)',
    packages=setuptools_find_packages(),
    include_package_data=True,
    install_requires=read_requires('requirements.txt'),
    use_2to3=False,
    zip_safe=False,
    platforms=['Linux'],
    cmdclass=cmdclass,
    ext_modules=ext_modules,
    description="A LCONF parser and emitter for Python.",
    long_description=open('README.md', 'r').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Topic :: Text Processing :: Markup',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keywords='python markup configuration json yaml LCONF LCONF-Data-Serialization-Format serialization',
    scripts=[
        'bin/pylconf-validate',
        'bin/pylconfsd-validate',
    ],
)
