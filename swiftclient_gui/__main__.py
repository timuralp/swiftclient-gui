#!/usr/bin/python

import wxversion
wxversion.select("3.0")
import wx, wx.html
import swiftclient
import sys

aboutText = """<p>Sorry, there is no information about this program. It is
running on version %(wxpy)s of <b>wxPython</b> and %(python)s of <b>Python</b>.
See <a href="http://wiki.wxpython.org">wxPython Wiki</a></p>""" 

# TODO:
# - Store and load settings
#   - Prompt for settings if none exist
# - Show containers for the given settings
#   - List containers?
# - Upload directory/file?
# - Download container/directory

class HtmlWindow(wx.html.HtmlWindow):
    def __init__(self, parent, id, size=(600,400)):
        wx.html.HtmlWindow.__init__(self,parent, id, size=size)
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()

    def OnLinkClicked(self, link):
        wx.LaunchDefaultBrowser(link.GetHref())
        
class AboutBox(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, -1, "About <<project>>",
            style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.RESIZE_BORDER|
                wx.TAB_TRAVERSAL)
        hwin = HtmlWindow(self, -1, size=(400,200))
        vers = {}
        vers["python"] = sys.version.split()[0]
        vers["wxpy"] = wx.VERSION_STRING
        hwin.SetPage(aboutText % vers)
        btn = hwin.FindWindowById(wx.ID_OK)
        irep = hwin.GetInternalRepresentation()
        hwin.SetSize((irep.GetWidth()+25, irep.GetHeight()+10))
        self.SetClientSize(hwin.GetSize())
        self.CentreOnParent(wx.BOTH)
        self.SetFocus()

class TextDropTarget(wx.TextDropTarget):
    def __init__(self, frame, *args, **kwargs):
        super(wx.TextDropTarget, self).__init__(*args, **kwargs)
        self.frame = frame

    def OnDrop(self, x, y):
        print 'dropping'

    def OnDropText(self, x, y, data):
        print 'copying', data


class Frame(wx.Frame):
    def __init__(self, title):
        wx.Frame.__init__(self, None, title=title, pos=(150,150), size=(1024,
        768))
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # TODO: load settings and if none, prompt!
        self.swift = swiftclient.client.Connection(
            authurl='http://localhost:32768/auth/v1.0',
            user = 'test:tester',
            key = 'testing')

        self.swift_status = 'account'

        menuBar = wx.MenuBar()
        menu = wx.Menu()
        m_exit = menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")
        self.Bind(wx.EVT_MENU, self.OnClose, m_exit)
        menuBar.Append(menu, "&File")
        menu = wx.Menu()
        m_about = menu.Append(wx.ID_ABOUT, "&About", "Information about this program")
        self.Bind(wx.EVT_MENU, self.OnAbout, m_about)
        menuBar.Append(menu, "&Help")
        self.SetMenuBar(menuBar)
        
        self.statusbar = self.CreateStatusBar()
 
        dir_split = wx.SplitterWindow(self, -1, size=(1024, -1))
        self.dirctrl = wx.GenericDirCtrl(dir_split, -1, style=wx.DIRCTRL_MULTIPLE)
        drop_target = TextDropTarget(self)
        self.dirctrl.SetDropTarget(drop_target)

        panel = wx.Panel(dir_split)
        box = wx.BoxSizer(wx.VERTICAL)
        self.swift_path_status = wx.StaticText(panel)
        self.set_swift_label()
        box.Add(self.swift_path_status)

        self.item_list = wx.ListCtrl(panel, -1, size=(512, 768),
                                     style=wx.LC_LIST)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnSwiftActivated,
                  self.item_list)
        self.Bind(wx.EVT_LIST_BEGIN_DRAG, self.OnDrag, self.item_list)
        # TODO: prefix/delimiter listing and search
        box.Add(self.item_list, 0, wx.ALL, 10)

        panel.SetSizer(box)
        panel.Layout()
        dir_split.SplitVertically(self.dirctrl, panel)
        self.populate_containers()

    def populate_containers(self):
        # TODO: pagination/scrolling
        self.containers = self.swift.get_account()[1]
        for container in self.containers:
            self.item_list.InsertStringItem(self.item_list.GetItemCount(),
                                            container['name'])

    def set_swift_label(self):
        if self.swift_status == 'account':
            self.swift_path_status.SetLabel('test:tester')
        else:
            self.swift_path_status.SetLabel(self.container['name'])

    def OnDrag(self, event):
        download_key = self.item_list.GetItemText(event.GetIndex())
        python_object = wx.PyTextDataObject(download_key)
        source = wx.DropSource(self.item_list)
        source.SetData(python_object)
        drag_result = source.DoDragDrop(wx.Drag_AllowMove)
        if drag_result == wx.DragError:
            print 'error!'
        elif drag_result == wx.DragNone:
            print 'no accept'
        elif drag_result == wx.DragCopy:
            print 'copy'
        elif drag_result == wx.DragCancel:
            print 'cancel'

    def OnSwiftActivated(self, event):
        if self.swift_status == 'account':
            item_index = self.item_list.GetNextItem(-1, wx.LIST_NEXT_ALL,
                                                    wx.LIST_STATE_SELECTED)
            self.container = self.containers[item_index]
            self.objects = self.swift.get_container(self.container['name'])[1]
            self.item_list.ClearAll()
            for obj in self.objects:
                self.item_list.InsertStringItem(self.item_list.GetItemCount(),
                                                obj['name'])
            self.swift_status = 'container'
            self.set_swift_label()

    def OnClose(self, event):
        self.Destroy()

    def OnAbout(self, event):
        dlg = AboutBox()
        dlg.ShowModal()
        dlg.Destroy()

def main():
    try:
        app = wx.App()   # Error messages go to popup window
        top = Frame("Swift")
        top.Show()
        app.MainLoop()
    except Exception as e:
        print e

if __name__ == '__main__':
    main()
