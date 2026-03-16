DROP TABLE IF EXISTS public.zone_inondable CASCADE;
DROP TABLE IF EXISTS public.questions_logement CASCADE;
DROP TABLE IF EXISTS public.protection_personnes CASCADE;

CREATE TABLE public.zone_inondable (
    id SERIAL PRIMARY KEY,
    critere VARCHAR(255) NOT NULL,
    question TEXT NOT NULL,
    reponses TEXT[] NOT NULL,
    scores_vulnerabilite NUMERIC[] NOT NULL,
    a_dependance BOOLEAN DEFAULT FALSE,
    id_question_liee INTEGER REFERENCES public.zone_inondable(id),
    recommandations TEXT[] -- Modifié en TEXT[] pour correspondre aux indices des réponses
);

CREATE TABLE public.questions_logement (
    id SERIAL PRIMARY KEY,
    critere VARCHAR(255) NOT NULL,
    question TEXT NOT NULL,
    reponses TEXT[] NOT NULL,
    scores_vulnerabilite NUMERIC[] NOT NULL,
    a_dependance BOOLEAN DEFAULT FALSE,
    id_question_liee INTEGER REFERENCES public.questions_logement(id),
    recommandations TEXT[] -- Modifié en TEXT[]
);

CREATE TABLE public.protection_personnes (
    id SERIAL PRIMARY KEY,
    critere VARCHAR(255) NOT NULL,
    question TEXT NOT NULL,
    reponses TEXT[] NOT NULL,
    scores_vulnerabilite NUMERIC[] NOT NULL,
    a_dependance BOOLEAN DEFAULT FALSE,
    id_question_liee INTEGER REFERENCES public.protection_personnes(id),
    recommandations TEXT[] -- Modifié en TEXT[]
);

INSERT INTO public.zone_inondable (critere, question, reponses, scores_vulnerabilite, a_dependance, id_question_liee, recommandations) VALUES

-- Zone inondable
('Zone inondable', 'Quelle est l''adresse de votre bien ?', 
 ARRAY['Zone de dissipation de l''énergie (ZDE)', 'Ecoulement préférentiel (EP)', 'Modéré (M)', 'Fort (F)', 'Très fort (TF)'], 
 ARRAY[140, 140, 80, 110, 140], FALSE, NULL, 
 ARRAY['', '', '', '', '']),

-- Niveau du plancher
('Niveau du plancher', 'Avez-vous fait des travaux récemment au niveau du rez-de-chaussée ?', 
 ARRAY['Oui', 'Non'], 
 ARRAY[0, 0], FALSE, NULL, 
 ARRAY['', '']),

('Niveau du plancher', 'Quel est le niveau du premier plancher habitable de mon habitation ?', 
 ARRAY['x'], 
 ARRAY[0], FALSE, NULL, 
 ARRAY['']),

-- Hauteur d'eau potentielle
('Hauteur d''eau potentielle', 'Calcul H = niveau d''inondation (donné dans la zone d''aléas) - niveau du premier plancher', 
 ARRAY['h >= 0.2', 'h <= 0.2'], 
 ARRAY[-20, 0], FALSE, NULL, 
 ARRAY['', '']);


INSERT INTO public.questions_logement (critere, question, reponses, scores_vulnerabilite, a_dependance, id_question_liee, recommandations) VALUES

-- 1. Murs
('Murs', 'Vos murs sont-ils faits en bois ?', 
 ARRAY['Oui', 'Non'], 
 ARRAY[7.5, 0], FALSE, NULL, 
 ARRAY['Lors de vos futurs travaux ou aménagements, privilégiez l''utilisation de matériaux hydrofuges, qui sont beaucoup plus résistants à l''immersion.', '']),

