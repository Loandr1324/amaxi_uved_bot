# import requests
# from config import HOST_API, USER_API, PASSWORD_API
#
#
# class ApiAbcpAuth:
#     def __init__(self):
#         self.host = HOST_API
#         self.user = USER_API
#         self.password = PASSWORD_API
#
#
# class ApiAbcp(ApiAbcpAuth):
#
#     def get_order(self, order_id: str) -> dict:
#         url = f"https://{self.host}/cp/order?userlogin={self.user}&userpsw={self.password}&number={order_id}"
#         response = requests.get(url)
#         return response.json()
#
#     def post_order_change_status_all_position(
#             self,
#             order_id: str,
#             count_pos: int or str,
#             status_code: int or str
#     ) -> dict:
#         """
#         userlogin=username
#         &userpsw=md5pass
#         &order[number]=5623478
#         &order[internalNumber]=786593
#         &order[positions][0][statusCode]=15
#         &order[positions][0][id]=653463
#         &order[positions][0][quantity]=10
#         &order[notes][0][value]=текст заметки
#         :param status_code: statusCode на платформе abcp, который устанавливаем на позициях заказа
#         :param count_pos: количество позиций в заказе
#         :param order_id: номер заказа на платформе abcp
#         :return:
#         """
#         try:
#             count_pos = int(count_pos)
#             status_code = int(status_code)
#         except ValueError as ve:
#             print('Не смог перевести значение count_pos или status_code в число. Передайте число')
#         if len(status_code) != 6:
#             print('Введён не корректный statusCode')
#         position = ''
#         for i in range(count_pos):
#             position = position + f'&order[positions][{i}][statusCode]={status_code}'
#         url = f"https://{self.host}/cp/order?userlogin={self.user}&userpsw={self.password}" \
#               f"&order[number]={order_id}{position}"
#         print(url)
#         response = requests.post(url)
#         return response.json()
#
#
# class ApiTSAbcp(ApiAbcpAuth):
#     def pass_one(self):
#         """
#         создать по API отгрузку на все позиции заказа
#         (документация Операция для создания отгрузки: https://clck.ru/32sFH8),
#         сразу завершить отгрузку (флаг doneRightAway.)
#         и присвоить все позициям статус типа “выдан”, с позициями заказа НЕ связывать
#         /cp/ts/orderPickings/createByOldPos
#         Параметры POST
#         userlogin=username
#         &userpsw=md5pass
#         &opId=33
#         &statusId=4444
#         &agreementId=1
#         &accountDetailsId=1
#         &locId=33
#         &doneRightAway=1
#         &ppIds[]=123123123
#         &ppIds[]=234234234
#         :return:
#         """
#
#         url = f"https://{self.host}/cp/ts/orderPickings/createByOldPos?userlogin={self.user}&userpsw={self.password}&number={order_id}"
#         response = requests.post(url)
#         return response.json()
#         pass
#
#
# if __name__ == "__main__":
#     a = ApiAbcp()
#     result = a.get_order('121603536')
#     print(result)
#     # result = a.post_order_change_status_all_position('121591753', 1, 188361)
#     # result = a.post_order_change_status_all_position('121591753', 5, 188361)
#     # print(result)
# """
# {
#     'number': '121591753',
#     'internalNumber': '',
#     'date': '2023-03-05 12:48:56',
#     'comment': '',
#     'userId': '6644958',
#     'dateUpdated': '2023-03-05 12:49:01',
#     'profileId': '5939998',
#     'deliveryAddressId': '0',
#     'deliveryAddress': 'Самовывоз',
#     'deliveryOfficeId': '0',
#     'deliveryOffice': None,
#     'deliveryTypeId': '0',
#     'deliveryType': None,
#     'deliveryCost': '0',
#     'paymentTypeId': '19084',
#     'shipmentDate': '0000-00-00 00:00:00',
#     'debt': '4200.00',
#     'basketId': '0',
#     'basketName': 'текучка',
#     'paymentType': 'Наличный',
#     'userName': 'Сотрудник',
#     'userFullName': '',
#     'userCode': '',
#     'code': '',
#     'managerId': '0',
#     'userEmail': 'm5.az23ru@gmail.com',
#     'isDelete': '0',
#     'clientOrderNumber': None,
#     'positions': [
#     {
#         'id': '355560822',
#         'statusCode': '233596',
#         'comment': '',
#         'commentAnswer': '',
#         'routeId': '11323901',
#         'distributorId': '1599030',
#         'distributorName': 'ОСН',
#         'distributorType': '20',
#         'supplierCode': '',
#         'dsRouteId': '',
#         'itemKey': 'mIBB9ecFoJivVJpvLOg8J51S247TMBD9lcjPza6dtKXNW9nlEgFdYIW0K4oiJ3bKaJ048qVQrfbfGTttoK9I0cRzPPY5ZzzPREguFPSSFHQ2JVXHf18AZd9qUhASEAUHaY7VYHTNa1DgjrHU+mFQIE3VaCHPtbYxMDjQPQI7T+dsHmJOQ5xnMb6KyCpGnsRfHTfauG5iZDGeDqfxN56TMYpxGyn/IbeDgQaVk4JNWVwPJ2y4825c3HMlY5ItKVrxg+BOVg66cFdGszyl+C0SlhWMFQt66a0SsuVeubPH/5WfvH/8tr3dlMm9VtyA3V1/KDfJV9BJWZZIyQ8c1NRy1A2iEmCdgdo7bRBarNc0RwONN0b2zbEywQeMdi9BffK+NwMpeq/UjPySsP+JKL1i68WMHLTyoQH0aoVU9k3PayU/cfu09V0tka7lykqUJQSENnD1eWwxCnB2nJhngmMifONKgWyrLIh2sosZW67yZWDlJorBY7UvO76X9qwI7Gs/8Sjd8MBj3+LeDb4zlpEtSx9SlqfZ7pqlOXlBQ1oL+w6vHG6mWWj5k4zippsP0H/xOMalQOj7D6Q2vBd3bSvN7d+X3Sj1EVmVPBVpA3tAoxvjoFEygC9/AId5CL0=',
#         'quantity': '1',
#         'quantityFinal': '1',
#         'priceIn': 1,
#         'priceOut': 4200,
#         'oldPriceOut': 4200,
#         'priceRate': 1,
#         'priceInSiteCurrency': 4200,
#         'currencyInId': '1',
#         'currencyOutId': '1',
#         'deadline': '0',
#         'deadlineMax': '0',
#         'status': 'Есть в наличии',
#         'number': '392102B100',
#         'numberFix': '392102B100',
#         'brand': 'Hyundai-KIA',
#         'brandFix': 'HYUNDAI-KIA',
#         'description': 'Датчик лямбда-зонд',
#         'dateUpdated': '2023-03-05 12:49:01',
#         'isCanceled': '0',
#         'lineReference': 'a:6:{s:9:"usedGroup";N;s:4:"code";N;s:20:"dsItemAdditionalInfo";N;s:13:"parentOrderId";N;s:16:"parentPositionId";N;s:18:"isEnableMaskNumber";b:0;}',
#         'code': '',
#         'distributorOrderId': None,
#         'weight': '0.195',
#         'volume': '0.8',
#         'isDelete': '0',
#         'noReturn': '0',
#         'articleCode': None,
#         'garageCarId': None
#     }],
#     'positionsQuantity': 1,
#     'sum': 4200,
#     'notes': []}
# """
