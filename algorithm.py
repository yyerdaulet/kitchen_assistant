
recepts = {
    "tomato-cucumber salad":['tomato','cucumber','onion'],
    "pizza":['cheese','tomato','dough'],
}

def choose_the_food(ingredients):
    food = ""
    max_compatibility = 0
    for recept in recepts:
        common = list(set(ingredients) & set(recepts[recept]))
        compatibility = len(common)/len(recepts[recept])
        if compatibility > max_compatibility:
            max_compatibility = compatibility
            food = recept
    return int(max_compatibility*100),food


