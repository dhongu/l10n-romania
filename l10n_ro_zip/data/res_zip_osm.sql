-- Strazile oraselor mici: nume din OpenStreetMap, cod de la posta-romana.ro. Idempotent.
-- Date OSM: (c) OpenStreetMap contributors, licenta ODbL (https://www.openstreetmap.org/copyright).
BEGIN;
SELECT setval('res_zip_id_seq', (SELECT MAX(id) FROM res_zip));

-- === oras Beresti (Galati) ===
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Beresti', 'Strada', 'Albinelor', '805100', '', 'Beresti Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805100' AND state='Galati' AND city='Beresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Albinelor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Beresti', 'Strada', 'Bizanului', '805100', '', 'Beresti Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805100' AND state='Galati' AND city='Beresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Bizanului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Beresti', 'Strada', 'Cartierul Nou', '805100', '', 'Beresti Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805100' AND state='Galati' AND city='Beresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Cartierul Nou');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Beresti', 'Strada', 'Codrului', '805100', '', 'Beresti Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805100' AND state='Galati' AND city='Beresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Codrului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Beresti', 'Strada', 'Crinului', '805100', '', 'Beresti Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805100' AND state='Galati' AND city='Beresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Crinului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Beresti', 'Strada', 'Crangului', '805100', '', 'Beresti Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805100' AND state='Galati' AND city='Beresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Crangului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Beresti', 'Strada', 'Duzilor', '805100', '', 'Beresti Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805100' AND state='Galati' AND city='Beresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Duzilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Beresti', 'Strada', 'Horincei', '805100', '', 'Beresti Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805100' AND state='Galati' AND city='Beresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Horincei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Beresti', 'Strada', 'Izvorului', '805100', '', 'Beresti Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805100' AND state='Galati' AND city='Beresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Izvorului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Beresti', 'Strada', 'Liliacului', '805100', '', 'Beresti Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805100' AND state='Galati' AND city='Beresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Liliacului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Beresti', 'Strada', 'Lt. Anton Cornita', '805100', '', 'Beresti Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805100' AND state='Galati' AND city='Beresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Lt. Anton Cornita');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Beresti', 'Strada', 'Lt. Iosub Dumitru', '805100', '', 'Beresti Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805100' AND state='Galati' AND city='Beresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Lt. Iosub Dumitru');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Beresti', 'Strada', 'Luceafarului', '805100', '', 'Beresti Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805100' AND state='Galati' AND city='Beresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Luceafarului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Beresti', 'Strada', 'Muncii', '805100', '', 'Beresti Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805100' AND state='Galati' AND city='Beresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Muncii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Beresti', 'Strada', 'Muncitorului', '805100', '', 'Beresti Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805100' AND state='Galati' AND city='Beresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Muncitorului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Beresti', 'Strada', 'Muzicii', '805100', '', 'Beresti Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805100' AND state='Galati' AND city='Beresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Muzicii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Beresti', 'Strada', 'Plugului', '805100', '', 'Beresti Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805100' AND state='Galati' AND city='Beresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Plugului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Beresti', 'Strada', 'Primaverii', '805100', '', 'Beresti Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805100' AND state='Galati' AND city='Beresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Primaverii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Beresti', 'Strada', 'Recoltei', '805100', '', 'Beresti Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805100' AND state='Galati' AND city='Beresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Recoltei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Beresti', 'Strada', 'Salcamului', '805100', '', 'Beresti Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805100' AND state='Galati' AND city='Beresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Salcamului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Beresti', 'Strada', 'Secerei', '805100', '', 'Beresti Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805100' AND state='Galati' AND city='Beresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Secerei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Beresti', 'Strada', 'Stadionului', '805100', '', 'Beresti Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805100' AND state='Galati' AND city='Beresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Stadionului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Beresti', 'Strada', 'Taberei', '805100', '', 'Beresti Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805100' AND state='Galati' AND city='Beresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Taberei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Beresti', 'Strada', 'Trandafirilor', '805100', '', 'Beresti Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805100' AND state='Galati' AND city='Beresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Trandafirilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Beresti', 'Strada', 'Trandafirilor nr 50', '805100', '', 'Beresti Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805100' AND state='Galati' AND city='Beresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Trandafirilor nr 50');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Beresti', 'Strada', 'Valea Chinejii', '805100', '', 'Beresti Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805100' AND state='Galati' AND city='Beresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Valea Chinejii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Beresti', 'Strada', 'Viilor', '805100', '', 'Beresti Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805100' AND state='Galati' AND city='Beresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Viilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Beresti', 'Strada', 'Voinestilor', '805100', '', 'Beresti Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805100' AND state='Galati' AND city='Beresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Voinestilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Beresti', 'Strada', 'Zefirului', '805100', '', 'Beresti Ghiseu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805100' AND state='Galati' AND city='Beresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Zefirului');

