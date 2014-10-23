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
import os
import shutil
import time
import re
import sys
import json

# XBMC modules
import xbmc
import xbmcaddon
import xbmcgui

# Custom modules
sys.path.append(xbmc.translatePath(os.path.join(xbmcaddon.Addon().getAddonInfo('path'), 'resources','lib')))
import thetvdbapi


QUERY_all_show_ids	    = {
							"jsonrpc": "2.0",
							"method": "VideoLibrary.GetTVShows",
							"params": {
								"properties": 
									["title"]},
							"id": "1"
							}

QUERY_all_episodes      = {
							"jsonrpc": "2.0",
							"method": "VideoLibrary.GetEpisodes",
							"params": {
								"properties": 
									["season","episode","playcount","file"],
								"tvshowid": "PLACEHOLDER"},
							"id": "1"
							}

QUERY_rescan			 = {
							"jsonrpc": "2.0",
							"method": "VideoLibrary.Scan",
							"params": {
								"directory": "PLACEHOLDER",
								"media": "video"},
							"id": 1
							}

QUERY_clean				 = {
							"jsonrpc": "2.0",
							"method": "VideoLibrary.Clean",
							"id": 1
							}							

QUERY_change_name		 = {
							"jsonrpc": "2.0",
							"method": "VideoLibrary.SetEpisodeDetails",
							"params": {
								"episodeid": "PLACEHOLDER",
								"title ": "PLACEHOLDER"},
							"id": 1
							}	

QUERY_remove_episode	 = {
							"jsonrpc": "2.0",
							"method": "VideoLibrary.RemoveEpisode",
							"params": {
								"episodeid": "PLACEHOLDER"},
							"id": 1
							}	

QUERY_filtered_episodes	= {	
							"jsonrpc": "2.0",
							"method": "VideoLibrary.GeEpisodes",
							 "params": 	{
							 	"tvshowid": "PLACEHOLDER",
								"filter": 	{
									"operator": "contains",
									"field": "title",
									"value": "PLACEHOLDER"
											},
								"properties": ["title", "file"]
										},
							"id": 1
							}

def json_query(query):

	xbmc_request = json.dumps(query)
	raw = xbmc.executeJSONRPC(xbmc_request)
	clean = unicode(raw, 'utf-8', errors='ignore')
	response = json.loads(clean)
	result = response.get('result', response)

	return result

class lazy_logger(object):
	''' adds addon specific logging to xbmc.log '''


	def __init__(self):
		self.keep_logs   = True
		self.base_time   = time.time()
		self.start_time  = time.time()


	def post_log(self, message, label = '', reset = False):

		if self.keep_logs:

			new_time    	= time.time()
			gap_time 		= "%5f" % (new_time - self.start_time)
			total_gap  		= "%5f" % (new_time - self.base_time)
			self.base_time  = start_time if reset else self.base_time
			self.start_time = new_time

			xbmc.log(msg = '{} : {} :: {} ::: {} - {} '.format('script.sub.missing', total_gap, gap_time, label, str(message)[:1000]) )

log = lazy_logger().post_log

class Monitor(xbmc.Monitor):

	def __init__(self, main):
		self.main = main

	def onDatabaseUpdate(self):
		if video:
			main.onLibrary_scan_complete()

	def onSettingsChanged(self):
		MAIN.retrieve_settings()


