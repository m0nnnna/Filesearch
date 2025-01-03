import os
import re
import wx
import subprocess
import platform
import shutil

def normalize_filename(filename):
    """Normalize the filename by converting to lowercase and removing non-alphanumeric characters except for letters, numbers, and dots."""
    return re.sub(r'[^a-zA-Z0-9.]', '', filename.lower())

def search_files(directory, keyword):
    results = []
    normalized_keyword = normalize_filename(keyword)

    if not normalized_keyword:  # If search is empty, show all files
        for root, _, files in os.walk(directory):
            for file in files:
                results.append(os.path.join(root, file))
    else:
        for root, _, files in os.walk(directory):
            for file in files:
                normalized_filename = normalize_filename(file)
                if normalized_keyword in normalized_filename:
                    results.append(os.path.join(root, file))
    return results

def open_file_explorer(file_path):
    if platform.system() == 'Windows':
        subprocess.run(['explorer', '/select,', file_path])
    elif platform.system() == 'Darwin':
        subprocess.run(['open', '-R', file_path])
    elif platform.system() == 'Linux':
        subprocess.run(['xdg-open', os.path.dirname(file_path)])
        subprocess.run(['nautilus', '--select', file_path])

def open_file(file_path):
    if platform.system() == 'Windows':
        os.startfile(file_path)
    elif platform.system() == 'Darwin':
        subprocess.run(['open', file_path])
    elif platform.system() == 'Linux':
        subprocess.run(['xdg-open', file_path])

class FileSearchFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="File Search", size=(500, 500))
        panel = wx.Panel(self)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Directory Path input
        dir_label = wx.StaticText(panel, label="Directory Path:")
        self.dir_text = wx.TextCtrl(panel)
        dir_button = wx.Button(panel, label="Browse")
        dir_row = wx.BoxSizer(wx.HORIZONTAL)
        dir_row.Add(dir_label, 0, wx.ALL, 5)
        dir_row.Add(self.dir_text, 1, wx.EXPAND | wx.ALL, 5)
        dir_row.Add(dir_button, 0, wx.ALL, 5)
        sizer.Add(dir_row, 0, wx.EXPAND)

        # Search Box
        search_label = wx.StaticText(panel, label="Search Keyword:")
        self.search_box = wx.TextCtrl(panel)
        sizer.Add(search_label, 0, wx.ALL, 5)
        sizer.Add(self.search_box, 0, wx.EXPAND | wx.ALL, 5)
        
        # Search Button
        search_button = wx.Button(panel, label="Search")
        sizer.Add(search_button, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        
        # Results List
        self.results_list = wx.ListCtrl(panel, style=wx.LC_REPORT)
        self.results_list.InsertColumn(0, 'Files', width=400)
        sizer.Add(self.results_list, 1, wx.EXPAND | wx.ALL, 5)
        
        # Buttons for operations
        select_all_button = wx.Button(panel, label="Select All")
        copy_button = wx.Button(panel, label="Copy")
        move_button = wx.Button(panel, label="Move")
        delete_button = wx.Button(panel, label="Delete")
        action_row = wx.BoxSizer(wx.HORIZONTAL)
        action_row.Add(select_all_button, 0, wx.ALL, 5)
        action_row.Add(copy_button, 0, wx.ALL, 5)
        action_row.Add(move_button, 0, wx.ALL, 5)
        action_row.Add(delete_button, 0, wx.ALL, 5)
        sizer.Add(action_row, 0, wx.CENTER)

        panel.SetSizer(sizer)

        # Bind events
        self.Bind(wx.EVT_BUTTON, self.on_search, search_button)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_search, self.search_box)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_search, self.dir_text)
        self.Bind(wx.EVT_BUTTON, self.on_browse, dir_button)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_select, self.results_list)
        self.Bind(wx.EVT_BUTTON, self.on_select_all, select_all_button)
        self.Bind(wx.EVT_BUTTON, self.on_copy, copy_button)
        self.Bind(wx.EVT_BUTTON, self.on_move, move_button)
        self.Bind(wx.EVT_BUTTON, self.on_delete, delete_button)

    def on_search(self, event):
        self.results_list.DeleteAllItems()
        directory = self.dir_text.GetValue()
        keyword = self.search_box.GetValue()
        
        if directory:
            results = search_files(directory, keyword)
            for item in results:
                self.results_list.Append([item])

    def on_browse(self, event):
        with wx.DirDialog(self, "Choose a directory:", style=wx.DD_DEFAULT_STYLE) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                self.dir_text.SetValue(dlg.GetPath())

    def on_select(self, event):
        item = event.GetItem()
        file_path = self.results_list.GetItemText(item.GetId())
        open_file(file_path)
        open_file_explorer(file_path)

    def on_select_all(self, event):
        for item in range(self.results_list.GetItemCount()):
            self.results_list.Select(item)

    def on_copy(self, event):
        selected = self.results_list.GetFirstSelected()
        if selected != -1:
            with wx.DirDialog(self, "Choose destination directory:", style=wx.DD_DEFAULT_STYLE) as dlg:
                if dlg.ShowModal() == wx.ID_OK:
                    dest_dir = dlg.GetPath()
                    while selected != -1:
                        source = self.results_list.GetItemText(selected)
                        dest = os.path.join(dest_dir, os.path.basename(source))
                        if not os.path.exists(dest):
                            shutil.copy2(source, dest_dir)
                        selected = self.results_list.GetNextSelected(selected)
                    wx.MessageBox(f"Files copied to {dest_dir}", "Copy Complete", wx.OK | wx.ICON_INFORMATION)

    def on_move(self, event):
        selected = self.results_list.GetFirstSelected()
        if selected != -1:
            with wx.DirDialog(self, "Choose destination directory:", style=wx.DD_DEFAULT_STYLE) as dlg:
                if dlg.ShowModal() == wx.ID_OK:
                    dest_dir = dlg.GetPath()
                    items_to_delete = []
                    while selected != -1:
                        source = self.results_list.GetItemText(selected)
                        dest = os.path.join(dest_dir, os.path.basename(source))
                        if not os.path.exists(dest):
                            shutil.move(source, dest_dir)
                            items_to_delete.append(selected)
                        else:
                            print(f"File {source} already exists in destination, skipping.")
                        selected = self.results_list.GetNextSelected(selected)
                    # Delete items in reverse order to maintain indices
                    for idx in sorted(items_to_delete, reverse=True):
                        self.results_list.DeleteItem(idx)
                    wx.MessageBox(f"Files moved to {dest_dir}", "Move Complete", wx.OK | wx.ICON_INFORMATION)

    def on_delete(self, event):
        selected = self.results_list.GetFirstSelected()
        if selected != -1:
            if wx.MessageBox("Are you sure you want to delete the selected files?", "Confirm Delete", wx.YES_NO | wx.ICON_QUESTION) == wx.YES:
                items_to_delete = []
                while selected != -1:
                    file_path = self.results_list.GetItemText(selected)
                    try:
                        os.remove(file_path)
                        items_to_delete.append(selected)
                        print(f"Deleted {file_path}")
                    except Exception as e:
                        print(f"Error deleting {file_path}: {e}")
                    selected = self.results_list.GetNextSelected(selected)
                for idx in sorted(items_to_delete, reverse=True):
                    self.results_list.DeleteItem(idx)
                wx.MessageBox("Selected files have been deleted.", "Delete Complete", wx.OK | wx.ICON_INFORMATION)

if __name__ == '__main__':
    app = wx.App(False)
    frame = FileSearchFrame()
    frame.Show()
    app.MainLoop()