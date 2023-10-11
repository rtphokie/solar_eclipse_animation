import unittest
from zoneinfo import ZoneInfo

import numpy as np
from skyfield import api
import dateutil
from solar_eclipse_animation.skyfieldcalcs import circumstances, eclipse_fraction

from solar_eclipse_animation.imaging import compositing
from solar_eclipse_animation.main import main, decdeg2dms
from solar_eclipse_animation.skyfieldcalcs import circumstances
from pprint import pprint
ts = api.load.timescale()
from timezonefinder import TimezoneFinder
tf = TimezoneFinder()

class MyTestCase(unittest.TestCase):
    def test_skyfield(self):
        # Start of partial eclipse (C1) : 	2023/10/14	15:56:02.8	+43.5°	157.7°	285°	01.9
        year = 2023
        month = 10
        day = 14
        lat = 35.7796
        lon = -78.6382
        ele = 99
        c1, c2, mid, c3, c4, df = circumstances(ts.utc(year, month, day), lat, lon, ele=ele)
        print(c1['utc_iso'])
        print(f"{c1['sun_r']:.4f} {c1['moon_r']:.4f}")
        print(
            f"sun {decdeg2dms(c1['sun_alt'])} {decdeg2dms(c1['sun_az'])} moon {decdeg2dms(c1['moon_alt'])} {decdeg2dms(c1['moon_az'])}")

    def test_comp(self):
        moon_alt_delta_deg = 0.6061575008073419
        moon_az_delta_deg = -0.2797259658417204
        compositing(label_ll=f"alt {moon_alt_delta_deg:.2f} az {moon_az_delta_deg:.2f}",
                    title='test', sun_radius=.26, moon_radius=.24,
                    moon_alt_delta_deg=moon_alt_delta_deg,
                    moon_az_delta_deg=moon_az_delta_deg,
                    imagedir='/Users/trice/PyCharmProjects/sandbox/solar_eclipse_animation/images')

    def test_Raleigh(self):
        main()

    def test_nashville(self):
        main(name='Nashville, TN', lat=36.1897, lon=-86.75875)

    def test_sev(self):
        main(name='Sevier, UT', lat=38.57264, lon=-112.24428)

    def test_alb(self):
        main(name='Albequeque, NM', lat=35.09868, lon=-106.65098)

    def test_Yak(self):
        main(name='Yakima, WA', lat=46.21, lon=-119.17)

    def test_fraction(self):
        from solar_eclipse_animation.skyfieldcalcs import eclipse_fraction
        foo = eclipse_fraction(0.001384,
                               0.253048,
                               0.267121,
                               )
        print(foo)
        foo2 = intersection_area(0.001384,
                                 0.253048,
                                 0.267121,
                                 )
        print(foo2)

    def test_images(self):
        import configparser
        config = configparser.ConfigParser()
        config.read('../astroreport.ini')
        sections = config.sections()
        cities={}
        for section in sections:
            cities[config[section]['city']]={'lat': float(config[section]['lat']),
                                            'lon': float(config[section]['lon']),
                                             'ele': int(config[section]['ele'])
                                            }
        from PIL import Image, ImageDraw, ImageFont
        fontsize = 100
        myFont = ImageFont.truetype('../fonts/BebasNeue-Bold.ttf', fontsize)


        for city, data in cities.items():
            if 'Richmond' not in city:
                continue
            print(city)
            pprint(data)
            # timezone = tf.timezone_at(lng=data['lon'], lat=data['lat'])
            main(name=city, lon=data['lon'], lat=data['lat'])

            # c1, c2, mid, c3, c4, df = circumstances(ts.utc(2023, 10, 14), data['lat'], data['lon'], ele=data['ele'])
            # event=mid
            # time_utc_dt = dateutil.parser.isoparse(event['utc_iso'])
            # time_local_dt = time_utc_dt.astimezone(ZoneInfo(timezone))
            # local_time = time_local_dt.strftime('%-I:%M %p %Z')
            # sun_alt = event['sun_alt']
            # sun_az = event['sun_az']
            # moon_alt = event['moon_alt']
            # moon_az = event['moon_az']
            # obs = eclipse_fraction(event['separation'], event['moon_r'], event['sun_r'])
            # dirname = compositing(label_ll=f"{local_time}", label_lr=f"Maximum Eclipse {obs * 100:.1f}%",
            #                       title=city, iso=time_local_dt.strftime('%Y%m%dT%H%M%S'),
            #                       sun_radius=event['sun_r'], moon_radius=event['moon_r'],
            #                       moon_alt_delta_deg=sun_alt - moon_alt,
            #                       moon_az_delta_deg=moon_az - sun_az,
            #                       imagedir='/Users/trice/PyCharmProjects/sandbox/solar_eclipse_animation/images')
            #

def obs(d, R, r):
    return (1 - intersection_area(d, R, r))


def intersection_area(d, R, r):
    """Return the area of intersection of two circles.

    The circles have radii R and r, and their centres are separated by d.

    """

    if d <= abs(R - r):
        # One circle is entirely enclosed in the other.
        return np.pi * min(R, r) ** 2
    if d >= r + R:
        # The circles don't overlap at all.
        return 0

    r2, R2, d2 = r ** 2, R ** 2, d ** 2
    alpha = np.arccos((d2 + r2 - R2) / (2 * d * r))
    beta = np.arccos((d2 + R2 - r2) / (2 * d * R))
    overlap = r2 * alpha + R2 * beta - 0.5 * (r2 * np.sin(2 * alpha) + R2 * np.sin(2 * beta))
    return overlap


def find_d(A, R, r):
    """
    Find the distance between the centres of two circles giving overlap area A.

    """

    # A cannot be larger than the area of the smallest circle!
    if A > np.pi * min(r, R) ** 2:
        raise ValueError("Intersection area can't be larger than the area"
                         " of the smallest circle")
    if A == 0:
        # If the circles don't overlap, place them next to each other
        return R + r

    if A < 0:
        raise ValueError('Negative intersection area')

    def f(d, A, R, r):
        return intersection_area(d, R, r) - A

    a, b = abs(R - r), R + r
    d = brentq(f, a, b, args=(A, R, r))
    return d


if __name__ == '__main__':
    unittest.main()
