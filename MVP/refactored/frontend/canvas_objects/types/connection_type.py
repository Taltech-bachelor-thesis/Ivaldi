from enum import Enum


class ConnectionType(Enum):
    GENERIC = 0
    FIRST = 1
    SECOND = 2
    THIRD = 3
    FOURTH = 4
    FIFTH = 5
    SIXTH = 6
    SEVENTH = 7
    EIGHTH = 8
    NINTH = 9

    COLORS = ['black', 'steel blue',
              'cyan', 'green yellow', 'hot pink',
              'SlateBlue1', 'SeaGreen1',
              'DarkOliveGreen1', 'goldenrod2', 'red3',]

    LABEL_NAMES = ['Black', 'Blue',
                   'Cyan', 'Green Yellow', 'Hot Pink',
                   'Slate Blue', 'Sea Green',
                   'Olive Green', 'Gold', 'Red']

    def next(self):
        self.COLORS: Enum
        return ConnectionType((self.value + 1) % len(self.COLORS.value))
