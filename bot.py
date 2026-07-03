import asyncio
import hashlib
import json
import os
import random
import re
from pathlib import Path
from typing import Any, Callable

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
RECIPES_PATH = BASE_DIR / "recipes.json"
PLACES_PATH = BASE_DIR / "places.json"
FAVORITES_PATH = BASE_DIR / "favorites.json"
SETTINGS_PATH = BASE_DIR / "settings.json"

COOKING_BUTTON = "🍳 рецепты"
PLACES_BUTTON = "📍 места"
FAVORITES_BUTTON = "⭐ любимое"
ADMIN_BUTTON = "⚙️ админка"
BACK_BUTTON = "⬅️ назад"

DAD_BUTTON = "🥚 папины омлеты"
RANDOM_BUTTON = "🎲 рандомный рецепт"
SEARCH_BUTTON = "🔎 найти рецепт"
ALL_BUTTON = "📚 все рецепты"
RECIPE_FAVORITES_BUTTON = "⭐ любимые рецепты"

ALL_PLACES_BUTTON = "📚 все места"
PLACE_SEARCH_BUTTON = "🔎 найти место"
RANDOM_PLACE_BUTTON = "🎲 куда сходить"
PLACE_FAVORITES_BUTTON = "⭐ любимые места"
VISITED_PLACES_BUTTON = "✅ где Аня была"
WISHLIST_PLACES_BUTTON = "📝 Аня хочет сходить"
DEFAULT_PLACES_MAP_URL = "https://yandex.ru/maps/?um=constructor%3A2d5f7ca17c7cad37b342c0a2d3038a5b02563b904e5dfdb3bb4034bbcaa2f8b4&source=constructorLink"

DAD_PASSWORD = "тома"
DAD_CLUSTER_LABELS = {
    "classic": "классика",
    "tender": "нежные",
    "cheese": "сырные",
    "hearty": "сытные",
    "vegetables": "овощные",
}
DAD_CLUSTER_ORDER = ["classic", "tender", "cheese", "hearty", "vegetables"]

PLACE_STATUS_LABELS = {
    "visited": "Аня была",
    "wishlist": "Аня хочет сходить",
}
PLACE_TYPE_LABELS = {
    "coffee": "кофе",
    "cafe": "кафе",
    "restaurant": "ресторан",
    "bar": "бар",
    "brunch": "завтрак / бранч",
    "kebab": "кебаб",
    "pizzeria": "пицца",
    "asian": "азиатское",
    "culture": "культурное",
    "record_store": "пластинки",
}
PLACE_TYPE_ALIASES = {
    "coffee": ["кофе", "кофейня", "кофейни", "капучино", "флэт", "латте"],
    "cafe": ["кафе", "посидеть", "поесть", "еда"],
    "restaurant": ["ресторан", "ресторанчик", "ужин", "поужинать"],
    "bar": ["бар", "коктейль", "коктейли", "вино", "выпить"],
    "brunch": ["бранч", "завтрак", "яйца", "eggs", "breakfast"],
    "kebab": ["кебаб", "шаурма", "кебабы"],
    "pizzeria": ["пицца", "пиццерия"],
    "asian": ["азиатское", "корея", "корейское", "китай", "китайское", "лапша"],
    "culture": ["культура", "культурное", "культурный"],
    "record_store": ["пластинки", "музыка", "record", "records"],
}
PLACE_RESULT_LIMIT = 10
RECIPE_RESULT_LIMIT = 10
BROAD_PLACE_QUERIES = {
    "места",
    "место",
    "заведения",
    "все места",
    "покажи места",
    "куда сходить",
    "куда пойти",
}

STOPWORDS = {
    "а",
    "без",
    "больше",
    "в",
    "во",
    "вот",
    "все",
    "всё",
    "выбери",
    "выше",
    "где",
    "давай",
    "для",
    "до",
    "есть",
    "из",
    "или",
    "как",
    "какая",
    "какое",
    "какой",
    "менее",
    "меньше",
    "мне",
    "можно",
    "на",
    "надо",
    "найди",
    "найти",
    "не",
    "нибудь",
    "ниже",
    "ну",
    "о",
    "от",
    "плиз",
    "по",
    "пожалуйста",
    "покажи",
    "посоветуй",
    "приготовить",
    "рандом",
    "рандомное",
    "рандомный",
    "рецепт",
    "рецепты",
    "с",
    "сам",
    "сама",
    "сегодня",
    "случайное",
    "случайный",
    "со",
    "то",
    "хочу",
    "что",
    "чтоб",
    "что-нибудь",
    "чтобы",
}

SMART_WORDS = {
    "белка",
    "белки",
    "белков",
    "белок",
    "бжу",
    "быстро",
    "быстрое",
    "быстрый",
    "жира",
    "жиры",
    "жирное",
    "калорий",
    "картинка",
    "картинкой",
    "ккал",
    "легкое",
    "лёгкое",
    "мин",
    "минут",
    "побыстрее",
    "пп",
    "сложное",
    "сложно",
    "углеводов",
    "углеводы",
    "фото",
}

PLACE_STOPWORDS = STOPWORDS | {
    "адрес",
    "была",
    "были",
    "вкусно",
    "заведение",
    "заведения",
    "карта",
    "куда",
    "любим",
    "любимое",
    "любимые",
    "любимый",
    "любимых",
    "места",
    "месте",
    "место",
    "метро",
    "отзыв",
    "отзывы",
    "сходить",
    "стоит",
}

PLACE_INTENT_WORDS = {
    "бар",
    "была",
    "заведение",
    "заведения",
    "кафе",
    "кофе",
    "кофейня",
    "куда",
    "места",
    "место",
    "метро",
    "ресторан",
    "сходить",
}

MACRO_ALIASES = {
    "calories": r"(?:ккал|калори[а-яё]*|калорийность)",
    "protein": r"(?:белк[а-яё]*|протеин[а-яё]*)",
    "fat": r"(?:жир[а-яё]*)",
    "carbs": r"(?:углевод[а-яё]*)",
}
MACRO_LABELS = {
    "calories": "ккал",
    "protein": "белки",
    "fat": "жиры",
    "carbs": "углеводы",
}
CATEGORY_ALIASES = {
    "завтрак": ["завтрак", "утро", "утром"],
    "ужин": ["ужин", "вечер", "вечером"],
    "паста": ["паста", "пасту", "макароны", "спагетти"],
}

router = Router()


class SearchState(StatesGroup):
    waiting_for_query = State()


class PlaceSearchState(StatesGroup):
    waiting_for_query = State()


class DadState(StatesGroup):
    waiting_for_password = State()


class AdminState(StatesGroup):
    waiting_for_place = State()
    waiting_for_map_url = State()
    waiting_for_place_photo = State()


def env_values(name: str, default: str = "") -> set[str]:
    raw = os.getenv(name, default)
    return {item.strip().casefold() for item in raw.split(",") if item.strip()}


def is_admin_user(user: Any) -> bool:
    if user is None:
        return False

    admin_ids = env_values("ADMIN_USER_IDS")
    if admin_ids and str(getattr(user, "id", "")) in admin_ids:
        return True

    usernames = env_values("ADMIN_USERNAMES", "shesocold,shesocccold")
    username = normalize(getattr(user, "username", ""))
    return bool(username and username in usernames)


def main_keyboard(user: Any = None) -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text=COOKING_BUTTON), KeyboardButton(text=PLACES_BUTTON)],
        [KeyboardButton(text=FAVORITES_BUTTON)],
    ]

    if is_admin_user(user):
        keyboard.append([KeyboardButton(text=ADMIN_BUTTON)])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="выбери, что хочешь",
    )


def cooking_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=DAD_BUTTON), KeyboardButton(text=RANDOM_BUTTON)],
            [KeyboardButton(text=SEARCH_BUTTON), KeyboardButton(text=ALL_BUTTON)],
            [KeyboardButton(text=RECIPE_FAVORITES_BUTTON), KeyboardButton(text=BACK_BUTTON)],
        ],
        resize_keyboard=True,
        input_field_placeholder="что сегодня делаем?",
    )


def places_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=ALL_PLACES_BUTTON), KeyboardButton(text=PLACE_SEARCH_BUTTON)],
            [KeyboardButton(text=RANDOM_PLACE_BUTTON), KeyboardButton(text=PLACE_FAVORITES_BUTTON)],
            [KeyboardButton(text=VISITED_PLACES_BUTTON), KeyboardButton(text=WISHLIST_PLACES_BUTTON)],
            [KeyboardButton(text=BACK_BUTTON)],
        ],
        resize_keyboard=True,
        input_field_placeholder="куда идём?",
    )


def all_menu_buttons() -> set[str]:
    return {
        COOKING_BUTTON,
        PLACES_BUTTON,
        FAVORITES_BUTTON,
        ADMIN_BUTTON,
        BACK_BUTTON,
        DAD_BUTTON,
        RANDOM_BUTTON,
        SEARCH_BUTTON,
        ALL_BUTTON,
        RECIPE_FAVORITES_BUTTON,
        ALL_PLACES_BUTTON,
        PLACE_SEARCH_BUTTON,
        RANDOM_PLACE_BUTTON,
        PLACE_FAVORITES_BUTTON,
        VISITED_PLACES_BUTTON,
        WISHLIST_PLACES_BUTTON,
    }


