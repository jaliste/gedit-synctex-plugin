# -*- coding: utf-8 -*-

#  synctex.py - Type here a short description of your plugin
#  
#  Copyright (C) 2010 - jaliste
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#   
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#   
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330,
#  Boston, MA 02111-1307, USA.

import gtk
import gedit
from gettext import gettext as _
from evince_dbus import EvinceController

ui_str = """<ui>
  <menubar name="MenuBar">
    <menu name="ToolsMenu" action="Tools">
      <placeholder name="ToolsOps_2">
        <menuitem name="ExamplePy" action="SynctexForwardSearch"/>
      </placeholder>
    </menu>
  </menubar>
</ui>
"""

class SynctexWindowHelper:
    def __init__(self, plugin, window):
        self._window = window
        self._plugin = plugin
        self._insert_menu()
        self._window.connect("tab_added", self._on_tab_added),
        self._window.connect("tab_removed", self._on_tab_removed),
        self._window.connect("active_tab_changed", self._on_active_tab_changed),
	self.active_document = None
	self.active_uri = None
	self.evince_controller = EvinceController() 
        #self._window.connect("destroy", self._on_window_destroyed) ]


    def __del__(self):
        self._window = None
        self._plugin = None
    
    def deactivate(self):
        pass
    
    def _insert_menu(self):
        # Get the GtkUIManager
        manager = self._window.get_ui_manager()

        # Create a new action group
        self._action_group = gtk.ActionGroup("ExamplePyPluginActions")
        self._action_group.add_actions([("SynctexForwardSearch", None, _("Forward Search"),
                                         None, _("Forward Search"),
                                         self.forward_search_cb)])

        # Insert the action group
        manager.insert_action_group(self._action_group, -1)

        # Merge the UI
        self._ui_id = manager.add_ui_from_string(ui_str)

        

    def update_ui(self):
	new_doc = self._window.get_active_document()
 	new_uri = new_doc.get_uri()
        if self.active_document == new_doc and self.active_uri == new_uri:
             return
	self.active_document = new_doc
	self.active_uri = new_uri
        print "UPDATE UI", self._window.get_active_document()
        pass

    def forward_search_cb(self, action):
        doc = self._window.get_active_document()

        if doc.get_mime_type()=='text/x-tex':
            cursor_iter =  doc.get_iter_at_mark(doc.get_insert())
            line = cursor_iter.get_line()
            col = cursor_iter.get_line_offset()
            evince_controller.forward_search(doc.get_uri(), line, col)
        if not doc:
            return

    def _on_tab_added(self, window, tab):
        print "Tab added ", tab.get_document().get_uri()
        pass
    def _on_tab_removed(self, window, tab):
        pass
    def _on_active_tab_changed(self, window, tab):
        print "Active tab changed ", tab.get_document().get_mime_type()
        pass

class SynctexPlugin(gedit.Plugin):
    WINDOW_DATA_KEY = "SynctexPluginWindowData"
    
    def __init__(self):
        gedit.Plugin.__init__(self)

    def activate(self, window):
        helper = SynctexWindowHelper(self, window)
        window.set_data(self.WINDOW_DATA_KEY, helper)
    
    def deactivate(self, window):
        window.get_data(self.WINDOW_DATA_KEY).deactivate()        
        window.set_data(self.WINDOW_DATA_KEY, None)
        
    def update_ui(self, window):
        window.get_data(self.WINDOW_DATA_KEY).update_ui()


# ex:ts=4:et:
