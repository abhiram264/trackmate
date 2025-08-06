from enum import Enum


class ItemCategory(str, Enum):
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    ACCESSORIES = "accessories"
    BOOKS = "books"
    DOCUMENTS = "documents"
    SPORTS = "sports"
    BAGS = "bags"
    JEWELRY = "jewelry"
    KEYS = "keys"
    OTHERS = "others"


class ItemStatus(str, Enum):
    ACTIVE = "active"
    CLAIMED = "claimed"
    RESOLVED = "resolved"
    EXPIRED = "expired"
