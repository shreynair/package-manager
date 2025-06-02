import unittest
from z3 import *
from package_manager import *
# ######################
# example package : (dependencies, size) dictionary
# ######################
packages = {
    # browsers
    "firefox": ([["rust"]], 200),
    "edge": ([], 150),
    "chrome": ([["webkit"], ["libpng"]], 100),

    # programming languages
    "gcc": ([["gmp"], ["mpfr"], ["libmpc"]], 1),
    "python3.7": ([], 3),
    "python3.9": ([], 3),
    "llvm": ([["python3.7", "python3.9"], ["gcc"], ["cmake"], ["make"]], 29),
    "rust": ([["python3.7", "python3.9"], ["cmake"], ["gcc"], ["make"]], 23),
    "java11": ([], 21),
    "java13": ([], 21),
    "java15": ([], 21),

    # solvers
    "z3": ([["gcc"], ["glibc"], ["cmake"], ["python3.7"]], 10),
    "cvc4": ([["gmp"], ["antlr"], ["boost"], ["libtool"]], 12),
    "cvc5": ([["gmp"], ["antlr"], ["boost"], ["libtool"]], 13),

    # editors
    "eclipse": ([["java11", "java13", "java15"]], 220),
    "vscode": ([["webkit"], ["glibc"]], 190),
    "vim": ([["gtk"]], 10),
    "emacs": ([["giflib"], ["harfbuzz"], ["gmp"], ["libpng"]], 15),

    # libraries, build tools, and utilities
    "giflib": ([], 2),
    "harfbuzz": ([], 1),
    "libpng": ([], 2),
    "gtk": ([], 3),
    "webkit": ([], 17),
    "gmp": ([], 7),
    "mpfr": ([], 8),
    "libmpc": ([], 3),
    "make": ([], 7),
    "cmake": ([], 5),
    "glibc": ([], 4),
    "boost": ([], 6),
    "libtool": ([], 5),
    "antlr": ([], 12),
}

