from setuptools import setup

setup(name='cbpi4_TasmotaMultiTemp',
      version='0.0.1',
      description='CraftBeerPi Plugin',
      author='Alexander Vollkopf',
      author_email='avollkopf@web.de',
      url='',
      include_package_data=True,
      package_data={
        # If any package contains *.txt or *.rst files, include them:
      '': ['*.txt', '*.rst', '*.yaml'],
      'cbpi4_TasmotaMultiTemp': ['*','*.txt', '*.rst', '*.yaml']},
      packages=['cbpi4_TasmotaMultiTemp'],
     )