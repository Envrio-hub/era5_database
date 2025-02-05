from setuptools import setup, find_packages

setup(
    name='era5_database',
    version='0.1.0',
    description='A library that handles the era5 database',
    author='Ioannis Tsakmakis, Nikolaos Kokkos',
    author_email='itsakmak@envrio.org, nkokkos@envrio.org',
    packages=find_packages(),
    python_requires='>=3.12',
    install_requires=[  
        'sqlalchemy>=2.0.37',
        'mysql-connector-python>=9.2.0',
        'pydantic>=2.10.6',
        'influxdb-client>=1.48.0',
        'database_companion @ git+https://github.com/Envrio-hub/LibCompanion.git@0.1.0#egg=database_companion'
    ],
    classifiers=[  
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.12',
        'Framework :: Flask',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
