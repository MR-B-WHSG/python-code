# main_app.py
"""
Main PyGame app for Maroon, referencing setup.py for game creation.
End-of-game:
 - Display scoreboard & finishing order
 - Ask user if they want to play again or return to main menu

Features:
 - AI turn logic, forced face-down flipping
 - 9 pop-up (human chooses high/low)
 - Discard history (last 3)
 - Dynamic row for the player's hand/face-up
 - If multi-player, we remove finishing players in turn order
   until only 1 remains, then end with finishing order
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

from setup import GameSetup

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
STATE_ENDGAME          = 4  # new end state

card_positions = {
    "player_face_down": [(300,400),(370,400),(440,400)],
    "player_face_up":   [(290,450),(360,450),(430,450)],

    "top_face_down":  [(300,50),(370,50),(440,50)],
    "top_face_up":    [(290,100),(360,100),(430,100)],

    "right_face_down":[(700,200),(700,260),(700,320)],
    "right_face_up":  [(640,200),(640,260),(640,320)],

    "left_face_down": [(100,200),(100,260),(100,320)],
    "left_face_up":   [(160,200),(160,260),(160,320)],

    "undealt_pile": (370,250),
    "active_pile":  (450,250),
}

CARD_IMAGES = {}
CARD_BACK_IMAGE = None

RANK_TO_FILEPART = {
    2:"02",3:"03",4:"04",5:"05",6:"06",
    7:"07",8:"08",9:"09",10:"10",
    11:"J",12:"Q",13:"K",14:"A"
}

def load_card_images():
    global CARD_BACK_IMAGE
    for rank in cards.RANKS:
        rank_str= RANK_TO_FILEPART[rank]
        for suit in cards.SUITS:
            fname= f"card_{suit.lower()}_{rank_str}.png"
            path= os.path.join("cards", fname)
            if os.path.exists(path):
                img= pygame.image.load(path).convert_alpha()
                CARD_IMAGES[(rank, suit)] = img
            else:
                fallback= pygame.Surface((CARD_W,CARD_H))
                fallback.fill((120,120,120))
                CARD_IMAGES[(rank,suit)] = fallback
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
        pygame.display.set_caption("Mr B's Awesome Card Game Of Fun")
        self.clock= pygame.time.Clock()

        self.state= STATE_MAIN_MENU
        self.num_ais=1
        self.game_in_progress= False

        self.players=[]
        self.discard_pile=[]
        self.leftover_deck=[]
        self.current_index=0
        self.scores={"You":0}
        self.round_count=1
        self.finish_order=[]
        self.msg_log=""
        self.selected_card_indices= set()

        self.setup_util= GameSetup()

        self.last_effective_card= None

    def run(self):
        load_card_images()
        running= True
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

    # -----------------------------------------------------
    # EVENT
    # -----------------------------------------------------
    def handle_event(self, event):
        if self.state==STATE_MAIN_MENU:
            self.handle_menu_event(event)
        elif self.state==STATE_OPTIONS:
            self.handle_options_event(event)
        elif self.state==STATE_FACEUP_SELECTION:
            self.handle_faceup_event(event)
        elif self.state==STATE_GAMEPLAY:
            self.handle_game_event(event)
        elif self.state==STATE_ENDGAME:
            self.handle_endgame_event(event)

    def handle_menu_event(self, event):
        if event.type==pygame.MOUSEBUTTONUP:
            x,y= event.pos
            # "Play"
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
                if len(self.setup_util.faceup_selected)==3:
                    self.setup_util.finalize_faceup_selection()
                    self.state= STATE_GAMEPLAY
                else:
                    self.msg_log="Select exactly 3!"
            else:
                # toggling
                rects= self.get_faceup_temp_rects()
                for i,r_ in enumerate(rects):
                    pop= 10 if i in self.setup_util.faceup_selected else 0
                    r_moved= r_.copy()
                    r_moved.y-= pop
                    if r_moved.collidepoint(x,y):
                        if i in self.setup_util.faceup_selected:
                            self.setup_util.faceup_selected.remove(i)
                        else:
                            if len(self.setup_util.faceup_selected)<3:
                                self.setup_util.faceup_selected.add(i)
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
            elif 650<=x<=780 and 550<=y<=590:
                self.pick_up_discard()
            else:
                cp= self.current_player()
                if cp and cp.is_human:
                    zone= self.get_active_zone(cp)
                    if zone:
                        for idx, rect_ in enumerate(self.player_zone_rects):
                            pop_off= 10 if idx in self.selected_card_indices else 0
                            r_moved= rect_.copy()
                            r_moved.y-=pop_off
                            if r_moved.collidepoint(x,y):
                                if idx in self.selected_card_indices:
                                    self.selected_card_indices.remove(idx)
                                else:
                                    self.selected_card_indices.add(idx)
                                break

    def handle_endgame_event(self, event):
        """
        In the endgame screen, we ask if they want to play again or go to main menu.
        """
        if event.type==pygame.MOUSEBUTTONUP:
            x,y= event.pos
            # "Play Again" button => state=faceup selection or do start_new_game
            if 300<=x<=500 and 400<=y<=440:
                # start new
                self.start_new_game()
            # "Main Menu" => state=main_menu
            elif 300<=x<=500 and 460<=y<=500:
                self.state= STATE_MAIN_MENU

    # -----------------------------------------------------
    # UPDATE
    # -----------------------------------------------------
    def update(self):
        if self.state==STATE_GAMEPLAY and self.game_in_progress:
            cp= self.current_player()
            if cp:
                if cp.total_cards_left()==0:
                    self.handle_player_done(cp)
                else:
                    if not cp.is_human:
                        self.handle_ai_turn()
                        pygame.time.wait(500)
                    else:
                        self.handle_human_turn_if_needed(cp)

    def handle_player_done(self, p):
        """
        If p has 0 cards, record them in finishing order. If 1v1 => game ends.
        If multi => remove them, keep going until 1 left, then end => show finishing order.
        """
        self.msg_log= f"{p.name} has 0 cards left!"
        self.finish_order.append(p.name)  # record their finishing

        if len(self.players)==2:
            # We are in 2-player => game ends
            if p.name=="You":
                self.msg_log="You have no cards => You win!"
            else:
                self.msg_log=f"{p.name} out => you lose!"
            self.game_in_progress=False
            # record other player too
            for pl in self.players:
                if pl!=p:
                    self.finish_order.append(pl.name)
            self.state= STATE_ENDGAME
        else:
            self.players.remove(p)
            if self.current_index>=len(self.players):
                self.current_index=0
            self.msg_log+=" Removed from table."
            if len(self.players)==1:
                lastp= self.players[0]
                self.finish_order.append(lastp.name)
                self.msg_log= f"Only {lastp.name} remains => game ends."
                self.game_in_progress=False
                self.state= STATE_ENDGAME

    def handle_human_turn_if_needed(self, cp):
        if cp.hand or cp.face_up:
            return
        if cp.face_down:
            flip_idx= random.randrange(len(cp.face_down))
            flipped= cp.face_down.pop(flip_idx)
            c_str= cards.card_name(flipped)
            self.msg_log= f"You flip {c_str}..."

            base_card= rules.get_effective_top(self.discard_pile)
            d,r= rules.special_card_next_turn_override
            if d and r:
                direction= d
                ref_card= r
            else:
                direction= "higher"
                ref_card= base_card

            if rules.can_play(flipped, ref_card, direction):
                self.msg_log+=" It's playable!"
                self.discard_pile.append(flipped)
                self.last_effective_card= flipped
                pts= scoring.compute_card_score(flipped, ref_card, self.round_count)
                self.scores["You"]+= pts
                self.msg_log+= f" => +{pts} pts."
                same= self.handle_special_card_9_popup(flipped, self.discard_pile, cp, ref_card)
                if not same:
                    self.current_index= (self.current_index+1)%len(self.players)
                else:
                    rules.recheck_special_overrides(self.discard_pile)
            else:
                self.msg_log+=" Not playable => pick it + discard up."
                cp.hand.append(flipped)
                cp.hand.extend(self.discard_pile)
                self.discard_pile.clear()
                self.current_index= (self.current_index+1)%len(self.players)
        else:
            self.msg_log="No face-down => skip."
            self.current_index= (self.current_index+1)%len(self.players)

    # -----------------------------------------------------
    # DRAW
    # -----------------------------------------------------
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
        elif self.state==STATE_ENDGAME:
            self.draw_endgame()

    def draw_menu(self):
        t= FONT.render("Maroon - Main Menu",True,WHITE)
        self.screen.blit(t,(300,100))
        self.draw_button(300,200,200,40,"Play")
        self.draw_button(300,260,200,40,"Options")
        self.draw_button(300,320,200,40,"Quit")

    def draw_options(self):
        t= FONT.render("Options",True,WHITE)
        self.screen.blit(t,(300,100))
        lab= FONT.render("Number of AI Opponents:",True,WHITE)
        self.screen.blit(lab,(100,200))

        self.draw_button(250,200,30,30,"-")
        val= FONT.render(str(self.num_ais),True,WHITE)
        self.screen.blit(val,(290,205))
        self.draw_button(320,200,30,30,"+")

        self.draw_button(300,400,200,40,"Back to Menu")

    def draw_faceup_selection(self):
        t= FONT.render("Pick 3 for face-up:",True,WHITE)
        self.screen.blit(t,(20,20))
        m= FONT.render(self.msg_log,True,WHITE)
        self.screen.blit(m,(20,50))

        rects= self.get_faceup_temp_rects()
        for i,c_ in enumerate(self.setup_util.faceup_temp_cards):
            pop= 10 if i in self.setup_util.faceup_selected else 0
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

        cp= self.current_player()
        if cp:
            turn_= FONT.render(f"Current turn: {cp.name}",True,WHITE)
            self.screen.blit(turn_,(20,80))

        msg_= FONT.render(self.msg_log,True,WHITE)
        self.screen.blit(msg_,(20,120))

        if self.last_effective_card:
            from cards import card_name
            eff_surf= FONT.render(f"Last effective card: {card_name(self.last_effective_card)}",True,WHITE)
            self.screen.blit(eff_surf,(20,150))

        self.draw_layout()
        self.draw_discard_history()

        # dynamic row
        cp= self.current_player()
        if cp and cp==self.players[0]:
            zone= self.get_active_zone(cp)
            if zone:
                self.draw_player_zone_dynamic(zone)

        self.draw_button(650,500,130,40,"End Turn")
        self.draw_button(650,550,130,40,"Pick Up")

    def draw_endgame(self):
        # Show scoreboard, finishing order, ask if play again or return menu
        t= FONT.render("GAME OVER!", True, WHITE)
        self.screen.blit(t,(300,100))

        # scoreboard
        sc= FONT.render(f"Your final score: {self.scores.get('You',0)}", True, WHITE)
        self.screen.blit(sc,(300,140))

        # finishing order
        fo= FONT.render("Finishing Order:", True, WHITE)
        self.screen.blit(fo,(300,180))
        y_offset= 210
        for i, name_ in enumerate(self.finish_order, start=1):
            line= FONT.render(f"{i}. {name_}", True, WHITE)
            self.screen.blit(line,(300,y_offset))
            y_offset+= 30

        # two buttons: "Play Again" => start_new_game, "Main Menu" => state=main_menu
        self.draw_button(300,400,200,40,"Play Again")
        self.draw_button(300,460,200,40,"Main Menu")

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
        if self.leftover_deck:
            zones_to_cards["undealt_pile"].append(CARD_BACK_IMAGE)
        if self.discard_pile:
            top_c= self.discard_pile[-1]
            zones_to_cards["active_pile"].append(self.get_card_image(top_c))

        seat_map= {}
        seat_map[self.players[0]]= "bottom"
        if len(self.players)>=2:
            seat_map[self.players[1]]= "top"
        if len(self.players)>=3:
            seat_map[self.players[2]]= "right"
        if len(self.players)>=4:
            seat_map[self.players[3]]= "left"

        for p in self.players:
            seat= seat_map[p]
            fd= p.face_down[:3]
            fu= p.face_up[:3]
            fd_surfs= [CARD_BACK_IMAGE]*len(fd)
            fu_surfs= [self.get_card_image(c_) for c_ in fu]
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

        for zone_name, surfs in zones_to_cards.items():
            self.draw_zone(zone_name, surfs)

    def draw_discard_history(self):
        x_start=500
        y=250
        spacing= CARD_W+5

        if len(self.discard_pile)>=2:
            last_two= self.discard_pile[-2:]
        else:
            last_two= self.discard_pile
        for i,c_ in enumerate(last_two):
            surf= self.get_card_image(c_)
            xx= x_start + i*spacing
            self.screen.blit(surf,(xx,y))

    def draw_zone(self, zone_name, surfaces):
        pos_list= card_positions[zone_name]
        if isinstance(pos_list, tuple):
            pos_list=[pos_list]
        angle=0
        if zone_name.startswith("left_"):
            angle= 90
        elif zone_name.startswith("right_"):
            angle= -90

        for i,s_ in enumerate(surfaces):
            if i>= len(pos_list):
                break
            x,y= pos_list[i]
            if angle!=0:
                rot= pygame.transform.rotate(s_, angle)
                self.screen.blit(rot,(x,y))
            else:
                self.screen.blit(s_,(x,y))

    def draw_player_zone_dynamic(self, card_list):
        self.player_zone_rects=[]
        x_start=300
        y_base=500
        spacing= CARD_W+10
        for i,c_ in enumerate(card_list):
            pop_off= 10 if i in self.selected_card_indices else 0
            x= x_start + i*spacing
            y= y_base - pop_off
            surf= self.get_card_image(c_)
            self.screen.blit(surf,(x,y))

            r_= pygame.Rect(x,y,CARD_W,CARD_H)
            self.player_zone_rects.append(r_)

    # -----------------------------------------------------
    # HELPER
    # -----------------------------------------------------
    def get_active_zone(self, p):
        if p.hand:
            return p.hand
        elif p.face_up:
            return p.face_up
        else:
            return None

    def get_card_image(self, card_):
        return CARD_IMAGES.get((card_[0],card_[1]), CARD_BACK_IMAGE)

    def get_faceup_temp_rects(self):
        rects=[]
        spacing= CARD_W+10
        total_w= 6*spacing
        start_x= (SCREEN_WIDTH-total_w)//2
        y=200
        for i in range(6):
            rects.append(pygame.Rect(start_x+i*spacing,y,CARD_W,CARD_H))
        return rects

    def current_player(self):
        if 0<= self.current_index< len(self.players):
            return self.players[self.current_index]
        return None

    def draw_button(self, x,y,w,h,text):
        rect= pygame.Rect(x,y,w,h)
        pygame.draw.rect(self.screen, GRAY, rect)
        pygame.draw.rect(self.screen, BLACK, rect,2)
        txt_surf= FONT.render(text, True, BLACK)
        tx= x+(w- txt_surf.get_width())//2
        ty= y+(h- txt_surf.get_height())//2
        self.screen.blit(txt_surf,(tx,ty))

    # -----------------------------------------------------
    # FLOW
    # -----------------------------------------------------
    def start_new_game(self):
        self.state= STATE_FACEUP_SELECTION
        self.game_in_progress= True
        self.msg_log=""
        self.finish_order=[]  # reset finishing order

        self.players, self.leftover_deck, self.discard_pile= self.setup_util.start_new_game(num_ais=self.num_ais)
        self.current_index=0


    def attempt_player_move(self):
        cp= self.current_player()
        if not cp or not cp.is_human:
            return
        zone= self.get_active_zone(cp)
        if not zone:
            self.msg_log= "No cards to play."
            return
        if not self.selected_card_indices:
            self.msg_log= "No cards selected!"
            return

        chosen_cards= [zone[i] for i in sorted(self.selected_card_indices)]
        ranks= [c_[0] for c_ in chosen_cards]
        if len(set(ranks))!=1:
            self.msg_log="All chosen must share rank!"
            return

        from rules import get_effective_top
        base_card= get_effective_top(self.discard_pile)
        d,r= rules.special_card_next_turn_override
        if d and r:
            direction= d
            ref_card= r
        else:
            direction= "higher"
            ref_card= base_card

        for c_ in chosen_cards:
            if not rules.can_play(c_, ref_card, direction):
                import cards
                self.msg_log= f"{cards.card_name(c_)} not playable."
                return

        for i in sorted(self.selected_card_indices,reverse=True):
            zone.pop(i)
        self.selected_card_indices.clear()

        for c_ in chosen_cards:
            self.discard_pile.append(c_)
        self.last_effective_card= chosen_cards[-1]

        total_pts=0
        for c_ in chosen_cards:
            pts= scoring.compute_card_score(c_, ref_card, self.round_count)
            total_pts+=pts
        self.scores["You"]+= total_pts
        self.msg_log= f"You played {len(chosen_cards)} => +{total_pts} pts"

        same_player= self.handle_special_card_9_popup(chosen_cards[-1], self.discard_pile, cp, ref_card)
        if not same_player:
            self.current_index= (self.current_index+1)%len(self.players)
        else:
            rules.recheck_special_overrides(self.discard_pile)

    def pick_up_discard(self):
        cp= self.current_player()
        if cp and cp.is_human:
            cp.hand.extend(self.discard_pile)
            self.discard_pile.clear()
            self.selected_card_indices.clear()
            self.msg_log= "You picked up the discard pile."
            self.current_index= (self.current_index+1)%len(self.players)

    def handle_ai_turn(self):
        ai= self.current_player()
        if not ai:
            return
        if ai.total_cards_left()==0:
            self.handle_player_done(ai)
            return

        from rules import get_effective_top
        base_card= get_effective_top(self.discard_pile)
        d,r= rules.special_card_next_turn_override
        if d and r:
            direction= d
            ref_card= r
        else:
            direction= "higher"
            ref_card= base_card

        if ai.hand:
            zone= ai.hand
        elif ai.face_up:
            zone= ai.face_up
        else:
            # forced random flip
            if ai.face_down:
                flip_idx= random.randrange(len(ai.face_down))
                flipped= ai.face_down.pop(flip_idx)
                from cards import card_name
                c_str= card_name(flipped)
                self.msg_log= f"{ai.name} flips {c_str}..."
                if rules.can_play(flipped, ref_card, direction):
                    self.msg_log+=" It's playable!"
                    self.discard_pile.append(flipped)
                    self.last_effective_card= flipped
                    same= self.handle_special_card_9_popup(flipped,self.discard_pile,ai,ref_card)
                    if not same:
                        self.current_index= (self.current_index+1)%len(self.players)
                    else:
                        rules.recheck_special_overrides(self.discard_pile)
                else:
                    self.msg_log+=" Not playable => picks it + discard."
                    ai.hand.append(flipped)
                    ai.hand.extend(self.discard_pile)
                    self.discard_pile.clear()
                    self.current_index= (self.current_index+1)%len(self.players)
            else:
                self.msg_log=f"{ai.name} has no face_down => skip."
                if ai.total_cards_left()==0:
                    self.handle_player_done(ai)
                else:
                    self.current_index= (self.current_index+1)%len(self.players)
            return

        # normal pick
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
        self.last_effective_card= chosen_cards[-1]
        same_= self.handle_special_card_9_popup(chosen_cards[-1],self.discard_pile,ai,ref_card)
        if not same_:
            self.current_index= (self.current_index+1)%len(self.players)
        else:
            rules.recheck_special_overrides(self.discard_pile)

    # 9 => pop-up
    def handle_special_card_9_popup(self, card_played, discard_pile, current_player, ref_card):
        from rules import special_card_next_turn_override, burn_pile
        # reset
        special_card_next_turn_override= (None,None)

        rank, suit= card_played
        if rank==2:
            special_card_next_turn_override= ("higher",(2,"Reset"))
            return False
        elif rank==9:
            base_rank= ref_card[0] if ref_card else 2
            if current_player.is_human:
                c_= self.show_9_popup(base_rank)
                special_card_next_turn_override= (c_,(base_rank,"NineRef"))
                self.msg_log+=f" => You chose {c_}"
            else:
                import random
                c_= random.choice(["higher","lower"])
                self.msg_log+=f" => {current_player.name} chooses {c_}"
                special_card_next_turn_override= (c_,(base_rank,"NineRef"))
            return False
        elif rank==10:
            self.msg_log+=" => 10 => burn pile, same player continues."
            burn_pile(discard_pile)
            return True
        # 8 => do nothing
        return False

    def show_9_popup(self, base_rank):
        popup_rect= pygame.Rect(200,200,400,200)
        choice= None
        running= True
        while running:
            self.screen.fill((20,100,20))
            self.draw()
            # draw overlay
            pygame.draw.rect(self.screen,(50,50,50), popup_rect)
            pygame.draw.rect(self.screen, WHITE, popup_rect,2)
            ptxt= FONT.render(f"9 on {base_rank}? Higher or Lower next turn?",True,WHITE)
            self.screen.blit(ptxt,(popup_rect.x+20, popup_rect.y+20))

            high_rect= pygame.Rect(popup_rect.x+50, popup_rect.y+120,100,40)
            low_rect=  pygame.Rect(popup_rect.x+250, popup_rect.y+120,100,40)
            self.draw_button_rect(high_rect,"Higher")
            self.draw_button_rect(low_rect,"Lower")

            pygame.display.flip()
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type==pygame.MOUSEBUTTONUP:
                    x,y= event.pos
                    if high_rect.collidepoint(x,y):
                        choice="higher"
                        running=False
                        break
                    elif low_rect.collidepoint(x,y):
                        choice="lower"
                        running=False
                        break
        return choice

    def draw_button_rect(self, rect, text):
        pygame.draw.rect(self.screen, GRAY, rect)
        pygame.draw.rect(self.screen, BLACK, rect,2)
        tsurf= FONT.render(text, True, BLACK)
        tx= rect.x+(rect.width-tsurf.get_width())//2
        ty= rect.y+(rect.height-tsurf.get_height())//2
        self.screen.blit(tsurf,(tx,ty))

    # End game scoreboard
    def draw_endgame(self):
        t= FONT.render("GAME OVER!", True, WHITE)
        self.screen.blit(t,(300,100))

        sc= FONT.render(f"Your final score: {self.scores.get('You',0)}", True, WHITE)
        self.screen.blit(sc,(300,140))

        fo= FONT.render("Finishing Order:", True, WHITE)
        self.screen.blit(fo,(300,180))
        y_off=210
        for i,name_ in enumerate(self.finish_order, start=1):
            line= FONT.render(f"{i}. {name_}", True, WHITE)
            self.screen.blit(line,(300,y_off))
            y_off+=30

        # two buttons => "Play Again" => startNewGame, "Main Menu" => state=MAIN_MENU
        self.draw_button(300,400,200,40,"Play Again")
        self.draw_button(300,460,200,40,"Main Menu")

    # final step: called in handle_endgame_event
    def handle_endgame_event(self, event):
        if event.type==pygame.MOUSEBUTTONUP:
            x,y= event.pos
            # "Play Again"
            if 300<=x<=500 and 400<=y<=440:
                self.start_new_game()
                self.state= STATE_FACEUP_SELECTION
            # "Main Menu"
            elif 300<=x<=500 and 460<=y<=500:
                self.state= STATE_MAIN_MENU
                self.msg_log= ""
                self.finish_order=[]
                self.players=[]
                self.game_in_progress= False

if __name__=="__main__":
    app= App()
    app.run()
