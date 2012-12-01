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

class Save(Entity):
	template={
		'name':'',
		'card':None
	}