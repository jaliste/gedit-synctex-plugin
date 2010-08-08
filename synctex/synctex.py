# -*- coding: utf-8 -*-

#  synctex.py - Synctex support with Gedit and Evince.
#  
#  Copyright (C) 2010 - José Aliste <jose.aliste@gmail.com>
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
import dbus.mainloop.glib
import os.path
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)


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
WINDOW_DATA_KEY = "SynctexPluginWindowData"


class SynctexViewHelper:

    mime_types = ['text/x-tex'];

    def __init__(self, view, window, tab):
        self._view = view
        self._window = window
        self._tab = tab
        self._doc = view.get_buffer()
        self.window_proxy = None
        self._handlers = [
            self._doc.connect('saved', self.on_saved_or_loaded),
            self._doc.connect('loaded', self.on_saved_or_loaded)
        ]
        self.active = False
        self.uri = self._doc.get_uri()
        self.mime_type = self._doc.get_mime_type()
        self.update_uri_mime_type()

    def on_saved_or_loaded(self, doc, data):
        self.update_uri_mime_type()
    
    def deactivate(self):
        pass

    def update_uri_mime_type(self):
        uri = self._doc.get_uri()
        if uri is not None and uri != self.uri:
            self._window.view_dic[uri] = self
            self.uri = uri
        if self.uri is not None:
            [self.directory, self.filename] = os.path.split(self.uri[7:])
        self.mime_type = self._doc.get_mime_type()
        self.update_active()

    def goto_line (self, line):
        self._doc.goto_line(line) 
        self._view.scroll_to_cursor()
        self._window.set_active_tab(self._tab)

    def source_view_handler(self, input_file, source_link):
        if self.filename == input_file:
            self.goto_line(source_link[0] - 1)
        else:
            uri = "file://" + os.path.join (self.directory,input_file)
            view_dict = self._window.get_data(WINDOW_DATA_KEY).view_dict
            if uri in view_dict:
                view_dict[uri].goto_line(source_link[0] - 1)
            else:
                self._window.create_tab_from_uri(uri, None, source_link[0]-1, False, True) 
        self._window.present()

    def sync_view(self):
        if self.active:
            cursor_iter =  self._doc.get_iter_at_mark(self._doc.get_insert())
            line = cursor_iter.get_line() + 1
            col = cursor_iter.get_line_offset()
            print "SyncView", self.uri[7:], (line, col)
            self.window_proxy.SyncView(self.uri[7:], (line, col))

    def update_active(self):
        # Activate the plugin only if the doc is a LaTeX file. 
        self.active = (self.mime_type in self.mime_types)

        if self.active and self.window_proxy is None:
            if self.uri.endswith(".tex"):
                uri_output = self.uri[:-3] + "pdf"
                self.window_proxy = EvinceWindowProxy (uri_output, True)
                self.window_proxy.set_source_handler (self.source_view_handler)
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
        self.view_dict = {}

        for view in window.get_views():
            self.add_helper(view)

        self.handlers = [
            window.connect("tab-added", lambda w, t: self.add_helper(t.get_view(),w, t)),
            window.connect("tab-removed", lambda w, t: self.remove_helper(t.get_view()))
        ]
        #window.set_data(WINDOW_DATA_KEY, (added_hid, removed_hid))

        #self._window.connect("destroy", self._on_window_destroyed) ]

    def add_helper(self, view, window, tab):
        helper = SynctexViewHelper(view, window, tab)
        if helper.uri is not None:
            self.view_dict[helper.uri] = helper
        view.set_data (VIEW_DATA_KEY, helper)

    def remove_helper(self, view):
        if helper.uri is not None:
            del self.view_dict[uri]
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
        self._window.get_active_view().get_data(VIEW_DATA_KEY).sync_view()

class SynctexPlugin(gedit.Plugin):
    
    def __init__(self):
        gedit.Plugin.__init__(self)

    def activate(self, window):
        helper = SynctexWindowHelper(self, window)
        window.set_data(WINDOW_DATA_KEY, helper)
    
    def deactivate(self, window):
        window.get_data(WINDOW_DATA_KEY).deactivate()        
        window.set_data(WINDOW_DATA_KEY, None)
        
    def update_ui(self, window):
        pass
#        window.get_data(WINDOW_DATA_KEY).update_ui()


# ex:ts=4:et:
