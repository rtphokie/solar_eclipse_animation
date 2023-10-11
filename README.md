# solar_eclipse_animation

Creates an MP4 animation of the Oct 14, 2023 annular solar clipse

## Requirements

* ffmpeg for assembling png still frames into an animation
* fonts 

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
2. create a ``fonts`` directory, put a true type font of your choice in there.
