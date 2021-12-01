"""
Project: Coffee Order
Author: Samuel Kurian

@WARNING: 
This program might need admin privileges to perform some of its functions.
This project is part of a NCEA Level 3 Digital Technologies Assessment.

Final Version:
Version no. : 1.6.3
> Fixed lack of warning when phone no was not number.
> Now shows 2 dp
> Aligned summary to right


 HOW THIS CODE IS STRUCTURED:
   imports
   constants:   PRICES, ADDITIVES, QUANTIZE_ADDITIVES, &c...
   external functions:  coffee_names(),  print_pdf()
   wx.Panel classes and their  methods: PickOrDelivery(),  Additives(), &c...
   main() function
"""

import wx
import wx.lib.scrolledpanel as scrolled
import wx.lib.wordwrap as wordwrap

from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import ast
import subprocess
import os
import re
import datetime
from sys import platform


PRICES = {
    'coffees': {
        'cappuccino': 4.5,
        'mochaccino': 4.5,
        'flat white': 4.5,
        'café late': 4.5,
        'espresso': 4.5,
        'hot chocolate': 4.5,
        'macchiato': 7.0,
        'ristretto': 7.0,
        'chai latte': 7.0,
        'affogato': 7.0,
        'café vienna': 7,
        'cubano': 7
    },
    'delivery': 3,
    'size': {
        # these are the prices added to the regular prices above for each size
        'small': 0,
        'medium': 0.5,
        'large': 1
    }
}

ADDITIVES = ['Sugar', 'Marshmallows', 'Ice',
             'Cinnamon Dusting', 'Chocolate Dusting']

QUANTIZE_ADDITIVES = ['Sugar']

SIZE = ['Large', 'Medium', 'Small']

DEFAULT_SIZE = (700, 500)  # default/min size of the window.


# Generate a list of coffees from the dictionary PRICES
def coffee_names():
    coffee_list = []
    for key in PRICES['coffees']:
        coffee_list.append(key.title())

    return coffee_list


# Print the receipt as PDF into receipts directory
def print_pdf(order_list, serve, phone):
    if serve == 1:
        address = order_list[-1 - bool(phone)].split("\n")
        order_list.pop(-1 - bool(phone))
        order_list += address
    else:
        address = list()

    try:
        os.mkdir('receipts')
    except FileExistsError:
        pass
    except PermissionError:
        wx.MessageBox(
                      'You don\'t seem to have Admin Privileges.\
                       This function wont work.', 
                      'Error',
                      wx.OK | wx.ICON_ERROR)
        return [False, 'Permission Error']

    time = str(datetime.datetime.now()).replace(' ', '_').replace(':', '-')
    max_h = 0
    for n in order_list:
        if len(n) > max_h:
            max_h = len(n)

    _width = (max_h + 2) * 6
    _height = (len(order_list) + 2) * 14

    # setting the pdf location
    if platform == "darwin":
        canvas = Canvas('receipts/' + time + ".pdf",
                        pagesize=(_width, _height))
    elif platform == "win32":
        canvas = Canvas('receipts\\' + time + ".pdf",
                        pagesize=(_width, _height))
    else:
        wx.MessageBox(
            'You don\'t seem to have Windows or MacOS. This function wont work.', 
            'Error',
            wx.OK | wx.ICON_ERROR)
        return [True]

    pdfmetrics.registerFont(TTFont('Verdana', 'Verdana.ttf'))
    canvas.setFont("Verdana", 8)

    i = 1  #
    canvas.drawString(12 * 3, _height - 12 * i, order_list[0])
    i += 1
    no = 1

    for n in order_list[1:(-4 - len(address) - bool(phone))]:
        if n in ADDITIVES or 'Sugar' in n:
            canvas.drawString(12 * 2, _height - 13 * i, n)
        else:
            canvas.drawString(1, _height - 13 * i, "{}. {}".format(no, n))
            no += 1
        i += 1

    i += 1
    for n in order_list[(-4 - len(address) - bool(phone)):]:
        canvas.drawString(12 * 1, _height - 14 * i, n)
        i += 1
    try:
        canvas.save()  # save the pdf
    except PermissionError:
        wx.MessageBox('You don\'t seem to have Admin Privileges. This function \
        wont work.', 'Error',
                      wx.OK | wx.ICON_ERROR)
        return [False, 'Permission Error']

    # open the pdf
    if platform == "win32":
        _p = subprocess.Popen('receipts\\' + time + '.pdf', shell=True)
    elif platform == "darwin":
        _p = subprocess.run(['open', 'receipts/' + time + '.pdf'], check=True)
    else:
        return [False, "OSError"]

    return [True]


# to fit the panel size when an element is added, removed or updated.
def fit(cont):
    try:
        cont.Layout()
    except (AttributeError, RuntimeError):
        pass
    cont_p = cont.parent

    while True:
        try:
            cont_p.Layout()
            cont_p = cont_p.parent
        except (AttributeError, RuntimeError):
            break


# The Radio Buttons Panel
class PickOrDelivery(wx.Panel):
    def __init__(self, parent):
        """Constructor"""

        super().__init__(parent)
        self.parent = parent
        s_box = wx.StaticBox(self, 0, 'Choose a serving option')
        s_box_sizer = wx.StaticBoxSizer(s_box, wx.VERTICAL)

        pick_sizer = wx.BoxSizer(wx.HORIZONTAL)
        pick_up_radio = wx.RadioButton(self, label="Pickup", style=wx.RB_GROUP)
        pick_up_radio.SetValue(1)
        pick_up_radio.Bind(wx.EVT_RADIOBUTTON, lambda evt,
                           serve=0: self.radio_select(evt, serve=serve))
        delivery_radio = wx.RadioButton(self, label="Delivery")
        delivery_radio.Bind(wx.EVT_RADIOBUTTON, lambda evt,
                            serve=1: self.radio_select(evt, serve=serve))
        pick_sizer.Add(pick_up_radio, 0, wx.ALIGN_CENTER, 5)
        pick_sizer.Add(delivery_radio, 0, wx.ALIGN_CENTER, 5)

        s_box_sizer.Add(pick_sizer, 0, wx.ALIGN_CENTRE, 5)
        self.SetSizer(s_box_sizer)

    def radio_select(self, event, serve):
        self.parent.parent.summary_panel.serving = serve
        self.parent.enable(serve)

        self.parent.parent.summary_panel.order_address = \
            self.parent.address_panel.address_txt_ctrl.GetValue()
        self.parent.parent.summary_refresh(0)
        fit(self)


# panel for each additive
class Additives(wx.Panel):
    def __init__(self, parent):
        """Constructor"""
        super().__init__(parent)
        self.parent = parent

        self.additives_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.addit_combo = wx.ComboBox(self, value='Choose additives...',
                                       choices=['Choose additives...']
                                       + self.parent.available_additives,
                                       style=wx.CB_READONLY)
        self.addit_combo.Bind(wx.EVT_COMBOBOX, self.combo_select_option)

        self.num_ctrl = wx.SpinCtrl(self, max=5)
        self.num_ctrl.Bind(
            wx.EVT_SPINCTRL,
            lambda num=0: self.parent.parent.parent.parent.summary_refresh(num)
        )
        self.num_ctrl.Disable()
        remove_btn = wx.Button(self, label='X', style=wx.BU_EXACTFIT)
        remove_btn.Bind(wx.EVT_BUTTON, self.remove)

        self.additives_sizer.Add(self.addit_combo, 0, wx.ALL, 5)

        self.additives_sizer.Add(self.num_ctrl, 0, wx.ALL, 5)
        self.additives_sizer.Add(remove_btn, 0, wx.ALL, 5)

        self.SetSizer(self.additives_sizer)

    # removing an additive
    def remove(self, event):
        self.parent.additives_added = self.parent.additives_added - 1
        self.parent.del_combo(self)

        self.Destroy()
        fit(self)

        # fix up the selected and available additives
        self.parent.selected_additives = list(self.parent.selected_additive())
        self.parent.available_additives = list(
            set(list(ADDITIVES)) - set(self.parent.selected_additives))
        self.parent.stop_additives()
        self.parent.parent.parent.parent.summary_refresh(0)

    # when there is a combobox selection in the additives
    def combo_select_option(self, event):
        combo_box = event.GetEventObject()
        if combo_box not in self.parent.default_delete \
                and combo_box.GetValue() in ADDITIVES:
            combo_box.Delete(0)
            self.parent.default_delete.append(combo_box)

        self.parent.selected_additives = list(self.parent.selected_additive())
        self.parent.available_additives = list(
            set(list(ADDITIVES)) - set(self.parent.selected_additives))

        self.parent.update_combo(self)
        self.parent.stop_additives()

        if combo_box.GetValue() in QUANTIZE_ADDITIVES:
            self.num_ctrl.Enable()
            self.num_ctrl.SetValue(1)
        else:
            self.num_ctrl.SetValue(0)
            self.num_ctrl.Disable()
        self.parent.parent.parent.parent.summary_refresh(0)


