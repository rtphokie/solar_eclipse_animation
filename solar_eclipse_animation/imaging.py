from pathlib import Path
import shutil
import os

from PIL import Image, ImageDraw, ImageFont


# https://note.nkmk.me/en/python-pillow-paste/

def makemask(pixels=1000):
    mask_im = Image.new("L", (pixels, pixels), 0)
    draw = ImageDraw.Draw(mask_im)
    draw.ellipse([0, 0, pixels, pixels], fill=255)
    return mask_im


def compositing( frame=False, title='unknown', filename=None,
                label_ll=None, label_lr=None,
                sun_radius=None, moon_radius=None, iso=None,
                moon_alt_delta_deg=0, moon_az_delta_deg=0,
                fontsize=100, basedir='.',
                imagedir=f'./images'):
    ratio = moon_radius / sun_radius
    moon_az_delta_deg *= .725  # rough adjustment for 2D representation
    imb, imb_size, bg_center, imb_mask = prep_image(f'{imagedir}/bluesky_4k.png',
                                                    None, 1)
    ims, ims_size, sun_center, ims_mask = prep_image(f'{imagedir}/sun.png',
                                                     None, 1)
    imm, imm_size, moon_center, imm_mask = prep_image(f'{imagedir}/newmoon.png',
                                                      ims, ratio)

    imb.paste(ims, (bg_center[0] - sun_center[0], bg_center[1] - sun_center[1]), ims_mask)

    # start with the Moon centered over the Sun
    centered_moon_x = bg_center[0] - moon_center[0]
    centered_moon_y = bg_center[1] - moon_center[1]

    # move the Moon's position based on the difference in altitude and azimum to the Sun, converted from degrees to pixels
    pixels_per_degree = round(ims_size[0] / (sun_radius * 2))
    x_offset = int(moon_az_delta_deg * pixels_per_degree)
    y_offset = int(moon_alt_delta_deg * pixels_per_degree)

    new_moon_x = round(centered_moon_x + (moon_az_delta_deg * pixels_per_degree))
    new_moon_y = round(centered_moon_y + (moon_alt_delta_deg * pixels_per_degree))
    imb.paste(imm, (new_moon_x, new_moon_y), imm_mask)

    border = fontsize * 1.3
    I1 = ImageDraw.Draw(imb)
    if label_ll is not None:
        myFont = ImageFont.truetype(filename, fontsize)
        I1.text((border, imb_size[1] - border), label_ll, font=myFont, fill=(0, 0, 0), anchor='ls')

    if label_lr is not None:
        text = f"{label_lr}"
        I1.text((imb_size[0] - border, imb_size[1] - border), text, font=myFont, fill=(0, 0, 0), anchor='rs')

    atoms=title.split(', ')
    if len(atoms) == 1:
        subdir = title
    else:
        subdir = f"US/{atoms[1]}/{title}"
    if frame:
        fullpath, dirname, filename = get_fullpath(basedir, iso, f"{subdir}/frames", filename=None)
    else:
        fullpath, dirname, filename = get_fullpath(basedir, iso, subdir, filename=None)
    if not os.path.isfile(fullpath):
        imb.save(fullpath, quality=95)

    if label_lr is not None and 'eclipse' in label_lr:
        if 'maximum' in label_lr:
            cnt = 150
        else:
            cnt = 100
        for x in range(cnt):
            dest = shutil.copyfile(fullpath, fullpath.replace('.png', f'{x:04}.png'))
    # fp = open (f"{dirname}/input.txt", 'a')

    return dirname


def get_fullpath(basedir, iso, title, filename=None):
    dirname = f"{basedir}/results/{title}"
    dirname = dirname.replace(',', '').replace(' ', '_')
    Path(dirname).mkdir(parents=True, exist_ok=True)
    if filename is None:
        filename = f"{iso}.png".replace(',', '').replace(' ', '_').replace('%', '')
    else:
        filename = f"{filename}_{iso}.png".replace(',', '').replace(' ', '_').replace('%', '')
    fullpath = f"{dirname}/{filename}"
    return fullpath, dirname, filename


def prep_image(filename, image_reference, ratio, make_mask=True):
    img = Image.open(filename)
    if image_reference is not None:
        new_size = (int(image_reference.size[0] * ratio), int(image_reference.size[1] * ratio))
        img = img.resize(new_size)
    img_size = img.size
    imm_center = (int(img_size[0] / 2), int(img_size[1] / 2))
    if make_mask:
        img_mask = makemask(pixels=img_size[0])
    else:
        img_mask = None

    return img, img_size, imm_center, img_mask
