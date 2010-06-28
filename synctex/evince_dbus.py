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

class EvinceController:
	"""A custom object to control an Evince process through DBUS."""
	daemon = None
	def __init__(self, uri, spawn = False):
#		self.context = context
		self.uri = uri
		bus = dbus.SessionBus()
		if spawn:
			self.proc = subprocess.Popen(['/home/jaliste/dev/evince/shell/evince',uri])
			# THE FOLLOWING IS WRONG!
			time.sleep(0.3)
		try:    			
			if EvinceController.daemon is None:
				EvinceController.daemon = daemon = bus.get_object('org.gnome.evince.Daemon','/org/gnome/evince/Daemon')
			self.dbus_name = daemon.FindDocument(uri)
			if self.dbus_name != '':
				print self.dbus_name
				self.window = bus.get_object(self.dbus_name, '/org/gnome/evince/Window/0')
				self.window.connect_to_signal("SyncSource", self.sync_source_cb, dbus_interface="org.gnome.evince.Window")
		except dbus.DBusException:
			traceback.print_exc()

	def sync_source_cb(self, source_file, source_point):
		"""
		A service call has been received
		
		@param filename: the filename
		@param line: a line number counting from 1 (!)
		"""
		#_log.debug("Received inverse DVI search call: %s %s" % (filename, line))
		
		print source_file, source_point
		#file = File(filename)
		
		#try:
		#	%self._context.activate_editor(file)
		#	editor = self._context.active_editor
			
		#	assert type(editor) is LaTeXEditor
			
		#	editor.select_lines(line - 1)
			
		#except KeyError:
		#	raise("Could not activate tab for file %s" % filename)
			
	def forward_search(self, data):
		self.window.SyncView('/home/jaliste/Documents/research/articles/rapid_convergence/10.tex',
		[data, 1],dbus_interface="org.gnome.evince.Window")
		return False				
if __name__ == '__main__':
	import dbus.mainloop.glib, gobject, glib
	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

 	a = EvinceController('file:///home/jaliste/Documents/research/articles/rapid_convergence/10.pdf', True)
	glib.timeout_add(10000, a.forward_search, 300)
	loop = gobject.MainLoop()
	
	loop.run()  


