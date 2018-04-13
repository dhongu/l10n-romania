# coding=utf-8

import werkzeug

from odoo import exceptions, fields, http, _
from odoo.http import request
from lxml import etree
import os
import base64


class Declarations(http.Controller):

    @http.route(['/declarations/<int:run_id>/<int:report_id>/<string:filename>' ], type='http', auth="user")
    def get_declarations(self, filename, run_id=None, report_id=None, **kwargs):

        if run_id:
            run_declaration = request.env['l10n_ro.run.declaration'].browse(run_id)

        else:
            if '_' in filename:
                code = filename.split('_')[0]
            else:
                code = filename.split('.')[0]
            run_declaration = request.env['l10n_ro.run.declaration'].with_context(declaration_code=code).create({})

        model = request.env['l10n_ro.%s_report' % run_declaration.declaration_id.code.lower()]
        report = model.browse(report_id)

        if run_declaration and  run_declaration.declaration_id.data_xdp:
            xml_file = base64.b64decode(run_declaration.declaration_id.data_xdp)
            xml_doc = etree.fromstring(xml_file)
        else:
            data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'file')
            xml_file = os.path.join(data_dir, filename)
            xml_doc = etree.parse(xml_file)




        tag_an = xml_doc.xpath('//an_r')
        if tag_an:
            tag_an[0].text = run_declaration.date_to[:4]

        tag_luna_r = xml_doc.xpath('//luna_r')
        if tag_luna_r:
            tag_luna_r[0].text = run_declaration.date_to[5:7]

        tag_cif = xml_doc.xpath('//cif')
        if tag_cif:
            cif = run_declaration.company_id.partner_id.vat
            if cif:
                cif = cif.replace('RO', '')
                tag_cif[0].text = cif

        tag_den = xml_doc.xpath('//den | //DENUMIRE')
        if tag_den:
            tag_den[0].text = run_declaration.company_id.partner_id.name

        tag_adresa = xml_doc.xpath('//adresa | //ADRESA')
        if tag_adresa and not tag_adresa[0].text:
            tag_adresa[0].text = run_declaration.company_id.partner_id._display_address(without_company=True)

        tag_telefon = xml_doc.xpath('//telefon | //text_telefon')
        if tag_telefon and not tag_telefon[0].text:
            tag_telefon[0].text = run_declaration.company_id.partner_id.phone or ''

        tag_mail = xml_doc.xpath('//mail | //text_email')
        if tag_mail and not tag_mail[0].text :
            tag_mail[0].text = run_declaration.company_id.partner_id.email or ''



        if ' ' in request.env.user.partner_id.name:
            name = request.env.user.partner_id.name.split(' ')
            nume = name[-1]
            prenume = ' '.join(name[:-1])

            tag_nume_declar = xml_doc.xpath('//nume_declar | //Nume')
            if tag_nume_declar and not tag_nume_declar[0].text:
                tag_nume_declar[0].text = nume

            tag_prenume_declar = xml_doc.xpath('//prenume_declar | //Prenume')
            if tag_prenume_declar and not tag_prenume_declar[0].text:
                tag_prenume_declar[0].text = prenume

            tag_functie_declar = xml_doc.xpath('//functie_declar | //Functia')
            if tag_functie_declar and not tag_functie_declar[0].text:
                tag_functie_declar[0].text = request.env.user.partner_id.function or ''

        xml_doc = report.xml_processing(xml_doc)

        declaration = '<?xml version="1.0" encoding="UTF-8"?><?xfa generator="XFA2_4" APIVersion="3.6.14289.0"?>'
        content = etree.tostring(xml_doc, encoding='utf8', xml_declaration=False)

        content = declaration + content.decode()

        headers = [('Content-Type', 'application/vnd.adobe.xdp+xml')]

        response = request.make_response(content, headers)

        return response