async def route_menu_button(message: Message, state: FSMContext, text: str) -> bool:
    if text not in all_menu_buttons():
        return False

    await state.set_state(None)

    if text == BACK_BUTTON:
        await handle_back(message, state)
    elif text == COOKING_BUTTON:
        await handle_cooking_home(message, state)
    elif text == PLACES_BUTTON:
        await handle_places_home(message, state)
    elif text == FAVORITES_BUTTON:
        await handle_favorites_home(message)
    elif text == ADMIN_BUTTON:
        await handle_admin_home(message, state)
    elif text == DAD_BUTTON:
        await handle_dad_gate(message, state)
    elif text == RANDOM_BUTTON:
        await handle_random_recipe(message, state)
    elif text == ALL_BUTTON:
        await handle_all_recipes(message, state)
    elif text == SEARCH_BUTTON:
        await handle_search_request(message, state)
    elif text == RECIPE_FAVORITES_BUTTON:
        await handle_recipe_favorites(message, state)
    elif text == ALL_PLACES_BUTTON:
        await handle_all_places(message)
    elif text == PLACE_SEARCH_BUTTON:
        await handle_place_search_request(message, state)
    elif text == RANDOM_PLACE_BUTTON:
        await handle_random_place(message)
    elif text == PLACE_FAVORITES_BUTTON:
        await handle_place_favorites(message)
    elif text == VISITED_PLACES_BUTTON:
        await handle_visited_places(message)
    elif text == WISHLIST_PLACES_BUTTON:
        await handle_wishlist_places(message)

    return True


def read_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback

    raw_text = path.read_text(encoding="utf-8").strip()
    if not raw_text:
        return fallback

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as error:
        print(f"не удалось прочитать {path.name}: {error}")
        return fallback


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_recipes() -> list[dict[str, Any]]:
    recipes = read_json(RECIPES_PATH, [])
    if not isinstance(recipes, list):
        print("recipes.json должен быть массивом рецептов")
        return []

    return [recipe for recipe in recipes if isinstance(recipe, dict)]


def load_places() -> list[dict[str, Any]]:
    places = read_json(PLACES_PATH, [])
    if not isinstance(places, list):
        print("places.json должен быть массивом мест")
        return []

    return [place for place in places if isinstance(place, dict)]


def save_places(places: list[dict[str, Any]]) -> None:
    write_json(PLACES_PATH, places)


def load_settings() -> dict[str, Any]:
    settings = read_json(SETTINGS_PATH, {})
    return settings if isinstance(settings, dict) else {}


def save_settings(settings: dict[str, Any]) -> None:
    write_json(SETTINGS_PATH, settings)


def places_map_url() -> str:
    return str(os.getenv("PLACES_MAP_URL") or load_settings().get("places_map_url") or DEFAULT_PLACES_MAP_URL)


def load_favorites() -> dict[str, dict[str, list[str]]]:
    favorites = read_json(FAVORITES_PATH, {})
    if not isinstance(favorites, dict):
        favorites = {}

    for kind in ("recipes", "places"):
        if not isinstance(favorites.get(kind), dict):
            favorites[kind] = {}

    return favorites


def normalize(value: Any) -> str:
    return str(value or "").casefold()


def compact_text(value: Any) -> str:
    return " ".join(re.findall(r"[a-zа-яё0-9]+", normalize(value)))


def words_from_text(text: str) -> list[str]:
    return re.findall(r"[a-zа-яё0-9]+", normalize(text))


def stem_word(word: str) -> str:
    word = normalize(word)
    endings = (
        "иями",
        "ями",
        "ами",
        "ого",
        "ему",
        "ому",
        "ыми",
        "ими",
        "ой",
        "ей",
        "ую",
        "юю",
        "ом",
        "ем",
        "ах",
        "ях",
        "ов",
        "ев",
        "а",
        "я",
        "ы",
        "и",
        "е",
        "у",
        "ю",
        "о",
    )

    for ending in endings:
        if len(word) - len(ending) >= 3 and word.endswith(ending):
            return word[: -len(ending)]

    return word


def item_id(item: dict[str, Any]) -> str:
    return normalize(item.get("id") or item.get("title"))


def user_key(user_id: int | None) -> str:
    return str(user_id or "unknown")


def favorite_ids(kind: str, user_id: int | None) -> set[str]:
    favorites = load_favorites()
    return set(favorites.get(kind, {}).get(user_key(user_id), []))


def is_favorite(kind: str, user_id: int | None, wanted_id: str) -> bool:
    return wanted_id in favorite_ids(kind, user_id)


def toggle_favorite(kind: str, user_id: int | None, wanted_id: str) -> bool:
    favorites = load_favorites()
    user = user_key(user_id)
    current = set(favorites[kind].get(user, []))

    if wanted_id in current:
        current.remove(wanted_id)
        is_added = False
    else:
        current.add(wanted_id)
        is_added = True

    favorites[kind][user] = sorted(current)
    write_json(FAVORITES_PATH, favorites)

    return is_added


def find_item(items: list[dict[str, Any]], wanted_id: str) -> dict[str, Any] | None:
    for item in items:
        if item_id(item) == wanted_id:
            return item

    return None


def is_dad_recipe(recipe: dict[str, Any]) -> bool:
    return recipe.get("is_for_dad") is True


def is_quick(recipe: dict[str, Any]) -> bool:
    time_minutes = recipe.get("time_minutes")
    tags = recipe.get("tags", [])
    has_quick_tag = isinstance(tags, list) and any(normalize(tag) == "быстро" for tag in tags)

    return time_minutes_is_at_most(time_minutes, 20) or has_quick_tag


def is_hard(recipe: dict[str, Any]) -> bool:
    time_minutes = recipe.get("time_minutes")
    tags = recipe.get("tags", [])
    has_hard_tag = isinstance(tags, list) and any(normalize(tag) == "сложно" for tag in tags)

    return time_minutes_is_at_least(time_minutes, 35) or has_hard_tag


def time_minutes_is_at_most(value: Any, limit: int) -> bool:
    try:
        return int(value) <= limit
    except (TypeError, ValueError):
        return False


def time_minutes_is_at_least(value: Any, limit: int) -> bool:
    try:
        return int(value) >= limit
    except (TypeError, ValueError):
        return False


async def has_dad_access(state: FSMContext) -> bool:
    data = await state.get_data()
    return data.get("dad_authorized") is True


async def visible_recipes(state: FSMContext) -> list[dict[str, Any]]:
    return [recipe for recipe in load_recipes() if not is_dad_recipe(recipe)]


def dad_recipes() -> list[dict[str, Any]]:
    return [recipe for recipe in load_recipes() if is_dad_recipe(recipe)]


def nutrition_value(recipe: dict[str, Any], key: str) -> float | None:
    nutrition = recipe.get("nutrition")
    if not isinstance(nutrition, dict):
        return None

    value = nutrition.get(key)
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def pretty_number(value: float | int | None) -> str:
    if value is None:
        return "?"

    if float(value).is_integer():
        return str(int(value))

    return str(value)


def format_nutrition(recipe: dict[str, Any]) -> str:
    calories = nutrition_value(recipe, "calories")
    protein = nutrition_value(recipe, "protein")
    fat = nutrition_value(recipe, "fat")
    carbs = nutrition_value(recipe, "carbs")

    if calories is None and protein is None and fat is None and carbs is None:
        return ""

    lines: list[str] = []
    if calories is not None:
        lines.append(f"ккал: примерно {pretty_number(calories)}")

    if protein is not None or fat is not None or carbs is not None:
        lines.append(
            "бжу: "
            f"{pretty_number(protein)} / {pretty_number(fat)} / {pretty_number(carbs)} г"
        )

    return "\n".join(lines)


def format_recipe(recipe: dict[str, Any]) -> str:
    title = recipe.get("title", "без названия")
    category = recipe.get("category", "не указана")
    time_minutes = recipe.get("time_minutes", "?")
    ingredients = recipe.get("ingredients", [])
    steps = recipe.get("steps", [])

    if not isinstance(ingredients, list):
        ingredients = []
    if not isinstance(steps, list):
        steps = []

    ingredients_text = "\n".join(f"— {item}" for item in ingredients)
    steps_text = "\n".join(f"{number}. {step}" for number, step in enumerate(steps, start=1))
    details = [
        f"категория: {category}",
        f"время: {time_minutes} мин",
    ]
    nutrition_text = format_nutrition(recipe)
    if nutrition_text:
        details.append(nutrition_text)

    details_text = "\n".join(details)

    return (
        f"🍳 {title}\n\n"
        f"{details_text}\n\n"
        f"ингредиенты:\n{ingredients_text or '— пока не записаны'}\n\n"
        f"как готовить:\n\n{steps_text or 'пока без шагов'}"
    )


def recipe_actions_keyboard(recipe: dict[str, Any], user_id: int | None) -> InlineKeyboardMarkup | None:
    if is_dad_recipe(recipe):
        return None

    wanted_id = item_id(recipe)
    text = "💔 убрать из любимых" if is_favorite("recipes", user_id, wanted_id) else "⭐ в любимые"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text, callback_data=f"recipe_fav:{wanted_id}")],
        ]
    )


async def send_recipe(message: Message, recipe: dict[str, Any], user_id: int | None = None) -> None:
    image = recipe.get("image")
    if isinstance(image, str) and image.strip():
        image_path = BASE_DIR / image
        if image_path.exists():
            await message.answer_photo(
                photo=FSInputFile(image_path),
                caption=str(recipe.get("title", "рецепт")),
            )

    await message.answer(format_recipe(recipe), reply_markup=recipe_actions_keyboard(recipe, user_id))


def recipe_search_text(recipe: dict[str, Any]) -> str:
    parts: list[str] = []

    for key in ("title", "category", "country"):
        value = recipe.get(key)
        if isinstance(value, str):
            parts.append(value)

    for key in ("tags", "ingredients", "steps"):
        value = recipe.get(key)
        if isinstance(value, list):
            parts.extend(str(item) for item in value)

    return compact_text(" ".join(parts))


def recipe_matches_term(recipe: dict[str, Any], term: str) -> bool:
    term = normalize(term).strip()
    if not term:
        return False

    haystack = recipe_search_text(recipe)
    stem = stem_word(term)

    return term in haystack or stem in haystack


