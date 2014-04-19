#!/bin/bash
# create multiresolution windows icon
ICON_DST=../../src/qt/res/icons/KumaCoin.ico

convert ../../src/qt/res/icons/KumaCoin-16.png ../../src/qt/res/icons/KumaCoin-32.png ../../src/qt/res/icons/KumaCoin-48.png ${ICON_DST}
