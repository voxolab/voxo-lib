from setuptools import setup

setup(
    name='voxo-lib',
    version='0.1.0',
    author='Voxolab',
    author_email='contact@voxolab.com',
    packages=['voxolab'],
    scripts=[],
    url='http://voxolab.com',
    license='LICENSE.txt',
    description='Useful Voxolab libs.',
    long_description=open('README.txt').read(),
    data_files=[('bin', ['bin/convertirAlphaEnNombre.pl', 'bin/convertirNombreEnAlpha.pl'])],
    requires=[
        'pytest',
        'lxml'
    ],
)