def extract_excluded_terms(text: str) -> list[str]:
    terms: list[str] = []
    patterns = [
        r"(?:без|кроме)\s+([a-zа-яё]+(?:\s+и\s+[a-zа-яё]+)*)",
        r"не хочу\s+([a-zа-яё]+(?:\s+и\s+[a-zа-яё]+)*)",
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, normalize(text)):
            for part in re.split(r"\s+и\s+", match.group(1)):
                word = part.strip()
                if word and word not in STOPWORDS:
                    terms.append(word)

    return terms


def extract_category(text: str, recipes: list[dict[str, Any]]) -> str | None:
    words = set(words_from_text(text))
    categories = sorted(
        {str(recipe.get("category")) for recipe in recipes if recipe.get("category")},
        key=len,
        reverse=True,
    )

    for category in categories:
        category_key = normalize(category)
        aliases = CATEGORY_ALIASES.get(category_key, [category_key])
        if any(alias in words or alias in normalize(text) for alias in aliases):
            return category

    return None


def set_macro_filter(filters: dict[str, Any], key: str, bound: str, value: int) -> None:
    filter_key = f"{key}_{bound}"
    current_value = filters.get(filter_key)

    if current_value is None:
        filters[filter_key] = value
        return

    if bound == "min":
        filters[filter_key] = max(current_value, value)
    else:
        filters[filter_key] = min(current_value, value)


def extract_macro_filters(text: str, filters: dict[str, Any]) -> None:
    normalized_text = normalize(text)
    max_words = r"(?:до|меньше|менее|ниже|не больше|<=|<)"
    min_words = r"(?:от|больше|выше|не меньше|>=|>)"

    for key, alias in MACRO_ALIASES.items():
        for pattern in (
            rf"{max_words}\s*(\d+)\s*{alias}",
            rf"{alias}\s*{max_words}\s*(\d+)",
        ):
            match = re.search(pattern, normalized_text)
            if match:
                set_macro_filter(filters, key, "max", int(match.group(1)))

        for pattern in (
            rf"{min_words}\s*(\d+)\s*{alias}",
            rf"{alias}\s*{min_words}\s*(\d+)",
        ):
            match = re.search(pattern, normalized_text)
            if match:
                set_macro_filter(filters, key, "min", int(match.group(1)))

    if re.search(r"(пп|низкокал|легкое|лёгкое)", normalized_text):
        set_macro_filter(filters, "calories", "max", 500)

    if re.search(r"(белковое|много белка|белка побольше|побольше белка)", normalized_text):
        set_macro_filter(filters, "protein", "min", 20)

    if re.search(r"(не жирное|меньше жира|поменьше жира)", normalized_text):
        set_macro_filter(filters, "fat", "max", 20)

    if re.search(r"(мало углеводов|низкоуглев)", normalized_text):
        set_macro_filter(filters, "carbs", "max", 35)


def extract_time_filters(text: str, filters: dict[str, Any]) -> None:
    normalized_text = normalize(text)
    match = re.search(r"(?:до|за|меньше|менее)\s*(\d+)\s*(?:мин|минут)", normalized_text)
    if match:
        filters["max_time"] = int(match.group(1))

    if re.search(r"(быстро|быстрое|быстрый|побыстрее|на скорую)", normalized_text):
        filters["quick"] = True

    if re.search(r"(сложное|сложно|замороч|долго)", normalized_text):
        filters["hard"] = True


def extract_include_terms(text: str, filters: dict[str, Any]) -> list[str]:
    excluded_stems = {stem_word(term) for term in filters["exclude_terms"]}
    category = normalize(filters.get("category") or "")
    terms: list[str] = []
    term_stems: set[str] = set()

    for word in words_from_text(text):
        stem = stem_word(word)
        if (
            word.isdigit()
            or word in STOPWORDS
            or word in SMART_WORDS
            or stem in excluded_stems
            or normalize(word) == category
            or len(stem) < 3
        ):
            continue

        if any(re.fullmatch(alias, word) for alias in MACRO_ALIASES.values()):
            continue

        if stem not in term_stems:
            terms.append(word)
            term_stems.add(stem)

    return terms


def parse_recipe_filters(text: str, recipes: list[dict[str, Any]]) -> dict[str, Any]:
    filters: dict[str, Any] = {
        "category": extract_category(text, recipes),
        "exclude_terms": extract_excluded_terms(text),
        "include_terms": [],
        "quick": False,
        "hard": False,
        "has_image": False,
        "random": bool(re.search(r"(рандом|случайн|выбери сама|судьба)", normalize(text))),
    }

    extract_time_filters(text, filters)
    extract_macro_filters(text, filters)

    if re.search(r"(с фото|с картин|фото|картинк)", normalize(text)):
        filters["has_image"] = True

    filters["include_terms"] = extract_include_terms(text, filters)
    return filters


def recipe_matches_macro_filters(recipe: dict[str, Any], filters: dict[str, Any]) -> bool:
    for key in MACRO_ALIASES:
        value = nutrition_value(recipe, key)
        min_value = filters.get(f"{key}_min")
        max_value = filters.get(f"{key}_max")

        if min_value is not None and (value is None or value < min_value):
            return False

        if max_value is not None and (value is None or value > max_value):
            return False

    return True


def apply_recipe_filters(recipes: list[dict[str, Any]], filters: dict[str, Any]) -> list[dict[str, Any]]:
    filtered = recipes

    category = filters.get("category")
    if category:
        filtered = [recipe for recipe in filtered if normalize(recipe.get("category")) == normalize(category)]

    if filters.get("quick"):
        filtered = [recipe for recipe in filtered if is_quick(recipe)]

    if filters.get("hard"):
        filtered = [recipe for recipe in filtered if is_hard(recipe)]

    max_time = filters.get("max_time")
    if max_time is not None:
        filtered = [recipe for recipe in filtered if time_minutes_is_at_most(recipe.get("time_minutes"), max_time)]

    if filters.get("has_image"):
        filtered = [recipe for recipe in filtered if isinstance(recipe.get("image"), str)]

    for term in filters["include_terms"]:
        filtered = [recipe for recipe in filtered if recipe_matches_term(recipe, term)]

    for term in filters["exclude_terms"]:
        filtered = [recipe for recipe in filtered if not recipe_matches_term(recipe, term)]

    return [recipe for recipe in filtered if recipe_matches_macro_filters(recipe, filters)]


def has_recipe_filters(filters: dict[str, Any]) -> bool:
    important_keys = (
        "category",
        "quick",
        "hard",
        "has_image",
        "max_time",
        "include_terms",
        "exclude_terms",
        "random",
    )

    if any(filters.get(key) for key in important_keys):
        return True

    return any(filters.get(f"{key}_min") is not None or filters.get(f"{key}_max") is not None for key in MACRO_ALIASES)


def recipe_filter_summary(filters: dict[str, Any]) -> str:
    parts: list[str] = []

    if filters.get("category"):
        parts.append(str(filters["category"]))
    if filters.get("quick"):
        parts.append("быстро")
    if filters.get("hard"):
        parts.append("посложнее")
    if filters.get("max_time") is not None:
        parts.append(f"до {filters['max_time']} мин")
    if filters.get("has_image"):
        parts.append("с фото")
    if filters["include_terms"]:
        parts.append("с " + ", ".join(filters["include_terms"]))
    if filters["exclude_terms"]:
        parts.append("без " + ", ".join(filters["exclude_terms"]))

    for key, label in MACRO_LABELS.items():
        min_value = filters.get(f"{key}_min")
        max_value = filters.get(f"{key}_max")
        if min_value is not None:
            parts.append(f"{label} от {min_value}")
        if max_value is not None:
            parts.append(f"{label} до {max_value}")

    return "; ".join(parts)


def page_count(total: int, limit: int) -> int:
    return max(1, (total + limit - 1) // limit)


def clamp_page(page: int, total: int, limit: int) -> int:
    return max(0, min(page, page_count(total, limit) - 1))


def recipe_results_keyboard(recipes: list[dict[str, Any]], page: int = 0) -> InlineKeyboardMarkup:
    page = clamp_page(page, len(recipes), RECIPE_RESULT_LIMIT)
    start = page * RECIPE_RESULT_LIMIT
    end = start + RECIPE_RESULT_LIMIT
    keyboard = [
        [InlineKeyboardButton(text=recipe.get("title", "без названия"), callback_data=f"recipe:{item_id(recipe)}")]
        for recipe in recipes[start:end]
    ]

    nav: list[InlineKeyboardButton] = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="← назад", callback_data=f"recipe_results:{page - 1}"))
    if end < len(recipes):
        nav.append(InlineKeyboardButton(text="дальше →", callback_data=f"recipe_results:{page + 1}"))
    if nav:
        keyboard.append(nav)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def save_recipe_result_ids(state: FSMContext | None, recipes: list[dict[str, Any]]) -> None:
    if state is not None:
        await state.update_data(recipe_result_ids=[item_id(recipe) for recipe in recipes])


async def send_recipe_result_list(
    message: Message,
    recipes: list[dict[str, Any]],
    state: FSMContext | None,
    title: str,
    page: int = 0,
) -> None:
    if not recipes:
        await message.answer("ничего не нашла 🥲 попробуй другой запрос", reply_markup=cooking_keyboard())
        return

    await save_recipe_result_ids(state, recipes)
    page = clamp_page(page, len(recipes), RECIPE_RESULT_LIMIT)
    header = title
    if len(recipes) > RECIPE_RESULT_LIMIT:
        header += f"\nстраница {page + 1}/{page_count(len(recipes), RECIPE_RESULT_LIMIT)}"

    await message.answer(header, reply_markup=cooking_keyboard())
    await message.answer("выбери рецепт:", reply_markup=recipe_results_keyboard(recipes, page))


