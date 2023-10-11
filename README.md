# solar_eclipse_animation

Creates an MP4 animation of the Oct 14, 2023 annular solar eclipse

## Requirements

* ffmpeg for assembling png still frames into an animation
* (optional) install HandBrake CLI 

## Some things you might have to tweak in non-linux, non-mac environments
* This code assumes the ``/var/data`` directory exists for downloading (and most importantly) reusing ephemeris from JPL.  They're big files so storing them centrally makes more sense than downloading them to the local directory of each project using them.  Skyfield will fetch them for you the first time.

## Getting started

1. clone this repo  
   ``git clone https://github.com/rtphokie/solar_eclipse_animation.git``
1. create a virtual environment  
``python3 -m venv venv``
1. upgrade pip if necessary  
``pip --upgrade pip``
1. install the necessary packages
``pip install -r pip``
1. generate an animation for the Oct 14, 2023 eclipse:  
``
python3 solar_eclipse_animation 35 -78
``

## Usage
```
usage: solar eclipse animation [-h] [--name NAME] [--fontfile FONTFILE]
                               [date] latitude longitude

Calculates the circumstances for a given solar eclipse for a given set of
coordinates. Creates frame for each minute, pausing at the beginning and end
of the partial eclipse, maximum eclipse, and (for coordinates inside the
annular or partial path) at the beginning and end of annularity or totality

positional arguments:
  date                 date of the solar eclipse YYYYMMDD (default 20231014)
  latitude             decimal latitude in degrees (example: 35.78)
  longitude            decimal longitude in degrees (example: -78.664

options:
  -h, --help           show this help message and exit
  --name NAME          subdirectory name, defaults to "lat__lon"
  --fontfile FONTFILE  path to true type font file, a (local time) clock to
                       the lower left and percent obscuration to the lower
                       right

Note: accuracy is withing a few seconds of tables published on the NASA GSFC
eclipse site. That accurracy is limited by the ephemeris used and gets worse
for larger values of delta T
```

References: 
* https://eclipse.gsfc.nasa.gov/eclipse.html
* Astronomical Algorithms 2nd Edition, by Jean Meeus, ISBN 978-0943396613



