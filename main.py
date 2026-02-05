import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message, BotCommand
from aiogram.filters import Command, CommandObject
from config import TOKEN, API_KEY
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import requests
from city import get_cities_for_select, get_city_by_name, RUSSIAN_CITIES




class Form(StatesGroup):
    name = State()
    weight = State()
    height = State()
    age = State()
    gender = State()
    city = State()
    activity = State()
    worker = State()
    
class FormFood(StatesGroup):
    name = State()

class User:
    def __init__(self) -> None:
        self.name = ""
        self.weigth = 0.0
        self.heigth = 0.0
        self.age = 0
        self.gender = ""
        self.city = ""
        self.activity = 0.0
        self.worker = 0.0
        self.lastFood = ""
        self.lastFoodCal = 0.0
        
    def set_arg(self, _name, _w, _h, _a, _gender, _city, _activ, _worker):
        self.name = _name
        self.weigth = _w
        self.heigth = _h
        self.age = _a
        self.gender = _gender
        self.city = _city
        self.activity = _activ
        self.worker = _worker
        
class UserLogs:
    def __init__(self) -> None:
        self.waterNorm = 0.0
        self.drinkWater = 0.0
        self.eatCalories = 0.0
        self.caloriesOut = 0.0
        self.calorNorm = 0.0
    
class Workout:
    def __init__(self, name, cal) -> None:
        self.name = name
        self.caloroutInMinut = cal

mass_workout: dict[str, Workout] = {}
mass_workout['бег'] =   Workout('бег', 10)
mass_workout['футбол'] =   Workout('футбол', 15)
mass_workout['волейбол'] =   Workout('волейбол', 8)        
mass_workout['тренажеры'] =   Workout('тренажеры', 11)    

mass_user: dict[int, User] = {}
mass_userLog: dict[int, UserLogs] = {}



bot = Bot(token=TOKEN) # type: ignore

dp = Dispatcher()

async def set_bot_commands():
    """Устанавливает команды бота в меню"""
    commands = [
        BotCommand(command="start", description="Начать работу"),
        BotCommand(command="help", description="Помощь и команды"),
        BotCommand(command="set_profile", description="Настроить профиль"),
        BotCommand(command="log_water", description="Записать воду"),
        BotCommand(command="log_food", description="Записать еду"),
        BotCommand(command="log_workout", description="Записать тренировку"),
        BotCommand(command="check_progress", description="Показать прогресс")
    ]
    await bot.set_my_commands(commands)
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Добро пожаловать! Я ваш бот для учета каллорий")

# Обработчик команды /help
@dp.message(Command("help"))
async def cmd_help(message: Message):
    help_text = """
<b>Доступные команды:</b>

<b>Основные:</b>
/start - Начать работу с ботом
/help - Показать это сообщение
/set_profile - Создать/обновить профиль

<b>Учет данных:</b>
/log_water количество - Записать выпитую воду (мл)
/log_food название - Записать съеденную еду
/log_workout тип время - Записать тренировку

<b>Просмотр прогресса:</b>
/check_progress - Показать текущий прогресс
/my_profile - Показать данные профиля

<b>Доступные тренировки:</b>
• бег
• футбол
• волейбол
• тренажеры

<b>Примеры:</b>
/log_water 500
/log_food банан
/log_workout бег 30
"""
    await message.answer(help_text, parse_mode="HTML")
    
# STATE-----------------------------------------------------------------------------------
@dp.message(Command("set_profile"))
async def start_form(message: Message, state: FSMContext):
    await message.answer("Как вас зовут?")
    await state.set_state(Form.name)
    
