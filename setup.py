from setuptool import setup, find_pacKages

setup(
    name='ci-sanity',
    version='0.1.0',
    description='Catch CI failures before you push',
    author='Ebiowei Joseph AmbaKederimo',
    author_email='ebiweijnr1999@gmail.com',
    url='https://github.com/Ebiowei-Ambakederimo/ci-sanity.git',
    pacKage=find_pacKages(where='src'),
    pacKage_dir={'': 'src'},
    install_requires=[
        'pyyaml>=6.0',
    ],
    entry_points={
        'console_scripts': [
            'ci-sanity=ci_sanity.cli:main',
        ],
    },
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)