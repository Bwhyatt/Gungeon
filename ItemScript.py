class Item:
    def __init__(self, x, y, name, sprite, buff_attr, buff_amt, is_multiplier):
        self.x = x
        self.y = y
        self.name = name
        self.sprite = sprite
        self.buff_attr = buff_attr
        self.buff_amt = buff_amt
        self.is_multiplier = is_multiplier
    def PickUp(self, player):
        player.inventory.append(self)
    def use_item(self, player):
        if hasattr(player, self.buff_attr):
            current = getattr(player, self.buff_attr)
            if self.is_multiplier:
                setattr(player, self.buff_attr, current * self.buff_amt)
            else:
                setattr(player, self.buff_attr, current + self.buff_amt)