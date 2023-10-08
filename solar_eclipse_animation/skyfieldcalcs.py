import pandas as pd
from skyfield import api
from skyfield.api import Loader
import math
from skyfield.api import wgs84

ts = api.load.timescale()
pd.set_option('display.max_rows', None)

MOON_RADIUS_KM = 1737.4
SUN_RADIUS_KM = 695700


def eclipse_fraction(s, body1, body2):
    '''
    calculates the percentage of the Sun's disk eclipse by the Moon, by calculating the size of the lune in squqre arc seconds
    created for solar eclipses but applicable to any two bodies
    see http://mathworld.wolfram.com/Lune.html
    :param s: separation in degrees
    :param body1: foreground body radius in degrees (Moon)
    :param body2: background body radius in degrees (Sub)
    :return:
    '''
    if s < (body1 + body2):
        a = (body2 + body1 + s) * (body1 + s - body2) * (s + body2 - body1) * (body2 + body1 - s)
        if a > 0:
            lunedelta = 0.25 * math.sqrt(a)
            lune_area = 2 * lunedelta + body2 * body2 * (
                math.acos(((body1 * body1) - (body2 * body2) - (s * s)) / (2 * body2 * s))) - body1 * body1 * (
                            math.acos(((body1 * body1) + (s * s) - (body2 * body2)) / (2 * body1 * s)))
            eclipse_fraction = (1 - (lune_area / (math.pi * body2 * body2)))
        else:
            body2area = math.pi * body2**2
            body1area = math.pi * body1**2
            if body1area > body2area:
                eclipse_fraction=1
            else:
                eclipse_fraction = body1area / body2area
    else:
        eclipse_fraction = 0
    return eclipse_fraction


def apparent_radius(df):
    for label in ['moon', 'sun']:
        if label == 'moon':
            equitorial_radius = MOON_RADIUS_KM
        elif label == 'sun':
            equitorial_radius = SUN_RADIUS_KM
        else:
            raise ValueError(f"unsupported body {label}")
        from numpy import arcsin
        df[f'{label}_r'] = 180.0 / math.pi * arcsin(equitorial_radius / df[f'{label}_dist'])
    df['ratio'] = df.moon_r / df.sun_r


def alt_az_dist(df, body, label):
    alt, az, distance = body.altaz()
    df[f'{label}_alt'] = alt.degrees
    df[f'{label}_az'] = az.degrees
    df[f'{label}_dist'] = distance.km


def circumstances(start, lat, lon, ele=100, end=None, tzstring=None, eph=None):
    '''
    Calculates local circumstances of an eclipse returning datetimes (UTC) for partial
    eclipse contact points (c1 and c4), the moment of maxium eclipse, along with contact
    points for total or annular eclipse as appropraite.

    :param start: the date and time to start searching for an eclipse (datetime, required)
                  when end is None, this is treated as a mid point of a search beginning 00:00 UTC
                  the previous day, ending 00:00 UTC the following day
    :param lat: latitude in degrees (float, positive north, negative south)
    :param lon: longitude in degrees (float, positive east, negative west)
    :param ele: elevation in meters (int)
    :param end: date and time to end search (datetime, default None)
    :param tzstring: converts UTC to local for all datetimes (optional, example 'US/Eastern')
    :return: for each of the 5 circumstances, a pandas series is returned:
        a da

        c1:  beginning of partial eclipse
        c2:  beginning of total or annular eclipse (or None outside of path of totality/annularity)
        mid: moment of maximum eclipse
        c3:  end of total or annular eclipse (or None outside of path of totality/annularity)
        c4:  end of partial eclipse

    '''

    day, hour, minute, month, second, year = get_ints_for_dt_params(start)
    if eph is None:
        eph = load_ephemeris(year)
    if end is None:
        # all we have is a day, so let look across all minutes across a
        # 2 day span centered on noon UTC on the day passed
        time = ts.utc(year, month, day, 12, range(-1440, 1440))
    else:
        # second level resolution across entire eclipse
        timespan_sec = (end - start) * 86400
        startsec = int(second) - 300  # 1 minutes before C1
        endsec = int(second + 300 + timespan_sec)  # 1 minute after C4
        time = ts.utc(year, month, day, hour, minute, range(startsec, endsec))

    # build data frame from those times
    df = pd.DataFrame({
        # 'ordinal': time.toordinal(),  # needed really only for testing against other calculations
        'utc_iso': time.utc_iso(),
        'tt': list(time),
        'jd': list(time.tt),
    })

    place = eph['earth'] + wgs84.latlon(lat, lon, elevation_m=ele)

    # get position of Moon and Sun at each time
    moon = place.at(time).observe(eph['moon']).apparent()
    sun = place.at(time).observe(eph['sun']).apparent()

    # add a column for angular separation of the Moon and Sun
    df['separation'] = moon.separation_from(sun).degrees

    # lets get the lunar and solar distance... that might be useful
    alt_az_dist(df, moon, 'moon')
    alt_az_dist(df, sun, 'sun')

    # and the apparant radius, which provides the ratio, we'll need that
    apparent_radius(df)

    for a in ['sun', 'moon']:
        df[f'{a}_d_dms'] = df.apply(lambda x: decdeg2dms(x[f'{a}_r']*2), axis=1)
        for b in ['alt', 'az']:
            df[f'{a}_{b}_dms'] = df.apply(lambda x: decdeg2dms(x[f'{a}_{b}']), axis=1)
    df['combined_rs']=df.apply(lambda x: x.sun_r + x.moon_r, axis=1)
    df['sepdelta'] = df.apply(lambda x: (x.separation - x.combined_rs)*1000, axis=1)

    # calculate how much of the Sun's disk is eclipsed by the Moon
    df['eclipse_fraction'] = df.apply(lambda x: eclipse_fraction(x['separation'], x['moon_r'], x['sun_r']), axis=1)

    # now we can find when the partial (and if applicable total or annular) eclipses begin and end as well as the midpoint
    c1, c2, mid_eclipse, c3, c4 = contact_points(df)

    if end is None and c1 is not None and False:
        # repeat at second resolution from C1 to C4
        c1, c2, mid_eclipse, c3, c4, df = circumstances(c1.tt, lat, lon, end=c4.tt, eph=eph,
                                                        ele=ele)  # refine at higher resolution
    return c1, c2, mid_eclipse, c3, c4, df


