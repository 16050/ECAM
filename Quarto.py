#!/usr/bin/env python3
# Quarto.py
# Authors: El Haddadi Yassine & El Bakkoury Yassine
# Version: Mai, 2018

import argparse
import socket
import sys
import random
import json
import copy

from lib import game

class QuartoState(game.GameState):
    '''Class representing a state for the Quarto game.'''
    def __init__(self, initialstate=None, currentPlayer=None):
        self.__player = 0
        random.seed()
        if initialstate is None:
            pieces = []
            for shape in ['round', 'square']:
                for color in ['dark', 'light']:
                    for height in ['low', 'high']:
                        for filling in ['empty', 'full']:
                            pieces.append({
                                'shape': shape,
                                'color': color,
                                'height': height,
                                'filling': filling
                            })
            initialstate = {
                'board': [None] * 16,
                'remainingPieces': pieces,
                'pieceToPlay': None,
                'quartoAnnounced': True
            }
        if currentPlayer is None:
            currentPlayer = random.randrange(2)

        super().__init__(initialstate, currentPlayer=currentPlayer)

    def applymove(self, move):
        #{pos: 8, quarto: true, nextPiece: 2}
        stateBackup = copy.deepcopy(self._state)
        try:
            state = self._state['visible']
            if state['pieceToPlay'] is not None:
                try:
                    if state['board'][move['pos']] is not None:
                        raise game.InvalidMoveException('The position is not free')
                    state['board'][move['pos']] = state['remainingPieces'][state['pieceToPlay']]
                    del(state['remainingPieces'][state['pieceToPlay']])
                except game.InvalidMoveException as e:
                    raise e
                except:
                    raise game.InvalidMoveException("Your move should contain a \"pos\" key in range(16)")

            if len(state['remainingPieces']) > 0:
                try:
                    state['pieceToPlay'] = move['nextPiece']
                except:
                    raise game.InvalidMoveException("You must specify the next piece to play")
            else:
                state['pieceToPlay'] = None

            if 'quarto' in move:
                state['quartoAnnounced'] = move['quarto']
                winner = self.winner()
                if winner is None or winner == -1:
                    raise game.InvalidMoveException("There is no Quarto !")
            else:
                state['quartoAnnounced'] = False
        except game.InvalidMoveException as e:
            self._state = stateBackup
            raise e

    
    def _same(self, feature, elems):
        
        try:
            elems = list(map(lambda piece: piece[feature], elems))
        except:
            return False
        return all(e == elems[0] for e in elems)

    def _quarto(self, elems):
        return self._same('shape', elems) or self._same('color', elems) or self._same('filling', elems) or self._same('height', elems)
    
    def winner(self):
        state = self._state['visible']
        board = state['board']
        player = self._state['currentPlayer']

        # 00 01 02 03
        # 04 05 06 07
        # 08 09 10 11
        # 12 13 14 15

        if state['quartoAnnounced']:
            # Check horizontal and vertical lines
            for i in range(4):
                if self._quarto([board[4 * i + e] for e in range(4)]):
                    return player
                if self._quarto([board[4 * e + i] for e in range(4)]):
                    return player
            # Check diagonals
            if self._quarto([board[5 * e] for e in range(4)]):
                return player
            if self._quarto([board[3 + 3 * e] for e in range(4)]):
                return player
        return None if board.count(None) == 0 else -1
    
    def displayPiece(self, piece):
        if piece is None:
            return " " * 6
        bracket = ('(', ')') if piece['shape'] == "round" else ('[', ']')
        filling = 'E' if piece['filling'] == 'empty' else 'F'
        color = 'L' if piece['color'] == 'light' else 'D'
        format = ' {}{}{}{} ' if piece['height'] == 'low' else '{0}{0}{1}{2}{3}{3}'
        return format.format(bracket[0], filling, color, bracket[1])

    def prettyprint(self):
        state = self._state['visible']

        print('Board:')
        for row in range(4):
            print('|', end="")
            for col in range(4):
                print(self.displayPiece(state['board'][row*4+col]), end="|")
            print()
        
        print('\nRemaining Pieces:')
        print(", ".join([self.displayPiece(piece) for piece in state['remainingPieces']]))

        if state['pieceToPlay'] is not None:
            print('\nPiece to Play:')
            print(self.displayPiece(state['remainingPieces'][state['pieceToPlay']]))


    def nextPlayer(self):
        self._state['currentPlayer'] = (self._state['currentPlayer'] + 1) % 2


class QuartoServer(game.GameServer):
    '''Class representing a server for the Quarto game.'''
    def __init__(self, verbose=False):
        super().__init__('Quarto', 2, QuartoState(), verbose=verbose)
    
    def applymove(self, move):
        try:
            move = json.loads(move)
        except:
            raise game.InvalidMoveException('A valid move must be a valid JSON string')
        else:
            self._state.applymove(move)