async def send_recipe_results(
    message: Message,
    recipes: list[dict[str, Any]],
    filters: dict[str, Any],
    user_id: int | None,
    state: FSMContext | None = None,
) -> None:
    found = apply_recipe_filters(recipes, filters)

    if not has_recipe_filters(filters):
        await message.answer(
            "по готовке понимаю так: «ужин с курицей до 600 ккал», «без бекона», «белка больше 20», «быстрое с сыром»",
            reply_markup=cooking_keyboard(),
        )
        return

    if not found:
        await message.answer("ничего не нашла 🥲 попробуй ослабить фильтр", reply_markup=cooking_keyboard())
        return

    if filters.get("random"):
        await message.answer("выбрала из подходящего:", reply_markup=cooking_keyboard())
        await send_recipe(message, random.choice(found), user_id)
        return

    await send_recipe_result_list(
        message,
        found,
        state,
        f"по твоему запросу я нашла рецептов: {len(found)}",
    )


def place_search_text(place: dict[str, Any]) -> str:
    parts: list[str] = []

    for key in ("title", "city", "address", "review", "url"):
        value = place.get(key)
        if isinstance(value, str):
            parts.append(value)

    for key in ("types", "tags", "metro"):
        value = place.get(key)
        if isinstance(value, list):
            parts.extend(str(item) for item in value)

    return compact_text(" ".join(parts))


def place_matches_term(place: dict[str, Any], term: str) -> bool:
    term = normalize(term).strip()
    if not term:
        return False

    haystack = place_search_text(place)
    stem = stem_word(term)

    return compact_text(term) in haystack or stem in haystack


def known_place_cities(places: list[dict[str, Any]]) -> list[str]:
    return sorted({str(place.get("city")) for place in places if place.get("city")})


def known_metros(places: list[dict[str, Any]]) -> list[str]:
    metro: set[str] = set()
    for place in places:
        value = place.get("metro")
        if isinstance(value, list):
            metro.update(str(item) for item in value if item)

    return sorted(metro, key=len, reverse=True)


def extract_place_type(text: str) -> str | None:
    normalized_text = compact_text(text)

    for place_type, aliases in PLACE_TYPE_ALIASES.items():
        if any(compact_text(alias) in normalized_text for alias in aliases):
            return place_type

    return None


def extract_place_status(text: str) -> str | None:
    normalized_text = normalize(text)

    if re.search(r"(не была|не был|хочу|куда сходить|сходить|надо сходить|wishlist)", normalized_text):
        return "wishlist"

    if re.search(r"(где я была|я была|была|ходила|посещ)", normalized_text):
        return "visited"

    return None


def extract_place_city(text: str, places: list[dict[str, Any]]) -> str | None:
    normalized_text = compact_text(text)
    for city in known_place_cities(places):
        if compact_text(city) in normalized_text:
            return city

    return None


def extract_place_metro(text: str, places: list[dict[str, Any]]) -> str | None:
    normalized_text = compact_text(text)
    for metro in known_metros(places):
        if compact_text(metro) in normalized_text:
            return metro

    match = re.search(r"(?:метро|м)\s+([a-zа-яё -]+)", normalize(text))
    if match:
        return match.group(1).strip()

    return None


def extract_place_terms(text: str, filters: dict[str, Any]) -> list[str]:
    skip_words = set(PLACE_STOPWORDS)

    for aliases in PLACE_TYPE_ALIASES.values():
        skip_words.update(aliases)

    if filters.get("city"):
        skip_words.update(words_from_text(str(filters["city"])))
    if filters.get("metro"):
        skip_words.update(words_from_text(str(filters["metro"])))

    terms: list[str] = []
    term_stems: set[str] = set()

    for word in words_from_text(text):
        stem = stem_word(word)
        if word.isdigit() or word in skip_words or len(stem) < 3:
            continue

        if stem not in term_stems:
            terms.append(word)
            term_stems.add(stem)

    return terms


def parse_place_filters(text: str, places: list[dict[str, Any]]) -> dict[str, Any]:
    filters: dict[str, Any] = {
        "status": extract_place_status(text),
        "type": extract_place_type(text),
        "city": extract_place_city(text, places),
        "metro": extract_place_metro(text, places),
        "favorite": bool(re.search(r"(любим|очень хорошо|было хорошо|стоит)", normalize(text))),
        "has_photo": bool(re.search(r"(с фото|фото|картинк)", normalize(text))),
        "random": bool(re.search(r"(рандом|случайн|выбери|куда сходить|куда пойти)", normalize(text))),
        "terms": [],
    }
    filters["terms"] = extract_place_terms(text, filters)

    return filters


def place_has_type(place: dict[str, Any], place_type: str) -> bool:
    types = place.get("types", [])
    tags = place.get("tags", [])

    return (
        isinstance(types, list)
        and place_type in types
        or isinstance(tags, list)
        and place_type in [normalize(tag) for tag in tags]
    )


def apply_place_filters(places: list[dict[str, Any]], filters: dict[str, Any]) -> list[dict[str, Any]]:
    filtered = places

    if filters.get("status"):
        filtered = [place for place in filtered if place.get("status") == filters["status"]]

    if filters.get("type"):
        filtered = [place for place in filtered if place_has_type(place, filters["type"])]

    if filters.get("city"):
        filtered = [place for place in filtered if normalize(place.get("city")) == normalize(filters["city"])]

    if filters.get("metro"):
        wanted_metro = compact_text(filters["metro"])
        filtered = [
            place
            for place in filtered
            if any(wanted_metro in compact_text(metro) for metro in place.get("metro", []))
        ]

    if filters.get("favorite"):
        filtered = [place for place in filtered if place.get("favorite") is True]

    if filters.get("has_photo"):
        filtered = [place for place in filtered if place.get("photos")]

    for term in filters["terms"]:
        filtered = [place for place in filtered if place_matches_term(place, term)]

    return filtered


def has_place_filters(filters: dict[str, Any]) -> bool:
    return any(filters.get(key) for key in ("status", "type", "city", "metro", "favorite", "has_photo", "random", "terms"))


def has_place_intent(text: str, filters: dict[str, Any]) -> bool:
    words = set(words_from_text(text))
    if words & PLACE_INTENT_WORDS:
        return True

    return any(filters.get(key) for key in ("status", "type", "metro", "favorite"))


def is_broad_place_query(text: str, filters: dict[str, Any]) -> bool:
    normalized_text = compact_text(text)
    if normalized_text in BROAD_PLACE_QUERIES:
        return True

    return (
        normalized_text in {"что по местам", "что есть по местам"}
        or words_from_text(text) == ["места"]
        or has_place_intent(text, filters)
        and not has_place_filters(filters)
    )


def place_filter_summary(filters: dict[str, Any]) -> str:
    parts: list[str] = []

    if filters.get("status"):
        parts.append(PLACE_STATUS_LABELS.get(filters["status"], filters["status"]))
    if filters.get("type"):
        parts.append(PLACE_TYPE_LABELS.get(filters["type"], filters["type"]))
    if filters.get("city"):
        parts.append(str(filters["city"]))
    if filters.get("metro"):
        parts.append(f"метро {filters['metro']}")
    if filters.get("favorite"):
        parts.append("любимое / стоит сходить")
    if filters.get("has_photo"):
        parts.append("с фото")
    if filters["terms"]:
        parts.append("по словам: " + ", ".join(filters["terms"]))

    return "; ".join(parts)


def format_place(place: dict[str, Any]) -> str:
    title = place.get("title", "без названия")
    types = place.get("types", [])
    metro = place.get("metro", [])
    tags = place.get("tags", [])
    status = PLACE_STATUS_LABELS.get(str(place.get("status")), str(place.get("status") or "не указано"))
    review = str(place.get("review") or "").strip()
    url = str(place.get("url") or "").strip()

    type_text = ", ".join(PLACE_TYPE_LABELS.get(place_type, place_type) for place_type in types) if isinstance(types, list) else ""
    metro_text = ", ".join(str(item) for item in metro) if isinstance(metro, list) and metro else "не указано"
    tag_text = ", ".join(str(item) for item in tags) if isinstance(tags, list) and tags else ""
    review_text = f"\nотзыв: {review}" if review else ""
    tags_text = f"\nтеги: {tag_text}" if tag_text else ""
    url_text = f"\n\nкарта: {url}" if url else ""

    return (
        f"📍 {title}\n\n"
        f"город: {place.get('city', 'не указан')}\n"
        f"тип: {type_text or 'не указан'}\n"
        f"статус: {status}\n"
        f"метро: {metro_text}\n"
        f"адрес: {place.get('address') or 'не указан'}"
        f"{review_text}"
        f"{tags_text}"
        f"{url_text}"
    )


def place_actions_keyboard(place: dict[str, Any], user_id: int | None) -> InlineKeyboardMarkup:
    wanted_id = item_id(place)
    text = "💔 убрать из любимых" if is_favorite("places", user_id, wanted_id) else "⭐ в любимые"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text, callback_data=f"place_fav:{wanted_id}")],
        ]
    )


async def send_place(message: Message, place: dict[str, Any], user_id: int | None = None) -> None:
    photos = place.get("photos", [])
    if isinstance(photos, list):
        for photo in photos[:1]:
            if isinstance(photo, str) and photo.strip():
                photo_path = BASE_DIR / photo
                if photo_path.exists():
                    await message.answer_photo(photo=FSInputFile(photo_path), caption=str(place.get("title", "место")))

    await message.answer(format_place(place), reply_markup=place_actions_keyboard(place, user_id))


async def send_places_dashboard(message: Message, user_id: int | None = None) -> None:
    places = load_places()
    if not places:
        await message.answer("мест пока нет", reply_markup=places_keyboard())
        return

    await message.answer(
        f"выбери подборку или напиши, что ищем.\n\nкарта всех мест: {places_map_url()}",
        reply_markup=places_keyboard(),
    )


