# pygame_app.py
"""
A PyGame front end for your maroon card game with:
 1) Dynamic row for the human's 'active' zone (hand or face-up).
 2) Forced random flip from face-down only when hand + face-up are empty.
 3) If a flipped face-down is unplayable, it goes into your hand,
    so you now see it (along with the discard pile).
 4) Immediate removal / game end if a player reaches 0 total cards.
 5) Multiple AI personalities (AIPlayer, LowestFirstAI, HighestFirstAI, RandomAI).
"""

import pygame
import sys
import os
import random

import cards
import rules
import scoring
import player
import game

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 30

WHITE = (255,255,255)
GRAY  = (180,180,180)
BLACK = (0,0,0)
GREEN = (0,200,0)
RED   = (200,0,0)

FONT = pygame.font.SysFont("arial", 18)

CARD_W = 42
CARD_H = 60

# States
STATE_MAIN_MENU        = 0
STATE_OPTIONS          = 1
STATE_FACEUP_SELECTION = 2
STATE_GAMEPLAY         = 3

# Pre-defined seat coords for up to 3 face-down/face-up plus center piles
card_positions = {
    # bottom
    "player_face_down": [(300,400),(370,400),(440,400)],
    "player_face_up":   [(300,450),(370,450),(440,450)],

    # top
    "top_face_down": [(300,50),(370,50),(440,50)],
    "top_face_up":   [(300,100),(370,100),(440,100)],

    # right
    "right_face_down": [(700,200),(700,260),(700,320)],
    "right_face_up":   [(640,200),(640,260),(640,320)],

    # left
    "left_face_down":  [(100,200),(100,260),(100,320)],
    "left_face_up":    [(160,200),(160,260),(160,320)],

    # center
    "undealt_pile": (370,250),
    "active_pile":  (450,250),
}

CARD_IMAGES = {}
CARD_BACK_IMAGE = None

# For file naming
RANK_TO_FILEPART = {
    2:"02",3:"03",4:"04",5:"05",6:"06",
    7:"07",8:"08",9:"09",10:"10",
    11:"J",12:"Q",13:"K",14:"A"
}

def load_card_images():
    global CARD_BACK_IMAGE
    # 52 combos
    for rank in cards.RANKS:
        rank_str= RANK_TO_FILEPART[rank]
        for suit in cards.SUITS:
            fname= f"card_{suit.lower()}_{rank_str}.png"
            path= os.path.join("cards", fname)
            if os.path.exists(path):
                img= pygame.image.load(path).convert_alpha()
                CARD_IMAGES[(rank, suit)] = img
            else:
                placeholder= pygame.Surface((CARD_W, CARD_H))
                placeholder.fill((120,120,120))
                CARD_IMAGES[(rank, suit)] = placeholder
    # card_back
    back_path= os.path.join("cards","card_backing.png")
    if os.path.exists(back_path):
        CARD_BACK_IMAGE= pygame.image.load(back_path).convert_alpha()
    else:
        fallback= pygame.Surface((CARD_W,CARD_H))
        fallback.fill((80,0,0))
        CARD_BACK_IMAGE= fallback

