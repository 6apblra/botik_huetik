from setuptools import setup, find_packages

setup(
    name="vpn_service",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "aiogram==3.4.1",
        "aiohttp==3.9.5",
        "python-dotenv==1.0.1",
        "qrcode[pil]==7.4.2"
    ],
)
