from setuptools import setup

setup(name='waabi',
    version='0.1',
    description='waabi is an Ojibwe Word for "s/he has vision, sees"',
    url='https://github.com/bdunford/waabi/',
    author='b1rch',
    author_email='birch.dunford@gmail.com',
    license='MIT',
    include_package_data=True,
    packages=[
        'waabi',
        'waabi/proxy',
        'waabi/belch',
        'waabi/scan',
        'waabi/utility',
        'waabi/wordlists'
    ],
    package_data={'waabi/wordlists':['*.txt']},
    zip_safe=False,
    scripts=['bin/waabi'],
    install_requires=[
        'requests',
        'requests-html',
        'proxy.py'
    ]
)
