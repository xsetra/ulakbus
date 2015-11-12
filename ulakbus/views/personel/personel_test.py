# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
import random

from pyoko import form
from zengine.lib.forms import JsonForm
from zengine.views.base import SimpleView, BaseView
from zengine.views.crud import CrudView


class TCKNForm(JsonForm):
    class Meta:
        title = 'Yeni Personel'

    tcno = form.String("TC No")
    ekle = form.Button("Ekle")


class YeniPersonelEkle(BaseView):
    def __init__(self, current=None):
        current.output['forms'] = TCKNForm().serialize()


def get_personel_from_hitap(current):
    tcno = current.input['form']['tcno']
    current.task_data['hitap_tamam'] = True
    current.task_data['tcno'] = tcno
    current.set_message(title='%s TC no için Hitap servisi başlatıldı' % tcno,
                        msg='', typ=1, url="/wftoken/%s" % current.token)

def get_by_tckn(current):
    current.task_data['aks_tamam'] = True

def get_from_mernis(current):
    # %60 ihtimalle yeni atama ekranina gidecek, %40  hata verecek...
    current.task_data['mernis_tamam'] = random.choice((1,2,3,4,5)) in (1,2,3)
    current.set_message(title='%s için Mernis\'e erişilemedi' % current.task_data['tcno'],
                        msg='', typ=1, url="/wftoken/%s" % current.token)

class AtamaYap(CrudView):
    MODEL = 'Atama'

class HataIncele(JsonForm):
    class Meta:
        title = 'İşlem Başarısız Oldu'
        help_text = "Dasd askdhjkasbdajs gasjkhdgasjkhg ajhdgas askjdhaskjhasj dhas dhaskjdhas" \
                    "aklsjsd haskljdhasklj dhaskldh akdhaksj dajskh dgasjkhdg ajshgdasj dgas" \
                    "aslkd haskldhaskdhaskldhaskl dhaklsd"

    restart = form.Button("Tekrar Dene", flow="hata_to_tcno")
    cancel = form.Button("İşlemi İptal Et", flow="iptal_hata")


# class Iptal(JsonForm):
#     class Meta:
#         title = 'İptal'
#         help_text = "Başarıyla iptal edildi"

def delete_draft(current):
    current.output['msgbox'] = {'type': 'info', "title": 'İptal', "msg": 'Başarıyla iptal edildi'}


class review_service_errors(SimpleView):
    def show_view(self):
        self.current.output['forms'] = HataIncele().serialize()
