from random import random,seed;seed()
import math
from event import Event

class WeightedChance:
	frequency = 2 # how many attempts it should take for a success.
	def success(self,attempts):
		# how many more until there should be a success?
		remaining = self.frequency - attempts
		probability = 1 - (remaining/self.frequency)
		probability_failure = 1.0 / probability
		return random() >= probability_failure

class Species:
	curve = 'medium-fast'
	base_exp = 100
	base_stat = {
		'hp':10,
		'atk':10,
		'def':10,
		'spatk':10,
		'spdef':10
		'speed':10
	}
	def base_moves(self, level, nature):
		return []
	def required_exp(self, level):
		def erratic_curve(nl):
			if nl<50:
				return math.floor(((nl**3)*(100-nl))/50)
			elif nl<68:
				return math.floor(((nl**3)*(150-nl))/100)
			elif nl<98:
				return math.floor(((nl**3)*((1911-10*nl)/3.0))/500.0)
			return math.floor(((nl**3)*(160-nl))/100)
		def fast_curve(nl):
			#durp
			return math.floor(.8 * (nl**3))
		def med_fast_curve(nl):
			#durp
			return nl**3
		def med_slow_curve(nl):
			a,b,c,d=nl**3,nl**2,nl,140
			return math.floor(((6.0/5.0)*a)-(15*b)+(100*n)-d)
		def slow_curve(nl):
			#durp
			return math.floor(1.25*nl**3)
		def fluctuating_curve(nl):
			exp_requirement = 0
			if nl<15:
				exp_requirement = nl**3 * ((((nl+1)/3)+24)/50)
			elif nl<36:
				exp_requirement = nl**3 * ((nl+14)/50)
			else:
				exp_requirement = nl**3 * (((nl/2)+32)/50)
			return math.floor(exp_requirement)
		return {
			'erratic':erratic_curve,
			'fast':fast_curve,
			'medium-fast':med_fast_curve,
			'medium-slow':med_slow_curve,
			'slow':slow_curve,
			'fluctuating':fluctuating_curve
		}[self.curve](level)
	def progress_level(self, level, exp, exp_gained):
		if level==100:return level, exp+exp_gained
		while level<=100 and self.required(level+1)<=exp+exp_gained:
			level+=1
			yield level
		return range(0)

class Nature:
	increase = 'atk'
	decrease = 'atk'

class StatSet:
	default_ivs = {
		'hp':0,
		'atk':0,
		'def':0,
		'spatk':0,
		'spdef':0,
		'speed':0 }
	default_evs = {
		'hp':0,
		'atk':0,
		'def':0,
		'spatk':0,
		'spdef':0,
		'speed':0 }
	def __init__(self,ivs):
		self.iv = {stat:math.floor(random() * 31) for stat in self.default_ivs}
		self.iv.update(ivs)
		self.ev = dict(self.default_evs)
	def calculate(self,species,stat,level,nature):
		part_a =self.iv[stat] + (2*species.base_stat[stat]) + math.floor(self.ev[stat]/4)
		if stat=='hp':
			part_a += 100
			return math.floor((part_a * level)/100.0) + 10
		stat_weight = 1.0
		if nature.increase==stat: stat_weight += .1
		if nature.decrease==stat: stat_weight -= .1
		return math.floor((((part_a * level)/100.0) + 5)*stat_weight)

class Pokemon:
	is_traded = False
	is_wild = True
	status = None
	def __init__(self,species,nature,level,ivs=None):
		self.species = species
		self.stats = StatSet(ivs or {})
		self.level = level
		self.nature = nature
		self.moves = species.base_moves(level,nature)
		self.hp = self.stats.calculate(self.species,'hp',self.level,self.nature)
		self.pp = {move:(move.base_pp,move.base_pp) for move in self.moves}
		self.exp = self.species.base_exp(level)
		self.on_level_gain = Event()
		self.on_faint = Event()
	def get_stat(self,stat_name, level=None):
		return self.stats.calculate(self.species,stat_name,level or self.level,self.nature)
	def defeat_pokemon(self,pokemon):
		self.stats.award_evs(pokemon)
		exp_gain = self.calculate_exp(pokemon)
		for level in self.species.progress_level(self.level,self.exp,self.exp_gain):
			ol,self.level = self.level,level
			self.on_level_gain(self,ol)
	def calculate_exp(self,target,participated=True):
		# http://bulbapedia.bulbagarden.net/wiki/Experience#Gain_formula
		a = 1 if target.is_wild else 1.5
		b = target.species.base_exp
		L = target.level
		s = 1 if participated else 2
		L_ = self.level
		t = 1.5 if self.is_traded else 1
		e = 1.5 if 'exp_boost' in self.item.flags else 1
		p = 1 # YEAH IM NOT EVEN GONNA TOUCH ON THIS.
		first = (a * b * L) / ( 5 * s )
		second = (( 2*L + 10) ** 2.5) / (L + L_ + 10 ) ** 2.5
		third = t * e * p
		return ((first*second)+1)*third
	def receive_damage(self,damage):
		self.hp = max(0,self.hp-damage)
		if self.hp<1:
			self.set_status('fainted')
	def set_status(self,status):
		self.status=status
		if status=='fainted':
			self.on_faint()
	def heal(self,restore_amount):
		assert self.status!='fainted'
		self.hp += restore_amount
	def revive(self,restore_weight=.5):
		self.status = None
		self.heal(restore_weight*self.stats.calculate(self.species,'hp',self.level,self.nature))