import click
import os
from getpass import getuser
from .licenses import Licenses
from datetime import datetime


@click.command()
@click.option('--docs',is_flag=True, help="To determine if the docs directory is created or not.")
@click.option('--user', default=str(getuser()),help="User name to put in licensing and in the setup.py.")
@click.option('-m', default="",help="A quick description of the package to put in the README.md")
@click.option('--email',default="",help="Email to put in the licensing and in the setup.py.")
@click.option('--year',default=str(datetime.now().year),help="Year to put in the licensing.")
@click.option('--license', type=click.Choice(['gplv3', 'mit','agplv3','bsd','apache2']),default='gplv3')
@click.argument('package_names',nargs=-1)
def main(m,email,year,user,license,docs,package_names):
    """
    Creates a basic framework for a python command line package.
    """

    for p in package_names:
        root_dir=os.path.abspath(os.path.dirname(p))
        if root_dir=='' or root_dir=='.':
            root_dir=os.getcwd()
        package_name=name_check(os.path.basename(p))
        if not package_name:
            click.echo("The package name, {}, is not valid. It may only include alphabetic characters and underscores.".format(package_name))
            continue
        click.echo("* Root directory for the project: {}".format(root_dir))
        click.echo("* Package name: {}".format(package_name))

        # Create repo structure
        dir_dict=create_file_structure(root_dir,package_name)
        # Create and retrive README.md text
        readme=create_readme(dir_dict['top'],package_name,description=m,docs=docs)
        click.echo("* Created README.md ")
        # Retrieve license text
        l=Licenses(year=year,name=user,email=email,package_name=package_name)
        license_str=l.retrieve_license(license)
        if license_str==None:
            click.echo("There was an error retrieving the licensing text.")
            return
        create_license(dir_dict['top'],license_str[0])
        click.echo("* Created the LICENSE file.")
        # Create test file
        create_test(dir_dict['tests'],package_name,license_str[1])
        click.echo("* Created test templates.")
        # Create __init__.py file
        create_init(dir_dict['sub'],license_str[1])
        click.echo("* Created the __init__.py script.")
        # Create setup.py
        create_setup(dir_dict['top'],user,package_name,license_str[1],readme,email)
        click.echo("* Created the setup installation script.")

def name_check(package_name,max_len=15):
    """
    By convention, packages and modules have short, all-lowercase names 
    made up of alphabetical characters and underscores.
    
    Cast to lower, replace dashes by underscores, remove periods and shorten if needed.
    """
    name=package_name.lower()
    name=name.replace("-","_")
    name=name.replace(".","")
    if not name.replace("_","").isalpha():
        return False
    return name[:max_len]
    
def create_license(top_dir,license_str):
    with open(os.path.join(top_dir,'LICENSE'),'w') as f:
        f.write(license_str)
    
    
def create_readme(top_dir,package_name,description="",docs=False):
    """
    README requires the name of the package and the directory in which to write the file in.
    Optionally, give a description and whether or not to create a 'docs' directory.
    """
    
    readme_str="""
# {package}

## Description
{description}

## Examples

## Repo Structure 

{package}:<br/>
┣━ README.md<br/>
┣━ LICENSE<br/>
┣━ setup.py<br/>
┣━ {package}:<br/>
┃   ┗━ __init__.py<br/>
"""
    if docs:
        readme_str= readme_str + \
                """┣━ tests:<br/>
┃   ┗━ test_basic.py<br/>
┗━ docs:<br/>
    ┗━"""
    else:
        readme_str= readme_str + \
        """┗━ tests:

    ┗━ test_basic.py
"""
        readme_str=readme_str.format(package=package_name,description=description)
        
        # Write to file
        with open(os.path.join(top_dir,'README.md'),'w') as f:
            f.write(readme_str)
            
        return readme_str

def create_init(sub_dir,license):
    """
    __init__.py does not require anything special. It will just create a boilerplate file.
    """
    init_str="""{license}

import click

@click.command()
@click.option('--option1',default='',help="First option")
def main(option1):
    '''
    Description of the package.
    '''
    """.format(license=license)

    with open(os.path.join(sub_dir,"__init__.py"),'w') as f:
        f.write(init_str)

def create_test(test_dir,package_name,license):
    """
    test_basic.py will create a template test file and a context script
    in order to run the tests without installing the package each time.
    """
    
    context="""{license}

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import {package_name}""".format(package_name=package_name,license=license) 
    
    with open(os.path.join(test_dir,"context.py"),"w") as f:
        f.write(context)
        
    test_template="""{license}
from .context import {package_name}""".format(package_name=package_name,license=license)
    with open(os.path.join(test_dir,"test_basic.py"),"w") as f:
        f.write(test_template)
        
def create_setup(top_dir,username,package_name,license,readme,email=""):

    """
    setup.py requires a readme, a license, the package name and the username.
    Email is optional but can be put into.
    """
    
    setup_str="""from setuptools import setup, find_packages

setup(
    name='{package_name}',
    version='0.1',
    author='{username}',""".format(package_name=package_name,username=username)
    if email:
        setup_str+="""
    author_email='{email}',"""
    setup_str+="""
    packages=find_packages(),
    long_description='''{readme}''',
    license='''{license}''',
    include_package_data=True,
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        {package_name}={package_name}.__init__:main
    ''',
)""".format(package_name=package_name,license=license,readme=readme,username=username)
    if email:
        setup_str=setup_str.format(email=email)
    
    with open(os.path.join(top_dir,"setup.py"),"w") as f:
        f.write(setup_str)

def create_file_structure(root_dir,package_name,docs=False,tests=True):
    top_dir=os.path.join(root_dir,package_name)
    sub_dir=os.path.join(top_dir,package_name)
    docs_dir=os.path.join(top_dir,'docs')
    tests_dir=os.path.join(top_dir,'tests')
    
    payload={}
    payload["top"]=top_dir
    payload["sub"]=sub_dir
    payload["docs"]=docs_dir
    payload["tests"]=tests_dir

    
    if not os.path.isdir(top_dir):
        os.mkdir(top_dir)
    if not os.path.isdir(sub_dir):
        os.mkdir(sub_dir)
    if docs and not os.path.isdir(docs_dir):
        os.mkdir(docs_dir)
    if tests and not os.path.isdir(tests_dir):
        os.mkdir(tests_dir)
    return payload
    
