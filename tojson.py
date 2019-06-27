import json

f = open("test").read().splitlines()

a = []
for i in range(0,len(f), 2):
    pokemon = f[i]
    fast,charged1,charged2 = f[i+1].split(",")
    a.append({'pokemon': pokemon.strip(), 'fast': fast.strip(), 'charged1': charged1.strip(), 'charged2': charged2.strip()})

print(json.dumps(a, indent=2))
