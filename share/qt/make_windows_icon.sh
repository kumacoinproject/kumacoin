#!/bin/bash
# create multiresolution windows icon
ICON_DST=../../src/qt/res/icons/PROBE.ico

convert ../../src/qt/res/icons/PROBE-16.png ../../src/qt/res/icons/PROBE-32.png ../../src/qt/res/icons/PROBE-48.png ${ICON_DST}
