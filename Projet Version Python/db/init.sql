DROP TABLE IF EXISTS public.zone_inondable CASCADE;
DROP TABLE IF EXISTS public.questions_logement CASCADE;

CREATE TABLE public.zone_inondable (
    id SERIAL PRIMARY KEY,
    critere VARCHAR(255) NOT NULL,
    question TEXT NOT NULL,
    reponses TEXT[] NOT NULL,
    scores_vulnerabilite NUMERIC[] NOT NULL,
    a_dependance BOOLEAN DEFAULT FALSE,
    id_question_liee INTEGER REFERENCES public.zone_inondable(id),
    recommandations TEXT
);

CREATE TABLE public.questions_logement (
    id SERIAL PRIMARY KEY,
    critere VARCHAR(255) NOT NULL,
    question TEXT NOT NULL,
    reponses TEXT[] NOT NULL,
    scores_vulnerabilite NUMERIC[] NOT NULL,
    a_dependance BOOLEAN DEFAULT FALSE,
    id_question_liee INTEGER REFERENCES public.questions_logement(id),
    recommandations TEXT
);

INSERT INTO public.zone_inondable (critere, question, reponses, scores_vulnerabilite, a_dependance, id_question_liee, recommandations) VALUES

-- Zone inondable
('Zone inondable', 'Quelle est l''adresse de votre bien ?', 
 ARRAY['Zone de dissipation de l''énergie (ZDE)', 'Ecoulement préférentiel (EP)', 'Modéré (M)', 'Fort (F)', 'Très fort (TF)'], 
 ARRAY[140, 140, 80, 110, 140], FALSE, NULL, NULL),

-- Niveau du plancher
('Niveau du plancher', 'Avez-vous fait des travaux récemment au niveau du rez-de-chaussée ?', 
 ARRAY['Oui', 'Non'], 
 ARRAY[0, 0], FALSE, NULL, NULL),

('Niveau du plancher', 'Quel est le niveau du premier plancher habitable de mon habitation ?', 
 ARRAY['x'], 
 ARRAY[0], FALSE, NULL, NULL),

-- Hauteur d'eau potentielle
('Hauteur d''eau potentielle', 'Calcul H = niveau d''inondation (donné dans la zone d''aléas) - niveau du premier plancher', 
 ARRAY['h >= 0.2', 'h <= 0.2'], 
 ARRAY[-20, 0], FALSE, NULL, NULL);


INSERT INTO public.questions_logement (critere, question, reponses, scores_vulnerabilite, a_dependance, id_question_liee, recommandations) VALUES

-- 1. Murs
('Murs', 'Vos murs sont-ils faits en bois ?', 
 ARRAY['Oui', 'Non'], 
 ARRAY[7.5, 0], FALSE, NULL, NULL),

-- 2. Isolant
('Isolant', 'Quel matériau d''isolation est utilisé dans votre logement ?', 
 ARRAY['Fibre minérale (laine de verre)', 'Fibre végétale', 'Vermiculite', 'Plastique alvéolaire', 'Je ne sais pas (proxi : fibre minérale)'], 
 ARRAY[10, 10, 10, 0, 10], FALSE, NULL, NULL),

-- 3. Isolant
('Isolant', 'Votre schéma d''isolation comporte-t-il un doublage collé en plâtre ?', 
 ARRAY['Oui', 'Non', 'Je ne sais pas'], 
 ARRAY[5, 0, 5], FALSE, NULL, NULL),

-- 4. Enduit intérieur
('Enduit intérieur', 'Quel enduit est posé sur vos murs et cloisons ?', 
 ARRAY['Mortier ciment', 'Plâtre'], 
 ARRAY[0, 2], FALSE, NULL, NULL),

-- 5. Revêtements muraux intérieurs
('Revêtements muraux intérieurs', 'Quel revêtement est posé sur vos enduits, cloisons ou portes ?', 
 ARRAY['Papier', 'Peinture', 'Textile', 'Bois', 'Carrelage collé', 'Carrelage scellé', 'Je ne sais pas (proxi : )'], 
 ARRAY[10, 7.5, 10, 5, 0, 0, 7.5], FALSE, NULL, NULL),

-- 6. Plancher
('Plancher', 'En quel matériau est fait votre plancher ?', 
 ARRAY['Béton', 'Métal et briques', 'Bois'], 
 ARRAY[0, 0, 7.5], FALSE, NULL, NULL),

-- 7. Revêtements sols
('Revêtements sols', 'Quelle est la matière de revêtement de vos sols ?', 
 ARRAY['Peinture', 'Textile', 'Plastique', 'Bois massif', 'Bois lamelles', 'Carrelage collé', 'Carrelage scellé'], 
 ARRAY[1, 7.5, 2, 3, 5, 0, 0], FALSE, NULL, NULL),

-- 8. Portes intérieures
('Portes intérieures', 'En quel matériau sont fabriquées vos portes intérieures ?', 
 ARRAY['Carton (portes alvéolaires)', 'Bois', 'Autre', 'Je ne sais pas'], 
 ARRAY[7.5, 4, 3, 4], FALSE, NULL, NULL),

-- 9. Portes intérieures
('Portes intérieures', 'En quel matériau sont faites les huisseries ?', 
 ARRAY['Bois', 'Métal', 'Je ne sais pas'], 
 ARRAY[1, 0, 1], FALSE, NULL, NULL),

