from setuptools import setup

__version__ = '0.1.0'

setup(
    name='weather-station',
    packages=['weather_station'],
    entry_points={
        "console_scripts": ["weather-station=weather_station.main:main"],
    },
    version=__version__,
    description='Weather station',
    url='https://github.com/jschnab/weather-station',
    author='Jonathan Schnabel',
    author_email='jonathan.schnabel31@gmail.com',
    license='GNU General Public License v3.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3.6',
    ],
    python_requires='>=3.6',
)
