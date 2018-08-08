from setuptools import find_packages, setup

setup(name="paradrop-voice",
      version="0.1",
      description="Enable voice interactivity with a Paradrop node.",
      author="Paradrop Labs",
      author_email="info@paradrop.io",
      url="https://paradrop.org",
      packages=find_packages(),
      install_requires=[
          "certifi==2018.4.16",
          "chardet==3.0.4",
          "Flask==1.0.2",
          "idna==2.6",
          "pocketsphinx==0.1.3",
          "pyttsx3==2.7",
          "requests==2.18.4",
          "urllib3==1.22",
          "pygame==1.9.4",
          "python-vlc==3.0.102"
      ],
      entry_points={
          "console_scripts": [
              "paradrop-voice = voice.server:main"
          ]
      }
)
