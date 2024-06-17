"""This module defines enumerations related to URLs and paths."""

from enum import Enum

class URLs(Enum):
    """Enumeration of URLs."""
    YAD2_URL = "https://www.yad2.co.il/realestate/forsale"

class Paths(Enum):
    """Enumeration of paths."""
    WEBDRIVER_PATH = "C:\\path\\to\\your\\chromedriver.exe"
    BASE_PATH = "C:\\path\\to\\your\\project"
