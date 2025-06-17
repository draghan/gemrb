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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
#
#instead of credits, you can listen the songs of the game :)
import GemRB
from GUIDefines import *

MoviesTable = 0

def OnLoad():
	global MovieWindow, TextAreaControl, MoviesTable

	MovieWindow = GemRB.LoadWindow(2, "GUIMOVIE")
	TextAreaControl = MovieWindow.GetControl(0)
	PlayButton = MovieWindow.GetControl(2)
	CreditsButton = MovieWindow.GetControl(3)
	DoneButton = MovieWindow.GetControl(4)
	MoviesTable = GemRB.LoadTable("MUSIC")
	TextAreaControl.SetOptions([MoviesTable.GetRowName(i) for i in range(0, MoviesTable.GetRowCount() )], "MovieIndex", 0)
	PlayButton.SetText(17318)
	CreditsButton.SetText(15591)
	DoneButton.SetText(11973)
	DoneButton.MakeEscape()

	PlayButton.OnPress (PlayPress)
	CreditsButton.OnPress (CreditsPress)
	DoneButton.OnPress (MovieWindow.Close)
	MovieWindow.Focus()
	return
	
def PlayPress():
	s = GemRB.GetVar("MovieIndex")
	t = MoviesTable.GetValue(s, 0)
	GemRB.LoadMusicPL(t,1)
	return

def CreditsPress():
	GemRB.PlayMovie("CREDITS", 1)
	return
