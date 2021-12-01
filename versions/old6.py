# HOW THIS CODE IS STRUCTURED:
#   imports
#   constants:   PRICES, LIMITS, SIZE
#   external functions:  coffee_names(),  ADDITIVES
#   wx.Panel classes and their respective functions: PickOrDelivery(),

import wx
import wx.lib.scrolledpanel as scrolled
import wx.lib.masked as masked
import copy
import ast


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

ADDITIVES = ['Sugar', 'Marshmallows', 'Ice', 'Cinnamon Dusting', 'Chocolate Dusting']

QUANTIZE_ADDITIVES = ['Sugar']

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
# def additive_names():
#     additive_list = []
#     for key in PRICES['additives']:
#         additive_list.append(key.title())
#
#     return additive_list


# class AddressFrame(wx.Frame):
#     def __init__(self, parent):
#         super().__init__(parent, title="Coffee Order")
#         self.parent = parent
#
#         outer_panel = wx.Panel(self)
#         outer_sizer = wx.BoxSizer(wx.HORIZONTAL)
#
#         self.address_panel = AddressPanel(outer_panel)
#         self.summary_panel = copy.deepcopy(self.parent.parent.summary_panel)
#
#         outer_sizer.Add(self.address_panel, 5, wx.EXPAND | wx.ALL, 5)
#         outer_sizer.Add(self.summary_panel, 2, wx.EXPAND | wx.ALL, 5)
#
#         outer_panel.SetSizer(outer_sizer)


