from cmd import Cmd
from entities import Save, Card, Species, Pokemon, Map, Town
from pydatastore.datastore import Query
from random import seed,choice,randrange,randint;seed()

def random_pokemon(species=None,level=5):
	if species is None:
		species = Species.load(choice(list(Species.keys())))
	pk = Pokemon()
	pk.update({"species":species.key,level:5})
	pk.save()
	return pk

def random_card(e=None):
	ret,i = Card(),0
	class_pool = ["Ace","Cool","Beauty","Veteran","Bug"]
	if e is None or e < 1:
		e = randint(1,6)
	while i<e:
		ret.party.append(random_pokemon().key)
		i+=1
	ret['class'] = choice(class_pool)
	ret.save()
	return ret

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
		else:self.game_save["name"]=name

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
		return True

class OverInstance:
	def __init__(self,location):
		assert location is not None
		self.location = location
		self.generated_events=[]
		for i in range(0,randrange(0,10)):#A maximum of 10 generated trainers.
			self.generated_events.append(random_card())
	@property
	def events(self):
		return self.location.events + self.generated_events
	def clear(self):
		for event in self.generated_events:
			event.delete()

class PlayGame(Cmd):
	intro = 'Welcome to pygame.PlayGame shell.'
	prompt = 'Play>'
	@classmethod
	def __init__(self,save,*args,**kwargs):
		Cmd.__init__(self,*args,**kwargs)
		self.save = save
		if self.save.card is None:
			self.save.update({"card":random_card(1).key})
			self.save.save()
		self.location = None
		if self.save.location:
			self.location = OverInstance(self.save.location)
	def do_travel(self,location):
		"""Set's the current-save's location to the given location.
		   can be a key or a location."""
		location=location.strip().lower()
		found=False
		for result in Query(Town,lambda t:t.name.lower()==location):
			self.save['location'] = result.outside.key
			self.save.save()
			found=True
			break
		if not found:
			for result in Query(Map,lambda m:m.key.lower()==location):
				self.save['location'] = result.key
				self.save.save()
				found=True
				break
		if found:print("You have successfully traveled to the given map.")
		else:print("We couldn't find a matching location. sorry.")
	def do_look(self,what):
		""" Reports information on the environment."""
		if self.location:
			for event in self.location.events:
				print("Trainer of class:",event['class'])
				for pokemon in event.party:
					print("\t+-",pokemon.species.name())
	def do_event(self,ind):
		""" Interacts with an event."""
		if self.location:
			ind = int(ind) if isinstance(ind,str) else ind
			event = self.location.events[ind]
			if isinstance(event,Card):
				print("Launching a battle!")

	def do_quit(self,blah):
		if self.location:
			self.location.clear()
		return True

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