# panel for each coffee
class Coffees(wx.Panel):
    def __init__(self, parent, no):
        """Constructor"""

        super().__init__(parent)
        self.parent = parent

        # Defining some variables
        self.available_additives = list(ADDITIVES)
        self.selected_additives = []
        self.additives_added = 0
        self.default_delete = []

        self.s_box = wx.StaticBox(self, 0, 'Coffee No {}'.format(no))
        s_box_sizer = wx.StaticBoxSizer(self.s_box, wx.VERTICAL)

        coffee_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.size_combo = wx.ComboBox(self, value="Sizes...", choices=[
                                      'Sizes...'] + SIZE, style=wx.CB_READONLY)
        self.size_combo.Bind(wx.EVT_COMBOBOX, self.remove_default_option)
        self.coffee_combo = wx.ComboBox(self, value="Choose a coffee...",
                                        choices=['Choose a coffee...']
                                        + coffee_names(), style=wx.CB_READONLY)
        self.coffee_combo.Bind(wx.EVT_COMBOBOX, self.remove_default_option)

        self.remove_btn = wx.Button(self, label='Remove')
        self.remove_btn.Bind(wx.EVT_BUTTON, self.remove)

        self.additives_container = wx.BoxSizer(wx.VERTICAL)

        self.add_additives_btn = wx.Button(self, label='Add Additives')
        self.add_additives_btn.Bind(wx.EVT_BUTTON, self.add_additives)

        coffee_sizer.Add(self.size_combo, 0, wx.EXPAND, 5)
        coffee_sizer.Add(self.coffee_combo, 0, wx.EXPAND, 5)
        coffee_sizer.Add(self.remove_btn, 0, wx.EXPAND, 5)

        s_box_sizer.Add(coffee_sizer, 0, wx.ALIGN_CENTRE, 5)
        s_box_sizer.Add(self.add_additives_btn, 0, wx.ALIGN_CENTRE, 5)
        s_box_sizer.Add(self.additives_container, 0, wx.ALIGN_CENTRE, 5)
        self.SetSizer(s_box_sizer)

    # remove a drink
    def remove(self, event):
        self.Destroy()
        self.parent.no_coffees = self.parent.no_coffees - 1
        self.parent.parent.parent.summary_refresh(0)
        self.parent.refresh_no()
        self.parent.add_default()

        if self.parent.no_coffees == 0:
            self.parent.parent.reset_btn.Disable()
        else:
            self.parent.parent.reset_btn.Enable()
        fit(self)

    # removing the default option in the combobox
    def remove_default_option(self, event):
        combo_box = event.GetEventObject()
        if combo_box not in self.default_delete and combo_box.GetValue() in\
                coffee_names() + SIZE:
            combo_box.Delete(0)
            self.default_delete.append(combo_box)

        self.parent.parent.parent.summary_refresh(0)
        fit(self)

    # adding an additive into the sizer
    def add_additives(self, event):
        additives_panel = Additives(self)
        self.additives_container.Add(additives_panel, 0, wx.ALIGN_CENTRE, 5)
        fit(self)
        self.additives_added = self.additives_added + 1
        self.stop_additives()

    # updating combobox choices to prevent duplicates
    def update_combo(self, me):
        for n in self.additives_container.GetChildren():
            additive_instance = n.GetWindow()
            to_remove = me.addit_combo.GetValue()

            if additive_instance != me:
                remove_index = additive_instance.addit_combo.FindString(
                    to_remove)
                additive_instance.addit_combo.Delete(remove_index)

                for i in self.available_additives:
                    if additive_instance.addit_combo.FindString(i) < 0 and\
                            n not in self.selected_additives:
                        additive_instance.addit_combo.Append(i)

    # appending combo box choices when an additive is removed
    def del_combo(self, me):
        for n in self.additives_container.GetChildren():
            additive_instance = n.GetWindow()
            to_add = me.addit_combo.GetValue()

            if additive_instance != me and to_add in ADDITIVES:
                additive_instance.addit_combo.Append(to_add)

    # disable/enable 'Add Additives' button
    def stop_additives(self):
        if self.additives_added == len(list(ADDITIVES)):
            self.add_additives_btn.Disable()
        elif len(self.available_additives) == 0:
            self.add_additives_btn.Disable()
        else:
            self.add_additives_btn.Enable()

    # generate a list of all selected additives
    def selected_additive(self):
        s_addit = []
        for n in self.additives_container.GetChildren():
            value = n.GetWindow().addit_combo.GetValue()
            s_addit.append(value)
        return s_addit


