from setuptools import setup, find_packages

setup(
    name='PlotHelper',
    version='3.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
  
    ],
    entry_points={
        'console_scripts': [
            'command=plot_helper:format',
        ],
    },
)
