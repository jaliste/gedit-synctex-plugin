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
from evince_dbus import EvinceWindowProxy

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

VIEW_DATA_KEY = "SynctexPluginViewData"


class SynctexViewHelper:

    mime_types = ['text/x-tex'];

    def __init__(self, view):
        self._view = view
        self._doc = view.get_buffer()
        self.window_proxy = None
        self._handlers = [
            self._doc.connect('saved', self.on_saved_or_loaded),
            self._doc.connect('loaded', self.on_saved_or_loaded)
        ]
        self.active = False
        self.update_uri_mime_type()

    def on_saved_or_loaded(self, doc, data):
        self.update_uri_mime_type()
    
    def deactivate(self):
        pass

    def update_uri_mime_type(self):
        self.uri = self._doc.get_uri()
        self.mime_type = self._doc.get_mime_type()
        self.update_active()
   
    def update_active(self):
        # Activate the plugin only if the doc is a LaTeX file. 
        self.active = (self.mime_type in self.mime_types)

        if self.active and self.window_proxy is None:
            if self.uri.endswith(".tex"):
                uri_output = self.uri[:-3] + "pdf"
                self.window_proxy = EvinceWindowProxy (uri_output, True)
                print "activando"
        elif not self.active and self.window_proxy is not None:
            # destroy the evince window proxy.
            print "desactivando"
            pass

class SynctexWindowHelper:
    def __init__(self, plugin, window):
        self._window = window
        self._plugin = plugin
        self._insert_menu()

        for view in window.get_views():
            self.add_helper(view)

        self.handlers = [
            window.connect("tab-added", lambda w, t: self.add_helper(t.get_view())),
            window.connect("tab-removed", lambda w, t: self.remove_helper(t.get_view()))
        ]
        #window.set_data(self.WINDOW_DATA_KEY, (added_hid, removed_hid))

        #self._window.connect("destroy", self._on_window_destroyed) ]

    def add_helper(self, view):
        helper = SynctexViewHelper(view)
        view.set_data (VIEW_DATA_KEY, helper)

    def remove_helper(self, view):
        view.get_data(VIEW_DATA_KEY).deactivate()
        view.set_data(VIEW_DATA_KEY, None)

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

    def forward_search_cb(self, action):
        view = self._window.get_active_view()
        view_helper  = view.get_data(VIEW_DATA_KEY)
        doc = view.get_buffer()
     
        if view_helper.active:
            cursor_iter =  doc.get_iter_at_mark(doc.get_insert())
            line = cursor_iter.get_line()
            col = cursor_iter.get_line_offset()
            print "syncview", view_helper.uri[7:], (line, col)
            view_helper.window_proxy.SyncView(view_helper.uri[7:], (line, col))

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
        pass
#        window.get_data(self.WINDOW_DATA_KEY).update_ui()


# ex:ts=4:et:
