import sublime
import sublime_plugin
import os.path
#import sys
#sys.path.append('/Applications/PyCharm.app/pycharm-debug-py3k.egg')
#import pydevd


# plugin_loaded()
def plugin_loaded():
    # pydevd.settrace('localhost', port=51234,stdoutToServer=True,stderrToServer=True)
    BookmarkExtended.settings = sublime.load_settings("BookmarkExtended.sublime-settings")


# plugin_unloaded()
def plugin_unloaded():
    pass


class Bookmark(object):
    region = None
    view = None
    view_name = None
    line = None
    content = None
    comment = None

    def __init__(self, view, region):
        self.view = view
        self.region = region

        self.line, _ = view.rowcol(region.begin())
        self.content = view.substr(region)

        # Check view name
        if view.file_name():
            self.view_name = os.path.basename(view.file_name())
        elif view.name():
            self.view_name = view.name()
        else:
            self.view_name = "untitled"

        # Comment is stored in view.settings()
        self.comment = Bookmark.__get_comment(self)

    @staticmethod
    def __get_comment(bookmark):
        view = bookmark.view
        region = bookmark.region

        settings = view.settings()

        comments = settings.get('bookmark_comments', {})
        for key, val in comments.items():
            if str(region) == key:
                return val
        return None


class BookmarkExtended(object):
    settings = sublime.load_settings('BookmarkExtended.sublime-settings')

    def dump_buffer(self):

        views = self.view.window().views()
        window = self.view.window()
        dump_view = None
        for view in views:
            if view.name() == "Dump Bookmarks":
                dump_view = view
                break
        if not dump_view:
            dump_view = window.new_file()
            dump_view.set_name("Dump Bookmarks")
        return dump_view

    def get_bookmarks(self, view=None):
        if view is None:
            view = self.view

        bookmarks = []
        if self.settings.get('enable_all_views'):
            window = view.window()
            for v in window.views():
                bookmarks += self.get_view_entries(v)
        else:
            bookmarks = self.get_view_entries()

        return bookmarks

    def get_view_entries(self, view=None):
        if view is None:
            view = self.view

        bookmarks = []
        # Get bookmark regions
        for region in view.get_regions('bookmarks'):
            # if region is empty, set its line as region.
            if region.empty():
                region = view.line(region)

            bookmarks.append(Bookmark(view, region))

        return bookmarks

    def set_comment(self, bookmark, comment):
        view = bookmark.view
        region = bookmark.region

        settings = view.settings()
        comments = settings.get('bookmark_comments', {})
        comments[str(region)] = comment
        settings.set('bookmark_comments', comments)

    def bookmark_formatter(self, bookmarks, view=None):
        if view is None:
            view = self.view

        header = self.settings.get('bookmark_dump_header', ['###'])
        footer = self.settings.get('bookmark_dump_footer', ['###'])

        entries = []
        for bookmark in bookmarks:
            view = bookmark.view
            view_name = bookmark.view_name
            comment = bookmark.comment
            content = bookmark.content
            line = bookmark.line

            header = "### {}({})\n".format(view_name, line)
            if comment is not None:
                header += "### {}\n".format(comment)

            footer = "\n###\n\n"
            entry = header + content + footer
            entries.append(entry)
        return entries


class DumpBookmarksToBufferCommand(sublime_plugin.TextCommand):
    """
    begin_edit() and end_edit() is resticited on ST3, so creating another
    command to insert strings to new entries
    """
    def run(self, edit, entry=None):
        self.view.insert(edit, 0, entry)


class DumpBookmarksCommand(BookmarkExtended, sublime_plugin.TextCommand):
    def run(self, edit):
        dump_view = self.dump_buffer()
        bookmarks = self.get_bookmarks()

        if len(bookmarks) == 0:
            sublime.status_message("No bookmark found.")

        formatted = self.bookmark_formatter(bookmarks)
        dump_view.run_command('dump_bookmarks_to_buffer', {'entry': "".join(formatted)})
        self.view.window().focus_view(dump_view)


