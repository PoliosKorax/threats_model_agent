"""Wizard endpoints для пошагового опроса."""

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.api.dependencies import get_db
from app.models.schemas import SystemProfile, ViolatorProfile, UserProfile
from app.db.queries import get_all_objects

router = APIRouter(prefix="/api/wizard", tags=["wizard"])


@router.get("/", response_class=HTMLResponse)
async def wizard_home(request: Request):
    """Главная страница wizard."""
    return request.app.templates.TemplateResponse(
        "wizard/step1_system.html",
        {"request": request, "step": 1}
    )


@router.post("/step1", response_class=HTMLResponse)
async def wizard_step1(request: Request, db: AsyncSession = Depends(get_db)):
    """Шаг 1: О системе - обработка и переход к шагу 2."""
    form_data = await request.form()
    
    # Сохраняем в сессии
    if "user_profile" not in request.session:
        request.session["user_profile"] = {}
    
    system_profile = {
        "processes_pd": form_data.get("processes_pd") == "on",
        "pd_security_level": int(form_data.get("pd_security_level")) if form_data.get("pd_security_level") else None,
        "uses_cloud": form_data.get("uses_cloud") == "on",
        "uses_virtualization": form_data.get("uses_virtualization") == "on",
        "external_responsibility": form_data.get("external_responsibility"),
        "uses_grid": form_data.get("uses_grid") == "on",
        "uses_ics": form_data.get("uses_ics") == "on",
        "uses_mobile": form_data.get("uses_mobile") == "on",
        "uses_docker": form_data.get("uses_docker") == "on",
        "uses_wifi": form_data.get("uses_wifi") == "on",
        "has_internet_access": form_data.get("has_internet_access") == "on",
        "uses_l3vpn": form_data.get("uses_l3vpn") == "on",
        "uses_vipnet": form_data.get("uses_vipnet") == "on",
        "uses_removable_media": form_data.get("uses_removable_media") == "on",
        "uses_remote_desktop": form_data.get("uses_remote_desktop") == "on",
    }
    
    request.session["user_profile"]["system"] = system_profile
    request.session["user_profile"]["current_step"] = 2
    
    return request.app.templates.TemplateResponse(
        "wizard/step2_violators.html",
        {"request": request, "step": 2}
    )


@router.post("/step2", response_class=HTMLResponse)
async def wizard_step2(request: Request, db: AsyncSession = Depends(get_db)):
    """Шаг 2: Нарушители - обработка и переход к шагу 3."""
    form_data = await request.form()
    
    if "user_profile" not in request.session:
        raise HTTPException(status_code=400, detail="Session expired. Please start over.")
    
    violator_profile = {
        "external_types": form_data.getlist("external_types"),
        "external_level": form_data.get("external_level"),
        "internal_types": form_data.getlist("internal_types"),
        "internal_level": form_data.get("internal_level"),
    }
    
    request.session["user_profile"]["violators"] = violator_profile
    request.session["user_profile"]["current_step"] = 3
    
    return request.app.templates.TemplateResponse(
        "wizard/step3_interfaces.html",
        {"request": request, "step": 3}
    )


@router.post("/step3", response_class=HTMLResponse)
async def wizard_step3(request: Request, db: AsyncSession = Depends(get_db)):
    """Шаг 3: Интерфейсы - обработка и переход к шагу 4."""
    form_data = await request.form()
    
    if "user_profile" not in request.session:
        raise HTTPException(status_code=400, detail="Session expired. Please start over.")
    
    interfaces = form_data.getlist("interfaces")
    request.session["user_profile"]["interfaces"] = interfaces
    request.session["user_profile"]["current_step"] = 4
    
    # Получаем объекты для шага 4
    objects = await get_all_objects(db)
    
    return request.app.templates.TemplateResponse(
        "wizard/step4_objects.html",
        {"request": request, "step": 4, "objects": objects}
    )


@router.post("/step4", response_class=HTMLResponse)
async def wizard_step4(request: Request, db: AsyncSession = Depends(get_db)):
    """Шаг 4: Объекты - обработка и переход к шагу 5."""
    form_data = await request.form()
    
    if "user_profile" not in request.session:
        raise HTTPException(status_code=400, detail="Session expired. Please start over.")
    
    selected_objects = form_data.getlist("selected_objects")
    request.session["user_profile"]["selected_objects"] = selected_objects
    request.session["user_profile"]["current_step"] = 5
    
    # Переходим к генерации отчёта (шаг 5)
    return request.app.templates.TemplateResponse(
        "wizard/step5_report.html",
        {"request": request, "step": 5}
    )


@router.get("/step/{step_number}", response_class=HTMLResponse)
async def wizard_get_step(request: Request, step_number: int):
    """Получить конкретный шаг wizard (для навигации назад)."""
    if step_number < 1 or step_number > 5:
        raise HTTPException(status_code=400, detail="Invalid step number")
    
    template_map = {
        1: "wizard/step1_system.html",
        2: "wizard/step2_violators.html",
        3: "wizard/step3_interfaces.html",
        4: "wizard/step4_objects.html",
        5: "wizard/step5_report.html",
    }
    
    if "user_profile" not in request.session:
        request.session["user_profile"] = {"current_step": step_number}
    else:
        request.session["user_profile"]["current_step"] = step_number
    
    return request.app.templates.TemplateResponse(
        template_map[step_number],
        {"request": request, "step": step_number}
    )
