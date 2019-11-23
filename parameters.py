import pygame #Game library
from pygame.locals import * #For useful variables
import copy #Library used to make exact copies of lists.
import pickle #Library used to store dictionaries in a text file and read them from text files.
import random #Used for making random selections
from collections import defaultdict #Used for giving dictionary values default data types.
from collections import Counter #For counting elements in a list effieciently.
import threading #To allow for AI to think simultaneously while the GUI is coloring the board.


# Initialize the board:
board = [['Rb', 'Nb', 'Bb', 'Qb', 'Kb', 'Bb', 'Nb', 'Rb'],  # 8
         ['Pb', 'Pb', 'Pb', 'Pb', 'Pb', 'Pb', 'Pb', 'Pb'],  # 7
         [0, 0, 0, 0, 0, 0, 0, 0],  # 6
         [0, 0, 0, 0, 0, 0, 0, 0],  # 5
         [0, 0, 0, 0, 0, 0, 0, 0],  # 4
         [0, 0, 0, 0, 0, 0, 0, 0],  # 3
         ['Pw', 'Pw', 'Pw', 'Pw', 'Pw', 'Pw', 'Pw', 'Pw'],  # 2
         ['Rw', 'Nw', 'Bw', 'Qw', 'Kw', 'Bw', 'Nw', 'Rw']]  # 1
# a      b     c     d     e     f     g     h

# In chess some data must be stored that is not apparent in the board:
player = 0  # This is the player that makes the next move. 0 is white, 1 is black
castling_rights = [[True, True], [True, True]]
# The above stores whether or not each of the players are permitted to castle on
# either side of the king. (Kingside, Queenside)
En_Passant_Target = -1  # This variable will store a coordinate if there is a square that can be
# en passant captured on. Otherwise it stores -1, indicating lack of en passant
# targets.
half_move_clock = 0  # This variable stores the number of reversible moves that have been played so far.
# Generate an instance of GamePosition class to store the above data:

# Store the piece square tables here so they can be accessed globally by pieceSquareTable() function:
pawn_table = [0, 0, 0, 0, 0, 0, 0, 0,
              50, 50, 50, 50, 50, 50, 50, 50,
              10, 10, 20, 30, 30, 20, 10, 10,
              5, 5, 10, 25, 25, 10, 5, 5,
              0, 0, 0, 20, 20, 0, 0, 0,
              5, -5, -10, 0, 0, -10, -5, 5,
              5, 10, 10, -20, -20, 10, 10, 5,
              0, 0, 0, 0, 0, 0, 0, 0]
knight_table = [-50, -40, -30, -30, -30, -30, -40, -50,
                -40, -20, 0, 0, 0, 0, -20, -40,
                -30, 0, 10, 15, 15, 10, 0, -30,
                -30, 5, 15, 20, 20, 15, 5, -30,
                -30, 0, 15, 20, 20, 15, 0, -30,
                -30, 5, 10, 15, 15, 10, 5, -30,
                -40, -20, 0, 5, 5, 0, -20, -40,
                -50, -90, -30, -30, -30, -30, -90, -50]
bishop_table = [-20, -10, -10, -10, -10, -10, -10, -20,
                -10, 0, 0, 0, 0, 0, 0, -10,
                -10, 0, 5, 10, 10, 5, 0, -10,
                -10, 5, 5, 10, 10, 5, 5, -10,
                -10, 0, 10, 10, 10, 10, 0, -10,
                -10, 10, 10, 10, 10, 10, 10, -10,
                -10, 5, 0, 0, 0, 0, 5, -10,
                -20, -10, -90, -10, -10, -90, -10, -20]
rook_table = [0, 0, 0, 0, 0, 0, 0, 0,
              5, 10, 10, 10, 10, 10, 10, 5,
              -5, 0, 0, 0, 0, 0, 0, -5,
              -5, 0, 0, 0, 0, 0, 0, -5,
              -5, 0, 0, 0, 0, 0, 0, -5,
              -5, 0, 0, 0, 0, 0, 0, -5,
              -5, 0, 0, 0, 0, 0, 0, -5,
              0, 0, 0, 5, 5, 0, 0, 0]
queen_table = [-20, -10, -10, -5, -5, -10, -10, -20,
               -10, 0, 0, 0, 0, 0, 0, -10,
               -10, 0, 5, 5, 5, 5, 0, -10,
               -5, 0, 5, 5, 5, 5, 0, -5,
               0, 0, 5, 5, 5, 5, 0, -5,
               -10, 5, 5, 5, 5, 5, 0, -10,
               -10, 0, 5, 0, 0, 0, 0, -10,
               -20, -10, -10, 70, -5, -10, -10, -20]
king_table = [-30, -40, -40, -50, -50, -40, -40, -30,
              -30, -40, -40, -50, -50, -40, -40, -30,
              -30, -40, -40, -50, -50, -40, -40, -30,
              -30, -40, -40, -50, -50, -40, -40, -30,
              -20, -30, -30, -40, -40, -30, -30, -20,
              -10, -20, -20, -20, -20, -20, -20, -10,
              20, 20, 0, 0, 0, 0, 20, 20,
              20, 30, 10, 0, 0, 10, 30, 20]
king_endgame_table = [-50, -40, -30, -20, -20, -30, -40, -50,
                      -30, -20, -10, 0, 0, -10, -20, -30,
                      -30, -10, 20, 30, 30, 20, -10, -30,
                      -30, -10, 30, 40, 40, 30, -10, -30,
                      -30, -10, 30, 40, 40, 30, -10, -30,
                      -30, -10, 20, 30, 30, 20, -10, -30,
                      -30, -30, 0, 0, 0, 0, -30, -30,
                      -50, -30, -30, -30, -30, -30, -30, -50]

