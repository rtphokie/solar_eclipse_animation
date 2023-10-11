import argparse
from main import main

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='solar eclipse animation',
        description='Calculates the circumstances for a given solar eclipse for a given set of coordinates. Creates frame for each minute, pausing at the beginning and end of the partial eclipse, maximum eclipse, and (for coordinates inside the annular or partial path) at the beginning and end of annularity or totality',
        epilog='Note: accuracy is withing a few seconds of tables published on the NASA GSFC eclipse site.  That accurracy is limited by the ephemeris used and gets worse for larger values of delta T.')
    parser.add_argument('date', help='date of the solar eclipse YYYYMMDD (default 20231014)',
                        default=20231014, nargs='?')
    parser.add_argument('latitude', help='decimal latitude in degrees (example:  35.78)')
    parser.add_argument('longitude', help='decimal longitude in degrees (example: -78.664')
    parser.add_argument('--name', help='subdirectory name, defaults to lat/lon')
    parser.add_argument('--fontfile', help='path to true type font file, a (local time) clock to the lower left and percent obscuration to the lower right')
    parser.add_argument('--eph', default='de430t.bsp', help='JPL planetary and lunar ephemerides spice file (default: DE430, which covers 1550 CE to 2650 CE with reasonable delta T)')
    args = parser.parse_args()
    try:
        longitude = float(args.longitude)
        latitude = float(args.latitude)
    except:
        longitude = None
        latitude = None

    if latitude is None or longitude is None or latitude < -90 or latitude > 90 or longitude < -180 or longitude > 180:
        parser.print_help()
        raise ValueError(f"please specify a decimal longitude and latitude")
    if args.name is None:
        name=f"{latitude:.2f}_{longitude:.2f}"
    else:
        name = args.name

    main(name=name, lat=latitude, lon=longitude, font=args.fontfile, ephfilename=args.eph)

