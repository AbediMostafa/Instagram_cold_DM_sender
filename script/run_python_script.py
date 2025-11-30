import random
first_names = [
    "Ethan","Mason","Logan","James","Benjamin","Elijah","Alexander","Henry","Jackson","Sebastian",
    "Aiden","Matthew","Samuel","David","Joseph","Carter","Owen","Wyatt","John","Jack",
    "Luke","Dylan","Gabriel","Isaac","Nathan","Julian","Levi","Ryan","Connor","Christian",
    "Andrew","Jonathan","Adrian","Leo","Elias","Anthony","Joshua","Daniel","Aaron","Evan",
    "Sofia","Alice","Victoria","Gabriela","Isadora","Helena","Beatriz","Clarissa","Leticia","Renata",
    "Carolina","Fernanda","Tatiana","Camilla","Bianca","Larissa","Isabel","Manuela","Ana","Paula",
    "Laura","Marina","Valentina","Bruna","Yasmin","Amanda","Nicole","Julia","Carla","Raquel",
    "Vanessa","Camile","Lorena","Aline","Isis","Rafaela","Júlia","Gabrielle","Melissa","Luana",
    "Evelyn","Stella","Clara","Emilly","Mirella","Lara","Luna","Victoria","Sara","Amanda",
    "Thais","Isabela","Marina","Júlia","Helena","Nicole","Camila","Sabrina","Larissa","Manuela"
]

last_names = [
    "Taylor","Anderson","Thomas","Moore","Jackson","White","Harris","Martin","Thompson","Garcia",
    "Martinez","Robinson","Clark","Rodriguez","Lewis","Lee","Walker","Hall","Allen","Young",
    "Hernandez","King","Wright","Lopez","Hill","Scott","Green","Adams","Baker","Nelson",
    "Carter","Mitchell","Perez","Roberts","Turner","Phillips","Campbell","Parker","Evans","Edwards",
    "Collins","Stewart","Sanchez","Morris","Rogers","Reed","Cook","Morgan","Bell","Murphy",
    "Bailey","Rivera","Cooper","Richardson","Cox","Howard","Ward","Torres","Peterson","Gray",
    "Ramirez","James","Watson","Brooks","Kelly","Sanders","Price","Bennett","Wood","Barnes",
    "Ross","Henderson","Coleman","Jenkins","Perry","Powell","Long","Patterson","Hughes","Flores",
    "Washington","Butler","Simmons","Foster","Gonzalez","Bryant","Alexander","Russell","Griffin","Diaz",
    "Mendoza","Freitas","Souza","Moreira","Nascimento","Alves","Lima","Vieira","Gomes","Barbosa",
    "Pinto","Moura","Fonseca","Machado","Cardoso","Araujo","Teixeira","Ramos","Campos","Santana"
]

adjectives = [
    "lit","dope","epic","savage","vibe","chill","fresh","rad","hype","wild",
    "crazy","boss","swag","sneaky","slick","icy","flashy","crisp","glow","prime",
    "raw","urban","neon","shady","stormy","frosty","blaze","fierce","sleek","sharp",
    "wavy","atomic","cosmic","pixel","retro","drip","boost","boosted","legend","mythic",
    "hyper","nova","galaxy","vortex","chaos","thunder","storm","shadow","ghost","phantom",
    "viper","rebel","blade","ace","titan","quake","drift","flare","ignite","pulse",
    "strike","volt","racer","crash","flash","neo","cyber","tech","steel","dark",
    "ghostly","glitch","crimson","onyx","steel","frost","ember","iron","quantum","blitz",
    "fusion","gravity","omega","alpha","beta","delta","zen","echo","alpha","drone","pixelated",
    "hyperdrive","vivid","chrome","neptune","mars","apollo","saturn","asteroid","lunar","solar"
]

def generate_username():
    # انتخاب تصادفی نام و فامیلی
    first = random.choice(first_names)
    last = random.choice(last_names)
    adj = random.choice(adjectives) if random.random() < 0.5 else ""

    # اضافه کردن شماره تصادفی
    number = str(random.randint(1, 9999)) if random.random() < 0.5 else ""  # 70٪ شانس عدد

    # انتخاب جداکننده تصادفی
    separator = random.choice(["", "_", "__", "._", "_.", "_._", "_.__", "_.__"])

    # ساختار یوزرنیم با طول تصادفی
    username = first + adj+ separator + last + number+adj+separator

    # کوتاه یا بلند کردن با اضافه کردن یک جداکننده یا عدد در صورت نیاز
    if len(username) < 10:
        username += str(random.randint(10, 99))
    if len(username) > 28:
        username = username[:28]  # محدودیت اینستاگرام

    return username


print(generate_username())