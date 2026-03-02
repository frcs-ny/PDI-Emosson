DROP TABLE IF EXISTS public.questions;

CREATE TABLE public.zone_inondable (
    id SERIAL PRIMARY KEY,
    critere VARCHAR(255) NOT NULL,
    question TEXT NOT NULL,
    reponses TEXT[] NOT NULL,
    scores_vulnerabilite NUMERIC[] NOT NULL
);

CREATE TABLE public.questions_logement (
    id SERIAL PRIMARY KEY,
    critere VARCHAR(255) NOT NULL,
    question TEXT NOT NULL,
    reponses TEXT[] NOT NULL,
    scores_vulnerabilite NUMERIC[] NOT NULL
);

INSERT INTO public.zone_inondable (critere, question, reponses, scores_vulnerabilite) VALUES

-- Zone inondable
('Zone inondable', 'Quelle est l''adresse de votre bien ?', 
 ARRAY['Zone de dissipation de l''énergie (ZDE)', 'Ecoulement préférentiel (EP)', 'Modéré (M)', 'Fort (F)', 'Très fort (TF)'], 
 ARRAY[140, 140, 80, 110, 140]),

-- Niveau du plancher
('Niveau du plancher', 'Avez-vous fait des travaux récemment au niveau du rez-de-chaussée ?', 
 ARRAY['Oui', 'Non'], 
 ARRAY[0, 0]),

('Niveau du plancher', 'Quel est le niveau du premier plancher habitable de mon habitation ?', 
 ARRAY['x'], 
 ARRAY[0]),

-- Hauteur d'eau potentielle
('Hauteur d''eau potentielle', 'Calcul H = niveau d''inondation (donné dans la zone d''aléas) - niveau du premier plancher', 
 ARRAY['h >= 0.2', 'h <= 0.2'], 
 ARRAY[-20, 0]);

INSERT INTO public.questions_logement (critere, question, reponses, scores_vulnerabilite) VALUES

-- Murs
('Murs', 'Vos murs sont-ils faits en bois ?', 
 ARRAY['Oui + H > 1', 'Oui + H < 1', 'Non'], 
 ARRAY[7.5, 7.5, 0]),

-- Isolant
('Isolant', 'Quel matériau d''isolation est utilisé dans votre logement ?', 
 ARRAY['Fibre minérale (laine de verre)', 'Fibre végétale', 'Vermiculite', 'Plastique alvéolaire', 'Je ne sais pas (proxi : fibre minérale)'], 
 ARRAY[10, 10, 10, 0, 10]),

('Isolant', 'Votre schéma d''isolation comporte-t-il un doublage collé en plâtre ?', 
 ARRAY['Oui', 'Non', 'Je ne sais pas'], 
 ARRAY[5, 0, 5]),

-- Enduit intérieur
('Enduit intérieur', 'Quel enduit est posé sur vos murs et cloisons ?', 
 ARRAY['Mortier ciment', 'Plâtre'], 
 ARRAY[0, 2]),

-- Revêtements muraux intérieurs
('Revêtements muraux intérieurs', 'Quel revêtement est posé sur vos enduits, cloisons ou portes ?', 
 ARRAY['Papier', 'Peinture', 'Textile', 'Bois', 'Carrelage collé', 'Carrelage scellé', 'Je ne sais pas (proxi : )'], 
 ARRAY[10, 7.5, 10, 5, 0, 0, 7.5]),

-- Plancher
('Plancher', 'En quel matériau est fait votre plancher ?', 
 ARRAY['Béton', 'Métal et briques', 'Bois'], 
 ARRAY[0, 0, 7.5]),

-- Revêtements sols
('Revêtements sols', 'Quelle est la matière de revêtement de vos sols ?', 
 ARRAY['Peinture', 'Textile', 'Plastique', 'Bois massif', 'Bois lamelles', 'Carrelage collé', 'Carrelage scellé'], 
 ARRAY[1, 7.5, 2, 3, 5, 0, 0]),

-- Portes intérieures
('Portes intérieures', 'En quel matériau sont fabriquées vos portes intérieures ?', 
 ARRAY['Carton (portes alvéolaires)', 'Bois', 'Autre', 'Je ne sais pas'], 
 ARRAY[7.5, 4, 3, 4]),

