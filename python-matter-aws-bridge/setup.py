from setuptools import find_packages, setup

setup(
    name="Matter AWS Bridge",
    version="1.0",
    python_requires=">=3.8, <4",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "matterawsbridge=matterawsbridge:main",
        ]
    },
)
