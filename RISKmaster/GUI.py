#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-

import functools
import pygame
from pygame.locals import *
import Risk
import glob
import pickle 

PATH_IMG='Pictures/'
PATH_MAP='Pictures/Maps/'
PATH_BCK='Pictures/Backgrounds/'
PATH_DCE='Pictures/Dices/'
MAP_IMG='Risk_game_map_fixed_greylevel.png'
MAP_LVL='Risk_game_map_fixed_greylevel.png'
BCK_IMG='background5.jpg'
BAR_IMG='barre.png'
DHE_IMG='tete-de-mort.png'
POLICE_NAME='freesansbold.ttf'
POLICE_SIZE=16
DICE_SIZE=25
#f_w=1280
#f_h=800

#Ajuste tamaño pantalla

import ctypes

user32 = ctypes.windll.user32
user32.SetProcessDPIAware()
ancho, alto = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
f_w=ancho
f_h=alto

class ColorMap():
	def __init__(self):
		self.green=(0,255,0)
		self.red=(255,0,0)
		self.blue=(0,0,255)
		self.white=(255,255,255)
		self.black=(0,0,0)
		self.grey=(100,100,100)
		self.yellow=(255,255,0)
		self.purple=(255,0,255)
		self.cian=(0,255,255)
		self.dark_purple=(127,0,255)
		self.dark_green=(0,170,0)
		self.dark_red=(170,0,0)
		self.dark_blue=(0,0,170)
		self.fondo=(227,208,150)

#Poner en una clase
def text_objects(text, font,color=(0,0,0)):
	textSurface = font.render(text, True, color)
	return textSurface, textSurface.get_rect()

def button(msg,x,y,w,h,ic,ac,action=None):
	mouse = pygame.mouse.get_pos()
	click = pygame.mouse.get_pressed()
	if x+w > mouse[0] > x and y+h > mouse[1] > y:
		pygame.draw.rect(ventana, ac,(x,y,w,h))
		if click[0] == 1 and action != None:
			Win.fonctions.append(action)
	else:
		pygame.draw.rect(ventana, ic,(x,y,w,h))

	smallText = pygame.font.Font(POLICE_NAME,POLICE_SIZE)
	textSurf, textRect = text_objects(msg, smallText)
	textRect.center = ( (x+(w/2)), (y+(h/2)) )
	ventana.blit(textSurf, textRect)

def color_surface(surface,color):
	for x in range(0,surface.get_width()):
		for y in range(0,surface.get_height()):
			if surface.get_at((x,y))!=(0,0,0):
				surface.set_at((x,y),color)

#not used right now
def color_surface_map(surface,color,map_color):
	for x in range(0,surface.get_width()):
		for y in range(0,surface.get_height()):
			if surface.get_at((x,y))==map_color:
				surface.set_at((x,y),color)
#useless?
def colorize(image, newColor):
    # zero out RGB values
    image.fill((0, 0, 0, 255), None, pygame.BLEND_RGBA_MULT)
    # add in new RGB values
    image.fill(newColor[0:3] + (0,), None, pygame.BLEND_RGBA_ADD)

def color_surface(sprite,color,alpha):
	for x in range(0,sprite.bounds.width):
		for y in range(0,sprite.bounds.height):
			if sprite.map_pays.get_at((sprite.bounds.x+x,sprite.bounds.y+y))!=(0,0,0):
				sprite.map_pays.set_at((sprite.bounds.x+x,sprite.bounds.y+y),color)
				sprite.map_pays.set_alpha(alpha)

def add_text(layer,message,pos,font,color=(0,0,0)):
	textSurf, textRect = text_objects(message, font,color)
	textRect.topleft = pos
	layer.append([textSurf, textRect])

def display_tropas(textes,sprites,Map):
	smallText = pygame.font.Font(POLICE_NAME,POLICE_SIZE)
	for sprite in sprites:
		pays=Map.pays[sprite.id-1]
		textSurf, textRect = text_objects(str(pays.nb_tropas), smallText)
		textRect.center = sprite.bounds.center
		textes.append([textSurf, textRect])

