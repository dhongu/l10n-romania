-- Delta posta-romana.ro (live) + OSM. Idempotent.
-- Comune: INSERT/UPDATE. Orase: UPDATE pe loc + INSERT + DELETE doar pt randuri nefolosite.
BEGIN;
SELECT setval('res_zip_id_seq', (SELECT MAX(id) FROM res_zip));

-- === comune OFFICE_ADD ===
UPDATE res_zip SET office='Aita Mare Agentie' WHERE id=25903 AND state='Covasna' AND city='Aita Mare';
UPDATE res_zip SET office='Aita Mare Agentie' WHERE id=25904 AND state='Covasna' AND city='Aita Medie';
UPDATE res_zip SET office='Aita Seaca Agentie' WHERE id=25905 AND state='Covasna' AND city='Aita Seaca';
UPDATE res_zip SET office='Cernat Oficiu' WHERE id=25943 AND state='Covasna' AND city='Albis';
UPDATE res_zip SET office='Turia Ghiseu' WHERE id=26001 AND state='Covasna' AND city='Alungeni';
UPDATE res_zip SET office='Ghidfalau Agentie' WHERE id=26048 AND state='Covasna' AND city='Anghelus';
UPDATE res_zip SET office='Reci Agentie' WHERE id=26057 AND state='Covasna' AND city='Aninoasa';
UPDATE res_zip SET office='Araci Agentie' WHERE id=26087 AND state='Covasna' AND city='Araci';
UPDATE res_zip SET office='Arcus Agentie' WHERE id=26108 AND state='Covasna' AND city='Arcus';
UPDATE res_zip SET office='Araci Agentie' WHERE id=26141 AND state='Covasna' AND city='Ariusd';
UPDATE res_zip SET office='Bacel Agentie' WHERE id=26386 AND state='Covasna' AND city='Bacel';
UPDATE res_zip SET office='Baraolt Oficiu' WHERE id=26322 AND state='Covasna' AND city='Baraolt';
UPDATE res_zip SET office='Barcani Ghiseu' WHERE id=26331 AND state='Covasna' AND city='Barcani';
UPDATE res_zip SET office='Batanii Mari Agentie' WHERE id=26633 AND state='Covasna' AND city='Batani';
UPDATE res_zip SET office='Batanii Mari Agentie' WHERE id=26634 AND state='Covasna' AND city='Batanii Mari';
UPDATE res_zip SET office='Batanii Mari Agentie' WHERE id=26635 AND state='Covasna' AND city='Batanii Mici';
UPDATE res_zip SET office='Poian Agentie' WHERE id=26770 AND state='Covasna' AND city='Belani';
UPDATE res_zip SET office='Belin Agentie' WHERE id=26787 AND state='Covasna' AND city='Belin';
UPDATE res_zip SET office='Belin-Vale Agentie' WHERE id=26788 AND state='Covasna' AND city='Belin-Vale';
UPDATE res_zip SET office='Biborteni Agentie' WHERE id=26895 AND state='Covasna' AND city='Biborteni';
UPDATE res_zip SET office='Ozun Agentie' WHERE id=26910 AND state='Covasna' AND city='Bicfalau';
UPDATE res_zip SET office='Reci Agentie' WHERE id=26960 AND state='Covasna' AND city='Bita';
UPDATE res_zip SET office='Bixad Agentie' WHERE id=26967 AND state='Covasna' AND city='Bixad';
UPDATE res_zip SET office='Bodoc Agentie' WHERE id=27074 AND state='Covasna' AND city='Bodoc';
UPDATE res_zip SET office='Biborteni Agentie' WHERE id=27076 AND state='Covasna' AND city='Bodos';
UPDATE res_zip SET office='Borosneu Mare Agentie' WHERE id=27240 AND state='Covasna' AND city='Borosneu Mare';
UPDATE res_zip SET office='Valea Mare Agentie' WHERE id=27241 AND state='Covasna' AND city='Borosneu Mic';
UPDATE res_zip SET office='Intorsura Buzaului Oficiu' WHERE id=27405 AND state='Covasna' AND city='Bradet';
UPDATE res_zip SET office='Bradut Agentie' WHERE id=27417 AND state='Covasna' AND city='Bradut';
UPDATE res_zip SET office='Brates Agentie' WHERE id=27370 AND state='Covasna' AND city='Brates';
UPDATE res_zip SET office='Bretcu Oficiu' WHERE id=27507 AND state='Covasna' AND city='Bretcu';
UPDATE res_zip SET office='Valea Crisului Agentie' WHERE id=27859 AND state='Covasna' AND city='Calnic';
UPDATE res_zip SET office='Capeni Agentie' WHERE id=28071 AND state='Covasna' AND city='Capeni';
UPDATE res_zip SET office='Poian Agentie' WHERE id=28109 AND state='Covasna' AND city='Carpinenii';
UPDATE res_zip SET office='Sanzieni Ghiseu' WHERE id=27927 AND state='Covasna' AND city='Casinu Mic';
UPDATE res_zip SET office='Catalina Agentie' WHERE id=27931 AND state='Covasna' AND city='Catalina';
UPDATE res_zip SET office='Cernat Oficiu' WHERE id=28355 AND state='Covasna' AND city='Cernat';
UPDATE res_zip SET office='Chichis Agentie' WHERE id=28469 AND state='Covasna' AND city='Chichis';
UPDATE res_zip SET office='Covasna 1 Oficiu' WHERE id=28565 AND state='Covasna' AND city='Chiurus';
UPDATE res_zip SET office='Comandau Agentie' WHERE id=28973 AND state='Covasna' AND city='Comandau';
UPDATE res_zip SET office='Covasna 1 Oficiu' WHERE id=29314 AND state='Covasna' AND city='Covasna';
UPDATE res_zip SET office='Zabratau Agentie' WHERE id=29353 AND state='Covasna' AND city='Crasna';
UPDATE res_zip SET office='Dalnic Agentie' WHERE id=29655 AND state='Covasna' AND city='Dalnic';
UPDATE res_zip SET office='Dobarlau Agentie' WHERE id=29957 AND state='Covasna' AND city='Dobarlau';
UPDATE res_zip SET office='Ilieni Agentie' WHERE id=29960 AND state='Covasna' AND city='Dobolii de Jos';
UPDATE res_zip SET office='Borosneu Mare Agentie' WHERE id=29961 AND state='Covasna' AND city='Dobolii de Sus';
UPDATE res_zip SET office='Doboseni Agentie' WHERE id=29963 AND state='Covasna' AND city='Doboseni';
UPDATE res_zip SET office='Estelnic Agentie' WHERE id=30387 AND state='Covasna' AND city='Estelnic';
UPDATE res_zip SET office='Filia Agentie' WHERE id=30598 AND state='Covasna' AND city='Filia';
UPDATE res_zip SET office='Intorsura Buzaului Oficiu' WHERE id=30678 AND state='Covasna' AND city='Floroaia';
UPDATE res_zip SET office='Ghelinta Ghiseu' WHERE id=31032 AND state='Covasna' AND city='Ghelinta';
UPDATE res_zip SET office='Ghidfalau Agentie' WHERE id=31072 AND state='Covasna' AND city='Ghidfalau';
UPDATE res_zip SET office='Haghig Ghiseu' WHERE id=31589 AND state='Covasna' AND city='Haghig';
UPDATE res_zip SET office='Ghelinta Ghiseu' WHERE id=31574 AND state='Covasna' AND city='Harale';
UPDATE res_zip SET office='Catalina Agentie' WHERE id=31629 AND state='Covasna' AND city='Hatuica';
UPDATE res_zip SET office='Herculian Agentie' WHERE id=31664 AND state='Covasna' AND city='Herculian';
UPDATE res_zip SET office='Valcele Agentie' WHERE id=31677 AND state='Covasna' AND city='Hetea';
UPDATE res_zip SET office='Ojdula Agentie' WHERE id=31687 AND state='Covasna' AND city='Hilib';
UPDATE res_zip SET office='Haghig Ghiseu' WHERE id=31895 AND state='Covasna' AND city='Iaras';
UPDATE res_zip SET office='Cernat Oficiu' WHERE id=31921 AND state='Covasna' AND city='Icafalau';
UPDATE res_zip SET office='Ilieni Agentie' WHERE id=31995 AND state='Covasna' AND city='Ilieni';
UPDATE res_zip SET office='Catalina Agentie' WHERE id=32014 AND state='Covasna' AND city='Imeni';
UPDATE res_zip SET office='Intorsura Buzaului Oficiu' WHERE id=32202 AND state='Covasna' AND city='Întorsura Buzaului';
UPDATE res_zip SET office='Barcani Ghiseu' WHERE id=32370 AND state='Covasna' AND city='Ladauti';
UPDATE res_zip SET office='Lemnia Agentie' WHERE id=32441 AND state='Covasna' AND city='Lemnia';
UPDATE res_zip SET office='Let Agentie' WHERE id=32481 AND state='Covasna' AND city='Let';
UPDATE res_zip SET office='Lisnau Agentie' WHERE id=32538 AND state='Covasna' AND city='Lisnau';
UPDATE res_zip SET office='Lisnau Agentie' WHERE id=32539 AND state='Covasna' AND city='Lisnau-Vale';
UPDATE res_zip SET office='Marcus Agentie' WHERE id=32717 AND state='Covasna' AND city='Lunca Marcusului';
UPDATE res_zip SET office='Bacel Agentie' WHERE id=32723 AND state='Covasna' AND city='Lunca Ozunului';
UPDATE res_zip SET office='Lunga Agentie' WHERE id=32753 AND state='Covasna' AND city='Lunga';
UPDATE res_zip SET office='Mereni Agentie' WHERE id=32797 AND state='Covasna' AND city='Lutoasa';
UPDATE res_zip SET office='Lisnau Agentie' WHERE id=32959 AND state='Covasna' AND city='Magherus';
UPDATE res_zip SET office='Malnas Agentie' WHERE id=32835 AND state='Covasna' AND city='Malnas';
UPDATE res_zip SET office='Malnas Agentie' WHERE id=32836 AND state='Covasna' AND city='Malnas-Bai';
UPDATE res_zip SET office='Marcus Agentie' WHERE id=33089 AND state='Covasna' AND city='Marcus';
UPDATE res_zip SET office='Martineni Agentie' WHERE id=33090 AND state='Covasna' AND city='Marcusa';
UPDATE res_zip SET office='Bretcu Oficiu' WHERE id=33117 AND state='Covasna' AND city='Martanus';
UPDATE res_zip SET office='Martineni Agentie' WHERE id=33119 AND state='Covasna' AND city='Martineni';
UPDATE res_zip SET office='Mereni Agentie' WHERE id=33227 AND state='Covasna' AND city='Mereni';
UPDATE res_zip SET office='Sita Buzaului Ghiseu' WHERE id=33250 AND state='Covasna' AND city='Merisor';
UPDATE res_zip SET office='Micfalau Agentie' WHERE id=33293 AND state='Covasna' AND city='Micfalau';
UPDATE res_zip SET office='Capeni Agentie' WHERE id=33300 AND state='Covasna' AND city='Miclosoara';
UPDATE res_zip SET office='Moacsa Agentie' WHERE id=33481 AND state='Covasna' AND city='Moacsa';
UPDATE res_zip SET office='Bretcu Oficiu' WHERE id=34120 AND state='Covasna' AND city='Oituz';
UPDATE res_zip SET office='Ojdula Agentie' WHERE id=34121 AND state='Covasna' AND city='Ojdula';
UPDATE res_zip SET office='Bodoc Agentie' WHERE id=34148 AND state='Covasna' AND city='Olteni';
UPDATE res_zip SET office='Ozun Agentie' WHERE id=34298 AND state='Covasna' AND city='Ozun';
UPDATE res_zip SET office='Batanii Mari Agentie' WHERE id=34299 AND state='Covasna' AND city='Ozunca-Bai';
UPDATE res_zip SET office='Brates Agentie' WHERE id=34300 AND state='Covasna' AND city='Pachia';
UPDATE res_zip SET office='Moacsa Agentie' WHERE id=34391 AND state='Covasna' AND city='Padureni';
UPDATE res_zip SET office='Papauti Agentie' WHERE id=34449 AND state='Covasna' AND city='Papauti';
UPDATE res_zip SET office='Zabala Agentie' WHERE id=34645 AND state='Covasna' AND city='Peteni';
UPDATE res_zip SET office='Sanzieni Ghiseu' WHERE id=34681 AND state='Covasna' AND city='Petriceni';
UPDATE res_zip SET office='Poian Agentie' WHERE id=35050 AND state='Covasna' AND city='Poian';
UPDATE res_zip SET office='Capeni Agentie' WHERE id=35553 AND state='Covasna' AND city='Racosul de Sus';
UPDATE res_zip SET office='Reci Agentie' WHERE id=35811 AND state='Covasna' AND city='Reci';
UPDATE res_zip SET office='Reci Agentie' WHERE id=36134 AND state='Covasna' AND city='Saciova';
UPDATE res_zip SET office='Ilieni Agentie' WHERE id=36482 AND state='Covasna' AND city='Sancraiu';
UPDATE res_zip SET office='Reci Agentie' WHERE id=36563 AND state='Covasna' AND city='Santionlunca';
UPDATE res_zip SET office='Sanzieni Ghiseu' WHERE id=36566 AND state='Covasna' AND city='Sanzieni';
UPDATE res_zip SET office='Barcani Ghiseu' WHERE id=36401 AND state='Covasna' AND city='Saramas';
UPDATE res_zip SET office='Intorsura Buzaului Oficiu' WHERE id=36670 AND state='Covasna' AND city='Scradoasa';
UPDATE res_zip SET office='Sita Buzaului Ghiseu' WHERE id=36872 AND state='Covasna' AND city='Sita Buzaului';
UPDATE res_zip SET office='Tamasfalau Agentie' WHERE id=37330 AND state='Covasna' AND city='Surcea';
UPDATE res_zip SET office='Bradut Agentie' WHERE id=37695 AND state='Covasna' AND city='Talisoara';
UPDATE res_zip SET office='Tamasfalau Agentie' WHERE id=37661 AND state='Covasna' AND city='Tamasfalau';
UPDATE res_zip SET office='Targu Secuiesc Oficiu' WHERE id=37807 AND state='Covasna' AND city='Targu Secuiesc';
UPDATE res_zip SET office='Brates Agentie' WHERE id=37875 AND state='Covasna' AND city='Telechia';
UPDATE res_zip SET office='Let Agentie' WHERE id=38318 AND state='Covasna' AND city='tufalau';
UPDATE res_zip SET office='Turia Ghiseu' WHERE id=38207 AND state='Covasna' AND city='Turia';
UPDATE res_zip SET office='Valcele Agentie' WHERE id=39108 AND state='Covasna' AND city='Valcele';
UPDATE res_zip SET office='Valea Crisului Agentie' WHERE id=38632 AND state='Covasna' AND city='Valea Crisului';
UPDATE res_zip SET office='Dobarlau Agentie' WHERE id=38646 AND state='Covasna' AND city='Valea Dobarlaului';
UPDATE res_zip SET office='Valea Mare Agentie' WHERE id=38742 AND state='Covasna' AND city='Valea Mare';
UPDATE res_zip SET office='Valea Mare Agentie' WHERE id=38778 AND state='Covasna' AND city='Valea Mica';
UPDATE res_zip SET office='Estelnic Agentie' WHERE id=38869 AND state='Covasna' AND city='Valea Scurta';
UPDATE res_zip SET office='Sanzieni Ghiseu' WHERE id=38873 AND state='Covasna' AND city='Valea Seaca';
UPDATE res_zip SET office='Aita Seaca Agentie' WHERE id=38942 AND state='Covasna' AND city='Valea Zalanului';
UPDATE res_zip SET office='Varghis Agentie' WHERE id=39163 AND state='Covasna' AND city='Varghis';
UPDATE res_zip SET office='Zabala Agentie' WHERE id=39532 AND state='Covasna' AND city='Zabala';
UPDATE res_zip SET office='Zabratau Agentie' WHERE id=39535 AND state='Covasna' AND city='Zabratau';
UPDATE res_zip SET office='Zagon Agentie' WHERE id=39514 AND state='Covasna' AND city='Zagon';

