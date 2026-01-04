import io
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from fretboardgtr.fretboard import FretBoard , FretBoardConfig
from fretboardgtr.notes_creators import ScaleFromName





class Guitar:
    def __init__(self, tuning):
        self.tuning = tuning


        
    def fretboard_config(self):
        self.config = {
            "general": {
                FretBoard.TUNING_KEY: self.tuning,
                FretBoard.FIRST_FRET_KEY: 0,
                FretBoard.LAST_FRET_KEY: 24,
                
                "show_tuning": True,
                "show_frets": True,
                "show_note_name": False,
                "show_degree_name": True,
                "open_color_scale": True,
                "fretted_color_scale": True,
                "fretted_colors": {
                    "root": "rgb(255,255,255)",
                },
                "open_colors": {
                    "root": "rgb(255,255,255)",
                },
                "enharmonic": True,
            },
            "background": {"color": "rgb(0,0,50)", "opacity": 0.4},
            "frets": {"color": "rgb(150,150,150)"},
            "fret_numbers": {"color": "rgb(150,150,150)", "fontsize": 20, "fontweight": "bold"},
            "strings": {"color": "rgb(200,200,200)", "width": 2},
        }
        return self.config
    
    def print_fretboard(self):
        fret_config = self.fretboard_config()
        fretboard = FretBoard(config=fret_config)
        scale = ScaleFromName(root="C", mode="Ionian").build()
        fretboard.add_notes(scale=scale)
        fretboard.export("my_fretboard.svg", format="svg")
        fp = open("my_fb.svg","w+")
        fp.write(fretboard.export("my_fb.svg", format="svg"))
        fp.close()
        
if __name__ == "__main__":
    guitar = Guitar(tuning="standard")
    guitar.tv_analog_Streambuffer()
    guitar.print_fretboard()
