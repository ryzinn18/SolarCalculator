from src.utils.utils import post_item_to_dynamodb, DDB_RESOURCE, check_http_response


def store_inputs(table_name: str, table_item: dict) -> dict:
    """Store input data to solarCalculatorTable-Inputs."""

    """UPDATE WITH TRY EXCEPT SEEN HERE: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GettingStarted.ReadItem.html"""

    ddb_table = DDB_RESOURCE.Table(table_name)

    ddb_response = post_item_to_dynamodb(ddb_table, item=table_item)

    if not check_http_response(response_code=ddb_response):
        # Log warning
        print(f'\t{table_item["username"]}: Log warning')
        return {
            "status": {
                "status_code": 442,
                "message": "Could not write info to database."
            }
        }
    else:
        # Log info - success
        print(f'\t{table_item["username"]}: Log info - success')
        return {
            "status": {
                "status_code": 200,
                "message": "Data successfully written to database."
            }
        }

if __name__ == '__main__':
    # TEST STORE INPUTS
    # import threading
    # item2 = {
    #     "name": "TEST",
    #     "time_stamp": "123"
    #     "stage": "init",
    #     "address": "My Street 123",
    #     "state": "Ohio",
    #     "monthly_data": [1, 2, 1],
    #     "mod_data": {
    #         'mod_kwh': "0.4",
    #         "mod_price": "200"
    #     },
    #     "capacity": "14",
    # }
    # item1 = {
    #     "name": "TEST",
    #     "time_stamp": "123"
    #     "stage": "init",
    #     "address": "My Street 123",
    #     "state": "Ohio",
    #     "monthly_data": [1] * 1000,
    #     "mod_data": {
    #         'mod_kwh': "0.4",
    #         "mod_price": "200"
    #     },
    #     "capacity": "14",
    # }
    # print("creating threads")
    # t1 = threading.Thread(target=store_inputs, args=[item1])
    # t2 = threading.Thread(target=store_inputs, args=[item2])
    #
    # print("starting threads")
    # t1.start()
    # t2.start()
    pass