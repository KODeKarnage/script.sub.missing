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

QUERY_all_show_ids	    = {"jsonrpc": "2.0",
						"method": "VideoLibrary.GetTVShows",
						"params": {
							"properties": 
								["title"]},
						"id": "1"}

QUERY_all_episodes      = {"jsonrpc": "2.0",
						"method": "VideoLibrary.GetEpisodes",
						"params": {
							"properties": 
								["season","episode","playcount","file"],
							"tvshowid": "PLACEHOLDER"},
						"id": "1"}

QUERY_rescan			 = {"jsonrpc": "2.0",
							"method": "VideoLibrary.Scan",
							"params": {
								"directory": "PLACEHOLDER",
								"media": "video"},
							"id": 1
							}
QUERY_clean				 = {"jsonrpc": "2.0",
							"method": "VideoLibrary.Clean",
							"id": 1
							}							

QUERY_change_name		 = {"jsonrpc": "2.0",
							"method": "VideoLibrary.SetEpisodeDetails",
							"params": {
								"episodeid": "PLACEHOLDER",
								"title ": "PLACEHOLDER"},
							"id": 1
							}	


# query all all_shows 
all_shows = T.json_query(QUERY_all_show_ids)

all_shows = all_shows.get('tvshows', [])

print str(all_shows)

for show in all_shows:

	idx = show.get('tvshowid', '')

	QUERY_all_episodes['params']['tvshowid'] = idx

	all_shows = T.json_query(QUERY_all_episodes)

	print all_shows

# 	show_tup = api.get_matching_shows(name)

# 	print show_tup

# 	show_tvdbid = show_tup[0][0]

# 	print api.get_show_and_episodes(show_tvdbid)[1]

# 	break


# # OPTIONS
# #	sub episodes AFTER the first one I have
# #	sub episodes BEFORE the latest one I have

# #	PREFIX for display















# XBMC modules
import xbmc
import xbmcaddon

# Standard modules
import os
import shutil
import time
import re
import sys

# Custom modules
import lazytools as T
log = T.logger()




class monitor(xbmc.Monitor):

	def __init__(self, main):
		self.main = main

	def onDatabaseUpdate(self):
		if video:
			main.onLibrary_scan_complete()

	def onSettingsChanged(self):
		MAIN.refresh_setings()