-- === oras Tecuci (Galati) ===
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Alee', 'Arinului', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Arinului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Alee', 'Egalitatii', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Egalitatii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Alee', 'Matei Basarab', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Matei Basarab');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Alee', 'Plopilor', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Plopilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Alee', 'Teilor', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Teilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Alee', 'Vasile Alecsandri', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Vasile Alecsandri');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Alee', 'Strandului', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Strandului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Bulevard', 'Victoriei', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Bulevard' AND COALESCE(street_name, '')='Victoriei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Fundatura', 'Ana Ipatescu', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Fundatura' AND COALESCE(street_name, '')='Ana Ipatescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Fundatura', 'Cuza Voda', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Fundatura' AND COALESCE(street_name, '')='Cuza Voda');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Fundatura', 'Doctor Ion Kopetki', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Fundatura' AND COALESCE(street_name, '')='Doctor Ion Kopetki');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Fundatura', 'Ecaterina Teodoroiu', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Fundatura' AND COALESCE(street_name, '')='Ecaterina Teodoroiu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Fundatura', 'Furceni', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Fundatura' AND COALESCE(street_name, '')='Furceni');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Fundatura', 'Grivitei', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Fundatura' AND COALESCE(street_name, '')='Grivitei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Fundatura', 'Horia', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Fundatura' AND COALESCE(street_name, '')='Horia');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Fundatura', 'Izvor', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Fundatura' AND COALESCE(street_name, '')='Izvor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Fundatura', 'Mihail Kogalniceanu', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Fundatura' AND COALESCE(street_name, '')='Mihail Kogalniceanu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Fundatura', 'Militari', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Fundatura' AND COALESCE(street_name, '')='Militari');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Fundatura', 'Partizanului', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Fundatura' AND COALESCE(street_name, '')='Partizanului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Fundatura', 'Plutonier Stoicescu', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Fundatura' AND COALESCE(street_name, '')='Plutonier Stoicescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Fundatura', 'Theodor Serbanescu', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Fundatura' AND COALESCE(street_name, '')='Theodor Serbanescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Fundatura', 'Vasile Lupu', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Fundatura' AND COALESCE(street_name, '')='Vasile Lupu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Fundatura', 'Vultureni', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Fundatura' AND COALESCE(street_name, '')='Vultureni');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Fundatura', 'Vanatori', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Fundatura' AND COALESCE(street_name, '')='Vanatori');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Fundatura', 'Stefan Corodeanu', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Fundatura' AND COALESCE(street_name, '')='Stefan Corodeanu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Pasaj', 'Unirii', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Pasaj' AND COALESCE(street_name, '')='Unirii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', '1 Decembrie 1918', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='1 Decembrie 1918');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', '1 Mai', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='1 Mai');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', '13 Septembrie', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='13 Septembrie');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Abatorului', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Abatorului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Agricola Cardas', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Agricola Cardas');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Alecu Russo', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Alecu Russo');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Alexandru Cel Bun', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Alexandru Cel Bun');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Alexandru Lascarov Moldoveanu', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Alexandru Lascarov Moldoveanu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Alexandru Lapusneanu', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Alexandru Lapusneanu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Alexandru Odobescu', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Alexandru Odobescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Alexandru Papadopol Calimah', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Alexandru Papadopol Calimah');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Alexe Mateevici', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Alexe Mateevici');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Ana Ipatescu', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ana Ipatescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Anton Pann', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Anton Pann');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Aurel Vlaicu', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Aurel Vlaicu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Avram Iancu', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Avram Iancu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Bazinului', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Bazinului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Berzei', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Berzei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Bobalna', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Bobalna');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Bogdan Petriceicu Hasdeu', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Bogdan Petriceicu Hasdeu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Bradului', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Bradului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Bran', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Bran');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Bucovinei', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Bucovinei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Barladului', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Barladului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Calistrat Hogas', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Calistrat Hogas');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Carol', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Carol');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Castelului', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Castelului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Ciocirliei', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ciocirliei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Ciresului', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ciresului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Closca', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Closca');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Constantin Brancoveanu', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Constantin Brancoveanu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Constantin I. Mocanu', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Constantin I. Mocanu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Constantin Radovici', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Constantin Radovici');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Constitutiei', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Constitutiei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Costache Conachi', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Costache Conachi');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Costache Negri', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Costache Negri');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Costache Racovita', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Costache Racovita');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Crisana', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Crisana');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Crangului', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Crangului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Cuza Voda', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Cuza Voda');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Calugareni', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Calugareni');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Capitan Darbun', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Capitan Darbun');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Capitan Vlad', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Capitan Vlad');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Caramidariei', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Caramidariei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Dacia', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Dacia');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Dealului', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Dealului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Decebal', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Decebal');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Depoului', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Depoului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Dimitrie Cantemir', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Dimitrie Cantemir');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Dorobanti', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Dorobanti');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Dragoslavele', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Dragoslavele');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Dragos Voda', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Dragos Voda');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Dumbrava Rosie', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Dumbrava Rosie');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Duzilor', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Duzilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Ecaterina Teodoroiu', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ecaterina Teodoroiu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Elena Doamna', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Elena Doamna');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Epureni', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Epureni');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Eroilor', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Eroilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Eugen Boureanu', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Eugen Boureanu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Fabricii', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Fabricii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Feroviarilor', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Feroviarilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Florilor', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Florilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Focsa', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Focsa');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Furceni', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Furceni');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Galati', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Galati');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'General David Praporgescu', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='General David Praporgescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'General Eremia Grigorescu', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='General Eremia Grigorescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'General Ion Dragalina', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='General Ion Dragalina');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'General Ion Gheorghe Istrate', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='General Ion Gheorghe Istrate');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Genoiu Maior', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Genoiu Maior');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'George Apostu', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='George Apostu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'George Cosbuc', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='George Cosbuc');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Gheorghe Asachi', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Gheorghe Asachi');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Gheorghe Doja', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Gheorghe Doja');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Gheorghe Lazar', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Gheorghe Lazar');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Gheorghe Petrascu', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Gheorghe Petrascu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Gheorghe Sincai', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Gheorghe Sincai');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Gloriei', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Gloriei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Grigore Alexandrescu', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Grigore Alexandrescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Grigore Tabacaru', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Grigore Tabacaru');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Grivitei', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Grivitei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Grozesti', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Grozesti');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Garlei', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Garlei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Garii', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Garii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Horia', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Horia');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Hortensia Papadat Bengescu', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Hortensia Papadat Bengescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Iancu Jianu', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Iancu Jianu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Independentei', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Independentei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Ion Creanga', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ion Creanga');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Ion Eliade Radulescu', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ion Eliade Radulescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Ion Ghica Voda', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ion Ghica Voda');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Ion Petrovici', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ion Petrovici');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Ionita Hrisanti', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ionita Hrisanti');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Iorgu Iordan', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Iorgu Iordan');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Irimia Grigorescu', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Irimia Grigorescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Izvor', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Izvor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Libertatii', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Libertatii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Linistei', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Linistei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Livezi', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Livezi');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Locotenent Dragomir', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Locotenent Dragomir');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Maior Andrei', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Maior Andrei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Maior Gheorghe Sontu', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Maior Gheorghe Sontu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Matei Basarab', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Matei Basarab');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Mierlei', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Mierlei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Mihai Berza', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Mihai Berza');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Mihai Eminescu', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Mihai Eminescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Mihai Voda', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Mihai Voda');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Mihail Kogalniceanu', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Mihail Kogalniceanu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Milcov', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Milcov');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Militari', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Militari');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Mircea Eliade', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Mircea Eliade');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Mircea Voda', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Mircea Voda');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Mitropolit Andrei Saguna', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Mitropolit Andrei Saguna');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Movilei', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Movilei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Muncii', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Muncii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Muncitorului', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Muncitorului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Muzei', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Muzei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Malureni', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Malureni');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Marasesti', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Marasesti');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Natalia Negru', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Natalia Negru');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Negoita Danaila', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Negoita Danaila');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Nicolae Balcescu', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Nicolae Balcescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Nicolae Iorga', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Nicolae Iorga');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Nicolae Titulescu', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Nicolae Titulescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Nicoresti', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Nicoresti');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Ochesesti', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ochesesti');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Odaia', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Odaia');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Oituz', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Oituz');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Oltului', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Oltului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Pamfil Seicaru', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Pamfil Seicaru');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Parcului', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Parcului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Partizanului', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Partizanului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Peri', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Peri');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Petru Rares', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Petru Rares');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Pictor Dimitrie Harlescu', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Pictor Dimitrie Harlescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Pietii', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Pietii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Plevnei', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Plevnei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Plugului', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Plugului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Plutonier Bogdan', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Plutonier Bogdan');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Plutonier Stoicescu', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Plutonier Stoicescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Popa Sapca', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Popa Sapca');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Primaverii', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Primaverii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Prundului', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Prundului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Prunului', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Prunului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Pacii', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Pacii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Republicii', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Republicii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Rodnei', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Rodnei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Rosiori', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Rosiori');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Salcamului', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Salcamului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Sergent Serea', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Sergent Serea');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Sergent Stefan Putanu', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Sergent Stefan Putanu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Sfintii Voievozi', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Sfintii Voievozi');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Simion Barnutiu', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Simion Barnutiu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Smaranda Braiescu', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Smaranda Braiescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Soarelui', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Soarelui');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Sperantei', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Sperantei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Stejarului', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Stejarului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Stelei', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Stelei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Sublocotenent Nicolae Petica', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Sublocotenent Nicolae Petica');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Tecucel', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Tecucel');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Tecuciul Nou', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Tecuciul Nou');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Tineretului', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Tineretului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Tractoristilor', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Tractoristilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Traian', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Traian');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Transilvania', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Transilvania');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Tudor Pamfile', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Tudor Pamfile');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Tudor Vladimirescu', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Tudor Vladimirescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Unirii', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Unirii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Vasile Alecsandri', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Vasile Alecsandri');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Vasile Conta', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Vasile Conta');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Vasile Lupu', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Vasile Lupu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Vasile Parvan', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Vasile Parvan');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Viei', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Viei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Vigilentei', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Vigilentei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Vlad Tepes', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Vlad Tepes');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Vointei', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Vointei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Vornicului', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Vornicului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Vultureni', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Vultureni');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Vanatori', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Vanatori');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Valeni', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Valeni');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Zimbrului', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Zimbrului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Zorilor', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Zorilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Stefan Octavian Iosif', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Stefan Octavian Iosif');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Stefan Petica', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Stefan Petica');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Tecuci', 'Strada', 'Stefan cel Mare', '805300', '', 'Tecuci Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805300' AND state='Galati' AND city='Tecuci' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Stefan cel Mare');

