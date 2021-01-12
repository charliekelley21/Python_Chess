"""
This is the main driver file. It is responsible for handeling user input
and displaying the current GameState object
"""

import pygame as p
import ChessEngine

WIDTH = HEIGHT = 512 #400 is another option
DIMENSION = 8 #chess boards are 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15 #for animation later on
IMAGES = {}

'''
Initialize a global dictionary of images. This will be called exactly once in main
'''
def load_images():
    pieces = ['wP', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bP', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    #NOTE: we can access an image by saying 'IMAGES['wP']'

'''
The main driver for our code. This will handle user input and updating the graphics
'''
def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    gs = ChessEngine.GameState()
    validMoves = gs.get_valid_moves()
    moveMade = False#flag variable for when a move is made
    load_images() #only do this once, before the while loop, reduced time complexity
    running = True
    sqSelected = () #no square selected initially, keep track of last click (tuple: row, collumn)
    playerClicks = [] #up to two player clicks tracked
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.KEYDOWN:
                if e.key == p.K_BACKSPACE:
                    gs.undo_move()
                    moveMade = True
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos() #(x, y) location of mouse
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if sqSelected == (row, col): #user double clicked a square
                    sqSelected = () #unselect
                    playerClicks = []
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected) #append for both 1st and 2nd playerClicks
                #was that the second click?
                if len(playerClicks) == 2: #after second click
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    for i in range(len(validMoves)):
                        if move == validMoves[i]:
                            gs.make_move(validMoves[i])
                            moveMade = True
                            sqSelected = () #reset user clicks
                            playerClicks = []
                    if not moveMade:
                        playerClicks = [sqSelected]
        if moveMade:
            validMoves = gs.get_valid_moves()
            moveMade = False

        draw_game_state(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()
    print(gs.board)

'''
Draws the squares and pieces on the boards. Responsible for all graphics.
'''
def draw_game_state(screen, gs):
    draw_board(screen) #draw squares on board
    #add in pieces highlighting or move suggestions (later)
    draw_pieces(screen, gs.board) #draw pieces on top of these squares

'''
Draw the squares on the boards. The top left square is always white
'''
def draw_board(screen):
    colors = [p.Color("white"), p.Color("gray")] #white - remainder 0, black - 1
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
Draw the pieces on the board using the current GameState.board
'''
def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--": #not an empty square
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

if __name__ == "__main__":
    main()
