from typing import Type, Mapping, Any, Optional, List, TypeVar

from sqlalchemy import Column, update
from sqlalchemy.orm import joinedload
from loguru import logger

from src.database.engine import Session
from src.database.models import Base, Payment, User, Devices
from src.database.db_selectors import handle_sqlalchemy_error

T = TypeVar('T', bound=Base)

# Маппинг модели на её связи для joinedload
joinedload_map = {
    Payment: [Payment.user, Payment.device],
    User: [
        User.devices,
        User.payments,
        User.referrals,  # 👈 Все, кого он пригласил
    ],
    Devices: [Devices.user, Devices.payments],
    # добавь свои модели и связи
}


@handle_sqlalchemy_error
def create_object(model: Type[T], expunge: bool = True, **kwargs: Any) -> T:
    """
    Создание объекта.

    :param model: Модель таблицы в БД
    :param expunge: Удалять ли объект из сессии перед возвратом
    :param kwargs: параметры для создания объекта
    :return: созданный объект или исключение
    """
    with Session() as session:
        for key, value in kwargs.items():
            if isinstance(value, Base):
                kwargs[key] = session.merge(value)

        obj = model(**kwargs)
        session.add(obj)
        session.commit()
        session.refresh(obj)

        if model in joinedload_map:
            query = session.query(model)
            for relation in joinedload_map[model]:
                query = query.options(joinedload(relation))

            pk_key = model.__mapper__.primary_key[0].key
            pk_value = getattr(obj, pk_key)

            obj = query.filter(getattr(model, pk_key) == pk_value).one()

        if expunge:
            session.expunge(obj)

        logger.info(f'Объект модели-{model.__name__} создан с подгрузкой связей.')
        return obj


@handle_sqlalchemy_error
def delete_object(del_object: Optional[Base]) -> bool:
    """
    Функция удаление объекта
    :param del_object: Объект БД для удаления
    :return: True, если удаление прошло успешно, иначе False
    """
    with Session() as session:
        obj = session.merge(del_object)
        session.delete(obj)
        session.commit()
        logger.warning(f'Объект был удален из БД {del_object.__dict__}')
        return True


@handle_sqlalchemy_error
def delete_by_attribute(model: Type[T], attr_name: str, attr_value: Any) -> bool:
    """
    Удаление объекта по определенному значению его поля.

    :param model - модель таблицы
    :param attr_name - имя поля
    :param attr_value - значение поля для поиска
    """
    with Session() as session:
        attr: Column = getattr(model, attr_name)
        db_obj = session.query(model).filter(attr == attr_value).first()
        if not db_obj:
            logger.error(f'Объект не найден в БД-{model.__name__} - {attr_name}:{attr_value}')
            return False
        session.delete(db_obj)
        session.commit()
        return True


@handle_sqlalchemy_error
def get_all_objects_model(model: Type[T]) -> Optional[List[T]]:
    """
    Возвращает все объекты данной модели
    :param model: Модель, для которой нужно получить объекты
    :return: Список объектов модели
    """
    with Session() as session:
        relationships = joinedload_map.get(model, [])
        result = session.query(model).options(
            *[joinedload(rel) for rel in relationships]
        ).all()
        for obj in result:
            session.expunge(obj)
        return result


@handle_sqlalchemy_error
def get_by_attribute(model: Type[T], attr_name: str, attr_value: Any) -> Optional[T]:
    """
    Получение объекта по определенному значению его поля.

    :param model - модель таблицы в БД
    :param attr_name - имя атрибута для поиска
    :param attr_value - значение атрибута для поиска

    :return db_obj - Найденный объект или None при ошибке или его отсутствии
    """
    with Session() as session:
        attr: Column = getattr(model, attr_name)
        relationships = joinedload_map.get(model, [])
        db_obj = session.query(model).options(
            *[joinedload(rel) for rel in relationships]).filter(attr == attr_value).first()
        if not db_obj:
            logger.error(f'Объекта в БД не найдено модель-{model.__name__} - {attr_name}: {attr_value}')
            return None
        session.expunge(db_obj)
        return db_obj


@handle_sqlalchemy_error
def update_attribute(
        model: Type[T], search_attr_name: str,
        search_attr_value: Any, **kwargs: Mapping[str, Any]) -> bool:
    """
    Функция обновления полей объекта в таблице БД

    :param model - модель таблицы в БД
    :param search_attr_name - имя столбца для поиска объекта
    :param search_attr_value - значения столбца для поиска объекта
    :param kwargs - именованные аргументы для изменения

    :return True- при успешном изменении. False - при ошибках в изменении объекта
    """
    with Session() as session:
        attr: Column = getattr(model, search_attr_name)
        sql = update(model).where(attr == search_attr_value).values(**kwargs)
        result = session.execute(sql)
        if result.rowcount:
            session.commit()
            return True
        return False


@handle_sqlalchemy_error
def update_attribute_object(obj: T) -> bool:
    """
    Обновление полей конкретного объекта

    :param obj - объект с уже измененными параметрами для сохранения в БД
    :return True- При корректном обновлении объекта False- при ошибке
    """
    with Session() as session:
        session.merge(obj)
        session.commit()
        return True
