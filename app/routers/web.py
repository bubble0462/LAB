from __future__ import annotations

from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import PROJECT_ROOT, settings
from app.dependencies import get_db_session
from app.services import category_service, item_service


router = APIRouter()
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "app" / "templates"))


def set_flash(request: Request, level: str, message: str) -> None:
    request.session["flash"] = {
        "level": level,
        "message": message,
    }


def pop_flash(request: Request) -> dict | None:
    return request.session.pop("flash", None)


def render_page(
    request: Request,
    template_name: str,
    context: dict | None = None,
    *,
    status_code: int = status.HTTP_200_OK,
) -> HTMLResponse:
    context = context or {}
    context.update(
        {
            "request": request,
            "app_title": settings.project_name,
            "flash": pop_flash(request),
        }
    )
    return templates.TemplateResponse(template_name, context, status_code=status_code)


def normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def parse_positive_int(value: str | None, default: int | None = None) -> int | None:
    if value is None:
        return default

    cleaned = value.strip()
    if cleaned == "":
        return default

    try:
        parsed = int(cleaned)
    except ValueError:
        return default

    return parsed if parsed >= 0 else default


def build_filter_query(search_keyword: str, category_id: int | None, page_size: int) -> str:
    params = {}
    if search_keyword.strip():
        params["q"] = search_keyword.strip()
    if category_id is not None:
        params["category_id"] = category_id
    if page_size > 0:
        params["page_size"] = page_size
    return urlencode(params)


def item_to_form_data(item=None) -> dict:
    if item is None:
        return {
            "name": "",
            "model": "",
            "category_id": "",
            "quantity": "0",
            "key_specifications": "",
            "function_description": "",
            "remarks": "",
            "location": "",
        }

    return {
        "name": item.name or "",
        "model": item.model or "",
        "category_id": str(item.category_id),
        "quantity": str(item.quantity),
        "key_specifications": item.key_specifications or "",
        "function_description": item.function_description or "",
        "remarks": item.remarks or "",
        "location": item.location or "",
    }


def category_to_form_data(category=None) -> dict:
    if category is None:
        return {
            "name": "",
            "description": "",
        }

    return {
        "name": category.name or "",
        "description": category.description or "",
    }


async def parse_item_form(request: Request, session: Session) -> tuple[dict, dict, list[str]]:
    form = await request.form()
    form_data = {
        "name": (form.get("name") or "").strip(),
        "model": (form.get("model") or "").strip(),
        "category_id": (form.get("category_id") or "").strip(),
        "quantity": (form.get("quantity") or "").strip(),
        "key_specifications": (form.get("key_specifications") or "").strip(),
        "function_description": (form.get("function_description") or "").strip(),
        "remarks": (form.get("remarks") or "").strip(),
        "location": (form.get("location") or "").strip(),
    }

    errors = []
    if not form_data["name"]:
        errors.append("名称不能为空。")
    if not form_data["model"]:
        errors.append("型号不能为空。")
    if not form_data["category_id"]:
        errors.append("请选择分类。")

    quantity = parse_positive_int(form_data["quantity"])
    if quantity is None:
        errors.append("数量必须是大于等于 0 的整数。")

    category_id = parse_positive_int(form_data["category_id"])
    category = None
    if category_id is None:
        errors.append("分类选择无效。")
    else:
        category = category_service.get_category(session, category_id)
        if category is None:
            errors.append("所选分类不存在，请重新选择。")

    cleaned_data = {
        "name": form_data["name"],
        "model": form_data["model"],
        "category_id": category.id if category else 0,
        "quantity": quantity or 0,
        "key_specifications": normalize_optional_text(form_data["key_specifications"]),
        "function_description": normalize_optional_text(form_data["function_description"]),
        "remarks": normalize_optional_text(form_data["remarks"]),
        "location": normalize_optional_text(form_data["location"]),
    }
    return cleaned_data, form_data, errors


async def parse_category_form(request: Request) -> tuple[dict, list[str]]:
    form = await request.form()
    form_data = {
        "name": (form.get("name") or "").strip(),
        "description": (form.get("description") or "").strip(),
    }

    errors = []
    if not form_data["name"]:
        errors.append("分类名称不能为空。")

    return form_data, errors


def not_found_page(request: Request, message: str) -> HTMLResponse:
    return render_page(
        request,
        "error.html",
        {
            "title": "未找到内容",
            "message": message,
        },
        status_code=status.HTTP_404_NOT_FOUND,
    )


