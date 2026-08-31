import random
import re
import zlib

from django.core.management.base import BaseCommand

from accounts.models import User
from products.models import Category, Product, ProductImage, ProductVariant
from vendors.models import VendorProfile

CATALOG = {
    "Electronics": [
        ("Wireless Headphones", 49.99),
        ("Bluetooth Speaker", 39.99),
        ("Smartwatch Pro", 129.99),
        ("Noise Cancelling Earbuds", 89.99),
        ("4K Action Camera", 159.99),
        ("Portable Power Bank", 24.99),
        ("Mechanical Keyboard", 74.99),
        ("Wireless Mouse", 19.99),
        ("USB-C Hub", 34.99),
        ("Smart LED Desk Lamp", 29.99),
    ],
    "Apparel": [
        ("Insulated Winter Parka", 129.99),
        ("Lightweight Rain Jacket", 59.99),
        ("Classic Denim Jacket", 69.99),
        ("Merino Wool Sweater", 79.99),
        ("Running Shorts", 24.99),
        ("Graphic Cotton T-Shirt", 19.99),
        ("Slim Fit Chinos", 44.99),
        ("Wool Blend Overcoat", 149.99),
        ("Athletic Joggers", 34.99),
        ("Flannel Shirt", 39.99),
    ],
    "Home & Kitchen": [
        ("Stainless Steel Cookware Set", 119.99),
        ("Ceramic Non-Stick Pan", 29.99),
        ("Electric Kettle", 27.99),
        ("French Press Coffee Maker", 22.99),
        ("Bamboo Cutting Board", 18.99),
        ("Air Fryer", 84.99),
        ("Knife Block Set", 64.99),
        ("Glass Food Storage Set", 32.99),
        ("Stand Mixer", 199.99),
        ("Cast Iron Skillet", 34.99),
    ],
    "Sports & Outdoors": [
        ("Yoga Mat", 29.99),
        ("Adjustable Dumbbell Set", 149.99),
        ("Camping Tent", 119.99),
        ("Insulated Water Bottle", 19.99),
        ("Trail Running Shoes", 89.99),
        ("Resistance Bands Set", 17.99),
        ("Hiking Backpack", 74.99),
        ("Foam Roller", 21.99),
        ("Folding Camping Chair", 39.99),
        ("Cycling Helmet", 54.99),
    ],
    "Books & Stationery": [
        ("Leather Bound Notebook", 14.99),
        ("Fountain Pen Set", 24.99),
        ("Desk Organizer", 19.99),
        ("Sticky Notes Bundle", 6.99),
        ("Hardcover Planner", 21.99),
        ("Watercolor Paint Set", 27.99),
        ("Bookend Set", 16.99),
        ("Calligraphy Kit", 22.99),
        ("Highlighter Set", 8.99),
        ("Leather Portfolio Folder", 34.99),
    ],
    "Beauty & Personal Care": [
        ("Electric Toothbrush", 44.99),
        ("Facial Cleansing Brush", 32.99),
        ("Hair Dryer", 49.99),
        ("Beard Trimmer Kit", 29.99),
        ("Skincare Gift Set", 39.99),
        ("Aromatherapy Diffuser", 24.99),
        ("Makeup Brush Set", 18.99),
        ("Manicure Kit", 14.99),
        ("Bath Bomb Gift Set", 19.99),
        ("Electric Shaver", 54.99),
    ],
    "Toys & Games": [
        ("Wooden Building Blocks", 24.99),
        ("Board Game Collection", 34.99),
        ("Remote Control Car", 44.99),
        ("Jigsaw Puzzle", 16.99),
        ("Camera Drone", 79.99),
        ("Card Game Party Pack", 12.99),
        ("Plush Teddy Bear", 19.99),
        ("STEM Robotics Kit", 59.99),
        ("Wooden Chess Set", 29.99),
        ("Action Figure", 22.99),
    ],
    "Pet Supplies": [
        ("Reflective Dog Leash", 14.99),
        ("Cat Scratching Post", 34.99),
        ("Orthopedic Pet Bed", 44.99),
        ("Automatic Pet Feeder", 54.99),
        ("Dog Chew Toy Set", 17.99),
        ("Enclosed Cat Litter Box", 39.99),
        ("Pet Carrier Backpack", 49.99),
        ("Pet Grooming Brush Set", 16.99),
        ("Aquarium Starter Kit", 64.99),
        ("Deluxe Bird Cage", 74.99),
    ],
}

STOP_WORDS = {"set", "kit", "pro", "the", "for", "a", "an", "of", "with", "and"}


def keywords_for(title):
    words = re.sub(r"[^a-zA-Z ]", "", title).lower().split()
    words = [w for w in words if w not in STOP_WORDS]
    return ",".join(words[:3]) or "product"


def lock_for(title):
    return zlib.crc32(title.encode()) % 100000


class Command(BaseCommand):
    help = "Seeds/updates ~80 demo products with real keyword-matched photos (via LoremFlickr, no API key needed)."

    def handle(self, *args, **options):
        vendor_user, created = User.objects.get_or_create(
            username="demo_vendor",
            defaults={"role": "vendor", "email": "vendor@producthub.demo"},
        )
        if created:
            vendor_user.set_password("DemoVendor123!")
            vendor_user.save()

        vendor, _ = VendorProfile.objects.get_or_create(
            user=vendor_user,
            defaults={"store_name": "ProductHub Demo Store", "status": "approved"},
        )

        total = 0
        for category_name, items in CATALOG.items():
            category, _ = Category.objects.get_or_create(name=category_name)

            for title, price in items:
                product, _ = Product.objects.update_or_create(
                    title=title,
                    defaults={
                        "vendor": vendor,
                        "category": category,
                        "description": f"A high-quality {title.lower()} from {vendor.store_name}.",
                        "base_price": price,
                        "is_active": True,
                    },
                )

                image_url = f"https://loremflickr.com/500/500/{keywords_for(title)}?lock={lock_for(title)}"
                ProductImage.objects.update_or_create(
                    product=product, is_primary=True,
                    defaults={"image_url": image_url, "alt_text": title},
                )

                if not product.variants.exists():
                    sku = f"SKU-{product.id:05d}"
                    ProductVariant.objects.create(
                        product=product, sku=sku, stock_quantity=random.randint(15, 200)
                    )

                total += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seeded/updated {total} products across {len(CATALOG)} categories."
        ))