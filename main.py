from concurrent import futures
import wx, os, shutil
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin

from database import db

APP_EXIT = 1
APP_IDIOMS = 2
APP_SEARCH = 3
APP_SETTINGS = 4
BUTTON_SEARCHING_ID = 5
BUTTON_CLEAR_ID = 6
INPUT_TEXT_ID = 7
OUTPUT_TEXT_ID = 8
BUTTON_ADD_ID = 9
BUTTON_DELETE_ID = 10
BUTTON_GO = 11
GAUGE_ID = 12
RESET_DB_ID = 13
NEW_FONT_ID = 14
LIST_IDIOMS = 15

# https://python-forum.io/thread-17858.html
thread_pool_executor = futures.ThreadPoolExecutor(max_workers=1)


class ListCtrlMixins(wx.ListCtrl, ListCtrlAutoWidthMixin):
    def __init__(self, *args, **kw):
        wx.ListCtrl.__init__(self, *args, **kw)
        ListCtrlAutoWidthMixin.__init__(self)
        self.EnableCheckBoxes(True)


class Example(wx.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.InitUI()

    def InitUI(self):
        self.SetBackgroundColour('#FFFFE5')
        self.SetSize((1000, 600))
        self.SetTitle('Idiom Finder')
        self.Centre()

        menu_bar = wx.MenuBar()
        app_menu = wx.Menu()
        reset_db_item = app_menu.Append(RESET_DB_ID, "Reset DB\tCtrl+S", 'Reset Database')
        new_font_item = app_menu.Append(NEW_FONT_ID, 'Font\tCtrl+F', 'New Font')
        app_menu.AppendSeparator()
        exit_item = app_menu.Append(wx.ID_EXIT, "Quit\tCtrl+Q", "Exit App")

        self.SetIcon(wx.Icon("imgs/app.png"))

        i = wx.Bitmap('imgs/settings.png')
        i.Rescale(i, (25, 25))
        reset_db_item.SetBitmap(i)

        i = wx.Bitmap('imgs/font.png')
        i.Rescale(i, (25, 25))
        new_font_item.SetBitmap(i)

        i = wx.Bitmap('imgs/exit.jpg')
        i.Rescale(i, (25, 25))
        exit_item.SetBitmap(i)

        self.Bind(wx.EVT_MENU, self.OnResetDB, reset_db_item)
        self.Bind(wx.EVT_MENU, self.OnSetFont, new_font_item)
        self.Bind(wx.EVT_MENU, self.onQuit, exit_item)

        menu_bar.Append(app_menu, 'App')

        self.SetMenuBar(menu_bar)

        ###

        self.tabs = wx.Notebook(self, id=wx.ID_ANY)

        ###
        panel = wx.Panel(self.tabs)

        splitter = wx.SplitterWindow(panel, id=wx.ID_ANY, style=wx.SP_LIVE_UPDATE)

        self.left_text = wx.TextCtrl(splitter, id=INPUT_TEXT_ID, style=wx.TE_MULTILINE | wx.TE_RICH2)
        self.right_text = wx.TextCtrl(splitter, id=OUTPUT_TEXT_ID, style=wx.TE_MULTILINE | wx.TE_RICH2)

        self.left_text.AppendText('Input text...')
        self.right_text.AppendText('Show result searching...')

        self.left_text.SetFont(font=wx.Font(14, wx.ROMAN, 0, 90, underline=False, faceName=""))
        self.right_text.SetFont(font=wx.Font(14, wx.ROMAN, 0, 90, underline=False, faceName=""))

        splitter.SplitVertically(self.left_text, self.right_text)
        splitter.SetMinimumPaneSize(200)

        vbox_splitter = wx.BoxSizer(wx.VERTICAL)
        vbox_splitter.Add(splitter, wx.ID_ANY, wx.EXPAND | wx.ALL)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(vbox_splitter, proportion=1, flag=wx.ALL | wx.EXPAND, border=15)

        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        hbox5.Add(wx.Button(panel, id=BUTTON_SEARCHING_ID, label='Search', size=(70, 30)))
        hbox5.Add(wx.Button(panel, id=BUTTON_CLEAR_ID, label='Clear', size=(70, 30)))

        vbox = wx.BoxSizer(wx.VERTICAL)

        vbox.Add(hbox, proportion=1, flag=wx.EXPAND, border=15)
        vbox.Add(hbox5, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=15)

        panel.SetSizer(vbox)

        self.tabs.InsertPage(0, panel, "Search")

        self.sb: wx.StatusBar = self.CreateStatusBar()
        self.sb.SetStatusText("Status Bar")
        self.sb.SetFont(font=wx.Font(14, wx.MODERN, 0, 90, underline=True, faceName=""))

        self.panel2 = wx.Panel(self.tabs)

        self.searcher = wx.TextCtrl(self.panel2, size=(200, 22))
        self.go_btn = wx.Button(self.panel2, id=BUTTON_GO, label='Go', size=(30, 22))

        self.searcher.SetFont(wx.Font(10, wx.ROMAN, 0, 90, underline=False, faceName=""))

        hbox_search = wx.BoxSizer(wx.HORIZONTAL)
        hbox_search.Add(self.searcher)
        hbox_search.Add(self.go_btn)

        self.list_idioms = ListCtrlMixins(self.panel2, LIST_IDIOMS, style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES)

        self.list_idioms.SetFont(wx.Font(14, wx.ROMAN, 0, 90, underline=False, faceName=""))
        self.list_idioms.InsertColumn(0, 'id', width=80)
        self.list_idioms.InsertColumn(1, 'name', width=140)

        vbox = wx.BoxSizer(wx.VERTICAL)

        vbox.Add(hbox_search, flag=wx.ALIGN_RIGHT)
        vbox.Add(self.list_idioms, proportion=1, flag=wx.EXPAND)

        hbox6 = wx.BoxSizer(wx.HORIZONTAL)

        self.btn_add = (wx.Button(self.panel2, id=BUTTON_ADD_ID, label='Add', size=(70, 30)))
        self.btn_remove = wx.Button(self.panel2, id=BUTTON_DELETE_ID, label='Delete', size=(70, 30))

        hbox6.Add(self.btn_add)
        hbox6.Add(self.btn_remove)

        vbox.Add(hbox6, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=15)

        self.gauge = wx.Gauge(self.panel2, id=GAUGE_ID, style=wx.GA_HORIZONTAL | wx.GA_SMOOTH)
        vbox.Add(self.gauge, flag=wx.EXPAND | wx.ALL, border=10)

        self.panel2.SetSizer(vbox)

        ###
        self.tabs.InsertPage(1, self.panel2, "Idioms")

        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnRow, id=LIST_IDIOMS)
        self.Bind(wx.EVT_BUTTON, self.OnSearch, id=BUTTON_SEARCHING_ID)
        self.Bind(wx.EVT_BUTTON, self.OnClear, id=BUTTON_CLEAR_ID)
        self.Bind(wx.EVT_BUTTON, self.OnAdd, id=BUTTON_ADD_ID)
        self.Bind(wx.EVT_BUTTON, self.OnRemove, id=BUTTON_DELETE_ID)
        self.Bind(wx.EVT_BUTTON, self.OnGo, id=BUTTON_GO)

        with db.Idiom() as session:
            data = session.get_all()
        self.searcher.AppendText('first 1000 idioms from %s' % len(data))

        thread_pool_executor.submit(self.LoadIdioms, data[:1000])

    def LoadIdioms(self, data):
        self.stop = False
        self.list_idioms.DeleteAllItems()
        len_data = len(data)
        self.gauge.SetRange(len_data)

        self.sb.SetStatusText('Select Idioms...')
        self.gauge.Show()
        count = 0
        for count, r in enumerate(data, 1):
            if self.stop:
                print('STOP')
                break
            self.gauge.SetValue(count)
            self.list_idioms.Append((count, r['name']))

        self.gauge.Hide()
        self.sb.SetStatusText('Competed Load idioms: %d' % count)
        self.AutoLayout()
        self.stop = True

    def FindAllIdioms(self, text: str):
        self.stop = False
        self.sb.SetStatusText("Loading...")

        with db.Idiom() as session:
            count = 0
            for line in text.splitlines():
                if self.stop:
                    return
                i = line.strip()
                if not i:
                    continue

                result = session.find((i, i, i))
                idioms = [i['name'] for i in result]
                if idioms:
                    count += 1
                    line1 = '{}) {}\n'.format(count, ', '.join(idioms), )
                    line2 = f'- {repr(i)}\n\n'
                    self.right_text.AppendText(line1)
                    self.right_text.AppendText(line2)

        if not self.right_text.GetValue().strip():
            self.right_text.AppendText('Not found Idioms.')

        self.sb.SetStatusText("Search completed.")
        self.stop = True

    def OnSearch(self, e):
        text = self.left_text.GetValue()
        self.right_text.Clear()
        self.sb.SetStatusText("Loading...")

        self.StopLoadTable()
        thread_pool_executor.submit(self.FindAllIdioms, text)

    def OnClear(self, e):
        self.left_text.Clear()
        self.right_text.Clear()

    def OnGo(self, e):
        self.StopLoadTable()

        text = self.searcher.GetValue()

        with db.Idiom() as session:
            if not text.strip():
                data = session.get_all()
            else:
                data = session.like(text)

        thread_pool_executor.submit(self.LoadIdioms, data)

    def OnRemove(self, e):
        self.StopLoadTable()

        dlg = wx.MessageBox('Are you sure you want to delete the selected idioms?', 'Question',
                            wx.YES_NO | wx.NO_DEFAULT, parent=self)

        if dlg == wx.NO:
            return
        elif dlg == wx.YES:
            len_data = self.list_idioms.GetItemCount()
            items = [(self.list_idioms.GetItem(i, 1)) for i in range(len_data) if
                     self.list_idioms.IsItemChecked(i)]

            idioms = [(i.Text,) for i in items]
            with db.Idiom() as session:
                session.removes(idioms)
                session.conn.commit()

            for i in items:
                self.list_idioms.DeleteItem(i.GetId())

    def OnAdd(self, e):
        dlg = wx.TextEntryDialog(self, "Add idiom", "Input NEW idiom", "Data...")
        res = dlg.ShowModal()
        if res == wx.ID_OK:
            text = dlg.GetValue()

            with db.Idiom() as session:
                result = session.get(text)

                if result:
                    dlg = wx.MessageBox('Idiom `{}` is exist'.format(result['name']), 'Warning', wx.ICON_EXCLAMATION,
                                        self)
                else:
                    session.insert(text)
                    session.conn.commit()

                    self.StopLoadTable()
                    self.list_idioms.Append((self.list_idioms.GetItemCount() + 1, text))

    def OnRow(self, event: wx.ListEvent):
        item = self.list_idioms.GetItem(event.GetIndex(), 1)
        dlg = wx.TextEntryDialog(self, "Update idiom", "Replace idiom", item.Text)
        res = dlg.ShowModal()
        if res == wx.ID_OK:

            text = dlg.GetValue().strip()

            self.StopLoadTable()
            self.list_idioms.SetItem(item.GetId(), 1, text)

            if not text:
                dlg = wx.MessageBox('Empty line!', 'Update Error', wx.ICON_EXCLAMATION, self)
            else:
                with db.Idiom() as session:
                    session.update(item.Text, text)
                    session.conn.commit()

    def OnSetFont(self, event):
        dlg = wx.FontDialog(self)
        res = dlg.ShowModal()
        if res == wx.ID_OK:
            font = dlg.GetFontData().GetChosenFont()  # wx.Font
            foreground_color = dlg.GetFontData().GetColour()

            self.left_text.SetFont(font=font)
            self.left_text.SetForegroundColour(foreground_color)

            self.right_text.SetFont(font=font)
            self.right_text.SetForegroundColour(foreground_color)

            self.list_idioms.SetFont(font=font)
            self.list_idioms.SetForegroundColour(foreground_color)

    def OnResetDB(self, event):
        os.remove('database/database.sqlite3')
        shutil.copy('database/database_default.sqlite3', 'database/database.sqlite3')
        self.sb.SetStatusText('Database was reset.')

    def onQuit(self, event):
        self.Close()

    def StopLoadTable(self):
        self.stop = True


def main():
    app = wx.App()
    ex = Example(None)
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
