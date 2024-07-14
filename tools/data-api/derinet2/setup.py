import setuptools

setuptools.setup(
    name = "derinet",
    packages = setuptools.find_packages(include="derinet*"),
    scripts = ["derinet/process_scenario.py"],
)
