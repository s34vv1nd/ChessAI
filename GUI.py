from parameters import *
from chessprocesssing import *

class Shades:
    # Self explanatory:
    def __init__(self, image, coord):
        self.image = image
        self.pos = coord

    def getInfo(self):
        return [self.image, self.pos]


class Piece:
    def __init__(self, pieceinfo, chess_coord):
        piece = pieceinfo[0]
        color = pieceinfo[1]
        if piece == 'K':
            index = 0
        elif piece == 'Q':
            index = 1
        elif piece == 'B':
            index = 2
        elif piece == 'N':
            index = 3
        elif piece == 'R':
            index = 4
        elif piece == 'P':
            index = 5
        else:
            index = -1
        left_x = square_width * index
        if color == 'w':
            left_y = 0
        else:
            left_y = square_height

        self.pieceinfo = pieceinfo
        # subsection defines the part of the sprite image that represents our
        # piece:
        self.subsection = (left_x, left_y, square_width, square_height)
        # There are two ways that the position of a piece is defined on the
        # board. The default one used is the chess_coord, which stores something
        # like (3,2). It represents the chess coordinate where our piece image should
        # be blitted. On the other hand, is pos does not hold the default value
        # of (-1,-1), it will hold pixel coordinates such as (420,360) that represents
        # the location in the window that the piece should be blitted on. This is
        # useful for example if our piece is transitioning from a square to another:
        self.chess_coord = chess_coord
        self.pos = (-1, -1)

    # The methods are self explanatory:
    def getInfo(self):
        return [self.chess_coord, self.subsection, self.pos]

    def setpos(self, pos):
        self.pos = pos

    def getpos(self):
        return self.pos

    def setcoord(self, coord):
        self.chess_coord = coord

    def __repr__(self):
        # useful for debugging
        return self.pieceinfo + '(' + str(self.chess_coord[0]) + ',' + str(self.chess_coord[1]) + ')'


##############################////////GUI FUNCTIONS\\\\\\\\\\\\\#############################
def chess_coord_to_pixels(chess_coord):
    x, y = chess_coord
    # There are two sets of coordinates that this function could choose to return.
    # One is the coordinates that would be usually returned, the other is one that
    # would be returned if the board were to be flipped.
    # Note that square width and height variables are defined in the main function and
    # so are accessible here as global variables.
    if isAI:
        if AIPlayer == 0:
            # This means you're playing against the AI and are playing as black:
            return ((7 - x) * square_width, (7 - y) * square_height)
        else:
            return (x * square_width, y * square_height)
    # Being here means two player game is being played.
    # If the flipping mode is enabled, and the player to play is black,
    # the board should flip, but not until the transition animation for
    # white movement is complete:
    if not isFlip or player == 0 ^ isTransition:
        return (x * square_width, y * square_height)
    else:
        return ((7 - x) * square_width, (7 - y) * square_height)


def pixel_coord_to_chess(pixel_coord):
    x, y = pixel_coord[0] // square_width, pixel_coord[1] // square_height
    # See comments for chess_coord_to_pixels() for an explanation of the
    # conditions seen here:
    if isAI:
        if AIPlayer == 0:
            return (7 - x, 7 - y)
        else:
            return (x, y)
    if not isFlip or player == 0 ^ isTransition:
        return (x, y)
    else:
        return (7 - x, 7 - y)


def getPiece(chess_coord, listofWhitePieces, listofBlackPieces):
    for piece in listofWhitePieces + listofBlackPieces:
        # piece.getInfo()[0] represents the chess coordinate occupied
        # by piece.
        if piece.getInfo()[0] == chess_coord:
            return piece


def createPieces(board):
    # Initialize containers:
    listofWhitePieces = []
    listofBlackPieces = []
    # Loop through all squares:
    for i in range(8):
        for k in range(8):
            if board[i][k] != 0:
                # The square is not empty, create a piece object:
                p = Piece(board[i][k], (k, i))
                # Append the reference to the object to the appropriate
                # list:
                if board[i][k][1] == 'w':
                    listofWhitePieces.append(p)
                else:
                    listofBlackPieces.append(p)
    # Return both:
    return [listofWhitePieces, listofBlackPieces]