# Make the GUI:
# Start pygame
pygame.init()
# Load the screen with any arbitrary size for now:
screen = pygame.display.set_mode((600, 600))

# Load all the images:
# Load the background chess board image:
background = pygame.image.load('Media\\board.png').convert()
# Load an image with all the pieces on it:
pieces_image = pygame.image.load('Media\\Chess_Pieces_Sprite.png').convert_alpha()
circle_image_green = pygame.image.load('Media\\green_circle_small.png').convert_alpha()
circle_image_capture = pygame.image.load('Media\\green_circle_neg.png').convert_alpha()
circle_image_red = pygame.image.load('Media\\red_circle_big.png').convert_alpha()
greenbox_image = pygame.image.load('Media\\green_box.png').convert_alpha()
circle_image_yellow = pygame.image.load('Media\\yellow_circle_big.png').convert_alpha()
circle_image_green_big = pygame.image.load('Media\\green_circle_big.png').convert_alpha()
yellowbox_image = pygame.image.load('Media\\yellow_box.png').convert_alpha()
# Menu pictures:
withfriend_pic = pygame.image.load('Media\\withfriend.png').convert_alpha()
withAI_pic = pygame.image.load('Media\\withAI.png').convert_alpha()
playwhite_pic = pygame.image.load('Media\\playWhite.png').convert_alpha()
playblack_pic = pygame.image.load('Media\\playBlack.png').convert_alpha()
flipEnabled_pic = pygame.image.load('Media\\flipEnabled.png').convert_alpha()
flipDisabled_pic = pygame.image.load('Media\\flipDisabled.png').convert_alpha()

# Getting sizes:
# Get background size:
size_of_bg = background.get_rect().size
# Get size of the individual squares
square_width = int(size_of_bg[0] / 8)
square_height = int(size_of_bg[1] / 8)

# Rescale the images so that each piece can fit in a square:

pieces_image = pygame.transform.scale(pieces_image,
                                      (square_width * 6, square_height * 2))
circle_image_green = pygame.transform.scale(circle_image_green,
                                            (square_width, square_height))
circle_image_capture = pygame.transform.scale(circle_image_capture,
                                              (square_width, square_height))
circle_image_red = pygame.transform.scale(circle_image_red,
                                          (square_width, square_height))
greenbox_image = pygame.transform.scale(greenbox_image,
                                        (square_width, square_height))
yellowbox_image = pygame.transform.scale(yellowbox_image,
                                         (square_width, square_height))
circle_image_yellow = pygame.transform.scale(circle_image_yellow,
                                             (square_width, square_height))
circle_image_green_big = pygame.transform.scale(circle_image_green_big,
                                                (square_width, square_height))
withfriend_pic = pygame.transform.scale(withfriend_pic,
                                        (square_width * 4, square_height * 4))
withAI_pic = pygame.transform.scale(withAI_pic,
                                    (square_width * 4, square_height * 4))
playwhite_pic = pygame.transform.scale(playwhite_pic,
                                       (square_width * 4, square_height * 4))
playblack_pic = pygame.transform.scale(playblack_pic,
                                       (square_width * 4, square_height * 4))
flipEnabled_pic = pygame.transform.scale(flipEnabled_pic,
                                         (square_width * 4, square_height * 4))
flipDisabled_pic = pygame.transform.scale(flipDisabled_pic,
                                          (square_width * 4, square_height * 4))

# Make a window of the same size as the background, set its title, and
# load the background image onto it (the board):
screen = pygame.display.set_mode(size_of_bg)
pygame.display.set_caption('Shallow Green')
screen.blit(background, (0, 0))

# (the list contains references to objects of the class Piece)
# Initialize a list of shades:
listofShades = []

clock = pygame.time.Clock()  # Helps controlling fps of the game.
isDown = False  # Variable that shows if the mouse is being held down
# onto a piece
isClicked = False  # To keep track of whether a piece was clicked in order
# to indicate intention to move by the user.
isTransition = False  # Keeps track of whether or not a piece is being animated.
isDraw = False  # Will store True if the game ended with a draw
chessEnded = False  # Will become True once the chess game ends by checkmate, stalemate, etc.
isRecord = False  # Set this to True if you want to record moves to the Opening Book. Do not
# set this to True unless you're 100% sure of what you're doing. The program will never modify
# this value.
isAIThink = False  # Stores whether or not the AI is calculating the best move to be played.
# Initialize the opening book dictionary, and set its values to be lists by default:
openings = defaultdict(list)
# If openingTable.txt exists, read from it and load the opening moves to the local dictionary.
# If it doesn't, create a new one to write to if Recording is enabled:
try:
    file_handle = open('openingTable.txt', 'r+')
    openings = pickle.loads(file_handle.read())
except:
    if isRecord:
        file_handle = open('openingTable.txt', 'w')

searched = {}  # Global variable that allows negamax to keep track of nodes that have
# already been evaluated.
prevMove = [-1, -1, -1, -1]  # Also a global varible that stores the last move played, to
# allow drawBoard() to create Shades on the squares.
# Initialize some more values:
# For animating AI thinking graphics:
ax, ay = 0, 0
numm = 0
# For showing the menu and keeping track of user choices:
isMenu = True
isAI = -1
isFlip = -1
AIPlayer = -1
# Finally, a variable to keep false until the user wants to quit:
winner = 'b'
gameEnded = False