-- 2. Isolant
('Isolant', 'Quel matériau d''isolation est utilisé dans votre logement ?', 
 ARRAY['Fibre minérale (laine de verre)', 'Fibre végétale', 'Vermiculite', 'Plastique alvéolaire', 'Je ne sais pas (proxi : fibre minérale)'], 
 ARRAY[10, 10, 10, 0, 10], FALSE, NULL, 
 ARRAY['Lors de vos futurs travaux ou aménagements, privilégiez l''utilisation de matériaux hydrofuges, qui sont beaucoup plus résistants à l''immersion.', 'Lors de vos futurs travaux ou aménagements, privilégiez l''utilisation de matériaux hydrofuges, qui sont beaucoup plus résistants à l''immersion.', 'Lors de vos futurs travaux ou aménagements, privilégiez l''utilisation de matériaux hydrofuges, qui sont beaucoup plus résistants à l''immersion.', '', 'Lors de vos futurs travaux ou aménagements, privilégiez l''utilisation de matériaux hydrofuges, qui sont beaucoup plus résistants à l''immersion.']),

-- 3. Isolant
('Isolant', 'Votre schéma d''isolation comporte-t-il un doublage collé en plâtre ?', 
 ARRAY['Oui', 'Non', 'Je ne sais pas'], 
 ARRAY[5, 0, 5], FALSE, NULL, 
 ARRAY['', '', '']),

-- 4. Enduit intérieur
('Enduit intérieur', 'Quel enduit est posé sur vos murs et cloisons ?', 
 ARRAY['Mortier ciment', 'Plâtre'], 
 ARRAY[0, 2], FALSE, NULL, 
 ARRAY['', '']),

-- 5. Revêtements muraux intérieurs
('Revêtements muraux intérieurs', 'Quel revêtement est posé sur vos enduits, cloisons ou portes ?', 
 ARRAY['Papier', 'Peinture', 'Textile', 'Bois', 'Carrelage collé', 'Carrelage scellé', 'Je ne sais pas (proxi : )'], 
 ARRAY[10, 7.5, 10, 5, 0, 0, 7.5], FALSE, NULL, 
 ARRAY['', '', '', '', '', '', '']),

-- 6. Plancher
('Plancher', 'En quel matériau est fait votre plancher ?', 
 ARRAY['Béton', 'Métal et briques', 'Bois'], 
 ARRAY[0, 0, 7.5], FALSE, NULL, 
 ARRAY['', '', 'Lors de vos futurs travaux ou aménagements, privilégiez l''utilisation de matériaux hydrofuges, qui sont beaucoup plus résistants à l''immersion.']),

-- 7. Revêtements sols
('Revêtements sols', 'Quelle est la matière de revêtement de vos sols ?', 
 ARRAY['Peinture', 'Textile', 'Plastique', 'Bois massif', 'Bois lamelles', 'Carrelage collé', 'Carrelage scellé'], 
 ARRAY[1, 7.5, 2, 3, 5, 0, 0], FALSE, NULL, 
 ARRAY['', '', '', '', '', '', '']),

-- 8. Portes intérieures
('Portes intérieures', 'En quel matériau sont fabriquées vos portes intérieures ?', 
 ARRAY['Carton (portes alvéolaires)', 'Bois', 'Autre', 'Je ne sais pas'], 
 ARRAY[7.5, 4, 3, 4], FALSE, NULL, 
 ARRAY['', '', '', '']),

-- 9. Portes intérieures
('Portes intérieures', 'En quel matériau sont faites les huisseries ?', 
 ARRAY['Bois', 'Métal', 'Je ne sais pas'], 
 ARRAY[1, 0, 1], FALSE, NULL, 
 ARRAY['', '', '']),

-- 10. Escalier intérieur
('Escalier intérieur', 'En quoi est fait votre ou vos escaliers intérieurs ?', 
 ARRAY['Béton', 'Bois', 'Autre'], 
 ARRAY[0, 4, 2], FALSE, NULL, 
 ARRAY['', '', '']),

-- 11. Portes d'entrée
('Portes d''entrée', 'En quelle matière sont faites vos portes d''entrée ?', 
 ARRAY['Bois massif', 'PVC', 'Métal (acier, aluminium)'], 
 ARRAY[4, 0, 0], FALSE, NULL, 
 ARRAY['', '', '']),

-- 12. Portes d'entrée
('Portes d''entrée', 'Et les huisseries ?', 
 ARRAY['Bois', 'Autre'], 
 ARRAY[1, 0], FALSE, NULL, 
 ARRAY['', '']),

