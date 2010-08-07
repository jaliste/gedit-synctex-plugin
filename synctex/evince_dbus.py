#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file is part of the Gedit Synctex plugin.
#
# Copyright (C) 2010 Jose Aliste <jose.aliste@gmail.com>
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public Licence as published by the Free Software
# Foundation; either version 2 of the Licence, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public Licence for more 
# details.
#
# You should have received a copy of the GNU General Public Licence along with
# this program; if not, write to the Free Software Foundation, Inc., 51 Franklin
# Street, Fifth Floor, Boston, MA  02110-1301, USA

import dbus, subprocess, time
from traceback import print_exc

RUNNING, CLOSED = range(2)

class EvinceController:
	"""A custom object to control an Evince process through DBUS."""
	daemon = None

	def __init__(self, uri, spawn = False):
		self.uri = uri
		self.spawn = spawn
		self.status = CLOSED
		bus = dbus.SessionBus()
		self._get_dbus_name()
	
	def _get_dbus_name (self):
		try:    			
			if EvinceController.daemon is None:
				EvinceController.daemon = bus.get_object('org.gnome.evince.Daemon','/org/gnome/evince/Daemon')
			self.dbus_name = EvinceController.daemon.FindDocument(self.uri, self.spawn, dbus_interface = "org.gnome.evince.Daemon")
			if self.dbus_name != '':
				self.status = RUNNING
				self.window = bus.get_object(self.dbus_name, '/org/gnome/evince/Application')
				self.window = bus.get_object(self.dbus_name, '/org/gnome/evince/Window/0')
				self.window.connect_to_signal("SyncSource", self.sync_source_cb, dbus_interface="org.gnome.evince.Window")
				self.window.connect_to_signal("Closed", self.on_window_close, dbus_interface="org.gnome.evince.Window")
		except dbus.DBusException:
			print_exc()		
		bus.add_signal_receiver(self.name_owner_changed_cb, signal_name = "NameOwnerChanged")
	def on_window_close(self):
		self.status = CLOSED

	def name_owner_changed_cb(self, service_name, old_owner, new_owner):
		if service_name == self.dbus_name and new_owner == '': 
			self.status = CLOSED
	def sync_source_cb(self, source_file, source_point):
		"""
		A service call has been received
		
		@param filename: the filename
		@param line: a line number counting from 1 (!)
		"""
		print source_file, source_point
		#file = File(filename)
		
		#try:
		#	%self._context.activate_editor(file)
		#	editor = self._context.active_editor
			
		#	assert type(editor) is LaTeXEditor
			
		#	editor.select_lines(line - 1)
			
		#except KeyError:
		#	raise("Could not activate tab for file %s" % filename)
			
	def SyncView(self, input_file, data):
		print self.status
		if self.status == CLOSED:
			if not self.spawn:
				self._get_dbus_name()
		# if self.status is still closed, it means there is a 
		# problem running evince.
		if self.status == CLOSED: 
			return False
		print input_file, data
		self.window.SyncView(input_file, (data, 1), dbus_interface="org.gnome.evince.Window")
		return False				
def print_usage():
	print '''
The usage is evince_dbus output_file line_number input_file from the directory of output_file. 
'''
## This file can be used as a script to support forward search and backward search in vim.
## It should be easy to adapt to other editors. 
##  evince_dbus  pdf_file  line_source input_file
if __name__ == '__main__':
	import dbus.mainloop.glib, gobject, glib, sys, os
	if len(sys.argv)!=4:
		print_usage()
		sys.exit(1)	
	try:
		line_number = int(sys.argv[2])
	except ValueError:
		print_usage()
		sys.exit(1)
	
	output_file = sys.argv[1]
	input_file  = sys.argv[3]
        path_output  = os.getcwd() + '/' + output_file
	path_input   = os.getcwd() + '/' + input_file

	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
	bus = dbus.SessionBus()

 	a = EvinceController('file://' + path_output, True )
        glib.timeout_add(1000, a.SyncView, path_input, line_number)
	loop = gobject.MainLoop()
	loop.run() 