class QuartoClient(game.GameClient):
    '''Class representing a client for the Quarto game.'''
    def __init__(self, name, server, verbose=False):
        super().__init__(server, QuartoState, verbose=verbose)
        self.__name = name
    
    def _handle(self, message):
        pass

    def _nextmove(self, state):
        visible = state._state['visible']
        move = {}

        #Ajoute une première clé dans move.
        if visible['pieceToPlay'] is not None:
            move['pos'] = visible['board'].index(None)
       
        #Sélecte les pièces de manière aléatoire.
        move['nextPiece'] = random.randint(0,(len(visible['remainingPieces'])-2))

        if (len(visible['remainingPieces']) == 16):
            move['nextPiece'] = random.randint(0,(len(visible['remainingPieces'])-2))
            self.E=0
            self.F=0
            self.L=0
            self.D=0
            self.Grand=0
            self.Petit=0
            self.Rond=0
            self.Carré=0
            if 'empty' in visible['remainingPieces'][move['nextPiece']]:
                self.E+=1
            if "empty" not in visible['remainingPieces'][move['nextPiece']]:
                self.F+=1
            if "light" in visible['remainingPieces'][move['nextPiece']]:
                self.L+=1
            if "light" not in visible['remainingPieces'][move['nextPiece']]:
                self.D+=1
            if ("high") in visible['remainingPieces'][move['nextPiece']]:
                self.Grand+=1
            if ("high") not in visible['remainingPieces'][move['nextPiece']]:
                self.Petit+=1
            if "round" in visible['remainingPieces'][move['nextPiece']]:
                self.Rond+=1
            if "round" not in visible['remainingPieces'][move['nextPiece']]:
                self.Carré+=1
            self.liste=[self.E,self.F,self.L,self.D,self.Grand,self.Petit,self.Rond,self.Carré]
            m=min(self.liste)
            self.indice=self.liste.index(m)
        if (len(visible['remainingPieces'])) < 16 and (len(visible['remainingPieces'])) != 1:
            if self.indice==0:
                rejet= 'empty'
            if self.indice==1:
                rejet= "full"
            if self.indice==2:
                rejet= "light"
            if self.indice==3:
                rejet= "dark"
            if self.indice==4:
                rejet= "high"
            if self.indice==5:
                rejet= 'low'
            if self.indice==6:
                rejet= 'round'
            if self.indice==7:
                rejet== 'square'   
            a=0
            while a < (len(visible['remainingPieces'])-1):
                move['nextPiece']= a
                try:
                    while rejet not in visible['remainingPieces'][move['nextPiece']]:
                        a=a+1
                        move['nextPiece']= a
                    
                except:
                    move['nextPiece']= random.randint(0,(len(visible['remainingPieces'])-2))
                    a=a+1
            if "empty" in visible['remainingPieces'][move['nextPiece']]:
                self.E+=1
            if "empty" not in visible['remainingPieces'][move['nextPiece']]:
                self.F+=1
            if "light" in visible['remainingPieces'][move['nextPiece']]:
                self.L+=1
            if "light" not in visible['remainingPieces'][move['nextPiece']]:
                self.D+=1
            if "high" in visible['remainingPieces'][move['nextPiece']]:
                self.Grand+=1
            if "high" not in visible['remainingPieces'][move['nextPiece']]:
                self.Petit+=1
            if "round" in visible['remainingPieces'][move['nextPiece']]:
                self.Rond+=1
            if "round" not in visible['remainingPieces'][move['nextPiece']]:
                self.Carré+=1
            self.liste=[self.E,self.F,self.L,self.D,self.Grand,self.Petit,self.Rond,self.Carré]
            m=min(self.liste)
            self.indice=self.liste.index(m)
  
        if (len(visible['remainingPieces']))==1:
            move['nextPiece']= 0

        
        if visible['pieceToPlay'] is not None:
            #Permet à chaque tour de vérifier que les 16 positions ne comportent
            #pas un Quarto avec la pièce reçue. Si y a, coupe avec return ;
            #sinon continue le programme sans conséquence avec Quarto false.
            i=0
            while i < 16:
                #Try-except permet d'éviter qu'une case déjà pleine ne soit chosie.
                try:
                    move['pos'] = i
                except:
                    pass
                #Si possibilité de faire un Quarto, pose la pièce.
                move['quarto'] = True
                try:
                    state.applymove(move)
                    return json.dumps(move)
                except: 
                    del(move['quarto'])
                    
                i=i+1

            #Permet d'éviter qu'un Quarto True ne se glisse après le while.
            try: 
                if move['quarto'] is True:
                    del(move['quarto'])
            except:
                pass

            #Si aucun Quarto n'a été trouvé avant, trouve une position libre au hasard.
            move['pos'] = random.randint(0,15)
            while visible['board'][move['pos']] is not None:
                move['pos'] = random.randint(0,15)
        #Renvoit le mouvement.
        return json.dumps(move)


if __name__ == '__main__':
    # Create the top-level parser
    parser = argparse.ArgumentParser(description='Quarto game')
    subparsers = parser.add_subparsers(description='server client', help='Quarto game components', dest='component')
    # Create the parser for the 'server' subcommand
    server_parser = subparsers.add_parser('server', help='launch a server')
    server_parser.add_argument('--host', help='hostname (default: localhost)', default='localhost')
    server_parser.add_argument('--port', help='port to listen on (default: 5000)', default=5000)
    server_parser.add_argument('--verbose', action='store_true')
    # Create the parser for the 'client' subcommand
    client_parser = subparsers.add_parser('client', help='launch a client')
    client_parser.add_argument('name', help='name of the player')
    client_parser.add_argument('--host', help='hostname of the server (default: localhost)', default='127.0.0.1')
    client_parser.add_argument('--port', help='port of the server (default: 5000)', default=5000)
    client_parser.add_argument('--verbose', action='store_true')
    # Parse the arguments of sys.args
    args = parser.parse_args()
    if args.component == 'server':
        QuartoServer(verbose=args.verbose).run()
    else:
        QuartoClient(args.name, (args.host, args.port), verbose=args.verbose)