-- 13. Fenêtres
('Fenêtres', 'En quelle matière sont faites vos fenêtres ?', 
 ARRAY['Bois + H > 1,2 m', 'PVC', 'Métal (acier, aluminium)'], 
 ARRAY[2, 0, 0], FALSE, NULL, 
 ARRAY['', '', '']),

-- 14. Panneaux vitrés de grande dimension
('Panneaux vitrés de grande dimension', 'Votre logement dispose-t-il de baies vitrées ou de porte-fenêtres ?', 
 ARRAY['Oui + H > 0,5', 'Non'], 
 ARRAY[5, 0], FALSE, NULL, 
 ARRAY['', '']),

-- 15. Volets
('Volets', 'Vos volets sont-ils en ?', 
 ARRAY['Bois', 'PVC', 'Autre'], 
 ARRAY[1, 0, 1], FALSE, NULL, 
 ARRAY['', '', '']),

-- 16. Garage (Question MAÎTRE)
('Garage', 'Avez-vous un garage ?', 
 ARRAY['Oui', 'Non'], 
 ARRAY[0, 0], FALSE, NULL, 
 ARRAY['', '']),

-- 17. Garage (Dépend de la 16)
('Garage', 'Où est-il situé ?', 
 ARRAY['Au niveau du rez-de-chaussée', 'En-dessous du rez-de-chaussée'], 
 ARRAY[0, 10], TRUE, 16, 
 ARRAY['', 'Puisque votre garage se situe en sous-sol, l''acquisition d''une pompe vous permettra d''évacuer l''eau plus efficacement en cas d''inondation. S''il s''agit d''un grand volume, une pompe de relevage sera particulièrement adaptée.']),

-- 18. Installation de chauffage (Question MAÎTRE)
('Installation de chauffage', 'Quel type de moyen de production de chaleur disposez-vous ?', 
 ARRAY['Chaudière sur socle', 'Chaudière murale', 'Brûleur de fioul'], 
 ARRAY[2, 10, 10], FALSE, NULL, 
 ARRAY['', '', '']),

-- 19. Installation de chauffage (Dépend de la 18)
('Installation de chauffage', 'Où est-ce que votre [chaudière sur socle, chaudière murale, brûleur de fioul] est située ?', 
 ARRAY['Au sous-sol', 'Au niveau du rez-de-chaussée', 'Autre'], 
 ARRAY[0, 0, 0], TRUE, 18, 
 ARRAY['', '', '']),

-- 20. Installation de chauffage (Dépend de la 18)
('Installation de chauffage', 'A quelle hauteur est située votre [chaudière sur socle, chaudière murale, brûleur de fioul] ? Hauteur à apprécier à partir du rdc ou du sous-sol en fonction de sa localisation', 
 ARRAY['x'], 
 ARRAY[10, 10, 0], TRUE, 18, 
 ARRAY['']),

-- 21. Installation de chauffage (Dépend de la 18)
 ('Installation de chauffage', 'A quelle hauteur est située votre [chaudière sur socle, chaudière murale, brûleur de fioul] ? Hauteur à apprécier à partir du rdc ou du sous-sol en fonction de sa localisation', 
 ARRAY['Si localisation au sous-sol', 'Si localisation au rdc et x > x de la crue de référence', 'Si localisation au rdc et x < x de la crue de référence'], 
 ARRAY[10, 10, 0], TRUE, 18, 
 ARRAY['Afin de protéger vos équipements vitaux, il est fortement conseillé de rehausser les éléments vulnérables à l''eau, comme votre chaudière, votre chauffe-eau, votre tableau électrique, ainsi que les prises et interrupteurs.', '', 'Afin de protéger vos équipements vitaux, il est fortement conseillé de rehausser les éléments vulnérables à l''eau, comme votre chaudière, votre chauffe-eau, votre tableau électrique, ainsi que les prises et interrupteurs.']),

-- 22. Installation de chauffage
('Installation de chauffage', 'Convecteurs électriques ? Utilisés notamment pour le chauffage de plancher ou chauffage mural', 
 ARRAY['Oui', 'Non'], 
 ARRAY[2, 0], FALSE, NULL, 
 ARRAY['', '']),

