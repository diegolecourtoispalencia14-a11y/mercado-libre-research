from abc import ABC, abstractmethod


class BaseAdapter(ABC):
    @abstractmethod
    def search(self, keyword: str, limit: int = 50) -> list[dict]:
        ...

    @abstractmethod
    def get_product(self, ml_id: str) -> dict:
        ...
