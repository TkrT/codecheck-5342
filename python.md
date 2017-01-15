# Command line application template for Python2.x

Implement CLI application by editing [main.py](app/main.py).  
You may add new files to keep your code clean, if it is allowed in your challenge.

## How to get input parameters

In [main.py](app/main.py), there is a function called `main`, which gives command line arguments as `argv`.

``` python
def main(argv):
    # code to run
```

`argv` passed here is came from [index.py](index.py), which passes `sys.argv` to `main` function. Script name information is excluded in `argv` of main method.

## How to output result
You can use the standard `print()` method to output results to `stdout`.

``` python
print(result)
```

## Install External Libraries
If you want to use external libraries, do the following:

- Write the library name and version in [requirements.txt](requirements.txt)
