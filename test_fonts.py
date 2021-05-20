"""
Test if a specific font is supported by pygame to render text/characters or test all fonts in fontlist.txt.
reference: https://stackoverflow.com/questions/64395597/how-to-find-out-if-a-character-is-supported-by-a-font
"""

import pygame
import os.path as osp

# Window size
WINDOW_WIDTH    = 1000
WINDOW_HEIGHT   = 400
WINDOW_SURFACE  = pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE

DARK_BLUE = (   3,   5,  54 )
YELLOW    = ( 255, 255,   0 )
RED       = ( 255,   0,   0 )

# symbols to check if they are supported
symbols_vis = [ 'a', 'e', 'h', 'ß', 'ü', 'ä', 'ö', 'm', 'k', 'n', 'j', 'Ä', 'Ü' ]
symbols = [ 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'ä', 'ö', 'ü', 'ß', 'Ä', 'Ö', 'Ü', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9' ]

def glyphInFont( glyph, font ):
    """ Given a glyph and a font, use a pixel-finding heuristic to determine
        if the glyph renders to something other than an "empty border" non-existant
        font symbol.  Returns True if it renders to something. 
    """

    result = False
    WHITE  = ( 255, 255, 255 )   # can be any colour pair with contrast
    BLACK  = (   0,   0,   0 )

    try:
        text_image = font.render( glyph, True, WHITE, BLACK )
        text_rect  = text_image.get_rect()
        x_centre = text_rect.width // 2
        y_centre = text_rect.height // 2

        # Non-renderable glyphs have a border.
        # work out a 50% search box, centred inside the glyph
        box_top    = y_centre - ( text_rect.height // 4 )
        box_bottom = y_centre + ( text_rect.height // 4 )
        box_left   = x_centre - ( text_rect.width // 4 )
        box_right  = x_centre + ( text_rect.width // 4 )

        # Trace a Horizontal line through the middle of the bitmap 
        # looking for non-black pixels
        for x in range( box_left, box_right ):
            if ( text_image.get_at( ( x, y_centre ) ) != BLACK ):
                result = True
                break

        # If not found already, trace a line vertically
        if ( result == False ):
            for y in range( box_top, box_bottom ):
                if ( text_image.get_at( ( x_centre, y ) ) != BLACK ):
                    result = True
                    break

        # If still not found, check every pixel in the centre-box
        if ( result == False ):
            for y in range( box_top, box_bottom ):
                for x in range( box_left, box_right ):
                    if ( text_image.get_at( ( x, y ) ) != BLACK ):
                        result = True
                        break

    except UnicodeError as uce:
        # Glyph-ID not supported
        pass  # False goes through

    return result

# use this function to test only a few fonts with visualization 
def testFonts():

    ### initialization 
    pygame.init()
    pygame.mixer.init()
    window = pygame.display.set_mode( ( WINDOW_WIDTH, WINDOW_HEIGHT ), WINDOW_SURFACE )
    pygame.display.set_caption("Glyph Check")

    ### Make some fonts
    data_dir = 'data'
    font_path1 = osp.join(data_dir, 'fonts/roboto/Roboto-Bold.ttf') # supported one 
    font_path2 = osp.join(data_dir, 'fonts/patrickhand/PatrickHandSC-Regular.ttf')
    font1 = pygame.font.Font(font_path1, 64 )  
    font2 = pygame.font.Font(font_path2, 64)

    ### Main Loop
    clock = pygame.time.Clock()
    done = False
    while not done:

        # Handle user-input
        for event in pygame.event.get():
            if ( event.type == pygame.QUIT ):
                done = True

        # Update the window, but not more than 60fps
        window.fill( DARK_BLUE )

        # Simply to layout nicely on the screen
        cursor_x = 50
        cursor_y = (WINDOW_HEIGHT // 2 ) - 100

        # Loop through the symbol list, rendering the symbol if it exists
        # or an "x" otherwise
        for glyph in symbols_vis:
            cursor_x += 50
            
            if ( glyphInFont( glyph, font1 ) ):
                window.blit( font1.render( glyph, True, YELLOW ), ( cursor_x, cursor_y ) )
            else:
                # does not exist
                window.blit( font1.render( 'x', True, YELLOW ), ( cursor_x, cursor_y ) )

            if ( glyphInFont( glyph, font2 ) ):
                window.blit( font2.render( glyph, True, YELLOW ), ( cursor_x, cursor_y+100 ) )
            else:
                # does not exist
                window.blit( font2.render( 'x', True, YELLOW ), ( cursor_x, cursor_y+100 ) )

        pygame.display.flip()

        # Clamp FPS
        clock.tick( 3 ) # slow update

    pygame.quit()

# use this function to test all fonts in fontlist.txt for every character of the german alphabet
def testFontList():

    pygame.init()
    data_dir = 'data'

    FONT_LIST = osp.join(data_dir, 'fonts/fontlist.txt')
    fonts = [osp.join(data_dir,'fonts',f.strip()) for f in open(FONT_LIST)]
    
    unsupported = False
    # loop over all fonts 
    for i in range(len(fonts)): 
        # initialize them 
        font = pygame.font.Font(fonts[i], 64 )  
        # test rendering all symbols with specific font
        for glyph in symbols: 
            if glyphInFont(glyph, font): 
                continue
            else: 
                # font not suitable for rendering with pygame
                print(fonts[i]) 
                unsupported = True
    if not unsupported:
        print('all fonts in fontlist are supported by pygame')
    pygame.quit()

if __name__ == '__main__':
    testFontList()
    #testFonts()