-- === oras Targu Bujor (Galati) ===
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', '11 Iunie', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='11 Iunie');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', '3 Stejari', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='3 Stejari');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Abatorului', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Abatorului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Adevarului', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Adevarului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Avantului', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Avantului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Berzei', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Berzei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Bradului', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Bradului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Brigadierilor', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Brigadierilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Bujorilor', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Bujorilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Constructorilor', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Constructorilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Campului', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Campului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Cazanesti', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Cazanesti');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Democratiei', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Democratiei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Doctor Gheorghe Buzoianu', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Doctor Gheorghe Buzoianu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Florilor', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Florilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Gen. Eremia Grigorescu', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Gen. Eremia Grigorescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'General Eremia Grigorescu', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='General Eremia Grigorescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Grigore Hagiu', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Grigore Hagiu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Independentei', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Independentei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Justitiei', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Justitiei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Mecanizatorilor', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Mecanizatorilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Melodiei', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Melodiei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Mercur', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Mercur');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Merilor', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Merilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Morii', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Morii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Movilei', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Movilei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Muzicii', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Muzicii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Nucilor', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Nucilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Pacii', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Pacii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Partizanilor', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Partizanilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Pietii', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Pietii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Primaverii', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Primaverii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Privighetorii', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Privighetorii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Prunului', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Prunului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Recoltei', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Recoltei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Salcamilor', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Salcamilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Secerii', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Secerii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Semanatorilor', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Semanatorilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Spicului', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Spicului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Stemei', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Stemei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Teiului', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Teiului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Tractorului', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Tractorului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Victoriei', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Victoriei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Viilor', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Viilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Zorilor', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Zorilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Galati', 'Targu Bujor', 'Strada', 'Scolii', '805200', '', 'Targu Bujor Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='805200' AND state='Galati' AND city='Targu Bujor' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Scolii');

