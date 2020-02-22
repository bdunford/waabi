from setuptools import setup

setup(name='waabi',
    version='0.1',
    description='waabi is an Ojibwe Word for "s/he has vision, sees"',
    url='https://github.com/bdunford/waabi/',
    author='b1rch',
    author_email='birch.dunford@gmail.com',
    license='MIT',
    packages=['waabi'],
    zip_safe=False,
    scripts=['bin/waabi'],
    install_requires=[
        'requests',
        'requests-html',
        'proxy.py'
    ]
)