# container for all the coffee panels
class CoffeesOuter(scrolled.ScrolledPanel):
    def __init__(self, parent):
        """Constructor"""
        super().__init__(parent, size=(400, 200), style=wx.SUNKEN_BORDER)

        # panel to hold all the coffees that are added.
        self.parent = parent
        self.no_coffees = 0
        self.outer_sizer = wx.BoxSizer(wx.VERTICAL)

        self.intro_txt = wx.StaticText(self, label="As coffees are added they will be found here.",
                                       style=wx.ALIGN_CENTRE)
        self.outer_sizer.Add(self.intro_txt, 1, wx.EXPAND, 5)

        self.SetSizer(self.outer_sizer)
        self.SetupScrolling()

    # add a drink
    def add(self, event):
        if self.intro_txt:
            self.intro_txt.Destroy()
        if self.no_coffees < 5:
            self.no_coffees = self.no_coffees + 1
            coffees_panel = Coffees(self, self.no_coffees)
            self.outer_sizer.Add(coffees_panel, 0, wx.EXPAND, 10)

            self.ShouldScrollToChildOnFocus(coffees_panel)

            self.parent.parent.summary_refresh(0)

            self.add_limit_check()
            self.parent.reset_btn.Enable()
            fit(self)

    def add_limit_check(self):
        if self.no_coffees == 5:
            self.parent.btn.Disable()
        else:
            self.parent.btn.Enable()

    # reset the coffees panel ie remove all drinks
    def reset(self, event):
        for n in self.outer_sizer.GetChildren():
            n.GetWindow().Destroy()
            self.no_coffees = 0
        self.parent.parent.summary_refresh(0)
        self.add_default()
        self.add_limit_check()
        self.parent.reset_btn.Disable()
        fit(self)

    # sets the default message if no other drinks
    def add_default(self):
        if len(self.outer_sizer.GetChildren()) == 0:
            self.intro_txt = wx.StaticText(self, label="As coffees are added \
            they will be found here.",
                                           style=wx.ALIGN_CENTRE)
            self.outer_sizer.Add(self.intro_txt, 1, wx.EXPAND, 5)

    # refresh the drink number in the heading of each drink if there is change
    def refresh_no(self):
        i = 1
        for n in self.outer_sizer.GetChildren():
            n.GetWindow().s_box.SetLabel('Coffee No {}'.format(i))
            i += 1
        self.add_limit_check()


