This file is a merged representation of a subset of the codebase, containing specifically included
files, combined into a single document by Repomix. The content has been processed where security
check has been disabled.

# File Summary

## Purpose

This file contains a packed representation of the entire repository's contents. It is designed to be
easily consumable by AI systems for analysis, code review, or other automated processes.

## File Format

The content is organized as follows:

1. This summary section
2. Repository information
3. Directory structure
4. Multiple file entries, each consisting of: a. A header with the file path (## File: path/to/file)
   b. The full contents of the file in a code block

## Usage Guidelines

- This file should be treated as read-only. Any changes should be made to the original repository
  files, not this packed version.
- When processing this file, use the file path to distinguish between different files in the
  repository.
- Be aware that this file may contain sensitive information. Handle it with the same level of
  security as you would the original repository.

## Notes

- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository
  Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: \*\*/\*.rst
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Security check has been disabled - content may contain sensitive information

## Additional Info

# Directory Structure

```
examples/
  README.rst
src/
  doc/
    _templates/
      module.rst
    misc/
      api.rst
      changelog.rst
      install.rst
      readme.rst
      usage.rst
    index.rst
INSTALL.rst
README.rst
USAGE.rst
```

# Files

## File: examples/README.rst

```
Examples
========

These example files show some typical (and not so typical) ways to use the Python exiv2 interface.
Some of them are based on the `C++ examples`_ provided by the Exiv2 project.
It might be instructive to compare the C++ and Python ways of doing the same thing.

.. _C++ examples:      https://www.exiv2.org/doc/examples.html
```

## File: src/doc/\_templates/module.rst

```
{% if fullname == "exiv2._version" %}
    {% set attributes = ['__version__', '__version_tuple__'] %}
{% endif %}

{% extends "!autosummary/module.rst" %}

   {% block classes %}
   {% if classes %}
   .. rubric:: {{ _('Classes') }}

   {% if fullname == "exiv2._value" %}
   .. inheritance-diagram:: {{ classes |
                               reject("in", ["Date", "Time"]) |
                               join(" ") }}
       :top-classes: exiv2.value.Value
   {% endif %}

   {% if fullname in ["exiv2._datasets", "exiv2._metadatum", "exiv2._properties", "exiv2._tags"] %}
   .. inheritance-diagram:: exiv2.ExifKey exiv2.IptcKey exiv2.XmpKey
       :top-classes: exiv2.metadatum.Key
   {% endif %}

   {% if fullname in ["exiv2._exif", "exiv2._iptc", "exiv2._metadatum", "exiv2._xmp"] %}
   .. inheritance-diagram:: exiv2.Exifdatum exiv2.Iptcdatum exiv2.Xmpdatum
       :top-classes: exiv2.metadatum.Metadatum
   {% endif %}

   .. autosummary::
   {% for item in classes %}
      {{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}
```

## File: src/doc/misc/api.rst

```
.. This is part of the python-exiv2 documentation.
   Copyright (C)  2024  Jim Easterbrook.

Detailed API
============

This part of the documentation is auto-generated from the Doxygen_ format documentation in the libexiv2 "header" files.
There are many ways in which the conversion process can fail, so you may need to consult the `Exiv2 C++ API`_ documentation as well.

The documentation is split into several pages, one for each module in the Python interface.
This makes it easier to use than having all the classes and functions in one document.
Do not use the module names in your Python scripts: always use ``exiv2.name`` rather than ``exiv2.module.name`` or ``exiv2._module.name``.

See :ref:`genindex` for a full index to all classes, attributes, functions and methods.

.. autosummary::
   :toctree: ../api
   :recursive:
   :template: module.rst

   exiv2._image
   exiv2._exif
   exiv2._iptc
   exiv2._xmp
   exiv2._preview
   exiv2._value
   exiv2._types
   exiv2._tags
   exiv2._datasets
   exiv2._properties
   exiv2._version
   exiv2._error
   exiv2._easyaccess
   exiv2._basicio
   exiv2._metadatum

.. _Doxygen: https://www.doxygen.nl/
.. _Exiv2 C++ API: https://exiv2.org/doc/index.html
```

## File: src/doc/misc/changelog.rst

```
.. This is part of the python-exiv2 documentation.
   Copyright (C)  2024  Jim Easterbrook.

Release history
===============

.. literalinclude:: ../../../CHANGELOG.txt
   :language: none
   :start-after: licenses/>
   :end-before: Changes in v0.4.0
```

## File: src/doc/misc/install.rst

```
.. This is part of the python-exiv2 documentation.
   Copyright (C)  2024  Jim Easterbrook.

.. include:: ../../../INSTALL.rst
   :end-before: .. _README

.. _README.rst:   readme.html
```

## File: src/doc/misc/readme.rst

```
.. This is part of the python-exiv2 documentation.
   Copyright (C)  2024  Jim Easterbrook.

Project overview
================

.. include:: ../../../README.rst
   :start-line: 2
   :end-before: .. _INSTALL

.. _INSTALL.rst: install.html
.. _USAGE.rst:   usage.html
```

## File: src/doc/misc/usage.rst

```
.. This is part of the python-exiv2 documentation.
   Copyright (C)  2024  Jim Easterbrook.

.. include:: ../../../USAGE.rst
```

## File: src/doc/index.rst

```
.. This is part of the python-exiv2 documentation.
   Copyright (C)  2024  Jim Easterbrook.

Python-exiv2 documentation
==========================


.. toctree::
   :maxdepth: 2

   misc/readme
   misc/install
   misc/usage
   misc/changelog
   misc/api
```

## File: INSTALL.rst

```
Installation
============

As mentioned in `README.rst`_, on most computers `python-exiv2`_ can be installed with a simple pip_ command::

    C:\>pip install exiv2
    Collecting exiv2
      Downloading exiv2-0.17.0-cp38-cp38-win_amd64.whl.metadata (7.3 kB)
    Downloading exiv2-0.17.0-cp38-cp38-win_amd64.whl (8.5 MB)
       ---------------------------------------- 8.5/8.5 MB 963.3 kB/s eta 0:00:00
    Installing collected packages: exiv2
    Successfully installed exiv2-0.17.0

If this doesn't work, or you need a non-standard installation, there are other ways to install `python-exiv2`_.

.. contents::
    :backlinks: top

Use installed libexiv2
----------------------

In the example above, pip_ installs a "binary wheel_".
This is pre-compiled and includes a copy of the libexiv2_ library, which makes installation quick and easy.
Wheels for `python-exiv2`_ are available for Windows, Linux, and MacOS with Python versions from 3.6 to 3.12.

If your computer already has libexiv2_ installed (typically by your operating system's "package manager") then pip_ might be able to compile `python-exiv2`_ to use it.
First you need to check what version of python-exiv2 you have::

    $ pkg-config --modversion exiv2
    0.27.5

If this command fails it might be because you don't have the "development headers" of libexiv2_ installed.
On some operating systems these are a separate package, with a name like ``exiv2-dev``.

If the ``pkg-config`` command worked, and your version of libexiv2 is 0.27.0 or later, then you should be able to install `python-exiv2`_ from source::

    $ pip3 install --user exiv2 --no-binary :all:
    Collecting exiv2
      Downloading exiv2-0.17.0.tar.gz (1.6 MB)
         ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.6/1.6 MB 870.6 kB/s eta 0:00:00
      Installing build dependencies ... done
      Getting requirements to build wheel ... done
      Installing backend dependencies ... done
      Preparing metadata (pyproject.toml) ... done
    Building wheels for collected packages: exiv2
      Building wheel for exiv2 (pyproject.toml) ... done
      Created wheel for exiv2: filename=exiv2-0.17.0-cp310-cp310-linux_x86_64.whl size=4586091 sha256=09d7f0d2a3654c1cf4bb944ed04d594a92e6f6eaa8a1a0acd5fa45cdf8746ffd
      Stored in directory: /home/jim/.cache/pip/wheels/e5/18/69/fc2199ac2c24b13e88a56c4660720fea109d69b0747e05eb1d
    Successfully built exiv2
    Installing collected packages: exiv2
    Successfully installed exiv2-0.17.0

This will take some time as python-exiv2 has to be compiled, and some of its modules are quite large.
If you want to see what's happening you can use the ``-v`` option to increase pip_'s verbosity.

If you change your installed libexiv2_, for example as part of an operating system update, then your installation of python-exiv2 will probably stop working.
If this happens you need to reinstall python-exiv2 to use the new version of libexiv2::

    $ pip3 install --user exiv2 --no-binary :all: --force-reinstall

Note the use of ``--force-reinstall`` to make pip reinstall python-exiv2 even if the latest version is already installed.

Download python-exiv2 source
----------------------------

The following installation procedures all require access to the `python-exiv2`_ source code.
You can download this from GitHub_ (use the most recent release) or, if you are familiar with git_, you could "clone" the GitHub repo.
The rest of this document assumes you have the source code and are in your ``python-exiv2`` directory.

You may also need to install the wheel package used to build Python wheels::

    $ pip3 install --user wheel

Use pre-built libexiv2
----------------------

The Exiv2 project provides builds_ for several operating systems.
Download and unpack the appropriate one for your operating system, then you can compile `python-exiv2`_ to use this source.
Note the use of the ``EXIV2_ROOT`` environment variable to select the source::

    $ EXIV2_ROOT=../exiv2-0.28.3-Linux64/ pip3 wheel .
    Processing /home/jim/python-exiv2
      Installing build dependencies ... done
      Getting requirements to build wheel ... done
      Installing backend dependencies ... done
      Preparing metadata (pyproject.toml) ... done
    Building wheels for collected packages: exiv2
      Building wheel for exiv2 (pyproject.toml) ... done
      Created wheel for exiv2: filename=exiv2-0.17.0-cp310-cp310-linux_x86_64.whl size=11839757 sha256=a7de01eadbf9bf608ff07cda506db1453fcb91c9b55cc9d5cbc93546ee6c52c7
      Stored in directory: /home/jim/.cache/pip/wheels/b6/c0/a3/68cf7238e1b7de98ca8bbce0f5f3f0bf6b85f9b6468a097cca
    Successfully built exiv2

As before, you can use pip_'s ``-v`` option to see what's happening as it compiles each python-exiv2 module.

If this worked you can now install the wheel_ you've just built::

    $ pip3 install --user exiv2-0.17.0-cp310-cp310-linux_x86_64.whl
    Processing ./exiv2-0.17.0-cp310-cp310-linux_x86_64.whl
    Installing collected packages: exiv2
    Successfully installed exiv2-0.17.0

Windows
^^^^^^^

The above instructions apply to Unix-like systems such as Linux, MacOS, and MinGW.
However, it is also possible to build `python-exiv2`_ on Windows.
There is a lot of confusing and contradictory information available about building Python extensions on Windows.
The following is what has worked for me.

First you need to install a compiler.
Python versions 3.5 onwards need Visual C++ 14.x.
Fortunately Microsoft provides a free `Visual C++ 14.2 standalone`_.
Download and install this first.

Build a wheel::

    C:\Users\Jim\python-exiv2>set EXIV2_ROOT=..\exiv2-0.28.3-2019msvc64

    C:\Users\Jim\python-exiv2>pip wheel .
    Processing c:\users\jim\python-exiv2
      Installing build dependencies ... done
      Getting requirements to build wheel ... done
      Preparing metadata (pyproject.toml) ... done
    Building wheels for collected packages: exiv2
      Building wheel for exiv2 (pyproject.toml) ... done
      Created wheel for exiv2: filename=exiv2-0.17.0-cp38-cp38-win_amd64.whl size=8448722 sha256=0408f9c99a1ca772dc62ec6689dc6ce8dd8d7027d7cb8808a91e8312590c498d
      Stored in directory: c:\users\jim\appdata\local\pip\cache\wheels\a3\3b\d4\d35463afd5940a14f17983a106ed52ffafc07877192bcc881a
    Successfully built exiv2

Install the wheel::

    C:\Users\Jim\python-exiv2>pip install exiv2-0.17.0-cp38-cp38-win_amd64.whl
    Processing c:\users\jim\python-exiv2\exiv2-0.17.0-cp38-cp38-win_amd64.whl
    Installing collected packages: exiv2
    Successfully installed exiv2-0.17.0

Build your own libexiv2
-----------------------

In some circumstances a pre-built libexiv2_ supplied by the exiv2 project may not be suitable.
For example, the Linux build might use newer libraries than are installed on your computer.

Building libexiv2 requires CMake_.
This should be available from your operating system's package manager.
If not (e.g. on Windows) then download an installer from the CMake web site.
You will also need to install the "development headers" of zlib_ and expat_.
Exiv2 provides some `build instructions`_, but I don't follow them exactly.

Download and unpack the exiv2 source, then change to its directory.
Then configure the build::

    $ cmake --preset linux-release -D CONAN_AUTO_INSTALL=OFF \
    > -D EXIV2_BUILD_SAMPLES=OFF -D EXIV2_BUILD_UNIT_TESTS=OFF \
    > -D EXIV2_BUILD_EXIV2_COMMAND=OFF -D EXIV2_ENABLE_NLS=ON

(The cmake options enable localisation and turn off building bits we don't need.)

If this worked you can now compile and install (to the local folder) libexiv2::

    $ cmake --build build-linux-release --config Release
    $ cmake --install build-linux-release --config Release

Back in your python-exiv2 directory, you can build the wheel as before, but using your new build::

    $ EXIV2_ROOT=../exiv2-0.28.3/build-linux-release/install pip3 wheel .
    Processing /home/jim/python-exiv2
      Installing build dependencies ... done
      Getting requirements to build wheel ... done
      Installing backend dependencies ... done
      Preparing metadata (pyproject.toml) ... done
    Building wheels for collected packages: exiv2
      Building wheel for exiv2 (pyproject.toml) ... done
      Created wheel for exiv2: filename=exiv2-0.17.0-cp310-cp310-linux_x86_64.whl size=11979058 sha256=85cf8d78bd8d6b82de6aae6fd8bb58ffb76a381cc921bc1bd77fbfb77e46e2dc
      Stored in directory: /home/jim/.cache/pip/wheels/b6/c0/a3/68cf7238e1b7de98ca8bbce0f5f3f0bf6b85f9b6468a097cca
    Successfully built exiv2

Then install the wheel as before.

Windows
^^^^^^^

Once again, doing this on Windows is just a bit more complicated.

The dependencies zlib_, expat_, and libiconv_ are installed with conan_.
First install conan with pip_::

    C:\Users\Jim\exiv2-0.28.3>pip install conan==1.59.0

Then configure CMake::

    C:\Users\Jim\exiv2-0.28.3>cmake --preset msvc -D CMAKE_BUILD_TYPE=Release ^
    More? -D EXIV2_BUILD_SAMPLES=OFF -D EXIV2_BUILD_EXIV2_COMMAND=OFF ^
    More? -D EXIV2_BUILD_UNIT_TESTS=OFF -G "Visual Studio 16 2019"

(The ``^`` characters are used to split this very long command.)

If that worked you can compile and install libexiv2::

    C:\Users\Jim\exiv2-0.28.3>cmake --build build-msvc --config Release

    C:\Users\Jim\exiv2-0.28.3>cmake --install build-msvc --config Release

Back in your python-exiv2 directory, build a wheel using your newly compiled libexiv2::

    C:\Users\Jim\python-exiv2>set EXIV2_ROOT=..\exiv2-0.28.3\build-msvc\install

    C:\Users\Jim\python-exiv2>pip wheel .
    Processing c:\users\jim\python-exiv2
      Installing build dependencies ... done
      Getting requirements to build wheel ... done
      Preparing metadata (pyproject.toml) ... done
    Building wheels for collected packages: exiv2
      Building wheel for exiv2 (pyproject.toml) ... done
      Created wheel for exiv2: filename=exiv2-0.17.0-cp38-cp38-win_amd64.whl size=8428068 sha256=c9c1364c0aaddb1455b2272cbd9ee64bc22d290f13eb7dc289b2ee67dcda87f3
      Stored in directory: c:\users\jim\appdata\local\pip\cache\wheels\a3\3b\d4\d35463afd5940a14f17983a106ed52ffafc07877192bcc881a
    Successfully built exiv2

Then install the wheel as before.

Running SWIG
------------

You should only need to run SWIG_ if your installed libexiv2 has extras, such as Windows Unicode paths, that aren't available with the SWIG generated files included with python-exiv2.
Note that SWIG version 4.1.0 or later is required to process the highly complex libexiv2 header files.

The ``build_swig.py`` script has one required parameter - the path of the exiv2 include directory.
If you've downloaded or build exiv2 you can run ``build_swig.py`` on the local copy::

    $ python3 utils/build_swig.py ../exiv2-0.28.3/build-linux-release/install/include/

Or you can run it on the system installed libexiv2::

    $ python3 utils/build_swig.py /usr/include

After running ``build_swig.py`` you can build and install a wheel as before::

    $ EXIV2_ROOT=../exiv2-0.28.3/build-linux-release/install pip3 wheel .
    $ pip3 install --user exiv2-0.17.0-cp310-cp310-linux_x86_64.whl

.. _build instructions:
    https://github.com/exiv2/exiv2#2
.. _builds:       https://www.exiv2.org/download.html
.. _CMake:        https://cmake.org/
.. _conan:        https://conan.io/
.. _expat:        https://libexpat.github.io/
.. _git:          https://git-scm.com/
.. _GitHub:       https://github.com/jim-easterbrook/python-exiv2/releases
.. _libexiv2:     https://www.exiv2.org/getting-started.html
.. _libiconv:     https://www.gnu.org/software/libiconv/
.. _pip:          https://pip.pypa.io/
.. _python-exiv2: https://github.com/jim-easterbrook/python-exiv2
.. _SWIG:         http://www.swig.org/
.. _Visual C++ 14.2 standalone:
    https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2019
.. _wheel:        https://www.python.org/dev/peps/pep-0427/
.. _zlib:         https://zlib.net/
.. _README.rst:   README.rst
```

## File: README.rst

```
python-exiv2 v\ 0.17.3
======================

python-exiv2 is a low level interface (or binding) to the exiv2_ C++ library.
It is built using SWIG_ to automatically generate the interface code.
The intention is to give direct access to all of the top-level classes in libexiv2_, but with additional "Pythonic" helpers where necessary.
Not everything in libexiv2 is available in the Python interface.
If you need something that's not there, please let me know.

.. note::
    This project has taken over the PyPI exiv2 package created by Michael Vanslembrouck.
    If you need to use Michael's project, it is available at https://bitbucket.org/zmic/exiv2-python/src/master/ and can be installed with pip_::

        pip install exiv2==0.3.1

.. contents::
    :backlinks: top

Introduction
------------

There are several other ways to access libexiv2_ from within Python.
The first one I used was `pyexiv2 (old)`_.
After its development ceased I moved on to using gexiv2_ and PyGObject_.
This works well, providing a ``Metadata`` object with high level functions such as ``set_tag_string`` and ``set_tag_multiple`` to get and set metadata values.

A more recent development is `pyexiv2 (new)`_.
This new project is potentially very useful, providing a simple interface with functions to read and modify metadata using Python ``dict`` parameters.

For more complicated metadata operations I think a lower level interface is required, which is where this project comes in.
Here is an example of its use:

.. code:: python

    Python 3.6.12 (default, Dec 02 2020, 09:44:23) [GCC] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import exiv2
    >>> image = exiv2.ImageFactory.open('IMG_0211.JPG')
    >>> image.readMetadata()
    >>> data = image.exifData()
    >>> data['Exif.Image.Artist'].print()
    'Jim Easterbrook'
    >>>

Please see `USAGE.rst`_ for more help with using the Python interface to libexiv2.

Transition to libexiv2 v0.28.x
------------------------------

Before python-exiv2 v0.16 the "binary wheels" available from PyPI_ incorporated libexiv2 v0.27.7 or earlier.
Binary wheels for python-exiv2 v0.16.3 incorporate libexiv2 v0.28.2, and those for python-exiv2 v0.16.2 incorporate libexiv2 v0.27.7.
Binary wheels for python-exiv2 v0.17.0 incorporate libexiv2 v0.28.3.
If your software is currently incompatible with libexiv2 v0.28.x you can use the older version of libexiv2 by explicitly installing python-exiv2 v0.16.2::

    $ pip install --user exiv2==0.16.2

There are some changes in the libexiv2 API between v0.27.7 and v0.28.x.
Future versions of python-exiv2 will all incorporate libexiv2 v0.28.x, so please update your software to use the changed API.

Documentation
-------------

The libexiv2_ library is well documented for C++ users, in Doxygen_ format.
Recent versions of SWIG_ can convert this documentation to pydoc_ format in the Python interface::

    $ pydoc3 exiv2.Image.readMetadata
    Help on method_descriptor in exiv2.Image:

    exiv2.Image.readMetadata = readMetadata(...)
        Read all metadata supported by a specific image format from the
            image. Before this method is called, the image metadata will be
            cleared.

        This method returns success even if no metadata is found in the
        image. Callers must therefore check the size of individual metadata
        types before accessing the data.

        :raises: Error if opening or reading of the file fails or the image
                data is not valid (does not look like data of the specific image
                type).

This is then converted to web pages by Sphinx_ and hosted on ReadTheDocs_.

Unfortunately some documentation gets lost in the manipulations needed to make a useful interface.
The C++ documentation is still needed in these cases.

Support for bmff files (e.g. CR3, HEIF, HEIC, AVIF, JPEG XL)
------------------------------------------------------------

Python-exiv2 from version 0.17.0 has support for BMFF files enabled by default if libexiv2 was compiled with support for BMFF files enabled.
In earlier versions you need to call the ``enableBMFF`` function before using BMFF files in your program.
Use of BMFF files may infringe patents.
Please read the Exiv2 `statement on BMFF`_ patents before doing so.

Installation
------------

Python "binary wheels" are available for Windows, Linux, and MacOS.
These include the libexiv2 library and should not need any other software to be installed.
They can be installed with Python's pip_ package.
For example, on Windows::

    C:\Users\Jim>pip install exiv2

or on Linux or MacOS::

    $ pip3 install --user exiv2

If the available wheels are not compatible with your operating system or Python version then pip will download the python-exiv2 source and attempt to compile it.
For more information, and details of how to compile python-exiv2 and libexiv2, see `INSTALL.rst`_.

Problems?
---------

Please email jim@jim-easterbrook.me.uk if you find any problems (or solutions!).

.. _Doxygen:           https://www.doxygen.nl/
.. _exiv2:             https://www.exiv2.org/getting-started.html
.. _gexiv2:            https://wiki.gnome.org/Projects/gexiv2
.. _GitHub:            https://github.com/jim-easterbrook/python-exiv2
.. _libexiv2:          https://www.exiv2.org/doc/index.html
.. _pip:               https://pip.pypa.io/
.. _pyexiv2 (new):     https://github.com/LeoHsiao1/pyexiv2
.. _pyexiv2 (old):     https://launchpad.net/pyexiv2
.. _PyGObject:         https://pygobject.readthedocs.io/en/latest/
.. _PyPI:              https://pypi.org/project/exiv2/
.. _SWIG:              http://swig.org/
.. _pydoc:             https://docs.python.org/3/library/pydoc.html
.. _Python3:           https://www.python.org/
.. _ReadTheDocs:       https://python-exiv2.readthedocs.io/
.. _Sphinx:            https://www.sphinx-doc.org/
.. _statement on BMFF: https://github.com/exiv2/exiv2#BMFF
.. _Visual C++:        https://wiki.python.org/moin/WindowsCompilers
.. _INSTALL.rst:       INSTALL.rst
.. _USAGE.rst:         USAGE.rst
```

## File: USAGE.rst

```
Hints and tips
==============

Here are some ideas on how to use python-exiv2.
In many cases there's more than one way to do it, but some ways are more "Pythonic" than others.
Some of this is only applicable to python-exiv2 v0.16.0 onwards.
You can find out what version of python-exiv2 you have with either ``pip3 show exiv2`` or ``python3 -m exiv2``.

.. contents::
    :backlinks: top

libexiv2 library version
------------------------

Python-exiv2 can be used with any version of libexiv2 from 0.27.0 onwards.
The "binary wheels" available from PyPI_ currently include a copy of libexiv2 v0.27.7, but if you install from source then python-exiv2 will use whichever version of libexiv2 is installed on your computer.

There are some differences in the API of libexiv2 v0.28.x and v0.27.y.
Some of these have been "backported" in the Python interface so you can start using the v0.28 methods, e.g. the ``exiv2.DataBuf.data()`` function replaces the ``exiv2.DataBuf.pData_`` attribute.

If you need to write software that works with both versions of libexiv2 then the ``exiv2.testVersion`` function can be used to test for version 0.28.0 onwards:

.. code:: python

    if exiv2.testVersion(0, 28, 0):
        int_val = datum.toInt64(0)
    else:
        int_val = datum.toLong(0)

Error handling
--------------

libexiv2_ has a multilevel warning system a bit like Python's standard logger.
The Python interface redirects all Exiv2 messages to Python logging with an appropriate log level.
The ``exiv2.LogMsg.setLevel()`` method can be used to control what severity of messages are logged.

Since python-exiv2 v0.16.2 the ``exiv2.LogMsg.setHandler()`` method can be used to set the handler.
The Python logging handler is ``exiv2.LogMsg.pythonHandler`` and the Exiv2 default handler is ``exiv2.LogMsg.defaultHandler``.

NULL values
-----------

Some libexiv2_ functions that expect a pointer to an object or data can have ``NULL`` (sometimes documented as ``0``) passed to them to represent "no value".
In Python ``None`` is used instead.

Deprecation warnings
--------------------

As python-exiv2 is being developed better ways are being found to do some things.
Some parts of the interface are deprecated and will eventually be removed.
Please use Python's ``-Wd`` flag when testing your software to ensure it isn't using deprecated features.
(Do let me know if I've deprecated a feature you need and can't replace with an alternative.)

Enums
-----

The C++ libexiv2 library often uses ``enum`` classes to list related data, such as the value type identifiers stored in `Exiv2::TypeId`_.
SWIG's default processing of such enums is to add all the values as named constants to the top level of the module, e.g. ``exiv2.asciiString``.
In python-exiv2 most of the C++ enums are represented by Python enum_ classes, e.g. ``exiv2.TypeId.asciiString`` is a member of ``exiv2.TypeId``.

Unfortunately there is no easy way to deprecate the SWIG generated top level constants, but they will eventually be removed from python-exiv2.
Please ensure you only use the enum classes in your use of python-exiv2.

Data structures
---------------

Some parts of the Exiv2 API use structures to hold several related data items.
For example, the `Exiv2::ExifTags`_ class has a ``tagList()`` method that returns a list of `Exiv2::TagInfo`_ structs.
In python-exiv2 (since v0.16.2) these structs have dict_ like behaviour, so the members can be accessed more easily:

.. code:: python

    >>> import exiv2
    >>> info = exiv2.ExifTags.tagList('Image')[0]
    >>> print(info.title_)
    Processing Software
    >>> print(info['title'])
    Processing Software
    >>> print(info.keys())
    ['tag', 'title', 'sectionId', 'desc', 'typeId', 'ifdId', 'count', 'name']
    >>> from pprint import pprint
    >>> pprint(dict(info))
    {'count': 0,
     'desc': 'The name and version of the software used to post-process the '
             'picture.',
     'ifdId': <IfdId.ifd0Id: 1>,
     'name': 'ProcessingSoftware',
     'sectionId': <SectionId.otherTags: 4>,
     'tag': 11,
     'title': 'Processing Software',
     'typeId': <TypeId.asciiString: 2>}

Note that struct member names ending with an underscore have the underscore removed in the dict_ like interface.

Reading data values
-------------------

Exiv2 stores metadata as (key, value) pairs in `Exiv2::Metadatum`_ objects.
The datum has two methods to retrieve the value: ``value()`` and ``getValue()``.
The first gets a reference to the value and the second makes a copy.
Use ``value()`` when you don't need to modify the data.
``getValue()`` copies the data to a new object that you can modify.

In the C++ API these methods both return (a pointer to) an `Exiv2::Value`_ base class object.
The Python interface uses the value's ``typeId()`` method to determine its type and casts the return value to the appropriate derived type.

Recasting data values
^^^^^^^^^^^^^^^^^^^^^

In earlier versions of python-gphoto2 you could set the type of value returned by ``value()`` or ``getValue()`` by passing an ``exiv2.TypeId`` parameter:

.. code:: python

    datum = exifData['Exif.Photo.UserComment']
    value = datum.value(exiv2.TypeId.comment)
    result = value.comment()

Since version 0.16.0 the returned value is always of the correct type and this parameter is ignored.

Writing data values
-------------------

The simplest way to set metadata is by assigning a value to the metadatum:

.. code:: python

    exifData['Exif.Image.ImageDescription'] = 'Uncle Fred at the seaside'
    iptcData['Iptc.Application2.Caption'] = 'Uncle Fred at the seaside'
    xmpData['Xmp.dc.description'] = 'Uncle Fred at the seaside'

The datum is created if it doesn't already exist and its value is set to the text.

Setting the type
^^^^^^^^^^^^^^^^

Metadata values have a type, for example Exif values can be ``Ascii``, ``Short``, ``Rational`` etc.
When a datum is created its type is set to the default for the key, so ``exifData['Exif.Image.ImageDescription']`` is set to ``Ascii``.
If a datum already exists, its current type is not changed by assigning a string value.

If you need to force the type of a datum (e.g. because it currently has the wrong type) you can create a value of the correct type and assign it:

.. code:: python

    exifData['Exif.Image.ImageDescription'] = exiv2.AsciiValue('Uncle Fred at the seaside')

Numerical data
^^^^^^^^^^^^^^

Setting string values as above is OK for text data such as Exif's Ascii or XMP's XmpText, but less suitable for numeric data such as GPS coordinates.
These can be set from a string, but it is better to use numeric data:

.. code:: python

    exifData['Exif.GPSInfo.GPSLatitude'] = '51/1 30/1 4910/1000'
    exifData['Exif.GPSInfo.GPSLatitude'] = ((51, 1), (30, 1), (4910, 1000))

In the first line the exiv2 library converts the string ``'51/1 30/1 4910/1000'`` to three (numerator, denominator) pairs.
In the second line the three pairs are supplied as integer numbers and no conversion is needed.
This is potentially quicker and more accurate.
(The Python Fraction_ type is very useful for dealing with rational numbers like these.)

Structured data
^^^^^^^^^^^^^^^

Some XMP data is more complicated to deal with.
For example, the locations shown in a photograph can be stored as a group of structures, each containing location/city/country information.
Exiv2 gives these complex tag names like ``Xmp.iptcExt.LocationShown[1]/Iptc4xmpExt:City``.

Data like this is written in several stages.
First create the array ``Xmp.iptcExt.LocationShown``:

.. code:: python

    tmp = exiv2.XmpTextValue()
    tmp.setXmpArrayType(exiv2.XmpValue.XmpArrayType.xaBag)
    xmpData['Xmp.iptcExt.LocationShown'] = tmp

Then create a structured data container for the first element in the array:

.. code:: python

    tmp = exiv2.XmpTextValue()
    tmp.setXmpStruct()
    xmpData['Xmp.iptcExt.LocationShown[1]'] = tmp

Then write individual items in the structure:

.. code:: python

    xmpData['Xmp.iptcExt.LocationShown[1]/Iptc4xmpExt:City'] = 'London'
    xmpData['Xmp.iptcExt.LocationShown[1]/Iptc4xmpExt:Sublocation'] = 'Buckingham Palace'

This can potentially be nested to any depth.

Exiv2::ValueType< T >
---------------------

Exiv2 uses a template class `Exiv2::ValueType< T >`_ to store Exif numerical values such as the unsigned rationals used for GPS coordinates.
This class stores the actual data in a ``std::vector`` attribute ``value_``.
In the Python interface this attribute is hidden and the data is accessed by indexing:

.. code:: python

    datum = exifData['Exif.GPSInfo.GPSLatitude']
    value = datum.getValue()
    print(value[0])
    value[0] = (47, 1)

Python read access to the data can be simplified by using it to initialise a list or tuple:

.. code:: python

    datum = exifData['Exif.GPSInfo.GPSLatitude']
    value = list(datum.value())

You can also construct new values from a Python list or tuple:

.. code:: python

    value = exiv2.URationalValue([(47, 1), (49, 1), (31822, 1000)])
    exifData['Exif.GPSInfo.GPSLatitude'] = value

String values
^^^^^^^^^^^^^

If you don't want to use the data numerically then you can just use strings for everything:

.. code:: python

    datum = exifData['Exif.GPSInfo.GPSLatitude']
    value = str(datum.value())
    exifData['Exif.GPSInfo.GPSLatitude'] = '47/1 49/1 31822/1000'

Iterators
---------

The ``Exiv2::ExifData``, ``Exiv2::IptcData``, and ``Exiv2::XmpData`` classes use C++ iterators to expose private data, for example the ``ExifData`` class has a private member of ``std::list<Exifdatum>`` type.
The classes have public ``begin()``, ``end()``, and ``findKey()`` methods that return ``std::list`` iterators.
In C++ you can dereference one of these iterators to access the ``Exifdatum`` object, but Python doesn't have a dereference operator.

This Python interface converts the ``std::list`` iterator to a Python object that has access to all the ``Exifdatum`` object's methods without dereferencing.
For example:

.. code:: python

    Python 3.6.12 (default, Dec 02 2020, 09:44:23) [GCC] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import exiv2
    >>> image = exiv2.ImageFactory.open('IMG_0211.JPG')
    >>> image.readMetadata()
    >>> data = image.exifData()
    >>> b = data.begin()
    >>> b.key()
    'Exif.Image.ProcessingSoftware'
    >>>

Before using an iterator you must ensure that it is not equal to the ``end()`` value.

You can iterate over the data in a very C++ like style:

.. code:: python

    >>> data = image.exifData()
    >>> b = data.begin()
    >>> e = data.end()
    >>> while b != e:
    ...     b.key()
    ...     next(b)
    ...
    'Exif.Image.ProcessingSoftware'
    <Swig Object of type 'Exiv2::Exifdatum *' at 0x7fd6053f9030>
    'Exif.Image.ImageDescription'
    <Swig Object of type 'Exiv2::Exifdatum *' at 0x7fd6053f9030>
    [skip 227 line pairs]
    'Exif.Thumbnail.JPEGInterchangeFormat'
    <Swig Object of type 'Exiv2::Exifdatum *' at 0x7fd6053f9030>
    'Exif.Thumbnail.JPEGInterchangeFormatLength'
    <Swig Object of type 'Exiv2::Exifdatum *' at 0x7fd6053f9030>
    >>>

The ``<Swig Object of type 'Exiv2::Exifdatum *' at 0x7fd6053f9030>`` lines are the Python interpreter showing the return value of ``next(b)``.
You can also iterate in a more Pythonic style:

.. code:: python

    >>> data = image.exifData()
    >>> for datum in data:
    ...     datum.key()
    ...
    'Exif.Image.ProcessingSoftware'
    'Exif.Image.ImageDescription'
    [skip 227 lines]
    'Exif.Thumbnail.JPEGInterchangeFormat'
    'Exif.Thumbnail.JPEGInterchangeFormatLength'
    >>>

The data container classes are like a cross between a Python list_ of ``Metadatum`` objects and a Python dict_ of ``(key, Value)`` pairs.
(One way in which they are not like a dict_ is that you can have more than one member with the same key.)
This allows them to be used in a very Pythonic style:

.. code:: python

    data = image.exifData()
    print(data['Exif.Image.ImageDescription'].toString())
    if 'Exif.Image.ProcessingSoftware' in data:
        del data['Exif.Image.ProcessingSoftware']
    data = image.iptcData()
    while 'Iptc.Application2.Keywords' in data:
        del data['Iptc.Application2.Keywords']

Warning: segmentation faults
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If an iterator is invalidated, e.g. by deleting the datum it points to, then your Python program may crash with a segmentation fault if you try to use the invalid iterator.
Just as in C++, there is no way to detect that an iterator has become invalid.

Segmentation faults
-------------------

There are many places in the libexiv2 C++ API where objects hold references to data in other objects.
This is more efficient than copying the data, but can cause segmentation faults if an object is deleted while another objects refers to its data.

The Python interface tries to protect the user from this but in some cases this is not possible.
For example, an `Exiv2::Metadatum`_ object holds a reference to data that can easily be invalidated:

.. code:: python

    exifData = image.exifData()
    datum = exifData['Exif.GPSInfo.GPSLatitude']
    print(str(datum.value()))                       # no problem
    del exifData['Exif.GPSInfo.GPSLatitude']
    print(str(datum.value()))                       # segfault!

Segmentation faults are also easily caused by careless use of iterators or memory blocks, as discussed below.
There may be other cases where the Python interface doesn't prevent segfaults.
Please let me know if you find any.

Binary data input
-----------------

Some libexiv2 functions, e.g. `Exiv2::ExifThumb::setJpegThumbnail`_, have an ``Exiv2::byte*`` parameter and a length parameter.
In python-exiv2 these are replaced by a single `bytes-like object`_ parameter that can be any Python object that exposes a simple `buffer interface`_, e.g. bytes_, bytearray_, memoryview_:

.. code:: python

    # Use Python imaging library to make a small JPEG image
    pil_im = PIL.Image.open('IMG_9999.JPG')
    pil_im.thumbnail((160, 120), PIL.Image.ANTIALIAS)
    data = io.BytesIO()
    pil_im.save(data, 'JPEG')
    # Set image thumbnail to small JPEG image
    thumb = exiv2.ExifThumb(image.exifData())
    thumb.setJpegThumbnail(data.getbuffer())

Binary data output
------------------

Some libexiv2 functions, e.g. `Exiv2::DataBuf::data`_, return ``Exiv2::byte*``, a pointer to a block of memory.
In python-exiv2 from v0.15.0 onwards this is converted directly to a Python memoryview_ object.
This allows direct access to the block of memory without unnecessary copying.
In some cases this includes writing to the data.

.. code:: python

    thumb = exiv2.ExifThumb(image.exifData())
    buf = thumb.copy()
    thumb_im = PIL.Image.open(io.BytesIO(buf.data()))

In python-exiv2 before v0.15.0 the memory block is converted to an object with a buffer interface.
A Python memoryview_ can be used to access the data without copying.
(Converting to bytes_ would make a copy of the data, which we don't usually want.)

Warning: segmentation faults
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Note that the memory block must not be deleted or resized while the memoryview exists.
Doing so will invalidate the memoryview and may cause a segmentation fault:

.. code:: python

    buf = exiv2.DataBuf(b'fred')
    data = buf.data()
    print(bytes(data))              # Prints b'fred'
    buf.alloc(128)
    print(bytes(data))              # Prints random values, may segfault

Buffer interface
----------------

The ``Exiv2::DataBuf``, ``Exiv2::PreviewImage``, and ``Exiv2::BasicIO`` classes are all wrappers around a potentially large block of memory.
They each have methods to access that memory without copying, such as ``Exiv2::DataBuf::data()`` and ``Exiv2::BasicIo::mmap()`` but in Python these classes also expose a `buffer interface`_. This allows them to be used almost anywhere that a `bytes-like object`_ is expected.

For example, you could save a photograph's thumbnail in a separate file like this:

.. code:: python

    thumb = exiv2.ExifThumb(image.exifData())
    with open('thumbnail.jpg', 'wb') as out_file:
        out_file.write(thumb.copy())

Image data in memory
--------------------

The `Exiv2::ImageFactory`_ class has a method ``open(const byte *data, size_t size)`` to create an `Exiv2::Image`_ from data stored in memory, rather than in a file.
In python-exiv2 the ``data`` and ``size`` parameters are replaced with a single `bytes-like object`_ such as bytes_ or bytearray_.
The buffered data isn't actually read until ``Image::readMetadata`` is called, so python-exiv2 stores a reference to the buffer to stop the user accidentally deleting it.

When ``Image::writeMetadata`` is called exiv2 allocates a new block of memory to store the modified data.
The ``Image::io`` method returns an `Exiv2::BasicIo`_ object that provides access to this data.

The ``BasicIo::mmap`` method allows access to the image file data without unnecessary copying.
However it is rather error prone, crashing your Python program with a segmentation fault if anything goes wrong.

The ``Exiv2::BasicIo`` object must be opened before calling ``mmap()``.
A Python `context manager`_ can be used to ensure that the ``open()`` and ``mmap()`` calls are paired with ``munmap()`` and ``close()`` calls:

.. code:: python

    from contextlib import contextmanager

    @contextmanager
    def get_file_data(image):
        exiv_io = image.io()
        exiv_io.open()
        try:
            yield exiv_io.mmap()
        finally:
            exiv_io.munmap()
            exiv_io.close()

    # after setting some metadata
    image.writeMetadata()
    with get_file_data(image) as data:
        rsp = requests.post(url, files={'file': io.BytesIO(data)})

The ``exiv2.BasicIo`` Python type exposes a `buffer interface`_ which is a lot easier to use.
It allows the ``exiv2.BasicIo`` object to be used anywhere that a `bytes-like object`_ is expected:

.. code:: python

    # after setting some metadata
    image.writeMetadata()
    exiv_io = image.io()
    rsp = requests.post(url, files={'file': io.BytesIO(exiv_io)})

Since python-exiv2 v0.15.0 this buffer can be writeable:

.. code:: python

    exiv_io = image.io()
    with memoryview(exiv_io) as data:
        data[23] = 157      # modifies data buffer
    image.readMetadata()    # reads modified buffer data

The modified data is written back to the file or memory buffer when the memoryview_ is released.

.. _bytearray:
    https://docs.python.org/3/library/stdtypes.html#bytearray
.. _bytes:
    https://docs.python.org/3/library/stdtypes.html#bytes
.. _bytes-like object:
    https://docs.python.org/3/glossary.html#term-bytes-like-object
.. _buffer interface:
    https://docs.python.org/3/c-api/buffer.html
.. _context manager:
    https://docs.python.org/3/reference/datamodel.html#context-managers
.. _dict:
    https://docs.python.org/3/library/stdtypes.html#dict
.. _enum:
    https://docs.python.org/3/library/enum.html
.. _Exiv2::BasicIo:
    https://exiv2.org/doc/classExiv2_1_1BasicIo.html
.. _Exiv2::BasicIo::mmap:
    https://exiv2.org/doc/classExiv2_1_1BasicIo.html
.. _Exiv2::DataBuf::data:
    https://exiv2.org/doc/structExiv2_1_1DataBuf.html
.. _Exiv2::ExifTags:
    https://exiv2.org/doc/classExiv2_1_1ExifTags.html
.. _Exiv2::ExifThumb::setJpegThumbnail:
    https://exiv2.org/doc/classExiv2_1_1ExifThumb.html
.. _Exiv2::Image:
    https://exiv2.org/doc/classExiv2_1_1Image.html
.. _Exiv2::ImageFactory:
    https://exiv2.org/doc/classExiv2_1_1ImageFactory.html
.. _Exiv2::Metadatum:
    https://exiv2.org/doc/classExiv2_1_1Metadatum.html
.. _Exiv2::TagInfo:
    https://exiv2.org/doc/structExiv2_1_1TagInfo.html
.. _Exiv2::TypeId:
    https://exiv2.org/doc/namespaceExiv2.html#a5153319711f35fe81cbc13f4b852450c
.. _Exiv2::Value:
    https://exiv2.org/doc/classExiv2_1_1Value.html
.. _Exiv2::ValueType< T >:
    https://exiv2.org/doc/classExiv2_1_1ValueType.html
.. _Fraction:
    https://docs.python.org/3/library/fractions.html
.. _libexiv2:
    https://www.exiv2.org/doc/index.html
.. _list:
    https://docs.python.org/3/library/stdtypes.html#list
.. _memoryview:
    https://docs.python.org/3/library/stdtypes.html#memoryview
.. _PyPI:
    https://pypi.org/project/exiv2/
```
