# -*- coding: utf-8 -*-
"""
Created on Tue May 15 22:29:06 2018

@author: Lianxin Zhang

This is the global variable for the information of flag, heading, PWM...
"""


def _init():#初始化
    global _global_dict
    _global_dict = {}


def set_value(key,value):
    _global_dict[key] = value


def get_value(key,defValue=None):
    try:
        return _global_dict[key]
    except KeyError:
        return defValue

_init()