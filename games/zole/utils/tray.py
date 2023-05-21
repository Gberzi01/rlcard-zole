"""
    File name: zole/utils/tray.py
"""


class Tray(object):
    def __init__(self, board_id: int):
        if board_id <= 0:
            raise Exception(f'Tray: invalid board_id={board_id}')
        self.board_id = board_id

    @property
    def dealer_id(self):
        return (self.board_id - 1) % 3

    def __str__(self):
        return f'{self.board_id}: dealer_id={self.dealer_id}'


if __name__ == '__main__':
    tray = Tray(4)
    print(tray)
