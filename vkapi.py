import requests
from requests.exceptions import RequestException


def read_token(token_file):
    """Чтение токена из файла"""
    try:
        with open(token_file, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        raise Exception(f"Файл с токеном {token_file} не найден")
    except Exception as e:
        raise Exception(f"Ошибка при чтении токена: {str(e)}")


class VKFriendsAPI:
    def __init__(self, token_file='token.txt'):
        self.base_url = "https://api.vk.com/method/"
        self.api_version = "5.199"
        self.access_token = read_token(token_file)

    def _make_api_request(self, method, params):
        """Выполнение запроса к API"""
        params.update({
            'access_token': self.access_token,
            'v': self.api_version
        })

        try:
            response = requests.get(f"{self.base_url}{method}", params=params)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            raise Exception(f"Ошибка API запроса: {str(e)}")

    def resolve_screen_name(self, screen_name):
        """Преобразование короткого имени в user_id"""
        params = {'screen_name': screen_name}
        data = self._make_api_request('utils.resolveScreenName', params)

        if data.get('response', {}).get('type') == 'user':
            return data['response']['object_id']
        return None

    def get_user_id(self, user_input):
        """Получение user_id из ввода пользователя"""
        try:
            return int(user_input)
        except ValueError:
            user_id = self.resolve_screen_name(user_input)
            if user_id:
                return user_id
            raise Exception(f"Не удалось определить ID пользователя по имени '{user_input}'")

    def get_friends(self, user_id, fields='nickname,city'):
        """Получение списка друзей"""
        params = {
            'user_id': user_id,
            'fields': fields,
            'count': 1000  # Максимальное количество друзей за один запрос
        }

        data = self._make_api_request('friends.get', params)

        if 'response' not in data:
            error_msg = data.get('error', {}).get('error_msg', 'Неизвестная ошибка API')
            raise Exception(f"Ошибка при получении друзей: {error_msg}")

        return data['response']['items']

    @staticmethod
    def format_friend_info(friend):
        """Форматирование информации о друге"""
        return (
            f"ID: {friend.get('id')}, "
            f"Ник: {friend.get('nickname', 'нет')}, "
            f"Имя: {friend.get('first_name', 'неизвестно')}, "
            f"Фамилия: {friend.get('last_name', 'неизвестно')}, "
            f"Город: {friend.get('city', {}).get('title', 'неизвестно')}"
        )


def main():
    try:
        vk_api = VKFriendsAPI()

        user_input = input("Введите ID пользователя или короткое имя (например, 'durov'): ").strip()
        user_id = vk_api.get_user_id(user_input)

        print(f"\nПолучаем список друзей для пользователя с ID {user_id}...\n")

        friends = vk_api.get_friends(user_id)

        if not friends:
            print("У этого пользователя нет друзей или доступ ограничен")
            return

        print(f"Найдено {len(friends)} друзей:")
        for i, friend in enumerate(friends, 1):
            print(f"{i}. {VKFriendsAPI.format_friend_info(friend)}")

    except Exception as e:
        print(f"\nОшибка: {str(e)}")


if __name__ == "__main__":
    main()
