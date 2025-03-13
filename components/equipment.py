from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from components.base_component import BaseComponent
from scripts.equipment_types import EquipmentType

if TYPE_CHECKING:
    from scripts.entity import Actor, Item


class Equipment(BaseComponent):
    parent: Actor

    def __init__(
        self,
        weapon: Optional[Item] = None,
        armor: Optional[Item] = None,
        ring: Optional[Item] = None,
    ):
        self.weapon = weapon
        self.armor = armor
        self.ring = ring

    @property
    def defense_bonus(self) -> int:
        bonus = 0

        if self.weapon is not None and self.weapon.equippable is not None:
            bonus += self.weapon.equippable.defense_bonus

        if self.armor is not None and self.armor.equippable is not None:
            bonus += self.armor.equippable.defense_bonus

        if self.ring is not None and self.ring.equippable is not None:
            bonus += self.ring.equippable.defense_bonus

        return bonus
    
    @property
    def power_bonus(self) -> int:
        bonus = 0

        if self.weapon is not None and self.weapon.equippable is not None:
            bonus += self.weapon.equippable.power_bonus

        if self.armor is not None and self.armor.equippable is not None:
            bonus += self.armor.equippable.power_bonus

        if self.ring is not None and self.ring.equippable is not None:
            bonus += self.ring.equippable.power_bonus

        return bonus
    
    def item_is_equipped(self, item: Item) -> bool:
        return self.weapon == item or self.armor == item or self.ring == item
    
    def unequip_message(self, item_name: str) -> None:
        self.parent.gamemap.engine.message_log.add_message(
            self.parent.gamemap.engine.translation.translate("unequip_message", item_name=item_name)
        )

    def equip_message(self, item_name: str) -> None:
        self.parent.gamemap.engine.message_log.add_message(
            self.parent.gamemap.engine.translation.translate("equip_message", item_name=item_name)
        )

    def equip_to_slot(self, slot: str, item: Item, add_message: bool) -> None:
        current_item = getattr(self, slot)

        if current_item is not None:
            self.unequip_from_slot(slot, add_message)

        setattr(self, slot, item)

        if add_message:
            self.equip_message(item.name)

    def unequip_from_slot(self, slot: str, add_message: bool) -> None:
        current_item = getattr(self, slot)

        if add_message:
            self.unequip_message(current_item.name)

        setattr(self, slot, None)

    def toggle_equip(
        self,
        equippable_item: Item,
        add_message: bool = True,
    ) -> None:
        if (
            equippable_item.equippable
            and equippable_item.equippable.equipment_type in EquipmentType
        ):
            match equippable_item.equippable.equipment_type:
                case EquipmentType.WEAPON:
                    slot = "weapon"
                case EquipmentType.ARMOR:
                    slot = "armor"
                case EquipmentType.RING:
                    slot = "ring"
        

        if getattr(self, slot) == equippable_item:
            self.unequip_from_slot(slot, add_message)
        else:
            self.equip_to_slot(slot, equippable_item, add_message)