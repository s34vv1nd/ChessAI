from AI import *
from GUI import *
from parameters import *

position = GamePosition(board, player, castling_rights, En_Passant_Target
                        , half_move_clock)

# Generate a list of pieces that should be drawn on the board:
listofWhitePieces, listofBlackPieces = createPieces(board)

#########MAIN FUNCTION####################################################
#########################INFINITE LOOP#####################################
# The program remains in this loop until the user quits the application
while not gameEnded:
    if isMenu:
        # Menu needs to be shown right now.
        # Blit the background:
        screen.blit(background, (0, 0))
        if isAI == -1:
            # The user has not selected between playing against the AI
            # or playing against a friend.
            # So allow them to choose between playing with a friend or the AI:
            screen.blit(withfriend_pic, (0, square_height * 2))
            screen.blit(withAI_pic, (square_width * 4, square_height * 2))
        elif isAI == True:
            # The user has selected to play against the AI.
            # Allow the user to play as white or black:
            screen.blit(playwhite_pic, (0, square_height * 2))
            screen.blit(playblack_pic, (square_width * 4, square_height * 2))
        elif isAI == False:
            # The user has selected to play with a friend.
            # Allow choice of flipping the board or not flipping the board:
            screen.blit(flipDisabled_pic, (0, square_height * 2))
            screen.blit(flipEnabled_pic, (square_width * 4, square_height * 2))
        if isFlip != -1:
            # All settings have already been specified.
            # Draw all the pieces onto the board:
            drawBoard(listofWhitePieces, listofBlackPieces)
            # Don't let the menu ever appear again:
            isMenu = False
            # In case the player chose to play against the AI and decided to
            # play as black, call upon the AI to make a move:
            if isAI and AIPlayer == 0:
                colorsign = 1
                bestMoveReturn = []
                move_thread = threading.Thread(target=negamax,
                                               args=(position, 3, -1000000, 1000000, colorsign, bestMoveReturn))
                move_thread.start()
                isAIThink = True
            continue
        for event in pygame.event.get():
            # Handle the events while in menu:
            if event.type == QUIT:
                # Window was closed.
                gameEnded = True
                break
            if event.type == MOUSEBUTTONUP:
                # The mouse was clicked somewhere.
                # Get the coordinates of click:
                pos = pygame.mouse.get_pos()
                # Determine if left box was clicked or right box.
                # Then choose an appropriate action based on current
                # state of menu:
                if (pos[0] < square_width * 4 and
                        pos[1] > square_height * 2 and
                        pos[1] < square_height * 6):
                    # LEFT SIDE CLICKED
                    if isAI == -1:
                        isAI = False
                    elif isAI == True:
                        AIPlayer = 1
                        isFlip = False
                    elif isAI == False:
                        isFlip = False
                elif (pos[0] > square_width * 4 and
                      pos[1] > square_height * 2 and
                      pos[1] < square_height * 6):
                    # RIGHT SIDE CLICKED
                    if isAI == -1:
                        isAI = True
                    elif isAI == True:
                        AIPlayer = 0
                        isFlip = False
                    elif isAI == False:
                        isFlip = True

        # Update the display:
        pygame.display.update()

        # Run at specific fps:
        clock.tick(60)
        continue
    # Menu part was done if this part reached.
    # If the AI is currently thinking the move to play
    # next, show some fancy looking squares to indicate
    # that.
    # Do it every 6 frames so it's not too fast:
    numm += 1
    if isAIThink and numm % 6 == 0:
        ax += 1
        if ax == 8:
            ay += 1
            ax = 0
        if ay == 8:
            ax, ay = 0, 0
        if ax % 4 == 0:
            createShades([], winner, position)
        # If the AI is white, start from the opposite side (since the board is flipped)
        if AIPlayer == 0:
            listofShades.append(Shades(greenbox_image, (7 - ax, 7 - ay)))
        else:
            listofShades.append(Shades(greenbox_image, (ax, ay)))

    for event in pygame.event.get():
        # Deal with all the user inputs:
        if event.type == QUIT:
            # Window was closed.
            gameEnded = True

            break
        # Under the following conditions, user input should be
        # completely ignored:
        if chessEnded or isTransition or isAIThink:
            continue
        # isDown means a piece is being dragged.
        if not isDown and event.type == MOUSEBUTTONDOWN:
            # Mouse was pressed down.
            # Get the oordinates of the mouse
            pos = pygame.mouse.get_pos()
            # convert to chess coordinates:
            chess_coord = pixel_coord_to_chess(pos)
            x = chess_coord[0]
            y = chess_coord[1]
            # If the piece clicked on is not occupied by your own piece,
            # ignore this mouse click:
            if not isOccupiedby(board, x, y, 'wb'[player]):
                continue
            # Now we're sure the user is holding their mouse on a
            # piecec that is theirs.
            # Get reference to the piece that should be dragged around or selected:
            dragPiece = getPiece(chess_coord, listofWhitePieces, listofBlackPieces)
            # Find the possible squares that this piece could attack:
            listofTuples = findPossibleSquares(position, x, y)
            # Highlight all such squares:
            createShades(listofTuples, winner, position)
            # A green box should appear on the square which was selected, unless
            # it's a king under check, in which case it shouldn't because the king
            # has a red color on it in that case.
            if ((dragPiece.pieceinfo[0] == 'K') and
                    (isCheck(position, 'white') or isCheck(position, 'black'))):
                None
            else:
                listofShades.append(Shades(greenbox_image, (x, y)))
            # A piece is being dragged:
            isDown = True
        if (isDown or isClicked) and event.type == MOUSEBUTTONUP:
            # Mouse was released.
            isDown = False
            # Snap the piece back to its coordinate position
            dragPiece.setpos((-1, -1))
            # Get coordinates and convert them:
            pos = pygame.mouse.get_pos()
            chess_coord = pixel_coord_to_chess(pos)
            x2 = chess_coord[0]
            y2 = chess_coord[1]
            # Initialize:
            isTransition = False
            if (x, y) == (x2, y2):  # NO dragging occured
                # (ie the mouse was held and released on the same square)
                if not isClicked:  # nothing had been clicked previously
                    # This is the first click
                    isClicked = True
                    prevPos = (x, y)  # Store it so next time we know the origin
                else:  # Something had been clicked previously
                    # Find out location of previous click:
                    x, y = prevPos
                    if (x, y) == (x2, y2):  # User clicked on the same square again.
                        # So
                        isClicked = False
                        # Destroy all shades:
                        createShades([], winner, position)
                    else:
                        # User clicked elsewhere on this second click:
                        if isOccupiedby(board, x2, y2, 'wb'[player]):
                            # User clicked on a square that is occupied by their
                            # own piece.
                            # This is like making a first click on your own piece:
                            isClicked = True
                            prevPos = (x2, y2)  # Store it
                        else:
                            # The user may or may not have clicked on a valid target square.
                            isClicked = False
                            # Destory all shades
                            createShades([], winner, position)
                            isTransition = True  # Possibly if the move was valid.

            if not (x2, y2) in listofTuples:
                # Move was invalid
                isTransition = False
                continue
            # Reaching here means a valid move was selected.
            # If the recording option was selected, store the move to the opening dictionary:
            if isRecord:
                key = pos2key(position)
                # Make sure it isn't already in there:
                if [(x, y), (x2, y2)] not in openings[key]:
                    openings[key].append([(x, y), (x2, y2)])

            # Make the move:
            makemove(position, x, y, x2, y2)
            # Update this move to be the 'previous' move (latest move in fact), so that
            # yellow shades can be shown on it.
            prevMove = [x, y, x2, y2]
            # Update which player is next to play:
            player = position.getplayer()
            # Add the new position to the history for it:
            position.addtoHistory(position)
            # Check for possibilty of draw:
            HMC = position.getHMC()
            if HMC >= 100 or isStalemate(position) or position.checkRepition():
                # There is a draw:
                isDraw = True
                chessEnded = True
            # Check for possibilty of checkmate:
            if isCheckmate(position, 'white'):
                winner = 'b'
                chessEnded = True
            if isCheckmate(position, 'black'):
                winner = 'w'
                chessEnded = True
            # If the AI option was selecteed and the game still hasn't finished,
            # let the AI start thinking about its next move:
            if isAI and not chessEnded:
                if player == 0:
                    colorsign = 1
                else:
                    colorsign = -1
                bestMoveReturn = []
                move_thread = threading.Thread(target=negamax,
                                               args=(position, 3, -1000000, 1000000, colorsign, bestMoveReturn))
                move_thread.start()
                isAIThink = True
            # Move the piece to its new destination:
            dragPiece.setcoord((x2, y2))
            # There may have been a capture, so the piece list should be regenerated.
            # However, if animation is ocurring, the the captured piece should still remain visible.
            if not isTransition:
                listofWhitePieces, listofBlackPieces = createPieces(board)
            else:
                movingPiece = dragPiece
                origin = chess_coord_to_pixels((x, y))
                destiny = chess_coord_to_pixels((x2, y2))
                movingPiece.setpos(origin)
                step = (destiny[0] - origin[0], destiny[1] - origin[1])

            # Either way shades should be deleted now:
            createShades([], winner, position)
    # If an animation is supposed to happen, make it happen:
    if isTransition:
        p, q = movingPiece.getpos()
        dx2, dy2 = destiny
        n = 30.0
        if abs(p - dx2) <= abs(step[0] / n) and abs(q - dy2) <= abs(step[1] / n):
            # The moving piece has reached its destination:
            # Snap it back to its grid position:
            movingPiece.setpos((-1, -1))
            # Generate new piece list in case one got captured:
            listofWhitePieces, listofBlackPieces = createPieces(board)
            # No more transitioning:
            isTransition = False
            createShades([], winner, position)
        else:
            # Move it closer to its destination.
            movingPiece.setpos((p + step[0] / n, q + step[1] / n))
    # If a piece is being dragged let the dragging piece follow the mouse:
    if isDown:
        m, k = pygame.mouse.get_pos()
        dragPiece.setpos((m - square_width / 2, k - square_height / 2))
    # If the AI is thinking, make sure to check if it isn't done thinking yet.
    # Also, if a piece is currently being animated don't ask the AI if it's
    # done thinking, in case it replied in the affirmative and starts moving
    # at the same time as your piece is moving:
    if isAIThink and not isTransition:
        if not move_thread.isAlive():
            # The AI has made a decision.
            # It's no longer thinking
            isAIThink = False
            # Destroy any shades:
            createShades([], winner, position)
            # Get the move proposed:
            [x, y], [x2, y2] = bestMoveReturn
            # Do everything just as if the user made a move by click-click movement:
            makemove(position, x, y, x2, y2)
            prevMove = [x, y, x2, y2]
            player = position.getplayer()
            HMC = position.getHMC()
            position.addtoHistory(position)
            if HMC >= 100 or isStalemate(position) or position.checkRepition():
                isDraw = True
                chessEnded = True
            if isCheckmate(position, 'white'):
                winner = 'b'
                chessEnded = True
            if isCheckmate(position, 'black'):
                winner = 'w'
                chessEnded = True
            # Animate the movement:
            isTransition = True
            movingPiece = getPiece((x, y), listofWhitePieces, listofBlackPieces)
            origin = chess_coord_to_pixels((x, y))
            destiny = chess_coord_to_pixels((x2, y2))
            movingPiece.setpos(origin)
            step = (destiny[0] - origin[0], destiny[1] - origin[1])

    # Update positions of all images:
    drawBoard(listofWhitePieces, listofBlackPieces)
    # Update the display:
    pygame.display.update()

    # Run at specific fps:
    clock.tick(60)

# Out of loop. Quit pygame:
pygame.quit()
# In case recording mode was on, save the openings dictionary to a file:
if isRecord:
    file_handle.seek(0)
    pickle.dump(openings, file_handle)
    file_handle.truncate()
    file_handle.close()