def createShades(listofTuples, winner, position):
    global listofShades
    # Empty the list
    listofShades = []
    if isTransition:
        # Nothing should be shaded when a piece is being animated:
        return
    if isDraw:
        # The game ended with a draw. Make yellow circle shades for
        # both the kings to show this is the case:
        coord = lookfor(board, 'Kw')[0]
        shade = Shades(circle_image_yellow, coord)
        listofShades.append(shade)
        coord = lookfor(board, 'Kb')[0]
        shade = Shades(circle_image_yellow, coord)
        listofShades.append(shade)
        # There is no need to go further:
        return
    if chessEnded:
        # The game has ended, with a checkmate because it cannot be a
        # draw if the code reached here.
        # Give the winning king a green circle shade:
        coord = lookfor(board, 'K' + winner)[0]
        shade = Shades(circle_image_green_big, coord)
        listofShades.append(shade)
    # If either king is under attack, give them a red circle:
    if isCheck(position, 'white'):
        coord = lookfor(board, 'Kw')[0]
        shade = Shades(circle_image_red, coord)
        listofShades.append(shade)
    if isCheck(position, 'black'):
        coord = lookfor(board, 'Kb')[0]
        shade = Shades(circle_image_red, coord)
        listofShades.append(shade)
    # Go through all the target squares inputted:
    for pos in listofTuples:
        # If the target square is occupied, it can be captured.
        # For a capturable square, there is a different shade.
        # Create the appropriate shade for each target square:
        if isOccupied(board, pos[0], pos[1]):
            img = circle_image_capture
        else:
            img = circle_image_green
        shade = Shades(img, pos)
        # Append:
        listofShades.append(shade)


def drawBoard(listofWhitePieces, listofBlackPieces):
    # Blit the background:
    screen.blit(background, (0, 0))
    # Choose the order in which to blit the pieces.
    # If black is about to play for example, white pieces
    # should be blitted first, so that when black is capturing,
    # the piece appears above:
    if player == 1:
        order = [listofWhitePieces, listofBlackPieces]
    else:
        order = [listofBlackPieces, listofWhitePieces]
    if isTransition:
        # If a piece is being animated, the player info is changed despite
        # white still capturing over black, for example. Reverse the order:
        order = list(reversed(order))
    # The shades which appear during the following three conditions need to be
    # blitted first to appear under the pieces:
    if isDraw or chessEnded or isAIThink:
        # Shades
        for shade in listofShades:
            img, chess_coord = shade.getInfo()
            pixel_coord = chess_coord_to_pixels(chess_coord)
            screen.blit(img, pixel_coord)
    # Make shades to show what the previous move played was:
    if prevMove[0] != -1 and not isTransition:
        x, y, x2, y2 = prevMove
        screen.blit(yellowbox_image, chess_coord_to_pixels((x, y)))
        screen.blit(yellowbox_image, chess_coord_to_pixels((x2, y2)))

    # Blit the Pieces:
    # Notw that one side has to be below the green circular shades to show
    # that they are being targeted, and the other side if dragged to such
    # a square should be blitted on top to show that it is capturing:

    # Potentially captured pieces:
    for piece in order[0]:

        chess_coord, subsection, pos = piece.getInfo()
        pixel_coord = chess_coord_to_pixels(chess_coord)
        if pos == (-1, -1):
            # Blit to default square:
            screen.blit(pieces_image, pixel_coord, subsection)
        else:
            # Blit to the specific coordinates:
            screen.blit(pieces_image, pos, subsection)
    # Blit the shades in between:
    if not (isDraw or chessEnded or isAIThink):
        for shade in listofShades:
            img, chess_coord = shade.getInfo()
            pixel_coord = chess_coord_to_pixels(chess_coord)
            screen.blit(img, pixel_coord)
    # Potentially capturing pieces:
    for piece in order[1]:
        chess_coord, subsection, pos = piece.getInfo()
        pixel_coord = chess_coord_to_pixels(chess_coord)
        if pos == (-1, -1):
            # Default square
            screen.blit(pieces_image, pixel_coord, subsection)
        else:
            # Specifc pixels:
            screen.blit(pieces_image, pos, subsection)