class QuickPanelBookmarksCommand(BookmarkExtended, sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        self.bookmarks = self.get_bookmarks()
        bookmarks = self.bookmarks

        # save the original position
        self.original_pt = sublime.Region(0, 0)
        if len(view.sel()):
            self.original_pt = view.sel()[0]

        # For quick panel menu
        bookmark_names = []  # associated bookmark name to show quick panel
        for bookmark in bookmarks:
            title = bookmark.content
            if bookmark.comment:
                title = bookmark.comment
            bookmark_names.append(title)

        if len(bookmark_names) == 0:
            bookmark_names = ["No Bookmark found."]

        if int(sublime.version()) > 3000:
            window = view.window()
            window.show_quick_panel(bookmark_names, self.on_done, 0, 0, self.on_highlighted)
        else:
            self.view.window().show_quick_panel(bookmark_names, self.on_done)

    def on_done(self, index):
        bookmark = self.bookmarks[index]
        view = bookmark.view

        # erase highlight
        [v.erase_regions('highlight.bookmark') for v in view.window().views()]

        if index == -1:
            # back to original position
            self.view.show(self.original_pt)
            self.view.window().focus_view(self.view)
        else:
            pt = bookmark.region.begin()

            self.view.window().focus_view(view)

            view.sel().clear()
            view.sel().add(pt)
            view.show(pt)

    def on_highlighted(self, index):
        bookmark = self.bookmarks[index]
        view = bookmark.view

        pt = bookmark.region

        self.view.window().focus_view(view)

        view.show(pt.begin())
        view.add_regions('highlight.bookmark', [pt], 'highlight.bookmark')


class SetBookmarkCommentCommand(BookmarkExtended, sublime_plugin.TextCommand):
    def selected_bookmark(self):
        bookmarks = self.get_bookmarks()
        cursor = self.view.sel()[0]

        for bookmark in bookmarks:
            if bookmark.region.contains(cursor):
                return bookmark
        return None

    def is_visible(self):
        """
         show this menu if the selection is included in bookmark key
        """
        if self.selected_bookmark() is None:
            return False
        return True

    def run(self, edit):
        view = self.view
        self.sel_bookmark = self.selected_bookmark()

        view.window().show_input_panel('Comment: ', '', self.on_done, None, None)

    def on_done(self, comment):
        self.set_comment(self.sel_bookmark, comment)


class SelectBookmarkExtendedCommand(BookmarkExtended, sublime_plugin.TextCommand):
    """
     Over write exsiting 'select_bookmark' class
    """
    def description(self, index):
        bookmarks = self.get_view_entries()
        if len(bookmarks) > index:
            bookmark = bookmarks[index]
            title = "Line {}: {}".format(bookmark.line, bookmark.content[:20])
            if bookmark.comment:
                title = "line {}: {}".format(bookmark.line, bookmark.comment)
            return title
        return ""

    def is_visible(self, index):
        if self.description(index) == "":
            return False
        return True

    def run(self, edit, index):
        bookmarks = self.get_view_entries()
        bookmark = bookmarks[index]
        view = bookmark.view
        view.sel().clear()
        view.sel().add(bookmark.region)
        view.show(bookmark.region.begin())


class AutoRunner(BookmarkExtended, sublime_plugin.EventListener):
    def on_activated(self, view, regions=None):
        if self.settings.get('highlight_bookmark', None):
            scope = self.settings.get('highlight_scope', 'string')
            if regions is None:
                regions = [b.region for b in self.get_view_entries(view)]
            view.add_regions('highlight', regions, scope)

    def on_text_command(self, view, command_name, args):
        # post_text_command does not work in current ST version...
        # So, highlight bookmark is implemented in on_text_command
        # at current ver.
        if command_name == 'toggle_bookmark':
            # This is not needed when post_text_commaned works
            regions = [b.region for b in self.get_view_entries(view)]
            # Check current sel has key 'bookmark'
            if len(view.sel()) > 0:
                pt = view.sel()[0].begin()
                found = None
                for i in range(0, len(regions)):
                    if regions[i].contains(pt):
                        # If find, the bookmark will be removed
                        del regions[i]
                        found = True
                        break
                if not found:
                    if view.sel()[0].empty():
                        regions.append(view.line(pt))
                    else:
                        regions.append(view.sel()[0])
                self.on_activated(view, regions)
        elif command_name == 'clear_bookmarks':
            self.on_activated(view, [])
