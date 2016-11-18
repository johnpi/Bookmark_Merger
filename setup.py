from setuptools import setup

setup(name='bookmark_merger',
        version='0.2.3',
        description='code for merging multiple firefox bookmark.html files',
        long_description="""\
Bookmarks merger allows the user to merge multiple firefox bookmark.html files 
together, taking care to intelligently merge duplicate folder layouts. The script
bookmark_merger.py can be used on a folder of bookmarks.html files or the 
bookmark_parser.py can be imported as a module. More detailed instructions exist
in the README file and on the sourceforge site.
        """,
        classifiers=[
          "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
          "Programming Language :: Python",
          "Development Status :: 3 - Alpha",
          "Environment :: Console",
          "Intended Audience :: Developers",
          "Intended Audience :: End Users/Desktop",
          "Intended Audience :: System Administrators",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Topic :: Utilities",
          "Topic :: Internet :: WWW/HTTP :: Browsers"
           ],
        author='robochat',
        author_email='rjsteed@talk21.com',
        url='https://sourceforge.net/projects/bookmark-merger/',
        license='LGPLv3',
        keywords='firefox',
        py_modules=['bookmark_pyparser','example','example_bookmark_merger','setup'], # this is too small to setup a package system
        scripts=['bookmark_merger.py'],
        data_files=[('',['COPYING','COPYING.LESSER','README'])],
        install_requires=['pyparsing'],
        zip_safe=False
        )