def display_win(final_layer,players):
	bigText = pygame.font.Font(POLICE_NAME,42)
	marge=50
	pos=(200,200)
	for p in players:
		if p.obj.get_state()==True:
			p_win=p
			#Jugador gana
			textSurf, textRect = text_objects(p_win.name+' win', bigText,p_win.color)
			textRect.topleft = pos
			pos=(pos[0],pos[1]+marge)
			final_layer.append([textSurf, textRect])
			#Objetivo
			textSurf, textRect = text_objects('Objetivo '+p_win.obj.description, bigText,p_win.color)
			textRect.topleft = pos
			pos=(pos[0],pos[1]+marge)
			final_layer.append([textSurf, textRect])

def display_help(final_layer,colormap):
	bigText = pygame.font.Font(POLICE_NAME,42)
	marge=50
	pos=(200,200)
	add_text(final_layer,'ESC : Salir del juego',pos,bigText,colormap.white)
	pos=(pos[0],pos[1]+marge)
	add_text(final_layer,'n : Siguiente fase',pos,bigText,colormap.white)
	pos=(pos[0],pos[1]+marge)
	add_text(final_layer,'p : Turno del siguiente jugador',pos,bigText,colormap.white)
	pos=(pos[0],pos[1]+marge)
	add_text(final_layer,'h : Mostrar/Ocultar menú de ayuda',pos,bigText,colormap.white)
	pos=(pos[0],pos[1]+marge)
	add_text(final_layer,'d : Mostrar/Ocultar búsqueda',pos,bigText,colormap.white)
	pos=(pos[0],pos[1]+marge)
	add_text(final_layer,'u : Usar cartas',pos,bigText,colormap.white)

def display_hud(nb_units,t_hud,turns,pos,hide):
	smallText = pygame.font.Font(POLICE_NAME,POLICE_SIZE)
	marge=20
	col=[100,400,700,1000]
	row=pos[1]

	#JUGADOR
	textSurf, textRect = text_objects('Turno : '+str(turns.num), smallText)
	textRect.topleft = pos
	t_hud.append([textSurf, textRect])
	textSurf, textRect = text_objects('Jugador : ',smallText)
	pos=(pos[0],pos[1]+marge)
	textRect.topleft = pos
	t_hud.append([textSurf, textRect])
	textSurf, textRect = text_objects(turns.players[turns.player_turn-1].name, smallText,turns.players[turns.player_turn-1].color)
	textRect.topleft = (pos[0]+70,pos[1])#no limpio
	t_hud.append([textSurf, textRect])
	textSurf, textRect = text_objects('Fase : '+turns.list_phase[turns.phase], smallText)
	pos=(pos[0],pos[1]+marge)
	textRect.topleft = pos
	t_hud.append([textSurf, textRect])
	textSurf, textRect = text_objects('Soldados por turnos : '+str(turns.players[turns.player_turn-1].sbyturn), smallText)
	pos=(pos[0],pos[1]+marge)
	textRect.topleft = pos
	t_hud.append([textSurf, textRect])
	textSurf, textRect = text_objects('Soldados a desplegar : '+str(turns.players[turns.player_turn-1].nb_tropas), smallText)
	pos=(pos[0],pos[1]+marge)
	textRect.topleft = pos
	t_hud.append([textSurf, textRect])
	textSurf, textRect = text_objects('Soldados seleccionados : '+str(nb_units), smallText)
	pos=(pos[0],pos[1]+marge)
	textRect.topleft = pos
	t_hud.append([textSurf, textRect])

	#OBJETIVOS
	textSurf, textRect = text_objects('Objetivos ', smallText)
	pos=(col[1],row)
	textRect.topleft = pos
	t_hud.append([textSurf, textRect])
	if hide==False:
		try:
			textSurf, textRect = text_objects(str(turns.players[turns.player_turn-1].obj.description), smallText)
		except AttributeError as e:
			print (e.args)
		pos=(col[1],row+marge)
		textRect.topleft = pos
		t_hud.append([textSurf, textRect])
		try:
			textSurf, textRect = text_objects('Estado : '+str(turns.players[turns.player_turn-1].obj.get_state()), smallText)
		except AttributeError as e:
			print (e.args)
		pos=(col[1],row+2*marge)
		textRect.topleft = pos
		t_hud.append([textSurf, textRect])

	#CARTAS
	textSurf, textRect = text_objects('Cartas ', smallText)
	pos=(col[1],row+3*marge)
	textRect.topleft = pos
	t_hud.append([textSurf, textRect])
	if hide==False:
		textSurf, textRect = text_objects(str(turns.players[turns.player_turn-1].cards), smallText)
		pos=(col[1],row+4*marge)
		textRect.topleft = pos
		t_hud.append([textSurf, textRect])

	#BONUS CONTINENTES
	pos=(col[3],row)
	textSurf, textRect = text_objects('Bonus Continentes', smallText)
	textRect.topleft = pos
	t_hud.append([textSurf, textRect])
	for idx,c in enumerate(turns.map.continents):
		pos=(col[3],row+(idx+1)*marge)
		textSurf, textRect = text_objects(c.name+' '+str(c.bonus), smallText)
		textRect.topleft = pos
		t_hud.append([textSurf, textRect])

