from athena_client import Athena
athena = Athena()

# Find aspirin
hits = athena.search("aspirin", size=3)
for c in hits.all():
    print(f"{c.id=} {c.name=} {c.vocabulary=}")

# Inspect top concept
d = athena.details(1112807)        # 1112807 = Aspirin (RxNorm)
print(d.conceptClassId, d.standardConcept)