class App:
    def __init__(self):
        self.screen= pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
        pygame.display.set_caption("maroon - Merged Hand UI + Forced FaceDown")
        self.clock= pygame.time.Clock()

        self.state= STATE_MAIN_MENU
        self.num_ais=1
        self.game_in_progress=False

        self.players=[]
        self.discard_pile=[]
        self.leftover_deck=[]
        self.current_index=0
        self.scores={"You":0}
        self.round_count=1
        self.finish_order=[]
        self.msg_log=""

        # face-up selection
        self.faceup_temp_cards=[]
        self.faceup_selected=set()
        self.faceup_player=None

        # dynamic row collision
        self.player_zone_rects=[]
        self.selected_card_indices=set()

    def run(self):
        load_card_images()
        running=True
        while running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    running=False
                self.handle_event(event)

            self.update()
            self.draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    # ----------------------------------------------------------------
    # EVENT
    # ----------------------------------------------------------------
    def handle_event(self, event):
        if self.state==STATE_MAIN_MENU:
            self.handle_menu_event(event)
        elif self.state==STATE_OPTIONS:
            self.handle_options_event(event)
        elif self.state==STATE_FACEUP_SELECTION:
            self.handle_faceup_event(event)
        elif self.state==STATE_GAMEPLAY:
            self.handle_game_event(event)

    def handle_menu_event(self, event):
        if event.type==pygame.MOUSEBUTTONUP:
            x,y= event.pos
            if 300<=x<=500 and 200<=y<=240:
                self.start_new_game()
            elif 300<=x<=500 and 260<=y<=300:
                self.state= STATE_OPTIONS
            elif 300<=x<=500 and 320<=y<=360:
                pygame.event.post(pygame.event.Event(pygame.QUIT))

    def handle_options_event(self, event):
        if event.type==pygame.MOUSEBUTTONUP:
            x,y= event.pos
            # - button
            if 250<=x<=280 and 200<=y<=230:
                if self.num_ais>0:
                    self.num_ais-=1
            # + button
            if 320<=x<=350 and 200<=y<=230:
                if self.num_ais<3:
                    self.num_ais+=1
            # back
            if 300<=x<=500 and 400<=y<=440:
                self.state= STATE_MAIN_MENU

    def handle_faceup_event(self, event):
        if event.type==pygame.MOUSEBUTTONUP:
            x,y= event.pos
            # confirm
            if 650<=x<=780 and 500<=y<=540:
                if len(self.faceup_selected)==3:
                    self.finalize_faceup_selection()
                else:
                    self.msg_log= "Select exactly 3!"
            else:
                rects= self.get_faceup_temp_rects()
                for i,r_ in enumerate(rects):
                    pop= 10 if i in self.faceup_selected else 0
                    r_moved= r_.copy()
                    r_moved.y-=pop
                    if r_moved.collidepoint(x,y):
                        if i in self.faceup_selected:
                            self.faceup_selected.remove(i)
                        else:
                            if len(self.faceup_selected)<3:
                                self.faceup_selected.add(i)
                            else:
                                self.msg_log="Max 3!"
                        break

    def handle_game_event(self, event):
        if not self.game_in_progress:
            return
        if event.type==pygame.MOUSEBUTTONUP:
            x,y= event.pos
            # End Turn
            if 650<=x<=780 and 500<=y<=540:
                self.attempt_player_move()
            # Pick Up
            elif 650<=x<=780 and 550<=y<=590:
                self.pick_up_discard()
            else:
                # possibly clicked on player's dynamic row
                cp= self.current_player()
                if cp and cp.is_human:
                    # only if we have an active zone (hand or face-up)
                    zone= self.get_active_zone(cp)
                    if zone is not None and zone:
                        for idx, rect_ in enumerate(self.player_zone_rects):
                            pop_off= 10 if idx in self.selected_card_indices else 0
                            r_moved= rect_.copy()
                            r_moved.y-= pop_off
                            if r_moved.collidepoint(x,y):
                                if idx in self.selected_card_indices:
                                    self.selected_card_indices.remove(idx)
                                else:
                                    self.selected_card_indices.add(idx)
                                break

    # ----------------------------------------------------------------
    # UPDATE
    # ----------------------------------------------------------------
    def update(self):
        if self.state==STATE_GAMEPLAY and self.game_in_progress:
            cp= self.current_player()
            if cp:
                # check if 0 => done
                if cp.total_cards_left()==0:
                    self.handle_player_done(cp)
                else:
                    if not cp.is_human:
                        self.handle_ai_turn()
                        pygame.time.wait(500)
                    else:
                        # forced random flip if no hand or face-up
                        self.handle_human_turn_if_needed(cp)

    def handle_player_done(self, p):
        self.msg_log= f"{p.name} has 0 cards left!"
        # if 1v1
        if len(self.players)==2:
            if p.name=="You":
                self.msg_log="You have no cards => You won!"
            else:
                self.msg_log=f"{p.name} is out => you lose."
            self.game_in_progress=False
        else:
            # remove them
            self.players.remove(p)
            if self.current_index>=len(self.players):
                self.current_index=0
            self.msg_log+= " Removed from table."
            if len(self.players)==1:
                lastp= self.players[0]
                if lastp.name=="You":
                    self.msg_log="You're last => Typically means you lose in maroon, or you can call it a 'win'."
                else:
                    self.msg_log=f"{lastp.name} is last => maroon tradition => they're the maroon!"
                self.game_in_progress=False

    def handle_human_turn_if_needed(self, cp):
        # if you have hand or face-up => you can click
        if cp.hand or cp.face_up:
            return
        # else forced random flip from face-down if any
        if cp.face_down:
            flip_idx= random.randrange(len(cp.face_down))
            flipped= cp.face_down.pop(flip_idx)
            c_str= cards.card_name(flipped)
            self.msg_log= f"You flip {c_str} from face-down..."

            base_card= rules.get_effective_top(self.discard_pile)
            d,r= rules.special_card_next_turn_override
            if d and r:
                direction= d
                ref_card= r
            else:
                direction= "higher"
                ref_card= base_card

            if rules.can_play(flipped, ref_card, direction):
                self.msg_log+= " It's playable!"
                self.discard_pile.append(flipped)
                # scoring
                pts= scoring.compute_card_score(flipped, ref_card, self.round_count)
                self.scores["You"]+= pts
                self.msg_log+= f" => +{pts} pts."
                same= rules.handle_special_card(flipped, self.discard_pile, cp, ref_card)
                if not same:
                    self.current_index= (self.current_index+1)%len(self.players)
                else:
                    rules.recheck_special_overrides(self.discard_pile)
            else:
                self.msg_log+= " Not playable => you pick it + discard up, added to your hand."
                cp.hand.append(flipped)
                cp.hand.extend(self.discard_pile)
                self.discard_pile.clear()
                self.current_index= (self.current_index+1)%len(self.players)
        else:
            # no face-down => skip
            self.msg_log="No face-down => skip."
            self.current_index= (self.current_index+1)%len(self.players)

    # ----------------------------------------------------------------
    # DRAW
    # ----------------------------------------------------------------
    def draw(self):
        self.screen.fill((20,100,20))
        if self.state==STATE_MAIN_MENU:
            self.draw_menu()
        elif self.state==STATE_OPTIONS:
            self.draw_options()
        elif self.state==STATE_FACEUP_SELECTION:
            self.draw_faceup_selection()
        elif self.state==STATE_GAMEPLAY:
            self.draw_gameplay()

    def draw_menu(self):
        t= FONT.render("Maroon - Main Menu", True,WHITE)
        self.screen.blit(t,(300,100))
        self.draw_button(300,200,200,40,"Play")
        self.draw_button(300,260,200,40,"Options")
        self.draw_button(300,320,200,40,"Quit")

    def draw_options(self):
        t= FONT.render("Options",True,WHITE)
        self.screen.blit(t,(300,100))
        label= FONT.render("Number of AI Opponents:",True,WHITE)
        self.screen.blit(label,(100,200))

        self.draw_button(250,200,30,30,"-")
        val= FONT.render(str(self.num_ais),True,WHITE)
        self.screen.blit(val,(290,205))
        self.draw_button(320,200,30,30,"+")

        self.draw_button(300,400,200,40,"Back to Menu")

    def draw_faceup_selection(self):
        t= FONT.render("Pick 3 for face-up:", True,WHITE)
        self.screen.blit(t,(20,20))
        m= FONT.render(self.msg_log,True,WHITE)
        self.screen.blit(m,(20,50))

        rects= self.get_faceup_temp_rects()
        for i, c_ in enumerate(self.faceup_temp_cards):
            pop= 10 if i in self.faceup_selected else 0
            r= rects[i].copy()
            r.y-= pop
            surf= self.get_card_image(c_)
            self.screen.blit(surf,(r.x,r.y))

        self.draw_button(650,500,130,40,"Confirm")

    def draw_gameplay(self):
        rnd= FONT.render(f"Round #{self.round_count}",True,WHITE)
        self.screen.blit(rnd,(20,20))

        sc= FONT.render(f"Your Score: {self.scores.get('You',0)}",True,WHITE)
        self.screen.blit(sc,(20,50))

        msg_= FONT.render(self.msg_log,True,WHITE)
        self.screen.blit(msg_,(20,120))

        cp= self.current_player()
        if cp:
            turn_= FONT.render(f"Current turn: {cp.name}",True,WHITE)
            self.screen.blit(turn_,(20,80))

        # seat-based face-down/face-up + center piles
        self.draw_layout()

        # draw player's active zone (hand if not empty, else face-up if not empty)
        # (But remember forced face-down flipping is random => no direct click for face-down.)
        human= self.players[0]
        active_zone= self.get_active_zone(human)
        if active_zone and human == cp and cp.is_human:
            # draw at bottom if we have cards to pick from
            self.draw_player_zone_dynamic(active_zone)

        self.draw_button(650,500,130,40,"End Turn")
        self.draw_button(650,550,130,40,"Pick Up")

    def get_active_zone(self, p):
        """If p has hand => that's the clickable zone.
           else if face_up => clickable.
           else if face_down => forced random => no direct click."""
        if p.hand:
            return p.hand
        elif p.face_up:
            return p.face_up
        else:
            return None

    def draw_layout(self):
        zones_to_cards= {
            "player_face_down": [],
            "player_face_up":   [],
            "top_face_down": [],
            "top_face_up":   [],
            "right_face_down": [],
            "right_face_up":   [],
            "left_face_down":  [],
            "left_face_up":    [],
            "undealt_pile": [],
            "active_pile":  [],
        }

        # leftover deck
        if self.leftover_deck:
            zones_to_cards["undealt_pile"].append(CARD_BACK_IMAGE)
        # discard
        if self.discard_pile:
            top_c= self.discard_pile[-1]
            zones_to_cards["active_pile"].append(self.get_card_image(top_c))

        seat_map= {}
        seat_map[self.players[0]]= "bottom"
        if len(self.players)>=2: seat_map[self.players[1]]= "top"
        if len(self.players)>=3: seat_map[self.players[2]]= "right"
        if len(self.players)>=4: seat_map[self.players[3]]= "left"

        for p in self.players:
            seat= seat_map[p]
            fd= p.face_down[:3]
            fu= p.face_up[:3]
            fd_surfs= [CARD_BACK_IMAGE]*len(fd)
            fu_surfs= [self.get_card_image(c) for c in fu]

            if seat=="bottom":
                zones_to_cards["player_face_down"]= fd_surfs
                zones_to_cards["player_face_up"]  = fu_surfs
            elif seat=="top":
                zones_to_cards["top_face_down"]= fd_surfs
                zones_to_cards["top_face_up"]  = fu_surfs
            elif seat=="right":
                zones_to_cards["right_face_down"]= fd_surfs
                zones_to_cards["right_face_up"]  = fu_surfs
            elif seat=="left":
                zones_to_cards["left_face_down"]= fd_surfs
                zones_to_cards["left_face_up"]  = fu_surfs

        for zone_name, surf_list in zones_to_cards.items():
            self.draw_zone(zone_name, surf_list)

    def draw_zone(self, zone_name, surfaces):
        pos_list= card_positions[zone_name]
        if isinstance(pos_list, tuple):
            pos_list=[pos_list]
        angle= 0
        if zone_name.startswith("left_"):
            angle= 90
        elif zone_name.startswith("right_"):
            angle= -90

        for i, s_ in enumerate(surfaces):
            if i>= len(pos_list):
                break
            x,y= pos_list[i]
            if angle!=0:
                rot= pygame.transform.rotate(s_, angle)
                self.screen.blit(rot,(x,y))
            else:
                self.screen.blit(s_,(x,y))

    def draw_player_zone_dynamic(self, card_list):
        """
        Draw the current player's (human) zone at bottom y=500.
        If a card is in self.selected_card_indices, pop it up by 10 px.
        Store collision rects for click detection.
        """
        self.player_zone_rects=[]
        x_start= 300
        y_base= 500
        spacing= CARD_W+10
        for i, c_ in enumerate(card_list):
            pop_off= 10 if i in self.selected_card_indices else 0
            x= x_start + i*spacing
            y= y_base - pop_off
            surf= self.get_card_image(c_)
            self.screen.blit(surf,(x,y))

            r_= pygame.Rect(x,y,CARD_W,CARD_H)
            self.player_zone_rects.append(r_)

    # ----------------------------------------------------------------
    # UTILS
    # ----------------------------------------------------------------
    def get_card_image(self, card_):
        return CARD_IMAGES.get((card_[0], card_[1]), CARD_BACK_IMAGE)

    def get_faceup_temp_rects(self):
        rects=[]
        spacing= CARD_W+10
        total_w= 6*spacing
        start_x= (SCREEN_WIDTH - total_w)//2
        y=200
        for i in range(6):
            rx= start_x + i*spacing
            rects.append(pygame.Rect(rx,y,CARD_W,CARD_H))
        return rects

    def current_player(self):
        if 0<= self.current_index< len(self.players):
            return self.players[self.current_index]
        return None

    def draw_button(self, x,y,w,h,text):
        rect= pygame.Rect(x,y,w,h)
        pygame.draw.rect(self.screen,GRAY,rect)
        pygame.draw.rect(self.screen,BLACK,rect,2)
        t_surf= FONT.render(text,True,BLACK)
        tx= x+(w - t_surf.get_width())//2
        ty= y+(h - t_surf.get_height())//2
        self.screen.blit(t_surf,(tx,ty))

    # ----------------------------------------------------------------
    # MAIN FLOW
    # ----------------------------------------------------------------
    def start_new_game(self):
        self.state= STATE_FACEUP_SELECTION
        self.game_in_progress= True
        self.msg_log=""
        deck= cards.build_full_deck()
        random.shuffle(deck)

        self.players=[]
        human= player.HumanPlayer("You")
        self.players.append(human)

        # multiple AI personalities
        ai_personality_list= [player.AIPlayer, player.LowestFirstAI, player.HighestFirstAI, player.RandomAI]
        male_names=["John","Michael","David","Chris","James"]
        female_names=["Sarah","Emily","Laura","Kate","Linda"]

        for i in range(self.num_ais):
            if random.random()<0.5:
                nm= random.choice(male_names)
            else:
                nm= random.choice(female_names)
            nm+= f"#{i+1}"
            ai_class= random.choice(ai_personality_list)
            ai_= ai_class(name= nm)
            self.players.append(ai_)

        # human => 3 face-down + 6 temp
        for _ in range(3):
            human.face_down.append(deck.pop())
        self.faceup_temp_cards= [deck.pop() for _ in range(6)]
        self.faceup_selected.clear()
        self.faceup_player= human

        # AI => standard deal
        for p in self.players[1:]:
            game.deal_to_player_shead_style(deck, p, allow_faceup_choice=False)

        self.discard_pile=[]
        self.leftover_deck= deck
        self.current_index=0
        self.finish_order=[]

    def finalize_faceup_selection(self):
        chosen= [self.faceup_temp_cards[i] for i in sorted(self.faceup_selected)]
        leftover= [self.faceup_temp_cards[i] for i in range(6) if i not in self.faceup_selected]
        self.faceup_player.face_up= chosen
        self.faceup_player.hand   = leftover
        self.state= STATE_GAMEPLAY

    def attempt_player_move(self):
        """
        If the user has selected some cards, remove them from the
        active zone (hand or face_up), place them on discard, check can_play,
        etc.
        """
        cp= self.current_player()
        if not cp or not cp.is_human:
            return
        if not self.selected_card_indices:
            self.msg_log= "No cards selected!"
            return

        zone= self.get_active_zone(cp)
        if not zone:
            self.msg_log= "You have no cards to play."
            return

        chosen_cards= [zone[i] for i in sorted(self.selected_card_indices)]
        # check all same rank
        ranks= [c_[0] for c_ in chosen_cards]
        if len(set(ranks))!=1:
            self.msg_log= "All chosen cards must share the same rank!"
            return

        base_card= rules.get_effective_top(self.discard_pile)
        d,r= rules.special_card_next_turn_override
        if d and r:
            direction= d
            ref_card= r
        else:
            direction= "higher"
            ref_card= base_card

        # check can_play
        for c_ in chosen_cards:
            if not rules.can_play(c_, ref_card, direction):
                from cards import card_name
                self.msg_log= f"{card_name(c_)} not playable right now."
                return

        # remove from zone
        for i in sorted(self.selected_card_indices,reverse=True):
            zone.pop(i)
        self.selected_card_indices.clear()

        # discard
        for c_ in chosen_cards:
            self.discard_pile.append(c_)

        # scoring
        total_pts=0
        for c_ in chosen_cards:
            pts= scoring.compute_card_score(c_, ref_card, self.round_count)
            total_pts+= pts
        self.scores["You"]+= total_pts
        self.msg_log= f"You played {len(chosen_cards)} => +{total_pts} pts"

        # special
        last_= chosen_cards[-1]
        same_player= rules.handle_special_card(last_, self.discard_pile, cp, ref_card)
        if not same_player:
            self.current_index= (self.current_index+1)%len(self.players)
        else:
            rules.recheck_special_overrides(self.discard_pile)

    def pick_up_discard(self):
        cp= self.current_player()
        if not cp or not cp.is_human:
            return
        cp.hand.extend(self.discard_pile)
        self.discard_pile.clear()
        self.selected_card_indices.clear()
        self.msg_log= "You picked up the discard pile."
        self.current_index= (self.current_index+1)%len(self.players)

    def handle_ai_turn(self):
        ai= self.current_player()
        if not ai:
            return
        # if 0 => done
        if ai.total_cards_left()==0:
            self.handle_player_done(ai)
            return

        base_card= rules.get_effective_top(self.discard_pile)
        d,r= rules.special_card_next_turn_override
        if d and r:
            direction= d
            ref_card= r
        else:
            direction= "higher"
            ref_card= base_card

        # if ai has hand => pick from hand
        if ai.hand:
            zone= ai.hand
        elif ai.face_up:
            zone= ai.face_up
        else:
            # forced random flip from face-down if any
            if ai.face_down:
                flip_idx= random.randrange(len(ai.face_down))
                flipped= ai.face_down.pop(flip_idx)
                from cards import card_name
                c_str= card_name(flipped)
                self.msg_log= f"{ai.name} flips {c_str} from face-down..."
                if rules.can_play(flipped, ref_card, direction):
                    self.msg_log+= " It's playable!"
                    self.discard_pile.append(flipped)
                    # no AI scoring
                    same= rules.handle_special_card(flipped, self.discard_pile, ai, ref_card)
                    if not same:
                        self.current_index= (self.current_index+1)%len(self.players)
                    else:
                        rules.recheck_special_overrides(self.discard_pile)
                else:
                    self.msg_log+= " Not playable => they pick it + discard up."
                    ai.hand.append(flipped)
                    ai.hand.extend(self.discard_pile)
                    self.discard_pile.clear()
                    self.current_index= (self.current_index+1)%len(self.players)
            else:
                # no face-down => skip
                self.msg_log=f"{ai.name} has no cards => skipping or removing them?"
                if ai.total_cards_left()==0:
                    self.handle_player_done(ai)
                else:
                    self.current_index= (self.current_index+1)%len(self.players)
            return

        # normal picking from zone
        valid_idx= [i for i,c_ in enumerate(zone) if rules.can_play(c_, ref_card, direction)]
        if not valid_idx:
            ai.hand.extend(self.discard_pile)
            self.discard_pile.clear()
            self.msg_log= f"{ai.name} picks up discard."
            self.current_index= (self.current_index+1)%len(self.players)
            return
        chosen_idx= ai.pick_cards_from_zone(zone, valid_idx, direction, ref_card, self.discard_pile)
        if not chosen_idx:
            ai.hand.extend(self.discard_pile)
            self.discard_pile.clear()
            self.msg_log= f"{ai.name} picks up discard."
            self.current_index= (self.current_index+1)%len(self.players)
            return
        chosen_cards= [zone[i] for i in sorted(chosen_idx)]
        for i in sorted(chosen_idx,reverse=True):
            zone.pop(i)
        for c_ in chosen_cards:
            self.discard_pile.append(c_)
        self.msg_log= f"{ai.name} plays {len(chosen_cards)} card(s)."
        last_= chosen_cards[-1]
        same_p= rules.handle_special_card(last_, self.discard_pile, ai, ref_card)
        if not same_p:
            self.current_index= (self.current_index+1)%len(self.players)
        else:
            rules.recheck_special_overrides(self.discard_pile)


def main():
    app= App()
    app.run()

if __name__=="__main__":
    main()