async def send_place_results(
    message: Message,
    places: list[dict[str, Any]],
    filters: dict[str, Any],
    user_id: int | None,
) -> None:
    found = apply_place_filters(places, filters)
    if filters.get("favorite"):
        saved_ids = favorite_ids("places", user_id)
        favorite_places = [place for place in places if item_id(place) in saved_ids or place.get("favorite") is True]
        found_ids = {item_id(place) for place in found}
        found.extend(place for place in favorite_places if item_id(place) not in found_ids)

    if not has_place_filters(filters):
        await message.answer(
            "по местам понимаю так: «кофе у метро Китай-город», «бар где Аня была», «Аня хочет сходить на бранч», «любимые места»",
            reply_markup=places_keyboard(),
        )
        return

    if not found:
        await message.answer("ничего не нашла 🥲 попробуй другой фильтр", reply_markup=places_keyboard())
        return

    if filters.get("random"):
        await message.answer("я бы выбрала вот это:", reply_markup=places_keyboard())
        await send_place(message, random.choice(found), user_id)
        return

    summary = place_filter_summary(filters)
    header = f"нашла мест: {len(found)}"
    if summary:
        header += f"\nфильтр: {summary}"
    if len(found) > PLACE_RESULT_LIMIT:
        header += f"\nпоказываю первые {PLACE_RESULT_LIMIT}; можно уточнить метро, тип или статус"

    await message.answer(header, reply_markup=places_keyboard())
    await message.answer(
        "выбери место:",
        reply_markup=place_list_keyboard(found[:PLACE_RESULT_LIMIT]),
    )


def chunk_buttons(buttons: list[InlineKeyboardButton], size: int = 2) -> list[list[InlineKeyboardButton]]:
    return [buttons[index : index + size] for index in range(0, len(buttons), size)]


def dad_cluster_keyboard(recipes: list[dict[str, Any]]) -> InlineKeyboardMarkup:
    buttons: list[InlineKeyboardButton] = []

    for cluster in DAD_CLUSTER_ORDER:
        count = sum(1 for recipe in recipes if recipe.get("dad_cluster", "classic") == cluster)
        if count:
            label = DAD_CLUSTER_LABELS.get(cluster, cluster)
            buttons.append(
                InlineKeyboardButton(
                    text=f"{label} ({count})",
                    callback_data=f"dad_cluster:{cluster}",
                )
            )

    keyboard = chunk_buttons(buttons)
    keyboard.append([InlineKeyboardButton(text="все омлеты", callback_data="dad_cluster:all")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def recipe_list_keyboard(
    recipes: list[dict[str, Any]],
    callback_prefix: str,
    back_callback: str,
) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text=recipe.get("title", "без названия"), callback_data=f"{callback_prefix}:{item_id(recipe)}")]
        for recipe in recipes
    ]
    keyboard.append([InlineKeyboardButton(text="назад", callback_data=back_callback)])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def all_categories_keyboard(recipes: list[dict[str, Any]]) -> InlineKeyboardMarkup:
    buttons: list[InlineKeyboardButton] = [
        InlineKeyboardButton(text=f"все рецепты ({len(recipes)})", callback_data="category:special:all")
    ]
    seen_categories: set[str] = set()
    category_labels = {
        "завтрак": "завтраки",
        "ужин": "ужины",
        "паста": "паста",
        "суп": "супы",
        "десерт": "десерты",
        "салат": "салаты",
    }

    for recipe in recipes:
        category = str(recipe.get("category") or "без категории")
        category_key = normalize(category)
        if category_key in seen_categories:
            continue

        seen_categories.add(category_key)
        count = sum(1 for item in recipes if normalize(item.get("category")) == category_key)
        buttons.append(
            InlineKeyboardButton(
                text=f"{category_labels.get(category_key, category)} ({count})",
                callback_data=f"category:{category}",
            )
        )

    quick_count = sum(1 for recipe in recipes if is_quick(recipe))
    if quick_count:
        buttons.append(InlineKeyboardButton(text=f"до 20 минут ({quick_count})", callback_data="category:special:quick"))

    hard_count = sum(1 for recipe in recipes if is_hard(recipe))
    if hard_count:
        buttons.append(InlineKeyboardButton(text=f"посложнее ({hard_count})", callback_data="category:special:hard"))

    photo_count = sum(1 for recipe in recipes if isinstance(recipe.get("image"), str))
    if photo_count:
        buttons.append(InlineKeyboardButton(text=f"с фото ({photo_count})", callback_data="category:special:photo"))

    protein_count = sum(1 for recipe in recipes if (nutrition_value(recipe, "protein") or 0) >= 20)
    if protein_count:
        buttons.append(InlineKeyboardButton(text=f"белка побольше ({protein_count})", callback_data="category:special:protein"))

    return InlineKeyboardMarkup(inline_keyboard=chunk_buttons(buttons))


def filter_category(
    recipes: list[dict[str, Any]],
    category_data: str,
) -> tuple[str, list[dict[str, Any]]]:
    if category_data == "special:all":
        return "все рецепты", recipes

    if category_data == "special:quick":
        return "до 20 минут", [recipe for recipe in recipes if is_quick(recipe)]

    if category_data == "special:hard":
        return "посложнее", [recipe for recipe in recipes if is_hard(recipe)]

    if category_data == "special:photo":
        return "с фото", [recipe for recipe in recipes if isinstance(recipe.get("image"), str)]

    if category_data == "special:protein":
        return "белка побольше", [recipe for recipe in recipes if (nutrition_value(recipe, "protein") or 0) >= 20]

    category = category_data
    return category, [recipe for recipe in recipes if normalize(recipe.get("category")) == normalize(category)]


def place_filters_keyboard(places: list[dict[str, Any]], user_id: int | None) -> InlineKeyboardMarkup:
    favorite_place_ids = {item_id(place) for place in places if place.get("favorite") is True} | favorite_ids("places", user_id)
    buttons = [
        InlineKeyboardButton(
            text=f"где Аня была ({sum(1 for place in places if place.get('status') == 'visited')})",
            callback_data="place_filter:status:visited",
        ),
        InlineKeyboardButton(
            text=f"Аня хочет сходить ({sum(1 for place in places if place.get('status') == 'wishlist')})",
            callback_data="place_filter:status:wishlist",
        ),
        InlineKeyboardButton(
            text=f"мои любимые ({len(favorite_place_ids)})",
            callback_data="place_filter:favorites",
        ),
    ]

    for place_type, label in PLACE_TYPE_LABELS.items():
        count = sum(1 for place in places if place_has_type(place, place_type))
        if count:
            buttons.append(
                InlineKeyboardButton(
                    text=f"{label} ({count})",
                    callback_data=f"place_filter:type:{place_type}",
                )
            )

    return InlineKeyboardMarkup(inline_keyboard=chunk_buttons(buttons))


def place_filter_home_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="по Аниным спискам", callback_data="place_group:status")],
            [InlineKeyboardButton(text="по формату места", callback_data="place_group:type")],
            [InlineKeyboardButton(text="по метро", callback_data="place_group:metro")],
            [InlineKeyboardButton(text="любимые / рекомендации", callback_data="place_filter:favorites")],
            [InlineKeyboardButton(text="все места списком", callback_data="place_filter:all")],
        ]
    )


def place_status_keyboard(places: list[dict[str, Any]]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"где Аня была ({sum(1 for place in places if place.get('status') == 'visited')})",
                    callback_data="place_filter:status:visited",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"Аня хочет сходить ({sum(1 for place in places if place.get('status') == 'wishlist')})",
                    callback_data="place_filter:status:wishlist",
                )
            ],
            [InlineKeyboardButton(text="назад", callback_data="place_group:home")],
        ]
    )


def place_type_keyboard(places: list[dict[str, Any]]) -> InlineKeyboardMarkup:
    buttons = []
    for place_type, label in PLACE_TYPE_LABELS.items():
        count = sum(1 for place in places if place_has_type(place, place_type))
        if count:
            buttons.append(InlineKeyboardButton(text=f"{label} ({count})", callback_data=f"place_filter:type:{place_type}"))

    keyboard = chunk_buttons(buttons)
    keyboard.append([InlineKeyboardButton(text="назад", callback_data="place_group:home")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def metro_filter_values(places: list[dict[str, Any]]) -> list[str]:
    values: set[str] = set()
    for place in places:
        metro = place.get("metro")
        if isinstance(metro, list):
            values.update(str(item) for item in metro if item)

    return sorted(values)


def place_metro_keyboard(places: list[dict[str, Any]]) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(
            text=f"{metro} ({sum(1 for place in places if metro in place.get('metro', []))})",
            callback_data=f"place_filter:metro:{index}",
        )
        for index, metro in enumerate(metro_filter_values(places))
    ]

    keyboard = chunk_buttons(buttons, size=1)
    keyboard.append([InlineKeyboardButton(text="назад", callback_data="place_group:home")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def place_list_keyboard(places: list[dict[str, Any]], back_callback: str = "places_home") -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text=place.get("title", "без названия"), callback_data=f"place:{item_id(place)}")]
        for place in places
    ]
    keyboard.append([InlineKeyboardButton(text="назад", callback_data=back_callback)])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def favorites_home_keyboard(user_id: int | None) -> InlineKeyboardMarkup:
    recipe_count = len(favorite_ids("recipes", user_id))
    favorite_place_ids = {item_id(place) for place in load_places() if place.get("favorite") is True} | favorite_ids("places", user_id)
    place_count = len(favorite_place_ids)

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"рецепты ({recipe_count})", callback_data="favorites:recipes")],
            [InlineKeyboardButton(text=f"места ({place_count})", callback_data="favorites:places")],
        ]
    )


