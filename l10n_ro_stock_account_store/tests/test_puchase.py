# Copyright (C) 2020 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import random

from odoo.tests import Form

from .common import TestStockCommon

# Generare note contabile la achizitie


class TestStockPurchaseStore(TestStockCommon):
    def test_nir_with_invoice_in_store(self):
        """
            Receptie produse in magazin in baza facturii
             - in stoc valoarea de achiztie
             - in contabilitate valoarea de vanzare
             - in diferente de pret difertnea dintre valoarea  de achiztie si valoarea de vanzare fara tva
             - in TVA neexigibilă valoarea de tva
        """
        po = self.create_po(picking_type_in=self.picking_type_in_store)

        # in stoc produsele sunt la valoarea de achizitie
        self.check_stock_valuation(self.val_p1_i, self.val_p2_i)

        # se inregistreaza in stoc diferente dintre pretul de vanzare si cel de achzitie
        self.check_account_valuation(self.adaos_p1, self.adaos_p2)

        self.create_invoice()

        # in stoc produsele sunt la valoarea de achizitie
        self.check_stock_valuation(self.val_p1_i, self.val_p2_i)

        # in contabilitate valoarea este la pret de vanzare
        self.check_account_valuation(self.val_p1_store, self.val_p2_store)

        # verificare inregistrare diferenta de pret
        diff1 = round(self.tva_p1 - self.adaos_p1, 2)
        diff2 = round(self.tva_p2 - self.adaos_p2, 2)
        self.check_account_diff(diff1, diff2)

    def test_nir_with_invoice_and_diff_in_store(self):
        """
         Receptie produse  in magazin in baza facturii cu inregistrare diferente dintre comanda de achizitie si factura
         Diferentele trebuie sa fie inregitrate in contul de  ....

             - in stoc valoarea de achiztie din factura
             - in contabilitate valoarea de vanzare
             - in diferente de pret difertnea dintre valoarea de achiztie finala si valoarea de vanzare fara tva
             - in TVA neexigibilă valoarea de tva avand ca baza valoarea de vanzare
        """
        po = self.create_po(picking_type_in=self.picking_type_in_store)

        # in stoc produsele sunt la valoarea din comanda de achizitie
        self.check_stock_valuation(self.val_p1_i, self.val_p2_i)

        # se inregistreaza in stoc diferente dintre pretul de vanzare si cel de din comanda achzitie
        self.check_account_valuation(self.adaos_p1, self.adaos_p2)

        self.create_invoice(self.diff_p1, self.diff_p2)

        # in stoc produsele sunt la valoarea de achizitie finala
        self.check_stock_valuation(self.val_p1_f, self.val_p2_f)

        # in contabilitate valoarea este la pret de vanzare

        self.check_account_valuation(self.val_p1_store, self.val_p2_store)

        # verificare inregistrare diferenta de pret
        diff1 = round(self.tva_p1 - self.adaos_p1, 2)
        diff2 = round(self.tva_p2 - self.adaos_p2, 2)
        self.check_account_diff(diff1, diff2)

    def test_nir_with_notice_and_invoice_in_store(self):
        """
            Receptie produse in magazin pe baza de aviz si inregistare ulterioara a facturii
        """
        po = self.create_po(notice=True, picking_type_in=self.picking_type_in_store)
        #  in stoc produsele sunt la valoarea de achizitie
        self.check_stock_valuation(self.val_p1_i, self.val_p2_i)

        # in contabilitate valoarea este la pret de vanzare
        self.check_account_valuation(self.val_p1_store, self.val_p2_store)

        self.create_invoice()

        # in stoc produsele sunt la valoarea de achizitie
        self.check_stock_valuation(self.val_p1_i, self.val_p2_i)
        # in contabilitate valoarea este la pret de vanzare
        self.check_account_valuation(self.val_p1_store, self.val_p2_store)

    def test_nir_with_notice_invoice_and_diff_in_store(self):
        """
         Receptie produse in magazin pe baza de aviz si inregistare ulterioara a facturii
         cu inregistrare diferente dintre comanda de achzitie si factura
         Diferentele trebuie sa fie inregitrate in contul de diferente de stoc
        """
        po = self.create_po(notice=True, picking_type_in=self.picking_type_in_store)

        # in stoc produsele sunt la valoarea de achizitie
        self.check_stock_valuation(self.val_p1_i, self.val_p2_i)

        # in contabilitate valoarea este la pret de vanzare
        self.check_account_valuation(self.val_p1_store, self.val_p2_store)

        self.create_invoice(self.diff_p1, self.diff_p2)

        # in stoc produsele sunt la valoarea de achizitie
        self.check_stock_valuation(self.val_p1_i, self.val_p2_i)

        # in contabilitate valoarea este la pret de vanzare
        self.check_account_valuation(self.val_p1_store, self.val_p2_store)

        # verificare  diferente de pret
