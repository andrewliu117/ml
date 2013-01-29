#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Pegasos inplemented in Python

import sys
import os
import math

G_WEIGHT = []

if __name__== "__main__":
    
    for i in range(32 * 32):
        G_WEIGHT.append(0)

    files = os.listdir(dirpath)
    for file in files:
        img = image()
        img.data = parse_image(dirpath + file)
        img.num = int(file[0])
        img.fn = file
        col.append(img)
