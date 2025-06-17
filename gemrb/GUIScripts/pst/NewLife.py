# GemRB - Infinity Engine Emulator
# Copyright (C) 2003 The GemRB Project
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

# NewLife.py - Character generation screen

###################################################

import GemRB
from GUIDefines import *
from ie_stats import *
import CommonTables

CommonTables.Load()

NewLifeWindow = 0
TextArea = 0

TotLabel = 0
AcLabel = 0
HpLabel = 0

StatTable = 0
# maintain this order in all lists!
StatIDs = [ IE_STR, IE_INT, IE_WIS, IE_DEX, IE_CON, IE_CHR ]
StatLimit = [ 18, 18, 18, 18, 18, 18 ]
StatLabels = [ None ] * 6
StatLowerLimit = [ 9 ] * 6

LevelUp = 0
TotPoints = 0
AcPoints = 0
HpPoints = 0

def OnLoad():
	OpenLUStatsWindow (0)
	return

def OpenLUStatsWindow(Type = 1, LevelDiff = 0):
	global NewLifeWindow, StatTable
	global TotPoints, AcPoints, HpPoints
	global TotLabel, AcLabel, HpLabel
	global TextArea, StatLabels, StatLowerLimit, StatLimit, LevelUp

	LevelUp = Type
	if LevelUp:
		# only TNO gets the main stat boosts
		pc = GemRB.GameGetSelectedPCSingle ()
		Specific = GemRB.GetPlayerStat (pc, IE_SPECIFIC)
		if Specific != 2 or LevelDiff == 0:
			return
	else:
		GemRB.CreatePlayer ("charbase", 1)

	StatTable = GemRB.LoadTable("abcomm")

	#setting up CG window
	NewLifeWindow = GemRB.LoadWindow(0, "GUICG")

	if LevelUp:
		StatLowerLimit = []
		for stat in StatIDs:
			StatLowerLimit.append (GemRB.GetPlayerStat (1, stat, 1))
		TotPoints = LevelDiff
		StatLimit = [ 25 ] * 6
	else:
		for stat in StatIDs:
			GemRB.SetPlayerStat (1, stat, 9)
		TotPoints = 21

	# stat label controls
	for i in range(6):
		StatLabels[i] = NewLifeWindow.GetControl(0x10000018 + i)

	# individual stat buttons
	for i in range(6):
		Button = NewLifeWindow.GetControl (i+2)
		Button.SetFlags (IE_GUI_BUTTON_NO_IMAGE, OP_SET)
		Button.OnMouseEnter (StatPress[i])

	Button = NewLifeWindow.GetControl(8)
	Button.SetFlags(IE_GUI_BUTTON_RADIOBUTTON, OP_SET)
	Button.SetState(IE_GUI_BUTTON_LOCKED)
	Button.SetSprites("", 0, 0, 0, 0, 0)
	Button.SetText(5025)
	Button.OnMouseEnter (AcPress)

	Button = NewLifeWindow.GetControl(9)
	Button.SetFlags(IE_GUI_BUTTON_RADIOBUTTON, OP_SET)
	Button.SetState(IE_GUI_BUTTON_LOCKED)
	Button.SetSprites("", 0, 0, 0, 0, 0)
	Button.SetText(5026)
	Button.OnMouseEnter (HpPress)

	Button = NewLifeWindow.GetControl(10)
	Button.SetFlags(IE_GUI_BUTTON_RADIOBUTTON, OP_SET)
	Button.SetState(IE_GUI_BUTTON_LOCKED)
	Button.SetSprites("", 0, 0, 0, 0, 0)
	Button.SetText(5027)
	Button.OnMouseEnter (PointPress)

	# stat +/- buttons
	for i in range(len(StatPress)):
		Button = NewLifeWindow.GetControl (11+2*i)
		Button.OnPress (IncreasePress)
		Button.OnMouseEnter (StatPress[i])
		Button.SetVarAssoc ("Pressed", i)
		Button.SetActionInterval (200)

		Button = NewLifeWindow.GetControl (12+2*i)
		Button.OnPress (DecreasePress)
		Button.OnMouseEnter (StatPress[i])
		Button.SetVarAssoc ("Pressed", i)
		Button.SetActionInterval (200)

	NewLifeLabel = NewLifeWindow.GetControl(0x10000023)
	if LevelUp:
		NewLifeLabel.SetText(19356)
	else:
		NewLifeLabel.SetText(1899)

	TextArea = NewLifeWindow.GetControl(23)
	TextArea.SetText(18495)

	TotLabel = NewLifeWindow.GetControl(0x10000020)
	AcLabel = NewLifeWindow.GetControl(0x1000001E)
	HpLabel = NewLifeWindow.GetControl(0x1000001F)

	Label = NewLifeWindow.GetControl(0x10000021)
	Label.SetText(254)

	PhotoButton = NewLifeWindow.GetControl(35)
	PhotoButton.SetState(IE_GUI_BUTTON_LOCKED)
	PhotoButton.SetFlags(IE_GUI_BUTTON_NO_IMAGE | IE_GUI_BUTTON_PICTURE, OP_SET)
	PhotoButton.OnMouseEnter (OverPhoto)
	PhotoButton.SetPicture("STPNOC")

	AcceptButton = NewLifeWindow.GetControl(0)
	AcceptButton.SetText(4192)
	AcceptButton.OnPress (AcceptPress)
	AcceptButton.MakeDefault()

	CancelButton = NewLifeWindow.GetControl(1)
	CancelButton.SetText(4196)
	CancelButton.OnPress (CancelPress)
	if LevelUp:
		CancelButton.SetState(IE_GUI_BUTTON_DISABLED)

	UpdateLabels()

	NewLifeWindow.Focus()
	return