# The Radio Buttons Panel this is part of the Choice() and MainPanel()
# todo invent an organisation system with priorities inside classes
class PickOrDelivery(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        # pick_sizer = wx.BoxSizer(wx.VERTICAL)
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
        self.parent.enable(serve)
        # self.parent.SetSize((1, 1))
        self.parent.Fit()
        # self.parent.parent.SetSize((1, 1))
        self.parent.parent.Fit()
        # self.parent.parent.parent.SetSize((1, 1))
        self.parent.parent.parent.Fit()


# todo change property names
# todo make changes to selected/available_additives lists through a(n external) function
class Additives(wx.Panel):
    def __init__(self, parent, no=1):
        super().__init__(parent)
        self.parent = parent

        self.additives_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.combo_bx = wx.ComboBox(self, choices=['Choose additives...'] + self.parent.available_additives,
                                    style=wx.CB_READONLY)
        self.combo_bx.Bind(wx.EVT_COMBOBOX, self.combo_select_option)
        # static_txt = wx.StaticText(self, label='Amount:')
        # text_ctrl = wx.TextCtrl(self, value='')

        self.num_ctrl = wx.SpinCtrl(self)
        self.num_ctrl.Bind(wx.EVT_SPINCTRL, lambda num=0: self.parent.parent.parent.parent.summary_refresh(num))
        self.num_ctrl.Disable()
        remove_btn = wx.Button(self, label='X', size=(40, -1))
        remove_btn.Bind(wx.EVT_BUTTON, self.remove)

        self.additives_sizer.Add(self.combo_bx, 0, wx.ALL, 5)
        # additives_sizer.Add(static_txt, 0, wx.ALL, 5)
        self.additives_sizer.Add(self.num_ctrl, 0, wx.ALL, 5)
        self.additives_sizer.Add(remove_btn, 0, wx.ALL, 5)

        self.SetSizer(self.additives_sizer)

    def remove(self, event):
        self.parent.additives_added = self.parent.additives_added - 1
        self.parent.adjust_additives(self, 1)

        self.Destroy()
        self.parent.Fit()
        self.parent.parent.fit()
        self.parent.selected_additives = list(self.parent.selected_additive())
        self.parent.available_additives = list(set(list(ADDITIVES)) - set(self.parent.selected_additives))
        print("Sel:", self.parent.selected_additives, 'Av:', self.parent.available_additives)
        self.parent.stop_additives()

    def combo_select_option(self, event):
        combo_box = event.GetEventObject()
        if combo_box not in self.parent.default_delete:
            combo_box.Delete(0)
            self.parent.default_delete.append(combo_box)

        self.parent.selected_additives = list(self.parent.selected_additive())

        # difference = list(set(list(ADDITIVES)) - set(self.parent.available_additives))
        # self.parent.available_additives.remove(combo_box.GetValue())
        self.parent.available_additives = list(set(list(ADDITIVES)) - set(self.parent.selected_additives))
        # self.parent.selected_additives.append(combo_box.GetValue())

        # for n in difference:
        #     if n not in self.parent.available_additives:
        #         self.parent.available_additives.append(n)
        #         # self.parent.selected_additives.remove(n)
        print(self.parent.selected_additives, self.parent.available_additives)

        self.parent.adjust_additives(self, 0)
        self.parent.stop_additives()

        if combo_box.GetValue() in QUANTIZE_ADDITIVES:
            self.num_ctrl.Enable()
        else:
            self.num_ctrl.SetValue(0)
            self.num_ctrl.Disable()
        self.parent.parent.parent.parent.summary_refresh(0)


class Coffees(wx.Panel):
    def __init__(self, parent, no=1):
        super().__init__(parent)
        self.parent = parent

        self.available_additives = list(ADDITIVES)
        self.selected_additives = []
        self.additives_added = 0
        self.default_delete = []

        s_box = wx.StaticBox(self, 0, 'Coffees No {}'.format(no))  # todo fix coffee no on re-input
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
        if self.additives_added == len(list(ADDITIVES)):
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


# todo update coffee numbers
class CoffeesOuter(scrolled.ScrolledPanel):
    def __init__(self, parent):
        super().__init__(parent, size=(400,200), style=wx.SUNKEN_BORDER)
        self.parent = parent
        self.no_coffees = 0
        self.outer_sizer = wx.BoxSizer(wx.VERTICAL)

        # self.intro_txt = wx.StaticText(self, label="As coffees are added they will be found here.")
        # # print(self.GetSize())
        # # intro_txt.Wrap(170)
        # self.outer_sizer.Add(self.intro_txt, 0, wx.ALIGN_CENTRE, 5)
        self.add_default()
        # self.SetSize(wx.Size(500, 200))

        # self.coffee_panel = Coffees(self)
        # self.add_btn = wx.Button(self, label='Add')
        # self.add_btn.Bind(wx.EVT_BUTTON, self.add)

        # self.outer_sizer.Add(self.coffee_panel, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(self.outer_sizer)
        self.SetupScrolling()
        # self.SetBackgroundColour('blue')

    def add(self, event):
        if self.intro_txt:
            self.intro_txt.Destroy()
        if self.no_coffees < 5:
            self.no_coffees = self.no_coffees + 1
            coffees_panel = Coffees(self, self.no_coffees)
            self.outer_sizer.Add(coffees_panel, 0, wx.ALIGN_CENTRE, 10)
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

    def reset(self, event):
        for n in self.outer_sizer.GetChildren():
            print(n.GetWindow())
            n.GetWindow().Destroy()
            self.no_coffees = 0
        self.parent.parent.summary_refresh(0)
        self.add_default()

    def add_default(self):
        self.intro_txt = wx.StaticText(self, label="As coffees are added they will be found here.",
                                       style=wx.ALIGN_CENTRE)
        self.outer_sizer.Add(self.intro_txt, 1, wx.EXPAND, 5)


class AddressPanel(wx.Panel):  # todo move this down till choices()
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        s_box = wx.StaticBox(self, 0, 'Add customer details')
        s_box_sizer = wx.StaticBoxSizer(s_box, wx.VERTICAL)

        outer_sizer = wx.BoxSizer(wx.VERTICAL)

        name_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.name_stc_txt = wx.StaticText(self, label='Name: ')
        self.name_txt_cntrl = wx.TextCtrl(self)
        self.name_txt_cntrl.Bind(wx.EVT_TEXT, self.change_name)
        name_sizer.Add(self.name_stc_txt, 0, wx.ALL, 5)
        name_sizer.Add(self.name_txt_cntrl, 0, wx.ALL, 5)

        address_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.address_stc_txt = wx.StaticText(self, label='Address: ')
        self.address_txt_cntrl = wx.TextCtrl(self, style=wx.HSCROLL)
        address_sizer.Add(self.address_stc_txt, 1, wx.ALL, 5)
        address_sizer.Add(self.address_txt_cntrl, 5, wx.ALL | wx.EXPAND, 5)

        outer_sizer.Add(name_sizer, 0, wx.ALL, 0)
        outer_sizer.Add(address_sizer, 0, wx.ALL, 0)

        # self.SetBackgroundColour('blue')
        s_box_sizer.Add(outer_sizer, 0, wx.EXPAND, 5)
        self.SetSizer(s_box_sizer)

        self.address_stc_txt.Disable()
        self.address_txt_cntrl.Disable()

    def change_name(self, event):
        self.parent.parent.summary_panel.serve_name = self.name_txt_cntrl.GetValue() + '\'s Order'
        print(self.parent.parent.summary_panel.serve_name)
        self.parent.parent.summary_refresh(0)

    def enable(self, serve):
        self.Enable()
        if serve == 1:
            self.address_stc_txt.Enable()
            self.address_txt_cntrl.Enable()
        else:
            self.address_stc_txt.Disable()
            self.address_txt_cntrl.Disable()
        self.name_stc_txt.Enable()
        self.name_txt_cntrl.Enable()


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

        self.reset_btn = wx.Button(self, label='Reset')
        self.reset_btn.Bind(wx.EVT_BUTTON, self.coffees_outer_panel.reset)
        self.btn_sizer.Add(self.reset_btn, 1, wx.ALL, 5)

        self.btn_sizer.AddStretchSpacer(2)

        # self.next_btn.Bind(wx.EVT_BUTTON, self.next)
        # self.btn_sizer.Add(self.next_btn, 1, wx.ALL, 5)

        self.address_panel = AddressPanel(self)

        self.btn_sizer_defaults = wx.BoxSizer(wx.HORIZONTAL)

        self.cancel_btn = wx.Button(self, label='Finish')
        self.btn_sizer_defaults.Add(self.cancel_btn, 1, wx.LEFT, 5)

        self.cancel_btn = wx.Button(self, label='Cancel')
        self.btn_sizer_defaults.Add(self.cancel_btn, 1, wx.LEFT, 5)

        self.choices_sizer.Add(pick_panel, 0, wx.ALIGN_LEFT, 5)
        self.choices_sizer.Add(self.coffees_outer_panel, 0, wx.EXPAND | wx.ALL, 5)
        self.choices_sizer.Add(self.btn_sizer, 1, wx.ALIGN_LEFT, 5)
        self.choices_sizer.Add(self.address_panel, 0, wx.ALL | wx.EXPAND, 5)
        self.choices_sizer.Add(self.btn_sizer_defaults, 0, wx.ALL | wx.ALIGN_RIGHT, 5)

        self.SetSizer(self.choices_sizer)
        # self.coffees_outer_panel.SetSize((1, 1))

        # self.coffees_outer_panel.Disable()
        self.btn.Disable()
        self.address_panel.Disable()

        # self.add(0)

    def fit(self):
        self.SetSize((1,1))
        self.Fit()
        self.parent.Fit()
        # self.parent.summary_panel.Fit()
        self.parent.parent.Fit()
        print(self.parent.parent.GetSize())
        # print(self.parent.parent.GetSize())
        # print(self.parent.summary_panel.GetSize())

    def add(self, event):
        if self.no_coffees < 5:
            self.no_coffees = self.no_coffees + 1
            coffees_panel = Coffees(self, self.no_coffees)
            self.choices_sizer.Add(coffees_panel, 0, wx.ALIGN_CENTRE, 10)
            print(self.no_coffees)
        else:
            pass

    def next(self, event):
        # address_frame = AddressFrame(self)
        # address_frame.Show()
        address_panel = AddressPanel(self)
        self.choices_sizer.Add(address_panel, 0, wx.ALL | wx.EXPAND, 5)
        self.fit()

    def enable(self, serve):
        self.coffees_outer_panel.Enable()
        self.btn.Enable()
        self.address_panel.enable(serve)


class Summary(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        s_box = wx.StaticBox(self, 0, 'Summary')
        s_box_sizer = wx.StaticBoxSizer(s_box, wx.VERTICAL)
        self.summary_sizer = wx.BoxSizer(wx.VERTICAL)

        intro_txt = wx.StaticText(self, label="As coffees are selected their overview would be found here",
                                  style=wx.ALIGN_CENTRE)
        # print(self.GetSize())
        intro_txt.Wrap(170)
        self.summary_sizer.Add(intro_txt, 0, wx.ALIGN_CENTRE, 5)

        s_box_sizer.Add(self.summary_sizer, 0, wx.EXPAND, 5)
        self.SetSizer(s_box_sizer)

        self.serving = int(0)
        self.order_name = 'Order'

    def remove(self):
        for n in self.summary_sizer.GetChildren():
            n.GetWindow().Destroy()

    def add(self, drink_dict=None):
        if len(drink_dict) != 0:
            self.remove()
            serving_type = ""
            delivery_cost = 0
            if self.serving == 1:
                serving_type = "Delivery"
                delivery_cost = 3
            elif self.serving == 0:
                serving_type = "Pick Up"
            print('o_n', self.order_name)
            serving_text = wx.StaticText(self, label=self.order_name)
            serving_text.SetFont(wx.Font(-1, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            self.summary_sizer.Add(serving_text, 0, wx.ALIGN_CENTRE, 5)

            # for checking duplicated: https://stackoverflow.com/a/20672375/14264797
            reverse_drink_dict = {}
            for key, value in drink_dict.items():
                reverse_drink_dict.setdefault(repr(value), set()).add(key)

            non_repeats_repr = [key for key, values in reverse_drink_dict.items() if len(values) == 1]
            repeat_dict = {key: len(values) for key, values in reverse_drink_dict.items() if len(values) > 1}
            print("repeat_dict", repeat_dict)
            # repeat_list = []
            # for r, n in repeat_dict.items():
            #     repeat_list.append(ast.literal_eval(r))
            #     repeat_list[len(repeat_list)-1].append(n)
            # # print(repeats)

            final_list = [ast.literal_eval(r) + [n] for r, n in repeat_dict.items()] + \
                         [ast.literal_eval(r) + [1] for r in non_repeats_repr]
            # non_repeat_list = [ast.literal_eval(r) + [1] for r in non_repeats_repr]
            # print(try_list)
            # print(repeat_list)
            #
            # non_repeats = []
            # for n in non_repeats_repr:
            #     non_repeats.append(ast.literal_eval(n))
            #     non_repeats[len(non_repeats) - 1].append(1)
            #
            # final_list = repeat_list + non_repeats
            print('final_list', final_list)

            total_coffee: int = 0
            total_price: int = 0

            for l in final_list:
                name = l[0]
                size = l[1]
                additives = l[2]
                times = l[3]
                price = PRICES['coffees'][name.lower()] * times

                if times > 1:
                    name_txt = wx.StaticText(self, label="{} {} x{} : ${}".format(size, name, times, price))
                else:
                    name_txt = wx.StaticText(self, label="{} {} : ${}".format(size, name, price))
                self.summary_sizer.Add(name_txt, 0, wx.ALIGN_RIGHT | wx.UP, 5)

                for ad, am in additives.items():
                    if am > 0:
                        additives_txt = wx.StaticText(self, label="{} x{}".format(ad, am))
                    else:
                        additives_txt = wx.StaticText(self, label="{}".format(ad))
                    self.summary_sizer.Add(additives_txt, 0, wx.ALIGN_RIGHT, 5)

                total_coffee += times
                total_price += price

            # no_select_coffee_dict = {}
            # for i in item:
            #     if i in no_select_coffee_dict:
            #         no_select_coffee_dict[i] = no_select_coffee_dict[i] + 1
            #     else:
            #         no_select_coffee_dict[i] = 1
            #
            # # print(no_select_coffee_dict)
            #
            #
            # for n in no_select_coffee_dict:
            #     if n != '' and n != 'Choose a coffee...':  # todo make the program, independent
            #         no = no_select_coffee_dict[n]
            #         total_coffee += no
            #         price = PRICES['coffees'][n.lower()] * no
            #         total_price = total_price + price
            #         txt = wx.StaticText(self, label="{} x{} : ${}".format(n, no, price))
            #         self.summary_sizer.Add(txt, 0, wx.ALIGN_RIGHT, 5)

            horz_line = wx.StaticLine(self, style=wx.LI_HORIZONTAL)
            self.summary_sizer.Add(horz_line, 0, wx.EXPAND, 5)

            total_txt = wx.StaticText(self, label="Drinks ({}) : ${}".format(total_coffee, total_price))
            self.summary_sizer.Add(total_txt, 0, wx.ALIGN_LEFT | wx.UP, 10)

            gst_price = round(total_price * 1.15, 3)
            gst_txt = wx.StaticText(self, label="With GST (15%) : ${}".format(gst_price))
            self.summary_sizer.Add(gst_txt, 0, wx.ALIGN_LEFT, 15)

            delivery_txt = wx.StaticText(self, label="Delivery Charge : ${}".format(delivery_cost))
            self.summary_sizer.Add(delivery_txt, 0, wx.ALIGN_LEFT, 15)

            horz_line = wx.StaticLine(self, style=wx.LI_HORIZONTAL)
            self.summary_sizer.Add(horz_line, 0, wx.EXPAND, 5)

            grand_total_txt = wx.StaticText(self, label="Grand Total : ${}".format(delivery_cost+gst_price))
            grand_total_txt.SetFont(wx.Font(-1, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            self.summary_sizer.Add(grand_total_txt, 0, wx.ALIGN_RIGHT | wx.UP, 10)

            self.SetSize(0,0)
            self.Fit()
            self.parent.SetSize(0,0)
            self.parent.Fit()


class MainPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        # outer_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.summary_panel = Summary(self)
        self.choices_panel = Choices(self)

        main_sizer.Add(self.choices_panel, 5, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(self.summary_panel, 2, wx.EXPAND | wx.ALL, 5)

        # outer_sizer.Add(main_sizer, 1, wx.EXPAND, 5)
        # btn = wx.Button(self, label='try')
        # outer_sizer.Add(btn, 1, wx.EXPAND, 5)
        # btn.Bind(wx.EVT_BUTTON, self.summary_refresh)
        self.SetSizer(main_sizer)

        self.Fit()

    def summary_refresh(self, event):
        summary_coffees = {}
        selected_drinks = {}
        i = 1
        for n in self.choices_panel.coffees_outer_panel.outer_sizer.GetChildren():
            print(type(n.GetWindow()), wx.StaticText)
            if type(n.GetWindow()) != wx.StaticText:
                drink = n.GetWindow().coffee_combo.GetValue()
                size = n.GetWindow().size_combo.GetValue()
                if drink.lower() in PRICES['coffees'] and size in SIZE:
                    summary_coffees[drink] = size

                    prop_list = []
                    selected_drinks[i] = []
                    prop_list.append(drink)
                    prop_list.append(size)

                    selected_additives = {}

                    # print(n.GetWindow().additives_container.GetChildren())
                    for p in n.GetWindow().additives_container.GetChildren():
                        # print(p.GetWindow().combo_bx.GetValue())
                        selected_additives[p.GetWindow().combo_bx.GetValue()] = p.GetWindow().num_ctrl.GetValue()

                    prop_list.append(selected_additives)
                    selected_drinks[i] = prop_list
                    i += 1

                # self.summary_panel.add(item=n.GetWindow().coffee_combo.GetValue())

        print(selected_drinks)
        print(summary_coffees)
        self.summary_panel.add(drink_dict=selected_drinks)
        # print(self.parent.GetSize())


class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="Coffee Order", size=(655,462))
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