-- 23. Cuves
('Cuves', 'Les cuves de produits polluants ou toxiques sont-elles arrimées ou fixées au sol ou enterrées ?', 
 ARRAY['Oui', 'Je n''ai pas de cuves', 'Non'], 
 ARRAY[0.5, 0, 10], FALSE, NULL, 
 ARRAY['', '', 'Pour éviter que vos cuves ne flottent ou ne libèrent des produits polluants, veillez à bien les arrimer. Il est conseillé de créer des points d''attache sur une dalle en béton à l''aide de sangles, ou de les placer en hauteur sur un support renforcé.']),

-- 24. Véranda (Question MAÎTRE)
('Véranda', 'Votre logement dispose-t-il d''une véranda ?', 
 ARRAY['Oui', 'Non'], 
 ARRAY[0, 0], FALSE, NULL, 
 ARRAY['', '']),

-- 25. Véranda (Dépend de la 24)
('Véranda', 'En quelle matière est-elle faite ?', 
 ARRAY['Bois', 'Aluminium, acier, PVC'], 
 ARRAY[2, 0], TRUE, 24, 
 ARRAY['', '']),

-- 26. Véranda (Dépend de la 24)
('Véranda', 'Quel est le type de vitrage utilisé ?', 
 ARRAY['Vitrage simple', 'Vitrage feuilleté', 'Je ne sais pas (proxi : )'], 
 ARRAY[0.5, 0, 0.5], TRUE, 24, 
 ARRAY['', '', '']),

-- 27. Terrasse extérieure
('Terrasse extérieure', 'Quel type de dalles utilisez-vous ?', 
 ARRAY['Dalles en béton + revêtement', 'Dalles, en béton ou pierre, sur sable'], 
 ARRAY[0, 1], FALSE, NULL, 
 ARRAY['', '']);


INSERT INTO public.protection_personnes (critere, question, reponses, scores_vulnerabilite, a_dependance, id_question_liee, recommandations) VALUES

-- Zone refuge
('Zone refuge', 'Disposez-vous d''une zone refuge ?', 
 ARRAY['Oui', 'Non'], 
 ARRAY[0, 30], FALSE, NULL, 
 ARRAY['', 'Il est recommandé de créer ou d''aménager un espace refuge pour vous mettre en sécurité. Selon la configuration de votre logement, cela peut passer par l''ajout d''une fenêtre de toit, la création d''un étage, ou l''aménagement d''une mezzanine ou d''une coursive.']),

('Zone refuge', 'Disposez-vous d''un kit d''urgence (lampe, radio, eau, médicaments, papiers importants) ?', 
 ARRAY['Oui', 'Non'], 
 ARRAY[0, 20], FALSE, NULL, 
 ARRAY['', 'Pensez à constituer un kit d''urgence (lampe, radio, eau, etc.) et à le conserver à portée de main, idéalement dans votre espace refuge.']),

-- Sensibilisation
('Sensibilisation', 'Quel est votre degré de connaissance du risque inondation (exemples : savoir trouver l''information officielle en cas d''alerte, participation à une réunion d''information ou un exercice sur le risque inondation) ?', 
 ARRAY['Elevé', 'Moyen', 'Faible'], 
 ARRAY[5, 10, 20], FALSE, NULL, 
 ARRAY['', '', '']),

-- Mobilité des occupants
('Mobilité des occupants', 'Est-ce que des personnes à mobilité réduite occupent le logement ?', 
 ARRAY['Oui', 'Non'], 
 ARRAY[30, 0], FALSE, NULL, 
 ARRAY['', '']),

-- Sécurité des secouristes
('Sécurité des secouristes', 'Si vous disposez d''une piscine ou d''un bassin immergé, est-ce que ses abords sont délimités (par des mâts, perches, visibles y compris en cas de submersion de la zone alentour) ?', 
 ARRAY['Oui', 'Non', 'Je n''ai pas de piscine'], 
 ARRAY[0, 20, 0], FALSE, NULL, 
 ARRAY['', 'Pour assurer la sécurité des secouristes en cas d''inondation, il est préconisé d''installer une barrière périphérique autour de votre piscine ou bassin. Assurez-vous qu''elle mesure au moins 1,10 mètre de haut afin de rester visible même sous 1 mètre d''eau.', '']);