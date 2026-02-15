DROP TABLE IF EXISTS public.questions;

CREATE TABLE public.questions (
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    critère character varying(100) NOT NULL,
    question character varying(1000) NOT NULL,
    réponse character varying(1000) NOT NULL,
    score_vulnerabilite integer DEFAULT 0
);

INSERT INTO public.questions (critère, question, réponse, score_vulnerabilite) VALUES 
('Zone inondable', 'Quelle est l''adresse de votre bien ?', '', 0),
('Niveau du plancher', 'Avez-vous fait des travaux récemment au niveau du rez-de-chaussée ?', '', 0),
('Niveau du plancher', 'Quel est le niveau du premier plancher habitable de mon habitation ?', '', 0),
('Hauteur d''eau potentielle', 'Calcul H = niveau d''inondation (donné dans la zone d''aléas) - niveau du premier plancher', 'si >= 0,2 m', -20),
('Hauteur d''eau potentielle', 'Calcul H = niveau d''inondation (donné dans la zone d''aléas) - niveau du premier plancher', 'si < 0,2 m', 0);