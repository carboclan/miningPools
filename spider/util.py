from loguru import logger

logger.add(
    "spider.log",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} - {level} - {file} - {line} - {message}",
    rotation="10 MB",
)

power_detail = {
    "id": "191110791",
    "merchant": "bitdeer",
    "created_time": 1573407000,
    "updated_time": 1575082525,
    "delivery_time": 1575590400,
    "hash_rate_price": "",
    "hash_rate_price_discount": "1",
    "electric_price": "",
    "electric_price_discount": "1",
    "mainteance_price": "0.0000",
    "mainteance_price_discount": "0.00",
    "days": "90",
    "amount": "50",
    "hash_rate_final_price": "510.0000",
    "maintance_final_price": "292.50",
    "electric_final_price": 0,
    "price": "0",
    "hash_rate": "1",
    "hash_rate_unit": "TH/s",
    "coin": "BTC",
    "pool": "AntPool",
    "algorithm": "SHA256",
    "sold_percent": "100.00",
    "mining_machine": "S17",
}
