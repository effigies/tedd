# Print if the specified verbosity is below the global verbose variable
for_real = True
verbose = 1

def debugPrint(string, verbosity=1):
    if verbosity <= verbose:
        print string
