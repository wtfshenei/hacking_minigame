# shuffle_commands.py

import json
import random

# 1) Charge le JSON
with open('commands.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 2) Récupère les commandes, en excluant la cachée (qu’on remettra à la fin)
cmds = data['commands']
visible = [k for k in cmds.keys() if k != 'agartha']
secret = [k for k in cmds.keys() if k == 'agartha']

# 3) Mélange et reconstruit l’ordre
random.shuffle(visible)
new_order = visible + secret
shuffled = {k: cmds[k] for k in new_order}

# 4) Réaffecte et écrit
data['commands'] = shuffled
with open('commands.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("✅ commands.json a été réordonné !")
