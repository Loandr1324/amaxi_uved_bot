import asyncio
from aioabcpapi import Abcp
from config import HOST_API, USER_API, PASSWORD_API, DISTRIB_ID, DICT_CLIENT_CONTRACT
from loguru import logger

host, login, password = HOST_API, USER_API, PASSWORD_API
api = Abcp(host, login, password)


async def search_order_position_to_change(num_order, id_status_old: int or str = '233596') -> list:
    """
    Находим позиции, которые необходимо изменить в заказе
    :param id_status_old: Id статус позиции, которые необходимо изменить
    :param num_order: Номер заказа
    :return:
    """

    try:
        order = await api.cp.admin.orders.get_order(num_order)
        # logger.info(order)

        id_item = [item['id'] for item in order['positions']
                   if (item['statusCode'] == id_status_old and item['distributorId'] in DISTRIB_ID)]
        return [order['userId'], id_item]
    except Exception as ex:
        logger.info(ex)
        logger.info(f"От платформы пришла ошибка '{ex}' при получении данных по заказу {num_order}")
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


async def change_status_pos(order):
    """
    Меняем статусы позиций заказа c "Есть в наличии" на "Готов к выдаче".
    :param order: Номер заказа для изменения статуса позиций.
    :return: result
    """
    # Получить список позиций заказа со статусом "Есть в наличии"
    list_pos = await search_order_position_to_change(order, '233596')
    logger.info(len(list_pos))
    logger.info(list_pos)
    if len(list_pos) == 0:
        logger.info(f"Заказ {order} не содержит позиций со статусом 'Есть в наличии'")
        return False

    # Изменить статус позиций заказа на "Готов к выдаче"
    result = await change_status_position(order, list_pos, '188361')
    logger.info(result)
    return result


async def create_by(id_contract: int, list_id_pos: list, new_status: int or str = '144929'):
    """Создаём отгрузку позиций и переводим их статус в заказе"""
    try:
        result = await api.ts.admin.order_pickings.create_by_old_pos(
            agreement_id=id_contract, account_details_id=8183, loc_id=0,
            pp_ids=list_id_pos, status_id=new_status, done_right_away=1
        )
        logger.info(result)
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

    # Создаем отгрузку по заказу
    result_create = False
    count = 0
    # while not result_create or count < 2:
    #     logger.info(f"{count + 1}-ая попытка создания отгрузки")
    result_create = await create_by(DICT_CLIENT_CONTRACT[id_user], list_pos, '144929')
        # count += 1
    logger.info(result_create)
    return result_create


if __name__ == '__main__':
    # asyncio.run(change_status_pos('125295275'))
    # list_posit = asyncio.run(search_order_position_to_change('124904514', '188361'))
    # user, pos = asyncio.run(search_order_position_to_change('154313232', '144929'))
    # user, pos = asyncio.run(search_order_position_to_change('154313232', '233596'))
    # logger.info(user, pos)
    # logger.info(len(pos))
    result = asyncio.run(create_ship('154442784'))
    logger.info(result)

