#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
 Copyright (C) 2014 KodeKarnage

 This Program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 2, or (at your option)
 any later version.

 This Program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with XBMC; see the file COPYING.  If not, write to
 the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
 http://www.gnu.org/copyleft/gpl.html
'''

# Standard modules
import sys
import os


# XBMC modules
import xbmc
import xbmcgui
import xbmcaddon

# Custom modules
sys.path.append(xbmc.translatePath(os.path.join(xbmcaddon.Addon().getAddonInfo('path'), 'resources','lib')))
from thetvdbapi import TheTVDB
import lazy_tools   as T

api = TheTVDB()

all_show_ids	       = {"jsonrpc": "2.0",
						"method": "VideoLibrary.GetTVShows",
						"params": {
							"properties": 
								["title", "lastplayed"]},
						"id": "1"}

# query all all_shows 
all_shows = T.json_query(all_show_ids)

all_shows = all_shows.get('tvshows', [])

for show in all_shows:

	name = show.get('title', '')

	show_tup = api.get_matching_shows(name)

	print show_tup

	show_tvdbid = show_tup[0][0]

	print api.get_show_and_episodes(show_tvdbid)

	break


# OPTIONS
#	sub episodes AFTER the first one I have
#	sub episodes BEFORE the latest one I have

#	PREFIX for display
