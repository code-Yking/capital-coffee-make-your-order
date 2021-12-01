"""
This is version 1.2.3 Dated: 18/09/2020
This version lacks proper summarisation of size and additives of the drinks.
A cumulative summary has been tried.
"""


# HOW THIS CODE IS STRUCTURED:
#   imports
#   constants:   PRICES, LIMITS, SIZE
#   external functions:  coffee_names(),  additive_names()
#   wx.Panel classes and their respective functions: PickOrDelivery(),

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
        'marshmallows': 2,
        'ice': 2,
        'cinnamon dusting': 0,
        'chocolate dusting': 0
    },
    'delivery': 3
}

ADDITIVES = ['sugar', 'marshmallows', 'ice', 'cinnamon dusting', 'chocolate dusting']

LIMITS = {
    'coffee': 5,
    'sugar': 6,
    'marshmallows': 4
}

SIZE = ['Large', 'Medium', 'Small']

no_coffee = 0


# This function is for generating a list of coffees from the dictionary PRICES
def coffee_names():
    coffee_list = []
    for key in PRICES['coffees']:
        coffee_list.append(key.title())

    return coffee_list


# This function is for generating a list of additives from the dictionary PRICES
def additive_names():
    additive_list = []
    for key in PRICES['additives']:
        additive_list.append(key.title())

    return additive_list


