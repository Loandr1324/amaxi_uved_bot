import asyncio
from aioabcpapi import Abcp
from config import HOST_API, USER_API, PASSWORD_API, DISTRIB_ID, DICT_CLIENT_CONTRACT
from loguru import logger

host, login, password = HOST_API, USER_API, PASSWORD_API
api = Abcp(host, login, password)


async def search_order_position_to_change(
        num_order: int or str,
        id_status_old: int or str = '233596',
        check_distributor: bool = True
) -> list:
    """
    Находим позиции, которые необходимо изменить в заказе

    :param num_order: Номер заказа
    :param id_status_old: Id статус позиции, которые необходимо изменить
    :param check_distributor: Проверять ли принадлежность дистрибьютору
    :return: [userId, list_of_position_ids]
    """

    try:
        order = await api.cp.admin.orders.get_order(num_order)

        id_item = []
        for item in order['positions']:
            # Базовая проверка статуса
            if item['statusCode'] != id_status_old:
                continue

            # Проверка дистрибьютора (если требуется)
            if check_distributor and item['distributorId'] not in DISTRIB_ID:
                continue

            id_item.append(item['id'])

        return [order['userId'], id_item]

    except Exception as ex:
        logger.error(f"Ошибка при получении данных по заказу {num_order}: {ex}")
        return [0, []]


async def change_status_position(num_order, list_id_pos: list, new_status: int or str = '188361'):
    """
    Меняем статусы позиций заказа
    :param num_order: номер заказа
    :param new_status: новый статус позиции
    :param list_id_pos: список id позиций
    :return:
    """
    list_positions = [{'id': item, 'statusCode': new_status} for item in list_id_pos]
    logger.info(list_positions)
    try:
        result = await api.cp.admin.orders.create_or_edit_order(number=num_order, order_positions=list_positions)
        logger.info(result)
        return True
    except Exception as ex:
        logger.info(ex)
        logger.info(f"От платформы пришла ошибка '{ex}' при получении данных по заказу {num_order}")
        return False


async def change_status_pos(order, id_status_old='233596', id_new_status='188361', check_distributor: bool = True):
    """
    Меняем статусы позиций заказа с id_status_old на id_new_status
    :param order: Номер заказа для изменения статуса позиций
    :param id_status_old: идентификатор статуса позиций для изменения
    :param id_new_status: идентификатор нового статуса для позиций
    :param check_distributor: проверять ли принадлежность дистрибьютору
    :return: result
    """
    # Получить список позиций заказа со статусом id_status_old
    id_user, list_pos = await search_order_position_to_change(order, id_status_old, check_distributor=check_distributor)
    logger.info(len(list_pos))
    logger.info(list_pos)
    if len(list_pos) == 0:
        logger.info(f"Заказ {order} не содержит позиций со статусом {id_status_old}")
        return False

    # Изменить статус позиций заказа на id_new_status
    result = await change_status_position(order, list_pos, id_new_status)
    logger.info(result)
    return result


async def create_by(id_contract: int, list_id_pos: list, new_status: int or str = '144929'):
    """Создаём отгрузку позиций и переводим их статус в заказе"""
    try:
        result = await api.ts.admin.order_pickings.create_by_old_pos(
            agreement_id=id_contract, account_details_id=8183, loc_id=0,
            pp_ids=list_id_pos, status_id=new_status, done_right_away=1
        )
        # logger.info(result)
        return True
    except Exception as ex:
        logger.info(ex)
        logger.info(f"От платформы пришла ошибка '{ex}' при создании отгрузки по позициям {list_id_pos}")
        return False


async def create_ship(order):
    """
    Создаем отгрузку по заказу.
    :param order: Номер заказа для создания отгрузки
    :return: result
    """
    # Получить список позиций заказа со статусом "Есть в наличии"
    id_user, list_pos = await search_order_position_to_change(order, '233596')
    logger.info(len(list_pos))
    logger.info(list_pos)
    if len(list_pos) == 0:
        logger.info(f"Заказ {order} не содержит позиций со статусом 'Есть в наличии'")
        return False

    # Получаем договор клиента
    user_agreement = DICT_CLIENT_CONTRACT.get(id_user)

    # Если договор не найден, то запрашиваем по API
    if not user_agreement:
        try:
            user_agreement = await get_agreement(id_user)
        except BaseException as ex:
            logger.error(f"Не удалось получить договор по API: {ex}")
            return None

    # Создаем отгрузку по заказу
    result_create = await create_by(user_agreement, list_pos, '144929')
    if not result_create:
        logger.info(f"Первая попытка создания отгрузки не удалась. Выполняем вторую попытку.")
        result_create = await create_by(user_agreement, list_pos, '144929')
    logger.info(result_create)
    return result_create


async def get_agreement(id_user: str) -> int | None:
    """
    Получаем список договоров по API от ABCP
    :param id_user: Идентификатор клиента на платформе ABCP
    :return: ID первого договора или None, если договоров нет или произошла ошибка
    """
    try:
        list_agreement = await api.ts.admin.agrements.get_list(contractor_ids=id_user)

        # Проверяем, что это словарь и содержит ключ 'list'
        if not isinstance(list_agreement, dict):
            return None

        list_agreement = list_agreement.get('list')
        return list_agreement[0]['id'] if list_agreement else None

    # Записываем ошибки при запросе договора
    except Exception as ex:
        logger.error(f"Произошла ошибка при запросе договора {ex=}")
        return None


if __name__ == '__main__':
    # asyncio.run(change_status_pos('125295275'))
    # list_posit = asyncio.run(search_order_position_to_change('124904514', '188361'))
    # user, pos = asyncio.run(search_order_position_to_change('154313232', '144929'))
    # user, pos = asyncio.run(search_order_position_to_change('154313232', '233596'))
    # logger.info(user, pos)
    # logger.info(len(pos))
    # result = asyncio.run(create_ship('154442784'))
    # for key in DICT_CLIENT_CONTRACT.keys():
    #
    #     result = asyncio.run(get_agreement(key))
    #     logger.error(f"{DICT_CLIENT_CONTRACT[key]=}")
    #     logger.error(f"{result=}")
    logger.info(f"Используем для тестов")
