import wx
import os
import csv
import backend.mariadb_connector
import backend.app_constants as app_global_vars
import frontend.views.institutions
import frontend.presenters.institutions_presenter


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
		self.main_sizer = wx.BoxSizer(wx.VERTICAL)
		self.helper_sizer = wx.BoxSizer(wx.VERTICAL)
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
			sizer.AddSpacer(10)
			self.controls["start_time"] = wx.Choice(
				self, choices=[lesson for lesson in self.lessons_without_breaks[:-3]]
			)
			sizer.Add(self.controls["start_time"])
			self.helper_sizer.Add(sizer)
			self.controls["start_time"].Bind(wx.EVT_CHOICE, self.on_choice)

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


class BreaksPanel(wx.Panel):

	def on_edit(self, event):
		index = self.list_ctrl.GetFocusedItem()
		dbIndex = self.list_ctrl.GetItemData(index)
		cols = []
		for colNumber in range(0, self.list_ctrl.GetColumnCount()):
			cols.append(self.list_ctrl.GetItemText(index, colNumber))
		dlg = EditBreakDLG(self, dbIndex, cols)
		dlg.ShowModal()
		dlg.Destroy()


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


class InstitutionContextMenu(wx.Menu):

	def __init__(self, parent):
		super().__init__()
		self.parent = parent
		lessonToSchedule = wx.MenuItem(self, id=wx.ID_ANY, text='Dodaj zajęcia do grafiku')
		showSchedule = wx.MenuItem(self, id=wx.ID_ANY, text='Wyświetl grafik')
		self.Append(lessonToSchedule)
		self.Append(showSchedule)
		self.Bind(wx.EVT_MENU, self.parent.on_AddLessonToSchedule, lessonToSchedule)
		self.Bind(wx.EVT_MENU, self.ShowSchedule, showSchedule)

	def ShowSchedule(self, event):
		index = self.parent.list_ctrl.GetFocusedItem()
		dbIndex = self.parent.list_ctrl.GetItemData(index)
		p = SchedulesPanel(self.parent.Parent, "InstitutionId", dbIndex)
		frame.showPanel(p)


class SchedulesPanel(wx.Panel):

	def populateListView(self):
		for index, row in enumerate(
			app_global_vars.active_db_con.fetch_all_matching(
				col_names=(
					"LessonId",
					"SubjectName",
					"ClassIdentifier",
					"FirstName",
					"LastName",
					"ClassRoomIdentifier"
				),
				condition_str=f"{self.what} = ? ORDER BY  WeekDay, LessonStartingHour",
			)
		):
			self.list_ctrl.SetItem(index, 6, row["ClassRoomIdentifier"])

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


if __name__ == '__main__':
	app_global_vars.active_db_con = backend.mariadb_connector.MariadbConnector.from_config()
	import frontend.app
	frontend.app.main()
