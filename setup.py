from setuptools import setup

setup(
    name='x',
    version='0.1-dev',
    packages=['x'],
    entry_points={
        'console_scripts': ['x = x:entry_point'],
    },
)
