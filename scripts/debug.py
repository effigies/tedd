# Print if the specified verbosity is below the global verbose variable
for_real = False
verbose = 2

def debugPrint(string, verbosity=1):
    if verbosity <= verbose:
        print string
