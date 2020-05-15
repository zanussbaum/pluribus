from setuptools import setup, find_namespace_packages

setup(name='pluribus',
      version='0.1',
      description='implementing pluribus',
      url='https://github.com/zanussbaum/pluribus',
      author='zanussbaum',
      license='MIT',
      packages=find_namespace_packages(include=["leduc.*"]),
      zip_safe=False)