def admin_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ добавить место", callback_data="admin:add_place")],
            [InlineKeyboardButton(text="🖼 добавить фото к месту", callback_data="admin:add_photo")],
            [InlineKeyboardButton(text="🗺 заменить ссылку карты", callback_data="admin:set_map")],
            [InlineKeyboardButton(text="🪪 мой telegram id", callback_data="admin:whoami")],
            [InlineKeyboardButton(text="🧷 стикеры", callback_data="admin:stickers")],
        ]
    )


def parse_admin_fields(text: str) -> dict[str, str]:
    aliases = {
        "название": "title",
        "имя": "title",
        "адрес": "address",
        "ссылка": "url",
        "карта": "url",
        "url": "url",
        "статус": "status",
        "тип": "types",
        "типы": "types",
        "метро": "metro",
        "отзыв": "review",
        "коммент": "review",
        "город": "city",
    }
    fields: dict[str, str] = {}

    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        normalized_key = normalize(key).strip()
        field = aliases.get(normalized_key)
        if field and value.strip():
            fields[field] = value.strip()

    return fields


def admin_place_id(title: str, url: str = "") -> str:
    words = re.findall(r"[a-z0-9]+", compact_text(title))
    prefix = "-".join(words[:5]) or "place"
    suffix = hashlib.sha1(f"{title}|{url}".encode("utf-8")).hexdigest()[:8]
    return f"{prefix}-{suffix}"[:64]


def normalize_admin_status(value: str) -> str:
    text = normalize(value)
    if any(word in text for word in ("была", "ходила", "visited")):
        return "visited"
    return "wishlist"


def normalize_admin_types(value: str) -> list[str]:
    result: list[str] = []
    chunks = [chunk.strip() for chunk in re.split(r"[,;/]", value) if chunk.strip()]
    for chunk in chunks:
        normalized_chunk = compact_text(chunk)
        matched_type = None
        for place_type, label in PLACE_TYPE_LABELS.items():
            aliases = [label, *PLACE_TYPE_ALIASES.get(place_type, [])]
            if any(compact_text(alias) == normalized_chunk for alias in aliases):
                matched_type = place_type
                break
        if matched_type and matched_type not in result:
            result.append(matched_type)

    return result or ["cafe"]


def build_admin_place(text: str) -> tuple[dict[str, Any] | None, str]:
    fields = parse_admin_fields(text)
    title = fields.get("title", "").strip()

    if not title:
        return None, "не вижу название. добавь строку `название: ...`"

    place = {
        "id": admin_place_id(title, fields.get("url", "")),
        "title": title,
        "city": fields.get("city", "Москва"),
        "address": fields.get("address", ""),
        "metro": [item.strip() for item in fields.get("metro", "").split(",") if item.strip()],
        "types": normalize_admin_types(fields.get("types", "кафе")),
        "status": normalize_admin_status(fields.get("status", "хочу")),
        "favorite": False,
        "tags": [],
        "review": fields.get("review", ""),
        "photos": [],
        "url": fields.get("url", ""),
    }

    return place, ""


def find_place_for_admin(query: str) -> dict[str, Any] | None:
    query = normalize(query).strip()
    if not query:
        return None

    places = load_places()
    by_id = find_item(places, query)
    if by_id:
        return by_id

    compact_query = compact_text(query)
    for place in places:
        if compact_query and compact_query in compact_text(place.get("title")):
            return place

    return None


async def send_dad_home(message: Message) -> None:
    recipes = dad_recipes()

    if not recipes:
        await message.answer("папиных омлетов пока нет 🥲", reply_markup=cooking_keyboard())
        return

    await message.answer(
        "папа, какой омлет хочешь сегодня?",
        reply_markup=dad_cluster_keyboard(recipes),
    )


async def answer_or_alert(
    callback: CallbackQuery,
    callback_body: Callable[[], Any],
) -> None:
    if callback.message is None:
        await callback.answer()
        return

    await callback_body()
    await callback.answer()


@router.message(CommandStart())
async def handle_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    sticker_id = os.getenv("START_STICKER_ID")
    if sticker_id:
        try:
            await message.answer_sticker(sticker_id)
        except Exception as error:
            print(f"не удалось отправить стартовый стикер: {error}")

    await message.answer(
        "привет, это Анин shesocold-бот 🍳📍\n\n"
        "тут можно смотреть рецепты, места, любимое и Анину карту. "
        "выбирай в меню, что хочешь, а если что-то бесит или хочется добавить — я жду обратной связи.",
        reply_markup=main_keyboard(message.from_user),
    )


@router.message(F.text == BACK_BUTTON)
async def handle_back(message: Message, state: FSMContext) -> None:
    await state.set_state(None)
    await message.answer("выбери, что хочешь", reply_markup=main_keyboard(message.from_user))


@router.message(F.text == COOKING_BUTTON)
async def handle_cooking_home(message: Message, state: FSMContext) -> None:
    await state.set_state(None)
    await message.answer("что сегодня делаем?", reply_markup=cooking_keyboard())


@router.message(F.text == PLACES_BUTTON)
async def handle_places_home(message: Message, state: FSMContext) -> None:
    await state.set_state(None)
    await send_places_dashboard(message, message.from_user.id if message.from_user else None)


@router.message(F.text == FAVORITES_BUTTON)
async def handle_favorites_home(message: Message) -> None:
    await message.answer("любимое:", reply_markup=favorites_home_keyboard(message.from_user.id if message.from_user else None))


@router.message(F.text == ADMIN_BUTTON)
async def handle_admin_home(message: Message, state: FSMContext) -> None:
    await state.set_state(None)
    if not is_admin_user(message.from_user):
        await message.answer("админка только для Ани.", reply_markup=main_keyboard(message.from_user))
        return

    await message.answer(
        "админка Ани.\n\n"
        "что делаем: добавляем место, меняем ссылку карты, прикручиваем фото или достаём file_id стикера.",
        reply_markup=admin_keyboard(),
    )


@router.callback_query(F.data.startswith("admin:"))
async def handle_admin_callback(callback: CallbackQuery, state: FSMContext) -> None:
    if not is_admin_user(callback.from_user):
        await callback.answer("админка только для Ани", show_alert=True)
        return

    action = (callback.data or "").removeprefix("admin:")

    async def body() -> None:
        if action == "add_place":
            await state.set_state(AdminState.waiting_for_place)
            await callback.message.answer(
                "пришли место вот так:\n\n"
                "название: Кофейня мечты\n"
                "адрес: Москва, ул. Примерная, 1\n"
                "ссылка: https://yandex.ru/maps/...\n"
                "статус: хочу\n"
                "тип: кофе, кафе\n"
                "метро: Китай-город\n"
                "отзыв: вайб на спокойный кофе"
            )
            return

        if action == "add_photo":
            await state.set_state(AdminState.waiting_for_place_photo)
            await callback.message.answer(
                "пришли фото, а в подписи напиши название места или его id.\n"
                "например: Мама Варит Кофе"
            )
            return

        if action == "set_map":
            await state.set_state(AdminState.waiting_for_map_url)
            await callback.message.answer("пришли новую ссылку на карту Яндекса одним сообщением.")
            return

        if action == "whoami":
            user = callback.from_user
            await callback.message.answer(
                f"id: `{user.id}`\nusername: @{user.username or 'нет'}",
                parse_mode="Markdown",
            )
            return

        if action == "stickers":
            await callback.message.answer(
                "пришли мне стикер, и я отвечу его `file_id`.\n"
                "потом можно положить его в `.env` как `START_STICKER_ID=...`, и бот будет слать его на /start.",
                parse_mode="Markdown",
            )

    await answer_or_alert(callback, body)


@router.message(AdminState.waiting_for_place)
async def handle_admin_place_text(message: Message, state: FSMContext) -> None:
    if not is_admin_user(message.from_user):
        await state.clear()
        await message.answer("админка только для Ани.", reply_markup=main_keyboard(message.from_user))
        return

    if await route_menu_button(message, state, message.text or ""):
        return

    place, error = build_admin_place(message.text or "")
    if place is None:
        await message.answer(error)
        return

    places = load_places()
    places.append(place)
    save_places(places)
    await state.set_state(None)
    await message.answer(f"добавила место: {place['title']}", reply_markup=places_keyboard())


@router.message(AdminState.waiting_for_map_url)
async def handle_admin_map_url(message: Message, state: FSMContext) -> None:
    if not is_admin_user(message.from_user):
        await state.clear()
        await message.answer("админка только для Ани.", reply_markup=main_keyboard(message.from_user))
        return

    if await route_menu_button(message, state, message.text or ""):
        return

    url = (message.text or "").strip()
    if not url.startswith("https://yandex.ru/maps/"):
        await message.answer("это не похоже на ссылку Яндекс.Карт. пришли ссылку, которая начинается с https://yandex.ru/maps/")
        return

    settings = load_settings()
    settings["places_map_url"] = url
    save_settings(settings)
    await state.set_state(None)
    await message.answer("обновила ссылку карты.", reply_markup=places_keyboard())


@router.message(AdminState.waiting_for_place_photo, F.photo)
async def handle_admin_place_photo(message: Message, state: FSMContext, bot: Bot) -> None:
    if not is_admin_user(message.from_user):
        await state.clear()
        await message.answer("админка только для Ани.", reply_markup=main_keyboard(message.from_user))
        return

    place = find_place_for_admin(message.caption or "")
    if place is None:
        await message.answer("не нашла место по подписи. подпиши фото названием места, например: Мама Варит Кофе")
        return

    photo = message.photo[-1]
    file_hash = hashlib.sha1(photo.file_unique_id.encode("utf-8")).hexdigest()[:10]
    filename = f"{item_id(place)[:40]}-{file_hash}.jpg"
    relative_path = Path("assets") / "places" / filename
    destination = BASE_DIR / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    await bot.download(photo, destination=destination)

    places = load_places()
    saved_place = find_item(places, item_id(place))
    if saved_place is None:
        await message.answer("место потерялось при сохранении, фото не привязала.")
        return

    photos = saved_place.get("photos")
    if not isinstance(photos, list):
        photos = []
    photos.append(relative_path.as_posix())
    saved_place["photos"] = photos
    save_places(places)
    await state.set_state(None)
    await message.answer(f"добавила фото к месту: {saved_place.get('title')}", reply_markup=places_keyboard())


