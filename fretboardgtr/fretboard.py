class FretBoardConfig:
    """Configuration class for fretboard settings"""
    def __init__(self, config=None):
        self.config = config or {}

class FretBoard:
    """Main FretBoard class for guitar fretboard visualization"""

    # Class constants
    TUNING_KEY = "tuning"
    FIRST_FRET_KEY = "first_fret"
    LAST_FRET_KEY = "last_fret"

    def __init__(self, config=None):
        self.config = config or {}
        self.notes = []

    def add_notes(self, scale=None):
        """Add notes to the fretboard"""
        if scale:
            self.notes.extend(scale)

    def export(self, filename=None, format="svg"):
        """Export fretboard as SVG or other format"""
        # Mock SVG output for demonstration
        svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="600" height="200" xmlns="http://www.w3.org/2000/svg">
  <rect width="600" height="200" fill="rgb(0,0,50)" opacity="0.4"/>
  <!-- Fretboard visualization would go here -->
  <text x="10" y="20" fill="white" font-size="16">Guitar Fretboard</text>
  <text x="10" y="40" fill="white" font-size="12">Tuning: {}</text>
</svg>'''.format(self.config.get('general', {}).get('tuning', 'standard'))

        if filename:
            return svg_content
        return svg_content
