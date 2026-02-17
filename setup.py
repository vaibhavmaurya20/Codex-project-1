from setuptools import find_packages, setup

setup(
    name="ascend-net-omega-x",
    version="0.2.0",
    description="Low-resource cognitive execution runtime",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.10",
)