# panel for customer details
class AddressPanel(wx.Panel):
    def __init__(self, parent):
        """Constructor"""

        super().__init__(parent)
        self.parent = parent

        s_box = wx.StaticBox(self, 0, 'Add customer details')
        s_box_sizer = wx.StaticBoxSizer(s_box, wx.VERTICAL)

        outer_sizer = wx.BoxSizer(wx.VERTICAL)

        name_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.name_stc_txt = wx.StaticText(self, label='Name: ')
        self.name_txt_ctrl = wx.TextCtrl(self)
        self.phone_stc_txt = wx.StaticText(self, label='Phone (optional): ')
        self.phone_txt_ctrl = wx.TextCtrl(self)
        name_sizer.Add(self.name_stc_txt, 0, wx.ALL, 5)
        name_sizer.Add(self.name_txt_ctrl, 0, wx.ALL, 5)
        name_sizer.Add(self.phone_stc_txt, 0, wx.ALL, 5)
        name_sizer.Add(self.phone_txt_ctrl, 1, wx.ALL, 5)

        address_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.address_stc_txt = wx.StaticText(self, label='Address: ')
        self.address_txt_ctrl = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        address_sizer.Add(self.address_stc_txt, 0, wx.ALL, 5)
        address_sizer.Add(self.address_txt_ctrl, 1, wx.ALL | wx.EXPAND, 5)

        set_btn = wx.Button(self, label='Set')
        set_btn.Bind(wx.EVT_BUTTON, self.change_details)

        outer_sizer.Add(name_sizer, 1, wx.ALL | wx.EXPAND, 0)
        outer_sizer.Add(address_sizer, 2, wx.ALL | wx.EXPAND, 0)
        outer_sizer.Add(set_btn, 0, wx.ALL, 0)

        s_box_sizer.Add(outer_sizer, 0, wx.EXPAND, 5)
        self.SetSizer(s_box_sizer)

        self.address_stc_txt.Disable()
        self.address_txt_ctrl.Disable()

    # validating name, phone and address
    def change_details(self, event):
        name = self.name_txt_ctrl
        address = self.address_txt_ctrl
        phone = self.phone_txt_ctrl

        phone_no = str('')

        # checks if empty
        if name.GetValue() == '':
            wx.MessageBox('Please insert Name', 'Error', wx.OK | wx.ICON_ERROR)
            name.SetFocus()
            return

        if address.IsEnabled():
            if address.GetValue() == '':
                wx.MessageBox('Please insert Address',
                              'Error', wx.OK | wx.ICON_ERROR)
                address.SetFocus()
                return

        # validating phone number according to New Zealand Phone Numbers.
        # 7-9 digits after the initial 0

        
        
        if len(phone.GetValue()) > 0:
            try:
                phone_no_trial = int(phone.GetValue())
            except:
                wx.MessageBox('Please insert proper number',
                                  'Error', wx.OK | wx.ICON_ERROR)
                phone.SetFocus()
                return
            
            if phone.GetValue()[0] == str(0):
                if len(phone.GetValue()) not in range(9, 12):
                    wx.MessageBox('Please insert proper number',
                                  'Error', wx.OK | wx.ICON_ERROR)
                    phone.SetFocus()
                    return
                else:
                    phone_no = str(phone.GetValue())
            else:
                if len(phone.GetValue()) not in range(8, 11):
                    wx.MessageBox('Please insert proper number',
                                  'Error', wx.OK | wx.ICON_ERROR)
                    phone.SetFocus()
                    return
                else:
                    phone_no = str(str(0) + str(phone.GetValue()))

        # checks for the presence of prohibited characters
        if re.search(r'[^a-zA-Z\s]', name.GetValue()):
            wx.MessageBox('Please insert proper name. No special characters',
                          'Error', wx.OK | wx.ICON_ERROR)
            name.SetFocus()
            return

        if re.search(r'[^0-9a-zA-Z-.,\s]', address.GetValue()):
            wx.MessageBox('Please insert proper address. No special characters\
                          ', 'Error', wx.OK | wx.ICON_ERROR)
            address.SetFocus()
            return

        # obtaining the address in one line from the multiline textbox
        address_value = ''
        for n in range(address.GetNumberOfLines()):
            if len(address.GetLineText(n)) == 0:
                continue
            if re.search(r'[^\s]', address.GetLineText(n)):
                if len(address_value) > 0:
                    address_value = address_value + " " + \
                        re.sub(r"\B\s\s+", "", address.GetLineText(n))
                else:
                    address_value = address.GetLineText(n)

        self.parent.parent.summary_panel.order_address = address_value
        self.parent.parent.summary_panel.order_name = name.GetValue()
        self.parent.parent.summary_panel.order_phone = str(phone_no)
        self.parent.parent.summary_refresh(0)

    # enables part(s) of the panel according to conditions
    def enable(self, serve):
        self.Enable()
        if serve == 1:
            self.address_stc_txt.Enable()
            self.address_txt_ctrl.Enable()
        else:
            self.address_stc_txt.Disable()
            self.address_txt_ctrl.Disable()
            self.address_txt_ctrl.SetValue('')
            self.parent.parent.summary_panel.choice_address = ''
        self.name_stc_txt.Enable()
        self.name_txt_ctrl.Enable()


