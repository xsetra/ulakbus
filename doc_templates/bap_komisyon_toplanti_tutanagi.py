# -*- coding: utf-8 -*-

from secretary import Renderer

template = "bap_komisyon_toplanti_tutanagi.odt"

karar_tarihi = "07-08-2017"
oturum_no = "oturum no 1"
karar_no = "karar_no 1"

baskan = "Baskan"
bap_koordinatoru = "BAP Koord."
uye1 = "uye ve ismi"


kararlar = []
karar1 = {"no":123, "fakulte":"teknoloji", "unvan":"zetaops", "unvan_no":123, "tutar":5123.23, "proje":"ulakbus"}
kararlar.append(karar1)
kararlar.append(karar1)
kararlar.append(karar1)
kararlar.append(karar1)

kararlar.append(karar1)
kararlar.append(karar1)

kararlar.append(karar1)
kararlar.append(karar1)



engine = Renderer()
result = engine.render(template, karar_tarihi=karar_tarihi, oturum_no=oturum_no, karar_no=karar_no, kararlar=kararlar, baskan=baskan, bap_koordinatoru=bap_koordinatoru, uye_1=uye1, uye_2=uye1, uye_3=uye1, uye_4=uye1, uye_5=uye1)

fp = open("rendered_template.odt", "wb")
fp.write(result)
fp.close()
