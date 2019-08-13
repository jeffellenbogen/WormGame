# WormGame

*wormgame2.py* is the original version of the game...keyboard based.

*wormgame_gamepad.py* uses the generic keypad controller to move the worm, and adds high score functionality.  Game now loops forever (or until ctl-c is pressed)

*usb_gamepad.py* is the driver module for the gamepad.  Uses the evdev package.

## High Score notes
Persistent high scores are now stored in the "high_scores.txt" file.  Could check in a default of this file to version control, but then every time we updated worm game, it would either push or pull those high scores as well.  As such, I think it's better to keep it out of version control.

One side effect here:  this means on the first deploy, you need to make a new "high_scores.txt" file (via "touch high_scores.txt"), and make sure that it's writeable (via "chmod 666 high_scores.txt")
