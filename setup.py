from setuptools import setup, find_packages

setup(
    name='Drone_Management_API',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'Flask==3.0.0',
        'Flask-RESTful==0.3.10',
        'Flask-SQLAlchemy==3.1.1',
        'marshmallow==3.20.1',
        'SQLAlchemy==2.0.23',
        'APScheduler==3.10.4',
    ],
    entry_points={
        'console_scripts': [
            'start_Drone = Drone_Management_API:main',
        ],
    },
)
