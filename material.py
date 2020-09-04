#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : material.py
# Author            : tzhang
# Date              : 28.10.2019
# Last Modified Date: 17.08.2020
# Last Modified By  : tzhang

# a library for material properties

# air properties (constant or calculated by ideal gas equation)
class air:
    def __init__(self):
        self.density = 0.0

    # constant air density 
    def constant(self):
        density = 1.204 # in kg/m^3, air density at 20 degC and 1 atm

        self.density = self.density+density

    def ideal(self):
        pass