-- === oras Sfantu Gheorghe (Covasna) ===
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9916 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9947 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9964 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9895 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9907 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9956 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10023 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10030 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10068 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9905 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Varadi Jozsef', office='Sfantu Gheorghe 1 Oficiu' WHERE id=10062 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9885 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9992 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9890 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9978 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Korosi Csoma Sandor', office='Sfantu Gheorghe 1 Oficiu' WHERE id=9979 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9897 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9911 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9999 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10017 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10022 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9902 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9928 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9976 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10052 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9904 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9915 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9934 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9933 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9971 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Orban Balazs', office='Sfantu Gheorghe 1 Oficiu' WHERE id=10016 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9918 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9927 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9939 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9958 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9914 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10067 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9952 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9974 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9983 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9899 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9943 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9986 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Gyarfas Jeno', office='Sfantu Gheorghe 1 Oficiu' WHERE id=9965 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9891 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9960 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10005 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9940 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9994 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10055 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9926 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9963 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10008 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10036 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9938 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10020 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10058 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Tigaretei', office='Sfantu Gheorghe 1 Oficiu' WHERE id=10059 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9919 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9942 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9977 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9998 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9892 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9910 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9972 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10012 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9937 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10021 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9883 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9922 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10006 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Dozsa Gyorgy nr. 21/A-T; 20-T', office='Sfantu Gheorghe 1 Oficiu' WHERE id=9936 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9945 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10050 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Zold Peter', office='Sfantu Gheorghe 1 Oficiu' WHERE id=10070 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9903 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9944 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9973 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Jozsef Attila', office='Sfantu Gheorghe 1 Oficiu' WHERE id=9975 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9906 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9917 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9946 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10019 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9901 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9991 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10026 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10041 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9949 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10034 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10066 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10027 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10035 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10040 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10063 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10071 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Kos Karoly', office='Sfantu Gheorghe 1 Oficiu' WHERE id=9980 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9990 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10053 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Dozsa Gyorgy nr. 1-21; 2-18', office='Sfantu Gheorghe 1 Oficiu' WHERE id=9935 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10060 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10065 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9954 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10048 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9932 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Laszlo Ferenc', office='Sfantu Gheorghe 1 Oficiu' WHERE id=9985 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10009 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10024 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10037 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10046 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9900 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9953 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10061 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9913 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10051 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu' WHERE id=9888 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu' WHERE id=9950 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu' WHERE id=10007 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu' WHERE id=9966 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu' WHERE id=10004 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu' WHERE id=10025 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu' WHERE id=9881 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu' WHERE id=9968 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu' WHERE id=10039 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu' WHERE id=9889 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu' WHERE id=9931 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu' WHERE id=10001 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu' WHERE id=10018 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9884 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Nagy Gyorgy', office='Sfantu Gheorghe 1 Oficiu' WHERE id=10010 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9957 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10013 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10043 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9925 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9984 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=10011 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET office='Sfantu Gheorghe 1 Oficiu' WHERE id=9961 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_type='Alee', office='Sfantu Gheorghe 1 Oficiu' WHERE id=9923 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_type='Alee', office='Sfantu Gheorghe 1 Oficiu' WHERE id=9995 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_type='Alee', office='Sfantu Gheorghe 1 Oficiu' WHERE id=10069 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_type='Alee', office='Sfantu Gheorghe 1 Oficiu' WHERE id=9924 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_type='Alee', office='Sfantu Gheorghe 1 Oficiu' WHERE id=9996 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_type='Alee', office='Sfantu Gheorghe 1 Oficiu' WHERE id=9941 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_type='Alee', office='Sfantu Gheorghe 1 Oficiu' WHERE id=10056 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_type='Alee', office='Sfantu Gheorghe 1 Oficiu' WHERE id=10054 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_type='Alee', office='Sfantu Gheorghe 1 Oficiu' WHERE id=10038 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_type='Alee', office='Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu' WHERE id=9894 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_type='Alee', office='Sfantu Gheorghe 1 Oficiu' WHERE id=9993 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_type='Bulevard', office='Sfantu Gheorghe 1 Oficiu' WHERE id=9970 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Libertatii nr. 1-5; 6-T', office='Sfantu Gheorghe 1 Oficiu' WHERE id=9989 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Mihai Viteazul nr. 1-T', office='Sfantu Gheorghe 1 Oficiu' WHERE id=10003 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Gabor Aron nr. 2-T', office='Sfantu Gheorghe 1 Oficiu' WHERE id=9948 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Kossuth Lajos', office='Sfantu Gheorghe 1 Oficiu' WHERE id=9981 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Mihai Viteazul nr. 2-T', office='Sfantu Gheorghe 1 Oficiu' WHERE id=10002 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Grigore Balan, general nr. 5-21; 2-14', office='Sfantu Gheorghe 1 Oficiu' WHERE id=9959 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Caminului nr. 1-T', office='Sfantu Gheorghe 1 Oficiu' WHERE id=9908 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='1 Decembrie 1918 nr. 21-45; 16-106', office='Sfantu Gheorghe 1 Oficiu' WHERE id=9886 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='1 Decembrie 1918 nr. 47-109', office='Sfantu Gheorghe 1 Oficiu' WHERE id=9887 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Balcescu Nicolae nr. 1-15; 2-18', office='Sfantu Gheorghe 1 Oficiu' WHERE id=9898 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Oltului nr. 1-T; 2-42; 52-T', office='Sfantu Gheorghe 1 Oficiu' WHERE id=10015 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Crangului nr. 1-11; 2-T', office='Sfantu Gheorghe 1 Oficiu' WHERE id=9921 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Caminului nr. 2-T', office='Sfantu Gheorghe 1 Oficiu' WHERE id=9909 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Grigore Balan, general nr. 43-51; 16-50', office='Sfantu Gheorghe 1 Oficiu' WHERE id=9962 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Stadionului nr. 2-8, 12-28', office='Sfantu Gheorghe 1 Oficiu' WHERE id=10049 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Goldis Vasile nr. 2-12', office='Sfantu Gheorghe 1 Oficiu' WHERE id=9955 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Stadionului nr. 9; 10', office='Sfantu Gheorghe 1 Oficiu' WHERE id=10047 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Harniciei nr. 1-T; 2-10, 20-T', office='Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu' WHERE id=9967 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Armata Romana nr. 1-35; 2-48', office='Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu' WHERE id=9893 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Sporturilor nr. 1- 3; 2 - 4', office='Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu' WHERE id=10042 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Oltului nr. 44-50', office='Sfantu Gheorghe 1 Oficiu' WHERE id=10014 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Puskas Tivadar nr. 1-63; 2-64', office='Sfantu Gheorghe 1 Oficiu' WHERE id=10029 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Sporturilor nr. 11-T; 6-T', office='Sfantu Gheorghe 1 Oficiu' WHERE id=10044 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='1 Decembrie 1918 bl. 4', office='Sfantu Gheorghe 1 Oficiu' WHERE id=9882 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Daliei nr. 2-T', office='Sfantu Gheorghe 1 Oficiu' WHERE id=9930 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Lacramioarei nr. 1-T; 2-14', office='Sfantu Gheorghe 1 Oficiu' WHERE id=9988 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Daliei nr. 1-T', office='Sfantu Gheorghe 1 Oficiu' WHERE id=9929 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Lacramioarei nr. 16-T', office='Sfantu Gheorghe 1 Oficiu' WHERE id=9987 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Puskas Tivadar nr. 65-T; 66-T', office='Sfantu Gheorghe 1 Oficiu' WHERE id=10028 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Luceafarului nr. 13-T; 14-T', street_type='Alee', office='Sfantu Gheorghe 1 Oficiu' WHERE id=9997 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET name='520092', country_id=NULL, office='Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu' WHERE id=9912 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET name='520092', country_id=NULL, office='Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu' WHERE id=9920 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET name='520092', country_id=NULL, office='Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu' WHERE id=10031 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET name='520092', country_id=NULL, office='Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu' WHERE id=10057 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET name='520092', country_id=NULL, office='Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu' WHERE id=10064 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Banki Donat', office='Sfantu Gheorghe 1 Oficiu' WHERE id=9896 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Ghioceilor', office='Sfantu Gheorghe 1 Oficiu' WHERE id=9951 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Cioflec Romulus nr. 9-T; 12-T', office='Sfantu Gheorghe 1 Oficiu' WHERE id=10033 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Horea, Closca si Crisan', office='Sfantu Gheorghe 1 Oficiu' WHERE id=9969 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Cioflec Romulus nr. 1-7; 2-10', office='Sfantu Gheorghe 1 Oficiu' WHERE id=10032 AND state='Covasna' AND city='Sfantu Gheorghe';
UPDATE res_zip SET street_name='Martinovics Ignac', office='Sfantu Gheorghe 1 Oficiu' WHERE id=10000 AND state='Covasna' AND city='Sfantu Gheorghe';
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Piata', 'Fantanii', '520009', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520009' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Piata' AND COALESCE(street_name, '')='Fantanii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Popoviciu Iosif', '520009', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520009' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Popoviciu Iosif');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Carierei', '520010', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520010' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Carierei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Kozak David', '520010', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520010' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Kozak David');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Gyarfas Gyozo', '520015', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520015' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Gyarfas Gyozo');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Paltineanu Grigore, dr.', '520015', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520015' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Paltineanu Grigore, dr.');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Rezervorului', '520015', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520015' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Rezervorului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Nistor Aurel', '520020', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520020' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Nistor Aurel');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Balazs Marton', '520023', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520023' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Balazs Marton');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Tavaszi Sandor', '520023', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520023' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Tavaszi Sandor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Piata', 'Sfantu Gheorghe', '520023', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520023' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Piata' AND COALESCE(street_name, '')='Sfantu Gheorghe');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Piata', 'Luther', '520024', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520024' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Piata' AND COALESCE(street_name, '')='Luther');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Alee', 'Fortuna', '520026', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520026' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Fortuna');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Ingusta', '520032', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520032' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ingusta');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Stramba', '520033', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520033' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Stramba');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Banyai Janos', '520034', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520034' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Banyai Janos');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Beke Gyorgy', '520034', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520034' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Beke Gyorgy');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Kisszek', '520034', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520034' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Kisszek');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Sylvester Lajos', '520035', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520035' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Sylvester Lajos');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Domokos Geza', '520035', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520035' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Domokos Geza');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Birtalan Akos', '520035', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520035' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Birtalan Akos');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Baasz Imre', '520035', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520035' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Baasz Imre');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Szekely Zoltan', '520035', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520035' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Szekely Zoltan');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Konya Adam', '520035', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520035' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Konya Adam');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Plugor Sandor', '520035', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520035' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Plugor Sandor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Rauca-Rauceanu Isidor', '520035', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520035' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Rauca-Rauceanu Isidor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Lorincz Csaba', '520035', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520035' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Lorincz Csaba');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Kiraly Karoly', '520035', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520035' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Kiraly Karoly');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Ferencvaros', '520037', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520037' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ferencvaros');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Gelei Jozsef', '520037', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520037' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Gelei Jozsef');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Gaal Sandor', '520037', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520037' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Gaal Sandor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Albert Almos', '520037', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520037' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Albert Almos');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Moldovan Nicolae', '520037', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520037' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Moldovan Nicolae');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Imreh Istvan', '520037', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520037' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Imreh Istvan');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Puskas Ferenc', '520037', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520037' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Puskas Ferenc');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Peter Laszlo', '520037', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520037' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Peter Laszlo');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Cegled', '520038', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520038' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Cegled');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Gernald Antal', '520038', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520038' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Gernald Antal');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Rodosto', '520038', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520038' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Rodosto');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Cantarului', '520039', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520039' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Cantarului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Kecskemet', '520039', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520039' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Kecskemet');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Kiskunhalas', '520039', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520039' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Kiskunhalas');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Toroczkai Wigand Ede', '520039', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520039' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Toroczkai Wigand Ede');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Veszprem', '520039', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520039' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Veszprem');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Bunika', '520039', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520039' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Bunika');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Piata', 'Szechenyi Istvan', '520042', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520042' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Piata' AND COALESCE(street_name, '')='Szechenyi Istvan');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Grigorescu Nicolae', '520042', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520042' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Grigorescu Nicolae');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Bogdan Laszlo', '520043', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520043' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Bogdan Laszlo');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Farkas Arpad', '520043', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520043' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Farkas Arpad');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Dali Sandor', '520043', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520043' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Dali Sandor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Magyari Lajos', '520043', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520043' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Magyari Lajos');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Timaru Constantin', '520043', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520043' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Timaru Constantin');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Caisului', '520044', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520044' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Caisului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Ciresului', '520044', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520044' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ciresului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Fagului', '520044', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520044' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Fagului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Maciesului', '520044', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520044' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Maciesului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Marului', '520044', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520044' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Marului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Murelor', '520044', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520044' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Murelor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Nucului', '520044', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520044' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Nucului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Prunului', '520044', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520044' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Prunului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Rasaritului', '520044', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520044' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Rasaritului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Stajarului', '520044', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520044' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Stajarului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Visinului', '520044', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520044' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Visinului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Zmeurei', '520044', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520044' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Zmeurei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Parului', '520044', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520044' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Parului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Socului', '520044', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520044' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Socului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Agrisului', '520044', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520044' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Agrisului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Afinului', '520044', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520044' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Afinului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Bogats Denes', '520045', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520045' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Bogats Denes');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Stancii', '520045', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520045' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Stancii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Budai Iozsef', '520046', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520046' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Budai Iozsef');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Lemnarilor', '520047', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520047' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Lemnarilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Esafodului', '520050', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520050' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Esafodului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Neri Szent Fulop', '520050', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520050' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Neri Szent Fulop');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Puczi Bela', '520050', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520050' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Puczi Bela');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Groapa Lupului', '520053', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520053' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Groapa Lupului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Losy Schmidt Ede', '520053', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520053' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Losy Schmidt Ede');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Mikszath Kalman', '520053', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520053' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Mikszath Kalman');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Mileniului', '520053', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520053' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Mileniului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Szabedi Laszlo', '520053', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520053' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Szabedi Laszlo');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Visky Arpad', '520053', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520053' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Visky Arpad');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Andrad Samuel', '520054', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520054' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Andrad Samuel');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Caragiale Ion Luca', '520054', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520054' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Caragiale Ion Luca');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Cserey Janosne', '520054', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520054' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Cserey Janosne');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Dioszeghy Laszlo', '520054', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520054' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Dioszeghy Laszlo');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Panorama Lumii', '520054', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520054' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Panorama Lumii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Varga Nandor Lajos', '520054', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520054' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Varga Nandor Lajos');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Hollo Erno', '520056', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520056' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Hollo Erno');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Carmen Sylva', '520059', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520059' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Carmen Sylva');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Berde Mozes', '520060', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520060' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Berde Mozes');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Bartok Bela', '520061', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520061' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Bartok Bela');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Enescu George', '520065', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520065' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Enescu George');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Gall Lajos', '520065', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520065' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Gall Lajos');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Koreh Endre', '520065', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520065' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Koreh Endre');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Infratirii', '520068', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520068' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Infratirii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Csiki Laszlo', '520068', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520068' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Csiki Laszlo');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Csutak Vilmos', '520077', '', 'Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520077' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Csutak Vilmos');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Infundata', '520077', '', 'Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520077' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Infundata');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Kula Kert', '520077', '', 'Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520077' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Kula Kert');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Malik Jozsef', '520082', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520082' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Malik Jozsef');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Liboc', '520085', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520085' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Liboc');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Piata', 'Europa', '520089', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520089' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Piata' AND COALESCE(street_name, '')='Europa');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Epresteto', '520092', '', 'Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520092' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Epresteto');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Pap Lehel', '520092', '', 'Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520092' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Pap Lehel');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Armata Romana nr. 37-T; 50-T', '520092', '', 'Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520092' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Armata Romana nr. 37-T; 50-T');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Campul Frumos', '520092', '', 'Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520092' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Campul Frumos');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Sombori Salamon Sandor', '520092', '', 'Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520092' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Sombori Salamon Sandor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Boll Heinrich', '520092', '', 'Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520092' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Boll Heinrich');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Pateanu Gelu', '520092', '', 'Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520092' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Pateanu Gelu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Neumann Jozsef', '520092', '', 'Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520092' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Neumann Jozsef');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Reimesch Ferenc', '520092', '', 'Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520092' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Reimesch Ferenc');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Nagy Gergely', '520092', '', 'Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520092' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Nagy Gergely');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Rednik', '520092', '', 'Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520092' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Rednik');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Suto Berta', '520092', '', 'Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520092' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Suto Berta');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Kolcza Sandor', '520092', '', 'Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520092' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Kolcza Sandor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Sugas Bai', '520093', '', 'Sfantu Gheorghe 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520093' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Sugas Bai');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Calea Brasovului, DN 12', '520094', '', 'Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520094' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Calea Brasovului, DN 12');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Covasna', 'Sfantu Gheorghe', 'Strada', 'Calea Valcele, DJ 13E', '520095', '', 'Sfantu Gheorghe 1 - Ghiseu 1 Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='520095' AND state='Covasna' AND city='Sfantu Gheorghe' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Calea Valcele, DJ 13E');

