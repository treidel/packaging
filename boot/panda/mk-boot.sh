#!/bin/bash

mkimage -A arm -T script -C none -n "Boot Image" -d boot.script boot.scr
