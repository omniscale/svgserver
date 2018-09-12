from setuptools import setup, find_packages

setup(
    name="svgserver",
    description="Render layered SVG files with MapServer",
    version="0.2.0",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": []
    },
    extras_require={},
    install_requires=["Werkzeug"],
)