-- === oras Bacau (Bacau) ===
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=2052 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=2378 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=2085 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=2379 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=2054 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=2169 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=2220 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=1806 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=2221 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=1825 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=1824 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=2100 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=1807 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=2223 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=2222 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=2114 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=2113 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=2101 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=2285 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=2103 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=1788 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=1983 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=2231 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=2238 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=2334 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=1828 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=2262 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=2261 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=1818 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=2303 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=1819 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=1810 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=2093 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=2286 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=1784 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=2219 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=1982 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=2217 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=2218 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=2263 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=2045 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=1861 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=2078 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=2363 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=2123 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=1808 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=1904 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=2084 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=1905 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=2086 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=2194 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=1909 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=1908 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=1963 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=2195 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=1858 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=1907 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=2055 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=2399 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=1790 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=1959 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2107 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2106 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=1956 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2108 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=1954 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2009 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=1913 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=1953 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=1958 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=1950 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2358 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=1951 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2071 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2203 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=1955 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2068 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2110 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2069 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=1911 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2011 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2214 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2213 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2212 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2387 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=1952 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=1944 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=1957 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=1946 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=1949 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=1948 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=1947 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=1943 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=1932 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=1942 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Cornisa Bistritei nr. 3', office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=1941 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=1916 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2232 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=1917 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=1918 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2028 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2105 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=1940 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2012 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2115 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2013 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2076 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2112 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2072 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2204 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2073 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2205 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2064 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2288 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2389 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2062 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2160 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2157 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2396 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2395 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2394 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2138 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2298 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2139 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Russo Alecu nr. 35, 45-47', office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2299 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2140 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2128 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2129 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2130 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2162 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2318 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2319 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2391 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=1990 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2132 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2131 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=1988 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2320 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2315 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2322 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2022 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2020 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2019 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2159 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2158 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2156 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=1816 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=1965 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=1814 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2252 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2133 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2316 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2134 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2092 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2197 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2293 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2306 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2381 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2171 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2135 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2136 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2137 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2127 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2297 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=1779 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2152 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2404 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2006 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2047 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2326 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2401 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2040 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2145 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2143 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=1996 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=1859 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=1882 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2376 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2382 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2150 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=1795 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=1855 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=1857 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=1854 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2225 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2234 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2362 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2380 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=1852 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=1853 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=1927 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2037 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2036 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2312 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2179 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=1856 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2039 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2260 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2185 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2184 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Primaverii bl. 7, 9, 10, 11', office='Bacau 8 Oficiu' WHERE id=2251 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=1895 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2025 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2324 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2044 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=1802 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2066 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2167 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2209 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=1827 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=1979 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2227 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2355 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2405 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=1797 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=1886 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=1921 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2026 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2327 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2330 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2385 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=1981 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2024 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2081 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2210 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=1922 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=1962 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=1978 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2397 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2398 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=1910 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=1964 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2030 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2031 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2046 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2228 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2352 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2027 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2142 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2328 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=1845 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=1997 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=1846 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2002 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2003 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2004 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2148 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2353 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=1885 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2087 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2088 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2089 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2090 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2015 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2200 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2201 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2016 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=1881 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2155 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=1842 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=1991 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=1841 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2029 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=1821 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2098 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2199 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2367 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=1901 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 Oficiu' WHERE id=2051 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=1998 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2257 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2001 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=1969 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=1999 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2224 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=1961 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=1971 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=1970 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=1850 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2154 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2147 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=1967 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2163 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=2192 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=1822 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 9 Oficiu' WHERE id=1973 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1872 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1987 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2253 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1985 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1986 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2254 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2276 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1871 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2255 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=1874 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2307 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1791 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1812 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1972 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2005 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1938 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1966 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Republicii nr. 40-44', office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2279 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2280 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1928 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1931 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2284 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2278 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1800 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1838 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1837 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2175 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2186 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1836 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2187 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1835 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1844 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2188 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1869 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2119 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2271 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1870 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2120 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1868 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1933 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1878 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1935 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2118 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1877 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1936 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2121 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2270 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1839 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1840 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2281 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1799 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1832 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2283 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1892 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2350 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1891 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2308 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1890 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1889 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2268 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2269 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1934 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2272 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1937 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2273 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2208 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2274 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1879 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2275 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1876 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2060 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2122 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2240 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Infratirii', office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2061 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2304 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1923 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1926 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2189 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2236 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2361 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=1829 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=1830 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=1903 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=1939 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=2010 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=2023 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=2067 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=2082 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=2083 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=2172 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=2173 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=2313 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=2406 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=1823 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=2094 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=2351 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=2164 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=2165 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=2336 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=2337 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=2369 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=1976 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=1977 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=2340 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=2244 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=2243 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=2245 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=1897 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=1896 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=2049 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=1813 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=2048 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=2095 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=2342 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=2384 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=2403 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=1796 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=2410 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=1794 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2291 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2041 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2292 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2042 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2096 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2237 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2287 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2289 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2309 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2377 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2097 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2258 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2311 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2314 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=1831 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2032 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2099 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2183 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2366 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2386 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2182 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2305 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2329 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=1865 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=1883 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=1920 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=1902 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2383 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2407 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=1866 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2202 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2267 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2348 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2034 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2079 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2400 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2393 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2091 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2370 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2233 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2371 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=1980 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2168 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2372 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=1798 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=1826 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=1884 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2065 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2256 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2364 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=1849 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=1900 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2310 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2343 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2402 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 8 Oficiu' WHERE id=2409 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=1867 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=2408 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=1919 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET office='Bacau 11 Oficiu' WHERE id=1820 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Florilor nr. 1-3; 2-6', office='Bacau 1 Oficiu' WHERE id=2007 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Ipatescu Ana nr. 5-11, 21-27; 2-4, 8, 12-48', office='Bacau 1 Oficiu' WHERE id=2053 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Florilor nr. 5-11; 8-38', office='Bacau 1 Oficiu' WHERE id=2008 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='1 Mai nr. 3-T; 4', office='Bacau 1 Oficiu' WHERE id=1778 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='1 Mai nr. 1; 2, 6-T', office='Bacau 1 Oficiu' WHERE id=1777 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Alecsandri Vasile nr. 9-35; 2, 6-22', office='Bacau 1 Oficiu' WHERE id=1804 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Alecsandri Vasile nr. 1-5, 53; 4, 24-56', office='Bacau 1 Oficiu' WHERE id=1803 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Alecsandri Vasile nr. 7, 37, 41-51, 55-59', office='Bacau 1 Oficiu' WHERE id=1805 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Marasesti nr. 3-9', office='Bacau 1 Oficiu' WHERE id=2102 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='9 Mai nr. 1; 2-24', office='Bacau 1 Oficiu' WHERE id=1781 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='9 Mai nr. 26-52', office='Bacau 1 Oficiu' WHERE id=1787 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='9 Mai nr. 15, 19; 54-62', office='Bacau 1 Oficiu' WHERE id=1783 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='9 Mai nr. 21-25; 64-104', office='Bacau 1 Oficiu' WHERE id=1785 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Soimului bl. 2A, 6A, 10B, 14B, 14C', office='Bacau 1 Oficiu' WHERE id=2331 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Soimului nr. 1-27', office='Bacau 1 Oficiu' WHERE id=2332 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Soimului nr. 2-30', office='Bacau 1 Oficiu' WHERE id=2333 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Razboieni nr. 2-12', office='Bacau 1 Oficiu' WHERE id=2266 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Razboieni bl. 26, 30', office='Bacau 1 Oficiu' WHERE id=2264 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Razboieni nr. 11-45; 14-48', office='Bacau 1 Oficiu' WHERE id=2265 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Parcului nr. 1-25; 2-4', office='Bacau 1 Oficiu' WHERE id=2215 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='9 Mai nr. 3-13', office='Bacau 1 Oficiu' WHERE id=1782 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Mihai Viteazul nr. 6-16', office='Bacau 1 Oficiu' WHERE id=2125 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Petru Rares nr. 1-9', office='Bacau 1 Oficiu' WHERE id=2229 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Petru Rares nr. 2-12', office='Bacau 1 Oficiu' WHERE id=2230 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Parcului nr. 27-33; 20, 24-28', office='Bacau 1 Oficiu' WHERE id=2216 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Titulescu Nicolae bl. 3', office='Bacau 1 Oficiu' WHERE id=2356 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Balcescu Nicolae nr. 1-3', office='Bacau 1 Oficiu' WHERE id=1860 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Balcescu Nicolae nr. 2-16', office='Bacau 1 Oficiu' WHERE id=1862 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Mihai Viteazul nr. 3-17', office='Bacau 1 Oficiu' WHERE id=2124 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Alexandru cel Bun nr. 7-13; 8-12', office='Bacau 1 Oficiu' WHERE id=1809 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Nufarului nr. 1-3; 2', office='Bacau 1 Oficiu' WHERE id=2193 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Caragiale Ion Luca nr. 1-13, 29; 2-20', office='Bacau 1 Oficiu' WHERE id=1906 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Nufarului nr. 11; 12-28', office='Bacau 1 Oficiu' WHERE id=2196 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='9 Mai nr. 27-35', office='Bacau 1 Oficiu' WHERE id=1786 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Marasesti nr. 173-179', office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2109 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Marasesti nr. 185-187; 100-110', office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2111 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Letea nr. 7; 6-14', office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2070 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Carpati nr. 5-13; 2', office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=1912 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Carpati nr. 17-25; 10-14', office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=1914 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Carpati nr. 27-29; 16-T', office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=1915 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Tolstoi Alexei nr. 1-3; 2-14', office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2359 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Violetelor nr. 3, 9A, 9B; 2-12', office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2388 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Cornisa Bistritei nr. 7A, 7B, 9; 8', office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=1945 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Marasesti nr. 151-157; 80-92, 96', office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2104 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Letea nr. 15-19', office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2074 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Orizontului nr. 13-85; 6-76', office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2206 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Miron Costin nr. 41-75, 79-83; 6-70', office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2161 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Lalelelor nr. 3, 7-9; 2, 6-10', office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2063 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Russo Alecu nr. 37-39; 24-46', office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2300 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Russo Alecu nr. 41-43, 57-59', office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2301 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Russo Alecu nr. 49-55; 48-86', office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2302 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Stadionului nr. 19-23', office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2321 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Viorelelor nr. 3-21', office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2390 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Eliade Mircea nr. 11-T; 10-T', office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=1989 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Viorelelor nr. 4-10', office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2392 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Stadionului nr. 1-9; 2-4', office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2317 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Ghioceilor nr. 25-29; 2-12', office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2021 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Aman Theodor, pictor nr. 9-T; 10-T', office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=1815 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Stadionului nr. 18-52', office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2323 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Milcov nr. 1-51; 18-106, 110', office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2126 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Russo Alecu nr. 1-13', office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2294 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Izvoare nr. 1-105; 2-100', office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2059 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Russo Alecu nr. 15; 2-22', office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2295 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Orizontului nr. 87; 78-80', office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2207 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Russo Alecu nr. 17-29', office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2296 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Mioritei nr. 12-24', office='Bacau 8 Oficiu' WHERE id=2151 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Mioritei nr. 32-36', office='Bacau 8 Oficiu' WHERE id=2153 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Mioritei nr. 19; 38-66', office='Bacau 8 Oficiu' WHERE id=2146 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Mioritei nr. 5-9', office='Bacau 8 Oficiu' WHERE id=2144 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Enea Nicu nr. 1-39; 2-42, 42A, 42B, 46-48', office='Bacau 8 Oficiu' WHERE id=1995 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Unirii nr. 1-35; 2-52', office='Bacau 8 Oficiu' WHERE id=2373 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='22 Decembrie nr. 1-3; 2-14', office='Bacau 8 Oficiu' WHERE id=1792 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Cocea Iosif nr. 1-3; 2-6, 22', office='Bacau 8 Oficiu' WHERE id=1929 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Primaverii nr. 1-21; 2-6', office='Bacau 8 Oficiu' WHERE id=2249 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='22 Decembrie nr. 5-17', office='Bacau 8 Oficiu' WHERE id=1793 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Cocea Iosif nr. 5-13; 8-20', office='Bacau 8 Oficiu' WHERE id=1930 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Banca Nationala nr. 1-23; 2-38', office='Bacau 8 Oficiu' WHERE id=1851 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Neagoe Voda nr. 1; 2-4', office='Bacau 8 Oficiu' WHERE id=2177 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Neagoe Voda nr. 3-17; 6-14', office='Bacau 8 Oficiu' WHERE id=2178 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Radu Negru nr. 1-9; 4', office='Bacau 8 Oficiu' WHERE id=2259 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Horia, martir nr. 17; 16-24', office='Bacau 8 Oficiu' WHERE id=2038 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Prieteniei nr. 1-67; 2-20', office='Bacau 8 Oficiu' WHERE id=2246 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Prieteniei nr. 69-91; 68', office='Bacau 8 Oficiu' WHERE id=2247 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Primaverii nr. 23-63; 8-36', office='Bacau 8 Oficiu' WHERE id=2250 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Buciumului nr. 1-49; 2-T', office='Bacau 8 Oficiu' WHERE id=1894 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Prelungirea Bradului nr. 1-111; 2-98', office='Bacau 8 Oficiu' WHERE id=2242 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Iasilor nr. 1-19; 2-22', office='Bacau 9 Oficiu' WHERE id=2043 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Alba Iulia nr. 1-27; 2-26', office='Bacau 9 Oficiu' WHERE id=1801 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Strat Procopie nr. 21-41; 20-34', office='Bacau 9 Oficiu' WHERE id=2325 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Militari nr. 1-35; 2-34', office='Bacau 9 Oficiu' WHERE id=2141 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Bacovia George nr. 65-T; 64-68', office='Bacau 9 Oficiu' WHERE id=1847 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Bacovia George nr. 70-T', office='Bacau 9 Oficiu' WHERE id=1848 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Nordului nr. 1-51; 2-16', office='Bacau 9 Oficiu' WHERE id=2190 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Depoului nr. 1', office='Bacau 9 Oficiu' WHERE id=1974 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Nordului nr. 53-107; 18-38', office='Bacau 9 Oficiu' WHERE id=2191 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Bucovinei nr. 2-6', office='Bacau 9 Oficiu' WHERE id=1899 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Bucovinei nr. 1-21; 8-14', office='Bacau 9 Oficiu' WHERE id=1898 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Tipografilor nr. 9-11; 8-12', office='Bacau 9 Oficiu' WHERE id=2354 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Garii nr. 1-15; 2-52, 62-68', office='Bacau 9 Oficiu' WHERE id=2014 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Garii nr. 70-76', office='Bacau 9 Oficiu' WHERE id=2017 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Eminescu Mihai bl. A1, A2, A3, A4', office='Bacau 9 Oficiu' WHERE id=1992 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Eminescu Mihai nr. 1-41; 2-28', office='Bacau 9 Oficiu' WHERE id=1993 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Avram Iancu bl. A1', office='Bacau 9 Oficiu' WHERE id=1843 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Mioritei nr. 33-39; 80-86', office='Bacau 9 Oficiu' WHERE id=2149 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Oituz nr. 1-9', office='Bacau 9 Oficiu' WHERE id=2198 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Titulescu Nicolae nr. 1-39; 2-34', office='Bacau 9 Oficiu' WHERE id=2357 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Ionita Sandu Sturza nr. 1-T; 28-T', office='Bacau 1 Oficiu' WHERE id=2050 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Energiei nr. 1-29; 2-30', office='Bacau 9 Oficiu' WHERE id=2000 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Cuza Voda nr. 1-33; 2-32', office='Bacau 9 Oficiu' WHERE id=1968 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Chimiei nr. 2-T', office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1925 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Electricienilor nr. 1-3; 2, 6-36', office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1984 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Bicaz nr. 23-25; 156-160, 164-T', office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1873 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Chimiei nr. 1-T', office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1924 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Bucegi nr. 1-49; 2-80', office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=1887 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Tolstoi Alexei nr. 5-69', office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2360 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Bucegi nr. 51-109', office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1888 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Alexandru Lapusneanu nr. 1-T; 2-64', office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1811 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Republicii nr. 29-37, 143-T; 198-T', office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2277 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Narciselor nr. 1-9; 8', office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2174 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Narciselor nr. 13-19C; 10-32', office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2176 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Aviatorilor bl. C1-C3', office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1833 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Aviatorilor nr. 2-6', office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1834 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Republicii nr. 56-68', office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2282 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Bucegi nr. 135-141; 82-140', office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1893 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Marasti nr. 55-83; 40-58', office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2117 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Marasti nr. 1-53; 2-38', office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2116 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Bicaz nr. 128-134', office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=1875 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Letea nr. 20-32', office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2077 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Letea nr. 21-25; 34-46, 50bis', office='Bacau 1 - Ghiseu 3 Ghiseu' WHERE id=2075 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Porumbescu Ciprian nr. 1-51C, 24-T', office='Bacau 1 - Ghiseuiseu 3' WHERE id=2239 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Digul Barnat nr. 1-9; 2-6', office='Bacau 11 Oficiu' WHERE id=1975 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Moldovei nr. 2-100', office='Bacau 11 Oficiu' WHERE id=2166 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Stefan cel Mare nr. 1-7; 2-8', office='Bacau 11 Oficiu' WHERE id=2335 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Stefan cel Mare nr. 17-23; 18-22', office='Bacau 11 Oficiu' WHERE id=2338 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Stefan cel Mare nr. 25-57; 24-32', office='Bacau 11 Oficiu' WHERE id=2339 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Stefan cel Mare nr. 42-66', office='Bacau 11 Oficiu' WHERE id=2341 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Prieteniei nr. 22-66, 70-96', office='Bacau 11 Oficiu' WHERE id=2248 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Romanului nr. 1-109; 2-76', office='Bacau 8 Oficiu' WHERE id=2290 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Barladului nr. 1-27; 2-110', office='Bacau 8 Oficiu' WHERE id=1863 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Barladului nr. 29-81; 112-160', office='Bacau 8 Oficiu' WHERE id=1864 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Triumfului nr. 1-7; 2-14', office='Bacau 8 Oficiu' WHERE id=2365 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Unirii nr. 58-102', office='Bacau 8 Oficiu' WHERE id=2375 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Holtului nr. 123-T; 86-122', office='Bacau 8 Oficiu' WHERE id=2035 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Licurici nr. 11-93; 12-66', office='Bacau 8 Oficiu' WHERE id=2080 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Unirii nr. 37-79; 54-56', office='Bacau 8 Oficiu' WHERE id=2374 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Holtului nr. 1-21; 124-T', office='Bacau 8 Oficiu' WHERE id=2033 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET name='600108', country_id=NULL, office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=2170 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET name='600254', country_id=NULL, office='Bacau 9 Oficiu' WHERE id=1994 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET name='600379', country_id=NULL, office='Bacau 8 Oficiu' WHERE id=2235 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Nechita Gheorghe, erou', office='Bacau 1 Oficiu' WHERE id=2180 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Trecatoarea 9 Mai', office='Bacau 1 Oficiu' WHERE id=1780 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Paun Pincio Ion', office='Bacau 1 Oficiu' WHERE id=2226 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Neculce Ion, cronicar', office='Bacau 1 Oficiu' WHERE id=2181 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Andreescu Ion, pictor', office='Bacau 1 - Ghiseu 1 Ghiseu' WHERE id=1817 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Logofat Tautu nr. 1; 2', office='Bacau 8 Oficiu' WHERE id=2344 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Logofat Tautu nr. 3', office='Bacau 8 Oficiu' WHERE id=2345 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Logofat Tautu nr. 5-9; 4-6', office='Bacau 8 Oficiu' WHERE id=2346 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Logofat Tautu nr. 11-13; 8-16', office='Bacau 8 Oficiu' WHERE id=2347 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Istrate Constantin, doctor nr. 1-17', office='Bacau 9 Oficiu' WHERE id=2057 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Istrate Constantin, doctor nr. 19-33; 2-10', office='Bacau 9 Oficiu' WHERE id=2058 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Ghelu Ion Destelnica', office='Bacau 9 Oficiu' WHERE id=2368 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Trecatoarea Gheraiesti', office='Bacau 11 Oficiu' WHERE id=2018 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Precup Victor, capitan', office='Bacau 8 Oficiu' WHERE id=2241 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Cornului', office='Bacau 8 Oficiu' WHERE id=1960 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Trecatoarea Islaz', office='Bacau 8 Oficiu' WHERE id=2056 AND state='Bacau' AND city='Bacau';
UPDATE res_zip SET street_name='Trecatoarea Tecuciului', office='Bacau 8 Oficiu' WHERE id=2349 AND state='Bacau' AND city='Bacau';
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Bacau', 'Bacau', 'Strada', 'Kogalniceanu Mihail', '600204', '', 'Bacau 8 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='600204' AND state='Bacau' AND city='Bacau' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Kogalniceanu Mihail');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Bacau', 'Bacau', 'Strada', 'Prutului', '600227', '', 'Bacau 9 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='600227' AND state='Bacau' AND city='Bacau' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Prutului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Bacau', 'Bacau', 'Strada', 'Timpului', '600234', '', 'Bacau 9 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='600234' AND state='Bacau' AND city='Bacau' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Timpului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Bacau', 'Bacau', 'Piata', 'Garii', '600254', '', 'Bacau 9 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='600254' AND state='Bacau' AND city='Bacau' AND COALESCE(street_type, '')='Piata' AND COALESCE(street_name, '')='Garii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Bacau', 'Bacau', 'Strada', 'Avram Iancu nr. 1-31; 2-30', '600260', '', 'Bacau 9 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='600260' AND state='Bacau' AND city='Bacau' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Avram Iancu nr. 1-31; 2-30');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Bacau', 'Bacau', 'Strada', 'Depoului nr. 3-T; 2-T', '600277', '', 'Bacau 9 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='600277' AND state='Bacau' AND city='Bacau' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Depoului nr. 3-T; 2-T');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Bacau', 'Bacau', 'Strada', 'Poligonului', '600293', '', 'Bacau 1 - Ghiseu 1 Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='600293' AND state='Bacau' AND city='Bacau' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Poligonului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Bacau', 'Bacau', 'Cale', 'Safran Alexandru', '600298', '', 'Bacau 1 - Ghiseu 3 Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='600298' AND state='Bacau' AND city='Bacau' AND COALESCE(street_type, '')='Cale' AND COALESCE(street_name, '')='Safran Alexandru');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Bacau', 'Bacau', 'Strada', 'Fagaras', '600332', '', 'Bacau 1 - Ghiseu 3 Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='600332' AND state='Bacau' AND city='Bacau' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Fagaras');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Bacau', 'Bacau', 'Cale', 'Marasesti nr. 300', '600342', '', 'Bacau 1 - Ghiseu 3 Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='600342' AND state='Bacau' AND city='Bacau' AND COALESCE(street_type, '')='Cale' AND COALESCE(street_name, '')='Marasesti nr. 300');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Bacau', 'Bacau', 'Alee', 'Chiries Corneliu, colonel', '600352', '', 'Bacau 1 - Ghiseu 4 Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='600352' AND state='Bacau' AND city='Bacau' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Chiries Corneliu, colonel');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Bacau', 'Bacau', 'Alee', 'Moldovitei', '600353', '', 'Bacau 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='600353' AND state='Bacau' AND city='Bacau' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Moldovitei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Bacau', 'Bacau', 'Strada', 'Bujorilor', '600354', '', 'Bacau 1 - Ghiseu 4 Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='600354' AND state='Bacau' AND city='Bacau' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Bujorilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Bacau', 'Bacau', 'Strada', 'Craitelor', '600354', '', 'Bacau 1 - Ghiseu 4 Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='600354' AND state='Bacau' AND city='Bacau' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Craitelor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Bacau', 'Bacau', 'Strada', 'Crizantemelor', '600354', '', 'Bacau 1 - Ghiseu 4 Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='600354' AND state='Bacau' AND city='Bacau' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Crizantemelor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Bacau', 'Bacau', 'Strada', 'Macilor', '600354', '', 'Bacau 1 - Ghiseu 4 Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='600354' AND state='Bacau' AND city='Bacau' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Macilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Bacau', 'Bacau', 'Strada', 'Magnoliilor', '600354', '', 'Bacau 1 - Ghiseu 4 Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='600354' AND state='Bacau' AND city='Bacau' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Magnoliilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Bacau', 'Bacau', 'Strada', 'Margaretelor', '600354', '', 'Bacau 1 - Ghiseu 4 Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='600354' AND state='Bacau' AND city='Bacau' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Margaretelor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Bacau', 'Bacau', 'Strada', 'Orhideelor', '600354', '', 'Bacau 1 - Ghiseu 4 Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='600354' AND state='Bacau' AND city='Bacau' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Orhideelor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Bacau', 'Bacau', 'Strada', 'Petuniilor', '600354', '', 'Bacau 1 - Ghiseu 4 Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='600354' AND state='Bacau' AND city='Bacau' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Petuniilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Bacau', 'Bacau', 'Strada', 'Sanzienelor', '600354', '', 'Bacau 1 - Ghiseu 4 Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='600354' AND state='Bacau' AND city='Bacau' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Sanzienelor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Bacau', 'Bacau', 'Strada', 'Zorelelor', '600354', '', 'Bacau 1 - Ghiseu 4 Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='600354' AND state='Bacau' AND city='Bacau' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Zorelelor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Bacau', 'Bacau', 'Strada', 'Merica Vasile, capitan', '600379', '', 'Bacau 8 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='600379' AND state='Bacau' AND city='Bacau' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Merica Vasile, capitan');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Bacau', 'Bacau', 'Strada', 'Sakellary Leon', '600379', '', 'Bacau 8 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='600379' AND state='Bacau' AND city='Bacau' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Sakellary Leon');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Bacau', 'Bacau', 'Strada', 'Tartescu Ernest, capitan', '600380', '', 'Bacau 8 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='600380' AND state='Bacau' AND city='Bacau' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Tartescu Ernest, capitan');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Bacau', 'Bacau', 'Strada', 'Draghici Nicolae, colonel', '600385', '', 'Bacau 8 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='600385' AND state='Bacau' AND city='Bacau' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Draghici Nicolae, colonel');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Bacau', 'Bacau', 'Strada', 'Grigorescu Eremia, general', '600385', '', 'Bacau 8 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='600385' AND state='Bacau' AND city='Bacau' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Grigorescu Eremia, general');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Bacau', 'Bacau', 'Strada', 'Uncescu Cezar', '600399', '', 'Bacau 8 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='600399' AND state='Bacau' AND city='Bacau' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Uncescu Cezar');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Bacau', 'Bacau', 'Alee', 'Zorilor', '600399', '', 'Bacau 8 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='600399' AND state='Bacau' AND city='Bacau' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Zorilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Bacau', 'Bacau', 'Strada', 'Sova Nicolae, general', '600401', '', 'Bacau 8 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='600401' AND state='Bacau' AND city='Bacau' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Sova Nicolae, general');

