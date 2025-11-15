# Установка

## Требования

- Python 3.9+
- pip, uv или poetry

## Установка через pip

```bash
pip install secreton-api-client
```

## Установка через poetry

```bash
poetry add secreton-api-client
```

## Установка через uv

```bash
uv add secreton-api-client
```

## Установка из исходного кода

```bash
git clone https://github.com/klukvaofficial/secreton_api_client_draft.git
cd secreton-api-client
pip install -e .
```

## Проверка установки

```python
import secreton_api_client
print(secreton_api_client.__version__)
```

## Дополнительные зависимости

Библиотека включает все необходимые зависимости:

- `httpx` - для HTTP запросов
- `pydantic` - для валидации данных
- `typing-extensions` - для расширенной поддержки типов

## Следующий шаг

[Перейти к быстрому старту →](quick-start.md)