# ######################
# example conflicts
# ######################
conflicts = [
    ("chrome", "firefox"),
    ("firefox", "edge"),
    ("python3.7", "python3.9"),
    ("cvc4", "cvc5"),
    ("java11", "java13"),
    ("java11", "java15"),
    ("java13", "java15"),
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

    def test_depsChrome(self):
        actual = self.pack.getDeps('chrome')
        expected = Or(Not(Bool('chrome')), And(Bool('webkit'), Bool('libpng')))
        self.assertEqual(tester(expected, actual), unsat)
    
    def test_depsz3(self):
        actual = self.pack.getDeps('z3')
        expected = Or(Not(Bool('z3')), And(Bool('gcc'), Or(Not(Bool('gcc')), And(Bool('gmp'), Bool('mpfr'), Bool('libmpc'))), Bool('glibc'), Bool('cmake'), Bool('python3.7')))
        self.assertEqual(tester(expected, actual), unsat)
    
    def test_depsLLVM(self):
        actual = self.pack.getDeps('llvm')
        expected = Or(Not(Bool('llvm')), And(Or(Bool('python3.7'), Bool('python3.9')), 
                                             And(Bool('gcc'),Or(Not(Bool('gcc')), And(Bool('gmp'), Bool('mpfr'), Bool('libmpc')))), 
                                             Bool('cmake'), Bool('make')))
        self.assertEqual(tester(expected, actual), unsat)
    
    def test_deps_cvc4(self):
        actual = self.pack.getDeps('cvc4')
        expected = Or(Not(Bool('cvc4')), And(Bool('gmp'), Bool('antlr'), Bool('boost'), Bool('libtool')))
        self.assertEqual(tester(expected, actual), unsat)

    def test_Conflict(self):
        actual = self.pack.getConflicts(repo)
        expected = And(Not(And(Bool('chrome'),Bool('firefox'))),Not(And(Bool('firefox'),Bool('edge'))),
                    Not(And(Bool('python3.7'),Bool('python3.9'))),Not(And(Bool('cvc4'),Bool('cvc5'))),
                    Not(And(Bool('java11'),Bool('java13'))),Not(And(Bool('java11'),Bool('java15'))),
                    Not(And(Bool('java13'),Bool('java15'))))
        self.assertEqual(tester(expected, actual), unsat)

    def test_can_install_cvc4(self):
        actual = self.pack.can_install(repo, "cvc4", "cvc5")
        expected = unsat
        self.assertEqual(actual, expected)
    
    def test_can_install_gcc(self):
        actual = self.pack.can_install(repo, "gcc", "z3")
        expected = sat
        self.assertEqual(actual, expected)

    def test_can_install_z3(self):
        actual = self.pack.can_install(repo, "cmake", "z3")
        expected = sat
        self.assertEqual(actual, expected)
    
    def test_can_install_chrome(self):
        actual = self.pack.can_install(repo, "chrome", "vscode")
        expected = sat
        self.assertEqual(actual, expected)

    def test_can_install_rust(self):
        actual = self.pack.can_install(repo, "rust", "gcc")
        expected = sat
        self.assertEqual(actual, expected)   
        
    def test_can_install_cvc4_2(self):
        actual = self.pack.can_installs(repo, [], [("cvc4")])
        expected = sat
        self.assertEqual(actual, expected)   

    def test_can_install_cvc4_firefox(self):
        actual = self.pack.can_installs(repo, [("chrome")], [("firefox")])
        expected = unsat
        self.assertEqual(actual, expected)  

    def test_can_install_cvc5_z3(self):
        actual = self.pack.can_installs(repo, [("z3")], [("cvc4"), ("cvc5")])
        expected = unsat
        self.assertEqual(actual, expected)  
    
    def test_can_install_python(self):
        actual =self.pack.can_installs(repo, [("python3.7")], [("cvc4"), ("python3.9")])
        expected = unsat
        self.assertEqual(actual, expected)  
    
    def test_can_install_java(self):
        actual = self.pack.can_installs(repo, [("java11")], [("eclipse"), ("java13")])
        expected = unsat
        self.assertEqual(actual, expected)  
    

    def test_install_under_constraints_cvc4(self):
        actual = self.pack.install_under_constraint(repo, ["cvc4", "z3", "firefox"],"cvc5")
        self.assertTrue(actual[Bool('firefox')])
        self.assertTrue(actual[Bool('cvc5')])
        self.assertFalse(actual[Bool('cvc4')])
        self.assertTrue(actual[Bool('z3')])

    def test_install_under_constraints_firefox(self):
        actual = self.pack.install_under_constraint(repo, ["chrome", "rust"], "firefox")
        self.assertTrue(actual[Bool('firefox')])
        self.assertTrue(actual[Bool('rust')])
        self.assertFalse(actual[Bool('chrome')])

    def test_install_under_constraints_firefox_rust(self):
        actual = self.pack.install_under_constraint(repo, ["rust", "z3", "emacs"], "firefox")
        self.assertTrue(actual[Bool('firefox')])
        self.assertTrue(actual[Bool('rust')])
        self.assertTrue(actual[Bool('z3')])
        self.assertTrue(actual[Bool('emacs')])

    def test_install_many_under_constraints_cvc4(self):
        actual = self.pack.install_many_under_constraint(repo, ["python3.7", "python3.9"], ["cvc4", "cvc5"])
        self.assertTrue(not actual)  
   
    def test_install_many_under_constraints_cvc4(self):
        actual = self.pack.install_many_under_constraint(repo, ["python3.7", "z3", "java15"], ["java11", "rust"])
        self.assertTrue(actual[Bool('java11')])
        self.assertTrue(actual[Bool('rust')])
        self.assertTrue(actual[Bool('python3.7')])
        self.assertTrue(actual[Bool('z3')])
        self.assertFalse(actual[Bool('java15')])
        
if __name__ == '__main__':
    unittest.main()