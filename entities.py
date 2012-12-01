from pydatastore.datastore import Entity

class Locale(Entity):
	template={
		'abbreviation':'',
		'name':''
	}

class LocaleString(Entity):
	default = 'en'
	template={}#language_abbreviation:key
	def __call__(self,lang=None):
		return self.dat.get(lang or self.default,"[UNKNOWN LANGUAGE]")

class EvolutionCondition(Entity):
	template={
		'type':'level',
		'value':0
	}

class Evolution(Entity):
	template={
		'to':None,
		'condition':None
	}
	foreign={
		'condition':EvolutionCondition.Reference()
	}

class Species(Entity):
	template={
		'pokedex':None,
		'name':None,
		'id':0,
		'evolutions':[],
		'base':{},#Base stats.
		'catch_rate':45,
		'happiness':70,
		'baby':False,
		'slug':''
	}
	foreign={
		'evolutions':Evolution.List(),
		'name':LocaleString.Reference()
	}

Evolution.foreign['to'] = Species.Reference()

class Pokemon(Entity):
	template={
		'species':None,
		'name':None,
		'nature':None,
		'ev':{},
		'level':0,#Lol, why was this a dict
		'stats':{}#What they currently are.
	}
	foreign={
		'species':Species.Reference()
	}

class Card(Entity):
	template={
		'class':None,
		'gender':'m',
		'party':[],
		'storage':[],
		'locale':None
	}
	foreign={
		'locale':Locale.Reference()
	}

class Map(Entity):
	template={
		'events':[],#Static events.
		'class_pool':[],#A pool of trainer-class's to generate.
		'tileset':None,#We'll get to that later, maybe.
		'tiles':[],#[z][x,y] = (tile)
		'width':1
	}
	@property
	def height(self):return max(len(l) for l in self.tiles)

class Town(Entity):
	template={
		'name':'',
		'outside':None,
		'inner':[]
	}
	foreign={
		'outside':Map.Reference(),
		'inner':Map.List()
	}

class Connection(Entity):
	template={
		'a':None,
		'b':None,
		'type':'north',#north|south|east|west|dive|emerge
		'offset':0#uses a as a base-point.
	}
	foreign={
		'a':Map.Reference(),
		'b':Map.Reference()
	}

class Save(Entity):
	template={
		'name':'',
		'card':None,
		'location':None,
		'position':[0,0]
	},
	foreign={
		'location':Map.Reference()
	}