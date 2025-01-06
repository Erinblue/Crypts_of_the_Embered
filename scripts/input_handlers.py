from typing import Optional

import tcod.event

from scripts.actions import Action, BumpAction, EscapeAction


class EventHandler(tcod.event.EventDispatch[Action]):
    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        raise SystemExit()
    
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        action: Optional[Action] = None

        key = event.sym

        match key:
            case tcod.event.KeySym.UP:
                action = BumpAction(dx=0, dy=-1)
            case tcod.event.KeySym.DOWN:
                action = BumpAction(dx=0, dy=1)
            case tcod.event.KeySym.LEFT:
                action = BumpAction(dx=-1, dy=0)
            case tcod.event.KeySym.RIGHT:
                action = BumpAction(dx=1, dy=0)
            
            case tcod.event.KeySym.ESCAPE:
                action = EscapeAction()
        
        return action