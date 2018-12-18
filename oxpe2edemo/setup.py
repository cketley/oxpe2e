from setuptools import setup

setup(
    name='oxpe2e-demo-mqtt-alice2bob',
    version='0.1.dev1',
    scripts=['oxpe2eDemoMqttAlice2Bob.py'],
    author="cheney",
    author_email="cheney.ketley@stfc.ac.uk",
    description="This is the demo suite for oxpe2e (The Offline Cross-Program language End to End encryption utility for IoT comms)",
    url="https://github.com/cketley/oxpe2e",
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: Apache 2",
        "Operating System :: GNU-Linux"
    ],
    install_requires=['pywin32 >= 1.0;platform_system=="Windows"', 'oxpe2elib' ]
)

setup(
    name='oxpe2e-demo-mqtt-bobfromalice',
    version='0.1.dev1',
    scripts=['oxpe2eDemoMqttBobFromAlice.py'],
    author="cheney",
    author_email="cheney.ketley@stfc.ac.uk",
    description="This is the demo suite for oxpe2e (The Offline Cross-Program language End to End encryption utility for IoT comms)",
    url="https://github.com/cketley/oxpe2e",
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: Apache 2",
        "Operating System :: GNU-Linux"
    ],
    install_requires=['pywin32 >= 1.0;platform_system=="Windows"', 'oxpe2elib' ]
)