-- === oras Husi (Vaslui) ===
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Alee', 'Dobrina', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Dobrina');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Alee', 'Mihail Kogalniceanu', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Mihail Kogalniceanu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Alee', 'Stadionului', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Stadionului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Bulevard', '1 Mai', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Bulevard' AND COALESCE(street_name, '')='1 Mai');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Fundatura', 'Calarasi', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Fundatura' AND COALESCE(street_name, '')='Calarasi');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Fundatura', 'Dobrina', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Fundatura' AND COALESCE(street_name, '')='Dobrina');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Fundatura', 'Viilor', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Fundatura' AND COALESCE(street_name, '')='Viilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Fundatura', 'Viticulturii', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Fundatura' AND COALESCE(street_name, '')='Viticulturii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Fundatura', 'Stefan Ionescu', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Fundatura' AND COALESCE(street_name, '')='Stefan Ionescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', '1 Decembrie 1918', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='1 Decembrie 1918');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', '14 Iulie', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='14 Iulie');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', '22 Decembrie', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='22 Decembrie');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Adam Baltatul', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Adam Baltatul');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Albita', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Albita');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Alecu Beldiman', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Alecu Beldiman');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Alexandru Ghitescu', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Alexandru Ghitescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Alexandru Giugaru', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Alexandru Giugaru');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Alexandru Ioan Cuza', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Alexandru Ioan Cuza');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Alexandru cel Bun', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Alexandru cel Bun');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Amurgului', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Amurgului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Ana Ipatescu', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ana Ipatescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Anton Adam', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Anton Adam');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Anton Sarbu', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Anton Sarbu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Arion', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Arion');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Avantului', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Avantului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Barbu Delavrancea', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Barbu Delavrancea');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Barbu Lautaru', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Barbu Lautaru');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Bariera Pascal', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Bariera Pascal');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Bradului', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Bradului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'C.Dragan', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='C.Dragan');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Calea Basarabiei', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Calea Basarabiei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Castroian', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Castroian');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Ciocu Toader', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ciocu Toader');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Ciprian Porumbescu', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ciprian Porumbescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Combinat', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Combinat');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Constantin David', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Constantin David');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Corneliu Adamesteanu', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Corneliu Adamesteanu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Cornii', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Cornii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Costache Negri', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Costache Negri');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Costache Olareanu', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Costache Olareanu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Cotoi', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Cotoi');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Cotroceni', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Cotroceni');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Crizantemelor', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Crizantemelor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Crucii', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Crucii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Calugaru Stefan', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Calugaru Stefan');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Calarasi', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Calarasi');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Capitan Anastasiu', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Capitan Anastasiu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Capitan Carp', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Capitan Carp');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Capitan Ianculescu', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Capitan Ianculescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Capitan Nicolae Cisman', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Capitan Nicolae Cisman');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Dacia', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Dacia');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Dealul Cotroceni', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Dealul Cotroceni');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Diaconu Irimia', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Diaconu Irimia');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Dobrina', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Dobrina');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Doctor Cherimbach', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Doctor Cherimbach');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Doctor Gheorghe Balan', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Doctor Gheorghe Balan');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Doctor Lupu Nicolau', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Doctor Lupu Nicolau');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Donea', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Donea');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Dumitru David', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Dumitru David');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Dumitru Hodea', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Dumitru Hodea');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Dumitru Patras', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Dumitru Patras');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Episcopiei', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Episcopiei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Eremia Movila', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Eremia Movila');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Eroilor', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Eroilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Erou Arhire Stefan', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Erou Arhire Stefan');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Erou Sergent Toma Anton', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Erou Sergent Toma Anton');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Frunzelor', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Frunzelor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Fantanilor', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Fantanilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'General Poenaru', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='General Poenaru');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'General Teleman', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='General Teleman');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'George Cosbuc', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='George Cosbuc');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'George Emil Palade', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='George Emil Palade');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Gheorghe Bucur', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Gheorghe Bucur');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Gheorghe Doja', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Gheorghe Doja');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Gheorghe Frent', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Gheorghe Frent');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Gheorghe Gociu', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Gheorghe Gociu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Gheorghe Nedelcu', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Gheorghe Nedelcu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Gheorghe Parpalea', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Gheorghe Parpalea');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Gheorghe Paveliu', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Gheorghe Paveliu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Gradinari', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Gradinari');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Garii', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Garii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Hanganu', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Hanganu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'I. Al. Anghelus', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='I. Al. Anghelus');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Iacob Anton', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Iacob Anton');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Iancu Apostu', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Iancu Apostu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Iancu Postu', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Iancu Postu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Iftene Caciula', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Iftene Caciula');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Ioan Slavici', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ioan Slavici');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Iojup Radu', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Iojup Radu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Ion Cernatescu', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ion Cernatescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Ion Creanga', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ion Creanga');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Ion Esanu', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ion Esanu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Ion Luca Caragiale', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ion Luca Caragiale');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Ion Voda cel Viteaz', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ion Voda cel Viteaz');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Ispas Ivanciu', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ispas Ivanciu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Jomir', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Jomir');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Locotenent Dragulet', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Locotenent Dragulet');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Locotenent Dumitru Radu', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Locotenent Dumitru Radu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Locotenent Gavril Teodoru', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Locotenent Gavril Teodoru');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Locotenent Mucenic', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Locotenent Mucenic');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Locotenent Octav Hagiu', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Locotenent Octav Hagiu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Luceafarul', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Luceafarul');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Lacramioarelor', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Lacramioarelor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'M.Romila', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='M.Romila');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Maior Popescu', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Maior Popescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Maior Popovici', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Maior Popovici');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Marin Ralea', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Marin Ralea');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Melchisedec', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Melchisedec');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Meleti Istrati', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Meleti Istrati');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Mihail Eminescu', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Mihail Eminescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Mihail Kogalniceanu', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Mihail Kogalniceanu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Mihail Sadoveanu', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Mihail Sadoveanu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Moldovei', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Moldovei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Mos Ion Roata', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Mos Ion Roata');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Neagoe Basarab', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Neagoe Basarab');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Nicolae Balcescu', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Nicolae Balcescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Nicolae Malaxa', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Nicolae Malaxa');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Nicolae Polojan', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Nicolae Polojan');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Nicolae Popa', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Nicolae Popa');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Obor', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Obor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Octav Hagiu', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Octav Hagiu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Octavian Cotescu', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Octavian Cotescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Orizontului', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Orizontului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Patras Ion', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Patras Ion');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Paul Barais', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Paul Barais');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Pavel Tacu', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Pavel Tacu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Petru Nicolau', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Petru Nicolau');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Petru Tomescu', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Petru Tomescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Plaiului', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Plaiului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Popa Stefan Iliescu', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Popa Stefan Iliescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Primaverii', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Primaverii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Prut', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Prut');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Rosetti Scarlat', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Rosetti Scarlat');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Rotundoaia', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Rotundoaia');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Raiesti', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Raiesti');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Saca', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Saca');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Schit', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Schit');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Sergent Major Erou Arhire Stefan', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Sergent Major Erou Arhire Stefan');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Sfantul Dumitru', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Sfantul Dumitru');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Sfantul Gheorghe', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Sfantul Gheorghe');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Sfantul Ioan', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Sfantul Ioan');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'T.Gheorghe', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='T.Gheorghe');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Toader Gaita', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Toader Gaita');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Toma Kisakoff', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Toma Kisakoff');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Tudor Arghezi', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Tudor Arghezi');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Tudor Vladimirescu', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Tudor Vladimirescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Turbata', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Turbata');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Vasile Alecsandri', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Vasile Alecsandri');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Vasile Croitoru', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Vasile Croitoru');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Vasile Lupu', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Vasile Lupu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Victoriei', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Victoriei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Viilor', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Viilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Valciu Veteranu', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Valciu Veteranu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Zidari', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Zidari');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Zorilor', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Zorilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Sara', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Sara');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Scolii', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Scolii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Stefan Burghelea', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Stefan Burghelea');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Stefan Dumitrescu', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Stefan Dumitrescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Strada', 'Stefan cel Mare', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Stefan cel Mare');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Stradela', 'Libertatii', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Stradela' AND COALESCE(street_name, '')='Libertatii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Husi', 'Sosea', 'Husi-Stanilesti', '735100', '', 'Husi 1 Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735100' AND state='Vaslui' AND city='Husi' AND COALESCE(street_type, '')='Sosea' AND COALESCE(street_name, '')='Husi-Stanilesti');

