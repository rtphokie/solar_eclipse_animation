from zoneinfo import ZoneInfo
import os

import dateutil
from skyfield import api
from timezonefinder import TimezoneFinder
from tqdm import tqdm

from solar_eclipse_animation.imaging import compositing
from solar_eclipse_animation.skyfieldcalcs import circumstances, eclipse_fraction

# reusable objects
ts = api.load.timescale()
tf = TimezoneFinder()


def decdeg2dms(dd):
    mult = -1 if dd < 0 else 1
    mnt, sec = divmod(abs(dd) * 3600, 60)
    deg, mnt = divmod(mnt, 60)
    return int(mult * deg), int(mult * mnt), mult * sec


def main(name='Raleigh, NC', lat=35.78255, lon=-78.63899, year=2023, month=10, day=14, ele=97):
    # def main(name='Nashville, TN', lat=36.1627, lon=-86.7816, year=2023, month=10, day=14, ele=0):
    timezone = tf.timezone_at(lng=lon, lat=lat)

    c1, c2, mid, c3, c4, df = circumstances(ts.utc(year, month, day), lat, lon, ele=ele)
    df_eclipsed = df[(df.eclipse_fraction > 0)]
    aaa = df[(df.eclipse_fraction > 0)]
    aaa = aaa[['utc_iso', 'separation', 'moon_r', 'sun_r', 'eclipse_fraction']]
    aaa.to_csv('dump.csv')

    # for event, msg in zip([c1, c2, mid, c3, c4], ['start of partial eclipse', 'start of annular eclipse', 'maximum eclipse', 'end of annular eclipse', 'end of partial eclipse']):
    pbar = tqdm(total=df_eclipsed.shape[0])
    dirname='unknown'
    for n, event in df_eclipsed.iterrows():
        msg = ' '
        pbar.update(1)
        # if n % 5 != 0:
        #     continue
        obs = event['eclipse_fraction']
        sun_alt = event['sun_alt']
        sun_az = event['sun_az']
        moon_alt = event['moon_alt']
        moon_az = event['moon_az']
        # print(f"moon {moon_alt:.2f} {moon_az:.2f}")

        time_utc_dt = dateutil.parser.isoparse(event['utc_iso'])
        time_local_dt = time_utc_dt.astimezone(ZoneInfo(timezone))
        local_tz_short = time_utc_dt.strftime('%Z')[0] + time_local_dt.strftime('%Z')[-1]
        local_time = time_local_dt.strftime('%-I:%M %p %Z')
        local_date = time_local_dt.strftime('%a %b %-d, %Y')
        obs = eclipse_fraction(event['separation'], event['moon_r'], event['sun_r'])

        if event['utc_iso']==c1['utc_iso']:
            msg='start of partial eclipse'
        elif c2 is not None and event['utc_iso']==c2['utc_iso']:
            msg='start of annular eclipse'
        elif event['utc_iso']==mid['utc_iso']:
            msg='maximum eclipse'
        elif c3 is not None and event['utc_iso']==c3['utc_iso']:
            msg='end of annular eclipse'
        elif event['utc_iso']==c4['utc_iso']:
            msg='end of partial eclipse'
        else:
            msg=''

        dirname = compositing(label_ll=f"{local_time}", label_lr=f"{msg} {obs * 100:.1f}%",
                    title=name, iso=time_local_dt.strftime('%Y%m%dT%H%M%S'),
                    sun_radius=event['sun_r'], moon_radius=event['moon_r'],
                    moon_alt_delta_deg=sun_alt - moon_alt,
                    moon_az_delta_deg=moon_az - sun_az,
                    imagedir='/Users/trice/PyCharmProjects/sandbox/solar_eclipse_animation/images')
    # print(dirname)
    os.chdir(dirname)
    cmd = f'''ffmpeg  -pattern_type glob -i "*.png" -c:v libx264 -pix_fmt yuv420p "{name.replace(' ', '_')}_ASE20231014.mp4"'''
    # cmd = f'''ffmpeg -f concat -i input.txt -c:v libx264 -pix_fmt yuv420p -y "{name.replace(' ', '_')}_ASE20231014.mp4"'''
    print(cmd)
    os.system(cmd)
