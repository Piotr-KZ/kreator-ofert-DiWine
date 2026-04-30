"""
Seed — pre-written text templates for offers. 20 variants.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.offer_text import OfferTextTemplate

TEMPLATES = [
    # GREETING — Boże Narodzenie
    {"block_type":"greeting","occasion_code":"christmas","variant":"A","name":"Powitanie BN — ciepłe","tone":"ciepły",
     "template_text":"Szanowna Pani {contact_person},\n\nz okazji zbliżających się Świąt Bożego Narodzenia pragniemy przedstawić ofertę prezentów firmowych dla {company_name}. Wierzymy, że starannie dobrane upominki to piękny sposób na wyrażenie wdzięczności wobec Państwa współpracowników i partnerów biznesowych."},
    {"block_type":"greeting","occasion_code":"christmas","variant":"B","name":"Powitanie BN — profesjonalne","tone":"profesjonalny",
     "template_text":"Szanowni Państwo,\n\nw nawiązaniu do zapytania dotyczącego prezentów świątecznych przygotowaliśmy ofertę {quantity} zestawów prezentowych dla {company_name}. Każdy zestaw został skomponowany z myślą o najwyższej jakości i elegancji odpowiedniej do tej wyjątkowej okazji."},
    {"block_type":"greeting","occasion_code":"christmas","variant":"C","name":"Powitanie BN — krótkie","tone":"profesjonalny",
     "template_text":"Dzień dobry,\n\ndziękujemy za zainteresowanie naszą ofertą prezentów świątecznych. Poniżej przedstawiamy propozycję {quantity} zestawów upominkowych przygotowaną specjalnie dla {company_name}."},

    # GREETING — Wielkanoc
    {"block_type":"greeting","occasion_code":"easter","variant":"A","name":"Powitanie Wielkanoc — ciepłe","tone":"ciepły",
     "template_text":"Szanowna Pani {contact_person},\n\nz okazji zbliżających się Świąt Wielkanocnych mamy przyjemność przedstawić ofertę wiosennych zestawów prezentowych dla {company_name}. Każdy zestaw został przygotowany z dbałością o sezonowe smaki i radosny charakter tych wyjątkowych dni."},
    {"block_type":"greeting","occasion_code":"easter","variant":"B","name":"Powitanie Wielkanoc — profesjonalne","tone":"profesjonalny",
     "template_text":"Szanowni Państwo,\n\nprzedstawiamy ofertę wielkanocnych zestawów prezentowych dla {company_name}. Przygotowaliśmy {quantity} propozycji upominków, które podkreślą wiosenny charakter Świąt."},

    # GREETING — Uniwersalny
    {"block_type":"greeting","occasion_code":"universal","variant":"A","name":"Powitanie uniwersalne","tone":"profesjonalny",
     "template_text":"Szanowni Państwo,\n\ndziękujemy za zapytanie ofertowe. Mamy przyjemność przedstawić propozycję {quantity} zestawów prezentowych przygotowanych specjalnie dla {company_name}."},
    {"block_type":"greeting","occasion_code":"universal","variant":"B","name":"Powitanie uniwersalne — osobiste","tone":"ciepły",
     "template_text":"Szanowna Pani {contact_person},\n\nw nawiązaniu do rozmowy, z przyjemnością przesyłam ofertę zestawów upominkowych dla {company_name}. Każdy zestaw skomponowaliśmy indywidualnie, aby jak najlepiej odpowiadał Państwa oczekiwaniom."},

    # WHY US
    {"block_type":"why_us","occasion_code":None,"variant":"A","name":"Dlaczego my — pełna","tone":"profesjonalny",
     "template_text":"Od lat specjalizujemy się w tworzeniu wyjątkowych zestawów prezentowych dla firm. Każdy prezent komponujemy indywidualnie — dobieramy wina od sprawdzonych polskich producentów, słodycze od rzemieślniczych manufaktur i opakowania, które robią wrażenie od pierwszego spojrzenia.\n\nZapewniamy pełną personalizację — od nadruku logo na opakowaniu po grawerunek na ekokorku. Realizujemy zamówienia od 50 do 1000+ sztuk z zachowaniem najwyższej jakości każdego egzemplarza."},
    {"block_type":"why_us","occasion_code":None,"variant":"B","name":"Dlaczego my — krótka","tone":"profesjonalny",
     "template_text":"Specjalizujemy się w prezentach firmowych — wina od polskich producentów, słodycze od rzemieślniczych manufaktur, pełna personalizacja. Indywidualne podejście do każdego zamówienia."},
    {"block_type":"why_us","occasion_code":None,"variant":"C","name":"Dlaczego my — z liczbami","tone":"profesjonalny",
     "template_text":"Ponad 500 zrealizowanych zamówień firmowych. 98% klientów wraca do nas w kolejnym sezonie. Współpracujemy z najlepszymi polskimi producentami win i rzemieślniczych słodyczy.\n\nGwarantujemy terminową realizację i pełną personalizację — od projektu opakowania po indywidualny dobór zawartości."},

    # FUN FACTS
    {"block_type":"fun_fact","occasion_code":None,"variant":"A","name":"Ciekawostka — wina owocowe","tone":"ciepły",
     "template_text":"Polskie wina owocowe przeżywają renesans — coraz więcej koneserów docenia ich unikalny charakter i rzemieślniczą produkcję. Nasze wina pochodzą od lokalnych producentów, którzy łączą tradycyjne receptury z nowoczesnym podejściem do winifikacji."},
    {"block_type":"fun_fact","occasion_code":None,"variant":"B","name":"Ciekawostka — jagoda kamczacka","tone":"ciepły",
     "template_text":"Jagoda kamczacka to superfruit o niezwykłych właściwościach — zawiera więcej witaminy C niż cytryna i więcej antyoksydantów niż jagody goji. Wino z jagody kamczackiej to prezent, który łączy wyjątkowy smak z dbałością o zdrowie."},
    {"block_type":"fun_fact","occasion_code":None,"variant":"C","name":"Ciekawostka — personalizacja","tone":"profesjonalny",
     "template_text":"Każde opakowanie personalizujemy indywidualnie — nadruk logo wykonujemy metodą sitodruku na papierze ekologicznym, a grawerunek na ekokorku to trwała pamiątka, która zostaje z obdarowanym na długo po wypiciu wina."},
    {"block_type":"fun_fact","occasion_code":None,"variant":"D","name":"Ciekawostka — słodycze rzemieślnicze","tone":"ciepły",
     "template_text":"Słodycze w naszych zestawach pochodzą z polskich manufaktur — czekolady ręcznie temperowane, pierniczki pieczone według stuletniej receptury, migdały prażone w małych partiach. Każdy kęs to rzemiosło, nie masowa produkcja."},

    # CLOSING
    {"block_type":"closing","occasion_code":None,"variant":"A","name":"Zakończenie — zaproszenie","tone":"profesjonalny",
     "template_text":"Zapraszamy do kontaktu w razie pytań lub chęci modyfikacji zestawów. Chętnie dopasujemy ofertę do Państwa indywidualnych potrzeb."},
    {"block_type":"closing","occasion_code":None,"variant":"B","name":"Zakończenie — z terminem","tone":"profesjonalny",
     "template_text":"Oferta jest ważna 14 dni. Przy potwierdzeniu zamówienia gwarantujemy realizację w ustalonym terminie. Zapraszamy do kontaktu — z przyjemnością odpowiemy na wszelkie pytania."},
    {"block_type":"closing","occasion_code":None,"variant":"C","name":"Zakończenie — osobiste","tone":"ciepły",
     "template_text":"Będzie mi miło, jeśli nasza propozycja przypadnie Państwu do gustu. Jestem do dyspozycji pod telefonem i mailem — chętnie omówię szczegóły lub przygotuję alternatywne warianty."},
]


async def seed_offer_texts(db: AsyncSession) -> int:
    count = 0
    for t in TEMPLATES:
        existing = (await db.execute(
            select(OfferTextTemplate).where(
                OfferTextTemplate.block_type == t["block_type"],
                OfferTextTemplate.occasion_code == t.get("occasion_code"),
                OfferTextTemplate.variant == t["variant"],
            )
        )).scalar_one_or_none()
        if not existing:
            db.add(OfferTextTemplate(**t))
            count += 1
    await db.commit()
    return count
