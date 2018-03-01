#!/usr/bin/env python
import sys
import os
from os.path import join as opj, basename
import re

outdir = "."
def get_crop(filename):
    # by default we will do cockpit one
    crop = re.search('(?P<basename>.*?)(_crop-(?P<crop>[^.]*))?\.(?P<ext>[^.]+?$)', filename)
    groups = crop.groupdict()
    if 'crop' in groups:
        #print("CROP: %s" % str(groups))
        crop = groups['crop']
    crop_ = {
      "dot+save": '736x577+196+890',
      "patientreg": '1030x710+100+940',
      "patientconf": '1074x857+67+868',
      "exam": '505x450+0+1348',
      "exam+menu": '505x801+0+997',
    }.get(
        crop, '639x511+196+890'  # default is the cockpit window
    )
    filename_ = "{basename}.{ext}".format(**groups)
    return crop_, filename_

for origfile in sys.argv[1:]:
   crop, filename = get_crop(basename(origfile))
   assert origfile != filename, "specify file under orig"
   cmd = "convert {origfile} -crop {crop} {filename}".format(**locals())
   print("Running {}".format(repr(cmd)))
   os.system(cmd)
