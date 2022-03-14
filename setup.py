from setuptools import setup

setup(
   name='solver',
   version='0.1',
   description='Solve term.ooo with python',
   author='Pedro Sidra de Freitas',
   author_email='pedrosidra0@gmail.com',
   packages=['solver'],  #same as name
    entry_points = {
        'console_scripts': [
            'termo-solver=solver.cli:main',
            'termo-player=solver.player:main',
            'termo-generate=solver.generate_matches:main'
            ],
    }

)