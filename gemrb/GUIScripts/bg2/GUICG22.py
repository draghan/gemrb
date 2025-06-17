# GemRB - Infinity Engine Emulator
# Copyright (C) 2003-2007 The GemRB Project
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
#character generation, class kit (GUICG22)

import GemRB
import CommonTables
from ie_stats import *
from GUIDefines import *

import CharGenCommon

KitWindow = 0
TextAreaControl = 0
DoneButton = 0
SchoolList = 0
ClassName = 0
TopIndex = 0
RowCount = 10
KitTable = 0
Init = 0
MyChar = 0
KitSelected = 0 #store clicked kit on redraw as number within RowCount

def OnLoad():
	global KitWindow, TextAreaControl, DoneButton
	global SchoolList, ClassName
	global RowCount, TopIndex, KitTable, Init, MyChar

	MyChar = GemRB.GetVar ("Slot")
	Race = GemRB.GetPlayerStat (MyChar, IE_RACE)
	RaceName = CommonTables.Races.GetRowName(CommonTables.Races.FindValue (3, Race) )

	ClassName = CommonTables.Classes.GetRowName (GemRB.GetPlayerStat (MyChar, IE_HITPOINTS)) # barbarian hack

	KitTable = GemRB.LoadTable("kittable")
	KitTableName = KitTable.GetValue(ClassName, RaceName)
	KitTable = GemRB.LoadTable(KitTableName,1)

	SchoolList = GemRB.LoadTable("magesch")

	#there is a specialist mage window, but it is easier to use
	#the class kit window for both
	KitWindow = GemRB.LoadWindow(22, "GUICG")
	CharGenCommon.PositionCharGenWin(KitWindow)
	
	if ClassName == "MAGE":
		Label = KitWindow.GetControl(0xfffffff)
		Label.SetText(595)

	for i in range(10):
		if i<4:
			Button = KitWindow.GetControl(i+1)
		else:
			Button = KitWindow.GetControl(i+5)
		Button.SetState(IE_GUI_BUTTON_DISABLED)
		Button.SetFlags(IE_GUI_BUTTON_RADIOBUTTON, OP_OR)

	if not KitTable: # sorcerer or monk
		RowCount = 1
	else:
		if ClassName == "MAGE": # mages
			RowCount = SchoolList.GetRowCount()
		else:
			RowCount = KitTable.GetRowCount()

	TopIndex = 0
	GemRB.SetVar("TopIndex", 0)

	tmpRowCount = RowCount
	if RowCount > 10: # create 11th kit button
		extrakit = KitWindow.CreateButton (15, 18, 250, 271, 20)
		extrakit.SetState (IE_GUI_BUTTON_DISABLED)
		extrakit.SetFlags (IE_GUI_BUTTON_RADIOBUTTON | IE_GUI_BUTTON_CAPS, OP_OR)
		extrakit.SetSprites ("GUICGBC", 0, 0, 1, 2, 3)
		RowCount = 11

	if tmpRowCount > 11: # create scrollbar
		ScrollBar = KitWindow.CreateScrollBar (1000, {'x' : 290, 'y' : 50, 'w' : 16, 'h' : 220}, "GUISCRCW")
		ScrollBar.SetVarAssoc ("TopIndex", tmpRowCount - 10, 0, tmpRowCount - 10)
		ScrollBar.OnChange (RedrawKits)
		KitWindow.SetEventProxy (ScrollBar)

	for i in range(RowCount):
		if i<4:
			Button = KitWindow.GetControl(i+1)
		else:
			Button = KitWindow.GetControl(i+5)
		Button.SetVarAssoc("ButtonPressed", i)
		Button.OnPress (KitPress)

	BackButton = KitWindow.GetControl(8)
	BackButton.SetText(15416)
	BackButton.MakeEscape()
	DoneButton = KitWindow.GetControl(7)
	DoneButton.SetText(11973)
	DoneButton.MakeDefault()

	TextAreaControl = KitWindow.GetControl(5)
	TextAreaControl.SetText(17247)

	DoneButton.OnPress (NextPress)
	BackButton.OnPress (BackPress)
	Init = 1
	RedrawKits()
	KitPress()
	KitWindow.Focus()
	return

