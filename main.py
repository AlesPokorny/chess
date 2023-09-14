from chess import Chess
import platform

game = Chess(windows=platform.system() == "Windows")
game.run()
game.tk_root.mainloop()