def display_continent(cont,temp_layer,sprites_pays_masque):
	for p in cont.pays:
		temp_layer.append(next((x.map_pays for x in sprites_pays_masque if x.id == p.id), None))

def save_game(obj_lst):
	# Guardar los objetos:
	with open('saved_game', 'wb') as f:
		pickle.dump(obj_lst, f)
		print('Juego guardado')

def restore_game(obj_lst):
	# Recuperando los objetos:
	with open('saved_game','rb') as f:
		obj_lst=pickle.load(f)
		print('Juego recuperado')

class GamePara():
	def __init__(self):
		self.nujugadores=0
		self.tour=0
		self.joueurs=[]

class SpritePays():
	def __init__(self,surface,name_id):
		self.map_pays=surface
		self.name_pays=''
		self.id=int(name_id[-6:-4])#no muy limpio
		self.bounds=surface.get_bounding_rect()

class CurrentWindow():
	def __init__(self,ventana,turns):
		self.ventana=ventana
		self.fonctions=[]	#lista de todas las funciones a ejecutar
		self.surfaces=[] #lista de todas las superficies para mostrar
		self.dices=[] #lista de todas las superficies de dados
		self.game=GamePara()
		self.turns=turns
		self.players=turns.players
		self.map=turns.map
		self.textes=[]#lista de textos de tropas para fusionarlos después de las superficies
		self.tmp=[]#lista de sprites temporales
		self.t_hud=[]#lista de textos de HUD
		self.final_layer=[]#última capa de visualización, utilizada para la pantalla ganadora y el menú de ayuda
		self._nb_units=25 #no limpio
		self.pays_select=None #pais seleccionado

	@property
	def nb_units(self):
		if self.turns.phase==0:#Reglas getter durante el despliegue de tropas
			return min(self._nb_units,self.players[self.turns.player_turn-1].nb_tropas)#le joueur ne peut pas selectionner plus de tropas qu'il n'en possede 
		else:
			return self._nb_units

	@nb_units.setter #Incompatible, como es python 2, necesita heredar de la clase de objeto
	def nb_units(self, value):
		if self.turns.phase==0:#Establecer reglas durante la fase de implementación
			if value<1:
				self._nb_units = 1
				raise ValueError('Muy pocas tropas',value)
			elif value>self.players[self.turns.player_turn-1].nb_tropas:
				self._nb_units = self.players[self.turns.player_turn-1].nb_tropas
				raise ValueError('Muchas tropas',value)
		else:#Establecer reglas durante otras fases
			if value<0:
				self._nb_units = 0
				raise ValueError('Muy pocas tropas',value)
			elif value>self.pays_select.nb_tropas-1:
				self._nb_units = self.pays_select.nb_tropas-1#solo puedes atacar / moverte con n-1 tropas
				raise ValueError('Muchas tropas',value)
		self._nb_units = value

	def color_players(self,sprites):
		for pl in self.players:
			for pays in pl.pays:
				#print(pl.id,pays,sprites[pays-1].name_pays)
				sprite=next((s for s in sprites if s.id == pays), None)
				color_surface(sprite,pl.color,255)
				#print(sprite.id,pays)

	def start_game(self):
		self.surfaces=[]
		#fond bleue
		# background = pygame.Surface(ventana.get_size())
		# background = background.convert()
		# background.fill(blue)
		#Fondo personalizado
		background=pygame.image.load(PATH_BCK+BCK_IMG).convert()
		coeff=f_w/background.get_width() #adapta la imagen de acuerdo al ancho
		w=int(coeff*background.get_width())
		h=int(coeff*background.get_height())
		background=pygame.transform.scale(background,(w,h))

		#map
		map_monde=pygame.image.load(PATH_IMG+MAP_IMG).convert_alpha()
		coeff=f_w/map_monde.get_width()#adapta la imagen de acuerdo al largo
		w=int(coeff*map_monde.get_width())
		h=int(coeff*map_monde.get_height())
		map_monde=pygame.transform.scale(map_monde,(w,h))

		#Barra de HUD
		barre=pygame.image.load(PATH_IMG+BAR_IMG).convert_alpha()
		barre=pygame.transform.scale(barre,(f_w,f_h-h))

		self.fonctions=[]
		self.surfaces.extend([[background,(0,0)],[barre,(0,h)],[map_monde,(0,0)]])

	def afficher(self,fonction=None):
		colormap=ColorMap()
		afficher=1
		select=False
		atck_winmove=False
		sprite_select=-1
		glob_pays=glob.glob(PATH_MAP+"*.png")
		sprites_pays=[]
		help_menu=False
		id_c=0
		hide=True
		#sprites de passage
		sprites_pays_masque=[]
		#cambiar los sprites del país
		for idx,fl in enumerate(glob_pays):
			s=pygame.image.load(fl).convert()
			coeff=f_w/s.get_width()
			s=pygame.transform.scale(s,(int(coeff*s.get_width()),int(coeff*s.get_height())))
			sp=SpritePays(s,fl)
			sp_masque=SpritePays(s.copy(),fl)
			color_surface(sp_masque,(1,1,1),150)
			sprites_pays.append(sp)
			sprites_pays_masque.append(sp_masque)

		#coloración de países según los colores del jugador
		self.color_players(sprites_pays)
		for idx, spr in enumerate(sprites_pays):#no super limpio
			if idx==0:
				merged_pays = spr.map_pays.copy()
			else:
				merged_pays.blit(spr.map_pays, (0, 0))

		#exhibición de tropas
		display_tropas(self.textes,sprites_pays,self.map)

		while afficher:
			for event in pygame.event.get():
				if event.type == QUIT:
					afficher=0
				elif event.type == KEYDOWN:
					if event.key == K_ESCAPE:
						afficher = 0
					elif event.key == K_n:
						try:
							self.turns.next()
						except ValueError as e:
							print(e.args)
						self.tmp=[]
						select=False
						sprite_select=0
					elif event.key == K_p:
						try:
							self.turns.next_player()
						except ValueError as e:
							print(e.args)
						self.tmp=[]
						select=False
						sprite_select=0
					elif event.key == K_w:#eliminar, depurar func
						self.turns.game_finish=True
					elif event.key == K_h:
						help_menu = not help_menu
					elif event.key == K_c:
						self.tmp=[]
						display_continent(self.turns.map.continents[id_c],self.tmp,sprites_pays_masque)
						id_c=(id_c+1)%len(self.turns.map.continents)
					elif event.key == K_u:#utilización de cartas
						self.turns.players[self.turns.player_turn-1].use_best_cards()
					elif event.key == K_d:#mostrar / ocultar objetivos del jugador
						hide = not hide
					elif event.key == K_s:#copia de seguridad
						save_game(self)
					elif event.key == K_r:#restauración
						restore_game(self.turns)
				elif event.type == MOUSEBUTTONDOWN:
					try:
						if event.button==3: #haga clic derecho para cancelar la selección
							self.tmp=[]
							select=False
							sprite_select=0
						elif event.button==4:#rueda de desplazamiento hacia arriba
							self.nb_units+=1
						elif event.button==5:#rueda de desplazamiento hacia abajo
							if self.nb_units>0:
								self.nb_units-=1
					except AttributeError as e:
						print('Debes seleccionar un Pais')
					except ValueError as e:
						print(e.args)

			for surface in self.surfaces:
				self.ventana.blit(surface[0],surface[1])
			for dice in self.dices:
				self.ventana.blit(dice[0],dice[1])
			#for sprite in sprites_pays:
			#	self.ventana.blit(sprite.map_pays,(0,0))
			self.ventana.blit(merged_pays,(0,0))
			for tmp in self.tmp:
				self.ventana.blit(tmp,(0,0))
			for texte in self.textes:
				self.ventana.blit(texte[0],texte[1])
			for t in self.t_hud:
				self.ventana.blit(t[0],t[1])
			for final in self.final_layer:
				self.ventana.blit(final[0],final[1])
			if self.fonctions != []:
				for f in self.fonctions:
					f()				#funciones de visualización

			#Pantalla de victoria cuando un jugador gana
			if self.turns.players[self.turns.player_turn-1].obj.get_state()==True: #no limpio
				self.final_layer=[]
				win_screen = pygame.Surface(self.ventana.get_size())
				win_screen = win_screen.convert()
				win_screen.fill(colormap.black)
				win_screen.set_alpha(180)
				self.final_layer.append([win_screen,(0,0)])
				display_win(self.final_layer,self.players)
			else:
				#pantalla de ayuda
				if help_menu:
					self.final_layer=[]
					win_screen = pygame.Surface(self.ventana.get_size())
					win_screen = win_screen.convert()
					win_screen.fill(colormap.black)
					win_screen.set_alpha(180)
					self.final_layer.append([win_screen,(0,0)])
					display_help(self.final_layer,colormap)
				else:
					self.final_layer=[]

			#pygame.display.flip()
			mouse = pygame.mouse.get_pos()
			#print(self.ventana.get_at((mouse[0], mouse[1])))
			#bucle de vuelo del país
			#for idx,sprite in enumerate(sprites_pays):
				#if sprite.bounds.x<mouse[0]<sprite.bounds.x+sprite.bounds.width and sprite.bounds.y<mouse[1]<sprite.bounds.y+sprite.bounds.height: 
			try:
				mouse_color=self.surfaces[2][0].get_at((mouse[0],mouse[1]))
			except IndexError as e:
				pass #pas propre
				#print(e.args)

			try:
				if mouse_color != (0,0,0,0) and mouse_color != (0,0,0,255):
				#if sprite.map_pays.get_at((mouse[0],mouse[1])) != (0,0,0):
					id_pays_tmp=mouse_color[0]-100
					#print(id_pays_tmp)
					sp_msq=next((sp for sp in sprites_pays_masque if sp.id == id_pays_tmp), None)
					#print(sp_msq.id) 
					#print(sprite.id)
					#masque quand passage de la souris crée à la volé
					# if sprite.id != sprite_select:
					# 	sprite_bis=SpritePays(sprite.map_pays.copy(),"00.png") #no limpio
					# 	color_surface(sprite_bis,(1,1,1),150)
					# 	self.ventana.blit(sprite_bis.map_pays,(0,0))
					# 	pygame.display.flip()
					if id_pays_tmp != sprite_select:
						self.ventana.blit(sp_msq.map_pays,(0,0))
						pygame.display.update(sp_msq.map_pays.get_rect())
						#pygame.display.update(sp_msq.bounds)
					click=pygame.mouse.get_pressed()
					if self.turns.list_phase[self.turns.phase] == 'placement':
						#for event in pygame.event.get():
							#if event.type == pygame.MOUSEBUTTONDOWN:
							if click[0]==1:
								pays=next((p for p in self.map.pays if p.id == id_pays_tmp), None) 
								if pays.id_player==self.turns.player_turn:
									#actualización del número de tropas
									self.turns.placer(pays,self.nb_units)
									pygame.time.wait(100) #no limpio
									# try:
									# 	self.nb_units=self.players[self.turns.player_turn-1].nb_tropas
									# except ValueError as e:
									# 	print(e.args)
								else:
									#raise error
									print('pays n\'appartenant pas au joueur')
					elif self.turns.list_phase[self.turns.phase] == 'attaque':
						if click[0]==1 and not select: #selección del país atacante 
							pays1=next((p for p in self.map.pays if p.id == id_pays_tmp), None)
							self.pays_select=pays1
							if pays1.id_player==self.turns.player_turn and pays1.nb_tropas>1:
								self.nb_units=pays1.nb_tropas-1
								self.tmp.append(sp_msq.map_pays)
								select=True 
								sprite_select=id_pays_tmp
						elif click[0]==1:#selección del país atacado
							pays2=next((p for p in self.map.pays if p.id == id_pays_tmp), None)
							if atck_winmove and pays2 == pays_atck and pays1.nb_tropas>1:#
								self.turns.deplacer(pays1,pays2,self.nb_units)
								select=False
								self.tmp=[]
								atck_winmove=False
							elif atck_winmove:
								select=False
								self.tmp=[]
								atck_winmove=False
							elif pays2.id_player!=self.turns.player_turn and pays2.id in pays1.voisins:
								try:
									self.dices=[]		 #eliminamos los viejos sprites de los dados								
									atck,res_l=self.turns.attaque(pays1,pays2,self.nb_units)
									print(res_l)
									for idx,res in enumerate(res_l):
										roll_dices(self,res[0],res[2],600,sprites_pays[0].map_pays.get_height()+10+idx*DICE_SIZE*1.1)#no limpio
										roll_dices(self,res[1],res[3],800,sprites_pays[0].map_pays.get_height()+10+idx*DICE_SIZE*1.1)
									pygame.time.wait(100) #no limpio
									#print(res)movimiento libre después de un ataque exitoso
								except ValueError as e:
									print(e.args)
									atck=False
									select=False
									self.tmp=[]
								if atck:
									sprite=next((s for s in sprites_pays if s.id == id_pays_tmp), None)
									color_surface(sprite,self.turns.players[self.turns.player_turn-1].color,255)
									merged_pays.blit(sprite.map_pays,(0,0))
									atck_winmove=True
									pays_atck=pays2
									self.nb_units=pays1.nb_tropas-1
								else:
									select=False
									self.tmp=[]
					elif self.turns.list_phase[self.turns.phase] == 'deplacement':
						if click[0]==1 and not select:
							pays1=next((p for p in self.map.pays if p.id == id_pays_tmp), None)
							self.pays_select=pays1
							if pays1.id_player==self.turns.player_turn and pays1.nb_tropas>1:
								self.nb_units=pays1.nb_tropas-1
								self.tmp.append(sp_msq.map_pays)
								select=True 
								sprite_select=id_pays_tmp
						elif click[0]==1:
							pays2=next((p for p in self.map.pays if p.id == id_pays_tmp), None)
							chemin=self.map.chemin_exist(self.turns.players[self.turns.player_turn-1].pays,pays1,pays2)
							select=False
							sprite_select=0
							self.tmp=[]
							if chemin and pays2.id != pays1.id:
								self.turns.deplacer(pays1,pays2,self.nb_units)
								self.turns.next()
					#exhibición de tropas
					self.textes=[]
					display_tropas(self.textes,sprites_pays,self.map)
					#pausa
			except ValueError as e:
				pass #no limpio

			#HUD
			#print('tour numero :', self.num,'ordre',self.ordre,'joueur tour', self.ordre[self.id_ordre])
			#print(self.list_phase[self.phase])
			self.t_hud=[]
			display_hud(self.nb_units,self.t_hud,self.turns,(75,sprites_pays[0].map_pays.get_height()+10),hide)
			pygame.display.flip()