def RedrawKits():
	global TopIndex, Init, KitSelected

	TopIndex=GemRB.GetVar("TopIndex")
	EnabledButtons = []
	for i in range(RowCount):
		if i<4:
			Button = KitWindow.GetControl(i+1)
		else:
			Button = KitWindow.GetControl(i+5)
		Button.SetState(IE_GUI_BUTTON_DISABLED)
		if not KitTable:
			KitIndex = 0
			KitName = CommonTables.Classes.GetValue (ClassName, "NAME_REF")
		else:
			KitIndex = KitTable.GetValue (i + TopIndex, 0)
			if ClassName == "MAGE":
				KitName = SchoolList.GetValue (i+TopIndex, 0)
				if KitIndex == 0:
					KitName = SchoolList.GetValue ("GENERALIST", "NAME_REF")
					Button.SetState(IE_GUI_BUTTON_ENABLED)
					if Init: #preselection of mage plain kit
						Button.SetState(IE_GUI_BUTTON_SELECTED)
						KitSelected = i+TopIndex
						Init=0
				if KitIndex != "*":
					EnabledButtons.append (KitIndex - 21)
			else:
				if KitIndex and KitIndex != "*":
					KitName = CommonTables.KitList.GetValue (KitIndex, 1)
				else:
					KitName = CommonTables.Classes.GetValue (ClassName, "NAME_REF")
		Button.SetText(KitName)
		if not EnabledButtons or i+TopIndex in EnabledButtons:
			Button.SetState(IE_GUI_BUTTON_ENABLED)
			if Init and i+TopIndex>0:
				Button.SetState(IE_GUI_BUTTON_SELECTED)
				KitSelected = i+TopIndex
				Init=0
		if KitIndex == "*":
			continue
		if Init and i+TopIndex==0:
			if EnabledButtons:
				GemRB.SetVar("ButtonPressed", EnabledButtons[0]) #but leave Init==1
			else:
				GemRB.SetVar("ButtonPressed", 0)
				Button.SetState(IE_GUI_BUTTON_SELECTED) 
				KitSelected = i+TopIndex
				Init=0
		if not Init and i+TopIndex == KitSelected: #remark selection state on redraw
			Button.SetState(IE_GUI_BUTTON_SELECTED)
	return

def KitPress():
	global KitSelected

	ButtonPressed=GemRB.GetVar("ButtonPressed")
	KitSelected = ButtonPressed + TopIndex
	if not KitTable:
		KitIndex = 0
	else:
		KitIndex = KitTable.GetValue (ButtonPressed + TopIndex, 0)
		if ClassName == "MAGE":
			if ButtonPressed + TopIndex == 0:
				KitIndex = 0
			else:
				KitIndex = ButtonPressed + TopIndex + 21

	if ClassName == "MAGE" and KitIndex != 0:
		GemRB.SetVar ("MAGESCHOOL", KitIndex - 21) # hack: -21 to make the generalist 0
	else:
		GemRB.SetVar("MAGESCHOOL", 0) # so bards don't get schools

	if KitIndex == 0:
		KitDescription = CommonTables.Classes.GetValue (ClassName, "DESC_REF")
	else:
		KitDescription = CommonTables.KitList.GetValue (KitIndex, 3)

	TextAreaControl.SetText(KitDescription)
	DoneButton.SetState(IE_GUI_BUTTON_ENABLED)

	GemRB.SetVar ("Class Kit", KitIndex)

	return

def BackPress():
	GemRB.SetVar("Class Kit", 0) # reverting the value so we are idempotent
	GemRB.SetVar("MAGESCHOOL", 0)
	if KitWindow:
		KitWindow.Close ()
	GemRB.SetNextScript("GUICG2")
	return

def NextPress():
	if KitWindow:
		KitWindow.Close ()

	#make gnomes always kitted
	KitIndex = GemRB.GetVar ("Class Kit")
	MageSchool = GemRB.GetVar ("MAGESCHOOL")
	if MageSchool and not KitIndex:
		KitValue = SchoolList.GetValue (MageSchool, 3)
	elif KitIndex:
		KitValue = CommonTables.KitList.GetValue (KitIndex, 6)
	else:
		KitValue = 0

	#save the kit
	GemRB.SetPlayerStat (MyChar, IE_KIT, KitValue)

	GemRB.SetNextScript("CharGen4") #abilities
	return
