
# DeriNet 2.0 API

An API for interfacing with derivational networks and tools for
creating and manipulating them.


<!-- TODO Coverage badges, perhaps CI links? -->


## Table of contents
- [Introduction](#introduction) – what is a derivational network?
- [Usage](#usage) – how to install and use the API, where to get support.
- [Contributing](#contributing) – how can you help us.
- [Authors](#authors) – acknowledgments and copyright.
- [License](#license) – terms of use.

## Introduction

A derivational network is a kind of a wordnet – a graph in which
the nodes are lexemes and edges are relations between them.
Despite being called “derivational”, the links need not be only
derivations. Various networks express conversion, compounding and
non-morphological changes as well.

<!-- TODO Some images. -->

<!-- TODO Why should you care about this API? -->
In order to process various such networks in a unified fashion,
we developed a universal file format documented in doc/xxx<!-- TODO link -->
and a modular Python application to process it.

So far, we have modules for loading the
[DeriNet dataset](https://ufal.mff.cuni.cz/derinet). 
<!-- TODO List other existing datasets for which we have
          conversion utilities. -->



<!-- TODO Links to other tools – DeriSearch etc. -->


<!-- TODO Documentation link. -->

## Usage

### Prerequisites

The only necessary package is `python3`. We test the API using
Python 3.6.5 and PyPy 6.0.0 on Linux.

For ease-of-use, you may want to install GNU Make as well.


### Installation

Checkout the Git tree. Set up PYTHONPATH.
<!-- TODO Tell the users how to set up PYTHONPATH. -->


### Usage

The API can be used in two ways – programmatically from Python code,
or by composing existing modules from the command-line.

#### Command-line

```shell
# Show help
python3 -m derinet.process_scenario -h

# List officially available modules.
python3 -m derinet.process_scenario -l

# Show help for the derinet.modules.Load module
python3 -m derinet.process_scenario Load -h

# Load a derinet and save it again in a different format.
python3 -m derinet.process_scenario Load derinet-2.0.tsv Save --format DERINET_V1 derinet-2.0-fmt1.tsv
```

#### Programming

Basic loading:
```python
import derinet.lexicon as dlex

# Create an empty lexicon.
lexicon = dlex.Lexicon()
# Load the DeriNet-2.0 database into it.
lexicon.load("./derinet-2-0.tsv")

# Use the lexicon object.
```

See TODO <!-- TODO Documentation link. --> for documentation of the
API and its components.



### Support

<!-- TODO Documentation link. -->
<!-- TODO DeriNet homepage link. -->
<!-- TODO My e-mail. -->


### Examples

Printing all lexemes from the database together with their parents:
```python
import derinet.lexicon as dlex

# Create an empty lexicon.
lexicon = dlex.Lexicon()
# Load the DeriNet-2.0 database into it.
lexicon.load("./derinet-2-0.tsv")

# Print all lexemes from the database, with the antecedent
#  if there is one.
for lexeme in lexicon.iter_lexemes():
    if lexeme.parent is None:
        # The lexeme is not created from another word.
        print("Base word: {} {}".format(lexeme.lemma, lexeme.pos))
    else:
        # The lexeme is created from another word.
        print("{} -> {}".format(lexeme.parent.lemma, lexeme.lemma))
```

<!-- TODO Add more examples. -->


## Contributing

We welcome all contributors – the preferred way of contributing is
submitting pull requests on GitHub, but if you don't have an account,
you can also submit patches by mail to user “vidra” at the domain
“ufal.mff.cuni.cz”.

All submitted code must be sufficiently covered by unit tests and
regression tests.

Possible tasks you can work on are listed below.


### Bugs

Please, report any bugs, inefficiencies and issues using the GitHub
bug tracker.


### Adding derivational networks



### Writing new processing modules

The user-facing side of our processing API consists of scriptable
scenarios composed of modules. Therefore, if you want to extend the
functionality of the API, the easiest way of doing so is writing
a new module which would perform the required actions.

The following rules apply to module writing:

#### Object-oriented classes

Modules are subclasses of `Block` (defined in <derinet/block.py>).
If your module doesn't need any command-line parameters, you can
just override the `process(self, lexicon)` method. In it, perform
the necessary processing with the lexicon object and return it.
Always return the modified lexicon!

#### Argument parsing

If your module requires command-line argument parsing, override the
`parse_args(args)` static method and `__init__(self, *args, **kwargs)`
as well.

The `parse_args(args)` method should read the arguments it understands
from the start of the `args` list of strings and return a tuple of three
objects: The positional arguments passed to the constructor, the keyword
arguments passed to the constructor and the unprocessed tail of `args`,
which will be passed to downstream modules.

Make sure to never eat more args than you need. In particular, never
include an unbounded number of positional parameters in your parser.
It may then happen that a name of another module is mistaken for
an argument to your module. For the same reason, be careful with
optional parameters.

The easiest way of parsing is to use argparse, add a `rest` parameter
to the list of positional parameters with `nargs=argparse.REMAINDER`,
and return that.

#### File names

The classes implementing blocks are stored in Python files. In order
for our custom classloading to work, the module name (its file name)
must be the lowercased name of the class. They are loaded using their
`package.class` name.

This means that a module which would be called as
“`derinet.modules.cs.LoadHTTPDerivations`” must be stored as a class
called `LoadHTTPDerivations` in file
`derinet/modules/cs/loadhttpderivations.py`.


### Running the test suite

Since the derinet API includes a comprehensive suite of unit tests,
you can help our project simply by running the test in your environment
and reporting any failures (or, for that matter, successes – especially
on unusual systems).

If you have GNU Make, you can run `make test` in the project directory
to automatically run all tests from `./test/`. Otherwise run single
test files directly or use the `unittest` discovery mode:
```shell
python3 -m unittest discover -s ./test/ -p 'test_*.py'
```

<!-- FIXME Delete this notice after it stops being true. -->
Currently, some tests are known to fail due to unimplemented features.
Please, be patient while we implement everything.




## Authors

Copyright &copy; 2019 Jonáš Vidra and the rest of the DeriNet team.
See the Git contributor history for the exact list of authors.

<!-- TODO acknowlegdments. Especially grants. -->


## License

This project is licensed under the
[TODO license][license]. <!-- TODO Specify the license. -->

[license]: https://example.net/
