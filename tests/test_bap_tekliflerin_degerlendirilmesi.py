# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
import time
from ulakbus.models import User, BAPTeklif, BAPButcePlani, BAPSatinAlma, BAPTeklifFiyatIsleme
from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    """
    Firmaların, teklife açık bütçe kalemlerine 
    teklif vermesini sağlayan iş akışı testi.

    """

    def test_bap_tekliflerin_degerlendirilmesi(self):
        obj_id = "JgrLlrsr61OEADCLmyVWDWrVbg1"
        self.prepare_client('/bap_tekliflerin_degerlendirilmesi',
                            username='bap_koordinasyon_birimi_1')

        resp = self.client.post()
        assert resp.json['forms']['schema']['title'] == "Teklife Kapanmış Satın Alma Duyuruları"

        resp = self.client.post(wf='bap_tekliflerin_degerlendirilmesi',
                                cmd="gor",
                                object_id=obj_id)

        assert "4 Kalem Kırtasiye Malzemesi" in resp.json['forms']['schema']['title']

        resp = self.client.post(wf='bap_tekliflerin_degerlendirilmesi',
                                cmd="isle",
                                data_key="530g49RwA2nX5fzwEMWurrbqouN")

        assert "Test Firma 2" in resp.json['forms']['schema']['title']

        key_dict = {'7uvtCCHGqcjnAdhVMDtBKYiFQ2T': 0.5,
                    'BNfJoUkHVZKH2dmjzZEuJST4its': None,
                    'WD0K3k6syBXJOX9hkS5wBmnCQBD': 8,
                    'Jj8IRgcmS6HFNKPegm5wASOjUAB': None}

        list_node_data = []
        for key, birim in key_dict.items():
            kalem = BAPButcePlani.objects.get(key)
            data = {'adet': kalem.adet,
                    'birim_fiyat': birim,
                    'kalem': kalem.ad,
                    'key': key
                    }
            list_node_data.append(data)

        resp = self.client.post(wf='bap_tekliflerin_degerlendirilmesi',
                                cmd="kaydet",
                                form={'TeklifIsle': list_node_data})

        assert resp.json['msgbox']['title'] == "İşlem Mesajı"
        assert "Test Firma 2" in resp.json['msgbox']['msg']

        resp = self.client.post(wf='bap_tekliflerin_degerlendirilmesi',
                                cmd="degerlendir")

        assert resp.json['msgbox']['title'] == "Hata Mesajı"

        resp = self.client.post(wf='bap_tekliflerin_degerlendirilmesi',
                                cmd="duzenle",
                                data_key="530g49RwA2nX5fzwEMWurrbqouN")

        time.sleep(2)
        for obj in resp.json['forms']['model']['TeklifIsle']:
            assert key_dict[obj['key']] == obj['birim_fiyat']

        for obj in list_node_data:
            if obj['key'] == 'WD0K3k6syBXJOX9hkS5wBmnCQBD':
                obj['birim_fiyat'] = 11.5
                key_dict['WD0K3k6syBXJOX9hkS5wBmnCQBD'] = obj['birim_fiyat']

        self.client.post(wf='bap_tekliflerin_degerlendirilmesi',
                         cmd="kaydet",
                         form={'TeklifIsle': list_node_data})

        resp = self.client.post(wf='bap_tekliflerin_degerlendirilmesi',
                                cmd="duzenle",
                                data_key="530g49RwA2nX5fzwEMWurrbqouN")

        for obj in resp.json['forms']['model']['TeklifIsle']:
            assert key_dict[obj['key']] == obj['birim_fiyat']

        self.client.post(wf='bap_tekliflerin_degerlendirilmesi',
                         cmd="geri_don")

        key_list = ['GqoC0MAcMAw2aedOcOi4JvjGFkd',
                    '1LqWUtM7s0Wsvj8rDYbvnGvYujy',
                    'GSX4LNZntJicEmD4k0DQ3u7M9ME']

        for key in key_list:
            self.client.post(wf='bap_tekliflerin_degerlendirilmesi',
                             cmd="isle",
                             data_key=key)

            self.client.post(wf='bap_tekliflerin_degerlendirilmesi',
                             cmd="kaydet",
                             form={'TeklifIsle': list_node_data})

        time.sleep(1)

        resp = self.client.post(wf='bap_tekliflerin_degerlendirilmesi',
                                cmd="degerlendir")

        assert resp.json['forms']['schema'][
                   'title'] == "4 Kalem Kırtasiye Malzemesi Alımı Satın Alma Duyurusuna Verilen Teklifler"

        resp = self.client.post(wf='bap_tekliflerin_degerlendirilmesi',
                                cmd="belirle")

        assert "4 Kalem Kırtasiye Malzemesi" in resp.json['forms']['schema']['title']

        key_dict = {'7uvtCCHGqcjnAdhVMDtBKYiFQ2T': 'QbuMU7XC8iG9oO18SqAUNlVjFXi',
                    'BNfJoUkHVZKH2dmjzZEuJST4its': None,
                    'WD0K3k6syBXJOX9hkS5wBmnCQBD': '2DsrZxp3dR6E6xZkDizahVYSMY6',
                    'Jj8IRgcmS6HFNKPegm5wASOjUAB': None}

        list_node_data = []
        for key, firma in key_dict.items():
            kalem = BAPButcePlani.objects.get(key)
            data = {'adet': kalem.adet,
                    'firma': firma,
                    'kalem': kalem.ad,
                    'key': key}
            list_node_data.append(data)

        resp = self.client.post(wf='bap_tekliflerin_degerlendirilmesi',
                                cmd="ilerle",
                                form={'KazananFirmalar': list_node_data})

        assert resp.json['forms']['schema']['title'] == "Kazanan Firmaların Onayı"

        resp = self.client.post(wf='bap_tekliflerin_degerlendirilmesi',
                                cmd="onayla")

        assert resp.json['msgbox']['title'] == "İşlem Bilgilendirme"

        satin_alma = BAPSatinAlma.objects.get(obj_id)
        BAPTeklifFiyatIsleme.objects.filter(satin_alma=satin_alma).delete()
        for teklif in BAPTeklif.objects.filter(satin_alma=satin_alma):
            teklif.fiyat_islemesi = False
            teklif.save()
