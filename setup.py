from setuptools import find_packages, setup

setup(name="paradrop-voice",
      version="0.1",
      description="Enable voice interactivity with a Paradrop node.",
      author="Paradrop Labs",
      author_email="info@paradrop.io",
      url="https://paradrop.org",
      packages=find_packages(),
      install_requires=[
          "certifi>=2019.6.16",
          "chardet>=3.0.4",
          "Flask>=1.0.2",
          "idna>=2.8",
          "pocketsphinx>=0.1.3",
          "pyttsx3>=2.7",
          "requests>=2.22.0",
          "urllib3>=1.25.3",
          "Werkzeug>=0.15.5"
      ],
      entry_points={
          "console_scripts": [
              "paradrop-voice = voice.server:main"
          ]
      }
)
