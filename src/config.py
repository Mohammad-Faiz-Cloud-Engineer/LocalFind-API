class Settings:
    app_name: str = "LocalFind API"
    app_version: str = "4.3.7"
    api_prefix: str = "/api/v1"
    contact_email: str = "hello@localfind.com"
    contact_phone: str = "+91 8004037031"
    contact_whatsapp: str = "+91 8004037031"
    contact_address: str = "Rasauli, Barabanki, Uttar Pradesh 225001"
    map_lat: float = 26.9135
    map_lng: float = 81.2328
    map_zoom: int = 14
    cors_origins: list[str] = ["*"]
    items_per_page: int = 6
    max_pages: int = 50
    founded_year: int = 2026
    site_name: str = "LocalFind"
    area_name: str = "Rasauli, Barabanki, Uttar Pradesh"
    tagline: str = "Discover Everything Around You"

    search_aliases: dict[str, list[str]] = {
        "csc": [
            "common service center", "common service centre",
            "csc center", "raheem csc", "golden csc", "vineet csc",
        ],
        "atm": ["automated teller machine", "cash machine"],
        "govt": ["government", "gov"],
        "govt services": ["government services", "government service"],
        "pan": ["permanent account number", "pan card"],
        "aadhaar": ["aadhar", "adhaar", "adhar", "uidai"],
        "pds": ["public distribution system", "ration shop", "ration card"],
        "hospital": [
            "clinic", "medical center", "health center", "dispensary",
            "abdul hospital", "janta clinic", "maxwell hospital",
            "rainbow hospital", "trauma centre", "trauma center",
        ],
        "pharmacy": [
            "medical store", "chemist", "drug store", "medicine shop",
            "hind pharmacy", "shri shyam medicals", "kartik medical store",
            "sanskar medical store",
        ],
        "restaurant": ["hotel", "dhaba", "eatery", "food"],
        "sweets": [
            "sweet shop", "mithai", "desserts", "pankaj sweets",
            "rajju sweets", "ice cream", "cake", "namkeen",
        ],
        "grocery": ["kirana", "general store", "supermarket", "provision store"],
        "bank": ["banking", "atm"],
        "school": [
            "education", "college", "institute", "academy",
            "chandra shekhar azad", "inter college", "up board",
            "jay hind", "sagar institute", "sitm", "technology", "management",
        ],
        "salon": ["parlour", "parlor", "beauty salon", "barber"],
        "repair": [
            "service center", "workshop", "mechanic", "mobile-repair",
            "phone-repair", "screen-replacement", "battery-replacement",
            "fix", "service",
        ],
        "electrician": ["electric", "electrical", "wiring", "shariq hashmi"],
        "garments": [
            "clothes", "clothing", "fashion", "apparel",
            "aman garments", "affan garments", "suraj kumar clothing",
        ],
        "footwear": ["shoes", "sandals", "slippers", "chappals", "satyam footwear"],
        "furniture": [
            "sofa", "bed", "table", "chair", "wardrobe", "dressing-table",
            "khidmat enterprises", "custom-furniture", "woodwork", "carpentry",
        ],
        "hardware": [
            "building-materials", "construction", "tools", "plywood",
            "wooden-doors", "paints", "cement", "rasauli hardware",
        ],
        "event-services": [
            "tent-house", "wedding-decoration", "party-rentals",
            "lighting", "catering-equipment", "sk tent", "event-planning",
        ],
        "gym": ["fitness", "workout", "exercise", "friends fitness", "bodybuilding"],
        "wellness": [
            "ayurveda", "spa", "resort", "retreat", "yoga", "meditation",
            "detox", "healing", "health-resort", "heritage",
            "panchakarma", "therapy",
        ],
        "photography": [
            "photo", "photographer", "videography", "video", "studio",
            "photo-shoot", "photoshoot", "wedding-photography",
            "event-photography", "saraswati-studio", "camera", "video-production",
        ],
        "studio": [
            "photography", "photo-studio", "video-studio", "saraswati-studio",
            "photo-shoot", "wedding-video", "event-video",
        ],
        "printing": ["cup-printing", "photo-printing", "mug-printing", "custom-printing", "print-shop"],
        "mobile": [
            "mobile-shop", "phone", "smartphone", "mobile-repair",
            "phone-repair", "mobile-accessories", "jamwant-mobile", "cell-phone",
        ],
        "electronics": [
            "mobile", "phone", "smartphone", "earphones", "headphones",
            "tws", "neckband", "accessories", "charger", "power-bank",
        ],
        "fast-food": [
            "momos", "spring-roll", "fried-rice", "burger", "chowmein",
            "finger-chips", "aloo-patty", "macaroni", "shri-shyam-fast-foods",
            "quick-bites", "snacks", "street-food",
        ],
        "momos": ["momo", "dumpling", "steamed-momos", "fried-momos", "veg-momos", "chicken-momos"],
        "bakery": [
            "hazelnut-factory", "the-hazelnut-factory", "thf",
            "bakery-shop", "baked-goods", "pastries", "croissants", "bread", "baking",
        ],
        "desserts": [
            "hazelnut-factory", "sweets", "cakes", "pastries",
            "dessert-shop", "sweet-shop", "mithai", "treats",
        ],
        "cafe": [
            "coffee-shop", "hazelnut-factory", "specialty-coffee",
            "coffee", "tea", "beverages", "european-cafe",
        ],
        "laundry": ["dry clean", "washing", "ironing"],
        "petrol": ["fuel", "gas station", "pump"],
        "delivery": ["courier", "logistics", "transport"],
        "jiffy": [
            "jiffy-by-spencers", "spencers", "grocery", "supermarket",
            "retail", "shopping", "mall",
        ],
        "spencers": [
            "jiffy-by-spencers", "jiffy", "grocery-store", "supermarket",
            "retail-chain", "shopping", "mall",
        ],
        "seven-eleven": [
            "7-eleven", "seven-eleven-mart", "convenience-store", "grocery",
            "general-store", "kirana", "daily-essentials", "snacks", "beverages",
        ],
        "vineet-jan-seva-kendra": [
            "vineet", "jan seva kendra", "csc",
            "common service center", "vineet csc",
        ],
    }

    @property
    def search_alias_map(self) -> dict[str, list[str]]:
        return self.search_aliases

    @property
    def alias_to_terms(self) -> dict[str, str]:
        result: dict[str, str] = {}
        for alias, terms in self.search_aliases.items():
            for term in terms:
                result[term.lower()] = alias
        return result


settings = Settings()