def menu(Win):
	#useless?
	barre=pygame.image.load(PATH_IMG+BAR_IMG).convert()
	r1=Win.ventana.blit(barre,(0,0))
	Win.surfaces.extend([[barre,r1]])

#visualización de dados (resultados) + calaveras por pérdidas
def roll_dices(Win,pertes,number,x,y):
	L=[]
	for idx,d in enumerate(number):
		de=pygame.image.load(PATH_DCE+str(d)+".png").convert_alpha()
		resize_de=pygame.transform.scale(de,(DICE_SIZE,DICE_SIZE)) #cambiar el tamaño de los dados
		L.append([resize_de,Win.ventana.blit(resize_de,(idx*DICE_SIZE*1.1+x,y))])

	for idx_p in range(0,pertes):
		deadhead=pygame.image.load(PATH_DCE+DHE_IMG).convert_alpha()
		resize_dh=pygame.transform.scale(deadhead,(DICE_SIZE,DICE_SIZE)) #cambiar el tamaño de la cabeza muerta
		L.append([resize_dh,Win.ventana.blit(resize_dh,(x-(idx_p+1)*DICE_SIZE*1.1,y))])
	Win.dices.extend(L) 

def menu_but(Win):
	#useless
	colors=ColorMap()
	#button('Start',150,150,100,50,colors.grey,colors.black,resize des deadheadstart_game)
	func=functools.partial(roll_dices,Win,[5,4,4],0,0)		#generación de una nueva función con agrupamientos
	button('Roll1',f_w/2,f_h/2,100,50,colors.grey,colors.black,func)
	func=functools.partial(roll_dices,Win,[1,6],0,0)		
	button('Roll2',300,300,100,50,colors.black,colors.black,func)