# The Radio Buttons Panel this is part of the Choice() and MainPanel()
# todo invent an organisation system with priorities inside classes
class PickOrDelivery(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        pick_sizer = wx.BoxSizer(wx.VERTICAL)
        s_box = wx.StaticBox(self, 0, 'Choose a serving option')
        s_box_sizer = wx.StaticBoxSizer(s_box, wx.VERTICAL)

        pick_sizer = wx.BoxSizer(wx.HORIZONTAL)
        pick_up_radio = wx.RadioButton(self, label="Pick up", style=wx.RB_GROUP)
        pick_up_radio.Bind(wx.EVT_RADIOBUTTON, lambda evt, serve=0: self.radio_select(evt, serve=serve))
        delivery_radio = wx.RadioButton(self, label="Delivery")
        delivery_radio.Bind(wx.EVT_RADIOBUTTON, lambda evt, serve=1: self.radio_select(evt, serve=serve))
        pick_sizer.Add(pick_up_radio, 0, wx.ALIGN_CENTER, 5)
        pick_sizer.Add(delivery_radio, 0, wx.ALIGN_CENTER, 5)

        s_box_sizer.Add(pick_sizer, 0, wx.ALIGN_CENTRE, 5)
        self.SetSizer(s_box_sizer)

    def radio_select(self, event, serve):
        self.parent.parent.summary_panel.serving = serve
        print(self.parent.parent.summary_panel.serving)
        self.parent.parent.summary_refresh(0)


# todo change property names
# todo make changes to selected/available_additives lists through a(n external) function
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
        self.parent.additives_added = self.parent.additives_added - 1
        self.parent.adjust_additives(self, 1)

        self.Destroy()
        self.parent.Fit()
        self.parent.parent.fit()
        self.parent.selected_additives = list(self.parent.selected_additive())
        self.parent.available_additives = list(set(list(additive_names())) - set(self.parent.selected_additives))
        print("Sel:", self.parent.selected_additives, 'Av:', self.parent.available_additives)
        self.parent.stop_additives()

    def combo_select_option(self, event):
        combo_box = event.GetEventObject()
        if combo_box not in self.parent.default_delete:
            combo_box.Delete(0)
            self.parent.default_delete.append(combo_box)

        self.parent.selected_additives = list(self.parent.selected_additive())

        # difference = list(set(list(additive_names())) - set(self.parent.available_additives))
        # self.parent.available_additives.remove(combo_box.GetValue())
        self.parent.available_additives = list(set(list(additive_names())) - set(self.parent.selected_additives))
        # self.parent.selected_additives.append(combo_box.GetValue())

        # for n in difference:
        #     if n not in self.parent.available_additives:
        #         self.parent.available_additives.append(n)
        #         # self.parent.selected_additives.remove(n)
        print(self.parent.selected_additives, self.parent.available_additives)

        self.parent.adjust_additives(self, 0)
        self.parent.stop_additives()
        # self.parent.parent.parent.summary_refresh(0)


class Coffees(wx.Panel):
    def __init__(self, parent, no=1):
        super().__init__(parent)
        self.parent = parent

        self.available_additives = list(additive_names())  # todo is available needed?
        self.selected_additives = []
        self.additives_added = 0
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

        self.parent.no_coffees = self.parent.no_coffees-1
        self.parent.parent.parent.summary_refresh(0)
        self.parent.parent.fit()

    def remove_default_option(self, event):
        combo_box = event.GetEventObject()
        if combo_box not in self.default_delete:
            combo_box.Delete(0)
            self.default_delete.append(combo_box)

        self.parent.parent.parent.summary_refresh(0)
        self.parent.fit()

    def add_additives(self, event):
        additives_panel = Additives(self)
        self.additives_container.Add(additives_panel, 0, wx.EXPAND, 5)
        self.parent.fit()
        self.additives_added = self.additives_added+1
        self.stop_additives()

    # def remove_additives(self, event, sz):
    #     sz.Destroy()
    # todo split this apart:
    def adjust_additives(self, me, action, diff=None):
        if action == 0:     # This is for updating combobox choices
            for n in self.additives_container.GetChildren():
                additive_instance = n.GetWindow()
                to_remove = me.combo_bx.GetValue()
                # print(to_remove)

                if additive_instance != me:
                    # print(additive_instance.combo_bx.GetValue())
                    remove_index = additive_instance.combo_bx.FindString(to_remove)
                    additive_instance.combo_bx.Delete(remove_index)

                    for i in self.available_additives:
                        if additive_instance.combo_bx.FindString(i) < 0 and n not in self.selected_additives:
                            print(additive_instance.combo_bx.FindString(i))
                            additive_instance.combo_bx.Append(i)

        elif action == 1:      # This is when deleting comboboxs
            print('h')
            for n in self.additives_container.GetChildren():
                additive_instance = n.GetWindow()
                to_add = me.combo_bx.GetValue()
                add_index = me.combo_bx.FindString(to_add)
                # print(add_index)
                # print(to_add)

                if additive_instance != me and to_add != 'Choose additives...':
                    # print(additive_instance.combo_bx.GetValue())
                    remove_index = additive_instance.combo_bx.FindString(to_add)
                    additive_instance.combo_bx.Append(to_add)

                    # print(self.selected_additives, self.available_additives)

    def stop_additives(self):
        if self.additives_added == len(list(additive_names())):
            self.add_additives_btn.Disable()
            # print(self.additives_added)
        elif len(self.available_additives) == 0:
            self.add_additives_btn.Disable()
            print(self.available_additives, self.selected_additives)
        else:
            self.add_additives_btn.Enable()

    def selected_additive(self):
        s_addit = []
        for n in self.additives_container.GetChildren():
            value = n.GetWindow().combo_bx.GetValue()
            s_addit.append(value)
        return s_addit


class CoffeesOuter(scrolled.ScrolledPanel):
    def __init__(self, parent):
        super().__init__(parent, size=(400,200), style=wx.SUNKEN_BORDER)
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

            self.parent.parent.summary_refresh(0)
            self.fit()

            if self.no_coffees == 5:
                event.GetEventObject().Disable()

        else:
            pass

    def fit(self):
        self.parent.SetSize((1, 1))
        self.parent.fit()


# todo make fit() global
class Choices(wx.Panel):
    def __init__(self, parent):
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

        self.btn_sizer.AddStretchSpacer(2)

        self.cancel_btn = wx.Button(self, label='Cancel')
        self.btn_sizer.Add(self.cancel_btn, 1, wx.ALL, 5)

        self.next_btn = wx.Button(self, label='Next')
        self.btn_sizer.Add(self.next_btn, 1, wx.ALL, 5)

        self.choices_sizer.Add(pick_panel, 0, wx.ALIGN_LEFT, 5)
        self.choices_sizer.Add(self.coffees_outer_panel, 0, wx.EXPAND, 5)
        self.choices_sizer.Add(self.btn_sizer, 1, wx.ALIGN_LEFT | wx.EXPAND, 5)

        self.SetSizerAndFit(self.choices_sizer)
        self.coffees_outer_panel.SetSize((1,1))

        # self.add(0)

    def fit(self):
        self.Fit()
        self.parent.Fit()
        # self.parent.summary_panel.Fit()
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

        self.serving = int(0)

    def remove(self):
        for n in self.summary_sizer.GetChildren():
            n.GetWindow().Destroy()

    def add(self, no=1, item=None, amount=0, cost=0):
        self.remove()
        serving_type = ""
        delivery_cost = 0
        if self.serving == 1:
            serving_type = "Delivery"
            delivery_cost = 3
        elif self.serving == 0:
            serving_type = "Pick Up"

        serving_text = wx.StaticText(self, label=serving_type)
        serving_text.SetFont(wx.Font(-1, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.summary_sizer.Add(serving_text, 0, wx.ALIGN_LEFT, 5)

        no_select_coffee_dict = {}
        for i in item:
            if i in no_select_coffee_dict:
                no_select_coffee_dict[i] = no_select_coffee_dict[i] + 1
            else:
                no_select_coffee_dict[i] = 1

        print(no_select_coffee_dict)
        total_coffee: int = 0
        total_price: int = 0

        for n in no_select_coffee_dict:
            if n != '' and n != 'Choose a coffee...':  # todo make the program, independent
                no = no_select_coffee_dict[n]
                total_coffee += no
                price = PRICES['coffees'][n.lower()] * no
                total_price = total_price + price
                txt = wx.StaticText(self, label="{} x{} : ${}".format(n, no, price))
                self.summary_sizer.Add(txt, 0, wx.ALIGN_RIGHT, 5)

        horz_line = wx.StaticLine(self, style=wx.LI_HORIZONTAL)
        self.summary_sizer.Add(horz_line, 0, wx.EXPAND, 5)

        total_txt = wx.StaticText(self, label="Drinks ({}) : ${}".format(total_coffee, total_price))
        self.summary_sizer.Add(total_txt, 0, wx.ALIGN_LEFT, 15)

        gst_price = round(total_price * 1.15, 3)
        gst_txt = wx.StaticText(self, label="With GST (15%) : ${}".format(gst_price))
        self.summary_sizer.Add(gst_txt, 0, wx.ALIGN_LEFT, 15)

        delivery_txt = wx.StaticText(self, label="Delivery Charge : ${}".format(delivery_cost))
        self.summary_sizer.Add(delivery_txt, 0, wx.ALIGN_LEFT, 15)

        horz_line = wx.StaticLine(self, style=wx.LI_HORIZONTAL)
        self.summary_sizer.Add(horz_line, 0, wx.EXPAND, 5)

        grand_total_txt = wx.StaticText(self, label="Grand Total : ${}".format(delivery_cost+gst_price))
        self.summary_sizer.Add(grand_total_txt, 0, wx.ALIGN_RIGHT, 15)

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

