from odoo import api, fields, models
from datetime import datetime

to_19_ar = (u'صفر', u'واحد', u'اثنان', u'ثلاثة', u'أربعة', u'خمسة', u'ستة',
            u'سبعة', u'ثمانية', u'تسعة', u'عشرة', u'أحد عشر', u'اثنا عشر', u'ثلاثة عشر',
            u'أربعة عشرة', u'خمسة عشر', u'ست عشرة', u'سبعة عشر', u'ثمانية عشر', u'تسعة عشر')

tens_ar = (u'', u'', u'عشرون', u'ثلاثون', u'أربعون', u'خمسون', u'ستون', u'سبعون', u'ثمانون', u'تسعون')

hund_ar = (u'', u'', u'مئتان', u'ثلاثمائة', u'أربعمائة', u'خمسمائة', u'ستمائة', u'سبعمائة',
           u'ثمانمائة', u'تسعمائة')


def convert_less_100(number):
    if number <= 19:
        number = int(number)
        return to_19_ar[number]
    elif number < 100:
        ten = number / 10
        rest = number % 10
        if rest != 0:
            rest = int(rest)
            ten = int(ten)
            return to_19_ar[rest] + u' و ' + tens_ar[ten]
        else:
            rest = int(rest)
            ten = int(ten)
            return tens_ar[ten]


def convert_less_1000(number):
    hund = number / 100
    rest = number % 100
    rest = int(rest)
    hund = int(hund)

    if hund == 0:
        hund_text = u''
    elif hund == 1:
        hund_text = u'مئة'
    elif hund < 10:
        hund_text = hund_ar[hund]
    else:
        hund_text = convert_less_1000(hund) + u'مئة'
    if rest != 0:
        if hund_text != u'':
            hund_text = hund_text + u' و ' + convert_to_ar(rest)
        else:
            hund_text = convert_to_ar(rest)
    return hund_text


def convert_less_10000(number):
    thous = int(number / 1000)
    rest = int(number % 1000)
    if thous == 0:
        thous_text = u''
    elif thous == 1:
        thous_text = u'ألف'
    elif thous == 2:
        thous_text = u'ألفان'
    elif thous <= 10:
        thous_text = convert_less_100(thous) + u' آلاف '
    else:
        thous_text = convert_less_1000(thous) + u' الف '
    if rest != 0:
        if thous_text != u'':
            thous_text = thous_text + u' و ' + convert_to_ar(rest)
        else:
            thous_text = convert_to_ar(rest)
    return thous_text


def convert_less_billion(number):
    million = int(number / 1000000)
    rest = int(number % 1000000)
    if million == 1:
        million_text = u'مليون'
    elif million == 2:
        million_text = u'مليونان'
    elif million <= 10:
        million_text = convert_less_100(million) + u' ' + u'ملايين'
    elif million > 10:
        million_text = convert_less_1000(million) + u' ' + u'مليونا'
    if rest != 0:
        million_text = million_text + u' و ' + convert_to_ar(rest)
    return million_text


def convert_over_billion(number):
    million = int(number / 1000000000)
    rest = int(number % 1000000000)
    if million == 1:
        million_text = u'مليار'
    elif million == 2:
        million_text = u'مليارين'
    elif million <= 10 and million != 1 and million != 2:
        million_text = convert_less_100(million) + u' ' + u'مليارات'
    else:
        million_text = convert_less_1000(million) + u' ' + u'مليار'
    if rest != 0:
        million_text = million_text + u' و ' + convert_to_ar(rest)
    return million_text


def convert_to_ar(number):
    if number < 100:
        return convert_less_100(number)
    elif number < 1000 and number >= 100:
        return convert_less_1000(number)
    elif number < 1000000 and number >= 1000:
        return convert_less_10000(number)
    elif number < 1000000000 and number >= 1000000:
        return convert_less_billion(number)
    else:
        return convert_over_billion(number)


def amount_to_text_ar(numbers,u,us,su,sus):
    number = '%.2f' % numbers
    list = str(number).split('.')

    start_word = convert_to_ar(abs(int(list[0])))
    end_word = convert_to_ar(int(list[1]))
    currenc = ""

    if us and u and su and sus:
        if start_word == u'واحد':
            currenc = u'' + str(u)
        elif start_word in [u'ثلاثة', u'أربعة', u'خمسة', u'ستة',
                            u'سبعة', u'ثمانية', u'تسعة', u'عشرة']:
            currenc = u'' + str(us)
        else:
            currenc = u'' + str(u)


    final_result = ""
    if int(list[0]) != 0 and int(list[1]) != 0:
        if end_word == u'واحد':
            final_result = start_word + u' ' + currenc + u' و ' + u' ' + str(su)
        elif end_word in [u'ثلاثة', u'أربعة', u'خمسة', u'ستة',
                            u'سبعة', u'ثمانية', u'تسعة', u'عشرة']:
            final_result = start_word + u' ' + currenc + u' و ' + end_word+ u' ' + str(sus)
        else:
            final_result = start_word + u' ' + currenc + u' و ' + end_word + u' ' + str(su)
    elif int(list[0]) == 0 and int(list[1]) != 0:
        if end_word == u'واحد':
            final_result = u' ' + str(su)
        elif end_word in [u'ثلاثة', u'أربعة', u'خمسة', u'ستة',
                            u'سبعة', u'ثمانية', u'تسعة', u'عشرة']:
            final_result = u' ' + str(sus)
        else:
            final_result = end_word + u' ' + str(su)
    elif int(list[0]) != 0 and int(list[1]) == 0:
        final_result = start_word + u' ' + currenc
    return final_result


if __name__ == '__main__':
    number = 23539000002.50
    currency = u' جنية مصري '

class account_currency(models.Model):
    _inherit = 'res.currency'

    arabic_unit_labels = fields.Char(string='Arabic Units')
    arabic_unit_label = fields.Char(string='Arabic Unit')
    arabic_subunit_labels= fields.Char(string='Arabic Subunits')
    arabic_subunit_label= fields.Char(string='Arabic Subunit')



class InvoiceOrder(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _compute_amount_in_word(self):
        for rec in self:
            rec.num_word = str(rec.currency_id.amount_to_text(rec.amount_total)) + ' only'

    @api.multi
    @api.depends('amount_total')
    def _compute_num_word_arabic(self):
        for rec in self:
            rec.num_word_arabic = "فقط "+ str(amount_to_text_ar(rec.amount_total,rec.currency_id.arabic_unit_label,rec.currency_id.arabic_unit_labels,rec.currency_id.arabic_subunit_label,rec.currency_id.arabic_subunit_labels))+" لا غير "

    num_word = fields.Char(string="Amount In Words:", compute='_compute_amount_in_word')
    num_word_arabic = fields.Char(compute='_compute_num_word_arabic')