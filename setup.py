from setuptools import setup, find_packages

setup(
    name='RedcapLite',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'requests',
        'pandas',
    ],
    description='A Python package for interacting with the REDCap API',
    author='Jubilee Tan',
    author_email='jubilee2@gmail.com',
)