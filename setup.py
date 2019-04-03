from setuptools import setup, find_packages

setup(name='IECview',
      version='0.0.1',
      packages=['IECview', 'IECview.tools', 'IECview.GUI'],
      python_requires='>3.6',
      setup_requires=['setuptools', 'wheel'],
      install_requires=['numpy', 'silx', 'h5py', 'freesas',],
      )
