from pathlib import Path
import json
import requests
data_dir = Path(__file__).parent / "data"
#print(data_dir, data_dir.exists())
#print(Path(".").absolute())
#print(Path("./data/set1-en_us.json").exists())

def read_json_file(json_file):
    with open(json_file,encoding='utf8') as f:
        return json.load(f)

try:
    cards_files = data_dir.glob("set*.json")
    cards = []
    for f in cards_files:
        f_json = read_json_file(f)
        cards += f_json
except Exception as e:
    print("Could not load card data")

class Card:
    def __init__(self, card=None, **kwargs):
        self.id = kwargs.get("CardID", None)
        self.cardCode = kwargs.get("CardCode", card)
        self.card_set = int(self.cardCode[:2])
        self.count = int(kwargs.get("count", 1))
        self._card_data = self.card_info()

        self.preview_image_online = f"https://cdn-lor.mobalytics.gg/production/images/cards-preview/{self.cardCode}.png"

    def card_info(self):
        return [card for card in cards if card["cardCode"] == self.cardCode][0]

    def add_copy(self):
        self.count += 1

    def remove_copy(self):
        self.count -= 1

    @property
    def name(self):
        return self._card_data["name"]

    @property
    def isChampion(self):
        return self.superType == "Champion"

    @property
    def description(self):
        return self._card_data["descriptionRaw"]

    @property
    def descriptionFancy(self):
        return self._card_data["description"]

    @property
    def keywords(self):
        return self._card_data["keywords"]

    @property
    def keywordRefs(self):
        return self._card_data["keywordRefs"]

    @property
    def cost(self):
        return self._card_data["cost"]

    @property
    def health(self):
        return self._card_data["health"]

    @property
    def attack(self):
        return self._card_data["attack"]

    @property
    def associatedCardRefs(self):
        return self._card_data["associatedCardRefs"]

    @property
    def associatedCards(self):
        return self._card_data["associatedCards"]

    @property
    def collectible(self):
        return self._card_data["collectible"]

    @property
    def flavorText(self):
        return self._card_data["flavorText"]

    @property
    def rarity(self):
        return self._card_data["rarity"]

    @property
    def rarityRef(self):
        return self._card_data["rarityRef"]

    @property
    def region(self):
        return self._card_data["region"]

    @property
    def regionRef(self):
        return self._card_data["regionRef"]

    @property
    def spellSpeed(self):
        return self._card_data["spellSpeed"]

    @property
    def spellSpeedRef(self):
        return self._card_data["spellSpeedRef"]

    @property
    def subType(self):
        return self._card_data["subtype"]

    @property
    def superType(self):
        return self._card_data["supertype"]

    @property
    def cardType(self):
        return self._card_data["type"]

    def serialize(self, props=None, as_dict=False):
        if not props:
            props = [
                "name",
                "description",
                "cardCode",
                "keywords",
                "cost",
                "health",
                "attack",
                "flavorText",
                "rarity",
                "rarityRef",
                "spellSpeed",
                "spellSpeedRef",
                "subtype",
                "supertype",
                "type",
            ]

        #s = {k: v for (k, v) in self.__dict__.items() if k in props}
        s = {k: v for (k, v) in self._card_data.items() if k in props}
        s["count"] = self.count
        return s if as_dict else json.dumps(s)

    def __str__(self):
        return f"({self.cost}) {self.name}: {self.description}"

    def __repr__(self):
        return f"Card({self.cardCode}, Name: {self.name}, Cost: {self.cost})"

    def __hash__(self):  # allow using cards as dict keys
        return hash(self.cardCode)