@dp.message(Form.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Какой у вас вес (кг.)?")
    await state.set_state(Form.weight)
    
@dp.message(Form.weight)
async def process_weight(message: Message, state: FSMContext):
    try:
        _weigth = float(message.text) # type: ignore
        if _weigth < 20 or _weigth > 300:
            await message.answer("Пожалуйста, введите реальный вес (20-300 кг)!")
            return
        await state.update_data(weigth=_weigth)
        await message.answer("Какой у вас рост (см)?")
        await state.set_state(Form.height)
    except ValueError:
        await message.answer("Пожалуйста, введите число!")
    
@dp.message(Form.height)
async def process_height(message: Message, state: FSMContext):
    try:
        _height = float(message.text) # type: ignore
        if _height < 100 or _height > 250:
            await message.answer("Пожалуйста, введите реальный рост (100-250 см)!")
            return
        await state.update_data(height=_height)
        await message.answer("Какой у вас возраст?")
        await state.set_state(Form.age)
    except ValueError:
        await message.answer("Пожалуйста, введите число!")    

@dp.message(Form.age)
async def process_age(message: Message, state: FSMContext):
    try:
        _age = float(message.text) # type: ignore
        if _age < 10 or _age > 120:
            await message.answer("Пожалуйста, введите реальный рост (10-120 лет)!")
            return
        await state.update_data(age=_age)
        await message.answer("Какой у вас пол (male/female)")
        await state.set_state(Form.gender)
    except ValueError:
        await message.answer("Пожалуйста, введите число!")  
 
@dp.message(Form.gender)
async def process_gender(message: Message, state: FSMContext):
    _gender = message.text.lower() # type: ignore
    if _gender != 'male' and _gender != 'female':
        await message.answer("Пожалуйста, введите ваш пол (male/female)!")
        return
    await state.update_data(gender=_gender)
    await message.answer("В каком городе вы живете?")
    await state.set_state(Form.city)
    
@dp.message(Form.city)
async def process_city(message: Message, state: FSMContext):
    _city = message.text # type: ignore
    _city = _city.capitalize() # type: ignore
    if not(_city in get_cities_for_select()):
        await message.answer(f"Пожалуйста, введите ваш город из {get_cities_for_select()}")
        return
    await state.update_data(city=_city)
    await message.answer("Какая ваша цель активности (мин.)?")
    await state.set_state(Form.activity) 
    
@dp.message(Form.activity)
async def process_activity(message: Message, state: FSMContext):
    try:
        _activ = int(message.text) # type: ignore
        await state.update_data(activity=_activ)
        await message.answer("Кем вы работайте?")
        await state.set_state(Form.worker)
    except ValueError:
        await message.answer("Пожалуйста, введите число!")


@dp.message(Form.worker)
async def process_worker(message: Message, state: FSMContext):
    try:
        _calor = message.text # type: ignore
        await state.update_data(worker=_calor)
        data = await state.get_data()
        if message.from_user.id in mass_user: # type: ignore
            mass_user[message.from_user.id].set_arg(data.get("name"),data.get("weigth"),data.get("height"),data.get("age"), data.get("gender"),data.get("city"), data.get("activity"), data.get("worker")) # type: ignore
        else:
            user = User()
            userLog = UserLogs()
            user_id = message.from_user.id # type: ignore
            user.set_arg(data.get("name"),data.get("weigth"),data.get("height"),data.get("age"), data.get("gender"),data.get("city"), data.get("activity"), data.get("worker"))
            mass_user[user_id] = user # type: ignore
            mass_userLog[user_id] = userLog # type: ignore
            temper = requestTemperat(user.city)
            if temper != None:
                mass_userLog[user_id].waterNorm = calc_water(user.weigth,user.activity,temper)
            else:
                message.answer("Не смог узнать температуру, рассчитаю данные без нее")
                mass_userLog[user_id].waterNorm = calc_water(user.weigth,user.activity,0)
            mass_userLog[user_id].calorNorm = calc_calories(user.weigth,user.heigth,user.age, user.gender)
        await message.answer("Данные сохранены")
        await state.clear()
    except ValueError:
        await message.answer("Пожалуйста, введите число!")  
#------------------------------------------------------------------------------------------

@dp.message(Command("log_water"))
async def log_water(message: Message, command : CommandObject):
    if command.args is None:
        await message.answer("Ошибка: не переданы аргументы")
        return
    user_id = message.from_user.id # type: ignore
    if user_id in mass_userLog:
        data = command.args
        data = data.split()
        if len(data) > 1:
            await message.answer("Ошибка: введите 1 число")
            return
        
        try:
            waterF = float(data[0])
            mass_userLog[user_id].drinkWater += waterF
            await message.answer("Записал!")
        except ValueError:
            await message.answer("Пожалуйста, введите число!")
            return
    else:
        await message.answer("Ошибка: cначала необходимо завести профиль (set_profile)")
        return
        
@dp.message(Command("log_food"))
async def log_food(message: Message, command : CommandObject, state: FSMContext):
    if command.args is None:
        await message.answer("Ошибка: не переданы аргументы")
        return
    user_id = message.from_user.id # type: ignore
    if user_id in mass_userLog:
        data = command.args
        data = data.split()
        if len(data) > 1:
            await message.answer("Ошибка: введите 1 название")
            return
        try:
            foodname = data[0]
            calor = request_food(foodname)
            if calor != None:
                mass_user[message.from_user.id].lastFoodCal = calor # type: ignore
                await message.answer(f"{foodname} - {calor}. Сколько грамм вы съели?")
                await state.set_state(FormFood.name)
            else:
                await message.answer(f"Не смог определить {foodname}") 
        except ValueError:
            await message.answer("Я не смог определить сколько каллорий в этой еде!")
            return
    else:
        await message.answer("Ошибка: cначала необходимо завести профиль (set_profile)")
        return    
    
@dp.message(FormFood.name)
async def process_nameFood(message: Message, state: FSMContext):
    if message.text == None:
        await message.answer(f"Сколько грамм вы съели?")
    try:
        gramm = float(message.text) # type: ignore
    except ValueError:
        await message.answer("Введите число!!")
        return
    grammCal = gramm * (mass_user[message.from_user.id].lastFoodCal / 100) # type: ignore
    mass_userLog[message.from_user.id].eatCalories += grammCal # type: ignore
    await message.answer(f"Записано: {grammCal}")
    await state.clear()

@dp.message(Command("log_workout"))
async def log_workout(message: Message, command : CommandObject, state: FSMContext):
    if command.args is None:
        await message.answer("Ошибка: не переданы аргументы")
        return
    user_id = message.from_user.id # type: ignore
    if user_id in mass_userLog:
        data = command.args
        data = data.split()
        if len(data) > 2:
            await message.answer("Ошибка: введите название тренировки и длительность")
            return
        try:
            workname = data[0]
            worktime = int(data[1])
            if workname.lower() in mass_workout:
                water = calc_water_work(worktime)
                mass_userLog[user_id].caloriesOut += mass_workout[workname.lower()].caloroutInMinut * worktime
                mass_userLog[user_id].waterNorm += water
                await message.answer(f"{workname} {worktime} минут - {mass_workout[workname.lower()].caloroutInMinut * worktime} ккал. Дополнительно выпейте {water} мл воды.")
                
            else:
                await message.answer(f"Доступен расчет по тренировкам: {mass_workout.keys()}")
                return
        except ValueError:
            await message.answer("Ошибка: введите название тренировки и длительность! Пример: (футбол 30)")
            return
    else:
        await message.answer("Ошибка: cначала необходимо завести профиль (set_profile)")
        return 

@dp.message(Command("check_progress"))
async def check_progress(message: Message, command : CommandObject, state: FSMContext):
    user_id = message.from_user.id # type: ignore
    if user_id in mass_userLog:
        drinkWater = mass_userLog[user_id].drinkWater
        normWater = mass_userLog[user_id].waterNorm
        caleat = mass_userLog[user_id].eatCalories
        calNorm = mass_userLog[user_id].calorNorm
        ostaWat = normWater - drinkWater if normWater - drinkWater > 0 else 0
        calout = mass_userLog[user_id].caloriesOut
        resCal = caleat - calout
        otvet = f"Прогресс\nВода:\n- Выпито: {drinkWater} из {normWater} мл.\n- Осталось: {ostaWat} мл.\n\n"
        otvet += f"Калории:\n-Потреблено: {caleat} ккал из {calNorm} ккал.\n- Сожжено {calout} ккал.\n-Баланс {resCal} ккал."
        await message.answer(f"{otvet}")
    else:
        await message.answer("Ошибка: cначала необходимо завести профиль (set_profile)")
        return

#calc--------------------------------------------------------------------------------------
def calc_water(weigth, activity_now, temperature):
    res = 30.0 * weigth + (activity_now // 30) * 500
    if temperature > 25:
        res += 1000
    return res

def calc_water_work(time):
    return (time // 30) * 200

def calc_calories(weigth,height,age, gender):
    res = 10 * weigth + 6.25 * height - 5 * age
    if gender == 'male':
        res += 500
    else:
        res += 200
    return res
    
def requestTemperat(city):
    
    API_URL = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=ru"
    response = requests.get(API_URL) 
    if response.status_code == 401:
        error_data = response.json()
        return None
    data_from_API = response.json()
    temper = data_from_API['main']['temp']
    return temper

def request_food(product_name: str):

    search_url = "https://world.openfoodfacts.org/cgi/search.pl"
    search_params = {
        "search_terms": product_name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 5  # Берем первые 5 результатов
    }
    
    try:
        response = requests.get(search_url, params=search_params, timeout=10)
        response.raise_for_status()
        search_data = response.json()
        
        if not search_data.get("products"):
            return None
        
        first_product = search_data["products"][0]
        product_code = first_product.get("code")
        
        if not product_code:
            return None
        
        product_url = f"https://world.openfoodfacts.org/api/v2/product/{product_code}"
        product_response = requests.get(product_url, timeout=10)
        product_response.raise_for_status()
        product_data = product_response.json()
        
        if product_data.get("status") != 1:
            return None
        
        product = product_data["product"]
        
        calories = product.get("nutriments", {}).get("energy-kcal_100g")
        
        if calories is None:
            calories = product.get("nutriments", {}).get("energy_100g")
            if calories is not None:
                
                calories = calories / 4.184
    
        if calories is not None:
            return calories
        else:
            return None
            
    except requests.exceptions.RequestException as e:
        return None
    except Exception as e:
        return None


async def main():
    print("Бот запущен!")
    await set_bot_commands()
    await dp.start_polling(bot)
    
    
    
if __name__ == "__main__":
    asyncio.run(main())