@router.get("/", name="home")
def home() -> RedirectResponse:
    return RedirectResponse(url="/items", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/items", response_class=HTMLResponse, name="item_list")
def item_list(
    request: Request,
    q: str = "",
    category_id: str | None = None,
    page: str = "1",
    page_size: str | None = None,
    session: Session = Depends(get_db_session),
) -> HTMLResponse:
    page_size_options = [10, 20, 50, 100]
    parsed_category_id = parse_positive_int(category_id)
    parsed_page = parse_positive_int(page, default=1) or 1
    parsed_page_size = parse_positive_int(page_size, default=settings.default_page_size) or settings.default_page_size
    if parsed_page_size not in page_size_options:
        parsed_page_size = settings.default_page_size

    pagination = item_service.list_items(
        session,
        search_keyword=q,
        category_id=parsed_category_id,
        page=parsed_page,
        page_size=parsed_page_size,
    )
    categories = category_service.list_categories(session)
    filter_query = build_filter_query(q, parsed_category_id, parsed_page_size)

    return render_page(
        request,
        "items/list.html",
        {
            "section": "items",
            "title": "器件列表",
            "items": pagination["items"],
            "categories": categories,
            "search_keyword": q.strip(),
            "selected_category_id": parsed_category_id,
            "pagination": pagination,
            "filter_query": filter_query,
            "page_size_options": page_size_options,
        },
    )


@router.get("/items/new", response_class=HTMLResponse, name="item_new")
def item_new(request: Request, session: Session = Depends(get_db_session)) -> HTMLResponse:
    categories = category_service.list_categories(session)
    return render_page(
        request,
        "items/form.html",
        {
            "section": "items",
            "title": "新增器件",
            "page_heading": "新增器件",
            "submit_label": "保存器件",
            "form_action": request.url_for("item_create"),
            "categories": categories,
            "form_data": item_to_form_data(),
            "errors": [],
        },
    )


@router.post("/items/new", name="item_create")
async def item_create(request: Request, session: Session = Depends(get_db_session)) -> Response:
    cleaned_data, form_data, errors = await parse_item_form(request, session)
    categories = category_service.list_categories(session)

    if errors:
        return render_page(
            request,
            "items/form.html",
            {
                "section": "items",
                "title": "新增器件",
                "page_heading": "新增器件",
                "submit_label": "保存器件",
                "form_action": request.url_for("item_create"),
                "categories": categories,
                "form_data": form_data,
                "errors": errors,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    item = item_service.create_item(session, cleaned_data)
    set_flash(request, "success", "器件已成功新增。")
    return RedirectResponse(
        url=request.url_for("item_detail", item_id=item.id),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/items/{item_id}", response_class=HTMLResponse, name="item_detail")
def item_detail(item_id: int, request: Request, session: Session = Depends(get_db_session)) -> HTMLResponse:
    item = item_service.get_item(session, item_id)
    if item is None:
        return not_found_page(request, "没有找到对应的器件记录。")

    return render_page(
        request,
        "items/detail.html",
        {
            "section": "items",
            "title": f"器件详情 - {item.name}",
            "item": item,
        },
    )


@router.get("/items/{item_id}/edit", response_class=HTMLResponse, name="item_edit_page")
def item_edit_page(item_id: int, request: Request, session: Session = Depends(get_db_session)) -> HTMLResponse:
    item = item_service.get_item(session, item_id)
    if item is None:
        return not_found_page(request, "没有找到需要编辑的器件记录。")

    categories = category_service.list_categories(session)
    return render_page(
        request,
        "items/form.html",
        {
            "section": "items",
            "title": f"编辑器件 - {item.name}",
            "page_heading": "编辑器件",
            "submit_label": "保存修改",
            "form_action": request.url_for("item_edit", item_id=item.id),
            "categories": categories,
            "form_data": item_to_form_data(item),
            "errors": [],
            "item": item,
        },
    )


@router.post("/items/{item_id}/edit", name="item_edit")
async def item_edit(item_id: int, request: Request, session: Session = Depends(get_db_session)) -> Response:
    item = item_service.get_item(session, item_id)
    if item is None:
        return not_found_page(request, "没有找到需要编辑的器件记录。")

    cleaned_data, form_data, errors = await parse_item_form(request, session)
    categories = category_service.list_categories(session)
    if errors:
        return render_page(
            request,
            "items/form.html",
            {
                "section": "items",
                "title": f"编辑器件 - {item.name}",
                "page_heading": "编辑器件",
                "submit_label": "保存修改",
                "form_action": request.url_for("item_edit", item_id=item.id),
                "categories": categories,
                "form_data": form_data,
                "errors": errors,
                "item": item,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    item_service.update_item(session, item, cleaned_data)
    set_flash(request, "success", "器件信息已更新。")
    return RedirectResponse(
        url=request.url_for("item_detail", item_id=item.id),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/items/{item_id}/delete", name="item_delete")
def item_delete(item_id: int, request: Request, session: Session = Depends(get_db_session)) -> RedirectResponse:
    item = item_service.get_item(session, item_id)
    if item is None:
        set_flash(request, "danger", "器件不存在，可能已经被其他人删除。")
        return RedirectResponse(url=request.url_for("item_list"), status_code=status.HTTP_303_SEE_OTHER)

    item_service.delete_item(session, item)
    set_flash(request, "success", "器件已删除。")
    return RedirectResponse(url=request.url_for("item_list"), status_code=status.HTTP_303_SEE_OTHER)


@router.get("/categories", response_class=HTMLResponse, name="category_list")
def category_list(request: Request, session: Session = Depends(get_db_session)) -> HTMLResponse:
    categories = category_service.list_categories_with_item_counts(session)
    return render_page(
        request,
        "categories/list.html",
        {
            "section": "categories",
            "title": "分类管理",
            "categories": categories,
        },
    )


@router.get("/categories/new", response_class=HTMLResponse, name="category_new")
def category_new(request: Request) -> HTMLResponse:
    return render_page(
        request,
        "categories/form.html",
        {
            "section": "categories",
            "title": "新增分类",
            "page_heading": "新增分类",
            "submit_label": "保存分类",
            "form_action": request.url_for("category_create"),
            "form_data": category_to_form_data(),
            "errors": [],
        },
    )


@router.post("/categories/new", name="category_create")
async def category_create(request: Request, session: Session = Depends(get_db_session)) -> Response:
    form_data, errors = await parse_category_form(request)
    if category_service.is_category_name_taken(session, form_data["name"]):
        errors.append("分类名称已存在，请换一个名称。")

    if errors:
        return render_page(
            request,
            "categories/form.html",
            {
                "section": "categories",
                "title": "新增分类",
                "page_heading": "新增分类",
                "submit_label": "保存分类",
                "form_action": request.url_for("category_create"),
                "form_data": form_data,
                "errors": errors,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    category_service.create_category(session, form_data["name"], normalize_optional_text(form_data["description"]))
    set_flash(request, "success", "分类已新增。")
    return RedirectResponse(url=request.url_for("category_list"), status_code=status.HTTP_303_SEE_OTHER)


@router.get("/categories/{category_id}/edit", response_class=HTMLResponse, name="category_edit_page")
def category_edit_page(category_id: int, request: Request, session: Session = Depends(get_db_session)) -> HTMLResponse:
    category = category_service.get_category(session, category_id)
    if category is None:
        return not_found_page(request, "没有找到需要编辑的分类记录。")

    return render_page(
        request,
        "categories/form.html",
        {
            "section": "categories",
            "title": f"编辑分类 - {category.name}",
            "page_heading": "编辑分类",
            "submit_label": "保存修改",
            "form_action": request.url_for("category_edit", category_id=category.id),
            "form_data": category_to_form_data(category),
            "errors": [],
            "category": category,
        },
    )


@router.post("/categories/{category_id}/edit", name="category_edit")
async def category_edit(category_id: int, request: Request, session: Session = Depends(get_db_session)) -> Response:
    category = category_service.get_category(session, category_id)
    if category is None:
        return not_found_page(request, "没有找到需要编辑的分类记录。")

    form_data, errors = await parse_category_form(request)
    if category_service.is_category_name_taken(session, form_data["name"], exclude_category_id=category.id):
        errors.append("分类名称已存在，请换一个名称。")

    if errors:
        return render_page(
            request,
            "categories/form.html",
            {
                "section": "categories",
                "title": f"编辑分类 - {category.name}",
                "page_heading": "编辑分类",
                "submit_label": "保存修改",
                "form_action": request.url_for("category_edit", category_id=category.id),
                "form_data": form_data,
                "errors": errors,
                "category": category,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    category_service.update_category(session, category, form_data["name"], normalize_optional_text(form_data["description"]))
    set_flash(request, "success", "分类信息已更新。")
    return RedirectResponse(url=request.url_for("category_list"), status_code=status.HTTP_303_SEE_OTHER)


@router.post("/categories/{category_id}/delete", name="category_delete")
def category_delete(category_id: int, request: Request, session: Session = Depends(get_db_session)) -> RedirectResponse:
    category = category_service.get_category(session, category_id)
    if category is None:
        set_flash(request, "danger", "分类不存在，可能已经被其他人删除。")
        return RedirectResponse(url=request.url_for("category_list"), status_code=status.HTTP_303_SEE_OTHER)

    try:
        category_service.delete_category(session, category)
        set_flash(request, "success", "分类已删除。")
    except ValueError as exc:
        set_flash(request, "danger", str(exc))

    return RedirectResponse(url=request.url_for("category_list"), status_code=status.HTTP_303_SEE_OTHER)
