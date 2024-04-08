from setuptools import find_packages, setup

setup(
    name="pyinterfacer",
    packages=find_packages(include=["pyinterfacer", "pyinterfacer.*"]),
    version="0.1.0",
    description="A modular library for handling interfaces in pygame projects.",
    author="Gabriel RQ",
    install_requires=["PyYAML", "pygame-ce"],
)
