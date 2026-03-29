from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import select

from app.database import Base, SessionLocal, engine
from app.models import Category, InvoiceRecord, Item


DEMO_CATEGORIES = [
    {"name": "开发板", "description": "单片机、控制板与评估板"},
    {"name": "传感器", "description": "用于检测温度、距离、电流等物理量"},
    {"name": "电源模块", "description": "稳压电源、电池管理与供电模块"},
    {"name": "连接器件", "description": "导线、端子、排针等连接类器件"},
]


DEMO_ITEMS = [
    {
        "name": "Arduino Uno R3",
        "model": "A000066",
        "category_name": "开发板",
        "quantity": 6,
        "key_specifications": "ATmega328P，5V 工作电压，14 路数字 IO，6 路模拟输入",
        "function_description": "用于快速原型搭建、基础控制实验与课程演示",
        "remarks": "2 块已焊接排针，可直接用于面包板实验",
        "location": "A柜-第1层-开发板盒",
    },
    {
        "name": "ESP32 开发板",
        "model": "ESP32-WROOM-32",
        "category_name": "开发板",
        "quantity": 8,
        "key_specifications": "双核 MCU，Wi-Fi + 蓝牙，3.3V 供电",
        "function_description": "适合物联网、无线数据采集和联网控制实验",
        "remarks": "烧录前请确认 USB 驱动已安装",
        "location": "A柜-第1层-无线模块盒",
    },
    {
        "name": "超声波测距模块",
        "model": "HC-SR04",
        "category_name": "传感器",
        "quantity": 12,
        "key_specifications": "测距范围 2cm-400cm，5V 供电",
        "function_description": "用于距离检测、避障实验和小车控制实验",
        "remarks": "建议与 5V 单片机直接配合使用",
        "location": "B柜-第2层-传感器抽屉",
    },
    {
        "name": "温湿度传感器",
        "model": "DHT22",
        "category_name": "传感器",
        "quantity": 10,
        "key_specifications": "温度范围 -40~80℃，湿度 0~100%RH",
        "function_description": "用于环境监测、温湿度采集与智能控制实验",
        "remarks": "采样频率不宜过高，建议 2 秒以上读取一次",
        "location": "B柜-第2层-传感器抽屉",
    },
    {
        "name": "可调降压模块",
        "model": "LM2596",
        "category_name": "电源模块",
        "quantity": 15,
        "key_specifications": "输入 4.5V-40V，输出 1.25V-35V，最大 3A",
        "function_description": "用于实验供电、电压转换和原型机快速调试",
        "remarks": "首次使用前请先调节输出电压，再连接负载",
        "location": "C柜-第1层-电源模块盒",
    },
    {
        "name": "杜邦线套装",
        "model": "公对公 / 公对母 / 母对母",
        "category_name": "连接器件",
        "quantity": 20,
        "key_specifications": "多规格长度，适合 2.54mm 排针连接",
        "function_description": "用于开发板、传感器、面包板之间的快速连线",
        "remarks": "请用后归回同一个收纳盒，避免混放",
        "location": "C柜-第2层-连接线盒",
    },
]


DEMO_INVOICES = [
    {
        "product_name": "Arduino Uno R3",
        "model": "A000066",
        "unit_price": Decimal("98.00"),
        "quantity": 4,
        "purchase_date": date(2026, 1, 18),
        "owner_name": "实验室公共采购",
        "invoice_status": "已开",
        "ownership_type": "公共",
        "remarks": "用于课程演示与基础控制实验",
    },
    {
        "product_name": "ESP32 开发板",
        "model": "ESP32-WROOM-32",
        "unit_price": Decimal("36.50"),
        "quantity": 6,
        "purchase_date": date(2026, 2, 6),
        "owner_name": "张同学",
        "invoice_status": "待开",
        "ownership_type": "私人",
        "remarks": "个人课题采购，后续可转为共享库存",
    },
    {
        "product_name": "超声波测距模块",
        "model": "HC-SR04",
        "unit_price": Decimal("8.80"),
        "quantity": 10,
        "purchase_date": date(2025, 12, 22),
        "owner_name": "实验室公共采购",
        "invoice_status": "已开",
        "ownership_type": "公共",
        "remarks": "机器人课程实验耗材",
    },
    {
        "product_name": "可调降压模块",
        "model": "LM2596",
        "unit_price": Decimal("12.60"),
        "quantity": 12,
        "purchase_date": date(2026, 3, 2),
        "owner_name": "李老师",
        "invoice_status": "待开",
        "ownership_type": "公共",
        "remarks": "统一采购，等待财务开票",
    },
    {
        "product_name": "数字示波器探头",
        "model": "P6100",
        "unit_price": Decimal("45.00"),
        "quantity": 2,
        "purchase_date": date(2025, 11, 30),
        "owner_name": "实验室公共采购",
        "invoice_status": "已开",
        "ownership_type": "公共",
        "remarks": "仪器配件补购",
    },
    {
        "product_name": "焊台替换烙铁头",
        "model": "900M-T-I",
        "unit_price": Decimal("6.50"),
        "quantity": 8,
        "purchase_date": date(2026, 1, 9),
        "owner_name": "王同学",
        "invoice_status": "待开",
        "ownership_type": "私人",
        "remarks": "个人毕设用，保留报销记录",
    },
]


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


def seed_demo_data() -> bool:
    with SessionLocal() as session:
        has_category = session.scalar(select(Category.id).limit(1)) is not None
        has_item = session.scalar(select(Item.id).limit(1)) is not None
        has_invoice = session.scalar(select(InvoiceRecord.id).limit(1)) is not None

        created_any = False

        if not has_category and not has_item:
            categories = [Category(**category_data) for category_data in DEMO_CATEGORIES]
            session.add_all(categories)
            session.flush()

            category_map = {category.name: category for category in categories}
            items = []
            for item_data in DEMO_ITEMS:
                category = category_map[item_data["category_name"]]
                items.append(
                    Item(
                        name=item_data["name"],
                        model=item_data["model"],
                        category_id=category.id,
                        quantity=item_data["quantity"],
                        key_specifications=item_data["key_specifications"],
                        function_description=item_data["function_description"],
                        remarks=item_data["remarks"],
                        location=item_data["location"],
                    )
                )

            session.add_all(items)
            created_any = True

        if not has_invoice:
            invoices = []
            for invoice_data in DEMO_INVOICES:
                invoices.append(
                    InvoiceRecord(
                        product_name=invoice_data["product_name"],
                        model=invoice_data["model"],
                        unit_price=invoice_data["unit_price"],
                        quantity=invoice_data["quantity"],
                        total_amount=invoice_data["unit_price"] * invoice_data["quantity"],
                        purchase_date=invoice_data["purchase_date"],
                        owner_name=invoice_data["owner_name"],
                        invoice_status=invoice_data["invoice_status"],
                        ownership_type=invoice_data["ownership_type"],
                        remarks=invoice_data["remarks"],
                    )
                )
            session.add_all(invoices)
            created_any = True

        if created_any:
            session.commit()
        return created_any


def initialize_database(with_demo_data: bool = True) -> None:
    create_tables()
    if with_demo_data:
        seed_demo_data()


if __name__ == "__main__":
    initialize_database(with_demo_data=True)
    print("数据库初始化完成。")