def decdeg2dms(dd):
    mult = -1 if dd < 0 else 1
    mnt, sec = divmod(abs(dd) * 3600, 60)
    deg, mnt = divmod(mnt, 60)
    return f"{int(mult * deg)} {int(mult * mnt)}' {mult * sec:.2f}\""


def get_ints_for_dt_params(start):
    year = int(start.utc_strftime('%Y'))
    month = int(start.utc_strftime('%-m'))
    day = int(start.utc_strftime('%-d'))
    hour = int(start.utc_strftime('%-H'))
    minute = int(start.utc_strftime('%-M'))
    second = int(start.utc_strftime('%-S'))
    return day, hour, minute, month, second, year


def contact_points(df):
    '''
    calculate the 4 contact points plus maximum eclipse, uses ordinal dates to simplify support for negative years
    c1: beginning of partial eclipse
    c2: beginning of total eclipse
    mid eclipse: mid point between c2 and c3, generally the best point to view the corona.
    c3: end of total eclipse
    c4: end of partial eclipse
    :param df: the dataframe containing timestamps separation and fraction of the Sun eclipsed by the Moon
    :return: rows for c1, c2, max_eclipse, c3, c4, and a dataframe sliced with just rows where the Sun is eclipsed.
    '''
    df_eclipsed = df[(df.eclipse_fraction > 0)]
    max_eclipse_fraction = df.eclipse_fraction.max()
    df_eclipsed_max = df[(df.eclipse_fraction == max_eclipse_fraction)]
    df['rdiff']=df.sun_r - df.moon_r
    df['sun_d']=2*df['sun_r']
    df['moon_d']=2*df['moon_r']
    df_anutot = df[(df.sun_r - df.moon_r) > df.separation]
    c1, c2, mid_eclipse, c3, c4 = None, None, None, None, None
    if len(df_eclipsed) > 0:
        c1 = df_eclipsed.loc[df_eclipsed.jd.idxmin()]  # earliest time Sun is obscured
        c4 = df_eclipsed.loc[df_eclipsed.jd.idxmax()]  # latest time
        if len(df_anutot) > 0:
            c2 = df_anutot.loc[df_anutot.jd.idxmin()]  # earliest time when Sun is 100% obscured
            c3 = df_anutot.loc[df_anutot.jd.idxmax()]  # latest  time
        mid_eclipse = df.loc[df.separation.idxmin()]  # time of min separtation
    return c1, c2, mid_eclipse, c3, c4


def load_ephemeris(year=2023):
    load = Loader("/var/data")  # centralize local caching of ephemeris files
    de = 'de430t.bsp'
    # de = 'de440s.bsp'

    eph = load(de)
    # jkl = str(eph).split("\n")
    # print(year, de, jkl[1])

    return eph
