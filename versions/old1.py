"""
This is version 1.2.0 Dated: 17/09/2020
This version lacks proper summarisation of the drinks. 
The size of the window is unfitting.

Coffees can be added. Additives can be added.

"""

import wx
import wx.lib.scrolledpanel as scrolled


'''''CONSTANTS'''''
PRICES = {
    'coffees': {
        '️cappuccino': 4,
        'mochaccino': 4,
        'flat white': 5,
        'café late': 3,
        'espresso': 3,
        'macchiato': 3,
        'ristretto': 3,
        'hot chocolate': 3,
        'chai latte': 4
    },
    'additives': {
        'sugar': 1,
        'marshmallows': 2
    },
    'delivery': 3
}

LIMITS = {
    'coffee': 5,
    'sugar': 6,
    'marshmallows': 4
}

SIZE = ['Large', 'Medium', 'Small']

no_coffee = 0


def coffee_names():
    coffee_list = []
    for key in PRICES['coffees']:
        coffee_list.append(key.title())

    return coffee_list


def additive_names():
    additive_list = []
    for key in PRICES['additives']:
        additive_list.append(key.title())

    return additive_list


class PickOrDelivery(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        pick_sizer = wx.BoxSizer(wx.VERTICAL)
        s_box = wx.StaticBox(self, 0, 'Choose an option')
        s_box_sizer = wx.StaticBoxSizer(s_box, wx.VERTICAL)

        pick_sizer = wx.BoxSizer(wx.HORIZONTAL)
        pick_up_radio = wx.RadioButton(self, label="Pick up", style=wx.RB_GROUP)
        delivery_radio = wx.RadioButton(self, label="Delivery")
        pick_sizer.Add(pick_up_radio, 0, wx.ALIGN_CENTER, 5)
        pick_sizer.Add(delivery_radio, 0, wx.ALIGN_CENTER, 5)

        s_box_sizer.Add(pick_sizer, 0, wx.ALIGN_CENTRE, 5)
        self.SetSizer(s_box_sizer)


class Additives(wx.Panel):
    def __init__(self, parent, no=1):
        super().__init__(parent)
        self.parent = parent

        self.additives_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.combo_bx = wx.ComboBox(self, choices=['Choose additives...'] + self.parent.available_additives)
        self.combo_bx.Bind(wx.EVT_COMBOBOX, self.combo_select_option)
        # static_txt = wx.StaticText(self, label='Amount:')
        text_ctrl = wx.TextCtrl(self, value='')
        remove_btn = wx.Button(self, label='X', size=(40, -1))
        remove_btn.Bind(wx.EVT_BUTTON, self.remove)

        self.additives_sizer.Add(self.combo_bx, 0, wx.ALL, 5)
        # additives_sizer.Add(static_txt, 0, wx.ALL, 5)
        self.additives_sizer.Add(text_ctrl, 0, wx.ALL, 5)
        self.additives_sizer.Add(remove_btn, 0, wx.ALL, 5)

        self.SetSizer(self.additives_sizer)

    def remove(self, event):
        self.Destroy()
        self.parent.Fit()
        self.parent.parent.fit()

    def combo_select_option(self, event):
        combo_box = event.GetEventObject()
        if combo_box not in self.parent.default_delete:
            combo_box.Delete(0)
            self.parent.default_delete.append(combo_box)

        self.parent.available_additives.remove(combo_box.GetValue())
        self.parent.adjust_additives(self, 0)
        # self.parent.parent.parent.summary_refresh(0)


class Coffees(wx.Panel):
    def __init__(self, parent, no=1):
        super().__init__(parent)
        self.parent = parent

        self.available_additives = list(additive_names())

        self.default_delete = []

        s_box = wx.StaticBox(self, 0, 'Coffees No {}'.format(no))
        s_box_sizer = wx.StaticBoxSizer(s_box, wx.VERTICAL)

        coffee_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.size_combo = wx.ComboBox(self, choices=['Sizes...']+SIZE, style=wx.CB_READONLY)
        self.size_combo.Bind(wx.EVT_COMBOBOX, self.remove_default_option)
        self.coffee_combo = wx.ComboBox(self, choices=['Choose a coffee...'] + coffee_names(), style=wx.CB_READONLY)
        self.coffee_combo.Bind(wx.EVT_COMBOBOX, self.remove_default_option)

        self.remove_btn = wx.Button(self, label='Remove')
        self.remove_btn.Bind(wx.EVT_BUTTON, self.remove)

        self.additives_container = wx.BoxSizer(wx.VERTICAL)

        self.add_additives_btn = wx.Button(self, label='Add Additives')
        self.add_additives_btn.Bind(wx.EVT_BUTTON, self.add_additives)
        # additives_sizer.Add(self.additives_container, 0, wx.ALL, 5)
        # additives_sizer.Add(self.add_additives_btn, 0, wx.EXPAND, 5)

        coffee_sizer.Add(self.size_combo, 0, wx.EXPAND, 5)
        coffee_sizer.Add(self.coffee_combo, 0, wx.EXPAND, 5)
        coffee_sizer.Add(self.remove_btn, 0, wx.EXPAND, 5)

        s_box_sizer.Add(coffee_sizer, 0, wx.EXPAND, 5)
        s_box_sizer.Add(self.add_additives_btn, 0, wx.ALIGN_CENTRE, 5)
        s_box_sizer.Add(self.additives_container, 0, wx.EXPAND, 5)
        self.SetSizer(s_box_sizer)

    def remove(self, event):
        self.Destroy()
        # self.parent.fit()
        self.parent.parent.SetSize((1, 1))
        self.parent.parent.fit()
        self.parent.no_coffees = self.parent.no_coffees-1
        self.parent.parent.parent.summary_refresh(0)

    def remove_default_option(self, event):
        combo_box = event.GetEventObject()
        if combo_box not in self.default_delete:
            combo_box.Delete(0)
            self.default_delete.append(combo_box)

        self.parent.parent.parent.summary_refresh(0)

    def add_additives(self, event):
        additives_panel = Additives(self)
        self.additives_container.Add(additives_panel, 0, wx.EXPAND, 5)
        self.parent.fit()

    # def remove_additives(self, event, sz):
    #     sz.Destroy()
    def adjust_additives(self, me, action):
        for n in self.additives_container.GetChildren():
            additive_instance = n.GetWindow()
            to_remove = me.combo_bx.GetValue()
            print(to_remove)
        if action == 0:
            if additive_instance != me:
                print(additive_instance.combo_bx.GetValue())
                remove_index = additive_instance.combo_bx.FindString(to_remove)
                additive_instance.combo_bx.Delete(remove_index)
        pass


class CoffeesOuter(scrolled.ScrolledPanel):
    def __init__(self, parent):
        super().__init__(parent, size=(400,200), style = wx.TAB_TRAVERSAL|wx.SUNKEN_BORDER)
        self.parent = parent
        self.no_coffees = 0
        self.outer_sizer = wx.BoxSizer(wx.VERTICAL)
        # self.SetSize(wx.Size(500, 200))

        # self.coffee_panel = Coffees(self)
        # self.add_btn = wx.Button(self, label='Add')
        # self.add_btn.Bind(wx.EVT_BUTTON, self.add)

        # self.outer_sizer.Add(self.coffee_panel, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(self.outer_sizer)
        self.SetupScrolling()
        # self.SetBackgroundColour('blue')

    def add(self, event):
        if self.no_coffees < 5:
            self.no_coffees = self.no_coffees + 1
            coffees_panel = Coffees(self, self.no_coffees)
            self.outer_sizer.Add(coffees_panel, 0, wx.ALIGN_LEFT, 10)
            # print(self.GetScaleX())
            # print(coffees_panel.GetSize()[0]*self.no_coffees)

            self.Scroll((0, coffees_panel.GetSize()[0]*self.no_coffees))
            self.fit()

            self.parent.parent.summary_refresh(0)

            if self.no_coffees == 5:
                event.GetEventObject().Disable()

        else:
            pass

    def fit(self):
        self.parent.SetSize((1, 1))
        self.parent.fit()


class Choices(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.no_coffees = 0
        self.choices_sizer = wx.BoxSizer(wx.VERTICAL)
        pick_panel = PickOrDelivery(self)
        self.coffees_outer_panel = CoffeesOuter(self)

        self.btn = wx.Button(self, label='Add')
        self.btn.Bind(wx.EVT_BUTTON, self.coffees_outer_panel.add)

        self.choices_sizer.Add(pick_panel, 0, wx.ALIGN_LEFT, 5)
        self.choices_sizer.Add(self.coffees_outer_panel, 0, wx.ALIGN_LEFT, 5)
        self.choices_sizer.Add(self.btn, 0, wx.ALIGN_LEFT, 5)

        self.SetSizerAndFit(self.choices_sizer)
        self.coffees_outer_panel.SetSize((1,1))

        # self.add(0)

    def fit(self):
        self.Fit()
        self.parent.Fit()
        self.parent.parent.Fit()

    def add(self, event):
        if self.no_coffees < 5:
            self.no_coffees = self.no_coffees + 1
            coffees_panel = Coffees(self, self.no_coffees)
            self.choices_sizer.Add(coffees_panel, 0, wx.ALIGN_CENTRE, 10)
            print(self.no_coffees)
        else:
            pass


class Summary(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        s_box = wx.StaticBox(self, 0, 'Summary')
        s_box_sizer = wx.StaticBoxSizer(s_box, wx.VERTICAL)
        self.summary_sizer = wx.BoxSizer(wx.VERTICAL)

        txt = wx.StaticText(self, label="Items:")
        self.summary_sizer.Add(txt, 0, wx.ALIGN_LEFT, 5)

        s_box_sizer.Add(self.summary_sizer, 0, wx.EXPAND, 5)
        self.SetSizer(s_box_sizer)

    def remove(self):
        for n in self.summary_sizer.GetChildren():
            n.GetWindow().Destroy()

    def add(self, no=1, item=None, amount=0, cost=0):
        self.remove()
        for n in item:
            if n != '':
                txt = wx.StaticText(self, label=n)
                self.summary_sizer.Add(txt, 0, wx.ALIGN_CENTRE, 5)
        self.SetSize(0,0)
        self.Fit()
        self.parent.SetSize(0,0)
        self.parent.Fit()


class MainPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        outer_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.summary_panel = Summary(self)
        self.choices_panel = Choices(self)

        main_sizer.Add(self.choices_panel, 5, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(self.summary_panel, 2, wx.EXPAND | wx.ALL, 5)

        outer_sizer.Add(main_sizer, 1, wx.EXPAND, 5)
        # btn = wx.Button(self, label='try')
        # outer_sizer.Add(btn, 1, wx.EXPAND, 5)
        # btn.Bind(wx.EVT_BUTTON, self.summary_refresh)
        self.SetSizer(outer_sizer)

        self.Fit()

    def summary_refresh(self, event):
        summary_coffees = []
        for n in self.choices_panel.coffees_outer_panel.outer_sizer.GetChildren():
            summary_coffees.append(n.GetWindow().coffee_combo.GetValue())
            # self.summary_panel.add(item=n.GetWindow().coffee_combo.GetValue())
        print(summary_coffees)
        self.summary_panel.add(item=summary_coffees)




class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="Coffee Order")
        main_panel = MainPanel(self)
        # main_sizer = wx.BoxSizer(wx.VERTICAL)
        #
        # pick_delivery = PickOrDelivery(main_panel)
        # main_sizer.Add(pick_delivery, 0, wx.EXPAND, 5)
        #
        # main_panel.SetSizer(main_sizer)
        self.Show()
        self.Fit()


if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame()
    app.MainLoop()

