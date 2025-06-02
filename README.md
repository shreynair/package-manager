# package-manager
 In this project, we're going to build a simple package manager 
    from scratch by calling out to Z3 Python APIs.

    This project highlights how easy it is to reduce common challenges
    to a series of solver calls.

    We will represent a package repo as a tuple: (packages, conflicts).

    - `packages` is a dictionary mapping package names to
        pairs of their (1) dependencies and (2) size.

        (1) Dependencies are specified as a *list of lists*. For package `p`
        to successfully install, at least one package from each
        inner list must be installed.

        (2) The size of a package represents how much disk space (in MB)
        the package will take once installed. You only need to use size
        if you choose to attempt the final challenge problem.

     - `conflicts` is a list of pairs of packages that cannot be
        installed together. For example, if the conflicts list
        contains `(p, q)` for packages named `p` and `q`, then only
        one of `p` or `q` can be installed, but not both.
    
    To run the tests:
        python3 test1.py
        python3 test2.py
