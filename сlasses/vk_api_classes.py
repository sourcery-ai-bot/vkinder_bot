import os
import time
from datetime import datetime, date
import requests
from сlasses.vk_api_constants import RATINGS


# DTO classes
from сlasses.vkinder_bot_constants import PHRASES


class ApiCity:
    def __init__(self, row: dict):
        self.id = row.get('id', None)
        self.title = row.get('title', None)
        self.area = row.get('area', None)
        self.region = row.get('region', None)


class ApiCountry:
    def __init__(self, row: dict):
        self.id = row.get('id', None)
        self.title = row.get('title', None)


class ApiPhoto:
    def __init__(self, row: dict):
        self.url = row.get('url', None)
        self.likes_count = row.get('likes_count', None)
        self.comments_count = row.get('comments_count', None)
        self.reposts_count = row.get('reposts_count', None)
        self.owner_id = row.get('owner_id', None)
        self.id = row.get('id', None)


class VKinderSearch:
    def __init__(self):
        self.id = None
        self.sex_id = None
        self.status_id = None
        self.min_age = None
        self.max_age = None
        self.city_id = None
        self.city_name = None


class ApiUser:
    def __init__(self, row: dict = None, rating_id: int = RATINGS['new']):
        if row is None:
            row = {}
        self.vk_id = str(row.get('id', None))
        self.fname = row.get('first_name', None)
        self.lname = row.get('last_name', None)
        self.sex_id = row.get('sex', None)
        self.is_closed = row.get('is_closed', None)
        # hardcoded country ID
        self.country_id = row.get('country', {}).get('id', 1)
        self.country_name = row.get('country', {}).get('title', 'Россия')
        self.city_id = row.get('city', {}).get('id', 1)
        self.city_name = row.get('city', {}).get('title', 'Россия')
        self.hometown = row.get('home_town', None)
        self.domain = row.get('domain', None)
        self.last_seen_time = row.get('last_seen', {}).get('time', None)
        self.db_id = None
        self.rating_id = rating_id
        self.photos: list[ApiPhoto] = []
        bdate = row.get('bdate', None)
        if bdate:
            bdate = decode_date_from_str(bdate)
            self.birth_day = bdate['birth_day']
            self.birth_month = bdate['birth_month']
            self.birth_year = bdate['birth_year']
            self.age = bdate['age']
            self.birth_date = bdate['birth_date']
        else:
            self.birth_day = None
            self.birth_month = None
            self.birth_year = None
            self.age = None
            self.birth_date = None


class VKinderClient(ApiUser):
    def __init__(self, user: ApiUser):
        super().__init__()
        self.__dict__.update(user.__dict__)
        self._found_user_iter = -1
        self._status = 0
        self.rating_filter = RATINGS['new']
        self._search = VKinderSearch()
        self.searches = []
        self.found_cities: list[ApiCity] = []
        self.found_countries: list[ApiCountry] = []
        self._found_users: list[ApiUser] = []
        self.last_contact = datetime.now()
        self.active_user: ApiUser = None

    # this prevents to import VKinderSearch in main modules
    def reset_search(self):
        self.search = VKinderSearch()

    def get_next_user(self) -> ApiUser:
        while self._found_user_iter < len(self._found_users)-1:
            self._found_user_iter += 1
            if self._found_users[self._found_user_iter].rating_id == self.rating_filter:
                return self._found_users[self._found_user_iter]

    @property
    def search(self):
        return self._search

    # here we also resets found users list
    @search.setter
    def search(self, value):
        self._search = value
        self.found_users = []

    @property
    def found_users(self):
        return self._found_users

    @found_users.setter
    def found_users(self, value):
        self._found_user_iter = -1
        self._found_users = value

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self.last_contact = datetime.now()
        self._status = value


def decode_date_from_str(datestr: str) -> dict:
    """
    Decode VK birth date
    :param datestr: string in format "D.M.YYYY" or "D.M"
    :return: dictionary {'birth_year': 0, 'birth_month': 0, 'birth_day': 0, 'age': 0, 'birth_date': date}
    """
    bdate = datestr.split('.') if datestr else []
    # extending list to prevent index out of range if received not full birth date (D.M.YYYY or D.M)
    bdate.extend([None, None, None])
    birth_day = int(bdate[0]) if bdate[0] else bdate[0]
    birth_month = int(bdate[1]) if bdate[1] else bdate[1]
    birth_year = int(bdate[2]) if bdate[2] else bdate[2]
    age = None
    birth_date = None
    if birth_year:
        age = calculate_age(birth_day, birth_month, birth_year)
        birth_date = date(birth_year, birth_month, birth_day)
    return {'birth_year': birth_year, 'birth_month': birth_month, 'birth_day': birth_day, 'age': age,
            'birth_date': birth_date}


def calculate_age(birth_date, birth_month, birth_year: int) -> int:
    """
    Determines the number of full years since the passed date till present time
    """
    today = date.today()
    return today.year - birth_year - ((today.month, today.day) < (birth_month, birth_date))


def decorator_speed_meter(is_debug_mode=True):
    """
    Measures working time of called function
    """
    def decorator_func(target_function):
        def wrapper_func(*args, **kwargs):
            start_time = time.time()
            result = target_function(*args, **kwargs)
            if is_debug_mode:
                log(f'{target_function.__name__}: {time.time() - start_time} sec', is_debug_mode)
            return result
        return wrapper_func
    return decorator_func


