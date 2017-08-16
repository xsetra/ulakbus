# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.settings import DATETIME_DEFAULT_FORMAT
from pyoko.db.connection import cache
from zengine.forms import JsonForm
from zengine.forms import fields
from zengine.models import TaskInvitation, WFInstance
from zengine.views.crud import CrudView, obj_filter, list_query
from zengine.lib.translation import gettext as _, gettext_lazy as __
from datetime import datetime, timedelta


class ProjeIslemGecmisiForm(JsonForm):
    """
    Projenin onaylandı, revizyona gönderildi gibi
    işlem geçmişini göstermek için kullanılan form.

    """

    class Meta:
        title = __(u"Proje İşlem Geçmişi")

    geri = fields.Button(__(u"Geri Dön"))


class BasvuruListeleme(CrudView):
    class Meta:
        model = "BAPProje"

    def __init__(self, current=None):
        CrudView.__init__(self, current)
        self.ListForm.add = None

    def islem_gecmisi_goster(self):
        """
        Projenin işlem geçmişini gösterir.

        """

        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_search"] = False
        self.output['objects'] = [[_(u'Eylem'), _(u'Açıklama'), _(u'Tarih')]]
        for islem in sorted(self.object.ProjeIslemGecmisi, key=lambda obj: obj.tarih):
            eylem = islem.eylem
            aciklama = islem.aciklama
            tarih = islem.tarih.strftime(DATETIME_DEFAULT_FORMAT) if islem.tarih else ''

            list_item = {
                "fields": [eylem, aciklama, tarih],
                "actions": '',
            }
            self.output['objects'].append(list_item)
        self.form_out(ProjeIslemGecmisiForm())

    def onayla_karari_sonrasi_islemler(self):
        """
        Listeden seçilen projenin onaylanmasına karar verilmiş ise proje sahibi
        öğretim üyesi bildirim ile bilgilendirilir.

        """

        role = self.object.basvuru_rolu
        role.send_notification(title=_(u"Proje Onayı"),
                               message=_(u"""%s adlı proje başvurunuz koordinasyon birimi
                                    tarafından onaylanarak gündeme alınmıştır.""" % self.object.ad),
                               typ=1,
                               url='',
                               sender=self.current.user
                               )

    def revizyon_karari_sonrasi_islemler(self):
        """
        Revizyon kararı verilmiş ise proje başvurusu iş akışı instance'ı bulunur
        ve invitation yollanır. Böylelikle öğretim üyesinin tekrardan iş akışına
        katılması ve projeyi revizyon etmesi sağlanır.

        """

        role = self.object.basvuru_rolu
        today = datetime.today()

        wfi = WFInstance.objects.get(wf_object=self.object.key, finished=True)
        wfi.finished = False
        wfi.data['karar'] = self.current.task_data['karar']
        wfi.data['revizyon_gerekce'] = self.current.task_data['revizyon_gerekce']
        wfi.step = '"bap_revizyon_noktasi", 1'
        wfi.blocking_save()

        cache.delete(wfi.key)

        role.send_notification(title=_(u"Proje Revizyon İsteği"),
                               message=_(u"""%s adlı başvurunuza koordinasyon birimi tarafından
                               revizyon istenmiştir. Aşağıda bulunan linke tıklayarak revizyon
                               işlemine devam edebilirsiniz.""" % self.object.ad),
                               typ=1,
                               url='#/cwf/bap_proje_basvuru/%s' % wfi.key,
                               sender=self.current.user
                               )
        inv = TaskInvitation(
            instance=wfi,
            role=role,
            wf_name=wfi.wf.name,
            progress=30,
            start_date=today,
            finish_date=today + timedelta(15)
        )
        inv.title = wfi.wf.title
        inv.save()

    def karar_sonrasi_islem_mesaji(self):
        """
        Koordinasyon biriminin kararından sonra başarılı işlem mesajı oluşturulur.

        """

        self.current.output['msgbox'] = {
            'type': 'info', "title": _(u'Kararınız İletildi'),
            "msg": _(u'%s projesi hakkındaki kararınız %s adlı personele iletilmiştir.') % (
                self.object.ad, self.object.yurutucu.__unicode__())}

    @obj_filter
    def basvuru_listeleme(self, obj, result):
        """
        Default action buttonlar, İncele ve İşlem Geçmişi ile değiştirilmiştir.

        """
        result['actions'] = [
            {'name': _(u'İncele'), 'cmd': 'incele', 'mode': 'normal', 'show_as': 'button'},
            {'name': _(u'İşlem Geçmişi'), 'cmd': 'islem_gecmisi', 'mode': 'normal',
             'show_as': 'button'},
            {'name': _(u'Hakem Daveti'), 'cmd': 'hakem_daveti', 'mode': 'normal',
             'show_as': 'button'},
            {'name': _(u'Komisyon Üyesi Ata'), 'cmd': 'komisyon_uyesi_atama', 'mode': 'normal',
             'show_as': 'button'}
        ]
        if obj.ProjeDegerlendirmeleri:
            result['actions'].append(
                {'name': _(u'Değerlendirmeler'), 'cmd': 'degerlendirmeler', 'mode': 'normal',
                 'show_as': 'button'}
            )

    @list_query
    def list_by_ordered(self, queryset):
        """
        Onaya gönderilen, onaylanan veya revizyon istenen projeler listelenir.

        2: Öğretim elemanı tarafından koordinasyon birimine onaya gönderildi.
        3: Koordinasyon birimi tarafından öğretim elemanına revizyon için gönderildi.
        4: Koordinasyon birimi projeyi onayladı.
        """
        return queryset.filter(durum__in=[2, 3, 4]).order_by()