# parent panel of PickOrDelivery, CoffeesOuter, AddressPanel
class Choices(wx.Panel):
    def __init__(self, parent):
        """Constructor"""

        super().__init__(parent)
        self.parent = parent
        self.no_coffees = 0

        self.choices_sizer = wx.BoxSizer(wx.VERTICAL)
        pick_panel = PickOrDelivery(self)
        self.coffees_outer_panel = CoffeesOuter(self)

        self.btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btn = wx.Button(self, label='Add')
        self.btn.Bind(wx.EVT_BUTTON, self.coffees_outer_panel.add)
        self.btn_sizer.Add(self.btn, 1, wx.ALL | wx.ALIGN_LEFT, 5)

        self.reset_btn = wx.Button(self, label='Reset')
        self.reset_btn.Bind(wx.EVT_BUTTON, self.coffees_outer_panel.reset)
        self.btn_sizer.Add(self.reset_btn, 1, wx.ALL, 5)

        self.btn_sizer.AddStretchSpacer(2)

        self.address_panel = AddressPanel(self)

        self.btn_sizer_defaults = wx.BoxSizer(wx.HORIZONTAL)

        self.finish_btn = wx.Button(self, label='Finish')
        self.finish_btn.Bind(wx.EVT_BUTTON, self.finish)
        self.btn_sizer_defaults.Add(self.finish_btn, 1, wx.LEFT, 5)

        self.cancel_btn = wx.Button(self, label='Cancel')
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.cancel_box)
        self.btn_sizer_defaults.Add(self.cancel_btn, 1, wx.LEFT, 5)

        # Adding components into choices_sizer
        self.choices_sizer.Add(pick_panel, 1, wx.ALIGN_LEFT, 5)
        self.choices_sizer.Add(self.coffees_outer_panel,
                               5, wx.EXPAND | wx.ALL, 5)
        self.choices_sizer.Add(self.btn_sizer, 1, wx.ALIGN_LEFT, 5)
        self.choices_sizer.Add(self.address_panel, 1, wx.ALL | wx.EXPAND, 5)
        self.choices_sizer.Add(self.btn_sizer_defaults,
                               0, wx.ALL | wx.ALIGN_RIGHT, 5)

        self.SetSizer(self.choices_sizer)

        self.finish_btn.Disable()
        self.reset_btn.Disable()

    # Enable parts of this panel
    def enable(self, serve):
        self.coffees_outer_panel.Enable()
        self.btn.Enable()
        self.address_panel.enable(serve)

    # finishing the order
    def finish(self, event):
        if wx.MessageBox('Are you done?', 'Finish',
                         wx.YES_NO | wx.ICON_QUESTION) == wx.NO:
            return

        if wx.MessageBox('Do you want a PDF receipt?', 'Receipt',
                         wx.YES_NO | wx.ICON_QUESTION) == wx.NO:
            self.ending()
            return

        to_print = []
        for n in self.parent.summary_panel.summary_sizer.GetChildren():
            if type(n.GetWindow()) == wx.StaticText:
                to_print.append(n.GetWindow().GetLabel())

        print_state = print_pdf(
            to_print, self.parent.summary_panel.serving,
            self.parent.summary_panel.order_phone)

        if print_state[0]:  # sends to the printing department
            self.ending()
        else:
            if wx.MessageBox('Do you want to close and restart with \
            Admin Rights?',
                             'There was a {}'.format(print_state[1]),
                             wx.YES_NO | wx.ICON_QUESTION) == wx.NO:
                self.ending()
            else:
                self.parent.parent.Destroy()

    # destroying the current instance and creating a new one.
    def ending(self):
        self.parent.parent.Destroy()
        MainFrame(self.parent.parent.GetSize(),
                  self.parent.parent.GetScreenPosition().Get())

    # asking whether to cancel
    def cancel_box(self, event):
        if wx.MessageBox(
                         'Are you sure to close this application without saving?', 
                         'Warning',
                         wx.YES_NO | wx.ICON_WARNING) == wx.YES:
            self.parent.parent.Destroy()