@router.message(AdminState.waiting_for_place_photo)
async def handle_admin_place_photo_wrong(message: Message) -> None:
    await message.answer("жду именно фото с подписью-названием места.")


@router.message(F.sticker)
async def handle_sticker_id(message: Message) -> None:
    if not is_admin_user(message.from_user):
        await message.answer("стикер красивый, но я пока умею сохранять file_id только для Ани.")
        return

    await message.answer(
        f"file_id стикера:\n`{message.sticker.file_id}`",
        parse_mode="Markdown",
    )


@router.message(F.text == DAD_BUTTON)
async def handle_dad_gate(message: Message, state: FSMContext) -> None:
    await state.set_state(DadState.waiting_for_password)
    await message.answer("если ты папа ани скажи пароль.", reply_markup=cooking_keyboard())


@router.message(DadState.waiting_for_password)
async def handle_dad_password(message: Message, state: FSMContext) -> None:
    text = message.text or ""
    if await route_menu_button(message, state, text):
        return

    if normalize(message.text).strip() != DAD_PASSWORD:
        await state.clear()
        await message.answer("доступ закрыт.", reply_markup=cooking_keyboard())
        return

    await state.update_data(dad_authorized=True)
    await state.set_state(None)
    await send_dad_home(message)


@router.message(F.text == RANDOM_BUTTON)
async def handle_random_recipe(message: Message, state: FSMContext) -> None:
    recipes = await visible_recipes(state)

    if not recipes:
        await message.answer("рецептов пока нет", reply_markup=cooking_keyboard())
        return

    await message.answer("сегодня судьба выбрала вот это:", reply_markup=cooking_keyboard())
    await send_recipe(message, random.choice(recipes), message.from_user.id if message.from_user else None)


@router.message(F.text == ALL_BUTTON)
async def handle_all_recipes(message: Message, state: FSMContext) -> None:
    recipes = await visible_recipes(state)

    if not recipes:
        await message.answer("рецептов пока нет", reply_markup=cooking_keyboard())
        return

    await message.answer("как будем искать рецепты?", reply_markup=all_categories_keyboard(recipes))


@router.message(F.text == SEARCH_BUTTON)
async def handle_search_request(message: Message, state: FSMContext) -> None:
    await state.set_state(SearchState.waiting_for_query)
    await message.answer(
        "напиши запрос: курица, ужин до 600 ккал, без бекона, белка больше 20",
        reply_markup=cooking_keyboard(),
    )


@router.message(F.text == RECIPE_FAVORITES_BUTTON)
async def handle_recipe_favorites(message: Message, state: FSMContext) -> None:
    recipes = await visible_recipes(state)
    ids = favorite_ids("recipes", message.from_user.id if message.from_user else None)
    found = [recipe for recipe in recipes if item_id(recipe) in ids]

    if not found:
        await message.answer("любимых рецептов пока нет. нажми ⭐ под рецептом, и он появится тут.", reply_markup=cooking_keyboard())
        return

    await send_recipe_result_list(message, found, state, f"любимые рецепты: {len(found)}")


@router.message(SearchState.waiting_for_query)
async def handle_search_query(message: Message, state: FSMContext) -> None:
    text = message.text or ""
    if await route_menu_button(message, state, text):
        return

    recipes = await visible_recipes(state)
    await state.set_state(None)
    await send_recipe_results(
        message,
        recipes,
        parse_recipe_filters(text, recipes),
        message.from_user.id if message.from_user else None,
        state,
    )


@router.message(F.text == ALL_PLACES_BUTTON)
async def handle_all_places(message: Message) -> None:
    await message.answer(
        "как хочешь отфильтровать места?",
        reply_markup=place_filter_home_keyboard(),
    )


@router.message(F.text == PLACE_SEARCH_BUTTON)
async def handle_place_search_request(message: Message, state: FSMContext) -> None:
    await state.set_state(PlaceSearchState.waiting_for_query)
    await message.answer(
        "напиши запрос: кофе у метро Китай-город, бар где Аня была, Аня хочет сходить на бранч",
        reply_markup=places_keyboard(),
    )


@router.message(F.text == RANDOM_PLACE_BUTTON)
async def handle_random_place(message: Message) -> None:
    places = load_places()
    if not places:
        await message.answer("мест пока нет", reply_markup=places_keyboard())
        return

    await message.answer("я бы сходила сюда:", reply_markup=places_keyboard())
    await send_place(message, random.choice(places), message.from_user.id if message.from_user else None)


@router.message(F.text == PLACE_FAVORITES_BUTTON)
async def handle_place_favorites(message: Message) -> None:
    places = load_places()
    ids = favorite_ids("places", message.from_user.id if message.from_user else None)
    found = [place for place in places if item_id(place) in ids or place.get("favorite") is True]

    if not found:
        await message.answer("любимых мест пока нет. нажми ⭐ под местом, и оно появится тут.", reply_markup=places_keyboard())
        return

    await message.answer(f"любимые места: {len(found)}", reply_markup=places_keyboard())
    await message.answer("выбери место:", reply_markup=place_list_keyboard(found[:PLACE_RESULT_LIMIT]))


@router.message(F.text == VISITED_PLACES_BUTTON)
async def handle_visited_places(message: Message) -> None:
    places = [place for place in load_places() if place.get("status") == "visited"]
    await send_place_results(
        message,
        load_places(),
        {"status": "visited", "type": None, "city": None, "metro": None, "favorite": False, "has_photo": False, "random": False, "terms": []},
        message.from_user.id if message.from_user else None,
    )


@router.message(F.text == WISHLIST_PLACES_BUTTON)
async def handle_wishlist_places(message: Message) -> None:
    await send_place_results(
        message,
        load_places(),
        {"status": "wishlist", "type": None, "city": None, "metro": None, "favorite": False, "has_photo": False, "random": False, "terms": []},
        message.from_user.id if message.from_user else None,
    )


@router.message(PlaceSearchState.waiting_for_query)
async def handle_place_search_query(message: Message, state: FSMContext) -> None:
    text = message.text or ""
    if await route_menu_button(message, state, text):
        return

    places = load_places()
    await state.set_state(None)
    await send_place_results(
        message,
        places,
        parse_place_filters(text, places),
        message.from_user.id if message.from_user else None,
    )


@router.callback_query(F.data == "dad_home")
async def handle_dad_home_callback(callback: CallbackQuery, state: FSMContext) -> None:
    if not await has_dad_access(state):
        await callback.answer("доступ закрыт", show_alert=True)
        return

    async def body() -> None:
        await send_dad_home(callback.message)

    await answer_or_alert(callback, body)


@router.callback_query(F.data.startswith("dad_cluster:"))
async def handle_dad_cluster(callback: CallbackQuery, state: FSMContext) -> None:
    if not await has_dad_access(state):
        await callback.answer("доступ закрыт", show_alert=True)
        return

    cluster = (callback.data or "").removeprefix("dad_cluster:")
    recipes = dad_recipes()

    if cluster != "all":
        recipes = [recipe for recipe in recipes if recipe.get("dad_cluster", "classic") == cluster]

    title = "все омлеты" if cluster == "all" else DAD_CLUSTER_LABELS.get(cluster, cluster)

    async def body() -> None:
        await callback.message.answer(
            f"{title}: выбери рецепт",
            reply_markup=recipe_list_keyboard(recipes, "dad_recipe", "dad_home"),
        )

    await answer_or_alert(callback, body)


@router.callback_query(F.data.startswith("dad_recipe:"))
async def handle_dad_recipe(callback: CallbackQuery, state: FSMContext) -> None:
    if not await has_dad_access(state):
        await callback.answer("доступ закрыт", show_alert=True)
        return

    wanted_id = (callback.data or "").removeprefix("dad_recipe:")
    recipe = find_item(dad_recipes(), wanted_id)

    async def body() -> None:
        if recipe is None:
            await callback.message.answer("не нашла этот омлет", reply_markup=cooking_keyboard())
            return

        await send_recipe(callback.message, recipe, callback.from_user.id if callback.from_user else None)

    await answer_or_alert(callback, body)


@router.callback_query(F.data == "categories_home")
async def handle_categories_home(callback: CallbackQuery, state: FSMContext) -> None:
    recipes = await visible_recipes(state)

    async def body() -> None:
        await callback.message.answer("как будем искать рецепты?", reply_markup=all_categories_keyboard(recipes))

    await answer_or_alert(callback, body)


@router.callback_query(F.data.startswith("category:"))
async def handle_category(callback: CallbackQuery, state: FSMContext) -> None:
    recipes = await visible_recipes(state)
    category_data = (callback.data or "").removeprefix("category:")
    category_name, filtered_recipes = filter_category(recipes, category_data)

    async def body() -> None:
        if not filtered_recipes:
            await callback.message.answer("тут пока пусто", reply_markup=cooking_keyboard())
            return

        await send_recipe_result_list(
            callback.message,
            filtered_recipes,
            state,
            f"{category_name}: {len(filtered_recipes)}",
        )

    await answer_or_alert(callback, body)


