from setuptools import find_packages
from setuptools import setup

with open('requirements.txt') as f:
    content = f.readlines()
requirements = [x.strip() for x in content if 'git+' not in x]

<<<<<<< HEAD
setup(name='menu_me',
      version="1.0",
      description="Project Description",
=======
setup(name='menu-me',
      version="1.0",
      description="Visualize your menu",
>>>>>>> d1450ba50b29deae198fad60f9429a31135a407c
      packages=find_packages(),
      install_requires=requirements,
      test_suite='tests',
      # include_package_data: to install data from MANIFEST.in
      include_package_data=True,
      scripts=['scripts/menu_me-run'],
      zip_safe=False)