# panel that shows the overview of the order
class Summary(wx.Panel):
    def __init__(self, parent):
        """Constructor"""

        super().__init__(parent)
        self.parent = parent
        s_box = wx.StaticBox(self, 0, 'Summary')
        s_box_sizer = wx.StaticBoxSizer(s_box, wx.VERTICAL)
        self.summary_sizer = wx.BoxSizer(wx.VERTICAL)

        self.add_default()

        s_box_sizer.Add(self.summary_sizer, 0, wx.EXPAND, 5)
        self.SetSizer(s_box_sizer)

        self.serving = int(0)
        self.order_name = ''
        self.order_address = ''
        self.order_phone = ''

    # destroy everything in the sizer
    def remove(self):
        for n in self.summary_sizer.GetChildren():
            n.GetWindow().Destroy()

    # adds the default message
    def add_default(self):
        intro_txt = wx.StaticText(self,
                                  label="As coffees are selected their \
overview would be found here",
                                  style=wx.ALIGN_CENTRE)
        intro_txt.Wrap(170)
        self.summary_sizer.Add(intro_txt, 0, wx.ALIGN_CENTRE, 5)

    # append (and calculate) all the user inputs into the final preview.
    def add(self, drink_dict=None):
        self.remove()  # clear the entire panel

        if len(drink_dict) == 0:  # prevent showing 0 drinks
            self.add_default()
            fit(self)
            self.parent.choices_panel.finish_btn.Disable()
            return
        elif len(self.order_name) != 0 and len(self.order_address) != 0\
                and self.serving == 1:
            self.parent.choices_panel.finish_btn.Enable()
        elif len(self.order_name) != 0 and self.serving == 0:
            self.parent.choices_panel.finish_btn.Enable()
        else:
            self.parent.choices_panel.finish_btn.Disable()

        # set the delivery cost
        if self.serving == 1:
            delivery_cost = 3
        else:
            delivery_cost = 0

        # to prevent unfinished title
        if self.order_name == '':
            name = 'Order'
        else:
            name = self.order_name.title() + "'s Order"

        serving_text = wx.StaticText(self, label=name)
        serving_text.SetFont(wx.Font(-1, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.summary_sizer.Add(serving_text, 0, wx.ALIGN_CENTRE, 5)

        # checking for duplicated, and grouping them in a dictionary
        reverse_drink_dict = {}
        for key, value in drink_dict.items():
            reverse_drink_dict.setdefault(repr(value), set()).add(key)

        # making the final list of drinks for printing into the summary panel
        # with Schema : [[ 'drink', 'size', { 'additive': amount,..},amount ],]
        non_repeats_list = [
            key for key, values in reverse_drink_dict.items()
            if len(values) == 1]
        repeat_dict = {key: len(
            values) for key, values in reverse_drink_dict.items()
            if len(values) > 1}

        all_list = [ast.literal_eval(r) + [n] for r, n in repeat_dict.items()]\
            + [ast.literal_eval(r) + [1] for r in non_repeats_list]

        total_coffee = 0
        total_price = 0

        # inserting as Static Texts into Summary Sizer
        for item in all_list:
            name = item[0]
            size = item[1]
            additives = item[2]
            times = item[3]
            price = (PRICES['coffees'][name.lower()] +
                     PRICES['size'][size.lower()]) * times

            if times > 1:
                name_txt = wx.StaticText(
                    self, label="{} {} x{} : ${:.2f}".format(size, name, times, 
                                                         price))
            else:
                name_txt = wx.StaticText(
                    self, label="{} {} : ${:.2f}".format(size, name, price))

            self.summary_sizer.Add(name_txt, 0, wx.ALIGN_RIGHT | wx.UP, 5)

            for ad, am in additives.items():
                if am > 0:
                    additives_txt = wx.StaticText(
                        self, label="{} x{}".format(ad, am))
                else:
                    additives_txt = wx.StaticText(self, label="{}".format(ad))
                self.summary_sizer.Add(additives_txt, 0, wx.ALIGN_RIGHT, 5)

            total_coffee += times
            total_price += price

        horz_line = wx.StaticLine(self, style=wx.LI_HORIZONTAL)
        self.summary_sizer.Add(horz_line, 0, wx.EXPAND, 5)

        total_txt = wx.StaticText(
            self, label="Drinks ({}) : ${:.2f}".format(total_coffee, total_price))
        self.summary_sizer.Add(total_txt, 0, wx.ALIGN_RIGHT | wx.UP, 10)

        gst_price = round(total_price * 1.15, 2)
        gst_txt = wx.StaticText(
            self, label="With GST (15%) : ${:.2f}".format(gst_price))
        self.summary_sizer.Add(gst_txt, 0, wx.ALIGN_RIGHT, 15)

        delivery_txt = wx.StaticText(
            self, label="Delivery Charge : ${:.2f}".format(delivery_cost))
        self.summary_sizer.Add(delivery_txt, 0, wx.ALIGN_RIGHT, 15)

        horz_line = wx.StaticLine(self, style=wx.LI_HORIZONTAL)
        self.summary_sizer.Add(horz_line, 0, wx.EXPAND, 5)

        grand_total_txt = wx.StaticText(
            self, label="Grand Total : ${:.2f}".format(delivery_cost + gst_price))
        grand_total_txt.SetFont(wx.Font(-1, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.summary_sizer.Add(grand_total_txt, 0, wx.ALIGN_RIGHT | wx.UP, 10)

        # to prevent blank address
        if self.order_address != '':
            address_txt = wx.StaticText(self, label="Address: {}"
                                        .format(wordwrap.wordwrap(
                                                    self.order_address, 170,
                                                    wx.ClientDC(self))))
            address_txt.Wrap(170)
            self.summary_sizer.Add(address_txt, 0, wx.ALIGN_LEFT | wx.UP, 15)

        if self.order_phone != '':
            phone_txt = wx.StaticText(self, label="Phone: {}\
            ".format(wordwrap.wordwrap(self.order_phone, 170,
                                       wx.ClientDC(self))))
            phone_txt.Wrap(170)
            self.summary_sizer.Add(phone_txt, 0, wx.ALIGN_LEFT | wx.UP, 15)
        fit(self)


class MainPanel(wx.Panel):
    def __init__(self, parent):
        """
        Constructor
        This method for constructing a main panel which holds all other panels.
        """
        super().__init__(parent)
        self.parent = parent
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.summary_panel = Summary(self)
        self.choices_panel = Choices(self)

        main_sizer.Add(self.choices_panel, 5, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(self.summary_panel, 2, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(main_sizer)

    # create a dictionary of all selected drinks and call method insummarypanel
    def summary_refresh(self, event):
        # Schema: { No: [ 'drink', 'size', { 'additive': amount,... } ],... }
        selected_drinks = {}

        # Add to  selected_drinks according to schema
        i = 1
        for n in self.choices_panel.\
                coffees_outer_panel.outer_sizer.GetChildren():
            if type(n.GetWindow()) != wx.StaticText:
                drink = n.GetWindow().coffee_combo.GetValue()
                size = n.GetWindow().size_combo.GetValue()

                # to prevent default messages
                if drink.lower() in PRICES['coffees'] and size in SIZE:
                    prop_list = [drink, size]
                    selected_additives = {}

                    for p in n.GetWindow().additives_container.GetChildren():
                        if p.GetWindow().addit_combo.GetValue() not\
                                in ADDITIVES:
                            continue
                        if p.GetWindow().num_ctrl.IsEnabled()\
                                and p.GetWindow().num_ctrl.GetValue() == 0:
                            pass
                        else:
                            selected_additives[p.GetWindow(
                            ).addit_combo.GetValue(
                            )] = p.GetWindow().num_ctrl.GetValue()

                    prop_list.append(selected_additives)
                    selected_drinks[i] = prop_list
                    i += 1

        self.summary_panel.add(drink_dict=selected_drinks)


class MainFrame(wx.Frame):
    def __init__(self, size, pos):
        """
        This is the Main wx.Frame Window into which all the other wx.Panels are 
        added.
        This method is called to create the generic layout for the application
        """
        super().__init__(parent=None, title="Coffee Order", size=size, pos=pos)
        self.panel = MainPanel(self)
        self.Show()
        self.SetMinSize(DEFAULT_SIZE)

        # to show the warning when tried to close
        self.Bind(wx.EVT_CLOSE, self.panel.choices_panel.cancel_box)


def main(size=DEFAULT_SIZE, pos=wx.DefaultPosition):
    app = wx.App()
    MainFrame(size, pos)
    app.MainLoop()


if __name__ == '__main__':
    main()

# # # # # End of Code # # # # #

