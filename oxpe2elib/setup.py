from setuptools import setup, find_packages
setup(
    name='oxpe2elib',
    version='0.1.dev1',
    ###scripts=['oxpe2e'],
    packages=find_packages(),
    author="cheney",
    author_email="cheney.ketley@stfc.ac.uk",
    description="This is the oxpe2e library (The Offline Cross-Program language End to End encryption utility)",
    url="https://github.com/cketley/oxpe2e",
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: Apache 2",
        "Operating System :: GNU-Linux"
    ],
    install_requires=['enum34;python_version<"3.4"','pywin32 >= 1.0;platform_system=="Windows"', 'paho-mqtt', 'pycrypto', 'valideer', 'pika']
)

