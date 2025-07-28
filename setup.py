from setuptools import setup, find_packages

setup(
    name="contextual-privacy-llm",
    version="0.1.8",
    description="A toolkit for safeguarding contextual privacy in LLM prompts",
    author="IBM Research",
    author_email="ivoline@ibm.com",
    url="https://github.com/IBM/contextual-privacy-LLM",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    package_data={
        "contextual_privacy_llm": ["prompts/*/*.txt"],
    },
    install_requires=["requests>=2.0"],
    entry_points={
        "console_scripts": [
            "contextual-privacy-llm=contextual_privacy_llm.runner:main",
        ],
    },
    python_requires=">=3.8",
)
