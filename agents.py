import random
from collections import defaultdict
from game import GameState

class Agent:
    
    def __init__(self):
        pass
    
    def play(self, game_state):
        pass
    
    def evaluate(self, score):
        pass
    
    def _score_guess(self, guess, truth):
        correct = [2*(g==t) for g,t in zip(guess, truth)]  # cast as int
        remains = [t for t,c in zip(truth, correct) if not c]
        for i, (g,c) in enumerate(zip(guess, correct)):
            if not c and g in remains:
                correct[i] = 1
                remains.remove(g)
        return tuple(correct)

class Basic(Agent):
    
    def __init__(self, verbose=True):
        self.candidates = GameState.solutions
        self.verbose = verbose
    
    def play(self, game_state):
        self.candidates = game_state.candidates
        if self.verbose:
            print(f'Player: {len(self.candidates)} candidate(s) to choose from')
        return random.choice(self.candidates)

class Shallow(Agent):
    """Strategy: choose the guess that gives the widest / most evenly distributed tree against the field of 
    solutions consistent with the reported score
    
    Notes:
    * method 1 (score sorted first by fewest branches, then by largest branch) performs better than 
      method 0 (score sorted first by largest branch, then by fewest branches)
    """
    
    CACHED_RESULTS = {}
    
    def __init__(self, verbose=True, method=1):
        self.candidates = GameState.solutions
        self.move_candidates = GameState.allowed
        self.verbose = verbose
        self.method = method
        
    def _test_guess_vs_candidates(self, guess):
        tree = defaultdict(list)
        for word in self.candidates:
            tree[self._score_guess(guess, word)].append(word)
        return tree
    
    def _score_tree(self, tree):
        nbranches = len(tree)
        largest_branch = max(len(val) for val in tree.values())
        if self.method == 0:
            return (largest_branch, -nbranches)
        elif self.method == 1:
            return (-nbranches, largest_branch)
        else:
            raise ValueError('method needs to be 0 or 1')
    
    def _update_move_candidates(self):
        letters = set("".join(self.candidates))
        self.move_candidates = [word for word in self.move_candidates if set(word) & letters]
    
    def best_guess(self, guess_candidates, verbose=True, text=''):
        best_score = (len(self.candidates), 0) if self.method == 0 else (0, len(self.candidates))
        best_guess = None
        for guess in guess_candidates:
            tree = self._test_guess_vs_candidates(guess)
            score = self._score_tree(tree)
            if score[self.method] == 1:
                # solved!
                if verbose:
                    print(f'{text} Solved with {guess}')
                return guess, score, True
            if score < best_score:
                best_score = score
                best_guess = guess
        if verbose:
            print(f'{text} Not solved: Best guess = {best_guess}, score ={best_score}')
        return best_guess, best_score, False
    
    def play(self, game_state):
        # update candidates
        self.candidates = game_state.candidates
        self._update_move_candidates()
        key = tuple(self.candidates)
        if key in Shallow.CACHED_RESULTS:
            # this has been done before!
            if self.verbose:
                print("we've seen this before ...")
            return Shallow.CACHED_RESULTS[key]
        # candidates:
        guess, score, solved = self.best_guess(self.candidates, verbose=self.verbose, text='(soln)')
        if solved:
            Shallow.CACHED_RESULTS[key] = guess
            return guess
        # additional candidates
        guess2, score2, solved = self.best_guess(self.move_candidates, verbose=self.verbose, text='(extra)')
        if solved:
            Shallow.CACHED_RESULTS[key] = guess2
            return guess2
        Shallow.CACHED_RESULTS[key] = guess if score <= score2 else guess2
        return Shallow.CACHED_RESULTS[key]