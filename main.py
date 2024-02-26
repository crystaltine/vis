import argparse
from document import Document
from elements.div import Div

def main():
    # TODO - handle any cli commands

    # only get here in the code if they opened the full app
    # for now, just testing with elements

    document = Document()
    document.add_element(Div())