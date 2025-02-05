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
        'aws_utils @ {ref = "1.1.0", git = "https://github.com/Envrio-hub/aws_utils.git"}',
        'mysql-connector-python>=9.2.0',
        'pydantic>=2.10.6',
        'influxdb-client>=1.48.0'
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