('Portes intérieures', 'En quel matériau sont faites les huisseries ?', 
 ARRAY['Bois', 'Métal', 'Je ne sais pas'], 
 ARRAY[1, 0, 1]),

-- Escalier intérieur
('Escalier intérieur', 'En quoi est fait votre ou vos escaliers intérieurs ?', 
 ARRAY['Béton', 'Bois', 'Autre'], 
 ARRAY[0, 4, 2]),

-- Portes d'entrée
('Portes d''entrée', 'En quelle matière sont faites vos portes d''entrée ?', 
 ARRAY['Bois massif', 'PVC', 'Métal (acier, aluminium)'], 
 ARRAY[4, 0, 0]),

('Portes d''entrée', 'Et les huisseries ?', 
 ARRAY['Bois', 'Autre'], 
 ARRAY[1, 0]),

-- Fenêtres
('Fenêtres', 'En quelle matière sont faites vos fenêtres ?', 
 ARRAY['Bois + H > 1,2 m', 'PVC', 'Métal (acier, aluminium)'], 
 ARRAY[2, 0, 0]),

-- Panneaux vitrés de grande dimension
('Panneaux vitrés de grande dimension', 'Votre logement dispose-t-il de baies vitrées ou de porte-fenêtres ?', 
 ARRAY['Oui + H > 0,5', 'Non'], 
 ARRAY[5, 0]),

-- Volets
('Volets', 'Vos volets sont-ils en ?', 
 ARRAY['Bois', 'PVC', 'Autre'], 
 ARRAY[1, 0, 1]),

-- Garage
('Garage', 'Avez-vous un garage ?', 
 ARRAY['Oui', 'Non'], 
 ARRAY[0, 0]),

('Garage', 'Où est-il situé ?', 
 ARRAY['Au niveau du rez-de-chaussée', 'En-dessous du rez-de-chaussée'], 
 ARRAY[0, 10]),

-- Installation de chauffage
('Installation de chauffage', 'Quel type de moyen de production de chaleur disposez-vous ?', 
 ARRAY['Chaudière sur socle', 'Chaudière murale', 'Brûleur de fioul'], 
 ARRAY[2, 10, 10]),

('Installation de chauffage', 'Où est-ce que votre [chaudière sur socle, chaudière murale, brûleur de fioul] est située ?', 
 ARRAY['Au sous-sol', 'Au niveau du rez-de-chaussée', 'Autre'], 
 ARRAY[0, 0, 0]),

('Installation de chauffage', 'A quelle hauteur est située votre [chaudière sur socle, chaudière murale, brûleur de fioul] ? Hauteur à apprécier à partir du rdc ou du sous-sol en fonction de sa localisation', 
 ARRAY['Si localisation au sous-sol', 'Si localisation au rdc et H > H de la crue de référence', 'Si localisation au rdc et H < H de la crue de référence'], 
 ARRAY[10, 10, 0]),

('Installation de chauffage', 'Convecteurs électriques ? Utilisés notamment pour le chauffage de plancher ou chauffage mural', 
 ARRAY['Oui', 'Non'], 
 ARRAY[2, 0]),

-- Cuves
('Cuves', 'Les cuves de produits polluants ou toxiques sont-elles arrimées ou fixées au sol ou enterrées ?', 
 ARRAY['Oui', 'Je n''ai pas de cuves', 'Non'], 
 ARRAY[0.5, 0, 10]),

-- Véranda
('Véranda', 'Votre logement dispose-t-il d''une véranda ?', 
 ARRAY['Oui', 'Non'], 
 ARRAY[0, 0]),

('Véranda', 'En quelle matière est-elle faite ?', 
 ARRAY['Bois', 'Aluminium, acier, PVC'], 
 ARRAY[2, 0]),

('Véranda', 'Quel est le type de vitrage utilisé ?', 
 ARRAY['Vitrage simple', 'Vitrage feuilleté', 'Je ne sais pas (proxi : )'], 
 ARRAY[0.5, 0, 0.5]),

-- Terrasse extérieure
('Terrasse extérieure', 'Quel type de dalles utilisez-vous ?', 
 ARRAY['Dalles en béton + revêtement', 'Dalles, en béton ou pierre, sur sable'], 
 ARRAY[0, 1]);