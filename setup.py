from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='pypackage-gen',
    version='0.2',
    packages=find_packages(),
    long_description=readme,
    license=license,
    include_package_data=True,
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        pypackage_gen=pypackage_gen.__init__:main
    ''',
)
