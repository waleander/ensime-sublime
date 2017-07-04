import sublime
import sublime_plugin

from functools import partial as bind

from .paths import relative_path, is_subpath
from . import env


class EnsimeCommon(object):
    def __init__(self, owner):
        if type(owner) == sublime.Window:
            self.w = owner
            self.v = None
        elif type(owner) == sublime.View:
            # owner.window() is sometimes None ??
            self.w = owner.window() or sublime.active_window()
            self.v = owner
        else:
            raise Exception("unsupported owner of type: " + str(type(owner)))
        self.env = env.getOrCreateNew(self.w)

    def status_message(self, msg):
        sublime.set_timeout(bind(sublime.status_message, msg), 0)

    def error_message(self, msg):
        sublime.set_timeout(bind(sublime.error_message, msg), 0)

    def is_valid(self):
        return bool(self.env and self.env.valid)

    def is_running(self):
        return self.is_valid() and self.env.running

    def _filename_from_wannabe(self, wannabe):
        if type(wannabe) == type(None):
            v = self.v if hasattr(self, "v") else self.w.active_view()
            return self._filename_from_wannabe(v) if v is not None else None
        if type(wannabe) == sublime.View:
            return wannabe.file_name()
        return wannabe

    def in_project(self, wannabe=None):
        filename = self._filename_from_wannabe(wannabe)
        extension_ok = bool(filename and (filename.endswith("scala") or filename.endswith("java")))
        subpath_ok = bool(self.env and is_subpath(self.env.project_root, filename))
        return extension_ok and subpath_ok

    def project_relative_path(self, wannabe):
        filename = self._filename_from_wannabe(wannabe)
        if not self.in_project(filename):
            return None
        return relative_path(self.env.project_root, filename)


class EnsimeWindowCommand(EnsimeCommon, sublime_plugin.WindowCommand):
    def __init__(self, window):
        super(EnsimeWindowCommand, self).__init__(window)
        self.window = window


class EnsimeTextCommand(EnsimeCommon, sublime_plugin.TextCommand):
    def __init__(self, owner):
        pass


# class EnsimeEventListener(sublime_plugin.EventListener):
#     def on_load(self, view):
#         if self.is_running() and self.in_project():
#             TypeCheckFileReq(view.file_name()).run(self.env.client)

#     def on_post_save(self, view):
#         pass

#     def on_activated(self, view):
#         pass
