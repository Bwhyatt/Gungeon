import pygame

def LoadSpriteSheet(path, frame_width, frame_height):
    sheet = pygame.image.load(path).convert_alpha()

    frames = []
    columns = sheet.get_width() // frame_width
    rows = sheet.get_height() // frame_height
    for y in range(rows):
        for x in range(columns):
            frame = sheet.subsurface(
                pygame.Rect(
                    x * frame_width,
                    y * frame_height,
                    frame_width,
                    frame_height
                )
            )
            frames.append(frame)

    return frames