import unittest
from math import pi

import ephem


def main():
    gatech = ephem.Observer()
    gatech.lon = '-78.63899'
    gatech.lat = '35.78255'
    gatech.elevation = 320
    gatech.date = '2023/10/14 15:55:47'
    v = ephem.Sun(gatech)
    print(f"{(v.alt*180.0/pi):.4f}", end=' ')
    print(f"{(v.az*180.0/pi):.4f}")
    v = ephem.Moon(gatech)
    print(f"{(v.alt*180.0/pi):.4f}", end=' ')
    print(f"{(v.az*180.0/pi):.4f}")


class MyTestCase(unittest.TestCase):
    def test_something(self):
        main()


if __name__ == '__main__':
    unittest.main()
