from __future__ import annotations

from typing import Optional, Tuple, TYPE_CHECKING

import scripts.color as color
import scripts.exceptions as exceptions

if TYPE_CHECKING:
    from scripts.engine import Engine
    from scripts.entity import Actor, Entity, Item
    from scripts.input_handlers import EventHandler



class Action:
    def __init__(self, entity: Actor) -> None:
        super().__init__()
        self.entity = entity

    
    @property
    def engine(self) -> Engine:
        """Return the engine this action belongs to."""
        return self.entity.gamemap.engine
    
    def perform(self) -> None: 
        """Perform this action with the objects needed to determine its scope.

        `self.engine` is the scope this action is being performed in.

        `self.entity` is the object performing the action.

        This method must be overridden by Action subclasses.
        """
        raise NotImplementedError()


class PickupAction(Action):
    """Pickup an item and add it to the inventory, if there is room for it."""

    def __init__(self, entity: Actor):
        super().__init__(entity)

    def perform(self) -> Optional[EventHandler]:
        actor_location_x = self.entity.x
        actor_location_y = self.entity.y
        inventory = self.entity.inventory

        for item in self.engine.game_map.items:
            if actor_location_x == item.x and actor_location_y == item.y:
                if len(inventory.items) >= inventory.capacity:
                    raise exceptions.Impossible(self.engine.translation.translate("inventory_full"))

                self.engine.game_map.entities.remove(item)
                item.parent = self.entity.inventory
                inventory.items.append(item)

                self.engine.message_log.add_message(self.engine.translation.translate("pick_item", item_name=item.name))
                
                # TODO: Check for win condition.
                if item.yendor:
                    self.engine.amulet_picked = True
                    
                return

        raise exceptions.Impossible(self.engine.translation.translate("nothing_to_pick"))
        

class ItemAction(Action):
    def __init__(
        self,
        entity: Actor,
        item: Item,
        target_xy: Optional[Tuple[int, int]] = None
    ):
        super().__init__(entity)
        self.item = item
        if not target_xy:
            target_xy = entity.x, entity.y
        self.target_xy = target_xy

    @property
    def target_actor(self) -> Optional[Actor]:
        """Return the actor at this actions destination."""
        return self.engine.game_map.get_actor_at_location(*self.target_xy)
    
    def perform(self) -> None:
        """Invoke the items ability, this action will be given to provide context."""
        if self.item.consumable:
            self.item.consumable.activate(self)
        
    
class DropItem(ItemAction):
    def perform(self) -> None:
        if self.entity.equipment.item_is_equipped(self.item):
            self.entity.equipment.toggle_equip(self.item)
            
        self.entity.inventory.drop(self.item)


class EquipAction(Action):
    def __init__(self, entity: Actor, item: Item):
        super().__init__(entity)

        self.item = item

    def perform(self) -> None:
        self.entity.equipment.toggle_equip(self.item)
        
    
class WaitAction(Action):
    def perform(self) -> None:
        pass


class TakeStairsAction(Action):
    def perform(self) -> None:
        """
        Take the stairs, if any exist at the entity's location.
        """
        if (self.entity.x, self.entity.y) == self.engine.game_map.downstairs_location:
            self.engine.game_world.generate_floor()
            self.engine.message_log.add_message(
                self.engine.translation.translate("descend"), color.descend
            )
        else:
            raise exceptions.Impossible(self.engine.translation.translate("no_stairs"))
        

class ActionWithDirection(Action):
    def __init__(self, entity: Actor, dx: int, dy: int):
        super().__init__(entity)

        self.dx = dx
        self.dy = dy

    @property
    def dest_xy(self) -> Tuple[int, int]:
        """Returns this actions destination."""
        return self.entity.x + self.dx, self.entity.y + self.dy
    

    @property
    def blocking_entity(self) -> Optional[Entity]:
        """Returns the blocking entity at this actions destination."""
        return self.engine.game_map.get_blocking_entity_at_location(*self.dest_xy)
    

    @property
    def target_actor(self) -> Optional[Actor]:
        """Return the actor at this actions destination."""
        return self.engine.game_map.get_actor_at_location(*self.dest_xy)


    def perform(self) -> None:
        raise NotImplementedError()


class BumpAction(ActionWithDirection):
    def perform(self) -> None:
        if self.target_actor:
            return MeleeAction(self.entity, self.dx, self.dy).perform()
        else:
            return MovementAction(self.entity, self.dx, self.dy).perform()

         

class MeleeAction(ActionWithDirection):
    def perform(self) -> None:
        target = self.target_actor

        if not target or target == self:
            raise exceptions.Impossible(self.engine.translation.translate("nothing_to_attack"))
        
        damage = self.entity.fighter.power - target.fighter.defense

        attack_desc = self.engine.translation.translate("attack_desc", entity=self.entity.name.capitalize(), target=target.name)
        
        if self.entity is self.engine.player:
            attack_color = color.player_atk
        else:
            attack_color = color.enemy_atk

        if damage > 0:
            self.engine.message_log.add_message(
                self.engine.translation.translate("attack_hit", attack_desc=attack_desc, damage=damage), attack_color
            )
            target.fighter.hp -= damage
        else:
            self.engine.message_log.add_message(
                self.engine.translation.translate("attack_dodge", attack_desc=attack_desc), attack_color
            )


class MovementAction(ActionWithDirection):
    def perform(self) -> None:
        dest_x, dest_y = self.dest_xy

        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            # Destination is out of bounds.
            raise exceptions.Impossible(self.engine.translation.translate("way_blocked"))
        if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
            # Destination is blocked by a tile.
            raise exceptions.Impossible(self.engine.translation.translate("way_blocked"))
        if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            # Destination is blocked by entity.
            raise exceptions.Impossible(self.engine.translation.translate("way_blocked"))

        self.entity.move(self.dx, self.dy)