if __name__ == '__main__':
	import Risk
	from Risk import *
	print("== Tests unitaires ==")
	M=Map('Terre')
	Continents=M.continents
	T=Turns(3,M)
	T.start_deploy()
	print(T.distrib_pays(M.pays))
	T.print_players()
	#M.print_pays()
	Colors=ColorMap()
	T.players[0].color=Colors.dark_purple
	T.players[1].color=Colors.dark_green
	T.players[2].color=Colors.dark_red
	# T.players[3].color=Colors.white
	# T.players[4].color=Colors.yellow
	# T.players[5].color=Colors.cian
	T.players[0].name='santi'
	T.players[1].name='danna'
	T.players[2].name='diana'
	# T.players[3].name='wis'
	# T.players[4].name='gogor'
	# T.players[5].name='pilou'
	# T.players[3].color=grey

	pygame.init()
	clock = pygame.time.Clock()
	ventana = pygame.display.set_mode((f_w, f_h))
	Win=CurrentWindow(ventana,T)
	Win.game.nujugadores=3
	Win.game.joueurs=['nico','nono','jojo']
	#menu_but(Win)							#cartel ini? inútil?
	Win.fonctions.append(Win.start_game)		#funciones ini
	clock.tick(60)

	Win.afficher()	#entramos en la pantalla mientras bucle
