from cmd import Cmd
from entities import Save, Card, Species, Pokemon
from pydatastore.datastore import Query
from random import seed,choice;seed()

class CreateGame(Cmd):
	""" Command interface for creating new game-saves. """
	intro = 'Welcome to pygame.CreateGame shell'
	prompt = 'Create Game>'
	game_save = None

	def __init__(self,*args,**kwargs):
		Cmd.__init__(self,*args,**kwargs)
		self.game_save = Save()

	def do_name(self,name):
		""" Set's the new save's name.
		 eg: name My new save """
		name = name.strip()
		if len(name)<1:
			print("Enter a name longer than 0 characters, please.")
		found,n=False,name.lower()
		for save in Query(Save,lambda s:s.name.lower()==n):
			found=True
			break
		if found: print("There's already a save with that name!")
		else:self.game_save.update({"name":name})

	def do_done(self,*args):
		""" Stores the new save. Complains if the name isn't set."""
		assert self.game_save is not None
		if self.game_save.name is not None:
			if len(self.game_save.name)<1:
				print("You need to enter a save-name!")
			else:
				self.game_save.save()
				return True

	def do_cancel(self,*args):
		""" Deletes the new save, and exits. """
		assert self.game_save is not None
		self.game_save.delete()

class PlayGame(Cmd):
	intro = 'Welcome to pygame.PlayGame shell.'
	prompt = 'Play>'
	@classmethod
	def random_card(self):
		r = Card()
		#Get a random species.
		#This should probably be a lot simpler.
		#I'll fix that when I update pydatastore, later.
		def create_pokemon(species=None,level=5):
			if species is None:
				species = Species.load(choice(list(Species.keys())))
			pk = Pokemon()
			pk.update({"species":species.key,level:5})
			print("New pokemon generated!")
			pk.save()
			return pk
		r.party.append(create_pokemon().key)
		r.save()
		return r
	def __init__(self,save,*args,**kwargs):
		Cmd.__init__(self,*args,**kwargs)
		self.save = save
		if self.save.card is None:
			self.save.update({"card":self.random_card().key})
			self.save.save()
	def do_travel(self,location):
	"""Set's the current-save's location to the given location."""

class Game(Cmd):
	intro = 'Welcome to pygame.Game shell.'
	prompt = 'Game>'
	loaded_game = None

	def do_quit(self,*a):return True

	def do_load(self,save):
		""" Loads a saved game, if it exists.
		  Otherwise, complains loudly.
		"""
		n = save.lower()
		self.loaded_game = Query(Save,lambda s:s.name.lower()==n).fetch_one()
		if self.loaded_game is None:
			print("Couldn't find a save named '"+save+"'")

	def do_new(self,*args):
		""" Creates a new save-game and loads it.
		  The new-game shell is ran, and when it dies,
		  it's save is loaded. """
		cg = CreateGame()
		cg.cmdloop()
		self.loaded_game = cg.game_save

	def do_play(self,*args):
		""" Launches the currently loaded game.
		  If no game is loaded, complains loudly.
		  The game-play interface is found in the
		  PlayGame class."""
		if self.loaded_game is not None:
			PlayGame(self.loaded_game).cmdloop()
		else:
			print("You need to load or create a game before playing it.")

if __name__=="__main__":Game().cmdloop()