#!/usr/bin/env python
import os
import fileinput
from string import maketrans

CEDILLATRANS = maketrans(u'\u015f\u0163\u015e\u0162\u00e2\u00c2\u00ee\u00ce\u0103\u0102'.encode(
    'utf8'), u'\u0219\u021b\u0218\u021a\u00e2\u00c2\u00ee\u00ce\u0103\u0102'.encode('utf8'))

for root, dirs, files in os.walk("."):
    for file in files:
        if (root.endswith("data") or root.endswith("i18n")) and (file.endswith(".csv") or file.endswith(".xml") or file.endswith("ro.po")):
            # print root, file
            for line in fileinput.input(os.path.join(root, file), inplace=1, backup='.bak'):
                print line.translate(CEDILLATRANS).rstrip()
