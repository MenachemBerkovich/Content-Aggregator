from config import USERS_DATA_COLUMNS


class Address:
    def __init__(self, address: str):
        self.address = address

class WhatsAppAddress(Address):
    def __init__(self, phone_number: str):
        super().__init__(phone_number)

class EmailAddress(Address):
    def __init__(self, email: str):
        super().__init__(email)

class AddressFactory:
    @staticmethod
    def create(address: str) -> Address:
        pass
    @staticmethod
    def match_db_index(address: str) -> str:
        # to return the correnspond USER_DATA_COLUMN string
        pass