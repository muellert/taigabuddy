from setuptools import setup, find_packages


with open('requirements.txt') as req:
    install_requires = [line for line in req.readlines()
                        if not line.startswith('#')]

packages = find_packages('.', exclude=['tests'])
print("packages found: ", packages)


setup(
    name="taigabuddy",
    version="0.1",
    package_dir={'': 'src'},
    packages=find_packages('src', exclude=['tests']),
    python_requires=">=3.5",
    install_requires=install_requires,
    tests_require=['pytest'],
    include_package_data=True,
    author='Toni Mueller',
    author_email='toni.muller@unipart.io',
    platforms=['linux'],
    zip_safe=False,
)
