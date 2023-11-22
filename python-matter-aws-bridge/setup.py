import os

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
    install_requires=[
        "aenum==3.1.15",
        "awscrt==0.19.1",
        "awsiotsdk==1.19.0",
        "certifi==2023.7.22",
        "cffi==1.16.0",
        "charset-normalizer==3.3.0",
        "cryptography==41.0.4",
        "dacite==1.8.1",
        "idna==3.4",
        "pycparser==2.21",
        "python-dotenv==1.0.0",
        "requests==2.31.0",
        "urllib3==2.0.6",
        "websocket-client==1.6.4",
        "chip-clusters",
    ],
    dependency_links=[
        os.path.join(os.getcwd(), "deps", "chip_clusters-0.0-py3-none-any.whl")
    ],
)