@router.callback_query(F.data.startswith("recipe_results:"))
async def handle_recipe_results_page(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        page = int((callback.data or "").removeprefix("recipe_results:"))
    except ValueError:
        page = 0

    data = await state.get_data()
    ids = data.get("recipe_result_ids", [])
    recipes = await visible_recipes(state)
    recipe_by_id = {item_id(recipe): recipe for recipe in recipes}
    found = [recipe_by_id[recipe_id] for recipe_id in ids if recipe_id in recipe_by_id]

    async def body() -> None:
        if not found:
            await callback.message.answer("список устарел, попробуй поиск ещё раз", reply_markup=cooking_keyboard())
            return

        await callback.message.answer(
            f"рецепты: {len(found)}\nстраница {clamp_page(page, len(found), RECIPE_RESULT_LIMIT) + 1}/{page_count(len(found), RECIPE_RESULT_LIMIT)}",
            reply_markup=recipe_results_keyboard(found, page),
        )

    await answer_or_alert(callback, body)


@router.callback_query(F.data.startswith("recipe:"))
async def handle_recipe(callback: CallbackQuery, state: FSMContext) -> None:
    recipes = await visible_recipes(state)
    wanted_id = (callback.data or "").removeprefix("recipe:")
    recipe = find_item(recipes, wanted_id)

    async def body() -> None:
        if recipe is None:
            await callback.message.answer("не нашла этот рецепт", reply_markup=cooking_keyboard())
            return

        await send_recipe(callback.message, recipe, callback.from_user.id if callback.from_user else None)

    await answer_or_alert(callback, body)


@router.callback_query(F.data.startswith("recipe_fav:"))
async def handle_recipe_favorite_toggle(callback: CallbackQuery) -> None:
    wanted_id = (callback.data or "").removeprefix("recipe_fav:")
    recipes = [recipe for recipe in load_recipes() if not is_dad_recipe(recipe)]
    recipe = find_item(recipes, wanted_id)

    if recipe is None:
        await callback.answer("не нашла рецепт", show_alert=True)
        return

    added = toggle_favorite("recipes", callback.from_user.id if callback.from_user else None, wanted_id)
    await callback.answer("добавила в любимые" if added else "убрала из любимых")

    if callback.message:
        try:
            await callback.message.edit_reply_markup(
                reply_markup=recipe_actions_keyboard(recipe, callback.from_user.id if callback.from_user else None)
            )
        except Exception:
            pass


@router.callback_query(F.data == "places_home")
async def handle_places_home_callback(callback: CallbackQuery) -> None:
    async def body() -> None:
        await send_places_dashboard(callback.message, callback.from_user.id if callback.from_user else None)

    await answer_or_alert(callback, body)


@router.callback_query(F.data.startswith("place_group:"))
async def handle_place_filter_group(callback: CallbackQuery) -> None:
    places = load_places()
    group = (callback.data or "").removeprefix("place_group:")

    async def body() -> None:
        if group == "status":
            await callback.message.answer("выбери Анин список:", reply_markup=place_status_keyboard(places))
            return
        if group == "type":
            await callback.message.answer("выбери формат места:", reply_markup=place_type_keyboard(places))
            return
        if group == "metro":
            await callback.message.answer("выбери метро:", reply_markup=place_metro_keyboard(places))
            return

        await callback.message.answer("как хочешь отфильтровать места?", reply_markup=place_filter_home_keyboard())

    await answer_or_alert(callback, body)


@router.callback_query(F.data.startswith("place_filter:"))
async def handle_place_filter(callback: CallbackQuery) -> None:
    places = load_places()
    data = (callback.data or "").removeprefix("place_filter:")
    user_id = callback.from_user.id if callback.from_user else None

    if data == "all":
        filtered_places = places
        title = "все места"
    elif data == "favorites":
        ids = favorite_ids("places", user_id)
        filtered_places = [place for place in places if item_id(place) in ids or place.get("favorite") is True]
        title = "любимые / рекомендации"
    elif data.startswith("status:"):
        status = data.removeprefix("status:")
        filtered_places = [place for place in places if place.get("status") == status]
        title = PLACE_STATUS_LABELS.get(status, status)
    elif data.startswith("metro:"):
        index_text = data.removeprefix("metro:")
        metros = metro_filter_values(places)
        metro = metros[int(index_text)] if index_text.isdigit() and int(index_text) < len(metros) else ""
        filtered_places = [place for place in places if metro and metro in place.get("metro", [])]
        title = f"метро {metro}" if metro else "метро"
    elif data.startswith("type:"):
        place_type = data.removeprefix("type:")
        filtered_places = [place for place in places if place_has_type(place, place_type)]
        title = PLACE_TYPE_LABELS.get(place_type, place_type)
    else:
        filtered_places = places
        title = "места"

    async def body() -> None:
        if not filtered_places:
            await callback.message.answer("тут пока пусто", reply_markup=places_keyboard())
            return

        header = f"{title}: {len(filtered_places)}"
        if len(filtered_places) > PLACE_RESULT_LIMIT:
            header += f"\nпоказываю первые {PLACE_RESULT_LIMIT}; можно уточнить запрос словами"

        await callback.message.answer(
            header,
            reply_markup=places_keyboard(),
        )
        await callback.message.answer(
            "выбери место:",
            reply_markup=place_list_keyboard(filtered_places[:PLACE_RESULT_LIMIT], back_callback="place_group:home"),
        )

    await answer_or_alert(callback, body)


@router.callback_query(F.data.startswith("place:"))
async def handle_place(callback: CallbackQuery) -> None:
    wanted_id = (callback.data or "").removeprefix("place:")
    place = find_item(load_places(), wanted_id)

    async def body() -> None:
        if place is None:
            await callback.message.answer("не нашла это место", reply_markup=places_keyboard())
            return

        await send_place(callback.message, place, callback.from_user.id if callback.from_user else None)

    await answer_or_alert(callback, body)


@router.callback_query(F.data.startswith("place_fav:"))
async def handle_place_favorite_toggle(callback: CallbackQuery) -> None:
    wanted_id = (callback.data or "").removeprefix("place_fav:")
    place = find_item(load_places(), wanted_id)

    if place is None:
        await callback.answer("не нашла место", show_alert=True)
        return

    added = toggle_favorite("places", callback.from_user.id if callback.from_user else None, wanted_id)
    await callback.answer("добавила в любимые" if added else "убрала из любимых")

    if callback.message:
        try:
            await callback.message.edit_reply_markup(
                reply_markup=place_actions_keyboard(place, callback.from_user.id if callback.from_user else None)
            )
        except Exception:
            pass


@router.callback_query(F.data.startswith("favorites:"))
async def handle_favorites_callback(callback: CallbackQuery, state: FSMContext) -> None:
    kind = (callback.data or "").removeprefix("favorites:")
    user_id = callback.from_user.id if callback.from_user else None

    async def body() -> None:
        if kind == "recipes":
            recipes = await visible_recipes(state)
            ids = favorite_ids("recipes", user_id)
            found = [recipe for recipe in recipes if item_id(recipe) in ids]
            if not found:
                await callback.message.answer("любимых рецептов пока нет", reply_markup=cooking_keyboard())
                return
            await send_recipe_result_list(callback.message, found, state, f"любимые рецепты: {len(found)}")
            return

        places = load_places()
        ids = favorite_ids("places", user_id)
        found = [place for place in places if item_id(place) in ids or place.get("favorite") is True]
        if not found:
            await callback.message.answer("любимых мест пока нет", reply_markup=places_keyboard())
            return
        await callback.message.answer(f"любимые места: {len(found)}", reply_markup=places_keyboard())
        await callback.message.answer("выбери место:", reply_markup=place_list_keyboard(found[:PLACE_RESULT_LIMIT]))

    await answer_or_alert(callback, body)


@router.message(F.text)
async def handle_smart_text(message: Message, state: FSMContext) -> None:
    text = message.text or ""
    recipes = await visible_recipes(state)
    places = load_places()
    normalized_text = normalize(text)
    user_id = message.from_user.id if message.from_user else None

    if re.search(r"(любим|избран).*(рецепт)|рецепт.*(любим|избран)", normalized_text):
        ids = favorite_ids("recipes", user_id)
        found = [recipe for recipe in recipes if item_id(recipe) in ids]
        if not found:
            await message.answer("любимых рецептов пока нет. нажми ⭐ под рецептом, и он появится тут.", reply_markup=cooking_keyboard())
            return

        await send_recipe_result_list(message, found, state, f"любимые рецепты: {len(found)}")
        return

    if re.fullmatch(r"(любимое|избранное|любимые)", normalized_text.strip()):
        await message.answer("любимое:", reply_markup=favorites_home_keyboard(user_id))
        return

    if compact_text(text) in {"рецепты", "все рецепты", "что приготовить"}:
        await message.answer("как будем искать рецепты?", reply_markup=all_categories_keyboard(recipes))
        return

    place_filters = parse_place_filters(text, places)
    recipe_filters = parse_recipe_filters(text, recipes)
    place_found = apply_place_filters(places, place_filters)
    recipe_found = apply_recipe_filters(recipes, recipe_filters)

    if has_place_intent(text, place_filters) or (place_found and not recipe_found):
        if is_broad_place_query(text, place_filters):
            await send_places_dashboard(message, user_id)
            return

        await send_place_results(message, places, place_filters, user_id)
        return

    await send_recipe_results(message, recipes, recipe_filters, user_id, state)


@router.message()
async def handle_unknown(message: Message) -> None:
    await message.answer("я пока понимаю текст, кнопки из меню и /start", reply_markup=main_keyboard(message.from_user))


async def main() -> None:
    load_dotenv(BASE_DIR / ".env")
    token = os.getenv("BOT_TOKEN")
    proxy = os.getenv("TELEGRAM_PROXY")

    if not token or token == "your_telegram_bot_token_here":
        raise SystemExit(
            "BOT_TOKEN не найден. Создай файл .env рядом с bot.py и добавь туда BOT_TOKEN=токен_от_BotFather"
        )

    session = AiohttpSession(proxy=proxy) if proxy else None
    bot = Bot(token=token, session=session)
    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher.include_router(router)

    if proxy:
        print("telegram proxy enabled")
    print("бот запущен")
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
