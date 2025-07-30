from typing import List, Tuple, Dict, Any
import json
from app.services.room_service import room_service


def populate_building_choices(include_all_option: bool = False) -> List[Tuple[int, str]]:
    """
    Populate building choices for SelectField
    
    Args:
        include_all_option: If True, adds (0, "Tất cả") as first option
        
    Returns:
        List of tuples (building_id, building_name)
    """
    try:
        buildings_data = room_service.get_buildings()
        buildings = buildings_data.get("buildings", [])
        choices = [(b["building_id"], b["building_name"]) for b in buildings]
        
        if include_all_option:
            choices = [(0, "Tất cả")] + choices
            
        return choices
    except Exception:
        return [(0, "Tất cả")] if include_all_option else []


def populate_room_type_choices(include_all_option: bool = False) -> List[Tuple[int, str]]:
    """
    Populate room type choices for SelectField
    
    Args:
        include_all_option: If True, adds (0, "Tất cả") as first option
        
    Returns:
        List of tuples (room_type_id, type_name)
    """
    try:
        room_types_data = room_service.get_room_types()
        room_types = room_types_data.get("room_types", [])
        choices = [(rt["room_type_id"], rt["type_name"]) for rt in room_types]
        
        if include_all_option:
            choices = [(0, "Tất cả")] + choices
            
        return choices
    except Exception:
        return [(0, "Tất cả")] if include_all_option else []


def populate_room_form_choices(form) -> None:
    """
    Populate building and room_type choices for RoomForm
    
    Args:
        form: RoomForm instance
    """
    form.building_id.choices = populate_building_choices()
    form.room_type_id.choices = populate_room_type_choices()


def populate_room_search_form_choices(form) -> None:
    """
    Populate building and room_type choices for RoomSearchForm
    
    Args:
        form: RoomSearchForm instance
    """
    form.building_id.choices = populate_building_choices(include_all_option=True)
    form.room_type_id.choices = populate_room_type_choices(include_all_option=True)
