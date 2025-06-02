import unittest
from z3 import *
from package_manager import *

# ######################
# example package : (dependencies, size) dictionary
# To visualize the dependency graph, refer to  "dependency.pdf"

# ######################
packages = {
    "X": ([["A"],["E","C"]],1),
    "A": ([["E"],["H", "Y"]],1),
    "E": ([["B"],["Z", "Y"]],2),
    "C": ([["A","K"]],4),
    "H": ([],3),
    "Y": ([],3),
    "Z": ([],3),
    "K": ([],3),
    "B": ([],3),
    "M": ([["J"]],3),
    "J": ([],13),
    "O": ([["K","P"]],23),
    "P": ([],15),
    
}

# ######################
# example conflicts
# ######################
conflicts = [
     ("B", "J"),
     ("Z", "J"),
     ("K", "Z")
]

# ######################
# a repository is just a pair of packages and conflicts
# ######################
repo = (packages, conflicts)

def tester(expected, actual):
        s = Solver()
        s.add(Not(actual==expected))
        return s.check()

class TestPack(unittest.TestCase):
    def setUp(self):
       self.pack = PackageManager(repo)

    def test_depsE(self):
        actual = self.pack.getDeps("E")
        expected = Implies(Bool('E'),And(Bool('B'),Or(Bool('Z'),Bool('Y'))))
        self.assertEqual(tester(expected, actual), unsat)

    def test_depsA(self):
        actual = self.pack.getDeps("A")
        expected = Implies(Bool('A'),And(And(Bool('E'), Implies(Bool('E'), And(Bool('B'), Or(Bool('Z'), Bool('Y'))))), Or(Bool('H'), Bool('Y'))))
        self.assertEqual(tester(expected, actual), unsat)
    
    def test_depsC(self):
        actual = self.pack.getDeps("C")
        expected=Implies(Bool('C'),Or(And(Bool('A'),Implies(Bool('A'),And(And(Bool('E'),Implies(Bool('E'),And(Bool('B'), Or(Bool('Z'), Bool('Y'))))), Or(Bool('H'), Bool('Y'))))), Bool('K')))
        self.assertEqual(tester(expected, actual), unsat)
   
    def test_depsK(self):
        actual = self.pack.getDeps("K")
        expected = True
        self.assertEqual(tester(expected, actual), unsat)
    
    def test_depsM(self):
        actual = self.pack.getDeps("M")
        expected = Or(Bool('J'), Not(Bool('M')))
        self.assertEqual(tester(expected, actual), unsat)
    
    def test_depsX(self):
        actual = self.pack.getDeps("X")
        expected = Or(Not(Bool('X')),And(Bool('A'),Or(Not(Bool('A')),And(Bool('E'), Or(Not(Bool('E')), And(Bool('B'), Or(Bool('Z'),
                   Bool('Y')))), Or(Bool('H'), Bool('Y')))), Or(And(Bool('E'), Or(Not(Bool('E')), And(Bool('B'), 
                   Or(Bool('Z'), Bool('Y'))))), And(Bool('C'), Or(Bool('K'), And(Bool('A'), Or(Not(Bool('A')), 
                   And(Bool('E'), Or(Not(Bool('E')), And(Bool('B'), Or(Bool('Z'), Bool('Y')))), Or(Bool('H'), Bool('Y'))))), Not(Bool('C')))))))
        self.assertEqual(tester(expected, actual), unsat)
   
    def test_conflictBJ(self):
        actual = self.pack.getConflicts(repo)
        expected = Not(And(Bool('B'), Bool('J')))
        self.assertEqual(tester(expected, actual), sat)

    def test_can_installX(self):
        actual = self.pack.can_install(repo, "", "X")
        expected = sat
        self.assertEqual(actual, expected)

    def test_can_installA(self):
        actual = self.pack.can_install(repo, "A", "X")
        expected = sat
        self.assertEqual(actual, expected)

    def test_can_installBJ(self):
        actual = self.pack.can_install(repo, "B", "J")
        expected = unsat
        self.assertEqual(actual, expected)

    def test_can_installBM(self):
        actual = self.pack.can_install(repo, "B", "M")
        expected = unsat
        self.assertEqual(actual, expected)

    def test_can_installZM(self):
        actual = self.pack.can_install(repo,"Z", "M")
        expected = unsat
        self.assertEqual(actual, expected)

    def test_can_installs_1(self):
        actual = self.pack.can_installs(repo,["Z"], ["M"])
        expected = unsat
        self.assertEqual(actual, expected)

    def test_can_installs_1(self):
        actual = self.pack.can_installs(repo,["E","A"], ["C"])
        expected = sat
        self.assertEqual(actual, expected)

    def test_can_installs_2(self):
        actual = self.pack.can_installs(repo,["E"], ["M"])
        expected = unsat
        self.assertEqual(actual, expected)

    def test_can_installs_2(self):
        actual = self.pack.can_installs(repo,["C"], ["M"])
        expected = sat
        self.assertEqual(actual, expected)

    def test_can_installs_3(self):
        actual = self.pack.can_installs(repo,["A","C"], ["O"])
        expected = sat
        self.assertEqual(actual, expected)

if __name__ == '__main__':
    unittest.main()
