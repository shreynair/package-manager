# CMSC433 Project 3 Package Manager

"""
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
"""

from z3 import *

class PackageManager:
    def __init__(self,repo):
        self.packages = repo[0]
        self.conflict = repo[1]
        self.solver  = Solver()

    #
    # TASK 1
    #
    # Given a package, `p` in `packages`,
    # return a boolean formula encoding its dependencies.
    #
    # For example, if the dependencies of `p` are
    #
    #       [["bar", "baz"], ["foo"]]
    #
    # then `getDepsBasic(p)` should return `Implies(p, And(Or(bar, baz), foo))`
    #

    def getDepsBasic(self, p):
        dep = self.packages[p][0]
        result = Implies(Bool(p), And([Or([Bool(elem) if len(self.packages[elem][0]) == 0 else And(Bool(elem), self.getDepsBasic(elem)) for elem in d]) for d in dep]))
        return result
    
    
    
    #
    # TASK 1a
    #
    # Inspect the results in TASK 1 and 
    # notice how they can sometimes be further simplified.
    # For example `Or(b)` can be rewritten to the simpler term, `b`.
    # Use the `simplify` command to apply transformations to the results
    # from `getDeps()` to simplify the formula.
    #
   
    def getDeps(self, p):
        result = simplify(self.getDepsBasic(p))
        return result
    
    # TASK 2
    #
    # Implement `getConflicts(repo)` following the description below.
    # Given a package repository, `repo`,
    # `getConflicts(repo)` must returns a boolean formula
    # encoding its conflicts.
    #
    # For example, if conflicts = [(p1, p2), (p1, p3), (p2, p4), ...],
    # getConflicts(repo) should return
    # And(Not(And(p1, p2)), Not(And(p1, p3)), Not(And(p2, p4)), ...)
    #
    def getConflicts(self, repo):
        results = And([Not(And(Bool(p[0]),Bool(p[1]))) for p in repo[1]])
        results = simplify(results)
        return results


    #
    # TASK 3a
    #
    # Implement `can_install(repo, installed_pkg, tgt_pkg)`
    # following the description below.
    #
    # Given a repository, a package that already installed, and
    # a target package, `can_install(repo, installed_pkg, tgt_pkg)`
    # must either return "sat" if `tgt_pkg` can be installed,
    # (again, assuming that `installed_pkg` is already installed!) or
    # return "unsat" if tgt_pkgs cannot be installed.
    #
    # HINT: you will need to use your implementation of
    # `getDeps(p)` and `getConflicts(repo)`.
    #
    # TIP: use the model() command to understand the concrete
    # example in the "sat" case.
    #
    def can_install(self, repo, installed_pkg, tgt_pkg):
        if(installed_pkg not in repo[0]):
            return sat
        installed_Deps = self.getDeps(installed_pkg)
        tgt_Deps = self.getDeps(tgt_pkg)
        Conflicts = self.getConflicts(repo)
        s = Solver()
        s.add(Bool(installed_pkg))
        s.add(Bool(tgt_pkg))
        s.add(installed_Deps)
        s.add(tgt_Deps)
        s.add(Conflicts)
        
        if s.check() == sat:
            return sat
        else:
            return unsat


    #
    # TASK 3c
    #
    # Now generalize `can_install` to support multiple
    # target packages.
    #
    def can_installs(self,repo, installed_pkgs, tgt_pkgs):
        for i in installed_pkgs:
            for t in tgt_pkgs:
                if(self.can_install(repo, i, t) == unsat):
                    return unsat
                if(t not in installed_pkgs):
                    installed_pkgs.append(t)
        return sat
   

    #
    # Implement `install_under_constraint` such that
    # it satisfies all `hard` clauses and the largest
    # number of `soft` clauses.
    #
    # In this setting, the hard constraint is `tgt_pkg` that
    # you have to install and the
    # soft contraints are `installed_pkgs` from which
    # you want to keep the largest number of packages
    # you can while still being able to install `tgt_pkg`.
    #
    # For this task, you will use the solver's `Optimize()`
    # feature instead of `Solve()`.
    #
    # You already know how to add "hard" clauses,
    # it's just: o.add(FORMULA).
    #
    # To add a "soft" clause, use: o.add_soft(FORMULA).
    #
    #
    def install_under_constraint(self, repo, installed_pkgs, tgt_pkg):
        o = Optimize()
        
        # Add the hard constraint (we must install tgt_pkg)
        o.add(Bool(tgt_pkg))
        
        # Add conflicts as hard constraints
        for p in repo[1]:
            if(tgt_pkg in p):
                o.add(Not(And(Bool(p[0]),Bool(p[1]))))
            else:
                o.add_soft(Not(And(Bool(p[0]),Bool(p[1]))))
        
        # Add dependencies of the target package as hard constraints
        o.add(self.getDeps(tgt_pkg))

        # Add installed packages as soft constraints (we prefer to keep them)
        for pkg in installed_pkgs:
            o.add_soft(Bool(pkg))
        
        # Check for satisfiability
        if o.check() == sat:
            model = o.model()
            result = {Bool(pkg): model.eval(Bool(pkg)) == True for pkg in installed_pkgs}
            result[Bool(tgt_pkg)] = True
            return result
        else:
            return unsat

    #
    # Now generalize install_under_constraint
    # to support multiple installed packages and target packages.
    #
    def install_many_under_constraint(self, repo, installed_pkgs, tgt_pkgs):
        o = Optimize()
        
        # Add hard constraints for each target package (we must install all of them)
        for pkg in tgt_pkgs:
            o.add(Bool(pkg))
            o.add(self.getDeps(pkg))

        # Add conflicts as hard constraints
        for p in repo[1]:
            for pkg in tgt_pkgs:
                if(pkg in p):
                    o.add(Not(And(Bool(p[0]),Bool(p[1]))))
                else:
                    o.add_soft(Not(And(Bool(p[0]),Bool(p[1]))))

        # Add installed packages as soft constraints
        for pkg in installed_pkgs:
            o.add_soft(Bool(pkg))

        # Check for satisfiability
        if o.check() == sat:
            model = o.model()
            result = {Bool(pkg): model.eval(Bool(pkg)) == True for pkg in installed_pkgs}
            result.update({Bool(pkg): model.eval(Bool(pkg)) == True for pkg in tgt_pkgs})
            return result
        else:
            return None