class Main:

	def __init__(self):

		'''
		self.show_dict = {
				SHOWID: {
					'TVDBID': @@@@, 
		 			'name': @@@@, 
		 			'local_episodes': { (season, episode) : episodeID, ..., ...},
		 			'TVDB_episodes'	: [ (season, episode), , ..., ...],
		 			'missing_episodes'  : [ (season, episode), , ..., ...],
		 			}
		 		}
		'''

		self.show_dict = {}

		# a list of the entries to remove from the library
		# this will only be populated when stubs are slated for removal
		self.remove_these = []

		# create TVDB api
		self.TVDB = THETVDBAPI()

		self.create_show_dict()

		# create database and settings monitor
		self.monitor = monitor()

	# MAIN 
	def onLibrary_scan_complete(self):
		'''
		# check for any new shows
			process any that are new

		# check all stubs to see if they have epid, if not then add them


		'''

		get all episodes
		GET ALL STUB EPS IN THE LIBRARY

		CHECK THE FILENAMES AGAINST SELF.remove_these
		REMOVE THE ITEMS THAT ARE IN THAT LIST 

		FOR ALL THE OTHERS, CHECK THE NAME IN THE LIBRARY, APPEND THE PREFIX IF NEEDED 

		self.change_name_in_library(epid, new_name)


	# MAIN
	def retrieve_settings(self):
		
		__addon__        = xbmcaddon.Addon('script.missing.tv')
		__setting__      = __addon__.getSetting


		self.sub_location = __setting__('sub_location')
		self.sub_prefix   = __setting__('prefix')

		if self.sub_location == 'default':
			self.ADDON_DATA_FOLDER = xbmc.translatePath('special://userdata')
			self.SUB_FOLDER = os.path.join(self.ADDON_DATA_FOLDER, 'Missing_TV')
		else:
			self.SUB_FOLDER = self.sub_location


		# check if the SUB_FOLDER exists, create if it doesnt
		if not os.path.exists(self.SUB_FOLDER):
			os.mkdirs(self.SUB_FOLDER)

	# MAIN		
	def threader(self, function, arguments):
		''' creates x number of threads to process the arguments in the function '''

	# SHOW DICT
	def create_show_dict(self, showid = None):
		''' 
		# self.show_dict = {
		#			SHOWID: {
		#			'TVDBID': @@@@, 
		# 			'name': @@@@, 
		# 			'local_episodes': { (season, episode) : episodeID, ..., ...},
		# 			'TVDB_episodes'	: [ (season, episode), , ..., ...],
		# 			'missing_episodes'  : [ (season, episode), , ..., ...],
		# 			}}
		'''

		# get showid, name from JSON
		# query get all_shows 
		all_shows = T.json_query(QUERY_all_show_ids)

		all_shows = all_shows.get('tvshows', [])

		for show in all_shows:

			name = show.get('title', '')
			show_id = show.get('tvshowid', '')

			self.show_dict[show_id] = {}
			self.show_dict[show_id]['name'] = name

			# get local_episodes from JSON, process into local_episodes dict
			all_episodes = T.json_query(QUERY_all_episodes)
			self.process_show_info(all_episodes, show_id)


			# get TVDB ID from api
			self.retrieve_TVDBID(show_id, name)

			# get TVDB episodes, process into TVDB_episodes
			self.retrieve_TVDB_info(show_id)


		## once created ##

		# find the missing episodes
		self.identify_missing()

		# create the subsitutes
		self.create_substitutes()

		# remove unneeded stubs from the library
		T.json_query(QUERY_clean)

		# call for a refresh of the SUB_FOLDER
		self.request_library_update()



	# SHOW DICT
	def process_show_info(self, local_show_dict, show_id):
		''' create or update entry in local_show_dict '''

		episodes = local_show_dict.get('episodes', [])

		local_episodes = {}

		for ep in episodes:
			s    = ep.get('season', False)
			e    = ep.get('episode', False)
			epid = ep.get('episodeid', False)

			if all([s, e, epid]):
				local_episodes[(s, e)] = epid

		self.show_dict[show_id]['local_episodes'] = local_episodes

	# SHOW DICT
	def retrieve_TVDBID(self, local_id, showname):
		''' use showname to get TVDBID '''

		show_tup = self.TVDB.get_matching_shows(name)

		try:
			show_tvdbid = show_tup[0][0]

			if show_tvdbid:

				self.show_dict[local_id]['TVDBID'] = show_tvdbid

				return True

		except:
			return None

	# SHOW DICT
	def retrieve_TVDB_info(self, local_id):
		''' retrieve all episode info for a specific show '''

		show = self.show_dict.get(local_id, False)

		# if the show isnt found then abandon effort
		if not show:
			return

		TVDBID = self.show_dict.get('TVDBID', False)

		# the tvdbid doesnt exist, try to populate it
		if not TVDBID:
			show_name = self.show_dict.get('name', False)

			# if there is no show name, then abandon the effort
			if not show_name:

				return

			# get the tvdbid
			self.retrieve_TVDBID(local_id, show_name)

			# try populating the info again
			self.retrieve_TVDB_info(local_id)

		else:

			# get the show info
			info = self.TVDB.get_show_and_episodes(TVDBID)

			# if info doesnt have episode info then abort
			try:
				# process the show info
				if info:
					self.process_tvdb_info(local_id, info[1])
			except:
				return

	# SHOW DICT
	def process_tvdb_info(self, local_id, info):
		''' Converts the tvdb info into the show dict entry TVDB_episodes '''

		TVDB_episodes = []
		for episode in info:
			e = episode.get('EpisodeNumber', False)
			s = episode.get('SeasonNumber', False)
			if all([e,s]):
				TVDB_episodes.append((s, e))

		self.show_dict[local_id] = TVDB_episodes

	# SHOW DICT
	def identify_missing(self, showid = None):
		''' compares the TVDB episodes to the local episodes 
			and updates show dict with all missing eps '''

		# allow for single show update
		pairs = single_or_all(showid)

		for k, v in pairs:
			
			local_eps  = set(v.get('local_episodes',{}).keys())
			remote_eps = set(v.get('TVDB-Episodes',[]))

			self.show_dict[k]['missing_episodes'] = list(remote_eps.difference(local_eps))

	# SHOW DICT
	def single_or_all(self, showid):
		''' allow for single show, or complete update '''

		if showid:
			pairs = (showid, self.show_dict.get(showid,{}))
		else:
			pairs = self.show_dict.iteritems()

		return pairs

	# STUBS
	def create_substitutes(self, showid = None):
		''' creates/updates the substitutes folder in addondata '''

		# allow for single show update
		pairs = single_or_all(showid)

		# get the current structure and population of sub folder
		subs = self.retrieve_subs()

		# get just the names of the folders (tvshows)
		existing_sub_folders = set(subs.keys())

		# get the list of the folders that are needed
		needed_sub_folders = set([v['name'] for k, v in pairs if v.get('name', False)])

		# create a list of the folders that need to be created
		create_these_folders  = needed_sub_folders.difference(existing_sub_folders)

		# create a list of the folders that need to be destroyed
		destroy_these_folders = destroy_these_folders.difference(needed_sub_folders)		

		# create the folders
		self.create_folders(create_these_folders)

		# only destroy folders if this ISNT a single show update
		if not showid:
			self.destroy_folders(destroy_these_folders)

		# cycle through the shows and create the episode stubs
		for k, v in pairs:

			self.create_or_delete_stubs(k, v, subs)

	# STUBS
	def retrieve_subs(self):
		''' returns a dict of {showname : [(season, episode), ...]}
			for each sub-folder in addondata '''

			subs_dict = {}

		for showname in os.walk(self.SUB_FOLDER):

			for stub in os.listdir(showname):

				p = r'Missing_Sub_s(\d+)e(\d+).avi'
				match = re.search(p, stub)

				if not match:
					continue

				subs_dict['showname'] = (match.group(1), match.group(2))

		return subs_dict

	# STUBS
	def create_folders(self, namelist):
		''' creates the folders in the namelist in the addondata directory '''
		for name in namelist:
			path = os.path.join(self.SUB_FOLDER, name)
			os.mkdir(path)

	# STUBS
	def destroy_folders(self, namelist):
		''' destroys the folders in the namelist from the addondata directory '''	

		for name in namelist:
			path = os.path.join(self.SUB_FOLDER, name)

			self.remove_these += os.listpath(path)

			shutil.rmtree(path)

	# STUBS
	def create_or_delete_stubs(self, k, v, subs):

		# get the missing episode tuples
		missing_episodes = set(v.get('missing_episodes', []))

		# get the existing episode tuples
		existing_stubs = set(subs.values())

		# delete the unneeded stubs
		delete_these_stubs = existing_stubs.difference(missing_episodes)

		for stub in delete_these_stubs:

			epid = self.remove_stub(stub)

		# create the missing stubs
		create_these_stubs = missing_episodes.difference(existing_stubs)

		for episode in create_these_stubs:
			
			self.add_stub(episode)

	# STUBS
	def remove_stub(self, stub):
		ep_name = 'Missing_Sub_s{}e{}.avi'.format(stub[0], stub[1])

		path = os.path.join(self.SUB_FOLDER, k, ep_name)		

		os.remove(path)

		self.remove_these.append(path)

	# STUBS
	def add_stub(self, episode):
		''' create_stub using season and episode, write the epid into the file '''

		ep_name = 'Missing_Sub_s{}e{}.avi'.format(episode[0], episode[1])

		stub = os.path.join(self.SUB_FOLDER, k, ep_name)

		with open(stub, 'w') as f:
			pass

	# STUBS
	def update_stub_epids(self):
		''' runs immediately after a library update, 
			writes the epid into each stub '''

		pass

	# STUBS
	def request_library_update(self):
		''' Request a library update of the specific addondata folder '''

		QUERY_rescan['params']['directory'] = self.SUB_FOLDER
		T.json_query(QUERY_rescan)

	# LIBRARY
	def clean_library(self):
		''' removes the episode from the library '''

		T.json_query(QUERY_clean)

	# LIBRARY		
	def change_name_in_library(self, epid, new_name):
		''' find all the stub items in the library and rename them using the 
			user selected prefix self.sub_prefix '''

		QUERY_rescan['params']['episodeid'] = epid
		QUERY_rescan['params']['title'] = new_name

		T.json_query(QUERY_rescan)



if ( __name__ == "__main__" ):

	Main()

	while not xbmc.abortRequested:

		xbmc.sleep(10)

	del Main



