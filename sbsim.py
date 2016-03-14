from sys import argv
from generator import *

script, inputfile = argv

def main():
    order = 2

    filetext = process_file()

    markov = GeneratorDict(filetext, order, 123)
    markov.read_text()
    output = markov.output_text()
    print output

def process_file():
    with open(inputfile) as f:
        filetext = f.read()

    return filetext

if __name__ == "__main__":
    main()
