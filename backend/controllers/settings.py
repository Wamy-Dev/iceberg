from copy import copy
from typing import Any, List

from fastapi import APIRouter, HTTPException
from program.settings.manager import settings_manager
from pydantic import BaseModel


class SetSettings(BaseModel):
    key: str
    value: Any


router = APIRouter(
    prefix="/settings",
    tags=["settings"],
    responses={404: {"description": "Not found"}},
)


@router.get("/load")
async def load_settings():
    settings_manager.load()
    return {
        "success": True,
        "message": "Settings loaded!",
    }


@router.post("/save")
async def save_settings():
    settings_manager.save()
    return {
        "success": True,
        "message": "Settings saved!",
    }


@router.get("/get/all")
async def get_all_settings():
    return {
        "success": True,
        "data": copy(settings_manager.settings),
    }


@router.get("/get/{paths}")
async def get_settings(paths: str):
    current_settings = settings_manager.settings.dict()
    data = {}
    for path in paths.split(","):
        keys = path.split(".")
        current_obj = current_settings

        for k in keys:
            if k not in current_obj:
                return None
            current_obj = current_obj[k]

        data[path] = current_obj

    return {
        "success": True,
        "data": data,
    }


@router.post("/set")
async def set_settings(settings: List[SetSettings]):
    current_settings = settings_manager.settings.dict()

    for setting in settings:
        keys = setting.key.split(".")
        current_obj = current_settings

        # Navigate to the last key's parent object, similar to the getter.
        for k in keys[:-1]:
            if k not in current_obj:
                # If a key in the path does not exist, raise an exception or optionally create a new dict.
                raise HTTPException(
                    status_code=400,
                    detail=f"Path '{'.'.join(keys[:-1])}' does not exist.",
                )
            current_obj = current_obj[k]

        # Set the value at the final key.
        if keys[-1] in current_obj:
            current_obj[keys[-1]] = setting.value
        else:
            # If the final key does not exist, raise an exception.
            raise HTTPException(
                status_code=400,
                detail=f"Key '{keys[-1]}' does not exist in path '{'.'.join(keys[:-1])}'.",
            )

    settings_manager.load(settings_dict=current_settings)

    return {"success": True, "message": "Settings updated successfully."}
