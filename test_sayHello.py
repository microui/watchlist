import unittest
from module_foo import sayHello


class SayHelloTestCase(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_sayHello(self):
        sv = sayHello()
        self.assertEqual(sv, 'hello')

    def test_sayHello_to_somebody(self):
        sv = sayHello('lily')
        self.assertEqual(sv, 'hello lily')


if __name__ == '__main__':
    unittest.main()

