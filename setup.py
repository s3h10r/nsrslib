# -*- coding: utf-8 -*-
from distutils.core import setup

setup(name='nsrslib',
      version='0.0.9',
      description='a simple scripting library for emc networker',
      author='Sven Hessenmüller',
      author_email='sven.hessenmueller@gmail.com',   
      url='https://github.com/s3h10r/nsrslib',
      py_modules=['usage-example'],
      packages=['nsrslib'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 2.7',
          'Topic :: System :: Archiving :: Backup',
          ],
      platforms = ['Linux'],
      license='GPLv3+',
)