-- === oras Iasi (Iasi) ===
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=15554 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=15555 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=15556 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=15559 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=15746 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=15558 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=15557 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=14977 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=15114 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=15115 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=15316 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=15429 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=15482 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=15489 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=15650 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=14655 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=14656 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=15007 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=15196 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=15346 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=15347 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=15376 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=15514 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=15512 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=14872 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=14994 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=14996 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=15647 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15018 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15296 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15310 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15303 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15304 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15306 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15639 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15305 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15307 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15586 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15587 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15615 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15616 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15617 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14629 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14725 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15088 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15089 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15103 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15398 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15613 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14997 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15598 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15599 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15609 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15297 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14547 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14691 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14719 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14876 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14878 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14692 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14879 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14611 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14881 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14608 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14610 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14609 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15006 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14880 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14946 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15640 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15195 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15490 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14553 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14554 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14840 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14958 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15046 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15739 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15491 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15127 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14562 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14563 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15636 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15634 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14583 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15182 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15635 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14546 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15585 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Cantacuzino G. M., arh.', office='Iasi 1 Oficiu' WHERE id=14735 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15102 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15253 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15252 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14663 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14664 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15251 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15309 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14888 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15161 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15250 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14668 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15311 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15584 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14945 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15300 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15476 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15560 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15694 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15731 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14841 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15301 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14652 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14653 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14871 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15302 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14769 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14963 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15094 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15095 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15279 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15317 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15473 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15483 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15484 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15548 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15732 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=14873 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=14990 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=14991 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=14988 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=15513 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=14993 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=15202 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=15744 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=15745 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=14599 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=14992 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=15747 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1' WHERE id=14989 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15060 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15061 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15057 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15058 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15059 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14842 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15055 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15054 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15734 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14752 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14753 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15414 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15416 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15547 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15029 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15361 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14985 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15379 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Independentei nr. 1 Spital Universitar „Sf. Spiridon“', office='Iasi 1 Oficiu' WHERE id=15053 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14927 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14943 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14944 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15237 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15430 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15637 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14681 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15474 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14613 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14654 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15147 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15148 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15281 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15367 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15478 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14665 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14677 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14739 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14870 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15096 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15523 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15606 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14612 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14766 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14767 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14908 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15200 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14545 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14549 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14877 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14548 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15582 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14596 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=14597 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=15350 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14639 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14995 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15216 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15217 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15218 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15595 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=14954 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=15104 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=15427 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=14600 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=15748 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=14630 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=14601 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=14602 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=14604 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=14662 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=14603 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14875 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15037 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15254 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15315 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15413 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15443 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15444 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15735 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14560 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14919 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14920 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15397 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15428 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14561 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14828 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14912 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15155 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15176 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Ticaul de Jos', office='Iasi 1 Oficiu' WHERE id=15624 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15736 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15524 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15485 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15486 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15695 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14717 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15721 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14700 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14617 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14723 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15602 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15603 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Tutora nr. 2-4', office='Iasi 3 Oficiu' WHERE id=15631 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Tutora nr. 1-3', office='Iasi 3 Oficiu' WHERE id=15628 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Tutora nr. 7-9, 11B, 11C', office='Iasi 3 Oficiu' WHERE id=15629 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Tutora nr. 9A, 9B, 13-T', office='Iasi 3 Oficiu' WHERE id=15630 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15401 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15402 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14783 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15140 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15405 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15150 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14787 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14788 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14792 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14790 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15042 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14618 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14701 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14791 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15090 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15738 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15525 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15532 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14593 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15400 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Tutora nr. 6-T', office='Iasi 3 Oficiu' WHERE id=15632 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15530 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15085 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15531 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15084 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14930 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15655 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14642 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15039 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15131 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15184 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15204 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15528 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15657 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15449 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15447 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15450 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15078 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15448 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15451 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15452 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15073 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15076 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15077 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15083 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15656 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14915 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15258 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15257 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15139 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15654 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14559 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15082 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15653 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14897 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14898 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14899 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14900 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14914 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15222 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15223 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15233 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15234 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15235 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15236 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15232 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14901 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14916 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14904 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14905 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14906 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14907 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14902 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14917 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15071 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15072 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15069 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15248 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15441 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15070 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14887 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14903 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15068 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14789 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14702 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14699 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15730 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15533 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15132 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14893 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14894 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15086 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15087 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15340 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15341 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14697 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14678 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14679 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15368 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15369 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15371 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14706 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15697 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14698 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14707 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14708 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15359 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15360 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15529 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14780 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15149 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15713 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15041 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14781 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15151 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14782 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14758 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14759 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14923 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14976 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14986 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14987 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15621 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15691 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14874 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14890 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14891 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15064 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15141 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14592 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15180 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15459 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14688 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14761 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14949 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15154 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15156 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15454 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15683 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15685 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15686 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14948 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15455 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15707 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14619 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14657 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14658 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14910 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15165 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15421 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15436 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15682 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15658 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15521 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15597 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Tepes Voda', office='Iasi 4 Oficiu' WHERE id=15623 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15687 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15710 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15714 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14818 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14866 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15122 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15152 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15220 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15338 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15442 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15711 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14806 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14909 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15349 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14858 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15466 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14857 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15467 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14863 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14931 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15357 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14802 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14859 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14922 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15358 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15545 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14911 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15299 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15544 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15543 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14951 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15091 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15092 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14947 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14950 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14860 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15546 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14800 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14804 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14803 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15465 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14801 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14861 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14955 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14807 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15664 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15671 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15669 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15670 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14816 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15672 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15025 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14798 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15026 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15276 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15288 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15662 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15696 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15275 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15668 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15666 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15673 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14817 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15674 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14819 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15014 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15015 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15660 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14779 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15009 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15012 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15661 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14808 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14813 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14814 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14848 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14892 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14925 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14926 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14961 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14970 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15098 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15145 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15146 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15409 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15410 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15445 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15536 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15539 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15540 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15561 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15601 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14584 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14669 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14693 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14696 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14962 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14967 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15137 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15378 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15535 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15541 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15684 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15715 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14694 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15138 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15177 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15178 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15487 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15605 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15619 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15004 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15192 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15193 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15375 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15417 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15716 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15717 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15166 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15190 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15191 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15273 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15743 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14862 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14924 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15027 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15574 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15719 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15395 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15575 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15633 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15720 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14620 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14624 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14625 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15198 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15278 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14555 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14741 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14768 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15034 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15181 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15249 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15272 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15396 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15733 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15136 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15408 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15737 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15157 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15010 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15158 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15197 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15312 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15314 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15542 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14777 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15011 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15013 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15313 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15270 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15271 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15293 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15337 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15394 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15600 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14558 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14940 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14941 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14942 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15048 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15219 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15426 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15522 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14643 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14713 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14756 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14959 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15003 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15740 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15741 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15742 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14651 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15028 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15185 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15186 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15708 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15709 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15517 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15701 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15705 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15515 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15518 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15700 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14839 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15519 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14836 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14590 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15224 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15464 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15567 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15463 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14929 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14928 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15406 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15407 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14886 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14885 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14882 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14883 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14721 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14720 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15704 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14587 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15553 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14838 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11' WHERE id=15520 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15551 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15420 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15591 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15572 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14588 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15569 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15570 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14589 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15419 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15568 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15571 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=15475 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=15480 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15387 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15477 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15479 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15481 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15099 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15415 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15472 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15610 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15100 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=15298 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 1 Oficiu' WHERE id=14718 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14843 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=15093 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=15124 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=15123 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14844 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=15681 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=15125 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=15678 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14627 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=15680 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14628 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=15679 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14972 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=15693 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14851 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14913 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14936 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14852 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14952 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14971 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14621 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14623 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=15119 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=15344 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=15692 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14622 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=15118 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=15120 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14832 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=15277 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14830 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14831 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14614 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14829 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14834 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14745 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14550 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14615 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14675 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14835 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14999 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=15604 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=15608 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=15718 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14734 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14738 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14932 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14935 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=15000 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=15458 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=15646 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14695 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=15457 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=15706 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14591 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14833 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14847 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=15105 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=15594 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14680 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=15356 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14736 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14737 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14845 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=15339 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=15588 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=15590 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=15589 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=15047 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=15644 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=15645 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14747 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14746 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14744 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=15153 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14740 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14742 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=15043 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 6 Oficiu' WHERE id=14743 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15319 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15044 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=14724 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=14964 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=14805 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=14820 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=14965 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15537 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15538 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=14660 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15327 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 - Ghiseu 2 Ghiseu' WHERE id=15188 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15035 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15322 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15247 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15326 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15321 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15390 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15391 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15576 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=14727 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=14733 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15422 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=14728 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=14687 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=14729 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=14730 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15549 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15329 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15324 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15328 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15318 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=14796 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15332 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15201 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Podul Inalt', office='Iasi 13 Oficiu' WHERE id=15377 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15446 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15611 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15330 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15199 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15335 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15336 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15431 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15432 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15433 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15333 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15393 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=14765 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15280 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15331 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15435 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15488 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=14855 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15203 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15323 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=14854 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=14552 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=14853 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15045 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15066 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15128 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=14556 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=14670 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=14715 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=14722 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=14856 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=14969 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15194 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15283 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15386 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15392 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15579 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15580 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15596 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 13 Oficiu' WHERE id=15622 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14616 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15712 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=14564 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 4 Oficiu' WHERE id=15348 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15229 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14568 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14569 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15438 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14570 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15437 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14571 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15439 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15722 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14716 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15160 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14577 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15159 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15207 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15206 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15208 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15209 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15440 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14649 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15725 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15724 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15212 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15213 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15726 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15215 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15364 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15366 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15365 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15462 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14650 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15214 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14580 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15225 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15226 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15227 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14676 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15228 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14581 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15019 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14867 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14978 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15353 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15351 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15577 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15024 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15352 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15578 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15642 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14671 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14674 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14975 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15728 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14586 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14690 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14953 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14966 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14983 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14762 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14763 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14764 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14793 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14794 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15380 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15381 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15641 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15023 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14865 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14864 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14982 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14980 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14981 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14572 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14646 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14647 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15727 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14573 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14644 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14575 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14574 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14645 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14648 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14576 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15167 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15173 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15168 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15174 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15169 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15175 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15170 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14771 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14567 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15205 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15172 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15171 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14770 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14869 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15113 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15676 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=14868 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15112 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 11 Oficiu' WHERE id=15677 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14682 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15164 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15289 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14939 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15290 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14686 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15292 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15471 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14685 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14684 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15022 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15255 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15412 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15384 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15135 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14754 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14755 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15016 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15129 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15130 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15133 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15382 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15134 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14750 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15108 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15284 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14822 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14827 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15109 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15295 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14776 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14775 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14774 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15362 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15385 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15268 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15242 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15241 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15266 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15260 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15424 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15261 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15425 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Tutea Petre nr. 2-T', office='Iasi 3 Oficiu' WHERE id=15627 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14799 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15163 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14938 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14921 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15469 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15008 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15468 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15470 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15291 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14748 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15107 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14973 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15389 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15101 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15097 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14825 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14821 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15262 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15245 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15033 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15032 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15031 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15263 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15005 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15051 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15065 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15052 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15294 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15423 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15259 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14824 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14823 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15111 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14749 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14974 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14683 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Tutea Petre nr. 1-11', office='Iasi 3 Oficiu' WHERE id=15625 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Tutea Petre nr. 13-T', office='Iasi 3 Oficiu' WHERE id=15626 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14673 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=14957 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15179 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15239 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15246 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15286 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15345 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15563 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15564 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15265 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET office='Iasi 3 Oficiu' WHERE id=15240 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_type='Stradela', office='Iasi 3 Oficiu' WHERE id=15343 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_type='Alee', office='Iasi 3 Oficiu' WHERE id=15652 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Panu Anastasie nr. 2-24, 28-42', office='Iasi 1 Oficiu' WHERE id=15308 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Stefan cel Mare si Sfant nr. 3-9; 14-26', office='Iasi 1 Oficiu' WHERE id=15583 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Independentei nr. 7', office='Iasi 1 Oficiu' WHERE id=15056 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Primaverii nr. 4-72', office='Iasi 3 Oficiu' WHERE id=15404 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Chisinaului nr. 27, 31-33', office='Iasi 3 Oficiu' WHERE id=14786 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Iorga Nicolae nr. 45-47; 4, 6-8', office='Iasi 3 Oficiu' WHERE id=15074 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Iorga Nicolae nr. 4A, 4B, 10, 20-24', office='Iasi 3 Oficiu' WHERE id=15081 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Iorga Nicolae nr. 2, 2A (Bloc CFR)', office='Iasi 3 Oficiu' WHERE id=15079 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Iorga Nicolae nr. 1, 1A, 1B, 3-5; 2A (fara Bloc CFR)', office='Iasi 3 Oficiu' WHERE id=15067 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Primaverii nr. 2, 2A', office='Iasi 3 Oficiu' WHERE id=15403 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Chisinaului nr. 23A, 25, 25A', office='Iasi 3 Oficiu' WHERE id=14784 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Sturdza Mihai nr. 1, 5-T; 2-T', office='Iasi 3 Oficiu' WHERE id=15566 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Socola nr. 51-53, 57-T; 82-102, 106-132, 136-T', office='Iasi 3 Oficiu' WHERE id=15526 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Bucium nr. 84-90', office='Iasi 3 Oficiu' WHERE id=14710 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Bucium nr. 97-T', office='Iasi 3 Oficiu' WHERE id=14705 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Bucium nr. 1-53', office='Iasi 3 Oficiu' WHERE id=14703 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Trei Fantani nr. 1-3; 2-12', office='Iasi 3 Oficiu' WHERE id=15614 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Barnova', office='Iasi 3 Oficiu' WHERE id=14666 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Bucium nr. 56-72', office='Iasi 3 Oficiu' WHERE id=14709 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Chisinaului nr. 23, 23B, 29', office='Iasi 3 Oficiu' WHERE id=14785 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Vasile Lupu nr. 84-90, 90A, 94', office='Iasi 4 Oficiu' WHERE id=15663 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Vasile Lupu nr. 82, 96, 98A, 100, 100A, 102', office='Iasi 4 Oficiu' WHERE id=15667 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Ciurchi nr. 101, 101A-101E', office='Iasi 4 Oficiu' WHERE id=14809 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Ciurchi nr. 109; 126', office='Iasi 4 Oficiu' WHERE id=14810 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Ciurchi nr. 117, 117A, 117B, 117C', office='Iasi 4 Oficiu' WHERE id=14815 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Ciurchi nr. 88-130', office='Iasi 4 Oficiu' WHERE id=14812 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Chimiei nr. 35-55', office='Iasi 4 Oficiu' WHERE id=14778 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Columnei nr. 3-17', office='Iasi 11 Oficiu' WHERE id=14837 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Vitejilor nr. 2-T', office='Iasi 11 Oficiu' WHERE id=15699 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Vitejilor nr. 2-10', office='Iasi 11 Oficiu' WHERE id=15702 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Dacia nr. 59-T', office='Iasi 11 Oficiu' WHERE id=14884 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Stramosilor nr. 19-43', office='Iasi 11 Oficiu' WHERE id=15552 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Tabacului nr. 13-17', office='Iasi 11 Oficiu' WHERE id=15593 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Tabacului nr. 3-11', office='Iasi 11 Oficiu' WHERE id=15592 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Dumbrava Rosie nr. 1-7', office='Iasi 6 Oficiu' WHERE id=14933 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Dumbrava Rosie nr. 9; 46-T', office='Iasi 6 Oficiu' WHERE id=14934 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Podgoriilor nr. 15-T; 16-T', office='Iasi 6 Oficiu' WHERE id=15372 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Arbore Luca nr. 1-T; 12-T', office='Iasi 13 Oficiu' WHERE id=14595 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Canta nr. 6A, 8', office='Iasi 13 Oficiu' WHERE id=14732 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Canta nr. 2-6, 10-T', office='Iasi 13 Oficiu' WHERE id=14731 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Pacurari nr. 94-T', office='Iasi 13 Oficiu' WHERE id=15334 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Musatini nr. 3-7', office='Iasi 11 Oficiu' WHERE id=15210 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Voievozilor nr. 11; 10', office='Iasi 11 Oficiu' WHERE id=15723 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Musatini nr. 9-15, 21-23; 2-T', office='Iasi 11 Oficiu' WHERE id=15211 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Sarmisegetuza nr. 9', office='Iasi 11 Oficiu' WHERE id=15461 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Alexandru cel Bun nr. 62', office='Iasi 11 Oficiu' WHERE id=14582 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Halipa Pantelimon nr. 9 (bl H6), 11, 17-T; 14-T; bl. L1B', office='Iasi 11 Oficiu' WHERE id=15021 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Sarmisegetuza nr. 5', office='Iasi 11 Oficiu' WHERE id=15460 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Cerna nr. 8, 8A, 12-18A', office='Iasi 11 Oficiu' WHERE id=14773 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Cerna nr. 2-6A', office='Iasi 11 Oficiu' WHERE id=14772 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Halipa Pantelimon nr. 7-9', office='Iasi 3 Oficiu' WHERE id=15020 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Alexandrescu Emil', office='Iasi 3 Oficiu' WHERE id=14566 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Poitiers nr. 27-39', office='Iasi 3 Oficiu' WHERE id=15383 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Neculai Tudor nr. 93-125', office='Iasi 3 Oficiu' WHERE id=15243 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700009', country_id=NULL, office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=15388 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700087', country_id=NULL, office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=14598 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700273', country_id=NULL, office='Iasi 3 Oficiu' WHERE id=15370 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700284', country_id=NULL, street_name='Barnova', street_type='Stradela', office='Iasi 3 Oficiu' WHERE id=14667 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700297', country_id=NULL, street_type='Stradela', office='Iasi 3 Oficiu' WHERE id=14846 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700306', country_id=NULL, office='Iasi 4 Oficiu' WHERE id=15453 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700306', country_id=NULL, office='Iasi 4 Oficiu' WHERE id=15492 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700306', country_id=NULL, office='Iasi 4 Oficiu' WHERE id=15581 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700308', country_id=NULL, office='Iasi 4 Oficiu' WHERE id=15030 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700380', country_id=NULL, office='Iasi 4 Oficiu' WHERE id=15049 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700412', country_id=NULL, office='Iasi 11 Oficiu' WHERE id=15116 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700412', country_id=NULL, office='Iasi 11 Oficiu' WHERE id=15121 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700421', country_id=NULL, office='Iasi 11 Oficiu' WHERE id=15516 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700447', country_id=NULL, office='Iasi 11 Oficiu' WHERE id=15117 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700484', country_id=NULL, office='Iasi 6 Oficiu' WHERE id=14960 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700485', country_id=NULL, office='Iasi 6 Oficiu' WHERE id=14896 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700486', country_id=NULL, street_name='Podgoriilor nr. 1-13; 2-16', street_type='Strada', office='Iasi 6 Oficiu' WHERE id=15373 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700492', country_id=NULL, office='Iasi 6 Oficiu' WHERE id=15456 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700492', country_id=NULL, office='Iasi 6 Oficiu' WHERE id=15607 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700494', country_id=NULL, office='Iasi 6 Oficiu' WHERE id=15550 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700516', country_id=NULL, street_name='Arbore Luca nr. 2-10', office='Iasi 13 Oficiu' WHERE id=14594 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700516', country_id=NULL, office='Iasi 13 Oficiu' WHERE id=15256 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700516', country_id=NULL, office='Iasi 13 Oficiu' WHERE id=15418 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700542', country_id=NULL, office='Iasi 13 Oficiu' WHERE id=14726 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700542', country_id=NULL, office='Iasi 13 Oficiu' WHERE id=14751 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700542', country_id=NULL, office='Iasi 13 Oficiu' WHERE id=14760 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700542', country_id=NULL, office='Iasi 13 Oficiu' WHERE id=14557 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700542', country_id=NULL, office='Iasi 13 Oficiu' WHERE id=14638 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700542', country_id=NULL, office='Iasi 13 Oficiu' WHERE id=15238 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700542', country_id=NULL, office='Iasi 13 Oficiu' WHERE id=15287 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700576', country_id=NULL, office='Iasi 11 Oficiu' WHERE id=15285 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700600', country_id=NULL, office='Iasi 11 Oficiu' WHERE id=15363 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700611', country_id=NULL, office='Iasi 11 Oficiu' WHERE id=15643 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700617', country_id=NULL, office='Iasi 11 Oficiu' WHERE id=15144 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700627', country_id=NULL, office='Iasi 11 Oficiu' WHERE id=14626 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700627', country_id=NULL, office='Iasi 11 Oficiu' WHERE id=14968 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700627', country_id=NULL, office='Iasi 11 Oficiu' WHERE id=14984 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700627', country_id=NULL, office='Iasi 11 Oficiu' WHERE id=15434 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700628', country_id=NULL, office='Iasi 11 Oficiu' WHERE id=14979 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700635', country_id=NULL, office='Iasi 11 Oficiu' WHERE id=14661 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700654', country_id=NULL, office='Iasi 11 Oficiu' WHERE id=15638 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700662', country_id=NULL, office='Iasi 3 Oficiu' WHERE id=15411 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700673', country_id=NULL, office='Iasi 3 Oficiu' WHERE id=15040 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700681', country_id=NULL, office='Iasi 3 Oficiu' WHERE id=14826 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700681', country_id=NULL, office='Iasi 3 Oficiu' WHERE id=15110 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET name='700736', country_id=NULL, office='Iasi 3 Oficiu' WHERE id=14672 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Varianta Uzinei', office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=15651 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Sfantul Petru Movila nr. 5-T; 2-T', office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=15649 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Lozonschi Iordache nr. 15-T; 20-T', office='Iasi 1 Oficiu' WHERE id=15689 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Sfantul Lazar nr. 1-3; 2-16', office='Iasi 1 Oficiu' WHERE id=15503 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Sfantul Lazar nr. 5-29; 18-30', office='Iasi 1 Oficiu' WHERE id=15504 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Sfantul Lazar nr. 31-T; 32-T', office='Iasi 1 Oficiu' WHERE id=15505 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Lozonschi Iordache nr. 2-4', office='Iasi 1 Oficiu' WHERE id=15690 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Lozonschi Iordache nr. 1-13; 6-18', office='Iasi 1 Oficiu' WHERE id=15688 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Baciu Ion, maestrul', office='Iasi 1 Oficiu' WHERE id=14659 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Sfantul Sava', office='Iasi 1 Oficiu' WHERE id=15506 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Sfantul Petru Movila nr. 1-3', office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=15648 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Negruzzi Costache', office='Iasi 1 - Ghiseu 1 Ghiseu' WHERE id=15036 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Sfantul Stefan', office='Iasi 1 Oficiu' WHERE id=15507 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Imasului', office='Iasi 3 Oficiu' WHERE id=15050 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Regele Mihai I al Romaniei  nr. 2-8, 8A', street_type='Bulevard', office='Iasi 3 Oficiu' WHERE id=14631 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Regele Mihai I al Romaniei nr. 10-16', street_type='Bulevard', office='Iasi 3 Oficiu' WHERE id=14632 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Regele Mihai I al Romaniei  nr. 18-22', street_type='Bulevard', office='Iasi 3 Oficiu' WHERE id=14633 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Regele Mihai I al Romaniei nr. 24-30', street_type='Bulevard', office='Iasi 3 Oficiu' WHERE id=14634 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Regele Mihai I al Romaniei nr. 32-T', street_type='Bulevard', office='Iasi 3 Oficiu' WHERE id=14635 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Gheorghiu Miluta, actor', office='Iasi 4 Oficiu' WHERE id=15620 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Trecatoarea Oitelor', office='Iasi 4 Oficiu' WHERE id=15282 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Trecatoarea Fantanilor', office='Iasi 4 Oficiu' WHERE id=14956 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Trecatoarea Ciobanului', office='Iasi 4 Oficiu' WHERE id=14797 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Sfantul Ioan', office='Iasi 4 Oficiu' WHERE id=15502 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Platou Abator', office='Iasi 4 Oficiu' WHERE id=14551 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Cazaban', office='Iasi 11 Oficiu' WHERE id=15063 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Vieru Grigore', office='Iasi 1 Oficiu' WHERE id=15573 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Trecatoarea Podgoriilor', office='Iasi 6 Oficiu' WHERE id=14850 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Ioan Grigore, serg. nr. 1-5; 2-8', office='Iasi 13 Oficiu' WHERE id=15062 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Sabo Iosef, dr.', office='Iasi 11 Oficiu' WHERE id=14895 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Diminetii nr. 1-T', office='Iasi 3 Oficiu' WHERE id=14565 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Magurii nr. 1-T', office='Iasi 3 Oficiu' WHERE id=15142 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Magurii nr. 2-T', office='Iasi 3 Oficiu' WHERE id=15143 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Greierul', office='Iasi 3 Oficiu' WHERE id=15017 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Sfantul Constantin', office='Iasi 1 Oficiu' WHERE id=15498 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Sfantul Constantin', office='Iasi 1 Oficiu' WHERE id=15499 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Sfantul Gheorghe', office='Iasi 3 Oficiu' WHERE id=15500 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Sfantul Gheorghe', office='Iasi 3 Oficiu' WHERE id=15501 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Trecatoarea Trei Ierarhi', office='Iasi 1 Oficiu' WHERE id=15618 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Trecatoarea Davidel', office='Iasi 1 Oficiu' WHERE id=14889 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Trecatoarea Mincu Ion, arh.', office='Iasi 1 Oficiu' WHERE id=15162 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Trecatoarea Leului', office='Iasi 1 Oficiu' WHERE id=15106 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Trecatoarea Hotin', office='Iasi 1 Oficiu' WHERE id=15038 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Trecatoarea Nucului', office='Iasi 1 Oficiu' WHERE id=15274 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Trecatoarea Bravilor', office='Iasi 1 Oficiu' WHERE id=14689 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Trecatoarea Duzilor', office='Iasi 1 Oficiu' WHERE id=14937 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Trecatoarea Alpilor', office='Iasi 1 Oficiu' WHERE id=14585 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Trecatoarea Transeului', office='Iasi 1 Oficiu' WHERE id=15612 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Trecatoarea Pricop', office='Iasi 4 Oficiu' WHERE id=15399 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Trecatoarea Doamnei', office='Iasi 4 Oficiu' WHERE id=14918 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Trecatoarea Bucsinescu', office='Iasi 4 Oficiu' WHERE id=14714 AND state='Iasi' AND city='Iasi';
UPDATE res_zip SET street_name='Trecatoarea Cazimir Otilia', office='Iasi 4 Oficiu' WHERE id=14757 AND state='Iasi' AND city='Iasi';
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Fundac', 'Rascanu Teodor', '700010', '', 'Iasi 1 - Ghiseu 1 Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700010' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Fundac' AND COALESCE(street_name, '')='Rascanu Teodor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Panu Anastasie nr. 26', '700025', '', 'Iasi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700025' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Panu Anastasie nr. 26');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Sfantul Andrei', '700028', '', 'Iasi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700028' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Sfantul Andrei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', '', 'Trecatoarea Bacalu Iancu', '700029', '', 'Iasi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700029' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='' AND COALESCE(street_name, '')='Trecatoarea Bacalu Iancu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Bulevard', 'Regele Ferdinand I al Romaniei nr. 1-25', '700029', '', 'Iasi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700029' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Bulevard' AND COALESCE(street_name, '')='Regele Ferdinand I al Romaniei nr. 1-25');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Bulevard', 'Regele Ferdinand I al Romaniei nr. 27-T', '700031', '', 'Iasi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700031' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Bulevard' AND COALESCE(street_name, '')='Regele Ferdinand I al Romaniei nr. 27-T');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Fundac', 'Sfantul Andrei', '700032', '', 'Iasi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700032' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Fundac' AND COALESCE(street_name, '')='Sfantul Andrei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Stradela', 'Sfantul Andrei', '700032', '', 'Iasi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700032' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Stradela' AND COALESCE(street_name, '')='Sfantul Andrei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', '9 Mai 1877', '700046', '', 'Iasi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700046' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='9 Mai 1877');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Palade George Emil', '700047', '', 'Iasi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700047' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Palade George Emil');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Melodiei', '700047', '', 'Iasi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700047' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Melodiei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Palas 1-T; 2-T', '700051', '', 'Iasi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700051' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Palas 1-T; 2-T');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Bulevard', 'Stefan cel Mare si Sfant nr. 11-67', '700067', '', 'Iasi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700067' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Bulevard' AND COALESCE(street_name, '')='Stefan cel Mare si Sfant nr. 11-67');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', '', 'Esplanada Negri Costache 1-T; 2-T', '700072', '', 'Iasi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700072' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='' AND COALESCE(street_name, '')='Esplanada Negri Costache 1-T; 2-T');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Sinagogelor', '700082', '', 'Iasi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700082' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Sinagogelor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Piata', 'Elevilor Martiri ai Progromului din iunie 1941', '700094', '', 'Iasi 1 - Ghiseu 1', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700094' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Piata' AND COALESCE(street_name, '')='Elevilor Martiri ai Progromului din iunie 1941');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Piata', 'Drepti intre Popoare', '700094', '', 'Iasi 1 - Ghiseu 1', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700094' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Piata' AND COALESCE(street_name, '')='Drepti intre Popoare');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Cihac Iacob, dr', '700115', '', 'Iasi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700115' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Cihac Iacob, dr');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Sfantul Atanasie', '700115', '', 'Iasi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700115' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Sfantul Atanasie');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Stradela', 'Sfantul Atanasie', '700115', '', 'Iasi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700115' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Stradela' AND COALESCE(street_name, '')='Sfantul Atanasie');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Sfantul Teodor', '700115', '', 'Iasi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700115' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Sfantul Teodor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Fundac', 'Balcescu Nicolae', '700117', '', 'Iasi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700117' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Fundac' AND COALESCE(street_name, '')='Balcescu Nicolae');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', '', 'Trecatoarea Corbului', '700117', '', 'Iasi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700117' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='' AND COALESCE(street_name, '')='Trecatoarea Corbului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Fundac', 'Sfantul Teodor', '700117', '', 'Iasi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700117' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Fundac' AND COALESCE(street_name, '')='Sfantul Teodor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Bulevard', 'Primaverii nr. 74-T', '700174', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700174' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Bulevard' AND COALESCE(street_name, '')='Primaverii nr. 74-T');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Bulevard', 'Socola nr. 16 (grup firme)', '700269', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700269' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Bulevard' AND COALESCE(street_name, '')='Socola nr. 16 (grup firme)');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Fundac', 'Dealul Bucium', '700272', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700272' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Fundac' AND COALESCE(street_name, '')='Dealul Bucium');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Iasomiei', '700272', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700272' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Iasomiei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Ispir Mircea', '700272', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700272' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ispir Mircea');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Nuferilor', '700272', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700272' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Nuferilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Fundac', 'Lesnea George', '700273', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700273' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Fundac' AND COALESCE(street_name, '')='Lesnea George');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Lesnea George', '700273', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700273' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Lesnea George');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Narciselor', '700273', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700273' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Narciselor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', '', 'Trecatoarea Paun', '700274', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700274' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='' AND COALESCE(street_name, '')='Trecatoarea Paun');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Carabus', '700275', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700275' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Carabus');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Stradela', 'Carabus', '700275', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700275' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Stradela' AND COALESCE(street_name, '')='Carabus');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Furnica', '700275', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700275' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Furnica');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Libelula', '700275', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700275' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Libelula');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Stradela', 'Libelula', '700275', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700275' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Stradela' AND COALESCE(street_name, '')='Libelula');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Alee', 'Antonescu Teohari', '700276', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700276' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Antonescu Teohari');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Fundac', 'Antonescu Teohari', '700276', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700276' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Fundac' AND COALESCE(street_name, '')='Antonescu Teohari');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Antonescu Teohari', '700276', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700276' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Antonescu Teohari');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Barbulescu Ilie', '700276', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700276' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Barbulescu Ilie');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Celebidache Sergiu', '700276', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700276' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Celebidache Sergiu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Haret Spiru', '700276', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700276' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Haret Spiru');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Lipatti Dinu', '700276', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700276' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Lipatti Dinu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Porumbescu Ciprian', '700276', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700276' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Porumbescu Ciprian');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Sava Iosif', '700276', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700276' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Sava Iosif');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Simenschy Theofil', '700276', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700276' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Simenschy Theofil');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Zirra Alexandru', '700276', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700276' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Zirra Alexandru');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Sosea', 'Bucium nr. 92-T', '700277', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700277' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Sosea' AND COALESCE(street_name, '')='Bucium nr. 92-T');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Sosea', 'Bucium nr. 75-95', '700278', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700278' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Sosea' AND COALESCE(street_name, '')='Bucium nr. 75-95');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Alee', 'Domenii', '700278', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700278' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Domenii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Sturdza Mihai nr. 3', '700280', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700280' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Sturdza Mihai nr. 3');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Chavez Geo', '700282', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700282' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Chavez Geo');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Alee', 'Fermei', '700282', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700282' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Fermei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Fermei', '700282', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700282' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Fermei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Tonitza N. Nicolae', '700282', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700282' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Tonitza N. Nicolae');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Fundac', 'Socola', '700283', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700283' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Fundac' AND COALESCE(street_name, '')='Socola');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', '', 'Trecatoarea Visan', '700284', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700284' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='' AND COALESCE(street_name, '')='Trecatoarea Visan');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Fundac', 'Tudoranu Gheorghe 1-T; 2-T', '700284', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700284' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Fundac' AND COALESCE(street_name, '')='Tudoranu Gheorghe 1-T; 2-T');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Trei Fantani nr. 5-T; 14-T', '700286', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700286' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Trei Fantani nr. 5-T; 14-T');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Sosea', 'Bucium nr. 55-73', '700287', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700287' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Sosea' AND COALESCE(street_name, '')='Bucium nr. 55-73');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Agricola Cardas, prof.', '700295', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700295' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Agricola Cardas, prof.');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Constantin Pop', '700295', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700295' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Constantin Pop');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Constantineanu I.C.', '700295', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700295' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Constantineanu I.C.');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Jitaru Petre', '700295', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700295' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Jitaru Petre');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Vasiliu Haralambie, prof.', '700295', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700295' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Vasiliu Haralambie, prof.');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Stradela', 'Carutasi', '700296', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700296' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Stradela' AND COALESCE(street_name, '')='Carutasi');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Livezi', '700296', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700296' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Livezi');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Stradela', 'Livezi', '700296', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700296' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Stradela' AND COALESCE(street_name, '')='Livezi');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Stradela', 'Raiului', '700296', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700296' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Stradela' AND COALESCE(street_name, '')='Raiului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Bedreag C. G.', '700297', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700297' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Bedreag C. G.');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Stradela', 'Fluierasi', '700297', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700297' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Stradela' AND COALESCE(street_name, '')='Fluierasi');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Mioarelor', '700297', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700297' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Mioarelor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Plugari', '700297', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700297' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Plugari');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Stradela', 'Plugari', '700297', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700297' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Stradela' AND COALESCE(street_name, '')='Plugari');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Teascului', '700297', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700297' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Teascului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Verde', '700297', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700297' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Verde');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Stradela', 'Verde', '700297', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700297' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Stradela' AND COALESCE(street_name, '')='Verde');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Campineanu Ion', '700298', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700298' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Campineanu Ion');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Alee', 'Castanilor', '700298', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700298' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Castanilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Cernat Alexandru', '700298', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700298' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Cernat Alexandru');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Ionescu Nae', '700298', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700298' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ionescu Nae');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Alee', 'Mestecenilor', '700298', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700298' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Mestecenilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Alee', 'Pinilor', '700298', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700298' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Pinilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Alee', 'Salcamilor', '700298', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700298' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Salcamilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Statescu Eugen', '700298', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700298' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Statescu Eugen');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Alee', 'Teilor', '700298', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700298' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Teilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Vancea Petre', '700298', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700298' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Vancea Petre');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Vernescu Gheorghe', '700298', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700298' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Vernescu Gheorghe');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Bulevard', 'Chimiei nr. 10', '700299', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700299' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Bulevard' AND COALESCE(street_name, '')='Chimiei nr. 10');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Barbu Lautaru', '700308', '', 'Iasi 4 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700308' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Barbu Lautaru');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Stradela', 'Barbu Lautaru', '700308', '', 'Iasi 4 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700308' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Stradela' AND COALESCE(street_name, '')='Barbu Lautaru');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Ciurchi nr. 117D-117F', '700346', '', 'Iasi 4 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700346' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ciurchi nr. 117D-117F');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Ciurchi nr. 121A', '700347', '', 'Iasi 4 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700347' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ciurchi nr. 121A');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', '', 'Esplanada Oancea 1-T; 2-T', '700350', '', 'Iasi 4 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700350' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='' AND COALESCE(street_name, '')='Esplanada Oancea 1-T; 2-T');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Fundac', 'Oancea', '700351', '', 'Iasi 4 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700351' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Fundac' AND COALESCE(street_name, '')='Oancea');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Vasile Lupu nr. 83-93', '700357', '', 'Iasi 4 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700357' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Vasile Lupu nr. 83-93');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Vasile Lupu nr. 94A, 96B, 100B, 102A', '700357', '', 'Iasi 4 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700357' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Vasile Lupu nr. 94A, 96B, 100B, 102A');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Ciurchi nr. 105A, 105B, 107', '700370', '', 'Iasi 4 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700370' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ciurchi nr. 105A, 105B, 107');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Braescu Smaranda', '700384', '', 'Iasi 4 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700384' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Braescu Smaranda');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Columnei nr. 1', '700413', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700413' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Columnei nr. 1');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Vitejilor nr. 1-5, 11-13', '700414', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700414' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Vitejilor nr. 1-5, 11-13');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Alee', 'Vitejilor nr. 1-9', '700420', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700420' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Vitejilor nr. 1-9');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Vitejilor nr. 7-9', '700422', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700422' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Vitejilor nr. 7-9');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Bulevard', 'Dacia nr. 38-T', '700428', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700428' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Bulevard' AND COALESCE(street_name, '')='Dacia nr. 38-T');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Piata', 'Sfantul Anton de Padova', '700430', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700430' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Piata' AND COALESCE(street_name, '')='Sfantul Anton de Padova');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Stramosilor nr. 9-17', '700436', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700436' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Stramosilor nr. 9-17');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Ion Grigore, serg. nr. 7-T; 10-T', '700439', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700439' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ion Grigore, serg. nr. 7-T; 10-T');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Tabacului nr. 19-51, 57-59; 28-T', '700445', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700445' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Tabacului nr. 19-51, 57-59; 28-T');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Tabacului nr. 53-55, 61-T', '700446', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700446' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Tabacului nr. 53-55, 61-T');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Fundac', 'Pallady Theodor', '700454', '', 'Iasi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700454' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Fundac' AND COALESCE(street_name, '')='Pallady Theodor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Tautu, logofat 1-T; 2-T', '700457', '', 'Iasi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700457' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Tautu, logofat 1-T; 2-T');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Cosbuc George nr. 1-29', '700468', '', 'Iasi 6 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700468' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Cosbuc George nr. 1-29');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Alee', 'Ghica Grigore Voda nr. 1-39', '700475', '', 'Iasi 6 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700475' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Ghica Grigore Voda nr. 1-39');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Cosbuc George nr. 31-T', '700476', '', 'Iasi 6 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700476' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Cosbuc George nr. 31-T');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Alee', 'Baltagului', '700489', '', 'Iasi 6 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700489' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Baltagului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Baltagului', '700489', '', 'Iasi 6 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700489' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Baltagului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Fundac', 'Sadoveanu Mihail', '700489', '', 'Iasi 6 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700489' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Fundac' AND COALESCE(street_name, '')='Sadoveanu Mihail');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Fundac', 'Viticultori', '700490', '', 'Iasi 6 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700490' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Fundac' AND COALESCE(street_name, '')='Viticultori');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', '', 'Trecatoarea Viticultori', '700490', '', 'Iasi 6 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700490' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='' AND COALESCE(street_name, '')='Trecatoarea Viticultori');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Alee', 'Ghica Grigore Voda nr. 8-T', '700493', '', 'Iasi 6 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700493' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Ghica Grigore Voda nr. 8-T');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Bacovia George', '700500', '', 'Iasi 6 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700500' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Bacovia George');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Blaga Lucian', '700500', '', 'Iasi 6 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700500' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Blaga Lucian');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Budai-Deleanu Ion', '700500', '', 'Iasi 6 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700500' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Budai-Deleanu Ion');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Calinescu George', '700500', '', 'Iasi 6 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700500' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Calinescu George');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Ciolan Antonin, prof', '700500', '', 'Iasi 6 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700500' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ciolan Antonin, prof');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Goga Octavian', '700500', '', 'Iasi 6 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700500' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Goga Octavian');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Labis Nicolae', '700500', '', 'Iasi 6 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700500' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Labis Nicolae');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Macedonschi  Alexandru', '700500', '', 'Iasi 6 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700500' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Macedonschi  Alexandru');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Minulescu Ion', '700500', '', 'Iasi 6 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700500' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Minulescu Ion');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Popinceanu Nicolai, prof.', '700500', '', 'Iasi 6 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700500' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Popinceanu Nicolai, prof.');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Slavici Ioan', '700500', '', 'Iasi 6 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700500' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Slavici Ioan');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Vianu Tudor', '700500', '', 'Iasi 6 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700500' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Vianu Tudor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Alee', 'Ghica Grigore Voda nr. 2-6', '700502', '', 'Iasi 6 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700502' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Ghica Grigore Voda nr. 2-6');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Cristescu Maria', '700508', '', 'Iasi 6 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700508' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Cristescu Maria');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Alee', 'Pancu-Iasi Octav', '700508', '', 'Iasi 6 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700508' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Pancu-Iasi Octav');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Fundac', 'Pancu-Iasi Octav', '700508', '', 'Iasi 6 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700508' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Fundac' AND COALESCE(street_name, '')='Pancu-Iasi Octav');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Pancu-Iasi Octav', '700508', '', 'Iasi 6 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700508' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Pancu-Iasi Octav');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Alee', 'Raianu Octavian', '700508', '', 'Iasi 6 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700508' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Raianu Octavian');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Raianu Octavian', '700508', '', 'Iasi 6 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700508' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Raianu Octavian');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Popescu Stefan', '700509', '', 'Iasi 6 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700509' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Popescu Stefan');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Stradela', 'Popescu Stefan', '700509', '', 'Iasi 6 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700509' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Stradela' AND COALESCE(street_name, '')='Popescu Stefan');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Sosea', 'Moara de Foc nr. 2-T', '700517', '', 'Iasi 13 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700517' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Sosea' AND COALESCE(street_name, '')='Moara de Foc nr. 2-T');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Pacurari nr. 52-112', '700524', '', 'Iasi 13 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700524' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Pacurari nr. 52-112');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Pacurari nr. 45-109', '700525', '', 'Iasi 13 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700525' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Pacurari nr. 45-109');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Oblu Nicolae 1-T; 2-T', '700534', '', 'Iasi 13 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700534' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Oblu Nicolae 1-T; 2-T');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Hurmuzachi Eudoxiu', '700540', '', 'Iasi 13 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700540' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Hurmuzachi Eudoxiu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Iancu Flondor', '700540', '', 'Iasi 13 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700540' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Iancu Flondor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Nistor Ion', '700540', '', 'Iasi 13 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700540' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Nistor Ion');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Alee', 'Rizea Elisabeta', '700541', '', 'Iasi 13 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700541' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Rizea Elisabeta');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Rizea Elisabeta', '700541', '', 'Iasi 13 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700541' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Rizea Elisabeta');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Fundac', 'Bucovinei', '700542', '', 'Iasi 13 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700542' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Fundac' AND COALESCE(street_name, '')='Bucovinei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Bucovinei', '700542', '', 'Iasi 13 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700542' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Bucovinei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', '', 'Varianta Soseaua Rediu', '700546', '', 'Iasi 13 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700546' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='' AND COALESCE(street_name, '')='Varianta Soseaua Rediu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Crizantemelor', '700548', '', 'Iasi 13 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700548' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Crizantemelor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Alee', 'Culianu Ioan Petru, prof.', '700548', '', 'Iasi 13 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700548' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Culianu Ioan Petru, prof.');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Culianu Ioan Petru, prof.', '700548', '', 'Iasi 13 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700548' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Culianu Ioan Petru, prof.');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Ianov Ioan', '700548', '', 'Iasi 13 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700548' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ianov Ioan');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Sosea', 'Pacurari nr. 6-18', '700549', '', 'Iasi 13 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700549' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Sosea' AND COALESCE(street_name, '')='Pacurari nr. 6-18');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Sosea', 'Moara de Foc nr. 1', '700556', '', 'Iasi 13 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700556' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Sosea' AND COALESCE(street_name, '')='Moara de Foc nr. 1');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Pasaj', 'Alexandru cel Bun 1-T; 2-T', '700569', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700569' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Pasaj' AND COALESCE(street_name, '')='Alexandru cel Bun 1-T; 2-T');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Bulevard', 'Alexandru cel Bun nr. 22-42', '700570', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700570' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Bulevard' AND COALESCE(street_name, '')='Alexandru cel Bun nr. 22-42');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Arges nr. 14-T', '700570', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700570' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Arges nr. 14-T');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Arges nr. 9-T', '700576', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700576' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Arges nr. 9-T');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Arges nr. 1-7; 2-12', '700584', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700584' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Arges nr. 1-7; 2-12');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Jijia', '700584', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700584' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Jijia');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Sosea', 'Nationala nr. 80-88', '700584', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700584' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Sosea' AND COALESCE(street_name, '')='Nationala nr. 80-88');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Bulevard', 'Alexandru cel Bun nr. 12-20', '700585', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700585' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Bulevard' AND COALESCE(street_name, '')='Alexandru cel Bun nr. 12-20');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Sosea', 'Nationala nr. 90-94', '700585', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700585' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Sosea' AND COALESCE(street_name, '')='Nationala nr. 90-94');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Piata', 'Voievozilor nr. 7-9; 8', '700592', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700592' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Piata' AND COALESCE(street_name, '')='Voievozilor nr. 7-9; 8');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Bulevard', 'Alexandru cel Bun nr. 50-60', '700609', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700609' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Bulevard' AND COALESCE(street_name, '')='Alexandru cel Bun nr. 50-60');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Barbat Alexandru', '700618', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700618' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Barbat Alexandru');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Pastia D. Ioan', '700618', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700618' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Pastia D. Ioan');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Ungureanu Ernest, prof. dr. doc.', '700618', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700618' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ungureanu Ernest, prof. dr. doc.');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Donici Alecu', '700619', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700619' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Donici Alecu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Romanescu Ioanid', '700619', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700619' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Romanescu Ioanid');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Zotta Sever', '700619', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700619' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Zotta Sever');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Petru Schiopu nr. 8', '700628', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700628' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Petru Schiopu nr. 8');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Petru Schiopu nr. 10-T', '700629', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700629' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Petru Schiopu nr. 10-T');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Sosea', 'Nationala nr. 1-19; 38', '700635', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700635' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Sosea' AND COALESCE(street_name, '')='Nationala nr. 1-19; 38');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Sarmisegetuza nr. 1-3', '700635', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700635' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Sarmisegetuza nr. 1-3');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Sarmisegetuza nr. 7', '700636', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700636' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Sarmisegetuza nr. 7');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Cerna nr. 10, 10A', '700651', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700651' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Cerna nr. 10, 10A');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Fundac', 'Ciubotarasu Stefan', '700652', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700652' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Fundac' AND COALESCE(street_name, '')='Ciubotarasu Stefan');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Ciubotarasu Stefan', '700652', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700652' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ciubotarasu Stefan');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Filotti Maria', '700652', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700652' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Filotti Maria');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Gane Constantin', '700652', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700652' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Gane Constantin');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Fundac', 'Ghibu Onisifor', '700652', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700652' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Fundac' AND COALESCE(street_name, '')='Ghibu Onisifor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Ghibu Onisifor', '700652', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700652' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ghibu Onisifor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Irimescu Ion', '700652', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700652' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Irimescu Ion');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Pruteanu Aglae', '700652', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700652' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Pruteanu Aglae');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Alee', 'Ressu Camil', '700652', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700652' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Ressu Camil');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Fundac', 'Ressu Camil', '700652', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700652' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Fundac' AND COALESCE(street_name, '')='Ressu Camil');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Ressu Camil', '700652', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700652' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ressu Camil');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Stradela', 'Ressu Camil', '700652', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700652' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Stradela' AND COALESCE(street_name, '')='Ressu Camil');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Romanescu Aristizza', '700652', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700652' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Romanescu Aristizza');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Alee', 'Strugurilor nr. 87-T; 104 -T', '700652', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700652' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Strugurilor nr. 87-T; 104 -T');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Strugurilor nr. 25-T; 10-T', '700652', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700652' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Strugurilor nr. 25-T; 10-T');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Sturdza-Bulandra Lucia', '700652', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700652' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Sturdza-Bulandra Lucia');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Alee', 'Barleanu Iftimie', '700653', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700653' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Barleanu Iftimie');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Fundac', 'Barleanu Iftimie', '700653', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700653' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Fundac' AND COALESCE(street_name, '')='Barleanu Iftimie');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Barleanu Iftimie', '700653', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700653' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Barleanu Iftimie');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Stradela', 'Barleanu Iftimie', '700653', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700653' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Stradela' AND COALESCE(street_name, '')='Barleanu Iftimie');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Margarit George', '700653', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700653' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Margarit George');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Zamfirescu Neculai, prof. nr. 27-T; 26-T', '700653', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700653' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Zamfirescu Neculai, prof. nr. 27-T; 26-T');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Arinis', '700654', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700654' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Arinis');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Codrului', '700654', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700654' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Codrului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Stradela', 'Codrului', '700654', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700654' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Stradela' AND COALESCE(street_name, '')='Codrului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Alee', 'Podisului', '700654', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700654' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Podisului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Podisului', '700654', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700654' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Podisului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Valeni', '700654', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700654' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Valeni');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Stradela', 'Valeni', '700654', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700654' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Stradela' AND COALESCE(street_name, '')='Valeni');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Viorelelor', '700654', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700654' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Viorelelor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Alee', 'Voinesti', '700654', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700654' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Voinesti');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Voinesti', '700654', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700654' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Voinesti');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Stradela', 'Voinesti', '700654', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700654' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Stradela' AND COALESCE(street_name, '')='Voinesti');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Sosea', 'Voinesti nr. 27-T; 28 - T', '700654', '', 'Iasi 11 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700654' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Sosea' AND COALESCE(street_name, '')='Voinesti nr. 27-T; 28 - T');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Diminetii nr. 2-T', '700668', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700668' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Diminetii nr. 2-T');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Bulevard', 'Poitiers nr. 79', '700674', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700674' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Bulevard' AND COALESCE(street_name, '')='Poitiers nr. 79');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Sosea', 'Iasi-Hlincea 1-T; 2-T', '700682', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700682' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Sosea' AND COALESCE(street_name, '')='Iasi-Hlincea 1-T; 2-T');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Sosea', 'Nicolina nr. 103-T', '700690', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700690' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Sosea' AND COALESCE(street_name, '')='Nicolina nr. 103-T');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Alee', 'Neculai Tudor nr. 127', '700691', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700691' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Neculai Tudor nr. 127');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Alee', 'Neculai Tudor nr. 129-131', '700692', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700692' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Neculai Tudor nr. 129-131');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Sosea', 'Nicolina nr. 94-T', '700710', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700710' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Sosea' AND COALESCE(street_name, '')='Nicolina nr. 94-T');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Constantin Brancusi', '700712', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700712' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Constantin Brancusi');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Stradela', 'Valea Adanca', '700712', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700712' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Stradela' AND COALESCE(street_name, '')='Valea Adanca');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Nicolae Grigorescu', '700712', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700712' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Nicolae Grigorescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Brancusi Constantin', '700712', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700712' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Brancusi Constantin');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Grigorescu Nicolae', '700712', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700712' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Grigorescu Nicolae');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Honoriu Emil, prof', '700717', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700717' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Honoriu Emil, prof');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Zamfirescu Neculai, prof. nr. 1-25; 2-24', '700717', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700717' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Zamfirescu Neculai, prof. nr. 1-25; 2-24');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Fortus', '700718', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700718' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Fortus');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Fundac', 'Otelariei', '700718', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700718' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Fundac' AND COALESCE(street_name, '')='Otelariei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Otelariei', '700718', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700718' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Otelariei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Bucur Nicolae', '700719', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700719' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Bucur Nicolae');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Fundac', 'Sfantul Vasile', '700732', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700732' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Fundac' AND COALESCE(street_name, '')='Sfantul Vasile');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Sfantul Vasile', '700732', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700732' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Sfantul Vasile');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Sosea', 'Nicolina nr. 44-56', '700735', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700735' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Sosea' AND COALESCE(street_name, '')='Nicolina nr. 44-56');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Alee', 'Neculai Tudor nr. 84-T, 84A', '700737', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700737' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Neculai Tudor nr. 84-T, 84A');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Dimitrescu Stefante Paun Pincio Ion', '700738', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700738' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Dimitrescu Stefante Paun Pincio Ion');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Baba Corneliu', '700739', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700739' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Baba Corneliu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Alee', 'Ivanescu Gheorghe', '700739', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700739' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Ivanescu Gheorghe');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Ivanescu Gheorghe', '700739', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700739' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ivanescu Gheorghe');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Stradela', 'Ivanescu Gheorghe', '700739', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700739' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Stradela' AND COALESCE(street_name, '')='Ivanescu Gheorghe');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Luchian Stefan', '700739', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700739' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Luchian Stefan');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Petrescu Cezar', '700739', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700739' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Petrescu Cezar');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Alee', 'Strugurilor nr. 1-85; 2 -102', '700739', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700739' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Strugurilor nr. 1-85; 2 -102');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Fundac', 'Baciu Margareta', '700935', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700935' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Fundac' AND COALESCE(street_name, '')='Baciu Margareta');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Baciu Margareta', '700935', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700935' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Baciu Margareta');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Caudella Eduard, prof.', '700935', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700935' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Caudella Eduard, prof.');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Galino Mihail', '700935', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700935' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Galino Mihail');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Ciuca Mihai', '700937', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700937' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ciuca Mihai');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Condrea P. Petru', '700937', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700937' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Condrea P. Petru');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Tudoranu Gheorghe', '700937', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700937' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Tudoranu Gheorghe');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Camarut Mihai', '700940', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700940' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Camarut Mihai');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Ganju Ioan', '700940', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700940' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ganju Ioan');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Hotnog Stefan', '700940', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700940' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Hotnog Stefan');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Mihailescu-Craiu Victor', '700940', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700940' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Mihailescu-Craiu Victor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Alee', 'Baliff Leon', '700946', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700946' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Baliff Leon');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Fundac', 'Baliff Leon', '700946', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700946' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Fundac' AND COALESCE(street_name, '')='Baliff Leon');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Baliff Leon', '700946', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700946' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Baliff Leon');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Braescu Alexandru', '700946', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700946' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Braescu Alexandru');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Claudian Alexandru', '700946', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700946' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Claudian Alexandru');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Manicatide Mihail', '700946', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700946' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Manicatide Mihail');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Obregia Anastasie', '700946', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700946' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Obregia Anastasie');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Popa T. Grigore', '700946', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700946' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Popa T. Grigore');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Ralea Mihail', '700946', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700946' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ralea Mihail');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Trancu-Rainer Marta', '700946', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700946' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Trancu-Rainer Marta');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Zeletin Stefan', '700946', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700946' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Zeletin Stefan');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Stradela', 'Zeletin Stefan', '700946', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700946' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Stradela' AND COALESCE(street_name, '')='Zeletin Stefan');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Sosea', 'Bucium nr. 74-82', '700932', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700932' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Sosea' AND COALESCE(street_name, '')='Bucium nr. 74-82');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Alee', 'Buzatov Petre', '700932', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700932' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Buzatov Petre');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Buzatov Petre', '700932', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700932' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Buzatov Petre');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Butureanu Vladimir', '700933', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700933' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Butureanu Vladimir');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Fundac', 'Anghel Dimitrie', '700934', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700934' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Fundac' AND COALESCE(street_name, '')='Anghel Dimitrie');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Anghel Dimitrie', '700934', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700934' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Anghel Dimitrie');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Capsa Scarlat', '700934', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700934' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Capsa Scarlat');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Carp Mihai', '700934', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700934' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Carp Mihai');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Chiritescu Gheorghe', '700934', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700934' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Chiritescu Gheorghe');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Cornea Mihail', '700934', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700934' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Cornea Mihail');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Emilian Cornelia', '700934', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700934' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Emilian Cornelia');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Hogas Calistrat', '700934', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700934' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Hogas Calistrat');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Missir Th. Petru', '700934', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700934' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Missir Th. Petru');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Nadejde Ioan', '700934', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700934' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Nadejde Ioan');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Popa I. Nicolae', '700934', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700934' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Popa I. Nicolae');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Sevastos Mihail', '700934', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700934' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Sevastos Mihail');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Erbiceanu Constantin', '700936', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700936' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Erbiceanu Constantin');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Gotcu Ioan', '700936', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700936' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Gotcu Ioan');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Ravarut Mihai', '700936', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700936' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ravarut Mihai');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Coanda Henri', '700950', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700950' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Coanda Henri');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Fundac', 'Garleanu Emil', '700950', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700950' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Fundac' AND COALESCE(street_name, '')='Garleanu Emil');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Rosetti Theodor', '700950', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700950' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Rosetti Theodor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Sebastian Mihail', '700950', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700950' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Sebastian Mihail');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Varnav Scarlat', '700950', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700950' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Varnav Scarlat');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Chelcea Ion', '700951', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700951' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Chelcea Ion');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Bogdan George', '700931', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700931' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Bogdan George');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Negura Nicolae', '700931', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700931' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Negura Nicolae');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Slatineanu Alexandru', '700931', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700931' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Slatineanu Alexandru');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Thiron Constantin', '700931', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700931' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Thiron Constantin');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Zane Gheorghe 1-T; 2-T', '700933', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700933' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Zane Gheorghe 1-T; 2-T');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Alee', 'Schit Tarata', '700952', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700952' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Schit Tarata');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Schit Tarata', '700952', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700952' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Schit Tarata');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Alee', 'Piatra Sfanta', '700952', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700952' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Piatra Sfanta');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Iasi', 'Iasi', 'Strada', 'Piatra Sfanta', '700952', '', 'Iasi 3 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='700952' AND state='Iasi' AND city='Iasi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Piatra Sfanta');

