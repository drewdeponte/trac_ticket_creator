#!/usr/bin/python

import xmlrpclib
import wx
import threading

username = "yourusername"
password = "yourpassword"
port = None # if need to specify a port set this to the port number
host = "trac.yourdomain.com"
path = "/your/trac/env/path"

# Do not edit variables below this point if you just want to use the script.
# If you are adding new functionality, please change the code all you want.

url = "https://%s:%s@%s" % (username, password, host) 
if (port):
    url += ":%s" % (str(port))
url += path + "/login/xmlrpc"


class TicketCreator(threading.Thread):
    def __init__(self, t_summary, t_description, t_milestone, t_list, t_list_lock):
        super(TicketCreator, self).__init__()
        self.m = t_milestone
        self.s = t_summary
        self.d = t_description
        self.t_list = t_list
        self.t_list_lock = t_list_lock
    
    def run(self):
        svr = xmlrpclib.ServerProxy(url)
        svr.ticket.create(self.s, self.d, {"type": "task", "milestone": self.m}, True)
        self.t_list_lock.acquire()
        self.t_list.Append((self.m, self.s))
        self.t_list_lock.release()
    

class TicketPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
                
        self.server = xmlrpclib.ServerProxy(url)
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Create the milestone label and drop down
        milestone_box = wx.BoxSizer(wx.HORIZONTAL)
        milestone_label = wx.StaticText(self, wx.ID_ANY, 'Milestone:')
        self.milestone_dropdown = wx.ComboBox(self, -1, style=wx.CB_READONLY)
        self.milestone_dropdown.Bind(wx.EVT_COMBOBOX, self.select_milestone)
        self.populate_milestone_dropdown()
        milestone_box.Add(milestone_label, 0, wx.RIGHT, 8)
        milestone_box.Add(self.milestone_dropdown, 1)
        vbox.Add(milestone_box, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        
        # Create the ticket summary label and box
        summary_box = wx.BoxSizer(wx.HORIZONTAL)
        summary_label = wx.StaticText(self, wx.ID_ANY, "Ticket Description:")
        self.summary_txt_ctrl = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER | wx.TE_MULTILINE)
        self.Bind(wx.EVT_TEXT_ENTER, self.create_ticket)
        summary_box.Add(summary_label, 0, wx.RIGHT, 8)
        summary_box.Add(self.summary_txt_ctrl, 1)
        vbox.Add(summary_box, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        
        # Ticket list box
        ticket_list_box = wx.BoxSizer(wx.HORIZONTAL)
        self.t_list = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.t_list.InsertColumn(0, "Milestone")
        self.t_list.InsertColumn(1, "Ticket Summary")
        self.t_list.SetColumnWidth(0, 100)
        self.t_list.SetColumnWidth(1, 570)
        ticket_list_box.Add(self.t_list, 1, wx.EXPAND)
        vbox.Add(ticket_list_box, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, 15)
        self.t_list_lock = threading.Lock()
                
        self.SetSizer(vbox)
        self.Show(True)
    
    def create_ticket(self, event):
        if (self.current_milestone_index == None):
            print "Select a milestone from the list, move the focus to the text box and press enter to create the ticket."
        else:
            d = event.GetString()
            s = d.split('.')[0]
            m = self.milestones[self.current_milestone_index]
            tc = TicketCreator(s, d, m, self.t_list, self.t_list_lock)
            tc.start()
            self.summary_txt_ctrl.Clear()
    
    def select_milestone(self, event):
        self.current_milestone_index = event.GetSelection()
    
    def populate_milestone_dropdown(self):
        self.milestone_dropdown.Clear()
        self.milestones = self.server.ticket.milestone.getAll()
        for m in self.milestones:
            self.milestone_dropdown.Append(m)
        self.current_milestone_index = None
        

class MainWindow(wx.Frame):
    def __init__(self, parent, id, title):
        super(MainWindow, self).__init__(parent, id, title, size=(700, 350))
        self.parent = parent
        self.id = id
        self. title = title
        tp = TicketPanel(self)
        self.Show(True)
    

app = wx.PySimpleApp()
mw = MainWindow(None, wx.ID_ANY, 'Trac Ticket Creator')
app.MainLoop()