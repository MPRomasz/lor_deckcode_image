from setuptools import setup, find_packages

setup(
    name='lor_deckcode_image',
    version='1.0',
    url='',
    description='Legends of Runeterra deck code into image',
    author='',
    maintainer='',
    maintainer_email='',
    license='MIT',
    packages=find_packages(exclude=('tests', 'tests.*')),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.5',
    install_requires=[
	'requests',
	'lor-deckcodes',
	'pillow'
    ],
)