import wx
import os
import csv
import backend.mariadb_connector
import backend.app_constants as app_global_vars
import frontend.views.institutions
import frontend.presenters.institutions_presenter


WEEK_DAYS = {
	0: "Poniedziałek",
	1: "Wtorek",
	2: "Środa",
	3: "Czwartek",
	4: "Piątek",
	5: "Sobota",
	6: "Niedziela"
}


def generate_lessons_with_breaks(beginning, finish, lesson_length, break_length, extra_breaks):
	"""Generates list of lessons for a given institution
	taking into account irregular breaks."""
	lessons = []
	start = beginning
	end = ''
	splitted_start = start.split(':')
	start_in_minutes = int(splitted_start[0]) * 60 + int(splitted_start[1])
	splitted_finish = finish.split(':')
	finish_in_minutes = int(splitted_finish[0]) * 60 + int(splitted_finish[1])
	while start_in_minutes <= (finish_in_minutes - lesson_length):
		end_in_minutes = start_in_minutes + lesson_length
		splitted_end = [str(end_in_minutes // 60).zfill(2), str(end_in_minutes % 60).zfill(2)]
		end = ':'.join(splitted_end)
		lessons.append((start, end))
		for extra_break in extra_breaks:
			if end == extra_break["BreakStartingHour"]:
				start = extra_break["BreakEndingHour"]
				splitted_start = start.split(':')
				start_in_minutes = int(splitted_start[0]) * 60 + int(splitted_start[1])
				break
		else:
			start_in_minutes = end_in_minutes + break_length
			splitted_start = [str(start_in_minutes // 60).zfill(2), str(start_in_minutes % 60).zfill(2)]
			start = ':'.join(splitted_start)
	return lessons


def generate_lessons_without_breaks(beginning, finish):
	"""Generates list of potential lessons for an institution without regular breaks i.e. lesson can start every quarter."""
	times = [beginning, ]
	time = beginning
	splitted_time = time.split(':')
	time_in_minutes = int(splitted_time[0]) * 60 + int(splitted_time[1])
	splitted_finish = finish.split(':')
	finish_in_minutes = int(splitted_finish[0]) * 60 + int(splitted_finish[1])
	while time_in_minutes < finish_in_minutes:
		time_in_minutes += 15
		splitted_time = [str(time_in_minutes // 60).zfill(2), str(time_in_minutes % 60).zfill(2)]
		time = ':'.join(splitted_time)
		times.append(time)
		splitted_time = time.split(':')
		time_in_minutes = int(splitted_time[0]) * 60 + int(splitted_time[1])
	return times


class LessonToScheduleDLG(wx.Dialog):

	"""Dialog for adding new lesson to the schedule."""

	controls = dict()

	def __init__(self, parent, index, refreshView):
		super().__init__(parent=parent, title="Dodaj zajęcia do grafiku")
		self.index = index
		self.refreshView = refreshView
		self.main_sizer = wx.BoxSizer(wx.VERTICAL)
		self.helper_sizer = wx.BoxSizer(wx.VERTICAL)
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		label = wx.StaticText(self, label="Dzień tygodnia:", size=(150, -1))
		sizer.Add(label, flag=wx.ALIGN_CENTER_VERTICAL)
		sizer.AddSpacer(10)
		self.controls["weekDay"] = wx.Choice(self, choices=list(WEEK_DAYS.values()))
		self.controls["weekDay"].SetSelection(0)
		sizer.Add(self.controls["weekDay"])
		self.helper_sizer.Add(sizer)

		res = app_global_vars.active_db_con.fetch_one(
			table_name="Institutions",
			col_names=(
				"StartingHour",
				"EndingHour",
				"HasBreaks",
				"NormalBreakLength",
				"NormalLessonLength"
			),
			condition_string="InstitutionId = ?",
			seq=(self.index,)
		)
		if res["HasBreaks"] == 1:
			extraBreaks = app_global_vars.active_db_con.fetch_all_matching(
				table_name="Breaks",
				col_names=("BreakStartingHour", "BreakEndingHour"),
				condition_str="InstitutionId = ?",
				seq=(self.index,)
			)
			self.lessons_with_breaks = generate_lessons_with_breaks(
				res["StartingHour"],
				res["EndingHour"],
				res["NormalLessonLength"],
				res["NormalBreakLength"],
				list(extraBreaks)
			)
			sizer = wx.BoxSizer(wx.HORIZONTAL)
			label = wx.StaticText(self, label="Lekcje:", size=(150, -1))
			sizer.Add(label, flag=wx.ALIGN_CENTER_VERTICAL)
			sizer.AddSpacer(10)
			self.controls["lessons"] = wx.Choice(
				self, choices=[' - '.join(lesson) for lesson in self.lessons_with_breaks]
			)
			sizer.Add(self.controls["lessons"])
			self.helper_sizer.Add(sizer)
		else:
			self.lessons_without_breaks = generate_lessons_without_breaks(
				res["StartingHour"], res["EndingHour"]
			)
			sizer = wx.BoxSizer(wx.HORIZONTAL)
			label = wx.StaticText(self, label="Godzina rozpoczęcia:", size=(150, -1))
			sizer.Add(label, flag=wx.ALIGN_CENTER_VERTICAL)
			sizer.AddSpacer(10)
			self.controls["start_time"] = wx.Choice(
				self, choices=[lesson for lesson in self.lessons_without_breaks[:-3]]
			)
			sizer.Add(self.controls["start_time"])
			self.helper_sizer.Add(sizer)
			self.controls["start_time"].Bind(wx.EVT_CHOICE, self.on_choice)
			sizer = wx.BoxSizer(wx.HORIZONTAL)
			label = wx.StaticText(self, label="Godzina zakończenia:", size=(150, -1))
			sizer.Add(label, flag=wx.ALIGN_CENTER_VERTICAL)
			sizer.AddSpacer(10)
			self.controls["end_time"] = wx.Choice(self, choices=[lesson for lesson in self.lessons_without_breaks[1:]])
			sizer.Add(self.controls["end_time"])
			self.helper_sizer.Add(sizer)

		self.teachersInInst = dict()
		res = app_global_vars.active_db_con.fetch_all_matching(
			table_name="Teachers",
			col_names=("TeacherId", "FirstName", "LastName"),
			condition_str="EmployedIn= ? and IsAvailable = 1",
			seq=(self.index,)
		)
		for indexInCB, record in enumerate(res):
			self.teachersInInst[indexInCB] = (record["TeacherId"], " ".join((record["FirstName"], record["LastName"])))
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		label = wx.StaticText(self, label="Prowadzący:", size=(150, -1))
		sizer.Add(label, flag=wx.ALIGN_CENTER_VERTICAL)
		sizer.AddSpacer(10)
		self.controls["teacher"] = wx.Choice(self, choices=[v[1] for v in self.teachersInInst.values()])
		sizer.Add(self.controls["teacher"])
		self.helper_sizer.Add(sizer)
		self.subjectsInInst = dict()
		res = app_global_vars.active_db_con.fetch_all_matching(
			table_name="Subjects",
			col_names=("SubjectId", "SubjectName"),
			condition_str="TaughtIn = ?",
			seq=(self.index,)
		)
		for indexInCB, record in enumerate(res):
			self.subjectsInInst[indexInCB] = (record["SubjectId"], record["SubjectName"])
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		label = wx.StaticText(self, label="Przedmiot:", size=(150, -1))
		sizer.Add(label, flag=wx.ALIGN_CENTER_VERTICAL)
		sizer.AddSpacer(10)
		self.controls["subject"] = wx.Choice(self, choices=[v[1] for v in self.subjectsInInst.values()])
		sizer.Add(self.controls["subject"])
		self.helper_sizer.Add(sizer)

		self.classesInInst = dict()
		res = app_global_vars.active_db_con.fetch_all_matching(
			table_name="Classes",
			col_names=("ClassId", "ClassIdentifier"),
			condition_str="ClassInInstitution = ?",
			seq=(self.index,)
		)
		for indexInCB, record in enumerate(res):
			self.classesInInst[indexInCB] = (record["ClassId"], record["ClassIdentifier"])
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		label = wx.StaticText(self, label="Grupa:", size=(150, -1))
		sizer.Add(label, flag=wx.ALIGN_CENTER_VERTICAL)
		sizer.AddSpacer(10)
		self.controls["class"] = wx.Choice(self, choices=[v[1] for v in self.classesInInst.values()])
		sizer.Add(self.controls["class"])
		self.helper_sizer.Add(sizer)

		self.classRoomsInInst = dict()
		res = app_global_vars.active_db_con.fetch_all_matching(
			table_name="ClassRooms",
			col_names=("ClassRoomId", "ClassRoomIdentifier"),
			condition_str="IsIn = ?",
			seq=(self.index,)
		)
		for indexInCB, record in enumerate(res):
			self.classRoomsInInst[indexInCB] = (record["ClassRoomId"], record["ClassRoomIdentifier"])
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		label = wx.StaticText(self, label="Sala:", size=(150, -1))
		sizer.Add(label, flag=wx.ALIGN_CENTER_VERTICAL)
		sizer.AddSpacer(10)
		self.controls["classRoom"] = wx.Choice(self, choices=[v[1] for v in self.classRoomsInInst.values()])
		sizer.Add(self.controls["classRoom"])
		self.helper_sizer.Add(sizer)

		self.main_sizer.Add(self.helper_sizer, border=20, flag=wx.LEFT | wx.RIGHT | wx.TOP)
		btn_sizer = wx.BoxSizer()
		save_btn = wx.Button(self, label='Dodaj')
		save_btn.Bind(wx.EVT_BUTTON, self.on_save)
		btn_sizer.Add(save_btn, 0, wx.ALL, 5)
		btn_sizer.Add(wx.Button(self, id=wx.ID_CANCEL), 0, wx.ALL, 5)
		self.main_sizer.Add(btn_sizer, 0, wx.CENTER)
		self.main_sizer.Fit(self)
		self.SetSizer(self.main_sizer)

	def on_choice(self, evt):
		"""Hides  lessons which makes no sense in the currennt context when user changes starting hour."""
		self.offset = self.controls["start_time"].GetSelection() + 3
		self.controls["end_time"].Set([lesson for lesson in self.lessons_without_breaks[self.offset:]])

	def on_save(self, evt):
		if hasattr(self, 'lessons_with_breaks'):
			start_hour = self.lessons_with_breaks[self.controls["lessons"].GetSelection()][0]
			end_hour = self.lessons_with_breaks[self.controls["lessons"].GetSelection()][1]
		elif hasattr(self, 'lessons_without_breaks'):
			start_hour = self.lessons_without_breaks[self.controls["start_time"].GetSelection()]
			end_hour = self.lessons_without_breaks[self.controls["end_time"].GetSelection() + self.offset]

		# Collision detection
		results = app_global_vars.active_db_con.fetch_all_matching(
			table_name="Schedule",
			col_names=("TeacherId", "ClassId", "ClassRoomId"),
			condition_str=(
				"InstitutionId = ? and WeekDay = ? "
				"and (? between LessonStartingHour and LessonEndingHour or ? between LessonEndingHour and LessonEndingHour)"
			),
			seq=(self.index, self.controls["weekDay"].GetSelection(), start_hour, end_hour)
		)
		message = []
		for row in results:
			if row["TeacherId"] == self.teachersInInst[self.controls["teacher"].GetSelection()][0]:
				t = self.controls["teacher"].GetString(self.controls["teacher"].GetSelection())
				message.append(f"Nauczyciel {t} prowadzi w tym czasie zajęcia.")
			if row["ClassId"] == self.classesInInst[self.controls["class"].GetSelection()][0]:
				g = self.controls["class"].GetString(self.controls["class"].GetSelection())
				message.append(f"Grupa {g} ma w tym czasie zajęcia.")
			if row["ClassRoomId"] == self.classRoomsInInst[self.controls["classRoom"].GetSelection()][0]:
				c = self.controls["classRoom"].GetString(self.controls["classRoom"].GetSelection())
				message.append(f"Sala {c} jest w tym czasie  zajęta.")
		if message:
			dialog = wx.MessageDialog(None, os.linesep.join(message), "Konflikt zajęć", wx.OK | wx.ICON_ERROR)
			dialog.ShowModal()
			return
		else:
			v = [
				self.index,
				self.controls["weekDay"].GetSelection(),
				start_hour, end_hour,
				self.teachersInInst[self.controls["teacher"].GetSelection()][0],
				self.subjectsInInst[self.controls["subject"].GetSelection()][0],
				self.classesInInst[self.controls["class"].GetSelection()][0],
				self.classRoomsInInst[self.controls["classRoom"].GetSelection()][0]
			]
			app_global_vars.active_db_con.insert(
				table_name="Schedule",
				col_names=(
					"InstitutionId",
					"WeekDay",
					"LessonStartingHour",
					"LessonEndingHour",
					"TeacherId",
					"SubjectId",
					"ClassId",
					"ClassRoomId"
				),
				col_values=v
			)
			if self.refreshView:
				self.Parent.list_ctrl.ClearAll()
				self.Parent.populateListView()
			self.Close()

	def add_widgets(self, label_text, ctrl_key):
		"""Adds a `wx.TextCtrl` with a given label to the dialog.
		the newly added control can be accessed using `ctrl_key` as the index to self.controls."""
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		label = wx.StaticText(self, label=label_text, size=(150, -1))
		sizer.Add(label, flag=wx.ALIGN_CENTER_VERTICAL)
		sizer.AddSpacer(10)
		self.controls[ctrl_key] = wx.TextCtrl(self)
		sizer.Add(self.controls[ctrl_key])
		self.helper_sizer.Add(sizer)


class EditScheduleDLG(wx.Dialog):
	pass


class EditBreakDLG(wx.Dialog):

	controls = dict()

	def __init__(self, parent, index, data):
		super().__init__(parent=parent, title="Edytuj długą przerwę")
		self.index = index
		self.data = data
		self.main_sizer = wx.BoxSizer(wx.VERTICAL)
		self.helper_sizer = wx.BoxSizer(wx.VERTICAL)
		self.add_widgets('Początek przerwy:', "breakStartingHour", 0)
		self.add_widgets('Koniec przerwy:', "breakEndingHour", 1)
		self.main_sizer.Add(self.helper_sizer, border=20, flag=wx.LEFT | wx.RIGHT | wx.TOP)
		btn_sizer = wx.BoxSizer()
		save_btn = wx.Button(self, label='Zapisz zmiany')
		save_btn.Bind(wx.EVT_BUTTON, self.on_save)
		btn_sizer.Add(save_btn, 0, wx.ALL, 5)
		btn_sizer.Add(wx.Button(self, id=wx.ID_CANCEL), 0, wx.ALL, 5)
		self.main_sizer.Add(btn_sizer, 0, wx.CENTER)
		self.main_sizer.Fit(self)
		self.SetSizer(self.main_sizer)

	def on_save(self, evt):
		v = [
			self.controls["breakStartingHour"].GetValue(),
			self.controls["breakEndingHour"].GetValue(),
		]
		app_global_vars.active_db_con.update_record(
			table_name="Breaks",
			col_names=("BreakStartingHour", "BreakEndingHour"),
			col_values=v,
			condition_str="BreakId = ?",
			condition_values=(self.index,)
		)
		self.Parent.list_ctrl.ClearAll()
		self.Parent.populateListView()
		self.Close()

	def add_widgets(self, label_text, ctrl_key, valIndex):
		"""Adds a `wx.TextCtrl` with a given label and content of self.data[valIndex] to the dialog.
		the newly added control can be accessed using `ctrl_key` as the index to self.controls.
		"""
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		label = wx.StaticText(self, label=label_text, size=(150, -1))
		sizer.Add(label, flag=wx.ALIGN_CENTER_VERTICAL)
		sizer.AddSpacer(10)
		self.controls[ctrl_key] = wx.TextCtrl(self, value=self.data[valIndex])
		sizer.Add(self.controls[ctrl_key])
		self.helper_sizer.Add(sizer)


class BreaksContextMenu(wx.Menu):

	def __init__(self, parent):
		super().__init__()
		self.parent = parent
		delBreak = wx.MenuItem(self, id=wx.ID_DELETE, text='Usuń')
		editBreak = wx.MenuItem(self, id=wx.ID_EDIT, text='Edytuj')
		self.Append(editBreak)
		self.Append(delBreak)
		self.Bind(wx.EVT_MENU, self.parent.on_edit, editBreak)
		self.Bind(wx.EVT_MENU, self.parent.on_remove, delBreak)


class BreaksPanel(wx.Panel):

	def __init__(self, parent, chosenInst):
		super().__init__(parent)
		self.inst = chosenInst
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		self.list_ctrl = wx.ListCtrl(
			self,
			size=(-1, 200),
			style=wx.LC_REPORT | wx.BORDER_SUNKEN
		)
		self.list_ctrl.Bind(wx.EVT_CONTEXT_MENU, self.onContext)
		self.list_ctrl.Bind(wx.EVT_KEY_UP, self.onKey)
		self.populateListView()
		main_sizer.Add(self.list_ctrl, 0, wx.ALL | wx.EXPAND, 5)
		new_breakBTN = wx.Button(self, label='Dodaj długą przerwę')
		new_breakBTN.Bind(wx.EVT_BUTTON, self.on_NewBreak)
		main_sizer.Add(new_breakBTN, 0, wx.ALL | wx.CENTER, 5)
		self.SetSizer(main_sizer)

	def onContext(self, event):
		self.PopupMenu(BreaksContextMenu(self), event.GetPosition())

	def onKey(self, event):
		"""Handles switching between panels when user presses ESC."""
		if event.KeyCode == wx.WXK_ESCAPE:
			frame.switchPanels()

	def populateListView(self):
		"""Sets up the list view columns and fills the list with the data from the database"""
		self.list_ctrl.InsertColumn(0, 'Początek przerwy', width=400)
		self.list_ctrl.InsertColumn(1, 'Koniec przerwy', width=400)
		for index, row in enumerate(
			app_global_vars.active_db_con.fetch_all_matching(
				table_name="Breaks",
				col_names=("BreakId", "BreakStartingHour", "BreakEndingHour"),
				condition_str="InstitutionId = ?",
				seq=(self.inst,)
			)
		):
			self.list_ctrl.InsertItem(index, row["BreakStartingHour"])
			self.list_ctrl.SetItem(index, 1, row["BreakEndingHour"])
			item = self.list_ctrl.GetItem(index)
			item.SetData(row["BreakId"])
			self.list_ctrl.SetItem(item)

	def on_remove(self, event):
		item = self.list_ctrl.GetItem(self.list_ctrl.GetFocusedItem())
		app_global_vars.active_db_con.delete_record(
			table_name="Breaks",
			condition_string="BreakId = ? ",
			seq=[item.GetData()]
		)
		self.list_ctrl.DeleteItem(self.list_ctrl.GetFocusedItem())

	def on_NewBreak(self, event):
		dlg = AddBreakDLG(self, self.inst, True)
		dlg.ShowModal()
		dlg.Destroy()

	def on_edit(self, event):
		index = self.list_ctrl.GetFocusedItem()
		dbIndex = self.list_ctrl.GetItemData(index)
		cols = []
		for colNumber in range(0, self.list_ctrl.GetColumnCount()):
			cols.append(self.list_ctrl.GetItemText(index, colNumber))
		dlg = EditBreakDLG(self, dbIndex, cols)
		dlg.ShowModal()
		dlg.Destroy()


class AddClassRoomDLG(wx.Dialog):

	controls = dict()

	def __init__(self, parent, index, refreshView):
		super().__init__(parent=parent, title="Dodaj salę")
		self.index = index
		self.refreshView = refreshView
		self.main_sizer = wx.BoxSizer(wx.VERTICAL)
		self.helper_sizer = wx.BoxSizer(wx.VERTICAL)
		self.add_widgets('Numer:', "name")
		self.coursesInInst = dict()
		self.coursesInInst[0] = (-1, "brak")
		res = app_global_vars.active_db_con.fetch_all_matching(
			table_name="Subjects",
			col_names=("SubjectId", "SubjectName"),
			condition_str="TaughtIn = ?",
			seq=(self.index,)
		)
		for indexInCB, record in enumerate(res, 1):
			self.coursesInInst[indexInCB] = (record["SubjectId"], record["SubjectName"])
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		label = wx.StaticText(self, label="Główny przedmiot:", size=(150, -1))
		sizer.Add(label, flag=wx.ALIGN_CENTER_VERTICAL)
		sizer.AddSpacer(10)
		self.controls["mainSubject"] = wx.Choice(self, choices=[v[1] for v in self.coursesInInst.values()])
		self.controls["mainSubject"].SetSelection(0)
		sizer.Add(self.controls["mainSubject"])
		self.helper_sizer.Add(sizer)
		self.main_sizer.Add(self.helper_sizer, border=20, flag=wx.LEFT | wx.RIGHT | wx.TOP)
		btn_sizer = wx.BoxSizer()
		save_btn = wx.Button(self, label='Dodaj')
		save_btn.Bind(wx.EVT_BUTTON, self.on_save)
		btn_sizer.Add(save_btn, 0, wx.ALL, 5)
		btn_sizer.Add(wx.Button(self, id=wx.ID_CANCEL), 0, wx.ALL, 5)
		self.main_sizer.Add(btn_sizer, 0, wx.CENTER)
		self.main_sizer.Fit(self)
		self.SetSizer(self.main_sizer)

	def on_save(self, evt):
		v = [
			self.controls["name"].GetValue(),
			self.index,
			self.coursesInInst[self.controls["mainSubject"].GetSelection()][0],
		]
		app_global_vars.active_db_con.insert(
			table_name="ClassRooms",
			col_names=("ClassRoomIdentifier", "IsIn", "PrimaryCourse"),
			col_values=v
		)
		if self.refreshView:
			self.Parent.list_ctrl.ClearAll()
			self.Parent.populateListView()
		self.Close()

	def add_widgets(self, label_text, ctrl_key):
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		label = wx.StaticText(self, label=label_text, size=(150, -1))
		sizer.Add(label, flag=wx.ALIGN_CENTER_VERTICAL)
		sizer.AddSpacer(10)
		self.controls[ctrl_key] = wx.TextCtrl(self)
		sizer.Add(self.controls[ctrl_key])
		self.helper_sizer.Add(sizer)


class ClassRoomsContextMenu(wx.Menu):

	def __init__(self, parent):
		super().__init__()
		self.parent = parent
		delClassRoom = wx.MenuItem(self, id=wx.ID_DELETE, text='Usuń')
		editClasRoom = wx.MenuItem(self, id=wx.ID_EDIT, text='Edytuj')
		showSchedule = wx.MenuItem(self, id=wx.ID_ANY, text='Wyświetl grafik')
		self.Append(editClasRoom)
		self.Append(delClassRoom)
		self.Append(showSchedule)
		self.Bind(wx.EVT_MENU, self.parent.on_edit, editClasRoom)
		self.Bind(wx.EVT_MENU, self.parent.on_remove, delClassRoom)
		self.Bind(wx.EVT_MENU, self.ShowSchedule, showSchedule)

	def ShowSchedule(self, event):
		index = self.parent.list_ctrl.GetFocusedItem()
		dbIndex = self.parent.list_ctrl.GetItemData(index)
		p = SchedulesPanel(self.parent.Parent, "cr.ClassRoomId", dbIndex)
		frame.showPanel(p)


class ClassRoomsPanel(wx.Panel):

	def __init__(self, parent, chosenInst):
		super().__init__(parent)
		self.inst = chosenInst
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		self.list_ctrl = wx.ListCtrl(
			self,
			size=(-1, 200),
			style=wx.LC_REPORT | wx.BORDER_SUNKEN
		)
		self.list_ctrl.Bind(wx.EVT_CONTEXT_MENU, self.onContext)
		self.list_ctrl.Bind(wx.EVT_KEY_UP, self.onKey)
		self.populateListView()
		main_sizer.Add(self.list_ctrl, 0, wx.ALL | wx.EXPAND, 5)
		new_classRoomBTN = wx.Button(self, label='Dodaj salę')
		new_classRoomBTN.Bind(wx.EVT_BUTTON, self.on_NewClassRoom)
		main_sizer.Add(new_classRoomBTN, 0, wx.ALL | wx.CENTER, 5)
		self.SetSizer(main_sizer)

	def onContext(self, event):
		self.PopupMenu(ClassRoomsContextMenu(self), event.GetPosition())

	def onKey(self, event):
		if event.KeyCode == wx.WXK_ESCAPE:
			frame.switchPanels()

	def populateListView(self):
		self.list_ctrl.InsertColumn(0, 'Numer', width=400)
		self.list_ctrl.InsertColumn(1, 'Główny kurs', width=400)
		for index, row in enumerate(
			app_global_vars.active_db_con.fetch_all_matching(
				table_name="ClassRooms CL LEFT OUTER JOIN Subjects su ON CL.PrimaryCourse = su.SubjectId",
				col_names=("ClassRoomId", "ClassRoomIdentifier", "SubjectName"),
				condition_str="IsIn = ?",
				seq=(self.inst,)
			)
		):
			self.list_ctrl.InsertItem(index, row["ClassRoomIdentifier"])
			if row["SubjectName"] is not None:
				self.list_ctrl.SetItem(index, 1, row["SubjectName"])
			else:
				self.list_ctrl.SetItem(index, 1, "brak")
			item = self.list_ctrl.GetItem(index)
			item.SetData(row["ClassRoomId"])
			self.list_ctrl.SetItem(item)

	def on_remove(self, event):
		item = self.list_ctrl.GetItem(self.list_ctrl.GetFocusedItem())
		app_global_vars.active_db_con.delete_record(
			table_name="ClassRooms",
			condition_string="ClassRoomId = ? ",
			seq=[item.GetData()]
		)
		self.list_ctrl.DeleteItem(self.list_ctrl.GetFocusedItem())

	def on_NewClassRoom(self, event):
		dlg = AddClassRoomDLG(self, self.inst, True)
		dlg.ShowModal()
		dlg.Destroy()

	def on_edit(self, event):
		index = self.list_ctrl.GetFocusedItem()
		dbIndex = self.list_ctrl.GetItemData(index)
		cols = []
		for colNumber in range(0, self.list_ctrl.GetColumnCount()):
			cols.append(self.list_ctrl.GetItemText(index, colNumber))
		dlg = EditTeacherDLG(self, dbIndex, cols)
		dlg.ShowModal()
		dlg.Destroy()


class EditTeacherDLG(wx.Dialog):

	controls = dict()

	def __init__(self, parent, index, data):
		super().__init__(parent=parent, title="Edytuj nauczyciela")
		self.index = index
		self.data = data
		self.main_sizer = wx.BoxSizer(wx.VERTICAL)
		self.helper_sizer = wx.BoxSizer(wx.VERTICAL)
		self.add_widgets('Imię:', "name", 0)
		self.add_widgets('Nazwisko:', "surName", 1)
		self.controls["Availability"] = wx.CheckBox(self, label="Dostępny")
		self.controls["Availability"].SetValue(self.data[2])
		self.helper_sizer.Add(self.controls["Availability"])
		self.main_sizer.Add(self.helper_sizer, border=20, flag=wx.LEFT | wx.RIGHT | wx.TOP)
		btn_sizer = wx.BoxSizer()
		save_btn = wx.Button(self, label='Zapisz zmiany')
		save_btn.Bind(wx.EVT_BUTTON, self.on_save)
		btn_sizer.Add(save_btn, 0, wx.ALL, 5)
		btn_sizer.Add(wx.Button(self, id=wx.ID_CANCEL), 0, wx.ALL, 5)
		self.main_sizer.Add(btn_sizer, 0, wx.CENTER)
		self.main_sizer.Fit(self)
		self.SetSizer(self.main_sizer)

	def on_save(self, evt):
		v = [
			self.controls["name"].GetValue(),
			self.controls["surName"].GetValue(),
			int(self.controls["Availability"].Value),
		]
		app_global_vars.active_db_con.update_record(
			table_name="Teachers",
			col_names=("FirstName", "LastName", "IsAvailable"),
			col_values=v,
			condition_str="TeacherId = ?",
			condition_values=(self.index,)
		)
		self.Parent.list_ctrl.ClearAll()
		self.Parent.populateListView()
		self.Close()

	def add_widgets(self, label_text, ctrl_key, valIndex):
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		label = wx.StaticText(self, label=label_text, size=(150, -1))
		sizer.Add(label, flag=wx.ALIGN_CENTER_VERTICAL)
		sizer.AddSpacer(10)
		self.controls[ctrl_key] = wx.TextCtrl(self, value=self.data[valIndex])
		sizer.Add(self.controls[ctrl_key])

		self.helper_sizer.Add(sizer)


class TeachersContextMenu(wx.Menu):

	def __init__(self, parent):
		super().__init__()
		self.parent = parent
		delTeacher = wx.MenuItem(self, id=wx.ID_DELETE, text='Usuń')
		editTeacher = wx.MenuItem(self, id=wx.ID_EDIT, text='Edytuj')
		showSchedule = wx.MenuItem(self, id=wx.ID_ANY, text='Wyświetl grafik')
		self.Append(editTeacher)
		self.Append(delTeacher)
		self.Append(showSchedule)
		self.Bind(wx.EVT_MENU, self.parent.on_edit, editTeacher)
		self.Bind(wx.EVT_MENU, self.parent.on_remove, delTeacher)
		self.Bind(wx.EVT_MENU, self.ShowSchedule, showSchedule)

	def ShowSchedule(self, event):
		index = self.parent.list_ctrl.GetFocusedItem()
		dbIndex = self.parent.list_ctrl.GetItemData(index)
		p = SchedulesPanel(self.parent.Parent, "te.TeacherID", dbIndex)
		frame.showPanel(p)


class AddTeacherDLG(wx.Dialog):

	controls = dict()

	def __init__(self, parent, index, refreshView):
		super().__init__(parent=parent, title="Dodaj nauczyciela")
		self.index = index
		self.refreshView = refreshView
		self.main_sizer = wx.BoxSizer(wx.VERTICAL)
		self.helper_sizer = wx.BoxSizer(wx.VERTICAL)
		self.add_widgets('Imię:', "name")
		self.add_widgets('Nazwisko:', "surName")
		self.controls["Availability"] = wx.CheckBox(self, label="Dostępny")
		self.controls["Availability"].SetValue(True)
		self.helper_sizer.Add(self.controls["Availability"])
		self.main_sizer.Add(self.helper_sizer, border=20, flag=wx.LEFT | wx.RIGHT | wx.TOP)
		btn_sizer = wx.BoxSizer()
		save_btn = wx.Button(self, label='Dodaj')
		save_btn.Bind(wx.EVT_BUTTON, self.on_save)
		btn_sizer.Add(save_btn, 0, wx.ALL, 5)
		btn_sizer.Add(wx.Button(self, id=wx.ID_CANCEL), 0, wx.ALL, 5)
		self.main_sizer.Add(btn_sizer, 0, wx.CENTER)
		self.main_sizer.Fit(self)
		self.SetSizer(self.main_sizer)

	def on_save(self, evt):
		v = [
			self.controls["name"].GetValue(),
			self.controls["surName"].GetValue(),
			int(self.controls["Availability"].Value),
			self.index
		]
		app_global_vars.active_db_con.insert(
			table_name="Teachers",
			col_names=(
				"FirstName",
				"LastName",
				"IsAvailable",
				"EmployedIn"
			),
			col_values=v
		)
		if self.refreshView:
			self.Parent.list_ctrl.ClearAll()
			self.Parent.populateListView()
		self.Close()

	def add_widgets(self, label_text, ctrl_key):
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		label = wx.StaticText(self, label=label_text, size=(150, -1))
		sizer.Add(label, flag=wx.ALIGN_CENTER_VERTICAL)
		sizer.AddSpacer(10)
		self.controls[ctrl_key] = wx.TextCtrl(self)
		sizer.Add(self.controls[ctrl_key])
		self.helper_sizer.Add(sizer)


class TeachersPanel(wx.Panel):

	def __init__(self, parent, chosenInst):
		super().__init__(parent)
		self.inst = chosenInst
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		self.list_ctrl = wx.ListCtrl(
			self,
			size=(-1, 200),
			style=wx.LC_REPORT | wx.BORDER_SUNKEN
		)
		self.list_ctrl.Bind(wx.EVT_CONTEXT_MENU, self.onContext)
		self.list_ctrl.Bind(wx.EVT_KEY_UP, self.onKey)
		self.populateListView()
		main_sizer.Add(self.list_ctrl, 0, wx.ALL | wx.EXPAND, 5)
		new_teacherBTN = wx.Button(self, label='Dodaj nauczyciela')
		new_teacherBTN.Bind(wx.EVT_BUTTON, self.on_NewTeacher)
		main_sizer.Add(new_teacherBTN, 0, wx.ALL | wx.CENTER, 5)
		self.SetSizer(main_sizer)

	def onContext(self, event):
		self.PopupMenu(TeachersContextMenu(self), event.GetPosition())

	def onKey(self, event):
		if event.KeyCode == wx.WXK_ESCAPE:
			frame.switchPanels()

	def populateListView(self):
		self.list_ctrl.InsertColumn(0, 'Imię', width=400)
		self.list_ctrl.InsertColumn(1, 'Nazwisko', width=400)
		self.list_ctrl.InsertColumn(2, 'Status', width=100)
		for index, row in enumerate(
			app_global_vars.active_db_con.fetch_all_matching(
				table_name="Teachers",
				col_names=("TeacherId", "FirstName", "LastName", "IsAvailable"),
				condition_str="EmployedIn = ?",
				seq=(self.inst,)
			)
		):
			self.list_ctrl.InsertItem(index, row["FirstName"])
			self.list_ctrl.SetItem(index, 1, row["LastName"])
			self.list_ctrl.SetItem(
				index,
				2,
				"dostępny" if row["IsAvailable"] else "niedostępny"
			)
			item = self.list_ctrl.GetItem(index)
			item.SetData(row["TeacherId"])
			self.list_ctrl.SetItem(item)

	def on_remove(self, event):
		item = self.list_ctrl.GetItem(self.list_ctrl.GetFocusedItem())
		app_global_vars.active_db_con.delete_record(
			table_name="Teachers",
			condition_string="TeacherId = ? ",
			seq=[item.GetData()]
		)
		self.list_ctrl.DeleteItem(self.list_ctrl.GetFocusedItem())

	def on_NewTeacher(self, event):
		dlg = AddTeacherDLG(self, self.inst, True)
		dlg.ShowModal()
		dlg.Destroy()

	def on_edit(self, event):
		index = self.list_ctrl.GetFocusedItem()
		dbIndex = self.list_ctrl.GetItemData(index)
		cols = []
		for colNumber in range(0, self.list_ctrl.GetColumnCount() - 1):
			cols.append(self.list_ctrl.GetItemText(index, colNumber))
		cols.append(True if self.list_ctrl.GetItemText(index, self.list_ctrl.GetColumnCount()) == "dostępny" else False)
		dlg = EditTeacherDLG(self, dbIndex, cols)
		dlg.ShowModal()
		dlg.Destroy()


class EditSubjectDialog(wx.Dialog):

	controls = dict()

	def __init__(self, parent, index, data):
		super().__init__(parent=parent, title="Edytuj zajęcia")
		self.index = index
		self.data = data
		self.main_sizer = wx.BoxSizer(wx.VERTICAL)
		self.helper_sizer = wx.BoxSizer(wx.VERTICAL)
		self.add_widgets('Nazwa zajęć:', "name", 0)
		self.main_sizer.Add(self.helper_sizer, border=20, flag=wx.LEFT | wx.RIGHT | wx.TOP)
		btn_sizer = wx.BoxSizer()
		save_btn = wx.Button(self, label='Zapisz zmiany')
		save_btn.Bind(wx.EVT_BUTTON, self.on_save)
		btn_sizer.Add(save_btn, 0, wx.ALL, 5)
		btn_sizer.Add(wx.Button(self, id=wx.ID_CANCEL), 0, wx.ALL, 5)
		self.main_sizer.Add(btn_sizer, 0, wx.CENTER)
		self.main_sizer.Fit(self)
		self.SetSizer(self.main_sizer)

	def on_save(self, evt):
		v = [
			self.controls["name"].GetValue(),
		]
		app_global_vars.active_db_con.update_record(
			table_name="Subjects",
			col_names=("SubjectName",),
			col_values=v,
			condition_str="SubjectId = ?",
			condition_values=(self.index,)
		)
		self.Parent.list_ctrl.ClearAll()
		self.Parent.populateListView()
		self.Close()

	def add_widgets(self, label_text, ctrl_key, valIndex):
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		label = wx.StaticText(self, label=label_text, size=(150, -1))
		sizer.Add(label, flag=wx.ALIGN_CENTER_VERTICAL)
		sizer.AddSpacer(10)
		self.controls[ctrl_key] = wx.TextCtrl(self, value=self.data[valIndex])
		sizer.Add(self.controls[ctrl_key])
		self.helper_sizer.Add(sizer)


class SubjectsContextMenu(wx.Menu):

	def __init__(self, parent):
		super().__init__()
		self.parent = parent
		delSubject = wx.MenuItem(self, id=wx.ID_DELETE, text='Usuń')
		editSubject = wx.MenuItem(self, id=wx.ID_EDIT, text='Edytuj')
		self.Append(editSubject)
		self.Append(delSubject)
		self.Bind(wx.EVT_MENU, self.parent.on_edit, editSubject)
		self.Bind(wx.EVT_MENU, self.parent.on_remove, delSubject)


class SubjectsPanel(wx.Panel):

	def __init__(self, parent, chosenInst):
		"""Displays subjects in the institution with the given ID."""
		super().__init__(parent)
		self.inst = chosenInst
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		self.list_ctrl = wx.ListCtrl(
			self,
			size=(-1, 200),
			style=wx.LC_REPORT | wx.BORDER_SUNKEN
		)
		self.list_ctrl.Bind(wx.EVT_CONTEXT_MENU, self.onContext)
		self.list_ctrl.Bind(wx.EVT_KEY_UP, self.onKey)
		self.populateListView()
		main_sizer.Add(self.list_ctrl, 0, wx.ALL | wx.EXPAND, 5)
		new_subjectBTN = wx.Button(self, label='Dodaj nowy przedmiot')
		new_subjectBTN.Bind(wx.EVT_BUTTON, self.on_NewSubject)
		main_sizer.Add(new_subjectBTN, 0, wx.ALL | wx.CENTER, 5)
		self.SetSizer(main_sizer)

	def onContext(self, event):
		self.PopupMenu(SubjectsContextMenu(self), event.GetPosition())

	def onKey(self, event):
		if event.KeyCode == wx.WXK_ESCAPE:
			frame.switchPanels()

	def populateListView(self):
		self.list_ctrl.InsertColumn(0, 'Nazwa', width=400)
		for index, row in enumerate(
			app_global_vars.active_db_con.fetch_all_matching(
				table_name="Subjects",
				col_names=("SubjectId", "SubjectName"),
				condition_str="TaughtIn = ?",
				seq=(self.inst,)
			)
		):
			self.list_ctrl.InsertItem(index, row["SubjectName"])
			item = self.list_ctrl.GetItem(index)
			item.SetData(row["SubjectId"])
			self.list_ctrl.SetItem(item)

	def on_remove(self, event):
		item = self.list_ctrl.GetItem(self.list_ctrl.GetFocusedItem())
		app_global_vars.active_db_con.delete_record(
			table_name="Subjects",
			condition_string="SubjectId= ? ",
			seq=[item.GetData()]
		)
		self.list_ctrl.DeleteItem(self.list_ctrl.GetFocusedItem())

	def on_NewSubject(self, event):
		dlg = AddSubjectDLG(self, self.inst, True)
		dlg.ShowModal()
		dlg.Destroy()

	def on_edit(self, event):
		index = self.list_ctrl.GetFocusedItem()
		dbIndex = self.list_ctrl.GetItemData(index)
		cols = []
		for colNumber in range(0, self.list_ctrl.GetColumnCount()):
			cols.append(self.list_ctrl.GetItemText(index, colNumber))
		dlg = EditSubjectDialog(self, dbIndex, cols)
		dlg.ShowModal()
		dlg.Destroy()


class EditClassDialog(wx.Dialog):

	controls = dict()

	def __init__(self, parent, index, data):
		super().__init__(parent=parent, title="Edytuj klasę")
		self.index = index
		self.data = data
		self.main_sizer = wx.BoxSizer(wx.VERTICAL)
		self.helper_sizer = wx.BoxSizer(wx.VERTICAL)
		self.add_widgets('Identyfikator klasy:', "name", 0)
		self.main_sizer.Add(self.helper_sizer, border=20, flag=wx.LEFT | wx.RIGHT | wx.TOP)
		btn_sizer = wx.BoxSizer()
		save_btn = wx.Button(self, label='Zapisz zmiany')
		save_btn.Bind(wx.EVT_BUTTON, self.on_save)
		btn_sizer.Add(save_btn, 0, wx.ALL, 5)
		btn_sizer.Add(wx.Button(self, id=wx.ID_CANCEL), 0, wx.ALL, 5)
		self.main_sizer.Add(btn_sizer, 0, wx.CENTER)
		self.main_sizer.Fit(self)
		self.SetSizer(self.main_sizer)

	def on_save(self, evt):
		v = [
			self.controls["name"].GetValue(),
		]
		app_global_vars.active_db_con.update_record(
			table_name="Classes",
			col_names=("ClassIdentifier",),
			col_values=v,
			condition_str="ClassId = ?",
			condition_values=(self.index,)
		)
		self.Parent.list_ctrl.ClearAll()
		self.Parent.populateListView()
		self.Close()

	def add_widgets(self, label_text, ctrl_key, valIndex):
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		label = wx.StaticText(self, label=label_text, size=(150, -1))
		sizer.Add(label, flag=wx.ALIGN_CENTER_VERTICAL)
		sizer.AddSpacer(10)
		self.controls[ctrl_key] = wx.TextCtrl(self, value=self.data[valIndex])
		sizer.Add(self.controls[ctrl_key])
		self.helper_sizer.Add(sizer)


class classesContextMenu(wx.Menu):

	def __init__(self, parent):
		super().__init__()
		self.parent = parent
		delClass = wx.MenuItem(self, id=wx.ID_DELETE, text='Usuń')
		editClass = wx.MenuItem(self, id=wx.ID_EDIT, text='Edytuj')
		showSchedule = wx.MenuItem(self, id=wx.ID_ANY, text='Wyświetl grafik')
		self.Append(editClass)
		self.Append(delClass)
		self.Append(showSchedule)
		self.Bind(wx.EVT_MENU, self.parent.on_edit, editClass)
		self.Bind(wx.EVT_MENU, self.parent.on_remove, delClass)
		self.Bind(wx.EVT_MENU, self.ShowSchedule, showSchedule)

	def ShowSchedule(self, event):
		index = self.parent.list_ctrl.GetFocusedItem()
		dbIndex = self.parent.list_ctrl.GetItemData(index)
		p = SchedulesPanel(self.parent.Parent, "cl.ClassId", dbIndex)
		frame.showPanel(p)


class classesPanel(wx.Panel):

	def __init__(self, parent, chosenInst):
		super().__init__(parent)
		self.inst = chosenInst
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		self.list_ctrl = wx.ListCtrl(
			self,
			size=(-1, 200),
			style=wx.LC_REPORT | wx.BORDER_SUNKEN
		)
		self.list_ctrl.Bind(wx.EVT_CONTEXT_MENU, self.onContext)
		self.list_ctrl.Bind(wx.EVT_KEY_UP, self.onKey)
		self.populateListView()
		main_sizer.Add(self.list_ctrl, 0, wx.ALL | wx.EXPAND, 5)
		newClass_BTN = wx.Button(self, label='Dodaj nową klasę')
		newClass_BTN.Bind(wx.EVT_BUTTON, self.on_NewClass)
		main_sizer.Add(newClass_BTN, 0, wx.ALL | wx.CENTER, 5)
		self.SetSizer(main_sizer)

	def onContext(self, event):
		self.PopupMenu(classesContextMenu(self), event.GetPosition())

	def onKey(self, event):
		if event.KeyCode == wx.WXK_ESCAPE:
			frame.switchPanels()

	def populateListView(self):
		self.list_ctrl.InsertColumn(0, 'Nazwa', width=400)
		for index, row in enumerate(
			app_global_vars.active_db_con.fetch_all_matching(
				table_name="Classes",
				col_names=("ClassId", "ClassIdentifier"),
				condition_str="ClassInInstitution = ?",
				seq=(self.inst,)
			)
		):
			self.list_ctrl.InsertItem(index, row["ClassIdentifier"])
			item = self.list_ctrl.GetItem(index)
			item.SetData(row["ClassId"])
			self.list_ctrl.SetItem(item)

	def on_remove(self, event):
		item = self.list_ctrl.GetItem(self.list_ctrl.GetFocusedItem())
		app_global_vars.active_db_con.delete_record(
			table_name="Classes",
			condition_string="ClassId = ? ",
			seq=[item.GetData()]
		)
		self.list_ctrl.DeleteItem(self.list_ctrl.GetFocusedItem())

	def on_NewClass(self, event):
		dlg = AddClassDLG(self, self.inst, True)
		dlg.ShowModal()
		dlg.Destroy()

	def on_edit(self, event):
		index = self.list_ctrl.GetFocusedItem()
		dbIndex = self.list_ctrl.GetItemData(index)
		cols = []
		for colNumber in range(0, self.list_ctrl.GetColumnCount()):
			cols.append(self.list_ctrl.GetItemText(index, colNumber))
		dlg = EditClassDialog(self, dbIndex, cols)
		dlg.ShowModal()
		dlg.Destroy()


class InstitutionContextMenu(wx.Menu):

	def __init__(self, parent):
		super().__init__()
		self.parent = parent
		showBreaks = wx.MenuItem(self, id=wx.ID_ANY, text='Wyświetl długie przerwy')
		addClass = wx.MenuItem(self, id=wx.ID_ANY, text='Dodaj klasę')
		addTeacher = wx.MenuItem(self, id=wx.ID_ANY, text='Dodaj nauczyciela')
		showClasses = wx.MenuItem(self, id=wx.ID_ANY, text='Wyświetl klasy')
		addSubject = wx.MenuItem(self, id=wx.ID_ANY, text='Dodaj przedmiot')
		lessonToSchedule = wx.MenuItem(self, id=wx.ID_ANY, text='Dodaj zajęcia do grafiku')
		addClasRoom = wx.MenuItem(self, id=wx.ID_ANY, text='Dodaj salę lekcyjną')
		showClassRooms = wx.MenuItem(self, id=wx.ID_ANY, text='Wyświetl sale lekcyjne')
		showSubjects = wx.MenuItem(self, id=wx.ID_ANY, text='Wyświetl przedmioty')
		showTeachers = wx.MenuItem(self, id=wx.ID_ANY, text='Wyświetl nauczycieli')
		showSchedule = wx.MenuItem(self, id=wx.ID_ANY, text='Wyświetl grafik')
		index = self.parent.list_ctrl.GetFocusedItem()
		dbIndex = self.parent.list_ctrl.GetItemData(index)
		res = app_global_vars.active_db_con.fetch_one(
			col_names=("HasBreaks",),
			table_name="Institutions",
			condition_string="InstitutionId = ?",
			seq=(dbIndex,)
		)
		if res["HasBreaks"] == 1:
			self.Append(showBreaks)
		self.Append(addClass)
		self.Append(addSubject)
		self.Append(addTeacher)
		self.Append(showClasses)
		self.Append(showSubjects)
		self.Append(showTeachers)
		self.Append(addClasRoom)
		self.Append(showClassRooms)
		self.Append(lessonToSchedule)
		self.Append(showSchedule)
		self.Bind(wx.EVT_MENU, self.showBreaks, showBreaks)
		self.Bind(wx.EVT_MENU, self.parent.on_AddSubject, addSubject)
		self.Bind(wx.EVT_MENU, self.parent.on_AddClass, addClass)
		self.Bind(wx.EVT_MENU, self.parent.on_AddTeacher, addTeacher)
		self.Bind(wx.EVT_MENU, self.parent.on_NewClassRoom, addClasRoom)
		self.Bind(wx.EVT_MENU, self.showClasses, showClasses)
		self.Bind(wx.EVT_MENU, self.ShowClassRooms, showClassRooms)
		self.Bind(wx.EVT_MENU, self.ShowSubjects, showSubjects)
		self.Bind(wx.EVT_MENU, self.ShowTeachers, showTeachers)
		self.Bind(wx.EVT_MENU, self.parent.on_AddLessonToSchedule, lessonToSchedule)
		self.Bind(wx.EVT_MENU, self.ShowSchedule, showSchedule)

	def showBreaks(self, event):
		index = self.parent.list_ctrl.GetFocusedItem()
		dbIndex = self.parent.list_ctrl.GetItemData(index)
		p = BreaksPanel(self.parent.Parent, dbIndex)
		frame.showPanel(p)

	def showClasses(self, event):
		index = self.parent.list_ctrl.GetFocusedItem()
		dbIndex = self.parent.list_ctrl.GetItemData(index)
		p = classesPanel(self.parent.Parent, dbIndex)
		frame.showPanel(p)

	def ShowSubjects(self, event):
		index = self.parent.list_ctrl.GetFocusedItem()
		dbIndex = self.parent.list_ctrl.GetItemData(index)
		p = SubjectsPanel(self.parent.Parent, dbIndex)
		frame.showPanel(p)

	def ShowTeachers(self, event):
		index = self.parent.list_ctrl.GetFocusedItem()
		dbIndex = self.parent.list_ctrl.GetItemData(index)
		p = TeachersPanel(self.parent.Parent, dbIndex)
		frame.showPanel(p)

	def ShowClassRooms(self, event):
		index = self.parent.list_ctrl.GetFocusedItem()
		dbIndex = self.parent.list_ctrl.GetItemData(index)
		p = ClassRoomsPanel(self.parent.Parent, dbIndex)
		frame.showPanel(p)

	def ShowSchedule(self, event):
		index = self.parent.list_ctrl.GetFocusedItem()
		dbIndex = self.parent.list_ctrl.GetItemData(index)
		p = SchedulesPanel(self.parent.Parent, "InstitutionId", dbIndex)
		frame.showPanel(p)


class AddClassDLG(wx.Dialog):

	controls = dict()

	def __init__(self, parent, index, refreshView):
		super().__init__(parent=parent, title="Dodaj Klasę")
		self.index = index
		self.refreshView = refreshView
		self.main_sizer = wx.BoxSizer(wx.VERTICAL)
		self.helper_sizer = wx.BoxSizer(wx.VERTICAL)
		self.add_widgets('Identyfikator klasy:', "name")
		self.main_sizer.Add(self.helper_sizer, border=20, flag=wx.LEFT | wx.RIGHT | wx.TOP)
		btn_sizer = wx.BoxSizer()
		save_btn = wx.Button(self, label='Dodaj')
		save_btn.Bind(wx.EVT_BUTTON, self.on_save)
		btn_sizer.Add(save_btn, 0, wx.ALL, 5)
		btn_sizer.Add(wx.Button(self, id=wx.ID_CANCEL), 0, wx.ALL, 5)
		self.main_sizer.Add(btn_sizer, 0, wx.CENTER)
		self.main_sizer.Fit(self)
		self.SetSizer(self.main_sizer)

	def on_save(self, evt):
		v = [
			self.controls["name"].GetValue(),
			self.index
		]
		app_global_vars.active_db_con.insert(
			table_name="Classes",
			col_names=("ClassIdentifier", "ClassInInstitution"),
			col_values=v
		)
		if self.refreshView:
			self.Parent.list_ctrl.ClearAll()
			self.Parent.populateListView()
		self.Close()

	def add_widgets(self, label_text, ctrl_key):
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		label = wx.StaticText(self, label=label_text, size=(150, -1))
		sizer.Add(label, flag=wx.ALIGN_CENTER_VERTICAL)
		sizer.AddSpacer(10)
		self.controls[ctrl_key] = wx.TextCtrl(self)
		sizer.Add(self.controls[ctrl_key])
		self.helper_sizer.Add(sizer)


class AddSubjectDLG(wx.Dialog):

	controls = dict()

	def __init__(self, parent, index, refreshView):
		super().__init__(parent=parent, title="Dodaj przedmiot")
		self.index = index
		self.refreshView = refreshView
		self.main_sizer = wx.BoxSizer(wx.VERTICAL)
		self.helper_sizer = wx.BoxSizer(wx.VERTICAL)
		self.add_widgets('Nazwa przedmiotu:', "name")
		self.main_sizer.Add(self.helper_sizer, border=20, flag=wx.LEFT | wx.RIGHT | wx.TOP)
		btn_sizer = wx.BoxSizer()
		save_btn = wx.Button(self, label='Dodaj')
		save_btn.Bind(wx.EVT_BUTTON, self.on_save)
		btn_sizer.Add(save_btn, 0, wx.ALL, 5)
		btn_sizer.Add(wx.Button(self, id=wx.ID_CANCEL), 0, wx.ALL, 5)
		self.main_sizer.Add(btn_sizer, 0, wx.CENTER)
		self.main_sizer.Fit(self)
		self.SetSizer(self.main_sizer)

	def on_save(self, evt):
		v = [
			self.controls["name"].GetValue(),
			self.index
		]
		app_global_vars.active_db_con.insert(
			table_name="Subjects",
			col_names=("SubjectName", "TaughtIn"),
			col_values=v
		)
		if self.refreshView:
			self.Parent.list_ctrl.ClearAll()
			self.Parent.populateListView()
		self.Close()

	def add_widgets(self, label_text, ctrl_key):
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		label = wx.StaticText(self, label=label_text, size=(150, -1))
		sizer.Add(label, flag=wx.ALIGN_CENTER_VERTICAL)
		sizer.AddSpacer(10)
		self.controls[ctrl_key] = wx.TextCtrl(self)
		sizer.Add(self.controls[ctrl_key])
		self.helper_sizer.Add(sizer)


class SchedulesContextMenu(wx.Menu):

	def __init__(self, parent):
		super().__init__()
		self.parent = parent
		delSchedule = wx.MenuItem(self, id=wx.ID_DELETE, text='Usuń')
		editSchedule = wx.MenuItem(self, id=wx.ID_EDIT, text='Edytuj')
		self.Append(editSchedule)
		self.Append(delSchedule)
		self.Bind(wx.EVT_MENU, self.parent.on_edit, editSchedule)
		self.Bind(wx.EVT_MENU, self.parent.on_remove, delSchedule)


class SchedulesPanel(wx.Panel):

	def __init__(self, parent, what, id):
		"""Displays schedule for a given  entity.
		To use provide entity id as a parameter and the name of the  column in the database representing it in a format table.colName"""
		super().__init__(parent)
		self.what = what
		self.id = id
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		self.list_ctrl = wx.ListCtrl(
			self,
			size=(-1, 200),
			style=wx.LC_REPORT | wx.BORDER_SUNKEN
		)
		self.list_ctrl.Bind(wx.EVT_CONTEXT_MENU, self.onContext)
		self.list_ctrl.Bind(wx.EVT_KEY_UP, self.onKey)
		self.populateListView()
		main_sizer.Add(self.list_ctrl, 0, wx.ALL | wx.EXPAND, 5)
		new_scheduleBTN = wx.Button(self, label='Dodaj zajęcia do grafiku')
		new_scheduleBTN.Bind(wx.EVT_BUTTON, self.on_NewSchedule)
		main_sizer.Add(new_scheduleBTN, 0, wx.ALL | wx.CENTER, 5)
		exportBTN = wx.Button(self, label='Eksportuj grafik')
		exportBTN.Bind(wx.EVT_BUTTON, self.on_export)
		main_sizer.Add(exportBTN, 0, wx.ALL | wx.CENTER, 5)
		self.SetSizer(main_sizer)

	def onContext(self, event):
		self.PopupMenu(SchedulesContextMenu(self), event.GetPosition())

	def onKey(self, event):
		if event.KeyCode == wx.WXK_ESCAPE:
			frame.switchPanels()

	def populateListView(self):
		self.list_ctrl.InsertColumn(0, 'Dzień tygodnia', width=100)
		self.list_ctrl.InsertColumn(1, 'Początek zajęć', width=100)
		self.list_ctrl.InsertColumn(2, 'Koniec zajęć', width=100)
		self.list_ctrl.InsertColumn(3, 'Przedmiot', width=200)
		self.list_ctrl.InsertColumn(4, 'Grupa', width=200)
		self.list_ctrl.InsertColumn(5, 'Prowadzący', width=200)
		self.list_ctrl.InsertColumn(6, 'Sala', width=200)
		for index, row in enumerate(
			app_global_vars.active_db_con.fetch_all_matching(
				table_name=(
					"Schedule sc JOIN  Subjects su ON sc.SubjectId = su.SubjectId "
					"JOIN Classes cl ON sc.ClassId = cl.ClassId "
					"join Teachers te on sc.TeacherId = te.TeacherId "
					"JOIN ClassRooms cr on sc.ClassRoomId = cr.ClassRoomId"
				),
				col_names=(
					"LessonId",
					"WeekDay",
					"LessonStartingHour",
					"LessonEndingHour",
					"SubjectName",
					"ClassIdentifier",
					"FirstName",
					"LastName",
					"ClassRoomIdentifier"
				),
				condition_str=f"{self.what} = ? ORDER BY  WeekDay, LessonStartingHour",
				seq=(self.id,)
			)
		):
			self.list_ctrl.InsertItem(index, WEEK_DAYS[row["WeekDay"]])
			self.list_ctrl.SetItem(index, 1, row["LessonStartingHour"])
			self.list_ctrl.SetItem(index, 2, row["LessonEndingHour"])
			self.list_ctrl.SetItem(index, 3, row["SubjectName"])
			self.list_ctrl.SetItem(index, 4, row["ClassIdentifier"])
			self.list_ctrl.SetItem(index, 5, ' '.join((row["FirstName"], row["LastName"])))
			self.list_ctrl.SetItem(index, 6, row["ClassRoomIdentifier"])
			item = self.list_ctrl.GetItem(index)
			item.SetData(row["LessonId"])
			self.list_ctrl.SetItem(item)

	def on_remove(self, event):
		item = self.list_ctrl.GetItem(self.list_ctrl.GetFocusedItem())
		app_global_vars.active_db_con.delete_record(
			table_name="Schedule",
			condition_string="LessonId = ? ",
			seq=(item.GetData(),)
		)
		self.list_ctrl.DeleteItem(self.list_ctrl.GetFocusedItem())

	def on_NewSchedule(self, event):
		dlg = LessonToScheduleDLG(self, self.id, True)
		dlg.ShowModal()
		dlg.Destroy()

	def on_edit(self, event):
		index = self.list_ctrl.GetFocusedItem()
		dbIndex = self.list_ctrl.GetItemData(index)
		cols = []
		for colNumber in range(0, self.list_ctrl.GetColumnCount()):
			cols.append(self.list_ctrl.GetItemText(index, colNumber))
		dlg = EditScheduleDLG(self, dbIndex, cols)
		dlg.ShowModal()
		dlg.Destroy()

	def on_export(self, event):
		rows = []
		header = [
			"Dzień tygodnia",
			"Godzina rozpoczęcia",
			"Godzina zakończenia",
			"Przedmiot",
			"Grupa",
			"Prowadzący",
			"Sala"
		]
		for itemIndex in range(0, self.list_ctrl.ItemCount):
			row = []
			for colIndex in range(0, self.list_ctrl.GetColumnCount()):
				row.append(self.list_ctrl.GetItemText(itemIndex, colIndex))
			rows.append(row)
		with wx.FileDialog(
			self,
			"Wybierz plik, do którego chcesz zapisać grafik",
			defaultFile="*.csv",
			wildcard="plik csv (*.csv)|*.csv",
			style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
		) as fileDialog:
			if fileDialog.ShowModal() == wx.ID_CANCEL:
				return
			pathname = fileDialog.GetPath()
			with open(pathname, "w", newline='', encoding='utf-8') as file:
				writer = csv.writer(file, delimiter="\t")
				writer.writerow(header)
				for row in rows:
					writer.writerow(row)


class InstitutionsPanel(frontend.views.institutions.listing):

	def on_AddClass(self, event):
		index = self.list_ctrl.GetFocusedItem()
		dbIndex = self.list_ctrl.GetItemData(index)
		dlg = AddClassDLG(self.Parent, dbIndex, False)
		dlg.ShowModal()
		dlg.Destroy()

	def on_AddSubject(self, event):
		index = self.list_ctrl.GetFocusedItem()
		dbIndex = self.list_ctrl.GetItemData(index)
		dlg = AddSubjectDLG(self.Parent, dbIndex, False)
		dlg.ShowModal()
		dlg.Destroy()

	def on_AddTeacher(self, event):
		index = self.list_ctrl.GetFocusedItem()
		dbIndex = self.list_ctrl.GetItemData(index)
		dlg = AddTeacherDLG(self.Parent, dbIndex, False)
		dlg.ShowModal()
		dlg.Destroy()

	def on_NewClassRoom(self, event):
		index = self.list_ctrl.GetFocusedItem()
		dbIndex = self.list_ctrl.GetItemData(index)
		dlg = AddClassRoomDLG(self.Parent, dbIndex, False)
		dlg.ShowModal()
		dlg.Destroy()

	def on_AddLessonToSchedule(self, event):
		index = self.list_ctrl.GetFocusedItem()
		dbIndex = self.list_ctrl.GetItemData(index)
		dlg = LessonToScheduleDLG(self.Parent, dbIndex, False)
		dlg.ShowModal()
		dlg.Destroy()


class mainFrame(wx.Frame):

	def __init__(self):
		self.mainPanel = InstitutionsPanel(self)
		self.currPanel = self.mainPanel
		self.oldPanel = self.mainPanel

	def switchPanels(self):
		"""Hides current view annd shows the one shown previously if any."""
		self.sizer.Remove(0)
		if self.oldPanel is None:
			self.oldPanel = self.mainPanel
		self.oldPanel.Show()
		self.currPanel.Hide()
		self.currPanel = self.oldPanel
		self.oldPanel = None
		self.Layout()
		self.currPanel.list_ctrl.SetFocus()

	def showPanel(self, toShow):
		"""Replaces the current view with the instance of `wx.Panel` provided as an parameter.
		The  previously shown panel can be accessed as `oldPanel` on the frame object."""
		self.oldPanel = self.currPanel
		self.currPanel = toShow
		self.sizer.Add(self.currPanel, 1, wx.EXPAND)
		self.currPanel.Show()
		self.oldPanel.Hide()
		self.Layout()
		toShow.list_ctrl.SetFocus()


if __name__ == '__main__':
	app_global_vars.active_db_con = backend.mariadb_connector.MariadbConnector.from_config()
	import frontend.app
	frontend.app.main()