def UpdateLabels():
	global AcPoints, HpPoints

	Str = GemRB.GetPlayerStat(1, IE_STR, 1)
	strEx = GemRB.GetPlayerStat(1, IE_STREXTRA, 1)
	if Str != 18 or strEx == 0:
		StatLabels[0].SetText(str(Str))
	else:
		StatLabels[0].SetText("18/" + ("00" if strEx == 100 else str(strEx)))
	for i in range(1, 6):
		StatLabels[i].SetText (str(GemRB.GetPlayerStat (1, StatIDs[i], 1)))

	TotLabel.SetText(str(TotPoints))
	if LevelUp:
		AcPoints = GemRB.GetPlayerStat(1, IE_ARMORCLASS, 1)
	else:
		AcPoints = 10
		Dex = GemRB.GetPlayerStat(1, IE_DEX, 1)
		if Dex > 14:
			AcPoints = AcPoints - (Dex-14)

	if LevelUp:
		HpPoints = GemRB.GetPlayerStat(1, IE_HITPOINTS, 1)
	else:
		HpPoints = 20
		Con = GemRB.GetPlayerStat(1, IE_CON, 1)
		if Con > 14:
			HpPoints = HpPoints + (Con-9)*2 + (Con-14)
		else:
			HpPoints = HpPoints + (Con-9)*2

	AcLabel.SetText(str(AcPoints))
	HpLabel.SetText(str(HpPoints))
	return

def AcceptPress():
	if TotPoints:
		QuitWindow = GemRB.LoadWindow(1, "GUICG")
		TextArea = QuitWindow.GetControl(0)
		TextArea.SetText(46782)

		Button = QuitWindow.GetControl(1)
		Button.SetText("")
		Button.SetFlags(IE_GUI_BUTTON_NO_IMAGE,OP_SET)
		Button.SetState(IE_GUI_BUTTON_DISABLED)
		Button = QuitWindow.GetControl(2)
		Button.SetText(46783)
		Button.MakeDefault()
		Button.OnPress (QuitWindow.Close)
		QuitWindow.ShowModal (MODAL_SHADOW_GRAY)
		return

	if LevelUp:
		# Return to the RecordsWindow
		NewLifeWindow.Close()
		return

	#don't add con bonus, it will be calculated by the game
	#interestingly enough, the game adds only one level's con bonus
	Table = GemRB.LoadTable ("hpinit")
	x = Table.GetValue (str(GemRB.GetPlayerStat (1, IE_CON, 1)), "HP")
	
	GemRB.SetPlayerStat(1, IE_MAXHITPOINTS, x)
	GemRB.SetPlayerStat(1, IE_HITPOINTS, x + 100) # x + 100 ensures the player starts at max hp when con > 14

	GemRB.FillPlayerInfo(1) #does all the rest
	#LETS PLAY!!
	GemRB.EnterGame()
	return

def CancelPress():
	QuitWindow = GemRB.LoadWindow(1, "GUICG")
	
	TextArea = QuitWindow.GetControl(0)
	TextArea.SetText(19406)
	
	def confirm():
		QuitWindow.Close()
		NewLifeWindow.Close()

	Button = QuitWindow.GetControl(1)
	Button.SetText(23787)
	Button.MakeDefault()
	Button.SetState(IE_GUI_BUTTON_ENABLED)
	Button.OnPress (confirm)

	Button = QuitWindow.GetControl(2)
	Button.SetText(23789)
	Button.MakeDefault()
	Button.OnPress (QuitWindow.Close)

	QuitWindow.ShowModal (MODAL_SHADOW_GRAY)
	return

