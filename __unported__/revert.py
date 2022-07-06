#!/usr/bin/env python
import os

for root, dirs, files in os.walk("."):
    for file in files:
        if root.endswith("data") and file.endswith(".bak"):
            os.rename(os.path.join(root, file), os.path.join(root, file[:-4]))