class Main:

	def __init__(self):



		# a list of the entries to remove from the library
		# this will only be populated when stubs are slated for removal
		self.remove_these = []

		# retrieve the addon settings
		self.retrieve_settings()

		# create TVDB api
		self.TVDB = thetvdbapi.TheTVDB()

		# create the all important show dict
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
		self.create_show_dict()

		# create database and settings monitor
		self.monitor = Monitor(self)


	# MAIN 
	def onLibrary_scan_complete(self):
		''' Gets all the episodes in the library that have 'Missing_Sub_' in the
		filename and adds the prefix to the title (if needed) or removes the entry
		if the episode in on the removal list 
		'''

		# get all episodes in the library
		QUERY_filtered_episodes['params']['tvshowid'] = -1
		QUERY_filtered_episodes['params']['filter']['field'] = "file"
		QUERY_filtered_episodes['params']['filter']['value'] = 'Missing_Sub_'

		all_episodes = json_query(QUERY_filtered_episodes)

		all_episodes = all_episodes.get('episodes', [])

		# cycle through the episodes
		for episode in all_episodes:

			title    = episode.get('title', '')
			filename = episode.get('file', '')
			epid     = episode.get('episodeid', '')

			# if the title doesnt start with the prefix, then append the prefix to the title
			if not title.startswith(self.sub_prefix):

				QUERY_change_name['params']['episodeid'] = epid
				QUERY_change_name['params']['title'] = self.sub_prefix + title

				json_query(QUERY_change_name)

			# if the filename is in the list of the ones to remove, then remove them from
			# the library

			if filename in self.remove_these:

				QUERY_remove_episode['params']['episodeid'] = epid 

				json_query(QUERY_remove_episode)

		# reset the contents of the remove list back to empty
		self.remove_these = []


	# MAIN
	def retrieve_settings(self):
		''' Retrieves the settings for the addon '''
		
		__addon__        = xbmcaddon.Addon('script.sub.missing')
		__setting__      = __addon__.getSetting


		self.new_sub_location = __setting__('sub_location')
		self.new_sub_prefix   = __setting__('prefix')

		# if the sublocation is the default location
		# then set the folder location to the addon data folder
		if self.new_sub_location == 'default':
			self.ADDON_DATA_FOLDER = xbmc.translatePath('special://userdata')
			self.SUB_FOLDER = os.path.join(self.ADDON_DATA_FOLDER, 'addon_data', 'script.sub.missing', 'Missing_TV')
		else:
			self.SUB_FOLDER = self.sub_location

		log(self.SUB_FOLDER ,'Folder location')

		# check if the SUB_FOLDER exists, create if it doesnt
		if not os.path.exists(self.SUB_FOLDER):
			os.mkdir(self.SUB_FOLDER)
			log('Created folder')

		# presume the variable self.sub_prefix exists, and check the new prefix against
		# the existing one, if they are different then rename all the files in the library
		# that are using the old prefix
		try:
			if self.sub_prefix != self.new_sub_prefix:


				self.change_prefix(self.new_sub_prefix, self.sub_prefix)
		
		except:
			# if the variable self.sub_prefix doesnt exist, the create it and
			# set it to the new prefix
			# this should only happen on the first run

			self.sub_prefix = self.new_sub_prefix

		log(self.sub_prefix, 'Prefix')


	def change_prefix(new_prefix, old_prefix = ''):
		''' Cycles through the names of the episodes in the library and 
			changes the prefix used in the titles '''

		log('changing prefix')

		# get all episodes in the library
		QUERY_filtered_episodes['params']['tvshowid'] = -1

		QUERY_filtered_episodes['params']['filter']['value'] = old_prefix

		QUERY_filtered_episodes['params']['filter']['field'] = "title"

		all_episodes = json_query(QUERY_filtered_episodes)

		all_episodes = all_episodes.get('episodes', [])

		# cycle through the episodes change the prefix when it is found
		for episode in all_episodes:

			title    = episode.get('title', '')
			epid     = episode.get('episodeid', '')

			if old_prefix:
				if title.startswith(old_prefix):

					raw_title = title[len(old_prefix):]

				QUERY_change_name['params']['episodeid'] = epid
				QUERY_change_name['params']['title'] = new_prefix + raw_title

				json_query(QUERY_change_name)


	# MAIN		
	def threader(self, function, arguments):
		''' creates x number of threads to process the arguments in the function '''
		pass

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
		all_shows = json_query(QUERY_all_show_ids)

		all_shows = all_shows.get('tvshows', [])

		log(all_shows, 'all_shows')

		for show in all_shows:

			log(show, 'show from all shows')

			name = show.get('title', '')
			show_id = show.get('tvshowid', '')

			log([name, show_id], 'show_dict processing')

			self.show_dict[show_id] = {}
			self.show_dict[show_id]['name'] = name

			QUERY_all_episodes['params']['tvshowid'] = show_id

			# get local_episodes from JSON, process into local_episodes dict
			all_episodes = json_query(QUERY_all_episodes)
			self.process_show_info(all_episodes, show_id)

			# get TVDB ID from api
			self.retrieve_TVDBID(show_id, name)

			# get TVDB episodes, process into TVDB_episodes
			self.retrieve_TVDB_info(show_id)

			break

		log(self.show_dict, 'show dict')

		## once created ##

		# find the missing episodes
		self.identify_missing()

		# create the subsitutes
		self.create_substitutes()

		# remove unneeded stubs from the library
		json_query(QUERY_clean)

		# call for a refresh of the SUB_FOLDER
		self.request_library_update()

	# SHOW DICT
	def process_show_info(self, local_show_dict, show_id):
		''' create or update entry in local_show_dict '''
		log(local_show_dict, 'local_show_dict')

		episodes = local_show_dict.get('episodes', [])

		local_episodes = {}

		log(episodes, 'episodes')

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

		show_tup = self.TVDB.get_matching_shows(showname)

		try:
			show_tvdbid = show_tup[0][0]

			if show_tvdbid:

				self.show_dict[local_id]['TVDBID'] = show_tvdbid

				log(show_tvdbid, 'tvshowid for %s' % showname)

				return True

			log('no showid found on tvdb for %s' % showname)

		except:

			log('Error retreiving tvdb showid')
			return None

	# SHOW DICT
	def retrieve_TVDB_info(self, local_id):
		''' retrieve all episode info for a specific show '''

		log(local_id, 'retrieve_TVDB_info')

		show = self.show_dict.get(local_id, False)

		log(show, 'show')

		# if the show isnt found then abandon effort
		if not show:
			return

		TVDBID = show.get('TVDBID', False)

		log(TVDBID, 'stored tvdbid')

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

			log('retrieving show info from tvdb')
			# get the show info
			info = self.TVDB.get_show_and_episodes(TVDBID)

			log(info, 'tvdb show info')

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

		log('processing show info for %s' % local_id)
		log(info, 'raw show info')

		TVDB_episodes = []
		for episode in info:
			e = episode.get('EpisodeNumber', False)
			s = episode.get('SeasonNumber', False)
			if all([e,s]):
				TVDB_episodes.append((int(s), int(e)))

		self.show_dict[local_id]['TVDB_Episodes'] = TVDB_episodes

	# SHOW DICT
	def identify_missing(self, showid = None):
		''' compares the TVDB episodes to the local episodes 
			and updates show dict with all missing eps '''

		# allow for single show update
		pairs = self.single_or_all(showid)

		for k, v in pairs.iteritems():
			
			local_eps  = set(v.get('local_episodes',{}).keys())
			remote_eps = set(v.get('TVDB_Episodes',[]))

			log('============')
			log(local_eps)
			log(remote_eps)
			log('============')

			self.show_dict[k]['missing_episodes'] = list(remote_eps.difference(local_eps))

	# SHOW DICT
	def single_or_all(self, showid):
		''' allow for single show, or complete update '''

		log(showid, 'single or all')

		if showid:
			pairs = {showid: self.show_dict.get(showid,{})}
		else:
			pairs = self.show_dict

		return pairs

	# STUBS
	def create_substitutes(self, showid = None):
		''' creates/updates the substitutes folder in addondata '''

		log('creating substitutes')

		# allow for single show update
		pairs = self.single_or_all(showid)

		# get the current structure and population of sub folder
		subs = self.retrieve_subs()
		log(subs, 'existing stubs')

		# get just the names of the folders (tvshows)
		existing_sub_folders = set(subs.keys())
		log(existing_sub_folders, 'existing_sub_folders')

		# get the list of the folders that are needed
		needed_sub_folders = set([os.path.join(self.SUB_FOLDER, v['name']) for k, v in pairs.iteritems() if v.get('name', False)])
		log(needed_sub_folders, 'needed_sub_folders')

		# create a list of the folders that need to be created
		create_these_folders  = needed_sub_folders.difference(existing_sub_folders)
		log(create_these_folders, 'create_these_folders')

		# create a list of the folders that need to be destroyed
		destroy_these_folders = existing_sub_folders.difference(needed_sub_folders)		
		log(destroy_these_folders,'destroy_these_folders')

		# create the folders
		self.create_folders(create_these_folders)

		# only destroy folders if this ISNT a single show update
		if not showid:
			self.destroy_folders(destroy_these_folders)

		# cycle through the shows and create the episode stubs
		for k, v in pairs.iteritems():

			self.create_or_delete_stubs(k, v, subs)

	# STUBS
	def retrieve_subs(self):
		''' returns a dict of {showname : [(season, episode), ...]}
			for each sub-folder in addondata '''

		subs_dict = {}

		for showname in os.walk(self.SUB_FOLDER):

			name = showname[0]

			for stub in os.listdir(showname[0]):

				p = r'Missing_Sub_s(\d+)e(\d+).avi'
				match = re.search(p, stub)

				if not match:
					continue

				if name not in subs_dict.keys():
					subs_dict[name] = []
				subs_dict[name].append((match.group(1), match.group(2)))

		return subs_dict

	# STUBS
	def create_folders(self, namelist):
		''' creates the folders in the namelist in the addondata directory '''
		for name in namelist:
			path = os.path.join(self.SUB_FOLDER, name)
			try:
				log(path, 'attempting to create folder')
				os.mkdir(path)
				log('folder created')
			except:
				log('folder creation failed')

	# STUBS
	def destroy_folders(self, namelist):
		''' destroys the folders in the namelist from the addondata directory '''	
		log(namelist, 'destroy these')

		for name in namelist:
			path = os.path.join(self.SUB_FOLDER, name)

			self.remove_these += os.listdir(path)

			shutil.rmtree(path)

	# STUBS
	def create_or_delete_stubs(self, k, v, subs):

		# get the missing episode tuples
		missing_episodes = set(v.get('missing_episodes', []))
		log(missing_episodes, 'missing_episodes')

		# get the existing episode tuples
		existing_stubs = set(subs.values())
		log(existing_stubs, 'existing_stubs')

		folder = v.get('name', False)
		
		# delete the unneeded stubs
		delete_these_stubs = existing_stubs.difference(missing_episodes)

		for stub in delete_these_stubs:

			log(stub, 'deleting stub')

			epid = self.remove_stub(folder, stub)

		# create the missing stubs
		create_these_stubs = missing_episodes.difference(existing_stubs)

		log(create_these_stubs, 'create_these_stubs')

		for episode in create_these_stubs:

			log(episode, 'creating stub')


			if folder:
			
				self.add_stub(folder, episode)

	# STUBS
	def remove_stub(self, folder, stub):
		ep_name = 'Missing_Sub_s{}e{}.avi'.format(stub[0], stub[1])

		path = os.path.join(self.SUB_FOLDER, folder, ep_name)		

		os.remove(path)

		self.remove_these.append(path)

	# STUBS
	def add_stub(self, folder, episode):
		''' create_stub using season and episode, write the epid into the file '''

		log(episode, 'creating stub')
		log(folder)
		log(episode)

		ep_name = 'Missing_Sub_s{}e{}.avi'.format(episode[0], episode[1])

		stub = os.path.join(self.SUB_FOLDER, folder, ep_name)

		with open(stub, 'w') as f:
			pass

	# LIBRARY
	def request_library_update(self):
		''' Request a library update of the specific addondata folder '''

		QUERY_rescan['params']['directory'] = self.SUB_FOLDER
		json_query(QUERY_rescan)

	# LIBRARY
	def clean_library(self):
		''' removes the episode from the library '''

		json_query(QUERY_clean)


if ( __name__ == "__main__" ):

	Main()

	while not xbmc.abortRequested:

		xbmc.sleep(10)

	del Main