def break_str(s: str, break_chars: list[str] = None, max_size: int = 4096) -> list[str]:
    """
    Split string into chunks with given max size, splitting done by line break, whitespace, comma or by given signs
    """
    if break_chars is None:
        break_chars = ['\n', ' ', ',']
    result = []
    start = 0
    end = max_size + 1
    while True:
        sample = s[start:end]
        if len(sample) < max_size:
            result.append(sample)
            break
        pos = -1
        for char in break_chars:
            pos = sample.rfind(char)
            if pos > -1:
                break
        if pos == -1:
            result.append(sample)
            start += max_size
            end += max_size + 1
        else:
            result.append(sample[:pos + 1])
            start += pos + 1
            end = start + max_size
    return result


def timestamp_to_str(timestamp: int) -> int:
    """
     Determines the number of days since the passed date till present time
    """
    return (datetime.today() - datetime.utcfromtimestamp(timestamp)).days


def last_seen(timestamp: int) -> str:
    """
    Human readable time that elapsed since given timestamp till present time
    """
    result = ''
    if timestamp is None:
        return result
    result = PHRASES['last_seen']
    days_ago = timestamp_to_str(timestamp)
    if days_ago == 0:
        result += PHRASES['today']
    elif days_ago == 1:
        result += PHRASES['yesterday']
    elif days_ago == 2:
        result += PHRASES['day_before_yesterday']
    elif 3 <= days_ago <= 7:
        result += PHRASES['at_this_week']
    elif 31 <= days_ago <= 365:
        result += PHRASES['x_months_ago'].format(int(days_ago / 30))
    elif days_ago >= 366:
        result += PHRASES['x_years_ago'].format(int(days_ago / 365))
    else:
        result += PHRASES['x_days_ago'].format(days_ago)
    return result


def log(message, is_debug_msg=False, sep='\n'):
    """
    Log messages to console if debug message flag set
    """
    if is_debug_msg:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
        if type(message) in [list, dict, tuple, set]:
            message = [f'{now} - {x}' for x in message]
            print(*message, sep=sep)
        else:
            print(f'{now} - {message}', sep=sep)
    else:
        return


def get_filetype_by_url(url: str) -> str:
    """
    Recognize file extension by it's MIME code returned by server, returns extension with preceding dot sign
    https://ru.wikipedia.org/wiki/%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA_MIME-%D1%82%D0%B8%D0%BF%D0%BE%D0%B2
    """
    extension = ''
    if not url:
        return extension
    response = requests.head(url)
    if not (200 <= response.status_code < 300):
        return extension
    file_type = response.headers.get('Content-Type', '')
    return extract_filetype(file_type)


def extract_filetype(content_type_str: str):
    """
    Extract exact MIME type from Content-Type, returns second MIME if Content-Type is complex (i.e. image/jpeg)
    """
    pos = content_type_str.find('/')
    if pos < 0:
        return '.' + content_type_str
    return '.' + content_type_str[pos + 1:]


def solve_filename_conflict(name: str, extension: str, folder: str = ''):
    """
    Calculates next available file name if desired file name is already taken
    """
    folder = folder + os.sep if folder else ''
    path = f'{os.path.abspath(os.getcwd())}{os.sep}{folder + os.sep if folder else ""}'
    tmp_name = name
    filename = f'{tmp_name}{extension}'
    i = 0
    postfix = '_'
    while os.path.isfile(path + filename):
        i += 1
        tmp_name = f'{name}{postfix}{i}'
        filename = f'{tmp_name}{extension}'
    return tmp_name


def prepare_params(*args):
    """
    Normalize all parameters that can be passed as integer or mixed list of integers and strings,
    and makes from them one string that can be accepted as request parameter
    :param args: integer, string or list of integers and string
    :return: string with values separated by commas
    """
    result = []
    for param in args:
        if param is None:
            continue
        if type(param) in [int, bool, float]:
            result += [str(param)]
        elif type(param) is str:
            result += [param]
        elif type(param) in [list, dict, tuple, set]:
            result += [','.join(str(x) for x in param)]
    result = ','.join(result)
    return result


def clear_db(sqlalchemy, engine):
    """
    Drops all tables in DB
    :param sqlalchemy: sqlalchemy instance
    :param engine: db engine
    :return: none
    """
    inspect = sqlalchemy.inspect(engine)
    for table_entry in reversed(inspect.get_sorted_table_and_fkc_names()):
        table_name = table_entry[0]
        if table_name:
            with engine.begin() as conn:
                conn.execute(sqlalchemy.text(f'DROP TABLE "{table_name}"'))
    return


def read_textfile(filename: str) -> str:
    """
    Reads text file
    :param filename: name of file with query
    :return: text of query
    """
    query_file = open(filename, mode='rt', encoding='utf-8')
    query_text = ''.join(query_file.readlines())
    query_file.close()
    return query_text


def get_users_ratings_counts(users: list[ApiUser]) -> dict:
    """
    Counts total ratings of all found users and return as dict {'new': 0, 'liked': 0, 'disliked': 0, 'banned': 0}
    """
    result = {'new': 0, 'liked': 0, 'disliked': 0, 'banned': 0}
    for user in users:
        result[get_dict_key_by_value(RATINGS, user.rating_id)] += 1
    return result


def get_dict_key_by_value(dictionary: dict, value):
    """
    Find and return key of element in dictionary by its value
    """
    for dict_key, dict_value in dictionary.items():
        if dict_value == value:
            return dict_key


def format_city_name(city: ApiCity) -> str:
    """
    Prepare city info for showing in huge lists
    """
    tmp = ', '.join([x for x in [city.area, city.region] if x])
    result = f'{city.title}{" (" + tmp + ")" if tmp else ""}'
    return result
