# RW214 Marking Script

## Running the script

To run the marking script execute the following from the testsuite directory:

```bash
sh mark.sh [mode]
```

The parameter `mode` can take on either 1, 2, or 3, corresponding to the modes of the project, and giving no parameters to `mark.sh` will run all modes.

After running the marking script, your marks will be saved to the file `rubric.md` in the testsuite directory which contains a breakdown for each test case and may contain additional comments if there were formatting issues.

## Compiling your work manually

You can compile your program into a jar file that is saved to the project directory like is done in the marking script by running the following in the testsuite directory:

```bash
sh build.sh
```

N.B. You will need to install _ant_ for both `build.sh` and the marking script to work.