-- === oras Murgeni (Vaslui) ===
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Murgeni', 'Alee', 'Ciulinilor', '737370', '', 'Murgeni Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='737370' AND state='Vaslui' AND city='Murgeni' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Ciulinilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Murgeni', 'Alee', 'Salcamilor', '737370', '', 'Murgeni Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='737370' AND state='Vaslui' AND city='Murgeni' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Salcamilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Murgeni', 'Strada', 'Academician Nicolaie Profir', '737370', '', 'Murgeni Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='737370' AND state='Vaslui' AND city='Murgeni' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Academician Nicolaie Profir');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Murgeni', 'Strada', 'Alecu Sturdza', '737370', '', 'Murgeni Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='737370' AND state='Vaslui' AND city='Murgeni' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Alecu Sturdza');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Murgeni', 'Strada', 'Antohi Petru', '737370', '', 'Murgeni Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='737370' AND state='Vaslui' AND city='Murgeni' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Antohi Petru');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Murgeni', 'Strada', 'Aurel Negara', '737370', '', 'Murgeni Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='737370' AND state='Vaslui' AND city='Murgeni' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Aurel Negara');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Murgeni', 'Strada', 'Coman Ghenuta', '737370', '', 'Murgeni Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='737370' AND state='Vaslui' AND city='Murgeni' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Coman Ghenuta');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Murgeni', 'Strada', 'Dimitrie Cantemir', '737370', '', 'Murgeni Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='737370' AND state='Vaslui' AND city='Murgeni' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Dimitrie Cantemir');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Murgeni', 'Strada', 'Doctor Emil Juvara', '737370', '', 'Murgeni Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='737370' AND state='Vaslui' AND city='Murgeni' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Doctor Emil Juvara');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Murgeni', 'Strada', 'Doctor Eugen Mitrofan', '737370', '', 'Murgeni Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='737370' AND state='Vaslui' AND city='Murgeni' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Doctor Eugen Mitrofan');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Murgeni', 'Strada', 'Doctor Panait Sarbu', '737370', '', 'Murgeni Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='737370' AND state='Vaslui' AND city='Murgeni' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Doctor Panait Sarbu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Murgeni', 'Strada', 'Dr. Emil Juvara', '737370', '', 'Murgeni Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='737370' AND state='Vaslui' AND city='Murgeni' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Dr. Emil Juvara');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Murgeni', 'Strada', 'Elan', '737370', '', 'Murgeni Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='737370' AND state='Vaslui' AND city='Murgeni' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Elan');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Murgeni', 'Strada', 'Energiei', '737370', '', 'Murgeni Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='737370' AND state='Vaslui' AND city='Murgeni' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Energiei');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Murgeni', 'Strada', 'I. C. Balmus', '737370', '', 'Murgeni Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='737370' AND state='Vaslui' AND city='Murgeni' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='I. C. Balmus');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Murgeni', 'Strada', 'Inginer Vasile Dumitriu', '737370', '', 'Murgeni Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='737370' AND state='Vaslui' AND city='Murgeni' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Inginer Vasile Dumitriu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Murgeni', 'Strada', 'Mihai Eminescu', '737370', '', 'Murgeni Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='737370' AND state='Vaslui' AND city='Murgeni' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Mihai Eminescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Murgeni', 'Strada', 'Profesor Ion Raianu', '737370', '', 'Murgeni Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='737370' AND state='Vaslui' AND city='Murgeni' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Profesor Ion Raianu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Murgeni', 'Strada', 'Sat Nou', '737370', '', 'Murgeni Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='737370' AND state='Vaslui' AND city='Murgeni' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Sat Nou');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Murgeni', 'Strada', 'Stadion', '737370', '', 'Murgeni Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='737370' AND state='Vaslui' AND city='Murgeni' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Stadion');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Murgeni', 'Strada', 'Valea Elanului', '737370', '', 'Murgeni Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='737370' AND state='Vaslui' AND city='Murgeni' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Valea Elanului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Murgeni', 'Strada', 'Viilor', '737370', '', 'Murgeni Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='737370' AND state='Vaslui' AND city='Murgeni' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Viilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Murgeni', 'Strada', 'Stefan cel Mare', '737370', '', 'Murgeni Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='737370' AND state='Vaslui' AND city='Murgeni' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Stefan cel Mare');

