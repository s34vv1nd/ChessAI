from parameters import *
from chessprocesssing import *
from gameposition import *


###########################////////AI RELATED FUNCTIONS\\\\\\\\\\############################

def negamax(position,depth,alpha,beta,colorsign,bestMoveReturn,root=True):
    #First check if the position is already stored in the opening database dictionary:
    if root:
        #Generate key from current position:
        key = pos2key(position)
        if key in openings:
            #Return the best move to be played:
            bestMoveReturn[:] = random.choice(openings[key])
            return
    #Access global variable that will store scores of positions already evaluated:
    global searched
    #If the depth is zero, we are at a leaf node (no more depth to be analysed):
    if depth==0:
        return colorsign*evaluate(position)
    #Generate all the moves that can be played:
    moves = allMoves(position, colorsign)
    #If there are no moves to be played, just evaluate the position and return it:
    if moves==[]:
        return colorsign*evaluate(position)
    #Initialize a best move for the root node:
    if root:
        bestMove = moves[0]
    #Initialize the best move's value:
    bestValue = -100000
    #Go through each move:
    for move in moves:
        #Make a clone of the current move and perform the move on it:
        newpos = position.clone()
        makemove(newpos,move[0][0],move[0][1],move[1][0],move[1][1])
        #Generate the key for the new resulting position:
        key = pos2key(newpos)
        #If this position was already searched before, retrieve its node value.
        #Otherwise, calculate its node value and store it in the dictionary:
        if key in searched:
            value = searched[key]
        else:
            value = -negamax(newpos,depth-1, -beta,-alpha,-colorsign,[],False)
            searched[key] = value
        #If this move is better than the best so far:
        if value>bestValue:
            #Store it
            bestValue = value
            #If we're at root node, store the move as the best move:
            if root:
                bestMove = move
        #Update the lower bound for this node:
        alpha = max(alpha,value)
        if alpha>=beta:
            #If our lower bound is higher than the upper bound for this node, there
            #is no need to look at further moves:
            break
    #If this is the root node, return the best move:
    if root:
        searched = {}
        bestMoveReturn[:] = bestMove
        return
    #Otherwise, return the bestValue (i.e. value for this node.)
    return bestValue
def evaluate(position):
    if isCheckmate(position,'white'):
        #Major advantage to black
        return -20000
    if isCheckmate(position,'black'):
        #Major advantage to white
        return 20000
    #Get the board:
    board = position.getboard()
    #Flatten the board to a 1D array for faster calculations:
    flatboard = [x for row in board for x in row]
    #Create a counter object to count number of each pieces:
    c = Counter(flatboard)
    Qw = c['Qw']
    Qb = c['Qb']
    Rw = c['Rw']
    Rb = c['Rb']
    Bw = c['Bw']
    Bb = c['Bb']
    Nw = c['Nw']
    Nb = c['Nb']
    Pw = c['Pw']
    Pb = c['Pb']
    #Note: The above choices to flatten the board and to use a library
    #to count pieces were attempts at making the AI more efficient.
    #Perhaps using a 1D board throughout the entire program is one way
    #to make the code more efficient.
    #Calculate amount of material on both sides and the number of moves
    #played so far in order to determine game phase:
    whiteMaterial = 9*Qw + 5*Rw + 3*Nw + 3*Bw + 1*Pw
    blackMaterial = 9*Qb + 5*Rb + 3*Nb + 3*Bb + 1*Pb
    numofmoves = len(position.gethistory())
    gamephase = 'opening'
    if numofmoves>40 or (whiteMaterial<14 and blackMaterial<14):
        gamephase = 'ending'
    #A note again: Determining game phase is again one the attempts
    #to make the AI smarter when analysing boards and has not been
    #implemented to its full potential.
    #Calculate number of doubled, blocked, and isolated pawns for
    #both sides:
    Dw = doubledPawns(board,'white')
    Db = doubledPawns(board,'black')
    Sw = blockedPawns(board,'white')
    Sb = blockedPawns(board,'black')
    Iw = isolatedPawns(board,'white')
    Ib = isolatedPawns(board,'black')
    #Evaluate position based on above data:
    evaluation1 = 900*(Qw - Qb) + 500*(Rw - Rb) +330*(Bw-Bb
                )+320*(Nw - Nb) +100*(Pw - Pb) +-30*(Dw-Db + Sw-Sb + Iw- Ib
                )
    #Evaluate position based on piece square tables:
    evaluation2 = pieceSquareTable(flatboard,gamephase)
    #Sum the evaluations:
    evaluation = evaluation1 + evaluation2
    #Return it:
    return evaluation
def pieceSquareTable(flatboard,gamephase):
    #Initialize score:
    score = 0
    #Go through each square:
    for i in range(64):
        if flatboard[i]==0:
            #Empty square
            continue
        #Get data:
        piece = flatboard[i][0]
        color = flatboard[i][1]
        sign = +1
        #Adjust index if black piece, since piece sqaure tables
        #were designed for white:
        if color=='b':
            i = int((7-i//8)*8 + i%8)
            sign = -1
        #Adjust score:
        if piece=='P':
            score += sign*pawn_table[i]
        elif piece=='N':
            score+= sign*knight_table[i]
        elif piece=='B':
            score+=sign*bishop_table[i]
        elif piece=='R':
            score+=sign*rook_table[i]
        elif piece=='Q':
            score+=sign*queen_table[i]
        elif piece=='K':
            #King has different table values based on phase
            #of the game:
            if gamephase=='opening':
                score+=sign*king_table[i]
            else:
                score+=sign*king_endgame_table[i]
    return score
def doubledPawns(board,color):
    color = color[0]
    #Get indices of pawns:
    listofpawns = lookfor(board,'P'+color)
    #Count the number of doubled pawns by counting occurences of
    #repeats in their x-coordinates:
    repeats = 0
    temp = []
    for pawnpos in listofpawns:
        if pawnpos[0] in temp:
            repeats = repeats + 1
        else:
            temp.append(pawnpos[0])
    return repeats
def blockedPawns(board,color):
    color = color[0]
    listofpawns = lookfor(board,'P'+color)
    blocked = 0
    #Self explanatory:
    for pawnpos in listofpawns:
        if ((color=='w' and isOccupiedby(board,pawnpos[0],pawnpos[1]-1,
                                       'black'))
            or (color=='b' and isOccupiedby(board,pawnpos[0],pawnpos[1]+1,
                                       'white'))):
            blocked = blocked + 1
    return blocked
def isolatedPawns(board,color):
    color = color[0]
    listofpawns = lookfor(board,'P'+color)
    #Get x coordinates of all the pawns:
    xlist = [x for (x,y) in listofpawns]
    isolated = 0
    for x in xlist:
        if x!=0 and x!=7:
            #For non-edge cases:
            if x-1 not in xlist and x+1 not in xlist:
                isolated+=1
        elif x==0 and 1 not in xlist:
            #Left edge:
            isolated+=1
        elif x==7 and 6 not in xlist:
            #Right edge:
            isolated+=1
    return isolated