def StrPress(btn = None, delta = 0):
	TextArea.SetText(18489)

	s = GemRB.GetPlayerStat(1, IE_STR, 1)
	strEx = GemRB.GetPlayerStat (1, IE_STREXTRA, 1)
	extras = (30, 60, 90, 99, 100)
	if delta == -1 and (s < 18 or s > 19):
		s -= 1
	elif delta == -1 and s == 19:
		s -= 1
		strEx = 100
	elif delta == -1 and s == 18:
		if strEx == 0:
			s -= 1
		elif strEx == 30:
			strEx = 0
		else:
			idx = extras.index (strEx)
			strEx = extras[idx - 1]
	elif delta == 1 and (s < 18 or s >= 19):
		s += 1
	elif delta == 1 and s == 18:
		if strEx == 100:
			s += 1
			strEx = 0
		elif strEx == 0:
			strEx = extras[0]
		else:
			idx = extras.index (strEx)
			strEx = extras[idx + 1]
	if delta != 0:
		GemRB.SetPlayerStat (1, IE_STR, s)
		GemRB.SetPlayerStat (1, IE_STREXTRA, strEx)

	toHit = CommonTables.StrMod.GetValue(s, 0)
	damage = CommonTables.StrMod.GetValue(s, 1)
	# this is for the STR==16 case, which displays only one number
	if toHit == 0:
		toHit = damage
		damage = 0
	elif s == 18 and strEx:
		toHit = toHit + CommonTables.StrModEx.GetValue (strEx, 0)
		damage = damage + CommonTables.StrModEx.GetValue (strEx, 1)

	if s == 18 and strEx > 60:
		s=19
	TextArea.Append("\n\n" + GemRB.GetString(StatTable.GetValue(s, 0), STRING_FLAGS_RESOLVE_TAGS).format(toHit, damage))
	return

def IntPress(delta = 0):
	TextArea.SetText(18488)
	intl = GemRB.GetPlayerStat(1, IE_INT, 1)
	TextArea.Append ("\n\n" + GemRB.GetString (StatTable.GetValue (intl, 1), STRING_FLAGS_RESOLVE_TAGS).format(0, 0))
	return

def WisPress(delta = 0):
	TextArea.SetText(18490)
	wis = GemRB.GetPlayerStat(1, IE_WIS, 1)
	TextArea.Append ("\n\n" + GemRB.GetString (StatTable.GetValue (wis, 2), STRING_FLAGS_RESOLVE_TAGS).format(0, 0))
	return

def DexPress(delta = 0):
	Table = GemRB.LoadTable("dexmod")
	dex = GemRB.GetPlayerStat (1, IE_DEX, 1)
	x = -Table.GetValue (dex, 2)
	TextArea.SetText(18487)
	TextArea.Append ("\n\n" + GemRB.GetString (StatTable.GetValue (dex, 3), STRING_FLAGS_RESOLVE_TAGS).format(x, 0))
	return

def ConPress(delta = 0):
	Table = GemRB.LoadTable("hpconbon")
	con = GemRB.GetPlayerStat(1, IE_CON, 1)
	x = Table.GetValue (con - 1, 1)
	TextArea.SetText(18491)
	TextArea.Append ("\n\n" + GemRB.GetString (StatTable.GetValue (con, 4), STRING_FLAGS_RESOLVE_TAGS).format(x, 0))
	return

def ChaPress(delta = 0):
	TextArea.SetText(1903)
	cha = GemRB.GetPlayerStat (1, IE_CHR, 1)
	TextArea.Append ("\n\n" + GemRB.GetString (StatTable.GetValue (cha, 5), STRING_FLAGS_RESOLVE_TAGS).format(0, 0))
	return

StatPress = [ StrPress, IntPress, WisPress, DexPress, ConPress, ChaPress ]

def PointPress():
	TextArea.SetText(18492)
	return

def AcPress():
	TextArea.SetText(18493)
	return

def HpPress():
	TextArea.SetText(18494)
	return

def DecreasePress():
	global TotPoints

	Pressed = GemRB.GetVar("Pressed")
	Sum = GemRB.GetPlayerStat(1, StatIDs[Pressed], 1)
	if Sum <= StatLowerLimit[Pressed]:
		return
	TotPoints = TotPoints+1
	if StatIDs[Pressed] != IE_STR:
		GemRB.SetPlayerStat (1, StatIDs[Pressed], Sum - 1)

	StatPress[Pressed](delta = -1)
	UpdateLabels()
	return

def IncreasePress():
	global TotPoints

	if TotPoints<=0:
		return
	Pressed = GemRB.GetVar("Pressed")
	Sum = GemRB.GetPlayerStat(1, StatIDs[Pressed], 1)
	if Sum >= StatLimit[Pressed] and (StatIDs[Pressed] != IE_STR or GemRB.GetPlayerStat(1, IE_STREXTRA, 1) == 100):
		return

	TotPoints = TotPoints-1
	if StatIDs[Pressed] != IE_STR:
		GemRB.SetPlayerStat (1, StatIDs[Pressed], Sum + 1)

	StatPress[Pressed](delta = 1)
	UpdateLabels()
	return

def OverPhoto():
	global TextArea
	TextArea.SetText (18495) # yep, the same is shown during level up