-- === orase GONE (61 randuri; cele folosite de parteneri raman) ===
DELETE FROM res_zip z
 WHERE (z.id, z.state, z.city) IN (VALUES (1789, 'Bacau', 'Bacau'), (1880, 'Bacau', 'Bacau'), (2211, 'Bacau', 'Bacau'), (9982, 'Covasna', 'Sfantu Gheorghe'), (10045, 'Covasna', 'Sfantu Gheorghe'), (14578, 'Iasi', 'Iasi'), (14579, 'Iasi', 'Iasi'), (14605, 'Iasi', 'Iasi'), (14606, 'Iasi', 'Iasi'), (14607, 'Iasi', 'Iasi'), (14636, 'Iasi', 'Iasi'), (14637, 'Iasi', 'Iasi'), (14640, 'Iasi', 'Iasi'), (14641, 'Iasi', 'Iasi'), (14704, 'Iasi', 'Iasi'), (14711, 'Iasi', 'Iasi'), (14712, 'Iasi', 'Iasi'), (14795, 'Iasi', 'Iasi'), (14811, 'Iasi', 'Iasi'), (14849, 'Iasi', 'Iasi'), (14998, 'Iasi', 'Iasi'), (15001, 'Iasi', 'Iasi'), (15002, 'Iasi', 'Iasi'), (15075, 'Iasi', 'Iasi'), (15080, 'Iasi', 'Iasi'), (15126, 'Iasi', 'Iasi'), (15183, 'Iasi', 'Iasi'), (15187, 'Iasi', 'Iasi'), (15189, 'Iasi', 'Iasi'), (15221, 'Iasi', 'Iasi'), (15230, 'Iasi', 'Iasi'), (15231, 'Iasi', 'Iasi'), (15244, 'Iasi', 'Iasi'), (15264, 'Iasi', 'Iasi'), (15267, 'Iasi', 'Iasi'), (15269, 'Iasi', 'Iasi'), (15320, 'Iasi', 'Iasi'), (15325, 'Iasi', 'Iasi'), (15342, 'Iasi', 'Iasi'), (15354, 'Iasi', 'Iasi'), (15355, 'Iasi', 'Iasi'), (15374, 'Iasi', 'Iasi'), (15493, 'Iasi', 'Iasi'), (15494, 'Iasi', 'Iasi'), (15495, 'Iasi', 'Iasi'), (15496, 'Iasi', 'Iasi'), (15497, 'Iasi', 'Iasi'), (15508, 'Iasi', 'Iasi'), (15509, 'Iasi', 'Iasi'), (15510, 'Iasi', 'Iasi'), (15511, 'Iasi', 'Iasi'), (15527, 'Iasi', 'Iasi'), (15534, 'Iasi', 'Iasi'), (15562, 'Iasi', 'Iasi'), (15565, 'Iasi', 'Iasi'), (15659, 'Iasi', 'Iasi'), (15665, 'Iasi', 'Iasi'), (15675, 'Iasi', 'Iasi'), (15698, 'Iasi', 'Iasi'), (15703, 'Iasi', 'Iasi'), (15729, 'Iasi', 'Iasi'))
   AND NOT EXISTS (SELECT 1 FROM res_partner p WHERE p.zip_id = z.id);