-- 10. Escalier intérieur
('Escalier intérieur', 'En quoi est fait votre ou vos escaliers intérieurs ?', 
 ARRAY['Béton', 'Bois', 'Autre'], 
 ARRAY[0, 4, 2], FALSE, NULL, NULL),

-- 11. Portes d'entrée
('Portes d''entrée', 'En quelle matière sont faites vos portes d''entrée ?', 
 ARRAY['Bois massif', 'PVC', 'Métal (acier, aluminium)'], 
 ARRAY[4, 0, 0], FALSE, NULL, NULL),

-- 12. Portes d'entrée
('Portes d''entrée', 'Et les huisseries ?', 
 ARRAY['Bois', 'Autre'], 
 ARRAY[1, 0], FALSE, NULL, NULL),

-- 13. Fenêtres
('Fenêtres', 'En quelle matière sont faites vos fenêtres ?', 
 ARRAY['Bois + H > 1,2 m', 'PVC', 'Métal (acier, aluminium)'], 
 ARRAY[2, 0, 0], FALSE, NULL, NULL),

-- 14. Panneaux vitrés de grande dimension
('Panneaux vitrés de grande dimension', 'Votre logement dispose-t-il de baies vitrées ou de porte-fenêtres ?', 
 ARRAY['Oui + H > 0,5', 'Non'], 
 ARRAY[5, 0], FALSE, NULL, NULL),

-- 15. Volets
('Volets', 'Vos volets sont-ils en ?', 
 ARRAY['Bois', 'PVC', 'Autre'], 
 ARRAY[1, 0, 1], FALSE, NULL, NULL),

-- 16. Garage (Question MAÎTRE)
('Garage', 'Avez-vous un garage ?', 
 ARRAY['Oui', 'Non'], 
 ARRAY[0, 0], FALSE, NULL, NULL),

-- 17. Garage (Dépend de la 16)
('Garage', 'Où est-il situé ?', 
 ARRAY['Au niveau du rez-de-chaussée', 'En-dessous du rez-de-chaussée'], 
 ARRAY[0, 10], TRUE, 16, NULL),

-- 18. Installation de chauffage (Question MAÎTRE)
('Installation de chauffage', 'Quel type de moyen de production de chaleur disposez-vous ?', 
 ARRAY['Chaudière sur socle', 'Chaudière murale', 'Brûleur de fioul'], 
 ARRAY[2, 10, 10], FALSE, NULL, NULL),

-- 19. Installation de chauffage (Dépend de la 18)
('Installation de chauffage', 'Où est-ce que votre [chaudière sur socle, chaudière murale, brûleur de fioul] est située ?', 
 ARRAY['Au sous-sol', 'Au niveau du rez-de-chaussée', 'Autre'], 
 ARRAY[0, 0, 0], TRUE, 18, NULL),

-- 20. Installation de chauffage (Dépend de la 18)
('Installation de chauffage', 'A quelle hauteur est située votre [chaudière sur socle, chaudière murale, brûleur de fioul] ? Hauteur à apprécier à partir du rdc ou du sous-sol en fonction de sa localisation', 
 ARRAY['x'], 
 ARRAY[10, 10, 0], TRUE, 18, NULL),

-- 21. Installation de chauffage (Dépend de la 18)
 ('Installation de chauffage', 'A quelle hauteur est située votre [chaudière sur socle, chaudière murale, brûleur de fioul] ? Hauteur à apprécier à partir du rdc ou du sous-sol en fonction de sa localisation', 
 ARRAY['Si localisation au sous-sol', 'Si localisation au rdc et x > x de la crue de référence', 'Si localisation au rdc et x < x de la crue de référence'], 
 ARRAY[10, 10, 0], TRUE, 18, NULL),

-- 22. Installation de chauffage
('Installation de chauffage', 'Convecteurs électriques ? Utilisés notamment pour le chauffage de plancher ou chauffage mural', 
 ARRAY['Oui', 'Non'], 
 ARRAY[2, 0], FALSE, NULL, NULL),

-- 23. Cuves
('Cuves', 'Les cuves de produits polluants ou toxiques sont-elles arrimées ou fixées au sol ou enterrées ?', 
 ARRAY['Oui', 'Je n''ai pas de cuves', 'Non'], 
 ARRAY[0.5, 0, 10], FALSE, NULL, NULL),

-- 24. Véranda (Question MAÎTRE)
('Véranda', 'Votre logement dispose-t-il d''une véranda ?', 
 ARRAY['Oui', 'Non'], 
 ARRAY[0, 0], FALSE, NULL, NULL),

-- 25. Véranda (Dépend de la 24)
('Véranda', 'En quelle matière est-elle faite ?', 
 ARRAY['Bois', 'Aluminium, acier, PVC'], 
 ARRAY[2, 0], TRUE, 24, NULL),

-- 26. Véranda (Dépend de la 24)
('Véranda', 'Quel est le type de vitrage utilisé ?', 
 ARRAY['Vitrage simple', 'Vitrage feuilleté', 'Je ne sais pas (proxi : )'], 
 ARRAY[0.5, 0, 0.5], TRUE, 24, NULL),

-- 27. Terrasse extérieure
('Terrasse extérieure', 'Quel type de dalles utilisez-vous ?', 
 ARRAY['Dalles en béton + revêtement', 'Dalles, en béton ou pierre, sur sable'], 
 ARRAY[0, 1], FALSE, NULL, NULL);