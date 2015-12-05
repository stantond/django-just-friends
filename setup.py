import os
from setuptools import setup, find_packages

from friendship import VERSION


f = open(os.path.join(os.path.dirname(__file__), 'README.rst'))
readme = f.read()
f.close()

setup(
    name='django-just-friends',
    version=".".join(map(str, VERSION)),
    description='django-just-friends is a basic friend system',
    long_description=readme,
    author='Daniel Stanton',
    author_email='danielstanton@live.co.uk',
    url='https://github.com/stringsonfire/django-just-friends/',
    include_package_data=True,
    packages=find_packages(),
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Framework :: Django',
    ],
    test_suite='friendship.tests.runtests.runtests'
)