-- === relatii pentru randurile noi/redenumite (ca post_init_hook) ===
DROP TABLE IF EXISTS _zip_remap;
CREATE TEMP TABLE _zip_remap ON COMMIT DROP AS SELECT id FROM res_zip WHERE country_id IS NULL;
UPDATE res_zip z SET country_id = c.id FROM res_country c, _zip_remap t WHERE z.id = t.id AND c.code = 'RO';
UPDATE res_zip z SET state_id = s.id
  FROM res_country_state s, _zip_remap t
 WHERE z.id = t.id AND s.l10n_ro_prefix_zip = SUBSTRING(z.name, 1, 2);
CREATE EXTENSION IF NOT EXISTS unaccent;
UPDATE res_zip z SET city_id = rc.id
  FROM res_city rc, _zip_remap t
 WHERE z.id = t.id AND unaccent(z.city) = unaccent(rc.name->>'en_US')
   AND z.state_id = rc.state_id AND z.name = rc.zipcode;
UPDATE res_zip z SET city_id = rc.id
  FROM res_city rc, _zip_remap t
 WHERE z.id = t.id AND unaccent(z.city) = unaccent(rc.name->>'en_US')
   AND z.state_id = rc.state_id AND z.city_id IS NULL;
UPDATE res_zip z SET city_id = rc.id, state_id = rc.state_id
  FROM ir_model_data d, res_city rc, _zip_remap t
 WHERE z.id = t.id AND d.module = 'l10n_ro_city' AND d.model = 'res.city' AND d.res_id = rc.id
   AND d.name = CASE z.sector WHEN '1' THEN 'RO_179141' WHEN '2' THEN 'RO_179150' WHEN '3' THEN 'RO_179169' WHEN '4' THEN 'RO_179178' WHEN '5' THEN 'RO_179187' WHEN '6' THEN 'RO_179196' END;
COMMIT;
