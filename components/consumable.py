from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import scripts.actions as actions
import scripts.color as color

import components.ai
import components.inventory
from components.base_component import BaseComponent

from scripts.exceptions import Impossible
from scripts.input_handlers import (
    ActionOrHandler,
    AreaRangedAttackHandler,
    SingleRangedAttackHandler,
)


if TYPE_CHECKING:
    from scripts.entity import Actor, Item


class Consumable(BaseComponent):
    parent: Item

    def get_action(self, consumer: Actor) -> Optional[ActionOrHandler]:
        """Try to return the action for this item."""
        return actions.ItemAction(consumer, self.parent)
    
    def activate(self, action: actions.ItemAction) -> None:
        """
        Invoke this items ability.

        `action` is the context for this activation.
        """
        raise NotImplementedError()
    
    def consume(self) -> None:
        """Remove the consumed item from its containing inventory."""
        entity = self.parent
        inventory = entity.parent
        if isinstance(inventory, components.inventory.Inventory):
            inventory.items.remove(entity)
    

class ConfusionConsumable(Consumable):
    def __init__(self, number_of_turns: int):
        self.number_of_turns = number_of_turns

    def get_action(self, consumer: Actor) -> SingleRangedAttackHandler:
        self.engine.message_log.add_message(
            self.engine.translation.translate("select_location"), color.needs_target
        )
        return SingleRangedAttackHandler(
            self.engine,
            callback=lambda xy: actions.ItemAction(consumer, self.parent, xy)
        )
    
    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        target = action.target_actor

        if not self.engine.game_map.visible[action.target_xy]:
            raise Impossible(self.engine.translation.translate("must_target_visible"))
        if not target:
            raise Impossible(self.engine.translation.translate("must_target_enemy"))
        if target is consumer:
            raise Impossible(self.engine.translation.translate("must_not_target_self"))
        
        self.engine.message_log.add_message(
            self.engine.translation.translate("confusion_message", target=target.name),
            color.status_effect_applied,
        )

        target.ai = components.ai.ConfusedEnemy(
            entity=target, previous_ai=target.ai, turns_remaining=self.number_of_turns
        )
        self.consume()

        
class HealingConsumable(Consumable):
    def __init__(self, amount: int):
        self.amount = amount

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        amount_recovered = consumer.fighter.heal(self.amount)

        if amount_recovered > 0:
            self.engine.message_log.add_message(
                self.engine.translation.translate("healing_consumable", amount_recovered=amount_recovered, item=self.parent.name)
            )
            self.consume()
        else:
            raise Impossible(self.engine.translation.translate("full_hp"))
        

class FireballDamageConsumable(Consumable):
    def __init__(self, damage: int, radius: int):
        self.damage = damage
        self.radius = radius

    def get_action(self, consumer: Actor) -> AreaRangedAttackHandler:
        self.engine.message_log.add_message(
            self.engine.translation.translate("select_location"), color.needs_target
        )
        return AreaRangedAttackHandler(
            self.engine,
            radius=self.radius,
            callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),
        )
    
    def activate(self, action: actions.ItemAction) -> None:
        target_xy = action.target_xy

        if not self.engine.game_map.visible[target_xy]:
            raise Impossible(self.engine.translation.translate("must_target_visible"))
        
        targets_hit = False
        for actor in self.engine.game_map.actors:
            if actor.distance(*target_xy) <= self.radius:
                self.engine.message_log.add_message(
                    self.engine.translation.translate("fireball_message", target=actor.name, damage=self.damage)
                )
                actor.fighter.take_damage(self.damage)
                targets_hit = True

        if not targets_hit:
            raise Impossible(self.engine.translation.translate("no_targets"))
        self.consume()


class LightningDamageConsumable(Consumable):
    def __init__(self, damage: int, maximum_range: int) -> None:
        self.damage = damage
        self.maximum_range = maximum_range

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        target = None
        closest_distance = self.maximum_range + 1.0

        for actor in self.engine.game_map.actors:
            if actor is not consumer and self.parent.gamemap.visible[actor.x, actor.y]:
                distance = consumer.distance(actor.x, actor.y)

                if distance < closest_distance:
                    target = actor
                    closest_distance = distance

        if target:
            self.engine.message_log.add_message(
                self.engine.translation.translate("lightning_message", target=target.name, damage=self.damage)
            )
            target.fighter.take_damage(self.damage)
            self.consume()
        else:
            raise Impossible(self.engine.translation.translate("no_close_enemy"))