import random

# Studentnr genereres som en sekvens fra 1 til 500
studentnr_list = list(range(1, 501))


emnekodernavn = [['Database 1', 'DAT1000'], ['Database 2','DAT2000'], ['Webutvikling og HCI','WEB1100'], ['Grunnleggende programering 1','PRG1000'], ['Informasjonssystemer', 'INF1000'], ['Praktisk Prosjektarbeid', 'PRO1000'], ['Grunnleggende programering 2','PRG1100'], ['Organisering og ledelse','ORL1000'], ['Objektorientert programering 1', 'OBJ2000']]

# Antallplasser på rommene genereres tilfeldig mellom 20 og 50
antallplasser_list = [random.randint(20, 50) for _ in range(30)]

# Datoene er i 2023, men tilfeldig valgt innenfor eksamensperioden
dato_list20=[]
for i in range (15, 25):
    dato_list20+=[f"2020-05-{i}"]

dato_list21 = []
for i in range(15, 25):
    dato_list21 += [f"2021-05-{i}"]

dato_list22 = []
for i in range(15, 25):
    dato_list22 += [f"2022-05-{i}"]

dato_list23 = []
for i in range(19, 21):
    dato_list23 += [f"2023-05-{i}"]

dato_list=[dato_list20, dato_list21, dato_list22, dato_list23]

# Karakterene er tilfeldig valgt fra A til F
karakter_list = ["'A'", "'B'", "'C'", "'D'", "'E'", "'F'", "Null"]

# Tilfeldig generert vilkårlige studentnavn
def generate_student_name():
    first_names = [
        'Oliver', 'Emma', 'Liam', 'Ava', 'Noah', 'Sophia', 'Ethan', 'Isabella', 'Lucas', 'Mia', 'Mason',
        'Charlotte', 'Logan', 'Amelia', 'Jackson', 'Harper', 'Elijah', 'Abigail', 'Aiden', 'Emily', 'Caden',
        'Ella', 'Grayson', 'Madison', 'Evelyn', 'Jacob', 'Avery', 'Caleb', 'Eleanor', 'Landon', 'Scarlett',
        'Owen', 'Grace', 'Muhammad', 'Chloe', 'Eli', 'Victoria', 'Levi', 'Aria', 'Luke', 'Lily', 'Alexander',
        'Aubrey', 'Gabriel', 'Addison', 'Carter', 'Hazel', 'Wyatt', 'Ellie', 'Isabelle', 'Matthew', 'Natalie',
        'Lincoln', 'Sofia', 'Henry', 'Elizabeth', 'Josiah', 'Camila', 'Samuel', 'Lila', 'William', 'Lucy',
        'Leo', 'Penelope', 'Nathan', 'Nova', 'David', 'Hannah', 'Adam', 'Zoe', 'Isaac', 'Stella', 'Benjamin',
        'Aurora', 'Dylan', 'Paisley', 'Sebastian', 'Brooklyn', 'Daniel', 'Audrey', 'Christian', 'Claire',
        'Luna', 'Zoey', 'Jaxon', 'Skylar', 'Julian', 'Savannah', 'Jayden', 'Bella', 'Miles', 'Nora',
        'Grayson', 'Riley', 'Leo', 'Valentina', 'Jace', 'Eva', 'Lincoln', 'Nevaeh', 'Bentley', 'Emilia'
    ]

    last_names = [
        'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Miller', 'Davis', 'Garcia', 'Rodriguez',
        'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Perez', 'Sanchez', 'Ramirez', 'Torres', 'Flores',
        'Rivera', 'Collins', 'Baker', 'Edwards', 'Turner', 'Campbell', 'Evans', 'Reed', 'Cook', 'Cooper',
        'Morgan', 'Bell', 'Ward', 'Watson', 'Sanders', 'Cruz', 'Fisher', 'Hayes', 'Lambert', 'Mills',
        'Perry', 'Ross', 'Powell', 'Long', 'Price', 'Barnes', 'Hughes', 'Butler', 'Simmons', 'Foster',
        'Gates', 'Bryant', 'Stewart', 'Harrison', 'Sanders', 'Howard', 'Cox', 'Boyd', 'Gray', 'James'
    ]

    name = random.choice(first_names) + ' ' + random.choice(last_names)
    return name.split()

# Funksjon for å generere et telefonnummer som består av åtte tilfeldige tall


def generate_phone_number():
    phone_number = ''.join(random.choices('0123456789', k=8))
    return phone_number

# Funksjon for å generere en tilfeldig karakter

def generate_karakter():
    karakter = random.choice(karakter_list)
    return karakter


# Åpne filen for å skrive MySQL-skriptet
with open('testdata.sql', 'w', encoding='UTF-8') as file:

    # Sett inn rader i Student tabellen
    studenter=[]
    for i in range(500):
        name = generate_student_name()
        fornavn = name[0]
        etternavn = name[1]
        epost = f"{fornavn.lower()}.{etternavn.lower()}@eksempel.no"
        telefon = generate_phone_number()
        studentnr = str(studentnr_list[i])
        studenter+=[studentnr]
        insert_query = f"INSERT INTO Student (Studentnr, Fornavn, Etternavn, Epost, Telefon) VALUES ('{studentnr}', '{fornavn}', '{etternavn}', '{epost}', '{telefon}');\n"
        file.write(insert_query)

    # Sett inn rader i Emne tab
    for i in range(9):
        emnekode = emnekodernavn[i][1]
        emnenavn = emnekodernavn[i][0]
        studiepoeng = random.uniform(5, 15)
        insert_query = f"INSERT INTO Emne (Emnekode, Emnenavn, Studiepoeng) VALUES ('{emnekode}', '{emnenavn}', {studiepoeng:.1f});\n"
        file.write(insert_query)

    # Sett inn rader i Rom tabellen
    for i in range(30):
        romnr = f"R{i+1:02d}"
        antallplasser = antallplasser_list[random.randint(0, len(antallplasser_list)-1)]          #antallplasser_list[i]
        insert_query = f"INSERT INTO Rom (Romnr, Antallplasser) VALUES ('{romnr}', {antallplasser});\n"
        file.write(insert_query)

    # Sett inn rader i Eksamen tabellen
    eksamner=[]
    for j in dato_list:
        eksamensar=[]
        for i in range(9):
            emnekode = emnekodernavn[i][1]
            dato = j[random.randint(0, len(j) - 1)]
            romnr = f"R{random.randint(1, 10):02d}"
            eksamensar+=[[emnekode, dato]]
            insert_query = f"INSERT INTO Eksamen (Emnekode, Dato, Romnr) VALUES ('{emnekode}', '{dato}', '{romnr}');\n"
            file.write(insert_query)
        eksamner+=[eksamensar]
    
    eksamner.remove(eksamner[3])

    # Sett inn rader i Eksamensresultat tabellen
    for j in eksamner:
        random.shuffle(studenter)
        for i in range(random.randint(300, 500)):
            studentnr = str(studenter[i])
            ranint = random.randint(0, len(j) - 1)
            emnekode = j[ranint][0]
            dato = j[ranint][1]
            karakter = generate_karakter()
            insert_query = f"INSERT INTO Eksamensresultat (Studentnr, Emnekode, Dato, Karakter) VALUES ('{studentnr}', '{emnekode}', '{dato}', {karakter});\n"
            file.write(insert_query)
