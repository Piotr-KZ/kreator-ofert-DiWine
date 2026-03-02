"""
KSeF XML Builder — generowanie faktur XML zgodnych ze schematem FA(3).

Buduje XML lokalnie — nie wymaga sesji KSeF.
Uzywany zarowno przez Provider (AutoFlow) jak i billing hook (FastHub).

Schemat: FA(3) — http://crd.gov.pl/wzor/2023/06/29/12648/
"""

import base64
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class KSeFXMLBuilder:
    """
    Builder faktur XML FA(3) dla KSeF.

    Uzycie:
        builder = KSeFXMLBuilder()
        result = builder.build(
            seller_nip="1234567890",
            seller_name="Firma Sp. z o.o.",
            buyer_nip="9876543210",
            buyer_name="Klient S.A.",
            issue_date="2026-03-02",
            sale_date="2026-03-02",
            positions=[
                {"name": "Plan Pro", "quantity": 1, "unit": "szt",
                 "price_net": 199.00, "vat_rate": 23},
            ],
        )
        result["invoice_xml"]         # XML string
        result["invoice_xml_base64"]  # base64 do wysylki
        result["summary"]            # podsumowanie (netto, VAT, brutto)
    """

    def build(
        self,
        seller_nip: str,
        seller_name: str,
        buyer_nip: str,
        buyer_name: str,
        issue_date: str,
        sale_date: str,
        positions: List[Dict[str, Any]],
        currency: str = "PLN",
        payment_method: Optional[str] = None,
        payment_deadline: Optional[str] = None,
        bank_account: Optional[str] = None,
        notes: Optional[str] = None,
        system_info: str = "FastHub",
    ) -> Dict[str, Any]:
        """
        Generuj XML FA(3).

        Args:
            seller_nip: NIP sprzedawcy (10 cyfr)
            seller_name: nazwa sprzedawcy
            buyer_nip: NIP nabywcy
            buyer_name: nazwa nabywcy
            issue_date: data wystawienia (RRRR-MM-DD)
            sale_date: data sprzedazy (RRRR-MM-DD)
            positions: lista pozycji [{name, quantity, unit, price_net, vat_rate}]
            currency: waluta (PLN, EUR, USD)
            payment_method: metoda platnosci (przelew, gotowka, karta)
            payment_deadline: termin platnosci (RRRR-MM-DD)
            bank_account: nr konta bankowego
            notes: uwagi na fakturze
            system_info: nazwa systemu generujacego

        Returns:
            {"invoice_xml": str, "invoice_xml_base64": str, "summary": dict}
        """
        seller_nip = seller_nip.replace("-", "").replace(" ", "")
        buyer_nip = buyer_nip.replace("-", "").replace(" ", "")

        xml_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<Faktura xmlns="http://crd.gov.pl/wzor/2023/06/29/12648/">',
            '  <Naglowek>',
            '    <KodFormularza kodSystemowy="FA (3)" wersjaSchemy="1-0E">FA</KodFormularza>',
            '    <WariantFormularza>3</WariantFormularza>',
            f'    <DataWytworzeniaFa>{issue_date}T00:00:00</DataWytworzeniaFa>',
            f'    <SystemInfo>{system_info}</SystemInfo>',
            '  </Naglowek>',
            '  <Podmiot1>',
            f'    <DaneIdentyfikacyjne><NIP>{seller_nip}</NIP><Nazwa>{seller_name}</Nazwa></DaneIdentyfikacyjne>',
            '  </Podmiot1>',
            '  <Podmiot2>',
            f'    <DaneIdentyfikacyjne><NIP>{buyer_nip}</NIP><Nazwa>{buyer_name}</Nazwa></DaneIdentyfikacyjne>',
            '  </Podmiot2>',
            '  <Fa>',
            f'    <KodWaluty>{currency}</KodWaluty>',
            f'    <P_1>{issue_date}</P_1>',
            f'    <P_6>{sale_date}</P_6>',
            '    <FaWiersz>',
        ]

        total_net = 0.0
        total_vat = 0.0

        for i, pos in enumerate(positions, 1):
            qty = pos.get("quantity", 1)
            price_net = pos.get("price_net", 0)
            net = round(price_net * qty, 2)
            vat_rate = pos.get("vat_rate", 23)
            vat_amount = round(net * vat_rate / 100, 2) if vat_rate > 0 else 0
            total_net += net
            total_vat += vat_amount

            xml_lines.extend([
                f'      <NrWierszaFa>{i}</NrWierszaFa>',
                f'      <P_7>{pos.get("name", "")}</P_7>',
                f'      <P_8A>{pos.get("unit", "szt")}</P_8A>',
                f'      <P_8B>{qty}</P_8B>',
                f'      <P_9A>{price_net}</P_9A>',
                f'      <P_11>{net}</P_11>',
                f'      <P_12>{vat_rate}</P_12>',
            ])

        total_net = round(total_net, 2)
        total_vat = round(total_vat, 2)
        total_gross = round(total_net + total_vat, 2)

        xml_lines.extend([
            '    </FaWiersz>',
            f'    <P_13_1>{total_net}</P_13_1>',
            f'    <P_14_1>{total_vat}</P_14_1>',
            f'    <P_15>{total_gross}</P_15>',
        ])

        if payment_method:
            xml_lines.append(
                f'    <Platnosc><FormaPlatnosci>{payment_method}</FormaPlatnosci></Platnosc>'
            )
        if payment_deadline:
            xml_lines.append(f'    <TerminPlatnosci>{payment_deadline}</TerminPlatnosci>')
        if bank_account:
            xml_lines.append(f'    <NrRachunku>{bank_account}</NrRachunku>')
        if notes:
            xml_lines.append(
                f'    <DodatkowyOpis><Klucz>Uwagi</Klucz><Wartosc>{notes}</Wartosc></DodatkowyOpis>'
            )

        xml_lines.extend(['  </Fa>', '</Faktura>'])
        invoice_xml = '\n'.join(xml_lines)
        xml_b64 = base64.b64encode(invoice_xml.encode('utf-8')).decode('utf-8')

        return {
            "invoice_xml": invoice_xml,
            "invoice_xml_base64": xml_b64,
            "summary": {
                "seller_nip": seller_nip,
                "buyer_nip": buyer_nip,
                "total_net": total_net,
                "total_vat": total_vat,
                "total_gross": total_gross,
                "positions_count": len(positions),
                "currency": currency,
            },
        }

    @staticmethod
    def validate_nip(nip: str) -> bool:
        """Walidacja NIP (cyfra kontrolna)."""
        nip = nip.replace("-", "").replace(" ", "")
        if len(nip) != 10 or not nip.isdigit():
            return False
        weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
        checksum = sum(int(nip[i]) * weights[i] for i in range(9)) % 11
        return checksum == int(nip[9])

    @staticmethod
    def validate_positions(positions: List[Dict]) -> List[str]:
        """Walidacja pozycji faktury. Zwroc liste bledow (pusta = OK)."""
        errors = []
        valid_vat_rates = (0, 5, 8, 23, -1)  # -1 = zw (zwolniony)

        for i, pos in enumerate(positions):
            if not pos.get("name"):
                errors.append(f"Pozycja {i+1}: brak nazwy")
            if pos.get("price_net", 0) <= 0:
                errors.append(f"Pozycja {i+1}: cena netto <= 0")
            if pos.get("quantity", 0) <= 0:
                errors.append(f"Pozycja {i+1}: ilosc <= 0")
            if pos.get("vat_rate") not in valid_vat_rates:
                errors.append(f"Pozycja {i+1}: nieprawidlowa stawka VAT ({pos.get('vat_rate')})")

        return errors