-- === oras Negresti (Vaslui) ===
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Alee', 'Nucilor', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Alee' AND COALESCE(street_name, '')='Nucilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', '1 Decembrie', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='1 Decembrie');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', '1 Mai', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='1 Mai');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', '11 Iunie', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='11 Iunie');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', '13 Septembrie', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='13 Septembrie');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', '8 Martie', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='8 Martie');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', '9 Mai', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='9 Mai');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Abator', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Abator');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Alexandru Ioan Cuza', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Alexandru Ioan Cuza');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Barladului', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Barladului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Casa Apelor', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Casa Apelor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Closca', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Closca');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Constantin Alexandru Rosetti', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Constantin Alexandru Rosetti');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Crisan', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Crisan');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Dacia', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Dacia');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Decebal', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Decebal');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Eternitatii', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Eternitatii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Florilor', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Florilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'George Cosbuc', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='George Cosbuc');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'George Enescu', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='George Enescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Gheorghe Doja', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Gheorghe Doja');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Garii', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Garii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Horia', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Horia');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Ion Costache Frimu', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ion Costache Frimu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Ion Creanga', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ion Creanga');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Ion Luca Caragiale', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Ion Luca Caragiale');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Micsunelelor', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Micsunelelor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Mihai Eminescu', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Mihai Eminescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Mihai Viteazu', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Mihai Viteazu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Mihail Kogalniceanu', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Mihail Kogalniceanu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Mihail Sadoveanu', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Mihail Sadoveanu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Negrea', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Negrea');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Nicolae Balcescu', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Nicolae Balcescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Nicolae Iorga', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Nicolae Iorga');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Noua', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Noua');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Nucului', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Nucului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Oborului', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Oborului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Pictor Nicolae Grigorescu', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Pictor Nicolae Grigorescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Pietii', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Pietii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Plopilor', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Plopilor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Pacii', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Pacii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Rozelor', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Rozelor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Stadionului', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Stadionului');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Traian', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Traian');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Tudor Vladimirescu', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Tudor Vladimirescu');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Unirii', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Unirii');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Vasile Alecsandri', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Vasile Alecsandri');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Viorelelor', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Viorelelor');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Zugravi', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Zugravi');
INSERT INTO res_zip (state, city, street_type, street_name, name, sector, office, address)
SELECT 'Vaslui', 'Negresti', 'Strada', 'Stefan cel Mare', '735200', '', 'Negresti Oficiu', ''
WHERE NOT EXISTS (SELECT 1 FROM res_zip WHERE name='735200' AND state='Vaslui' AND city='Negresti' AND COALESCE(street_type, '')='Strada' AND COALESCE(street_name, '')='Stefan cel Mare');

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
