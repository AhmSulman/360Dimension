class ScaleFromName:
    """Class for creating musical scales from names"""

    def __init__(self, root="C", mode="Ionian"):
        self.root = root
        self.mode = mode
        self.notes = []

    def build(self):
        """Build the scale notes"""
        # Basic chromatic scale starting from C
        chromatic = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

        # Define scale patterns (intervals)
        scale_patterns = {
            "Ionian": [0, 2, 4, 5, 7, 9, 11],  # Major scale
            "Dorian": [0, 2, 3, 5, 7, 9, 10],  # Minor scale with raised 6th
            "Phrygian": [0, 1, 3, 5, 7, 8, 10],  # Minor scale with flat 2nd
            "Lydian": [0, 2, 4, 6, 7, 9, 11],  # Major scale with raised 4th
            "Mixolydian": [0, 2, 4, 5, 7, 9, 10],  # Major scale with flat 7th
            "Aeolian": [0, 2, 3, 5, 7, 8, 10],  # Natural minor
            "Locrian": [0, 1, 3, 5, 6, 8, 10],  # Diminished scale
        }

        # Get root note index
        if self.root in chromatic:
            root_index = chromatic.index(self.root)
        else:
            root_index = 0  # Default to C

        # Build scale using pattern
        pattern = scale_patterns.get(self.mode, scale_patterns["Ionian"])
        self.notes = [(chromatic[(root_index + interval) % 12]) for interval in pattern]

        return self.notes
