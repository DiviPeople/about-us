""" Script for building the About-us package. """

from setuptools import setup

try:
    import pypandoc

    LONG_DESCRIPTION = pypandoc.convert('README.md', 'rst')
except (ImportError, OSError):
    # OSError is raised when pandoc is not installed.
    LONG_DESCRIPTION = ('About-us is microservice intended to '
                        'gather info about organization from Github '
                        'to display them on the client.')

with open('requirements.txt') as outfile:
    REQUIREMENTS_LIST = outfile.read().splitlines()

setup(name='about-us',
      version='0.1',
      description='About-us package',
      long_description=LONG_DESCRIPTION,
      url='https://github.com/SwallowMyCode/about-us',
      author='Vladislav Yarovoy, Dmitry Ivanko',
      author_email='vlad_yarovoy_97@mail.ru, tmwsls12@gmail.com',
      maintainer='Vladislav Yarovoy',
      maintainer_email='Vladislav Yarovoy vlad_yarovoy_97@mail.ru',
      license='http://www.apache.org/licenses/LICENSE-2.0',
      scripts=['bin/server.py'],
      packages=['about-us'],
      include_package_data=True,
      data_files=[
          ('', ['requirements.txt',
                'LICENSE'])
      ],
      install_requires=REQUIREMENTS_LIST)
